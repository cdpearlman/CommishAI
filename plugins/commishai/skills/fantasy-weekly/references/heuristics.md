# Decision heuristics

Seven principles. Every recommendation should trace to at least one, and you should
name it when the call is close.

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

## Lineup optimization

**4. Synthesize projections, don't defer to them.** ESPN's projection (the `PROJ`
column) is a reasonable prior and a bad oracle — it lags role changes by about a week
and is largely blind to game script. Use it as the baseline, then adjust on the
evidence below. When you override a projection, say why.

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
already projected to lose. This flips the correct answer on genuine toss-ups, so check
the margin before settling one.

## Tiebreakers

When two options are still level after all seven:

- Take the player whose role is trending up over the one trending down, even at equal
  current volume.
- Take the player in the better offense — talent around a player creates opportunity.
- Take the healthy player over the one who just cleared a questionable tag.
- Take the player playing later in the week only if you'd benefit from information
  first; otherwise it's irrelevant.
