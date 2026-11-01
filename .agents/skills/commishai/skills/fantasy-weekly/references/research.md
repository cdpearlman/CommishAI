# Research playbook

`ff.py` supplies ESPN roster, projections, ownership, opponent ranks and scoring
history. It does not supply structured advanced usage or efficiency data. Retrieve
those from dated web sources; do not imply the CLI calculated them.

## Research the decisions that matter

Investigate close start/sit calls, proposed adds and their exact drops, streamers,
new injuries, returning competition, and any materially changed role. A large
projection gap does not settle a role-change decision. Secure, healthy starters
with no credible challenger need no exhaustive research pass.

Expand the free-agent pool beyond the snapshot's top five at positions of need.
Search weekly injury/role changes to discover candidates, then check each candidate
with `ff.py owned "Name"` or an expanded `available` pool. ESPN projection ordering
can bury breakout players and temporary replacements. Ownership is an availability
and market signal, not a player-quality metric; OPRK is context, not a complete matchup.

For each consequential comparison:
1. Search for each player's opportunity metrics and what changed in their role.
2. Compare the latest game with the previous 3–4 games, where available; establish
   whether the role should persist and who could take work away.
3. Check health and expected workload, opponent strengths, and scoring environment.
4. Use efficiency and projections/rankings to cross-check the conclusion. Stop when
   evidence resolves the call; avoid repeated generic rankings searches.

## Position-specific evidence

| Position | Opportunity and role first | Supporting efficiency/context |
|---|---|---|
| QB | Pass attempts/dropbacks, designed rushes and total rushing attempts, red-zone rushing, starter/job security | CPOE (completion percentage over expected), pressure environment, opponent pass defense |
| RB | Carries and team RB carry share, offensive snap share, routes/route participation, targets, two-minute/third-down role, inside-10/goal-line touches | RYOE (rushing yards over expected), missed tackles forced per touch; line health, team total and game script |
| WR | Routes/route participation, targets and target share, air-yard share, red-zone targets, depth-chart and QB changes | YPRR (yards per route run), WOPR (weighted target and air-yard shares), opponent coverage and pass defense |
| TE | Routes/route participation, target share, red-zone/end-zone targets, receiving versus blocking role | YPRR and available WOPR; opponent TE coverage and team scoring environment |
| D/ST | Opponent implied total, sacks/pressure opportunities versus opponent sacks allowed, giveaways, QB/OL injuries | Defensive pressure/sack rate and opponent offensive efficiency/DVOA where available |
| K | Team implied total, field-goal attempts/opportunities, drives reaching scoring range, red-zone stalls, job security | Dome/wind/weather and distance usage under league scoring |

Snap share alone can mislead: an RB may pass protect and a TE may block. For PPR,
receiving opportunities can beat a modest carry advantage. WOPR overlaps target
and air-yard share; treat it as a summary, not an additional independent vote.
Efficiency measures do not establish workload. CPOE measures passing accuracy
relative to expectation, not fantasy rushing upside or overall decision-making.

## Metric-specific query patterns

Substitute the configured season from `league.yaml`, the requested week, and the
last completed week. Tuesday research normally uses last week's actual usage and
this week's health/matchup. Never hardcode 2025 or 2026 into reusable searches.
Use a player name plus one related metric group per query, not a bundle of every
advanced acronym. Search both sides of the comparison.

```text
QB opportunity:
"<player>" <season> week <last_completed> pass attempts dropbacks rushing attempts designed runs
QB efficiency:
"<player>" <season> CPOE completion percentage over expected

RB rushing role:
"<player>" <season> week <last_completed> carries snap share rushing attempts share
RB receiving/high-value work:
"<player>" <season> week <last_completed> routes targets third down goal line touches
RB efficiency (when role or sustainability is disputed):
"<player>" <season> rushing yards over expected RYOE
"<player>" <season> missed tackles forced per touch

WR/TE receiving role:
"<player>" <season> week <last_completed> routes route participation target share
WR/TE high-value opportunity:
"<player>" <season> week <last_completed> air yards share red zone targets
WR/TE efficiency and opportunity summary:
"<player>" <season> yards per route run YPRR
"<player>" <season> weighted opportunity rating WOPR

Role durability and health:
"<player>" <season> week <upcoming> depth chart workload <injured_or_returning_teammate>
"<player>" <season> <date> injury practice report limited full participation expected return
"<player>" <season> rest of season role <returning_teammate>

Matchup:
"<opponent>" <season> defense vs <position> target coverage efficiency DVOA
<team> <opponent> <season> week <upcoming> spread total odds

D/ST:
"<opponent>" <season> sacks allowed sack rate turnovers offensive line injury quarterback
"<defense>" <season> pressure rate sack rate
K:
"<kicker>" <season> field goal attempts red zone possessions
<stadium_city> <game_date> wind weather forecast
```

If an exact weekly metric is unavailable, try a season-to-date table, official game
book, or a focused source-domain query. Label that broader window explicitly. Do not
keep retrying unrelated generic start/sit articles or substitute consensus for usage.

## Sources and evidence quality

Prefer official NFL/team game books, injury/practice reports and stats; NFL Next Gen
Stats/NFL Pro for usage and efficiency; PlayerProfiler, FTN and PFF for attributed
advanced metrics; sportsbooks for current lines. ESPN, NBC, Rotowire and Yahoo can
provide dated player news. FantasyPros and expert rankings are cross-checks.
Corroborate important role changes with team reports or sourced workload data.

Do not cite Reddit, X/Twitter, Facebook or Instagram as the evidence source. Follow
an attributed report to its publisher when possible; uncorroborated claims remain
uncertain. Search result relevance scores are not fantasy player ratings.

Record each decisive metric's source, publication/as-of date, game window and
denominator where available (team targets versus pass attempts, routes versus
dropbacks, team RB carries versus all rushing attempts). Compare like windows and
definitions. Small samples, blowouts, missed time and backup-QB games can distort
shares and efficiency; explain whether the context will recur. A preseason or
wrong-season page is not current usage evidence.

Missing metrics are unknown, not zero. If a comparable metric is unavailable for
one side, say so, use the best observable touches/routes/targets, lower confidence,
and give a trigger for revisiting. Do not fabricate raw metrics, weights, or adjusted
point forecasts. A big scoring game alone is not proof of opportunity growth.

## Health and betting context

Check practice participation and the expected workload, not just a questionable
tag. Wednesday DNP alone is inconclusive; repeated DNP late in the week increases
risk. Full practice or active status does not guarantee unrestricted work. If a
report has not been issued yet, state that and name the next checkpoint/fallback.

Implied team total = (game total / 2) + (favorite's spread magnitude / 2) for the
favorite; subtract for the underdog. A 49 total with a 7-point favorite implies
28 points for the favorite and 21 for the underdog. Verify the favorite and timestamp;
do not mix a spread from one update with a total from another. Lines guide expected
scoring and game script, not a guaranteed individual workload. Use opponent offensive
efficiency for D/ST; opponent defensive efficiency for offensive players.

## Turn evidence into a decision

Weigh opportunity and persistent role first, health and matchup next, projections
last. Health gates eligibility; D/ST and K instead lead with matchup/scoring context.
Efficiency helps assess sustainability and distinguish similar roles. Projections
can break a tie when roles are comparable; they cannot substitute for research of a
fresh workload change. Do not double-count a matchup already embedded in projections.

For adds/drops and trades, extend the comparison to future opportunity, expected
return of competitors, positional replacement value and the player sacrificed.
For close starts, floor/ceiling posture is a final tiebreaker after checking whether
the opponent's lineup is complete. Log the evidence actually used, any projection
override, and missing metrics; do not claim all listed metrics were retrieved.
