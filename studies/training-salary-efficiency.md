# Training per salary dollar

Added 2026-11-10. Static snapshot of the roster retrieved 2026-11-09, not recomputed by the daily job. Script and output in [`training-salary-efficiency/`](training-salary-efficiency/).

This study reconciles the [Training doctrine](training-doctrine.md), the "Minimize salary" mode in [Training strategy notes](../references/training_strategy_notes.md), and [Skill salary costs](skill-salary-costs.md), and rescores training by each skill's salary cost **at our players' current ratings**.

## Main findings

1. **Calculated.** For the young cohort (10 players aged 21 or under, 7 of them PFs), the cheapest documented trainings per salary dollar are Ball Handling and Passing (21–34 skill points per $100 of added weekly salary), because our players sit below those skills' steep breakpoints. Among the inside trainings the old mode compares for C/PF, **Shot Blocking (PF/C) is still the cheapest** (0.93 points per $100), ahead of Inside Defense (0.51), Inside Scoring (0.49) and Rebounding (0.36). That confirms the report's current "Minimize salary" pick.
2. **[Inference]** One on One at C/PF would beat Shot Blocking (est. 1.59 points per $100, about 1.7× better). training.aspx offers "C / PF (90%)" for One on One ([dropdown map](../references/training_dropdown_map.md)), but the [coefficient capture](../references/training_coefficients.md) has no C/PF row, so the estimate is 90% of the SF/PF row. Capturing the real row would settle it.
3. **Official.** The Free Throw contradiction resolves: both statements are true. Free Throws are only a *training focus* under Team Training ([Training chapter](https://www.buzzerbeater.com/community/rules.aspx?nav=Training)). Separately, the Training Court building "will enable players to work on their free throws during the season", on top of normal training, though "the effect is not nearly as large as dedicating a full week of training to free throws" ([Arena chapter, Team Infrastructure](https://www.buzzerbeater.com/community/rules.aspx?nav=Arena)). It costs $500k for level 1 plus $5k a week per level.
   - **[Inference]** We don't own one: the finance ledger in `docs/report.db` has no facility or maintenance line. So for us, Team Training is still the only way to raise Free Throw.
4. **Shot Blocking is not expensive in any data we hold, but position may change that.** The doctrine deprioritizes it for salary reasons, but Tom confirmed on 2026-11-10 that this rule was a guess, not a tested finding. Both of our price sources say it is one of the cheapest skills:
   - **Community (unverified):** the buzzer-manager.com curve is 1.65× from rating 1 to 20, ninth of ten priced skills ([curves](../salary-model/skill-curves-reference.md)).
   - **Calculated:** in the 266-player market regression, SB 5→20 raises predicted salary 1.79×, against 3.49× for Jump Range ([formula history](../salary-model/formula-history.md)).
   - **Official (patch notes):** the season-73 formula "priced up" Shot Blocking everywhere and made centers slightly more expensive ([floor players and deflation](../salary-model/reference-cases/floor-players-and-deflation.md)). Neither source above has a position term, so SB on a center may cost more than they show. This stays open until the skill-salary pricing work tests position.
5. **[Inference]** Points per dollar is not wins per dollar. A Passing point on a center counts the same here as an Inside Defense point. The ranking needs each skill's weight in winning by position, which [Skill impact via match ratings](ratings-impact.md) is meant to produce.

## Why cheap training matters for profit too

Tom's goal is both wins and profit, with profit paying for the stretches where the team pushes to win (2026-11-10).

- **Official.** Salaries are recalculated once a season from current skills ([formula history](../salary-model/formula-history.md)). The game manual itself suggests training more players than you need and selling the extras ([Training chapter](https://www.buzzerbeater.com/community/rules.aspx?nav=Training)).
- **[Inference]** So a skill point does two jobs. It helps win games now, and it raises the player's sale value before that player's salary catches up. Cheap-to-train skills keep the payroll low for the season the player is kept, and the gain is still there when the player is sold.
- **[Inference]** This study only measures the salary side. Whether buyers pay more for some skills than others is not measured here; the transfer-list data in [`salary-model/players.csv`](../salary-model/players.csv) has starting (asking) prices, not final sale prices.

## Method

**Calculated** by [`score.py`](training-salary-efficiency/score.py) from three files already in the repo:

- Weekly gains per skill for every (training, position combo) row: [Training coefficients](../references/training_coefficients.md).
- Salary at each rating 1–20 for each priced skill: [Skill-to-salary curves](../salary-model/skill-curves-reference.md). Stamina and Free Throw have no salary effect.
- The roster (ratings, best position, current salary): the `state` table in `docs/report.db`.

For each player a row trains, one week adds `coef × (curve[r+1] − curve[r]) / curve[r] × current salary` for each skill it touches, where `r` is the player's current rating. That uses the skill's *marginal* cost at our players' level instead of the flat 1→20 multiplier the report divides by today. Points per $100 is total points a week over total salary added a week, summed over the players trained.

Assumptions, each **[Inference]**:

- A player is trained by a combo if the player's best position is in it. In the game it's the minutes played there.
- The calculator's relative step for one skill, measured with every other skill at 10, carries over to our players, whose other skills and salaries are much lower. The regression's log-linear form supports a multiplicative effect, but it isn't tested at our salary range.
- The added salary only lands at the next season's recalculation. Salaries are recalculated once a season from current skills ([formula history](../salary-model/formula-history.md)), so training gains are free until then.

## Results

Rows that train at least one cohort player, best first. Full table: [`scores.csv`](training-salary-efficiency/scores.csv).

| Training | Combo | Players | Points / week | $ salary added / week | Points per $100 |
|---|---|---|---|---|---|
| Ball Handling | PG | 1 | 1.00 | 2.92 | 34.25 |
| Ball Handling | PG/SG/SF | 2 | 0.80 | 2.50 | 32.05 |
| Passing | Team | 10 | 2.30 | 10.78 | 21.33 |
| Inside Defense | C | 2 | 1.30 | 38.49 | 3.38 |
| Shot Blocking | C | 2 | 1.60 | 82.32 | 1.94 |
| One on One | C/PF (est.) | 8 | 9.36 | 589.81 | 1.59 |
| One on One | SF/PF | 7 | 9.10 | 596.93 | 1.52 |
| Shot Blocking | PF/C | 8 | 4.88 | 526.94 | 0.93 |
| Inside Defense | PF/C | 8 | 4.00 | 781.02 | 0.51 |
| Inside Scoring | PF/C | 8 | 4.00 | 817.75 | 0.49 |
| Jump Shot | SF/PF | 7 | 4.55 | 957.28 | 0.48 |
| Rebounding | PF/C | 8 | 4.80 | 1,316.14 | 0.36 |

**[Inference]** In absolute terms every option is cheap right now. The costliest, Rebounding PF/C, adds about $1,300 a week to next season's payroll per week trained, across 8 players. That supports the promotion-era plan of training hard while salaries lag.

## Next steps

1. Capture the One on One and Jump Shot rows at C/PF on training.aspx, and replace the 90% estimate.
2. When [Skill impact via match ratings](ratings-impact.md) has skill weights by position, multiply each coefficient by its weight and rescore as rating gain per salary dollar.
3. Once the salary pricing work tests position, recheck the Shot Blocking and Jump Range rules in the doctrine, and swap the report's flat multipliers for the marginal method used here.
