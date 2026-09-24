# Bench-player acquisitions: which one is cheapest, long-run?

Added 2026-09-10. Moved here from the report's Investments tab on 2026-09-24. Static analysis, not recomputed by the daily job.

A total-cost-of-ownership comparison of three hypothetical bench-player acquisitions. Salary is **projected forward** rather than held flat, using a decay curve fitted from 15 real players' season-by-season salary histories.

## The decay model

Player salaries peak around age 33–34, then decline. Fitted from the 15-player sample (log-linear regression, R² = 0.24; larger salaries drop more sharply). Each season past the peak:

`% change ≈ 14.1% − 4.02% × ln(salary)`

- A $200/week floor applies: no tracked player was ever seen below it.
- Age advances 1 year per season.
- Each season's salary cost is that season's weekly rate × **13** (Monday paydays, not a flat 14; see [Season structure](season-structure.md)).

**[Inference]** The $200 floor is empirical, drawn from the sample's lowest observed salary. It isn't a documented game rule and could be wrong.

## The three options modeled

- **A**: $800/wk, $40,000 acquisition, starting age 32
- **B**: $250/wk, $100,000 acquisition, starting age 50
- **C**: $2,000/wk, $1,000 acquisition, starting age 30

| Season | A: cumulative cost | B: cumulative cost | C: cumulative cost |
|---|---|---|---|
| 2 | $60,800 | $105,742 | **$53,000** |
| 5 | **$84,866** | $113,542 | $126,722 |
| 10 | **$110,283** | $126,542 | $195,337 |
| 15 | **$126,032** | $139,542 | $229,907 |
| 20 | **$139,032** | $152,542 | $250,015 |
| 30 | **$165,032** | $178,542 | $276,651 |

Cheapest option per season in bold.

## Result

**Calculated.** **A is cheapest from season 3 onward, indefinitely.**

- Both A and B eventually hit the $200 floor: A by season 16, B already by season 3.
- Once both are at the floor, the gap between them (B's larger acquisition price) never closes.
- C is only competitive in the first two seasons, thanks to its near-zero acquisition price. Its high starting salary catches up fast, before decay has had time to bite.
