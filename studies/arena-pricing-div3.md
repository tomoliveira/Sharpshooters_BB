# Arena pricing: where we sit vs. our Division III peers

Added 2026-09-12. Moved here from the report's Investments tab on 2026-09-24. Figures are from that date's snapshot.

336 Brazil teams scraped from public buzzerbeater.com pages: Liga Nacional, Division II and all 16 Division III conferences. That's the Sharpshooters' actual peer group, not a top-division benchmark. Full data and scripts are in [`arena-model/`](../arena-model/): `brazil_leagues_all.csv`, `brazil_league_analysis.py` and `sharpshooters_arena_optimizer.py`.

| Measure | Sharpshooters | Division III comparison |
|---|---|---|
| Revenue per game | $92,273 (**55th percentile**) | Median $80,520 across 256 teams |
| Win% | 3–7 (**22nd percentile**) | Revenue is outperforming results |
| Bleachers price | $12 | Median $10, mean $11.0 |
| Courtside price | $119 | Median $100, mean $119.1 |

## Winning and fill rate

**[Inference]** A same-snapshot check across all 336 teams found win% and fill rate **negatively** correlated (−0.17 to −0.18).

- Losing teams (win% ≤ 0.4) average 90.3% fill; winning teams (win% ≥ 0.6) average 84.5%. That's a 5.9-point gap.
- A likely confound: winning teams tend to have bigger arenas that are harder to fill, while many bottom-table teams sit at the 6,000-seat minimum and sell out regardless of form.
- So fill rate alone isn't a clean price-demand signal unless capacity and form are controlled for. See also the [Sharpshooters arena optimizer handoff](../arena-model/handoff.md).

## Price scenarios

| Tier | Current fill | Top price tested | Est. revenue per game | Est. change |
|---|---|---|---|---|
| Bleachers | 82.1% | $12 → $16 (+33%) | $68,526 | +$9,225 |
| Courtside | 100.0% | $119 → $155 (+30%) | $16,740 | +$3,888 |
| Lower Tier | 96.8% | $44 → $57 (+30%) | $27,243 | +$3,395 |
| Luxury | 62.5% | Excluded | | |

Luxury is excluded because its fill already dropped after the last expansion. Don't add more boxes or raise the price until it recovers.

## Expansion scenarios by budget

**Calculated.** From the optimizer's own recommendation engine:

| Budget | Recommended allocation | Est. added revenue per game |
|---|---|---|
| $50,000 | +25 courtside seats | +$2,975 |
| $150,000 | +40 courtside, +100 lower tier | +$9,019 |
| $500,000 (only $185,000 usefully spent) | +40 courtside, +150 lower tier | +$11,148 |

**[Inference]** The price and expansion estimates assume a flat −0.4 price elasticity, not one fitted from real data. The percentile comparisons use the 256-team Division III set, not the top-division benchmark used in [Arena expansion payback](arena-expansion-payback.md). Re-run `sharpshooters_arena_optimizer.py` and `brazil_league_analysis.py` from time to time: prices, capacity and the comparison set all drift during a season.
