# Layer 2: team match ratings vs the scoreboard

Added 2026-11-10. Part of [Skill impact via match ratings](../ratings-impact.md). Script: [`layer2_team_ratings.py`](layer2_team_ratings.py). Full output: [`layer2_results.json`](layer2_results.json).

**Question:** do the six team match ratings explain who wins and by how much, does that hold on games the model never saw, and how many points is one rating point worth?

**Answer:** yes. Rating differences explain about 90% of the variation in final margin on held-out games and pick the winner about 95% of the time. One rating point, summed across the six ratings, is worth about **4.5 points of margin**. Per rating, **rebounding and outside defense** are worth the most points; **inside scoring** adds almost nothing once the other five are known.

## Data

- Source: `docs/report.db`, table `match_ratings` (boxscore ratings cached by `scripts/bbapi_lib.py` for the division Power Rankings).
- 287 team-game rows for 16 team ids; **135 matches** have both teams' rows, played 2026-08-29 to 2026-11-07. Only those 135 are used to fit.
- Match types: 104 league regular season, 17 TV regular season, 6 relegation, 8 playoff.
- Margin = home score minus away score. Its standard deviation is 41.4 points, and the home team won 55.6% of these games.
- Features: home minus away for each rating (outside scoring, inside scoring, outside defense, inside defense, rebounding, offensive flow). Margin flips sign when the teams are swapped, so differences are the full set of linear inputs.

## Results

### 1. Ratings explain the margin, also out of sample

| Model | 5-fold CV R² (200 repeats) | CV error (RMSE, pts) | CV winner picked | Date holdout R² | Holdout RMSE | Holdout winner picked |
|---|---|---|---|---|---|---|
| Home edge only | -0.02 | 41.6 | 55% | -0.07 | 40.9 | 63% |
| Sum of six rating differences (one weight) | 0.91 | 12.3 | 95% | 0.89 | 13.0 | 96% |
| Six rating differences (six weights) | **0.92** | **11.5** | 94% | **0.90** | **12.4** | 96% |

- Date holdout: fit on 89 matches through 2026-10-10, tested on the 46 matches from 2026-10-13 to 2026-11-07.
- In sample, the six-weight model has R² 0.93 (RMSE 10.8). The out-of-sample R² is only 0.01 to 0.03 lower, so the fit is not driven by overfitting.
- Separate weights per rating beat one shared weight by about 0.8 points of error. Small, but consistent in every check.

### 2. Points of margin per rating point

From the full-sample fit (135 matches). "Per 1 SD" is the coefficient times the typical size of that rating gap between two teams in this league.

| Rating | Points per +1.0 rating gap | 95% CI | Points per 1 SD of gap | Bootstrap: share of resamples where it is the largest |
|---|---|---|---|---|
| Rebounding | **6.7** | 3.6 to 9.7 | **13.9** | 52% |
| Outside defense | **6.4** | 4.7 to 8.1 | 12.2 | 42% |
| Offensive flow | 4.7 | 2.7 to 6.8 | 5.8 | 3% |
| Inside defense | 3.8 | 0.8 to 6.7 | 8.8 | 2% |
| Outside scoring | 3.4 | 0.7 to 6.2 | 4.8 | 1% |
| Inside scoring | 0.4 | -1.4 to 2.2 | 0.6 | 0% |

- Home edge after ratings: +0.3 points (SE 1.0), so in these games, home court adds nothing beyond what shows up in the ratings.
- One-weight version: **4.52 points per summed rating point** (SE 0.12).
- Rating-sum gap needed for an in-game win probability (assumes normal residuals, SD 12.2 from the one-weight fit): 60% → +0.7, 75% → +1.8, 90% → +3.5, 95% → +4.4.

Caveats on reading the table:

- The rating gaps are correlated (inside defense vs rebounding r = 0.93; most other pairs 0.5 to 0.8). Rebounding vs outside defense as the top one is a coin flip (52% vs 42%), and the inside defense and rebounding split is uncertain. The ranking of the top two over the bottom two is stable: outside defense, rebounding and flow never fell below zero in 2,000 resamples, and inside scoring did 36% of the time.
- [Inferrence] Inside scoring may look weak because a team's inside points also show up as inside defense and rebounding gaps of the opponent, or because few teams here run inside-heavy offenses. This data cannot separate the two.
- These are ratings from the same game as the score. They describe how the game went; they are not yet the effect of a player's skill. Fitting skills to ratings is the next step.

### 3. Ratings also forecast games before they are played

Walk-forward test: before each match, each team's average ratings over its earlier games in the table (3+ games), with weights fitted only on matches before that date. 94 matches from 2026-09-19 on.

| Pre-game forecast | R² | RMSE | Winner picked |
|---|---|---|---|
| Average rating gaps × weights | **0.74** | **21.6** | **85%** |
| Average point differential gap + home edge | 0.69 | 23.4 | 80% |

Rating averages forecast the next game better than point differential does. So rating levels are a usable measure of team strength, not just a game summary.

### 4. Where Sharpshooters stand

Season-average gaps versus the league average of all 287 rows, converted to points per game with the six weights above.

| Rating | Sharpshooters gap | Points/game | Castelo Basquete gap | Points/game | Sharpshooters minus Castelo (pts) |
|---|---|---|---|---|---|
| Outside scoring | +0.14 | +0.5 | +1.39 | +4.8 | -4.3 |
| Inside scoring | +1.32 | +0.5 | +0.57 | +0.2 | +0.3 |
| Outside defense | +0.66 | +4.2 | +2.63 | +16.8 | **-12.6** |
| Inside defense | +1.86 | +7.0 | +1.75 | +6.6 | +0.4 |
| Rebounding | +1.73 | +11.5 | +2.30 | +15.3 | -3.8 |
| Offensive flow | +0.86 | +4.1 | +1.07 | +5.0 | -0.9 |
| **Total** | | **+27.8** | | **+48.7** | **-20.9** |

- Actual average margin: Sharpshooters +18.9 (24 games), Castelo +43.6 (21 games), a 24.7-point gap. The ratings account for 20.9 of it.
- **Outside defense is 12.6 of the 20.9 points**, the largest single gap. Inside scoring is where Sharpshooters lead the league most (+1.32), and it is the rating that buys the fewest points.
- [Inferrence] The official manual says outside defense is driven by both guards heavily and SF medium ([Nomenclature](https://www.buzzerbeater.com/community/rules.aspx?nav=Nomenclature), quoted in [the study plan](../ratings-impact.md)). If that holds, perimeter defense at the guard and SF slots is the first place to look. Step 3 below tests this with the roster data.
- Several team ids changed names during the season (for example, id 24703 played as Escada Barons, Time do Povo and Paraná Bluebird). Profiles group by id and use the latest name. [Inferrence] A rename may mean a new manager and a strength break, so those teams' averages mix two periods.

## Limits

- One league (16 Division III teams, one season). Weights may differ at higher levels.
- Tactics are not in the table. [Inferrence] Offense/defense tactic choices and effort settings move both the ratings and the score, so part of each weight may be tactic, not skill.
- 135 matches is enough for six weights (22 matches per weight) but not for per-tactic or interaction models.

## Next steps

1. **Fit lineup skills to team ratings.** Join each game to that team's roster (Sharpshooters: `snapshots` table; others: `opponent_rosters`, one snapshot per team only) and fit the 12 skills by position to each of the six ratings. Then chain: skill → rating → points.
2. **Add tactics and minutes per player** to each row from the boxscore, so skill effects are not confused with tactic choices.
3. **Price it:** combine points per skill level with the salary curves in [skill-curves-reference.md](../../salary-model/skill-curves-reference.md) to get points per $1k of weekly salary. This is the study's original goal.
4. Re-run this script each week. It reads the live table, so new games add data with no extra API pulls.
