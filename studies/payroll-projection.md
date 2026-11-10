# Payroll after the next recalculation vs. Division II

Added 2026-11-10. Static snapshot, not recomputed by the daily job. Script and output in [`payroll-projection/`](payroll-projection/) (`python3 studies/payroll-projection/project.py`).

Follow-up to [Salaries by division level](salary-by-division.md), which asked for a projection of our payroll after the season-start recalculation, set against Division II's floor. It also checks the manual's Division III minimum-payroll rule against what we have actually been charged.

## Short answer

- **Projected payroll after recalculation: about $109k a week**, up from $78.7k on today's roster. Model band $76k–$157k.
- **That's still far below Division II.** It would rank above only 1 of Division II's 59 human teams (1.7th percentile). The gap to Division II's p10 ($275.6k) is about **$167k a week, or $2.2M a season**, roughly three times the $750k promotion bonus.
- **The 130%-of-TV-money minimum payroll has never been charged to us.** In the 12 paydays on record, player salaries were 57%–82% of TV money, and the amount paid equals the sum of the roster's salaries. Either the rule is not what our manual summary says, or it is applied on a base we don't know. This needs checking on the official Economy page (see Next steps).

## Data

- **Our roster:** 17 players, API roster XML retrieved 2026-11-09T20:40:46Z (`docs/report.db`, table `state`). **Official.**
- **Weekly ledger:** every `playerSalaries` and `tvMoney` transaction in the 144 daily snapshots from 2026-09-03 to 2026-11-09 (`docs/report.db`, table `snapshots`), covering paydays from 2026-08-17. **Official** (API `economy`).
- **Salary model:** 266 transfer-list players in [`salary-model/players.csv`](../salary-model/players.csv), pulled 2026-09-11.
- **Division II payrolls:** Brazil, season 73, from [`salary-by-division/summary.json`](salary-by-division/summary.json).

## The minimum-payroll check

[Our manual summary](../references/game-manual.md) (Economy section) says Division III teams pay at least **130%** of league TV money in salaries. [`arena-model/handoff.md`](../arena-model/handoff.md) lists the same 130% for Division III, but differs for the other divisions (Division II 190% vs. the manual summary's 187%; Division I 245% vs. 241.5%).

What we were actually charged. **Official** figures, ratio **calculated**:

| Payday (Monday) | Player salaries | TV money | Salaries ÷ TV money |
|---|---|---|---|
| 2026-08-17 | $47,895 | $84,021 | 0.57 |
| 2026-08-31 | $54,233 | $84,021 | 0.65 |
| 2026-09-07 | $55,636 | $84,021 | 0.66 |
| 2026-09-14 | $53,241 | $84,021 | 0.63 |
| 2026-09-21 to 2026-11-02 (7 paydays) | $57,193 each | $84,021 | 0.68 |
| 2026-11-09 | $68,457 | $84,021 | 0.81 |

(The ledger has no entry for 2026-08-24; the snapshots start after it.)

- **130% of $84,021 is $109,227.** A top-up to that level would have been $41k–$61k every payday, and no weekly charge like that appears. The only other recurring charges are staff salaries and $10k scouting.
- **Two one-off charges are of that size, but don't fit.** `revenueSharing` took $61,500 on 2026-08-25 and $62,500 on 2026-10-20 (with smaller `unknown` charges of $2,000 and $26,507 at the same timestamps), plus $1,000 on 2026-09-02. They're on a Tuesday, not on Monday paydays, and only twice in 12 weeks. **[Inferrence]** They're more likely gate or prize sharing than a payroll top-up, but the ledger doesn't say.
- **The salary charge is just the roster.** On 2026-10-18 our 13 players' salaries summed to exactly **$57,193** ([`players.csv`](salary-by-division/players.csv), team 32988), the same amount paid every Monday from 2026-09-21 to 2026-11-02.
- **Other teams are below it too.** Division III's human-team p10 payroll is $41k and its p25 is $59k ([Salaries by division level](salary-by-division.md)). If TV money is similar across Division III, a quarter of the division would be under a 130% floor.

**[Inferrence]** Possible explanations, none confirmed: the rule's base is not the `tvMoney` figure in our ledger (for example a smaller base amount); it applies only in some weeks or at season end; it changed after our summary was written on 2026-09-24; or our summary is wrong. The check costs nothing and matters, because it decides whether "keep salaries low" saves any money at all.

## The projection

**Method.** BuzzerBeater recalculates salaries once a season, at season start, from current skills ([Salary model: formula history](../salary-model/formula-history.md)). So the projection prices each player's **current** skills with a log-linear model fitted on the 266 market players:

`log(salary) = a + Σ bᵢ × skillᵢ`, over the 10 skills that price (Stamina and Free Throw are excluded, as is Age). N = 266, **R² = 0.868**, residual SD 0.36 in log terms. **Calculated.**

The band (**$76k–$157k**) moves the whole roster up or down by one residual SD together. That's a deliberately wide, worst-case band: it assumes every player's error goes the same way.

| Player | Age | Salary now | Projected | Change |
|---|---|---|---|---|
| Stefos Akrivopoulos | 19 | $6,983 | $17,261 | +147% |
| Sit Ki Poon | 28 | $11,699 | $11,576 | −1% |
| Paschalis Dolianitis | 30 | $8,789 | $10,921 | +24% |
| Che Xiaozhuo | 25 | $8,309 | $10,013 | +21% |
| Gunnar Støen | 19 | $4,282 | $9,340 | +118% |
| Piotr Wiszowata | 19 | $5,976 | $8,369 | +40% |
| Tapati Venkateswarlu | 20 | $4,281 | $7,951 | +86% |
| Robson de Castilho | 19 | $5,785 | $6,886 | +19% |
| Nizan Stucco | 19 | $4,700 | $6,063 | +29% |
| Fiorindo Valença | 19 | $2,723 | $3,674 | +35% |
| Élder Landim | 18 | $2,778 | $3,591 | +29% |
| Sandoval Mustafa | 40 | $2,922 | $3,476 | +19% |
| Danilo Luza | 19 | $2,575 | $2,854 | +11% |
| Lauro Mendonça | 18 | $2,343 | $2,852 | +22% |
| Andrzej Przeor | 42 | $2,162 | $1,832 | −15% |
| Alessandro Diaferia | 43 | $1,403 | $1,325 | −6% |
| Matas Muknickas | 46 | $1,030 | $1,050 | +2% |
| **Total** | | **$78,740** | **$109,032** | **+38%** |

- **Most of the rise is the teenagers we're training.** Akrivopoulos and Støen alone add about $15k a week. That's the doctrine working as intended: the salary catches up with the training.
- **A sanity check that held up.** Sit Ki Poon isn't being trained ([Zhang vs. Sit Ki](zhang-vs-sit-ki-tco.md)), so his salary should already match his skills. The model puts him at $11,576 against an actual $11,699, 1% off. **[Inferrence]** The three oldest players (42–46) are probably not being trained either, and they land within 2%–15%.
- **Caveat: most of our players are cheaper than the model's sample.** Only 16 of the 266 market players earn under $10k, and 14 of our 17 do. The close fit on the veterans is reassuring, but the cheapest players are an extrapolation.

## Against Division II

| | Weekly payroll |
|---|---|
| Our projection after recalculation | **$109k** (band $76k–$157k) |
| Cheapest human team in Division II | $78k |
| Division II p10 | $276k |
| Division II median | $388k |

**Calculated.** At $109k we'd be the second-cheapest human team in Division II. Even the top of the band ($157k) is below Division II's p10. [Salaries by division level](salary-by-division.md) found that the 15 Division II teams with the fewest wins have a median payroll of $298k, and that payroll and win% correlate at +0.68 inside Division II.

**Paying for it.** Closing the gap to the p10 means about **$167k more a week**, or **$2.17M** over a 13-payday season ([Season structure](season-structure.md)). Promotion pays a one-time **$750k** into Division II ([Game manual](../references/game-manual.md)). **[Inferrence]** The bonus covers roughly a third of one season at Division II's floor. Staying up has to be paid for by Division II revenue (TV money, gate, merchandise), which we have no figures for yet.

## What this means

**[Inferrence]**

- **Training alone won't make us Division II-sized by next season.** Recalculation lifts the payroll by about $30k a week; Division II's floor is about $170k higher still. Getting there takes buying players, or several more seasons of training.
- **That's not automatically bad.** Payroll correlates with winning, but it isn't the whole story. The cheapest Division II team pays $78k and is still in Division II. A cheap, developing roster in Division II earns the promotion bonus and higher income, at the risk of relegation.
- **The choice depends on what you're optimizing.** Wins now mean buying salary. Money and long-run strength mean staying cheap, accepting relegation risk, and timing the climb. That's a decision for Tom, not something the data settles.

## Next steps

1. **Check the minimum-payroll rule on the official [Economy page](https://www.buzzerbeater.com/community/rules.aspx?nav=Economy).** This session couldn't reach buzzerbeater.com, so it's still unconfirmed. Note what the percentage applies to, when it's charged, and the Division II figure (187% or 190%).
2. **Re-run the projection after the recalculation** and compare it with the real new salaries. That tests the model on our own players.
3. **Get Division II's TV money and gate figures** for a Division II team. Without them, the cost of staying up can't be weighed against Division II income.
4. **Decide the target: profit or wins.** That decides whether a study of Młoty Stargard-style teenage flips ([How long-run winners are built](../top-teams-research/BB_Top_Teams_Strategy_Report.md)) is worth doing.
