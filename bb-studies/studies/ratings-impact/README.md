# Study: skill impact via match ratings

**Goal:** measure how much each skill, at each position, contributes to winning, then divide by salary cost to find salary-efficient skills ("produce more than salary is expected to").

**Impact definition chosen:** option A, team match ratings (game-engine based).

## What the game documents (official manual, Nomenclature page)

- Teams receive several ratings per match, used in the calculation of each possession.
- Position weights:
  - Outside Scoring / Defense: both guards heavily, SF medium, PF slightly.
  - Inside Scoring / Defense: C heavily, PF somewhat heavily, SF medium.
  - Rebounding: C and PF heavily, SF somewhat heavily, guards medium.
  - Offensive Flow: PG very heavily, SG and SF medium.
- Players with more than 5 minutes get an individual match rating based on stats and contribution.

Source: https://www.buzzerbeater.com/community/rules.aspx?nav=Nomenclature

**Community caveats (unverified):** tactics change skill weights; some argue the engine resolves individual matchups per shot, so ratings may be a summary, not the mechanism. Layer 2 tests this.

## Design

### Layer 1: player level (transfer list)
- Sample ~300 transfer-list players, ages ~26-32 (skills near-stable), weighted toward PFs.
- Use each player's last 2-4 weeks of games; 5+ minutes per game.
- Model: player match rating ~ skills x position played + minutes + game type + tactics + team-rating context.
- Efficiency = actual average rating - expected rating for salary.

### Layer 2: team level (own games)
- Every Sharpshooters game since 2026-08-28 (~50) plus new games.
- Validate that ratings predict margin and wins; convert rating units into points.
- Fit lineup skills -> team ratings.

### Fields per row
| Group | Fields |
|---|---|
| Player | id, age, height, displayed position, 12 skills + Game Shape, salary, potential + cap % |
| Game | match id, date, type, home/away, minutes, position played, player match rating |
| Context | both teams' 6 ratings, both teams' offense/defense tactics, final score |

### Known risks
- Individual rating may favor scorers over defenders (Layer 2 checks).
- Tactics shift weights: record in every row; fit Base offense separately once data allows.
- Team and opponent strength: control with rating differentials.

## Pull budget
See [`data/pull_budget.csv`](data/pull_budget.csv) (live version in the Claude Sheet "BB ratings study - page-pull budget").

## Next steps
See [`NEXT_STEPS.md`](NEXT_STEPS.md).
