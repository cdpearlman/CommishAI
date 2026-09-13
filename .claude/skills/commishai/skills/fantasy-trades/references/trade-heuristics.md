# Trade heuristics

## Value is rest-of-season, always

Points already scored are sunk. A WR averaging 18/game who scored three of his
touchdowns in one blowout is not an 18/game player. Value from here: role, offense,
health, schedule.

The fastest read on whether production is real is `ff.py player "Name"` — look at the
actual-vs-projected column week by week. A player consistently beating projection has a
role the market hasn't priced. A player with one enormous week and five quiet ones is a
sell.

## Buy low

- **Bad touchdown luck.** High yardage and target volume, few touchdowns. Touchdown
  rate regresses hard; yardage and targets don't. This is the most reliable buy-low in
  fantasy.
- **A tough stretch just ended.** A player who faced three top-5 defenses looks broken
  and isn't. Check what's next before judging.
- **Returning from injury.** The week or two after a return, before the role is
  visibly restored, is the cheapest a good player gets.
- **A backup with a starter's role coming.** Handcuffs and next-men-up are nearly free
  before the injury and unaffordable after.

## Sell high

- **Touchdown-dependent production.** Modest yardage, heavy scoring. The inverse of
  buy-low, and it's the exact moment his name value peaks.
- **An unsustainable role.** A committee back who got 25 carries in one game script.
- **Age plus a soft schedule already spent.** The name still carries value the
  production won't.
- **Anyone you'd bench in the playoffs.** If he's not in your week-15 lineup, he's
  trade capital.

## Positional scarcity

The value of a player is his margin over what you'd otherwise start — replacement
level, not raw points. A 15 ppg RB in a league where the waiver wire offers 8 ppg RBs
is worth far more than a 17 ppg WR when the wire offers 14 ppg WRs.

This is why elite TEs and rushing QBs trade at a premium and why the third-best WR on
your roster is nearly worthless in trade: the market for him is thin because everyone
has one.

`ff.py rosters` computes this for you. The SURPLUS and THIN AT columns are not roster
head counts — they count players projecting **above replacement level at that
position**, where replacement is the projection of the last startable player league-wide
(position slots plus a share of the flex, times the number of teams). So a team carrying
four quarterbacks in a 1-QB league shows no QB surplus if only one of them is startable,
which is correct: the other three have almost no trade value.

Read it accordingly. "THIN AT: TE" means they cannot fill their TE slot with a startable
player — that is a motivated trade partner. A surplus number is how many startable
players they have beyond their slots, which is exactly what they can afford to trade.

`ff.py available --pos RB` shows what the wire offers, which is the other half: never
trade for a player you could have added for free.

## Consolidation

2-for-1 trades concentrate value into your starting lineup, which is correct in
principle: you start one lineup, not a roster. But price the cost honestly —

- You must drop someone to make room. That drop is part of the trade.
- You lose depth against injury and bye weeks.
- The single player you receive must clearly beat the *better* of the two you gave,
  not the average of them. Getting the best player in the deal is the usual test, and
  a 2-for-1 that doesn't deliver the best player is almost always a loss.

Consolidate when you're deep and contending. Don't when you're already thin.

## Playoff schedule

Weight weeks 15–17 heavily for anyone you're acquiring to win now. A player facing
three elite defenses in the fantasy playoffs is worth materially less than his
season-long value, and a player with a soft playoff run is worth more than the market
charges — most managers don't look that far ahead.

Look this up on the web; ESPN's data doesn't rank future matchup difficulty.

## Reading the other manager

- **Contenders** overpay for certainty and proven starters. Sell them your steady,
  boring producer at a premium — and your high-variance player if they're desperate.
- **Sellers** take upside, youth, and lottery tickets. Buy their proven starter.
- **A manager who just spent big FAAB** at a position is telling you they're worried
  about it. `ff.py transactions` shows you this.
- **The team that just lost a starter to injury** is the most motivated buyer in the
  league for about 48 hours.

## Fairness

Offer trades you'd accept from the other side. A reputation for lopsided offers ends
your ability to trade in a league you'll be in all season, and a veto or a bad-faith
accusation costs more than any single deal is worth. The goal is a deal where both
starting lineups improve — those exist constantly, because rosters are unbalanced in
complementary ways.
