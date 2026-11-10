# Profit engine for winning stints

Added 2026-11-10. Static snapshot, not recomputed by the daily job. Scripts and outputs in [`profit-engine/`](profit-engine/) (`python3 studies/profit-engine/flip_trend.py`, `python3 studies/profit-engine/cash_plan.py`).

Tom's goal (2026-11-10): balance profit and wins, because profit pays for future winning stretches. This study asks three things: how much cash one winning stretch costs, whether the post-draft teenage flip still pays, and which visible skills set a teenager's resale price. The first two are answered from data already in the repo. The third is **blocked**: it needs final sale prices from the transfer list, and buzzerbeater.com refuses connections from cloud sessions (proxy 403 and `robots_disallowed`, checked 2026-11-10).

## Short answer

- **A two-season stretch at Division II's floor payroll costs about $2.0M–$2.5M in salary above what our Division III income carries.** After the $750k promotion bonus and today's $283k cash, that's **0.9–1.7 seasons of saving** at our projected payroll. Contending in Division II (median payroll) takes **3.4–4.9 seasons** of saving. **Calculated**, salary only (see caveats).
- **Flips still sell, but the engine is a fraction of what it was.** Młoty Stargard's profitable flips fell from **23 a year (2017–2020, $4.8M profit a year)** to **2.3 a year (2024–2026, $163k a year)**. Median sale prices held near $195k–$204k through 2025, so a flip that sells still pays well; there are just far fewer of them. **Calculated** from the 134 recorded flips.
- **The flip window is open now.** Młoty bought 97% of its flips in the first 14 days of a season (median day 5) and sold at a median day 44 (quartiles day 34–57). Season 74 started around **2026-11-09**, so the buy window runs to about **2026-11-23** and the sell window to about **2026-12-13 to 2027-01-05**. **Calculated** from season dates.
- **Three flips a season at the 2024–2026 median profit ($78k) would cut the saving time for a Division II stretch by about half a season.** At the 2021–2023 median ($135k) it's closer to a full season. **Calculated.**
- **We already hold zero-cost flip candidates.** Three players first appeared on our roster in the 2026-11-09 snapshot: Danilo Luza (19, MVP potential, $2,575/wk) and Robson de Castilho and Nizan Stucco (19, superstar potential). **[Inferrence]** They're this season's draftees; the ledger records them as `drafted` with no fee. Młoty's profitable MVP and superstar flips sold at a median **$191k** and **$130k**. **Tom's decision (2026-11-10): he is selling the new draftees.** Their sale prices are free data points for section 3.

## 1. What one winning stretch costs

**Inputs**, all copied from other studies:

| Input | Value | Source |
|---|---|---|
| Payroll our Division III income carries (break-even) | $178k–$197k per payday | [Payroll projection](https://github.com/tomoliveira/Sharpshooters_BB/pull/10) (PR #10, draft), ledger 2026-08-17 to 2026-11-09. **Official** ledger, **calculated** |
| Our payroll after the season-start recalculation | $109k per payday | Same study, log-linear skill model. **Calculated** |
| Paydays per season | 13 | [Season structure](season-structure.md). **Official** |
| Promotion bonus into Division II | $750k | [Game manual](../references/game-manual.md). **Official** |
| Cash on 2026-11-09 | $283,141 | `docs/report.db`, snapshot 2026-11-09 17:40. **Official** |
| Stretch payroll targets | Div III league winners' median $245k; Div II p10 $276k; Div II median $388k | [Salaries by division level](salary-by-division.md), Brazil S73 human teams. **Calculated** |

**Method.** Saving per season = (break-even − $109k) × 13, plus flip profit. Stretch cost = (target payroll − break-even) × 13 × 2 seasons, minus flip profit. Cash needed = stretch cost − promotion bonus (Division II targets only) − today's cash. Each scenario runs at both ends of the break-even range. Full grid in [`cash_plan.csv`](profit-engine/cash_plan.csv).

| Two-season stretch | Stretch cost | Seasons of saving, no flips | With 3 flips/season at $78k | With 3 flips/season at $135k |
|---|---|---|---|---|
| Div III title push ($245k) | $1.25M–$1.74M | 0.8–1.6 | 0.4–0.9 | 0.1–0.5 |
| Div II survival ($276k) | $2.05M–$2.55M | 0.9–1.7 | 0.4–0.9 | 0.1–0.5 |
| Div II contender ($388k) | $4.97M–$5.46M | 3.4–4.9 | 2.5–3.5 | 2.0–2.8 |

(Stretch cost shown without flips. The Division II rows subtract the $750k bonus before dividing; the Division III row does not, since the bonus only arrives on promotion.)

**Caveats, which pull in opposite directions:**

- **Transfer fees aren't counted.** The table prices salary only. Buying salary costs fees on top: Młoty paid $1.3M–$6.8M for core players on $42k–$173k a week ([Top teams report](../top-teams-research/BB_Top_Teams_Strategy_Report.md), section 4). Payroll that grows through training costs no fee, which is the doctrine's advantage. This makes the table **optimistic**.
- **Division II income isn't known.** Break-even uses Division III income. **[Inferrence]** Division II's TV money, gate and merchandise are probably higher, which makes the Division II rows **pessimistic**.
- **Arena spending competes for the same surplus.** This season's $1.41M of arena expansion used up the whole operating surplus ([Payroll projection](https://github.com/tomoliveira/Sharpshooters_BB/pull/10)). Every season of arena capex at that size adds about a season to the saving times above.
- **Acquisition limit.** At world rank 13,701 we could only buy players earning up to $116,779 a week ([Top teams report](../top-teams-research/BB_Top_Teams_Strategy_Report.md), section 7). A Division II contender roster needs a few players above that, so it has to be trained or bought after our rank improves.
- **Cash ceilings don't bind.** The hoarding tax starts at $25M ([Game manual](../references/game-manual.md)), far above any figure here. The floor that matters is debt: below −$500k for two weekly updates, the whole roster is listed at $0. **[Inferrence]** Keep at least one season's stretch deficit in reserve before starting a stretch, so a bad season can't trigger a forced sale.

## 2. Do post-draft flips still pay?

**Data.** Młoty Stargard's 134 profitable teenage flips, 2017-03 to 2026-06, in [`mloty_stargard_teen_flips.csv`](../top-teams-research/mloty_stargard_teen_flips.csv). **Official** public transfer histories, collected 2026-09-24. Output in [`flip_trend.json`](profit-engine/flip_trend.json).

| Years bought | Flips | Per year | Median buy | Median sale | Median profit | Profit per year |
|---|---|---|---|---|---|---|
| 2017–2020 | 92 | 23.0 | $22k | $203k | $195k | $4.83M |
| 2021–2023 | 35 | 11.7 | $56k | $187k | $135k | $1.74M |
| 2024–2026 | 7 | 2.3 | $26k | $99k | $78k | $0.16M |

By year since 2023 (**calculated**):

| Year | Flips | Median buy | Median sale | Median profit |
|---|---|---|---|---|
| 2023 | 7 | $101k | $195k | $102k |
| 2024 | 1 | $21k | $99k | $78k |
| 2025 | 3 | $84k | $204k | $120k |
| 2026 | 3 | $6k | $52k | $46k |

- **Sale prices held up until 2025; volume didn't.** The 2025 flips still sold at a median $204k. **[Inferrence]** The drop in volume could be Młoty choosing to flip less, or fewer flips working out. The data only holds profitable resales, so it can't tell the two apart.
- **Buy prices rose before volume fell.** Median buy went from $10k–$13k (2017–2018) to $67k–$101k (2022–2023). **[Inferrence]** More managers bidding on draftees right after the draft would explain both the higher buy prices and the thinner margins.
- **2026 is three flips** ($8k, $52k and $175k sales). Too few to say prices have collapsed.
- **Survivorship.** Młoty bought 239 teenagers and only these 134 resold at a profit ([Top teams report](../top-teams-research/BB_Top_Teams_Strategy_Report.md), section 4). The other 105 aren't priced here, so the true return per attempt is lower than these medians.
- **Sale prices are gross.** The manual says agent fees fall with longer ownership and fewer sales in the last 14 weeks ([Game manual](../references/game-manual.md)); the rate isn't in our summary, so the profits above are before fees.

**By potential** (all years, **calculated**):

| Potential | Flips | Median buy | Median sale |
|---|---|---|---|
| Hall of famer | 74 | $44k | $229k |
| MVP | 49 | $22k | $191k |
| Superstar | 11 | $10k | $130k |

**Timing** (**calculated**, against official season starts in [`seasons.csv`](../top-teams-research/data/seasons.csv)):

- 97% of buys came in the first 14 days of a season, median day 5.
- Sales came at a median day 44 (quartiles 34 and 57).
- The last eight seasons ran 96–98 days. Season 73 started 2026-08-04, so Season 74 started around **2026-11-09**. That matches three new 19-year-olds first appearing on our roster in the 2026-11-09 14:43 snapshot.

**Our own recent teenage buys**, for comparison (`docs/report.db`, investments ledger, **official**; potential words from the manual scale in `scripts/bbapi_lib.py`):

| Player | Bought | Price | Age | Potential |
|---|---|---|---|---|
| Stefos Akrivopoulos | 2026-11-04 | $114,100 | 19 | Hall of famer |
| Gunnar Støen | 2026-08-26 | $42,820 | 19 | Superstar |
| Tapati Venkateswarlu | 2026-11-06 | $25,000 | 20 | MVP |
| Piotr Wiszowata | 2026-08-26 | $16,000 | 19 | Star (5) |

**[Inferrence]** These were bought to train, not to flip. Akrivopoulos cost about 2.6× Młoty's median hall-of-famer buy, but still under half its median hall-of-famer sale.

## 3. Which visible skills set the resale price? (blocked)

**Why it's blocked.** Public transfer histories show the price but not the skills at the time of sale, so Młoty's flips can't answer it. The transfer list shows skills while a player is listed, and the final price appears afterwards. Both need buzzerbeater.com, which cloud sessions can't reach. The 18-year-olds in [`salary-model/players.csv`](../salary-model/players.csv) (8 players, 2026-09-11) only have asking prices of $1.0M–$2.6M, far above any recorded flip, so they say nothing about what sells.

**What unblocks it.** A weekly sweep of listed 18–19-year-olds during weeks 0–8 of a season, recording skills, potential, height and salary at listing and the final price (or no sale) after the deadline. The pull budget is in [`pull_budget.csv`](profit-engine/pull_budget.csv): about 420 pulls a week at 30 a minute, about 14 minutes a sweep and 2 hours a season. It has to run from Tom's computer or browser. The salary-model workflow already pulls transfer-list players with their skills; it would need a final-price column.

**Fit to run once ~150 sales are in:** `log(sale price) ~ potential + height + age + each skill`, the same form as the salary model, so the two can be compared skill by skill.

## What this means

**[Inferrence]** throughout.

- **The cheapest profit engine is our own draft.** A draftee costs no fee. If one of this season's draftees sells near the historical MVP or superstar medians, that's $130k–$190k, about 1.5–2.8 paydays of our projected operating surplus ($69k–$88k a payday at a $109k payroll). The trade-off: the manual says self-drafted players raise merchandise sales, and the training doctrine may want them. Tom decided on 2026-11-10 to sell this season's draftees. He doesn't want live sales or bids run as experiments; findings come from recorded data only.
- **Buying to flip is a weaker bet than it was.** Margins halved from 2017–2020 to 2021–2023, and a buyer now pays more up front. A test of one or two buys would cost little, but it can't be judged until the skills-to-price data exists.
- **For the saving plan:** keep payroll growth to training, keep arena capex below the surplus, and treat a Division II floor stretch as about 1–2 seasons away, or about one season with a modest flip habit. A Division II contender stretch is 2–5 seasons away and also needs a better world rank to buy players above $116,779.

## Next steps

1. Record each draftee's skills, potential, height and salary at listing, and the final price, as the first rows of the skills-to-price data. Młoty's timing puts the best sell window at about 2026-12-13 to 2027-01-05.
2. Run the transfer-list sweep from Tom's computer during weeks 0–8 of Season 74, then fit the skills-to-price model.
3. Rerun [`cash_plan.py`](profit-engine/cash_plan.py) once Season 74 salaries post and once Division II income figures are known.
