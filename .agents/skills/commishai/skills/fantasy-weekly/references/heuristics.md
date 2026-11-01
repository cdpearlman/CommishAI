# Decision heuristics

Seven principles. Every recommendation should trace to at least one, and you should
name it when the call is close.

## How to weigh the evidence

Use an evidence hierarchy, not invented percentage weights or a player score:

1. **Opportunity and role:** expected touches, routes, targets, and high-value work.
   Compare the latest game with the previous 3–4 games when available. Explain why
   a change should persist: injury, depth-chart change, coaching use, or returning
   competition. A starting label or one big scoring week does not establish a role.
2. **Health and matchup:** availability is a gate, then estimate any workload limit.
   Adjust the role for opponent strengths, offensive-line/QB injuries, game script,
   and implied scoring. A difficult matchup does not automatically erase a secure
   workload advantage. D/ST and K are exceptions: opponent/scoring environment leads.
3. **Projections and rankings:** use as a calibration check and tiebreaker when roles
   are comparable. If they disagree with the opportunity evidence, explain which
   assumption differs. Do not invent a precise points adjustment without a model.

Efficiency (CPOE, RYOE, missed tackles per touch, YPRR) supports sustainability and
breaks ties; it does not manufacture volume. Avoid double-counting correlated signals
such as target share and WOPR, or projections and the matchup already baked into them.
For adds/drops, apply this hierarchy to expected rest-of-season work and replacement
value; distinguish a temporary injury fill-in from a durable upgrade. Price the drop
and future bench depth, not just the new player's current-week points.

## Roster management

**1. Opportunity is king.** Volume is the most predictive input available: snap share,
target share, route participation, red-zone touches, carry share. A player with a large
and *growing* role beats a more talented player in a committee. Efficiency fluctuates
week to week; role is sticky. When two players look close, take the one with the bigger
share of his offense.

**2. Protect long-term assets.** An injured player's 0-point week is irrelevant to his
*roster value*. Before recommending a drop, establish two things: the expected return
timeline, and his rest-of-season value once back. Compare that to the ROS value of the
best available replacement — not to this week's projection. Never drop a genuine starter
for a one-week streamer unless the injury is season-ending or the roster crunch is
truly forced. This is the single most expensive mistake available in fantasy.

**3. Stream deliberately.** D/ST and kicker are matchup positions, not talent positions.
Each week, take the defense facing a turnover-prone or backed-up offense and the kicker
in the best offense-plus-dome environment. Do not hold a "good" D/ST through a bad
matchup out of name loyalty. Same logic applies to TE when you don't have a top-6 one.

## Weekly waiver-claim strategy

Separate player evaluation from claim sequencing:

1. **Rank adds across positions** by net roster improvement: expected role and
   rest-of-season upside, immediate starting needs, scarcity and alternatives.
   Do not sort solely by weekly projections or group the queue by position.
2. **Rank drops separately**, first cut to last acceptable cut. Compare every
   plausible fringe player, including incumbents whose role or health changed;
   do not protect a name or a lineup slot without evidence. Apply the injury/ROS
   check in heuristic 2. State confidence and where the cut list stops.
3. **Choose acceptable combinations.** Separate rankings are a starting point,
   not permission for every add/drop pairing. Account for positional depth and
   whether an add is worth the second or later cut. Honor the manager's stated
   drop preference; distinguish it from the analyst's recommendation when different.
4. **Build one numbered submission queue** that implements those outcomes under
   ESPN's rules. Name an exact add and drop on each row. Reuse the first drop for
   fallback adds, then repeat an add with a later drop when it is also wanted as
   an additional acquisition. Label each row's purpose: preferred, fallback, or
   additional acquisition. Stop before an unacceptable tradeoff.
5. **Walk the outcomes before recommending the queue.** Apply each successful
   claim to roster state before examining the next row. Check both/all targets,
   each target alone, and no targets; confirm the intended cuts in each case.
   An add must still be available, its drop must still be rostered, and roster
   rules must allow the move. A successful claim can change league priority, so
   later awards are never guaranteed.

Example: adds A (Marks), then B (Bernard); drops X (Washington), then Y (Kamara).
The manager wants X cut if only one add wins, and both X/Y cut only if both win:

1. ADD A / DROP X — preferred.
2. ADD B / DROP X — fallback when A is missed.
3. ADD B / DROP Y — additional acquisition when A succeeds and B is still available.

| Acquired | Dropped |
|---|---|
| A and B | X and Y |
| A only | X |
| B only | X |
| Neither | Nobody |

If row 1 succeeds, X is gone and row 2 cannot process; row 3 can acquire B if it
remains available. If row 1 loses A to another manager, row 2 can acquire B for X;
then row 3 cannot acquire B again. If B is awarded elsewhere, neither B claim
succeeds. This example implements a drop preference, not a fixed player ranking.

A failed claim alone does not prove the add was taken: its drop may be gone or a
roster restriction may block it. Distinguish logical eligibility from an actual
award. Do not propose manual post-waiver edits when an ordered queue already
expresses the intended outcomes. For more targets, construct only the additional
rows needed for acceptable combinations and check each reachable roster state.
Keep the final explanation to ranked adds, ranked cuts, the queue and a compact
outcome summary; leave the detailed state reasoning out of the recommendation.

Use the league's actual waiver system. In this league, use the manager's reported
draft-order priority and an explicit ordered queue, not assumed FAAB bids; label
old manager-priority information as unverified. Distinguish immediate free agents
from players requiring claims; if the CLI does not expose status, check in ESPN.
Recommend no D/ST or K change when the incumbent is preferable. After processing,
refresh ownership with `--fresh`, record successful/missed claims and rerank only
remaining improvements. These are recommendations, not submitted transactions.

## Lineup optimization

**4. Synthesize projections, don't defer to them.** ESPN's `PROJ` column helps screen
candidates, but can miss a fresh role change. First establish expected opportunity,
then health and matchup, and use projections to check the conclusion. Neither a
2-point edge nor a 6-point gap removes the need to check changed roles. When overriding
a projection, cite the dated role evidence and acknowledge uncertainty. Do not assume
every projection systematically lags by a fixed time or ignores game script.

**5. Matchup analysis is paramount.** Evaluate the specific opponent, not their overall
record: how they defend *this position*, the individual coverage matchup, and any
schematic vulnerability. A defense ranked 30th against WRs but 5th against RBs is two
completely different matchups depending on who you're starting.

**6. Follow the Vegas money.** A team's implied total (over/under adjusted for the
spread) is the best single-number forecast of scoring environment available, and it's
priced by people with money at risk. Prioritize players in high implied-total games.
A big spread also tells you the game script: heavy favorites run late, underdogs throw.

**7. Floor vs. ceiling follows the matchup.** `ff.py snapshot` prints the projected
margin and a posture line. When favored, take the high-floor player — you win by not
losing. When you're the underdog, take variance; the safe play loses a game you were
already projected to lose. Use this only to break genuine toss-ups, not to prefer a
poor role for volatility alone. Reassess the margin after accounting for likely bye
and injury replacements; flag uncertainty when the opponent's lineup is incomplete.

## Tiebreakers

When two options are still level after all seven:

- Take the player whose role is trending up over the one trending down, even at equal
  current volume.
- Take the player in the better offense — talent around a player creates opportunity.
- Take the healthy player over the one who just cleared a questionable tag.
- Take the player playing later in the week only if you'd benefit from information
  first; otherwise it's irrelevant.
