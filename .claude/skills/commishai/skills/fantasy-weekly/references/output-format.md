# Output format

End every weekly session with this block. No scratchpad reasoning inside it — the
analysis happens before, the block states conclusions and the reason for each.

```
== WEEK <N> RECOMMENDATIONS: COMMISH ==

MATCHUP: vs <opponent team>  ·  projected <mine> — <theirs>  ·  <favored|underdog>
POSTURE: <floor|ceiling> — <one clause on why>

ROSTER MOVES
  ADD    <Player>, <POS>  (<FAAB or waiver priority>)
         <one line: the reason, tied to a heuristic>
  DROP   <Player>, <POS>
         <one line: why he's the cut, and why not someone else>

  (or: "No moves. Roster is optimized." — say it plainly when it's true.)

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

Match the lineup slots to the actual league settings — `ff.py doctor` prints them.
Don't emit a FLEX row for a league without one.

Every start/sit justification carries at least one **number**: a snap share, an implied
total, a target share, a projection margin. "Better matchup" is not a justification;
"opponent allows the 3rd-most PPR points to WRs, and he ran 89% of routes last week" is.

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
