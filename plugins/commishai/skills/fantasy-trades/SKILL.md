---
name: fantasy-trades
description: Evaluate and construct ESPN fantasy football trades — judge a proposed offer, find which rival teams need what you have, value players rest-of-season, and draft the offer and the pitch message. Use whenever the user asks about trading, a trade offer they received or want to send, whether a trade is fair, who to trade for or away, or which teams need a position.
---

# Commish — trade analysis

Trades are the highest-leverage move in fantasy and the easiest to lose. Two rules
frame everything below: **value players on what they'll do from here, not what they've
already banked**, and **a trade only happens if it's good for the other manager too** —
your job is to find the deal where both sides improve, not to fleece someone.

**You cannot execute trades.** `espn-api` is read-only. You produce the offer and the
message; the manager sends it in the ESPN app.

## Gather

```bash
python ${PLUGIN_ROOT}/scripts/ff.py rosters    # every team + surplus/need
python ${PLUGIN_ROOT}/scripts/ff.py league     # standings — who's buying, who's selling
```

`rosters` prints a summary table with each team's positional surplus and where they're
thin, computed against the league's actual starting requirements. That table is the
trade market. Follow up with `ff.py player "Name"` for anyone on either side of a
serious offer. Actual-vs-projected history identifies questions; it does not establish
whether a hot start is sustainable. Before valuing either side, read
`../fantasy-weekly/references/research.md` for metric-specific searches and evidence
quality. Compare opportunity and role first, health and remaining matchups second,
then use rest-of-season projections/rankings as a cross-check. Gather the relevant
usage metrics for both sides and distinguish persistent roles from temporary fills.

`ff.py transactions` is worth a look too: a manager who just burned FAAB on a backup RB
is telling you where they think they're weak.

## Evaluating an offer you received

1. **Value both sides rest-of-season.** Ignore points already scored. What matters is
   each player's role from here, remaining schedule, and health.
2. **Count the starting lineup and useful depth.** Evaluate expected starts before and
   after, replacement value, injury/bye coverage, and the reliability of each role.
   Projected lineup improvement is a check, not the sole measure of trade value.
3. **Check the roster-slot cost.** 2-for-1 consolidation improves your starters but
   forces a drop; make sure the player you'd cut isn't worth more than the upgrade.
4. **Ask why they want it.** The other manager has a read. If they're selling a player
   who just got a workload bump, find out whether there's news you're missing.
5. **Check the playoff weeks.** A player with a brutal weeks 15–17 schedule is worth
   less to a contender than his season-long value suggests.

Then say plainly: accept, decline, or counter — and if counter, give the exact counter.

## Constructing an offer

Find the complementary fit: a team with surplus at your position of need *and* need at
your position of surplus. Both halves are required — a team with a spare RB2 who is
already deep at WR has no reason to talk to you.

Read the standings for posture. A contender pays a premium for win-now certainty and
will overpay for a proven starter. A team out of the race will take upside and youth.
Sell your volatile boom/bust player to the desperate team; buy the steady producer from
the team that's given up.

Lead with an offer that's *visibly* good for them — name the need it fills in the
pitch. A lowball first offer mostly teaches the other manager not to reply.

Draft the actual message: short, specific about why it helps them, no fake urgency.

See `references/trade-heuristics.md` for valuation mechanics — buy-low and sell-high
triggers, positional scarcity, and how to weight the playoff schedule.

## Output

State the recommendation first, then the reasoning:

```
VERDICT: <Accept | Decline | Counter>

You get:   <players>  →  +<x> proj pts/wk to your starting lineup
You give:  <players>  →  −<y> proj pts/wk
Net:       <+/− z> per week, plus <roster-slot / bye / playoff-schedule note>

WHY
  - <evidence with a number>
  - <evidence with a number>

<If counter:>
COUNTER: you send <players>, you receive <players>
PITCH: "<the message to send, 2–4 sentences>"
```

Always name the risk you're accepting — the injury history, the schedule, the
role that might not hold. A trade recommendation without a stated downside is
incomplete.

Support consequential valuations with dated opportunity metrics for both sides,
including recent trends and role durability. Explain any disagreement with projections
or ROS rankings. Label unavailable metrics and provisional conclusions; use a range
or qualitative improvement when a precise points-per-week estimate is unsupported.
