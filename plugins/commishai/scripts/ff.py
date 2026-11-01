#!/usr/bin/env python
"""CommishAI ESPN fantasy football CLI.

One entrypoint, many subcommands. Read-only: espn-api exposes no write
endpoints, so nothing here can set a lineup or process a transaction. Output is
evidence for a recommendation the manager executes in the ESPN app.

    python scripts/ff.py snapshot
    python scripts/ff.py available --pos RB --n 15
    python scripts/ff.py player "Bijan Robinson" --json
"""

import argparse
import sys
from typing import Any, Dict, List, Optional

import client
import render
from client import ConfigError, current_week, get_league, get_my_team, load_config

BENCH_SLOTS = {"BE", "IR"}
SKILL_POSITIONS = ["QB", "RB", "WR", "TE", "D/ST", "K"]
POSITION_ALIASES = {"DEF": "D/ST", "DST": "D/ST", "D": "D/ST", "PK": "K"}


# ---------------------------------------------------------------- extraction


def week_stats(player: Any, week: int) -> Dict[str, Any]:
    """Pull one week out of player.stats, which is keyed by int scoring period."""
    stats = getattr(player, "stats", None) or {}
    return stats.get(week) or stats.get(str(week)) or {}


def opponent(player: Any, week: int) -> str:
    """Opponent for the week, or BYE.

    Two shapes arrive here. `league.free_agents()` and `box_scores()` return
    BoxPlayer, which carries `pro_opponent` and an authoritative `on_bye_week`
    but leaves `schedule` empty. `team.roster` returns plain Player, which has
    only `schedule` — keyed by *string* week. Reading just one shape is why
    every free agent reported BYE.
    """
    if getattr(player, "on_bye_week", False):
        return "BYE"

    pro_opponent = getattr(player, "pro_opponent", None)
    if pro_opponent and pro_opponent != "None":
        return str(pro_opponent)

    schedule = getattr(player, "schedule", None) or {}
    entry = schedule.get(str(week)) or schedule.get(week)
    if isinstance(entry, dict):
        team = entry.get("team")
        if team:
            return str(team)
    return "BYE"


def recent_points(player: Any, week: int, count: int = 3) -> List[Optional[float]]:
    """Actual points for the `count` completed weeks before `week`, oldest first."""
    out: List[Optional[float]] = []
    for wk in range(max(1, week - count), week):
        out.append(week_stats(player, wk).get("points"))
    return out


def _clean(value: Any) -> Any:
    """ESPN's -1 sentinel means 'not provided', not a real value."""
    if isinstance(value, (int, float)) and value < 0:
        return None
    return value


def player_row(player: Any, week: int) -> Dict[str, Any]:
    """The common row shape every roster/free-agent listing shares."""
    stats = week_stats(player, week)
    opp = opponent(player, week)
    injury = getattr(player, "injuryStatus", None) or ""
    if injury in ("ACTIVE", "NORMAL"):
        injury = ""

    # BoxPlayer uses slot_position ('FA' for free agents); Player uses lineupSlot.
    slot = getattr(player, "slot_position", None) or getattr(player, "lineupSlot", "") or ""
    if slot == "FA":
        slot = ""

    # ESPN's rank of the opposing defense against this player's position, 1-32.
    # Higher is a softer matchup. Only BoxPlayer carries it.
    oprk = getattr(player, "pro_pos_rank", None) or None

    last3 = recent_points(player, week)
    return {
        "name": player.name,
        "pos": getattr(player, "position", "?"),
        "slot": slot,
        "team": getattr(player, "proTeam", "?"),
        "opp": opp,
        "oprk": oprk,
        "proj": stats.get("projected_points", getattr(player, "projected_points", None)),
        "actual": stats.get("points", getattr(player, "points", None)),
        "avg": getattr(player, "avg_points", None),
        "last3": " ".join(render.fmt(p, 0) for p in last3) if last3 else "-",
        "injury": injury or ("BYE" if opp == "BYE" else ""),
        # ESPN uses -1 for "unknown" on these; don't render it as a number.
        "owned": _clean(getattr(player, "percent_owned", None)),
        "started": _clean(getattr(player, "percent_started", None)),
        "rank": _clean(getattr(player, "posRank", None)),
        "player_id": getattr(player, "playerId", None),
    }


def normalize_position(pos: Optional[str]) -> Optional[str]:
    if not pos:
        return None
    pos = pos.strip().upper()
    return POSITION_ALIASES.get(pos, pos)


def flag_row(row: Dict[str, Any]) -> str:
    """A short reason this player needs attention, or ''."""
    if row["opp"] == "BYE":
        return "ON BYE"
    injury = (row["injury"] or "").upper()
    if injury in ("OUT", "INJURY_RESERVE", "SUSPENSION"):
        return f"OUT ({injury})"
    if injury in ("QUESTIONABLE", "DOUBTFUL"):
        return injury
    return ""


def roster_players(league, team, week: int) -> List[Any]:
    """A team's players with the best of both ESPN payloads.

    Neither source is complete on its own: box scores give the lineup slot,
    the opponent, and the opponent-defense rank but return -1 for ownership;
    `team.roster` has real ownership and season stats but no per-week slot.
    Take the box lineup and backfill from the roster by player id.
    """
    by_id = {getattr(p, "playerId", None): p for p in team.roster}

    lineup = None
    try:
        for box in league.box_scores(week=week):
            if getattr(box.home_team, "team_id", None) == team.team_id:
                lineup = list(box.home_lineup)
                break
            if getattr(box.away_team, "team_id", None) == team.team_id:
                lineup = list(box.away_lineup)
                break
    except Exception:
        lineup = None

    if lineup is None:
        return list(team.roster)

    for bp in lineup:
        base = by_id.get(getattr(bp, "playerId", None))
        if base is None:
            continue
        for attr in ("percent_owned", "percent_started", "posRank", "avg_points", "total_points"):
            value = getattr(base, attr, None)
            if value is not None and not (isinstance(value, (int, float)) and value < 0):
                setattr(bp, attr, value)
    return lineup


# ------------------------------------------------------------------ commands


def cmd_roster(league, cfg, args) -> None:
    week = current_week(league, cfg, args.week)
    # `snapshot` reuses this command, and its subparser has no --team.
    team_id = getattr(args, "team", None)
    team = (
        get_my_team(league, cfg)
        if not team_id
        else next((t for t in league.teams if t.team_id == team_id), None)
    )
    if team is None:
        raise ConfigError(f"No team with id {team_id} in this league.")

    rows = [player_row(p, week) for p in roster_players(league, team, week)]
    starters = [r for r in rows if r["slot"] not in BENCH_SLOTS]
    bench = [r for r in rows if r["slot"] in BENCH_SLOTS]
    starters.sort(key=lambda r: SKILL_POSITIONS.index(r["pos"]) if r["pos"] in SKILL_POSITIONS else 99)
    bench.sort(key=lambda r: -(r["proj"] or 0))

    render.collect("week", week)
    render.collect("team", team.team_name)
    render.collect("starters", starters)
    render.collect("bench", bench)

    render.heading(f"{team.team_name} — week {week} starters")
    _player_table(starters)
    render.heading("Bench")
    _player_table(bench)

    flags = [(r["name"], flag_row(r)) for r in rows if flag_row(r)]
    if flags:
        render.heading("Needs attention")
        for name, why in flags:
            render.line(f"  {name}: {why}")


def _player_table(rows: List[Dict[str, Any]]) -> None:
    render.table(
        rows,
        ["slot", "name", "pos", "team", "opp", "oprk", "proj", "avg", "last3", "owned", "injury"],
        ["SLOT", "PLAYER", "POS", "TM", "OPP", "OPRK", "PROJ", "AVG", "LAST3", "OWN%", "STATUS"],
    )


def cmd_available(league, cfg, args) -> None:
    week = current_week(league, cfg, args.week)
    pos = normalize_position(args.pos)

    # Over-fetch so the projection sort has a real pool to work with; ESPN
    # returns free agents in its own order, not ours.
    pool = league.free_agents(week=week, size=max(args.n * 4, 60), position=pos)
    rows = [player_row(p, week) for p in pool]

    # Rank by this week's projection. The 2025 version sorted on season average,
    # which buries a just-promoted starter behind a fading veteran.
    rows.sort(key=lambda r: (r["proj"] if r["proj"] is not None else -1), reverse=True)
    rows = rows[: args.n]

    render.collect("week", week)
    render.collect("position", pos or "all")
    render.collect("free_agents", rows)

    render.heading(f"Top free agents — {pos or 'all positions'}, week {week}")
    render.table(
        rows,
        ["name", "pos", "team", "opp", "oprk", "proj", "avg", "last3", "owned", "started", "injury"],
        ["PLAYER", "POS", "TM", "OPP", "OPRK", "PROJ", "AVG", "LAST3", "OWN%", "ST%", "STATUS"],
    )
    render.line()
    render.line("Sorted by ESPN weekly projection for discovery, not recommendation priority.")
    render.line("Weigh opportunity/role first, health/matchup next, projections last; OWN% is market context.")
    render.line("Expand the pool and check role-change targets by name; usage metrics require web research.")
    render.line("OPRK is the opponent defense's rank vs this position (1-32, higher = softer).")


def cmd_owned(league, cfg, args) -> None:
    """Who rosters this player? Answers the question `is_available` couldn't."""
    week = current_week(league, cfg, args.week)
    needle = " ".join(args.name).strip().lower()

    for team in league.teams:
        for p in team.roster:
            if needle in p.name.lower():
                row = player_row(p, week)
                render.collect("player", row)
                render.collect("owner", team.team_name)
                render.heading(p.name)
                render.line(f"  rostered by: {team.team_name} (team_id {team.team_id})")
                render.line(f"  slot {row['slot']} · proj {render.fmt(row['proj'])} · vs {row['opp']}")
                return

    pool = league.free_agents(week=week, size=1000)
    for p in pool:
        if needle in p.name.lower():
            row = player_row(p, week)
            render.collect("player", row)
            render.collect("owner", None)
            render.heading(p.name)
            render.line("  FREE AGENT — available to add")
            render.line(f"  proj {render.fmt(row['proj'])} · vs {row['opp']} · owned {render.fmt(row['owned'])}%")
            return

    render.collect("player", None)
    render.heading(needle)
    render.line("  not found on any roster or in the free-agent pool")


def cmd_player(league, cfg, args) -> None:
    """Full player card: week-by-week actual vs projected."""
    week = current_week(league, cfg, args.week)
    name = " ".join(args.name).strip()

    player, owner = _find_player(league, name, week)
    if player is None:
        raise ConfigError(f"No player matching {name!r} on a roster or the wire.")

    row = player_row(player, week)
    history = []
    for wk in range(1, week + 1):
        st = week_stats(player, wk)
        if not st:
            continue
        history.append(
            {
                "week": wk,
                "opp": opponent(player, wk),
                "proj": st.get("projected_points"),
                "actual": st.get("points"),
                "diff": (
                    round(st["points"] - st["projected_points"], 1)
                    if st.get("points") is not None and st.get("projected_points") is not None
                    else None
                ),
            }
        )

    render.collect("player", row)
    render.collect("owner", owner)
    render.collect("history", history)

    render.heading(f"{player.name} — {row['pos']}, {row['team']}")
    render.line(f"  owner:     {owner or 'FREE AGENT'}")
    render.line(f"  week {week}:   vs {row['opp']} · proj {render.fmt(row['proj'])}")
    render.line(f"  season:    {render.fmt(getattr(player, 'total_points', None))} pts, "
                f"{render.fmt(row['avg'])} avg · pos rank {row['rank']}")
    render.line(f"  ownership: {render.fmt(row['owned'])}% rostered, {render.fmt(row['started'])}% started")
    if row["injury"]:
        render.line(f"  status:    {row['injury']}")

    render.heading("Week by week")
    render.table(
        history,
        ["week", "opp", "proj", "actual", "diff"],
        ["WK", "OPP", "PROJ", "ACTUAL", "+/-"],
    )


def _find_player(league, name: str, week: int):
    """Locate a player and their owner, preferring sources with weekly stats.

    `league.player_info()` looks like the obvious call but returns only season
    totals — its stats dict has no per-week entries, so a player card built
    from it is blank. Rostered Players and free-agent BoxPlayers both carry
    week-by-week scoring, so search those first.
    """
    needle = name.strip().lower()

    for team in league.teams:
        for p in team.roster:
            if needle in p.name.lower():
                return p, team.team_name

    try:
        for p in league.free_agents(week=week, size=1000):
            if needle in p.name.lower():
                return p, None
    except Exception:
        pass

    try:
        p = league.player_info(name=name)
        if isinstance(p, list):
            p = p[0] if p else None
        if p:
            return p, None
    except Exception:
        pass
    return None, None


def cmd_matchup(league, cfg, args) -> None:
    week = current_week(league, cfg, args.week)
    my_team = get_my_team(league, cfg)

    try:
        boxes = league.box_scores(week=week)
    except Exception as exc:
        raise ConfigError(f"box scores unavailable for week {week}: {exc}")

    box = next(
        (
            b
            for b in boxes
            if getattr(b.home_team, "team_id", None) == my_team.team_id
            or getattr(b.away_team, "team_id", None) == my_team.team_id
        ),
        None,
    )
    if box is None:
        render.heading(f"Week {week}")
        render.line("  no matchup found (bye week, or the schedule isn't posted yet)")
        return

    mine_is_home = getattr(box.home_team, "team_id", None) == my_team.team_id
    me, them = (
        (box.home_team, box.away_team) if mine_is_home else (box.away_team, box.home_team)
    )
    my_score, their_score = (
        (box.home_score, box.away_score) if mine_is_home else (box.away_score, box.home_score)
    )
    my_lineup, their_lineup = (
        (box.home_lineup, box.away_lineup) if mine_is_home else (box.away_lineup, box.home_lineup)
    )

    def summarize(lineup):
        rows = []
        for p in lineup:
            if getattr(p, "slot_position", "") in BENCH_SLOTS:
                continue
            rows.append(
                {
                    "slot": getattr(p, "slot_position", ""),
                    "name": p.name,
                    "team": getattr(p, "proTeam", "?"),
                    "proj": getattr(p, "projected_points", None),
                    "actual": getattr(p, "points", None),
                }
            )
        return rows

    mine, theirs = summarize(my_lineup), summarize(their_lineup)
    my_proj = sum(r["proj"] or 0 for r in mine)
    their_proj = sum(r["proj"] or 0 for r in theirs)

    render.collect("week", week)
    render.collect("me", {"team": me.team_name, "score": my_score, "projected": round(my_proj, 1), "lineup": mine})
    render.collect("opponent", {"team": them.team_name, "score": their_score, "projected": round(their_proj, 1), "lineup": theirs})

    render.heading(f"Week {week}: {me.team_name} vs {them.team_name}")
    render.line(f"  live:      {my_score:.1f} — {their_score:.1f}")
    render.line(f"  projected: {my_proj:.1f} — {their_proj:.1f}   ({my_proj - their_proj:+.1f})")
    posture = "favored — prioritize floor" if my_proj >= their_proj else "underdog — prioritize ceiling"
    render.line(f"  posture:   {posture}")

    render.heading("My lineup")
    render.table(mine, ["slot", "name", "team", "proj", "actual"], ["SLOT", "PLAYER", "TM", "PROJ", "PTS"])
    render.heading(f"{them.team_name}")
    render.table(theirs, ["slot", "name", "team", "proj", "actual"], ["SLOT", "PLAYER", "TM", "PROJ", "PTS"])


def cmd_rosters(league, cfg, args) -> None:
    """Every team's roster plus positional surplus/need — the trade skill's input."""
    week = current_week(league, cfg, args.week)
    slots = _starting_slots(league)
    replacement = _replacement_levels(league, slots, week)

    teams_out = []
    for team in sorted(league.teams, key=lambda t: t.team_id):
        rows = [player_row(p, week) for p in team.roster]
        counts: Dict[str, int] = {}
        for r in rows:
            counts[r["pos"]] = counts.get(r["pos"], 0) + 1

        surplus, need = [], []
        for pos in ("QB", "RB", "WR", "TE"):
            required = slots.get(pos, 0)
            if not required:
                continue
            startable = sum(
                1
                for r in rows
                if r["pos"] == pos and (r["proj"] or 0) >= replacement[pos]
            )
            if startable > required:
                surplus.append(f"{pos}+{startable - required}")
            elif startable < required:
                need.append(pos)

        teams_out.append(
            {
                "team_id": team.team_id,
                "team": team.team_name,
                "record": f"{team.wins}-{team.losses}",
                "counts": counts,
                "surplus": surplus,
                "need": need,
                "roster": rows,
            }
        )

    render.collect("week", week)
    render.collect("starting_slots", slots)
    render.collect("teams", teams_out)

    render.heading(f"League rosters — week {week}")
    render.table(
        [
            {
                "id": t["team_id"],
                "team": t["team"],
                "rec": t["record"],
                "qb": t["counts"].get("QB", 0),
                "rb": t["counts"].get("RB", 0),
                "wr": t["counts"].get("WR", 0),
                "te": t["counts"].get("TE", 0),
                "surplus": ", ".join(t["surplus"]) or "-",
                "need": ", ".join(t["need"]) or "-",
            }
            for t in teams_out
        ],
        ["id", "team", "rec", "qb", "rb", "wr", "te", "surplus", "need"],
        ["ID", "TEAM", "REC", "QB", "RB", "WR", "TE", "SURPLUS", "THIN AT"],
    )

    for t in teams_out:
        render.heading(f"[{t['team_id']}] {t['team']} ({t['record']})")
        render.table(
            sorted(t["roster"], key=lambda r: (r["pos"], -(r["proj"] or 0))),
            ["name", "pos", "team", "proj", "avg", "owned", "injury"],
            ["PLAYER", "POS", "TM", "PROJ", "AVG", "OWN%", "STATUS"],
        )


# A flex slot is filled by an RB, WR, or TE in roughly these proportions.
# Used only to size the startable pool at each position.
FLEX_SHARE = {"RB": 0.4, "WR": 0.5, "TE": 0.1}


def _replacement_levels(league, slots: Dict[str, int], week: int) -> Dict[str, float]:
    """The projection of the last startable player at each position, league-wide.

    A player is worth his margin over replacement, not his raw points — so
    "surplus" has to mean startable depth beyond the slots available, not just
    a big roster. Counting bodies instead flags every team carrying a backup QB
    in a 1-QB league as having a QB surplus, and every 1-QB team as thin.

    Sizing off the league's own settings also makes this self-correcting: a
    12-team league has a higher replacement level than a 10-team one.
    """
    n_teams = len(league.teams) or 1
    flex_total = sum(v for k, v in slots.items() if "/" in k)

    pool: Dict[str, List[float]] = {}
    for team in league.teams:
        for p in team.roster:
            pos = getattr(p, "position", None)
            if pos in ("QB", "RB", "WR", "TE"):
                pool.setdefault(pos, []).append(week_stats(p, week).get("projected_points") or 0.0)

    levels: Dict[str, float] = {}
    for pos in ("QB", "RB", "WR", "TE"):
        starters = (slots.get(pos, 0) + flex_total * FLEX_SHARE.get(pos, 0)) * n_teams
        projections = sorted(pool.get(pos, []), reverse=True)
        index = max(int(round(starters)) - 1, 0)
        levels[pos] = projections[index] if index < len(projections) else 0.0
    return levels


def _starting_slots(league) -> Dict[str, int]:
    """Required starters per position, from league settings."""
    counts = getattr(getattr(league, "settings", None), "position_slot_counts", {}) or {}
    return {k: int(v) for k, v in counts.items() if v and k not in BENCH_SLOTS}


def cmd_league(league, cfg, args) -> None:
    week = current_week(league, cfg, args.week)
    rows = []
    for i, team in enumerate(league.standings(), start=1):
        rows.append(
            {
                "rk": i,
                "id": team.team_id,
                "team": team.team_name,
                "rec": f"{team.wins}-{team.losses}",
                "pf": round(getattr(team, "points_for", 0), 1),
                "pa": round(getattr(team, "points_against", 0), 1),
            }
        )

    power = []
    try:
        for score, team in league.power_rankings(week=max(week - 1, 1)):
            power.append({"score": score, "team": team.team_name})
    except Exception:
        pass

    render.collect("standings", rows)
    render.collect("power_rankings", power)

    render.heading("Standings")
    render.table(rows, ["rk", "id", "team", "rec", "pf", "pa"], ["#", "ID", "TEAM", "REC", "PF", "PA"])
    if power:
        render.heading("Power rankings")
        render.table(power, ["score", "team"], ["SCORE", "TEAM"])


def cmd_transactions(league, cfg, args) -> None:
    """What rivals are doing — the waiver market in motion."""
    try:
        activity = league.recent_activity(size=args.n)
    except Exception as exc:
        raise ConfigError(f"activity unavailable: {exc}")

    rows = []
    for item in activity:
        for team, action, player, bid in _unpack_actions(item.actions):
            rows.append(
                {
                    "team": getattr(team, "team_name", str(team)),
                    "action": action,
                    "player": getattr(player, "name", str(player)),
                    "bid": bid or None,
                }
            )

    render.collect("transactions", rows)
    render.heading(f"Recent league activity (last {args.n})")
    render.table(rows, ["team", "action", "player", "bid"], ["TEAM", "ACTION", "PLAYER", "FAAB"])


def _unpack_actions(actions):
    """espn-api action tuples are (team, action, player) or (..., bid)."""
    for action in actions:
        if len(action) >= 4:
            yield action[0], action[1], action[2], action[3]
        else:
            yield action[0], action[1], action[2], None


def cmd_snapshot(league, cfg, args) -> None:
    """The composite entry point — one call, the whole week."""
    week = current_week(league, cfg, args.week)
    render.line(f"CommishAI — {cfg['year']} week {week}, {cfg.get('scoring', 'PPR')}")

    cmd_matchup(league, cfg, args)
    cmd_roster(league, cfg, args)

    fa_by_pos = {}
    render.heading("Top free agents by position")
    for pos in SKILL_POSITIONS:
        try:
            pool = league.free_agents(week=week, size=25, position=pos)
        except Exception:
            continue
        rows = [player_row(p, week) for p in pool]
        rows.sort(key=lambda r: (r["proj"] if r["proj"] is not None else -1), reverse=True)
        rows = rows[:5]
        fa_by_pos[pos] = rows
        render.line(f"\n  {pos}")
        render.table(
            rows,
            ["name", "team", "opp", "oprk", "proj", "avg", "owned"],
            ["PLAYER", "TM", "OPP", "OPRK", "PROJ", "AVG", "OWN%"],
        )
    render.collect("free_agents_by_position", fa_by_pos)


def cmd_review(league, cfg, args) -> None:
    """Grade a past week: what the lineup scored vs. what the bench would have."""
    week = args.week or max(current_week(league, cfg, None) - 1, 1)
    my_team = get_my_team(league, cfg)

    try:
        league.load_roster_week(week)
    except Exception:
        pass

    boxes = league.box_scores(week=week)
    box = next(
        (b for b in boxes
         if my_team.team_id in (getattr(b.home_team, "team_id", None), getattr(b.away_team, "team_id", None))),
        None,
    )
    if box is None:
        raise ConfigError(f"No box score for week {week}.")

    mine_is_home = getattr(box.home_team, "team_id", None) == my_team.team_id
    lineup = box.home_lineup if mine_is_home else box.away_lineup
    my_score = box.home_score if mine_is_home else box.away_score
    their_score = box.away_score if mine_is_home else box.home_score

    started, benched = [], []
    for p in lineup:
        row = {
            "slot": getattr(p, "slot_position", ""),
            "name": p.name,
            "pos": getattr(p, "position", "?"),
            "proj": getattr(p, "projected_points", None),
            "actual": getattr(p, "points", None),
        }
        (benched if row["slot"] in BENCH_SLOTS else started).append(row)

    # Bench players who outscored a starter at a position they could have filled.
    misses = []
    for b in benched:
        for s in started:
            if b["pos"] == s["pos"] and (b["actual"] or 0) > (s["actual"] or 0):
                misses.append(
                    {
                        "benched": b["name"],
                        "benched_pts": b["actual"],
                        "started": s["name"],
                        "started_pts": s["actual"],
                        "cost": round((b["actual"] or 0) - (s["actual"] or 0), 1),
                    }
                )
                break

    misses.sort(key=lambda m: -m["cost"])
    left_on_bench = round(sum(m["cost"] for m in misses), 1)

    render.collect("week", week)
    render.collect("score", {"me": my_score, "opponent": their_score})
    render.collect("started", started)
    render.collect("misses", misses)
    render.collect("points_left_on_bench", left_on_bench)

    render.heading(f"Week {week} review")
    if my_score == 0 and their_score == 0:
        render.line(f"  week {week} has not been played yet — nothing to grade")
        render.flush()
        return
    outcome = "WIN" if my_score > their_score else "TIE" if my_score == their_score else "LOSS"
    render.line(f"  {outcome} {my_score:.1f} — {their_score:.1f}")
    render.line(f"  points left on bench: {left_on_bench}")

    render.heading("Started")
    render.table(started, ["slot", "name", "proj", "actual"], ["SLOT", "PLAYER", "PROJ", "PTS"])
    if misses:
        render.heading("Start/sit misses")
        render.table(
            misses,
            ["started", "started_pts", "benched", "benched_pts", "cost"],
            ["STARTED", "PTS", "SHOULD HAVE", "PTS", "COST"],
        )

    log = client.REPO_ROOT / "decisions" / f"{cfg['year']}-wk{week:02d}.md"
    if log.exists():
        render.line(f"\nDecision log for this week: {log}")


def cmd_doctor(league, cfg, args) -> None:
    """Validate config, auth, and connectivity with actionable errors."""
    render.heading("Configuration")
    render.line(f"  league_id: {cfg['league_id']}")
    render.line(f"  team_id:   {cfg['team_id']}")
    render.line(f"  year:      {cfg['year']}")
    render.line(f"  cookies:   {'set' if cfg.get('espn_s2') and cfg.get('swid') else 'NOT SET (fine for public leagues)'}")

    render.heading("Connection")
    render.line(f"  league:       {getattr(league.settings, 'name', '?')}")
    render.line(f"  teams:        {len(league.teams)}")
    render.line(f"  current week: {getattr(league, 'current_week', '?')}")

    slots = _starting_slots(league)
    render.line(f"  starting slots: {', '.join(f'{k}x{v}' for k, v in sorted(slots.items()))}")

    render.heading("Teams")
    render.table(
        [{"id": t.team_id, "team": t.team_name, "rec": f"{t.wins}-{t.losses}"} for t in league.teams],
        ["id", "team", "rec"],
        ["ID", "TEAM", "REC"],
    )

    try:
        me = get_my_team(league, cfg)
        render.line(f"\nOK — configured team resolves to: {me.team_name} ({len(me.roster)} players)")
    except ConfigError as exc:
        render.line(f"\nPROBLEM — {exc}")


# --------------------------------------------------------------------- main

COMMANDS = {
    "snapshot": cmd_snapshot,
    "roster": cmd_roster,
    "player": cmd_player,
    "available": cmd_available,
    "owned": cmd_owned,
    "matchup": cmd_matchup,
    "rosters": cmd_rosters,
    "league": cmd_league,
    "transactions": cmd_transactions,
    "review": cmd_review,
    "doctor": cmd_doctor,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ff.py", description=__doc__.split("\n")[0])
    parser.add_argument("--json", action="store_true", help="emit JSON instead of tables")
    parser.add_argument("--week", type=int, help="week to report on (default: current)")
    parser.add_argument("--fresh", action="store_true", help="bypass the 15-minute league cache")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("snapshot", help="roster + matchup + free agents in one call (start here)")

    p = sub.add_parser("roster", help="a team's roster with projections")
    p.add_argument("--team", type=int, help="team id (default: yours)")

    p = sub.add_parser("player", help="full player card, week by week")
    p.add_argument("name", nargs="+")

    p = sub.add_parser("available", help="free agents ranked by weekly projection")
    p.add_argument("--pos", help="QB, RB, WR, TE, K, D/ST")
    p.add_argument("--n", type=int, default=15)

    p = sub.add_parser("owned", help="which team rosters a player")
    p.add_argument("name", nargs="+")

    sub.add_parser("matchup", help="this week's head-to-head with both lineups")
    sub.add_parser("rosters", help="all teams' rosters + positional surplus/need")
    sub.add_parser("league", help="standings and power rankings")

    p = sub.add_parser("transactions", help="recent league adds, drops, and trades")
    p.add_argument("--n", type=int, default=25)

    sub.add_parser("review", help="grade a past week's lineup against the bench")
    sub.add_parser("doctor", help="validate config, auth, and connectivity")
    return parser


def _force_utf8() -> None:
    """Windows consoles default to cp1252 and mangle the em-dashes we print."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def main(argv: Optional[List[str]] = None) -> int:
    _force_utf8()
    args = build_parser().parse_args(argv)
    render.set_json_mode(args.json)

    try:
        cfg = load_config()
        league = get_league(cfg, fresh=args.fresh)
        COMMANDS[args.command](league, cfg, args)
    except ConfigError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130

    render.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
