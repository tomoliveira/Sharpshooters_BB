# Salaries by division level: what each tier of Brazil pays

Added 2026-10-18. Static snapshot, not recomputed by the daily job. Data, collector and analysis scripts in [`salary-by-division/`](salary-by-division/).

How player payrolls are distributed across Brazil's five division levels, and where Sharpshooters sits on that ladder. Season 73, pulled after 20 regular-season games.

## Data

**Official** (BuzzerBeater API: `leagues`, `standings`, `roster`). Every team in Divisions I–III (21 leagues, 336 teams), plus a random sample of 16 leagues each from Division IV (of 64) and Division V (of 256). That's 848 teams and 21,982 players.

- **Payroll** is the sum of the weekly salaries on a team's roster. Staff salaries aren't included.
- **Human teams only** in the payroll figures. Bot teams (the API's `isBot` flag) are reported separately. Two abandoned human teams with under 5 players were excluded too: Sindicato S.A. in Division I (1 player) and a team in Division II with an empty roster.

## The payroll ladder

Weekly payroll, human teams. **Calculated.**

| Level | Human teams | p10 | p25 | **Median** | p75 | p90 | Max |
|---|---|---|---|---|---|---|---|
| I (Liga Nacional) | 15 | $561k | $717k | **$791k** | $852k | $974k | $1,092k |
| II | 59 | $276k | $305k | **$388k** | $477k | $507k | $586k |
| III | 120 | $41k | $59k | **$129k** | $202k | $274k | $445k |
| IV | 0 (256 bots sampled) | | | | | | |
| V | 0 (256 bots sampled) | | | | | | |

- **Each step up costs about 2–3× more.** The median payroll goes from III to II at 3.0×, and from II to I at 2.0×.
- **Divisions IV and V are entirely bots.** All 32 sampled leagues (512 teams) had no human team. More than half of Division III is bots too (136 of 256). Brazil's human game is effectively Divisions I–III.
- **Division III is the most unequal tier.** Its coefficient of variation is 0.64, against 0.28 in II and 0.21 in I. It mixes teams spending to win promotion with teams that are coasting.

## Player-level salaries

Weekly salary per player, human teams. **Calculated.**

| Level | Median player | p75 | p90 | Median team's best-paid player | Players over $180k | Top 3's share of payroll (median) |
|---|---|---|---|---|---|---|
| I | $31.4k | $119k | $168k | $203k | 9.4% | 62% |
| II | $17.5k | $51k | $79k | $92k | 0.7% | 59% |
| III | $5.4k | $12k | $25k | $26k | 0% | 51% |

- **Payroll is concentrated at every level.** A team's top three players take more than half of what it pays, and the share is highest in Division I. Every tier is built on stars and cheap bench players, not a flat roster.
- **The $180k tier is almost purely a Division I phenomenon.** The season-73 formula change made players over $180k more expensive and everyone else cheaper (see [the season-73 formula change notes](../salary-model/reference-cases/floor-players-and-deflation.md)). In practice that cost lands almost entirely on Liga Nacional teams. Nobody in Division III and almost nobody in II is affected.

## Does payroll buy wins?

Correlation between payroll and win% inside each level, human teams only. **Calculated.**

| Level | corr(payroll, win%) |
|---|---|
| I | +0.78 |
| II | +0.68 |
| III | +0.65 |

Strongly, at every level. This is a same-snapshot correlation, not causal: winning teams also earn more and can afford more. **[Inference]** The link gets tighter higher up, so there's less room in the top tiers to win by drafting and training well rather than by spending.

## Where Sharpshooters sits

- **Payroll $57.2k/week, 23rd percentile of Division III's human teams.** We're 13-7, 5th in III.15 and tied with Novo Mundo Last Dance, with the league's 5th-highest payroll. Within III.15 we're getting about what our payroll predicts. That fits the [training strategy](../references/training_strategy_notes.md)'s "keep salaries low, promote" doctrine.
- **III.15 is a cheap league.** Castelo Basquete leads at 20-0 on $200k, Blumenau Drunkers are 18-2 on $89k, and everyone else pays under $75k.
- **The best team in each Division III league spends a median of $245k.** That's the human team with the most wins in each of the 12 Division III leagues that have human teams, ranging from $135k to $445k. It's about 4.3× our payroll.
- **Division II's floor is around $275k.** That's its p10, and the 15 Division II teams with the fewest wins have a median payroll of $298k. Even the cheapest human team in II pays $78k, more than we do now.

**[Inference]** Promotion out of III.15 doesn't take Division III-leader money, since the league's top two pay $200k and $89k. Staying in Division II probably does: a payroll near $300k a week is roughly 5× today's. The plan to get there is players who were trained up in III. Their salaries rise at the season-start recalculation, so the payroll should grow before promotion, not after it. This is worth modeling as its own study: a projection of our payroll after the next recalculation, set against Division II's floor.

## Caveats

- **One country, one snapshot.** These figures cover Brazil, mid-season 73. Other countries' ladders differ, and ones with human teams in their lower divisions would look very different.
- **Salaries lag skills.** Salaries are recalculated once per season, at the start. Teams that train hard (like us) look cheaper mid-season than they'll be next season.
- **Bot payrolls aren't comparable.** Bot rosters are odd: Division V bots carry a median of 54 players. They're excluded from all the human figures.
- **Sampling.** Divisions IV and V were sampled with a fixed random seed (73), at 16 leagues each. A full census might turn up a few human teams, but 0 out of 512 makes them rare.
