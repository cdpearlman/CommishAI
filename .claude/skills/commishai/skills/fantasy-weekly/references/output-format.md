# Output format

End every weekly session with this block. No scratchpad reasoning inside it — the
analysis happens before, the block states conclusions and the reason for each.

```
== WEEK <N> RECOMMENDATIONS: COMMISH ==

MATCHUP: vs <opponent team>  ·  projected <mine> — <theirs>  ·  <favored|underdog>
POSTURE: <floor|ceiling> — <one clause on why>

RANKED ADDS: <best target first>
RANKED DROPS: <first cut first; stop at last acceptable cut>

ROSTER MOVES — SUBMISSION ORDER
  1. ADD <Player>, <POS>  (<preferred, fallback, or additional acquisition; claim or free agent>)
         <one line: the reason, tied to a heuristic>
  DROP   <Player>, <POS>
         <one line: why he's the cut, and why not someone else>

  (or: "No moves. Roster is optimized." — say it plainly when it's true.)

CLAIM OUTCOMES: <acquired targets -> exact cuts; include partial/no wins>

STARTING LINEUP
  QB     <Player>
  RB     <Player>
  RB     <Player>
  WR     <Player>
  WR     <Player>
  TE     <Player>
  FLEX   <Player>
  D/ST   <Team>
  K      <Player>

KEY DECISIONS
  <Player A> over <Player B> at <slot>
    - <evidence, with the number>
    - <evidence, with the number>
    - <the heuristic that settles it>

WATCH LIST
  <Player>: <what to check and when — e.g. "Fri practice report; if DNP, start X">
```

## Rules

Show ranked cross-position adds and ranked drops (first cut first), then the complete
numbered claim queue in submission order. Use the strategy in `heuristics.md`, name
the exact drop on every row, and label preferred, fallback and additional-acquisition
claims. Repeat an add with successive drops when needed. Include a compact outcome
summary showing the cuts if both/all targets win, only one wins, or none wins; verify
each outcome respects the intended drop order and acceptable roster combinations.
Do not describe eligible later claims as guaranteed awards. Use FAAB only when the
league actually uses it. Record the rankings, final queue, intended outcomes and
successful/missed claims in the decision log.

Match the lineup slots to the actual league settings — `ff.py doctor` prints them.
Don't emit a FLEX row for a league without one.

Every start/sit justification carries at least one **number**: a snap share, an implied
total, a target share, a projection margin. "Better matchup" is not a justification;
"opponent allows the 3rd-most PPR points to WRs, and he ran 89% of routes last week" is.

For close starts and proposed adds/drops, compare opportunity evidence for both
players before quoting projections. Include the metric, timeframe, dated source,
and why the role should persist. Separate efficiency from volume and weekly value
from rest-of-season value. Explain projection overrides without invented numerical
weights. A projection margin alone is not a complete researched justification.

If comparable usage metrics cannot be found, say which are missing, label the call
provisional, and name the evidence that could change it. Never replace a missing
metric with zero or present season averages as current role evidence. Keep obvious
starts concise; reserve detailed evidence for decisions that affect the recommendation.

Flag anything genuinely uncertain in the watch list with the trigger and the fallback,
rather than burying a hedge inside a recommendation. A manager should be able to act on
this block Sunday morning without re-reading the analysis.

State plainly that these are recommendations to execute in the ESPN app — nothing here
sets a lineup.

## Decision log

Append the same content, condensed, to `decisions/<year>-wk<NN>.md`:

```markdown
# 2026 Week <N>

**Matchup:** vs <opponent> · projected <x> — <y>
**Lineup:** QB <p> · RB <p>, <p> · WR <p>, <p> · TE <p> · FLEX <p> · D/ST <t> · K <p>
**Moves:** ADD <p> ($<faab>) / DROP <p>

## <Decision: Player A over Player B at FLEX>
- <evidence>
- <evidence>
- <heuristic applied>
```

Keep it to six bullets per decision. `ff.py review --week <N>` reads the scoreboard
against this next week, so the value is in recording *what you believed and why*, not
in restating the box score.

Use claim order instead of FAAB amounts for this league. Within the six-bullet limit,
record opportunity evidence for both sides, dates/windows and sources, health/matchup,
projection agreement or override, and missing evidence/confidence. Save the log in
the project-root `decisions/` directory beside `league.yaml`, not inside the skill.
