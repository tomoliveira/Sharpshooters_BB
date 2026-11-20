# Arena expansions: payback recheck with real fill

Added 2026-11-10. Static snapshot from `docs/report.db` as of the 2026-11-09 17:40 snapshot, not recomputed by the daily job. Data and script: [`arena-expansion-recheck/`](arena-expansion-recheck/) (`python studies/arena-expansion-recheck/analyze.py` from the repo root).

## Main findings

1. **Calculated.** There were **seven** arena expansions this season, not one: **$1,408,400** in total (`investments.capex` in the snapshot). [Arena expansion payback](arena-expansion-payback.md) only covers the first ($205,800).
2. **Calculated.** With the real attendance on the seats each expansion added, the six built expansions ($1,046,400) earn about **$51,220 per full-value home game**. That's a payback of **about 1.9 seasons** at 11 home league games a season. They have recovered **$311,058 (30%)** so far.
3. **Calculated.** Payback gets worse with each expansion. The first one pays back in **1.46 seasons** (better than the 1.75 first claimed, because prices rose). The sixth (+900 bleachers) fills only **58%** of its seats and needs **2.46 seasons**.
4. **Calculated.** The "96.1% fill" assumption doesn't hold on new seats. Fill on the added seats ranged from **58% to 100%**, and the added bleachers filled 58–86%.
5. **[Inference]** The **$362,000 expansion bought on 2026-11-09 has no demand to fill yet at today's prices.** No tier has sold out at the current prices ($14 / $55 / $150 / $1,300). New seats only earn when attendance goes past the current capacity, so they'd earn about $0 a game until demand grows or prices drop.
6. **Calculated.** Our own games put ticket price elasticity at about **−1.5 in every tier**, not the −0.4 the optimizer assumes. At −1.5, raising the price on a tier that isn't sold out **loses** revenue. The price that just sells a tier out is the revenue maximum.
7. **Calculated.** The 16-team league data can't be used to fit elasticity. **13 of the 15 other teams never changed a price** in the 34 daily price snapshots (2026-10-07 to 2026-11-09), most of them at the default $10 / $35 / $100 / $800.

## What each expansion actually earned

**Calculated** from `match_attendance`, `league_arena_prices` and the snapshot's `investments` block. Each seat count was checked against the expansion's cost: seats × the per-seat prices in the [handoff](../arena-model/handoff.md) match all six built expansions to the dollar.

| # | Bought | Live by | Cost | Seats added (B / LT / CS / Lux) | Games since | Earned so far | Per full game | Payback (11 games) |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-08-26 | 2026-09-04 | $205,800 | +162 / +42 / +48 / +3 | 10 | $108,835 (53%) | $12,804 | **1.46 seasons** |
| 2 | 2026-09-04 | 2026-09-11 | $144,600 | +420 / +18 / 0 / +3 | 9 | $52,001 (36%) | $6,933 | 1.90 |
| 3 | 2026-09-11 | 2026-09-20 | $150,000 | +750 / 0 / 0 / 0 | 8 | $42,750 (29%) | $6,577 | 2.07 |
| 4 | 2026-09-20 | 2026-09-28 | $152,000 | +230 / +60 / +32 / 0 | 7 | $47,832 (31%) | $8,697 | 1.59 |
| 5 | 2026-09-28 | 2026-10-07 | $214,000 | 0 / +100 / +72 / 0 | 6 | $43,012 (20%) | $9,558 | 2.04 |
| 6 | 2026-10-14 | 2026-10-22 | $180,000 | +900 / 0 / 0 / 0 | 4 | $16,628 (9%) | $6,651 | **2.46** |
| 7 | 2026-11-09 | not built yet | $362,000 | unknown | 0 | $0 | — | no demand yet |

Real fill on the added seats, by expansion (seats used ÷ seats added, averaged over the games since):

| # | Bleachers | Lower Tier | Courtside | Luxury |
|---|---|---|---|---|
| 1 | 76.6% | 90.0% | 100% | 100% |
| 2 | 75.1% | 88.9% | — | 81.5% |
| 3 | 75.0% | — | — | — |
| 4 | 85.7% | 85.7% | 94.2% | — |
| 5 | — | 62.0% | 73.6% | — |
| 6 | 58.3% | — | — | — |

By seat type, across every built expansion:

| Tier | Seats added | Cost | Earned per added seat per full game | Payback |
|---|---|---|---|---|
| Bleachers | 2,462 | $492,400 | $8.74 | 2.08 seasons |
| Lower Tier | 220 | $154,000 | $36.05 | 1.77 |
| Courtside | 152 | $304,000 | $117.60 | 1.55 |
| Luxury | 6 | $96,000 | $948.17 | 1.53 |

**[Inference]** Courtside and luxury seats paid back fastest per dollar, and bleachers slowest. Almost half the money ($492,400) went to bleachers.

### Method

- **Seats used by an expansion.** Fans fill a tier's existing seats first. So an expansion's seats only count when attendance in that tier goes past the capacity it was built on top of: `max(0, min(attendance, capacity after) − capacity before)`. Without the expansion, the same game would have been capped at the old capacity, so this is the revenue it added at the prices actually charged.
- **Prices in effect.** For each game, the script takes the price snapshot on or just after the game day that reproduces the real gate receipts from the Economy page. **9 of 11 home games match to the dollar.** The 2026-09-01 and 2026-09-08 games don't, because `league_arena_prices` keeps one row per day and the price changed between snapshots. Those two use the nearest snapshot.
- **Playoff games** count at half value, because gate receipts are split 50/50 with the visitors (**Official**, [Standings](https://www.buzzerbeater.com/community/rules.aspx?nav=Standings); see the [Game Manual notes](../references/game-manual.md)). The quarterfinal, semifinal and final receipts are each exactly half of attendance × price.
- **Season length.** **Official:** 22 league games, so 11 at home. A deep run like this season's adds 3 home playoff games at half value, so 12.5 full-value games. That gives payback 12% shorter than the 11-game figures above (in `expansions.csv`).

### Caveats

- **[Inference]** Expansions 5 and 6 are measured on 6 and 4 games, mostly playoffs, when demand was higher (see the playoff effect below). Their regular-season payback is probably slower than shown.
- **[Inference]** Demand grew during the season as the team won. The figures assume next season's demand matches this one's. A promotion would raise it, because the promotion bonus also boosts season tickets and arena income (**Official**, [Standings](https://www.buzzerbeater.com/community/rules.aspx?nav=Standings)).
- Arena revenue per regular-season home game went from **$81,222** (2026-09-01, before any expansion was built) to **$152,142** (2026-10-24). Of that **$70,920** gain, about **$51,220** comes from the new seats. **[Inference]** The rest came from higher prices on the old seats.

## The $362,000 expansion

**Calculated.** The 2026-11-09 snapshot records a $362,000 arena expansion (`investments.capex`, and the cash projection's `change_vs_prev` of −$362,000). The arena still showed 7,900 / 720 / 212 / 8 seats that day, so the seat mix isn't known yet. The script will pick it up once a snapshot shows the new capacity.

The most fans in each tier at the current prices, and the highest attendance ever, against today's capacity:

| Tier | Capacity | Current price | Most at current price | Most ever (at a lower price) |
|---|---|---|---|---|
| Bleachers | 7,900 | $14 | 7,649 (QF, $14) | 7,649 |
| Lower Tier | 720 | $55 | 689 (Final) | 720 ($45, $47) |
| Courtside | 212 | $150 | 180 (Final) | 212 ($125) |
| Luxury | 8 | $1,300 | 7 (SF, Final) | 8 (≤ $1,066) |

**[Inference]** Even in the playoffs, the highest-demand games of the season, no tier sold out at the current prices. So new seats of any type would stay empty unless demand grows, which needs winning or promotion, or prices drop. Since expansions can't be refunded, the useful questions now are: which seats is it adding, and what price would fill them?

## Price elasticity from our own games

**Calculated** from the 9 verified home games: a log-log fit of attendance on price per tier, with a playoff dummy. It only uses games where the tier wasn't sold out. A sold-out game only shows demand was at least its attendance.

| Tier | Games used | Sold-out games left out | Elasticity | Playoff effect on attendance |
|---|---|---|---|---|
| Bleachers | 7 | 2 | **−1.51** | +45% (log 0.37) |
| Lower Tier | 5 | 4 | **−1.58** | +34% |
| Courtside | 6 | 3 | **−1.58** | +27% |
| Luxury | 3 | 6 | not enough data | |

Two regular-season pairs of home games tell the same story:

| Games | Tier | Price | Attendance | Elasticity |
|---|---|---|---|---|
| 2026-10-13 vs 10-17 (same capacity) | Bleachers | $14 → $12 | 5,545 → 7,000 (sold out) | −1.51 or more elastic |
| 2026-10-13 vs 10-17 | Lower Tier | $45 → $48 | 720 (sold out) → 632 | −2.02 or more elastic |
| 2026-10-13 vs 10-17 | Courtside | $130 → $118 | 178 → 204 | −1.41 |
| 2026-09-15 vs 09-26 | Bleachers | $12 → $14 | 5,917 → 4,950 | −1.16 |

**[Inference]** What it means for prices:

- Above an elasticity of 1 (in absolute value), revenue falls when you raise the price, until the tier sells out. The best price is the one that just fills the tier.
- At −1.5, the bleachers price rise that [Arena pricing vs. Division III peers](arena-pricing-div3.md) tested ($12 → $16, "+$9,225") would instead cut bleachers revenue by about **13%**: (16/12) × (16/12)^−1.5 ≈ 0.87.
- **[Inference]** For playoff-level demand, the bleachers price that just sells out the 7,900 seats is about **$13.7**: $14 × (7,900 / 7,649)^(−1/1.5). That's barely different from $14, so bleachers pricing is about right for big games. Regular-season games need a lower price.

**[Inference]** Limits of this fit:

- It uses only 5–7 games per tier, and opponents differ. The 2026-10-13 game was against the league leader, Blumenau Drunkers.
- Demand grew over the season while prices also rose. That pushes the estimate toward zero, so true demand may be even more price-sensitive.
- The −0.4 in `sharpshooters_arena_optimizer.py` shouldn't be used for our arena until this is refit on more games.

## Against Tom's income target

**Tom's goal (2026-11-10):** weekly income at least **$100k above the league's minimum payroll plus expenses**. The test and figures come from the Payroll projection study ([PR #10](https://github.com/tomoliveira/Sharpshooters_BB/pull/10), `studies/payroll-projection.md`). They're per payday, over the last 8 paydays.

- **Division III: $12,099 a week short (95% of target).** Gate averages **$130,285** a payday.
- **Division II:** merchandise plus gate has to reach **$221,988–$279,390** a payday, against **$161,997** today. That's **+$60k to +$117k a week**.

What the arena can add, at today's demand:

| Lever | Added per home game | Basis |
|---|---|---|
| Price each tier to just sell out | Small, a few $k | **[Inference]** The playoff bleachers price that sells out is $13.7 vs $14. Regular-season demand at today's prices isn't observed yet. |
| Sell every seat at today's prices | Up to **+$40k** vs the 2026-10-24 game ($152,142) | **Calculated.** The full house at current prices is $192,400 (`arena_live.max_sellout`). |
| Fill the $362,000 expansion | ~**$18k** if it fills like the built ones | **[Inference]** $51,220 × 362/1,046. That needs demand above today's capacity. |

**[Inference]** What it means for the target:

- **The arena can close the Division III gap.** About $12k a week is within reach of better pricing plus some demand growth.
- **It can't reach the Division II target at Division III demand.** Selling every seat at today's prices every week adds about $62k a payday over the $130k average, which only reaches the low end of the +$60k to +$117k needed. The rest has to come from the demand boost that promotion gives season tickets and arena income (**Official**, [Standings](https://www.buzzerbeater.com/community/rules.aspx?nav=Standings)), and from merchandise.
- **More seats bought ahead of demand work against the target.** The $362,000 expansion equals about 3.6 weeks of the $100k margin. Until a tier sells out in a regular-season game, cash is better kept for payroll, which also counts against the target.

## Next steps

1. **Before setting next season's prices:** find out which seats the $362,000 expansion adds, then set each tier to the price that sells it out (the elasticity above gives a starting point). Any change on buzzerbeater.com needs Tom's go-ahead.
2. **Pause new expansions** until a tier sells out at its current price in a regular-season game. **[Inference]** That's the signal that new seats in that tier would earn money.
3. **Get cleaner elasticity data:** change one tier's price by a known step between two similar regular-season games, and save the price at tip-off. One row per day in `league_arena_prices` loses same-day changes, as it did for 2026-09-08.
4. **Rerun `analyze.py`** after a few games of next season to measure expansion 7 and refresh the payback.
