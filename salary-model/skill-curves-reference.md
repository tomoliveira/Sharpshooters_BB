# Skill-to-salary curves (ground truth reference)

**Source:** buzzer-manager.com/estimation_salaire (credited by the tool to formulas by TonyLux and Josef Ka). Queried once per skill, per rating point 1–20, holding every other rating fixed — isolating each skill's own contribution to the game's salary formula. Pulled 2026-09-11.

**Held constant across all queries:** Age 30, Italy, Perennial All-Star potential, all other 11 skills fixed at 10 ("prominent"). Baseline salary with every skill at 10 is **$17,609/week** — every per-skill curve passes through this exact value at rating 10, confirming internal consistency.

## Raw data (weekly salary $, one row per skill, columns = rating 1–20)

| Skill | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jump Shot | 14194 | 14218 | 14241 | 14265 | 14289 | 14312 | 14336 | 15148 | 16332 | 17609 | 19407 | 22516 | 26122 | 30305 | 35158 | 40789 | 47321 | 54899 | 63691 | 73890 |
| Jump Range | 17515 | 17525 | 17536 | 17546 | 17556 | 17567 | 17577 | 17588 | 17598 | 17609 | 17918 | 19193 | 20558 | 22021 | 23587 | 26387 | 29574 | 33144 | 37146 | 41631 |
| Perimeter Def | 17429 | 17449 | 17469 | 17489 | 17509 | 17529 | 17549 | 17569 | 17589 | 17609 | 17712 | 18754 | 19858 | 21236 | 23864 | 26818 | 30137 | 33867 | 38058 | 42769 |
| Handling | 17537 | 17545 | 17553 | 17561 | 17569 | 17577 | 17585 | 17593 | 17601 | 17609 | 17617 | 17625 | 18415 | 19720 | 21117 | 22613 | 24215 | 25930 | 27767 | 29734 |
| Driving | 17469 | 17484 | 17500 | 17515 | 17531 | 17546 | 17562 | 17577 | 17593 | 17609 | 17624 | 17640 | 17655 | 17671 | 17928 | 18579 | 19255 | 19954 | 20680 | 21431 |
| Passing | 17400 | 17423 | 17446 | 17469 | 17492 | 17515 | 17539 | 17562 | 17585 | 17609 | 17632 | 19716 | 22607 | 25921 | 29721 | 34078 | 39074 | 44802 | 51370 | 58901 |
| Inside Shot | 16548 | 16568 | 16588 | 16608 | 16628 | 16648 | 16668 | 16688 | 16708 | 17609 | 19489 | 21569 | 23872 | 26421 | 29242 | 32364 | 35819 | 39644 | 43876 | 48561 |
| Inside Def | 14842 | 14859 | 14876 | 14894 | 14911 | 14928 | 14945 | 14967 | 15905 | 17609 | 19495 | 21583 | 23895 | 26454 | 29288 | 32425 | 35899 | 39744 | 44001 | 48714 |
| Rebounding | 10933 | 11324 | 11728 | 12148 | 12582 | 13031 | 13497 | 14389 | 15917 | 17609 | 19479 | 21549 | 23838 | 26371 | 29172 | 32271 | 35699 | 39492 | 43687 | 48328 |
| Shot Blocking | 16421 | 16455 | 16489 | 16523 | 16557 | 16591 | 16625 | 16660 | 16866 | 17609 | 18384 | 19194 | 20040 | 20923 | 21845 | 22807 | 23812 | 24861 | 25956 | 27099 |
| Stamina | 17609 (flat at every rating — zero salary effect) |
| Free Throw | 17609 (flat at every rating — zero salary effect) |

## Derived shape: two-regime exponential per skill

Every skill except Stamina and Free Throw shows `log(salary)` increasing at a small, roughly-constant "low regime" rate up to a per-skill breakpoint (~rating 7–14), then jumping to a much steeper, constant "high regime" rate for the rest of the range. This is **not** a power law (`skill^p`) — it's piecewise-linear in log-space, i.e. two back-to-back exponentials.

| Skill | Low-regime rate (per point) | High-regime rate (per point) | 1→20 salary multiplier |
|---|---|---|---|
| Jump Shot | 0.0017 | 0.1485 | 5.21× |
| Rebounding | 0.0351 (only skill with a real floor slope) | 0.1010 | 4.42× |
| Passing | 0.0013 | 0.1368 | 3.39× |
| Inside Def | 0.0012 | 0.1018 | 3.28× |
| Inside Shot | 0.0012 | 0.1014 | 2.93× |
| Perimeter Def | 0.0011 | 0.1167 | 2.45× |
| Jump Range | 0.0006 | 0.1136 (3-stage: mid-rate ~0.069 around ratings 10–14) | 2.38× |
| Handling | 0.0005 | 0.0684 | 1.70× |
| Shot Blocking | 0.0021 | 0.0431 | 1.65× |
| Driving | 0.0009 | 0.0357 | 1.23× |
| Stamina | 0 | 0 | 1.00× (zero effect) |
| Free Throw | 0 | 0 | 1.00× (zero effect) |

## Cross-validation against the Notion market regression

This lines up closely with the same-day (2026-09-11) regression fit on 266 real transfer-list rows: Stamina/Free Throw/Handling/Driving had the smallest (near-zero or negative) linear coefficients there too, and Jump Shot/Rebounding were the top two ranked coefficients. Two independent sources — noisy real market listings vs. clean isolated-skill calculator queries — agree on the same ranking.

## Open items

- Need the same isolated-curve treatment for **age**, **potential rating**, and **nationality** (hold all 12 skills at a fixed baseline, e.g. all = 10, and vary each of these in turn) to replace the market-regression's age/TSP terms with a calculator-derived baseline function.
- Jump Range's apparent 3-stage curve (low → mid ~0.069 → high ~0.114) is worth double-checking with more resolution around ratings 10–15 if a cleaner 2-stage fit is wanted.
