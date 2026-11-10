# Skill impact via match ratings

Added 2026-11-10. Study plan; no data collected yet. Pull budget in [`ratings-impact/`](ratings-impact/).

**Status: on hold.** BuzzerBeater moved to a new website on 2026-11-10. The collector waits for a mapping pass on the new site (see [Next steps](#next-steps)).

**Goal:** measure how much each skill, at each position, contributes to winning, then divide by salary cost to find salary-efficient skills ("produce more than salary is expected to").

**Impact definition chosen:** option A, team match ratings (game-engine based).

## Collection rules

These apply to any BuzzerBeater data collection, not just this study.

- **Max 30 page pulls per minute.**
- Re-check page structure after the 2026-11-10 site migration before reusing any scraper.
- Facts sourced from the official Game Manual vs community forums vs inference are labelled as such.

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

See [`ratings-impact/pull_budget.csv`](ratings-impact/pull_budget.csv) (live version in the Claude Sheet "BB ratings study - page-pull budget"). At 30 pulls/min, the full collection is about 2,180 pulls (~73 minutes), or 1,640-2,000 pulls (~55-67 minutes) with shared box scores pulled once.

## Next steps

| # | Step | Status |
|---|---|---|
| 1 | Short mapping pass on the new site: one player page, its game-ratings links and one box score | Waiting for new site |
| 2 | Confirm which fields still exist (rating links, tactics, both teams' ratings) and their new names | Waiting for new site |
| 3 | Check whether the official API still works after the redesign, to save page pulls | Waiting for new site |
| 4 | Write the collector spec against the new structure (max 30 pulls/min) | Not started |
