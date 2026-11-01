# CommishAI 2026

An ESPN fantasy football manager packaged as skills for Claude Code, ChatGPT, and
Codex.

The [2025 version](https://github.com/cdpearlman/CommishAI) was an MCP server: 12 thin
tools, a Tavily API key, and all the strategy stuffed into an always-on Cursor rule.
This is the same idea rebuilt for skills — the tools are a Python CLI, the strategy
lives in skill files that load only when relevant, and web research uses the host
model's built-in search instead of a paid API.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env          # then paste in your ESPN cookies
```

Fill in `league.yaml` with your `league_id` (from your league URL) and `team_id`, then:

```bash
python .claude/skills/commishai/scripts/ff.py doctor
```

That validates config and auth, and lists every team id.

## Using it with ChatGPT or Codex

The OpenAI-compatible package lives at `plugins/commishai/`. Its portable root
`plugin.json` works across Agent Plugin hosts, while `.codex-plugin/plugin.json`
provides OpenAI presentation metadata. The repo-local marketplace at
`.agents/plugins/marketplace.json` exposes it for local installation and testing.

After installing the repo marketplace in the ChatGPT desktop app, ask:

> set my lineup for this week

The local package uses the same `league.yaml`, `.env`, and `decisions/` files at the
repository root. ESPN credentials remain local. A public web deployment will require
a hosted MCP service rather than local `.env` credentials.

## Using it with Claude Code

Open Claude Code **in this directory** and ask for what you want:

> set my lineup for this week

The plugin lives at `.claude/skills/commishai/`, which Claude Code auto-loads as a
skills-directory plugin — no install step and no `--plugin-dir` flag. You'll be asked
to trust the workspace the first time. Launch from the repo root; project-scope plugins
don't load from a subdirectory.

To use it from any directory instead of just this one, move
`.claude/skills/commishai/` to `~/.claude/skills/commishai/` and leave `league.yaml`
and `.env` where they are — the CLI finds them either way.

## Skills

**`fantasy-weekly`** — start/sit, waivers, add/drop, injuries. Triggers on "set my
lineup", "who should I start", "waiver wire", "should I drop X".

**`fantasy-trades`** — evaluate offers, find trade fits across the league, draft the
offer and the pitch. Triggers on anything trade-shaped.

Both read from `scripts/ff.py` and carry their strategy in `references/`. Skills are
namespaced, so you can also invoke one directly as `/commishai:fantasy-weekly`.

## CLI

`ff.py` is useful on its own, at `plugins/commishai/scripts/ff.py`. Every
command takes `--json`, `--week N`, and `--fresh` (bypasses the 15-minute cache).

| Command | What it does |
|---|---|
| `snapshot` | Matchup, roster, injuries, and top free agents in one call — start here |
| `roster [--team ID]` | A roster with weekly projections, last-3 scores, and status |
| `player "Name"` | Player card with week-by-week actual vs. projected |
| `available --pos RB` | Free agents ranked by **this week's projection** |
| `owned "Name"` | Which team rosters a player |
| `matchup` | Head-to-head with both lineups and the projected margin |
| `rosters` | Every team's roster plus positional surplus/need |
| `league` | Standings and power rankings |
| `transactions` | Recent league adds, drops, and trades |
| `review --week N` | Grades a past week's lineup against the bench |
| `doctor` | Validates config, auth, connectivity |

## Notes

**Player evaluation.** Weigh opportunity and role first, health and matchup second,
then projections and expert rankings as a cross-check. Research close decisions,
proposed adds/drops, streamers, and changed roles with explicit position-specific
metric searches: touches/carry share and receiving work for RBs; routes, target share,
air yards and red-zone work for WRs/TEs; passing/rushing volume for QBs. CPOE, RYOE,
missed tackles per touch, YPRR and WOPR provide supporting context. D/ST and K lead
with matchup and scoring environment. Compare dated evidence for both players and
flag missing metrics; no fixed weighted player score is calculated.

The CLI provides ESPN fantasy data, not an advanced usage feed. Its free-agent lists
are sorted by weekly projection for discovery, not by final recommendation priority.
Expand beyond the top-five snapshot and check researched targets by name. Detailed
search and weighting guidance lives in the weekly skill's `references/research.md`
and `references/heuristics.md`; the trade skill uses the same evidence hierarchy.

**Weekly waiver strategy.** Recommend one numbered claim queue across all positions,
best option first and lowest priority last. Rank net roster improvement, current
needs, rest-of-season upside, and replacement scarcity—not position order or weekly
projection alone. Use this league's draft-order waiver priority rather than assumed
FAAB. Each claim names its drop; fallback-only claims are clearly labeled and reuse
the intended drop. Refresh availability after processing. Full strategy lives in
the weekly skill's `references/heuristics.md` across all three local packages.

**Read-only.** `espn-api` has no write endpoints — nothing here can set a lineup or
process a transaction. The output is a recommendation you execute in the ESPN app.

**Cookies expire.** If commands start failing auth mid-season, re-copy `ESPN_S2` and
`SWID` into `.env`. `ff.py doctor` will tell you that's what happened.

**Decisions are logged.** Each week's recommendation lands in `decisions/`, and
`ff.py review` grades it the following week — so the season produces a record of
whether the reads were actually good.
