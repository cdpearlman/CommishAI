# Research playbook

`ff.py` gives you ESPN's own numbers — roster, projections, ownership, scoring history.
Everything ESPN *doesn't* know (news, snap counts, advanced metrics, betting lines)
comes from the web. This is how to get it without wasting calls.

## When to search at all

Search only for decisions the snapshot leaves genuinely open:

- A questionable/doubtful tag on someone you plan to start
- A FLEX or WR3 call where the projections are within ~2 points
- A waiver target you're considering spending real FAAB on
- A streaming slot (D/ST, K, TE) where the whole decision is matchup
- A player whose role may have just changed (injury ahead of him, trade, new coach)

Do not research a decision the projections already settle by 6+ points. Do not research
every starter. One search that changes a decision beats ten that confirm one.

## Check the CLI first

Two things you might reach for the web to get are already in `ff.py` output:

- **`OPRK`** — ESPN's rank of the opposing defense against that player's position,
  1–32, higher meaning a softer matchup. It appears in `roster`, `available`, and
  `snapshot`. It is empty in week 1, because ranking defenses against positions
  requires games to have been played; expect it from week 2 on.
- **`OWN%`** — rostered percentage across ESPN. A big gap between a high `PROJ` and a
  low `OWN%` is the waiver signal worth acting on before the rest of your league does.

Use those before searching for matchup difficulty or waiver consensus.

## Sources

Prefer these with `WebSearch`'s `allowed_domains`, or `WebFetch` them directly.

**Tier 1 — lead with these.** `fantasypros.com` (consensus rankings — the single most
useful page, it aggregates ~100 experts), `rotowire.com` (fastest injury and practice
reports), `espn.com`, `nfl.com`, `playerprofiler.com` (advanced metrics),
`ftnfantasy.com` (DVOA), `nbcsports.com`, `sports.yahoo.com`.

**Tier 2 — corroborate with these.** `cbssports.com`, `rotoballer.com`,
`footballguys.com`, `pff.com`, `sharpfootballanalysis.com`.

**Never cite.** `reddit.com`, `twitter.com`/`x.com`, `facebook.com`, `instagram.com`.
Anonymous takes and beat-writer speculation dressed as news. If a claim only exists on
social media, treat it as a rumor and say so.

Always note how fresh a source is. A Tuesday ranking is stale by Sunday, and injury
news from before the final Friday practice report is worth very little.

## Position-specific metrics

Ask for the metric that actually predicts the position. Generic "is X a good start"
searches return generic answers.

| Position | Metrics that matter | Why |
|---|---|---|
| QB | CPOE, pass attempts, rushing attempts | Rushing floor is what separates fantasy QBs; CPOE isolates accuracy from receiver play |
| RB | Snap %, carry share, RYOE, MTF/touch, routes run | Passing-down work is the difference between an RB2 and a flex dart |
| WR | Target share, route participation %, air yards share, YPRR, WOPR | WOPR combines target and air-yards share — the best single opportunity number |
| TE | Route participation %, target share, red-zone looks | TE scoring is touchdown-dependent; red-zone role is the tell |
| D/ST | Opponent implied total, opponent turnover rate, opponent OL injuries | You are betting against a specific offense, not for a defense |
| K | Team implied total, dome/weather, offense's red-zone efficiency | A good offense that stalls inside the 30 is the ideal kicker spot |

## Query patterns that work

```
"<player>" snap share target share week <N> 2026
"<player>" injury practice report week <N>          # Rotowire, Wed–Fri
"<team> defense" vs <position> rankings 2026        # the matchup, not the record
week <N> NFL implied team totals odds               # scoring environment
week <N> waiver wire pickups <position>             # consensus adds
"<player>" rest of season outlook                   # before any drop decision
```

For injuries, the useful question is never "is he hurt" — it's **did he practice, and
in what capacity**. DNP Wednesday through Friday means he is very likely out regardless
of the official tag. Full participation Friday with a questionable tag usually means he
plays.

## Betting lines

Implied total = (over/under ÷ 2) ± (spread ÷ 2). A 49-point total with a team favored
by 7 gives that team 28 implied points — a strong offensive environment. Under 20
implied is a real reason to bench a borderline starter. This is heuristic 6, and it's
usually the fastest way to break a tie between two similar players.

## Weighing what you find

Volume and role beat pundit opinion. If the snap share says a player is a full-time
starter and an article calls him a "committee back," believe the snaps. Rankings are
useful as a consensus check, not as an answer — when your read differs from consensus,
that's worth stating explicitly along with why, rather than quietly deferring.
