# Arena expansion: payback and long-run surplus

Added 2026-09-10. Moved here from the report's Investments tab on 2026-09-24. Static analysis, not recomputed by the daily job.

Payback and surplus analysis of the real, already-executed **$205,800** arena expansion, using the report's own live arena data at the time.

| Measure | Value | How |
|---|---|---|
| Incremental revenue per full-value game | **$10,716** | ($103,449 new sellout − $92,298 old) × 96.1% average utilization |
| Payback, baseline season | **1.75 seasons** | 11 full-value-equivalent games per season |
| Payback, deep-run season | **1.48 seasons** | 13 full-value-equivalent games per season |

## Sellout revenue math

**Calculated.** At the prices of the time and full capacity:

- Before the expansion, one sellout ≈ **$92,298** in gate receipts (5,438 × $12 + 500 × $38 + 60 × $106 + 2 × $841).
- After it, the maximum sellout ≈ **$103,449** at the same prices (5,600 × $12 + 542 × $38 + 108 × $106 + 5 × $841; 6,255 seats in total).

Expansion cost per seat: Bleachers $200 (+162 seats), Lower Tier $700 (+42), Courtside $2,000 (+48), Luxury Boxes $16,000 (+3 boxes).

## Where "11" and "13" games per season come from

Modeled on a proxy schedule: Velotrol Metalizado, Season 72, a completed season with league finals plus a tie-breaker (a deep playoff run). Home games are broken down by type, using the Game Manual's arena-revenue rules:

| Type | Home games | Arena revenue treatment |
|---|---|---|
| Regular league | 9 | Full, counts |
| TV | 2 | Full, counts (treated as regular league) |
| Playoffs (PO, SF, F, TB) | 4 | Half, split with visitors |
| Cup (C) | 6 | Zero, excluded (confirmed by the manual) |
| Private League (PL) | 5 | Zero, excluded |
| B3 | 2 | Zero, excluded |
| Scrimmage (SC) | 0 | Zero, excluded (none at home that season) |
| **Total home games** | **28** | |

- Deep-run season: **9 + 2 + (4 × 0.5) = 13** full-value-equivalent games.
- Baseline season with no playoff run: drop the 4 half-value playoff games, leaving **9 + 2 = 11**.

**[Inference]** That's another team's schedule, used as a structural proxy, not the Sharpshooters' own game mix. The 96.1% fill rate is also assumed, not confirmed, to hold on the new seats specifically.

## Cumulative surplus

Cumulative incremental revenue − $205,800, assuming revenue grows at a flat annual rate.

**Baseline season (11 games a year)**

| Growth | Season 5 | Season 10 | Season 15 | Season 20 |
|---|---|---|---|---|
| 0% | $383,580 | $972,960 | $1,562,340 | $2,151,720 |
| 3% | $420,020 | $1,145,516 | $1,986,566 | $2,961,572 |
| 5% | $445,539 | $1,276,832 | $2,337,795 | $3,691,882 |
| 8% | $485,731 | $1,501,818 | $2,994,783 | $5,188,437 |
| 10% | $513,845 | $1,672,840 | $3,539,413 | $6,545,548 |

**Deep-run season (13 games a year)**

| Growth | Season 5 | Season 10 | Season 15 | Season 20 |
|---|---|---|---|---|
| 0% | $490,740 | $1,187,280 | $1,883,820 | $2,580,360 |
| 3% | $533,805 | $1,391,210 | $2,385,177 | $3,537,458 |
| 5% | $563,965 | $1,546,401 | $2,800,267 | $4,400,552 |
| 8% | $611,464 | $1,812,294 | $3,576,707 | $6,169,208 |
| 10% | $644,689 | $2,014,411 | $4,220,361 | $7,773,066 |

## Result

**Calculated.** The expansion **pays for itself within its second season in every scenario tested**.

- The growth rate barely changes the payback timing, because compounding is small over that horizon.
- It does compound the long-run surplus a lot. By season 20, the gap between 0% and 10% growth is about 3× the 0% surplus itself.

**[Inference]** The growth rates (0/3/5/8/10%) are illustrative, not checked against any real trend. Two of the four price tiers were already close to the game's price ceiling. That limits how much of any growth could come from raising prices rather than from more demand.

See also: [Arena pricing vs. Division III peers](arena-pricing-div3.md), [Season structure](season-structure.md).
