# Skill prices: calculator curves vs. the real market

Added 2026-11-10. Tests the three open contradictions about how much each skill costs in salary. Scripts: [`analysis/calculator_vs_market.py`](analysis/calculator_vs_market.py) and [`analysis/salary_rollover.py`](analysis/salary_rollover.py). Both run on data already in the repo.

## Read this first: the prices may change this week

The Notion pages for [Gintaras Selvinavicius](https://app.notion.com/p/3db9ccbce26681309930f26f47e21a4e) and [Costante Martellini](https://app.notion.com/p/3db9ccbce26681be8224dc70f11b1e99) (updated 2026-10-09) quote BuzzerBeater's official "Season 74 Update: Salaries, Hoarding Tax, Training and Our Next Steps" announcement: *"Salary formulas: We will return to the formulas used in Season 72 and earlier."* I could not open the announcement from here, so that quote is only as good as the Notion copy.

**Calculated.** Season 73 has not ended yet in our data. Our last games were the league finals on 2026-11-03 and 2026-11-07 (`match_ratings` in `docs/report.db`). Not one of our 9 tracked players had a salary change in the 144 snapshots from 2026-09-03 to 2026-11-09 (`salary_rollover.py`). So no Season 74 recalculation has happened yet.

**[Inferrence]** If the announcement holds, everything measured under the Season 73 formula expires at the rollover. That includes the 266-player dataset (pulled 2026-09-11, mid-Season 73) and the "Shot Blocking was repriced up" finding. The old formula that comes back is the one the patch notes called "very cheap" for Shot Blocking.

## Test 1: does the calculator match real salaries?

Method: for each skill, take the calculator's own curve, `f(s) = ln(calc(s) / 17,609)`, from [skill-curves-reference.md](skill-curves-reference.md). Then fit `ln(salary) = a + Σ β·f(skill)` on the 266 players, with position intercepts. If the calculator were the game formula, every β would be 1. Ratings above 20 are extrapolated at each curve's 19→20 rate. The 90% intervals come from 2,000 bootstrap resamples. R² = 0.909.

| Skill | Calculator 1→20 | Market 1→20 | Market 90% interval | Verdict |
|---|---|---|---|---|
| Rebounding | 4.42× | **8.65×** | 6.65–10.83× | Market is steeper. The most expensive skill. |
| Jump Shot | 5.21× | 5.37× | 4.52–6.39× | Agrees |
| Jump Range | 2.38× | **3.95×** | 3.04–5.37× | Market is steeper |
| Inside Def | 3.28× | 3.24× | 2.60–3.99× | Agrees |
| Outside Def | 2.45× | 1.87× | 1.65–2.11× | Market is cheaper |
| Passing | 3.39× | 1.71× | 1.29–2.44× | Market is cheaper (moves a lot with position controls) |
| Handling | 1.70× | 1.45× | 1.15–1.87× | Roughly agrees |
| Inside Shot | 2.93× | **1.30×** | 1.14–1.46× | Market is much cheaper |
| Shot Blocking | 1.65× | **1.15×** | 0.86–1.50× | Market is cheaper, not dearer |
| Driving | 1.23× | 0.92× | 0.74–1.11× | No measurable price |

**Calculated.** Taking the calculator literally, multiplying the 10 curves together, explains only R² = 0.186 of real salaries. It overpredicts the median player by about 1.7× (actual/predicted 0.60), and overpredicts players above $180k by about 5× (0.21). The curves are usable as single-skill shapes, not as a salary formula.

### Shot Blocking by position

**Calculated.** Shot Blocking's coefficient split by position group, with the other skills pooled:

| Group | n | SB range | Market 1→20 | Standard error on β |
|---|---|---|---|---|
| Guards (PG/SG) | 130 | 1–14 | 0.85× | 0.80 (no signal) |
| SF | 58 | 3–13 | 6.20× | 0.98 (noisy, narrow range) |
| Bigs (PF/C) | 78 | 4–22 | 1.13× | 0.28 |

**Calculated.** At PF/C, where Shot Blocking actually varies (up to 22), the market put almost no price on it during Season 73. One caveat: among bigs, Shot Blocking correlates 0.66 with Inside Def, so part of its price may be credited to Inside Def. At equal skills, centers cost 1.08× PFs, 1.12× SGs and 1.39× SFs, but 0.93× PGs (position intercepts). That partly fits the patch note that centers got dearer.

### Caveats

- One league (III.15), one day (2026-09-11), transfer-listed players only.
- **[Inferrence]** Salaries are recalculated once a season, so players trained during the season look cheap for their current skills. Skills that teams train most (likely Jump Shot, Inside Shot, Rebounding for bigs) may come out with lower prices than the formula really charges.

## Test 2: the decay curve and the Season 73 cut

[bench-player-tco.md](../studies/bench-player-tco.md) fits `% change ≈ 14.1% − 4.02% × ln(salary)` from 15 players' salary histories. **Not refittable yet:** those 15 histories are not in the repo, and a Notion search found only the 3 reference cases. Every one of those 3 cases shows the one-time Season 73 change (−8.4% at the floor; see [floor-players-and-deflation.md](reference-cases/floor-players-and-deflation.md)). **[Inferrence]** If the 15 histories end at Season 73, the last step of every series includes that cut, so the curve overstates decline by up to about 8 points in that season. If Season 74 reverts the formula, floor players should jump back about 9% ($207 → about $226), which would add the opposite error.

## What to do with this now

**[Inferrence]** For training decisions in Season 74, these readings hold under either formula, because the calculator (built on older community formulas) and the Season 73 market agree on them:

- Stamina and Free Throw: free.
- Driving and Handling: nearly free.
- Jump Shot, Rebounding and Inside Def: the expensive skills. Rebounding is likely even dearer than the calculator says.

What is formula-dependent and should be re-checked after the rollover: Shot Blocking, Inside Shot (both repriced by the Season 73 patch), and Jump Range.

## Next steps

1. **After the first Season 74 snapshot:** run `python3 salary-model/analysis/salary_rollover.py`. Same players and near-identical skills, before and after, tell us whether the old formula came back and by how much per player.
2. **Check the floor players** (12588874, 6769817): back to about $226 means the revert happened.
3. **One fresh transfer-list pull** after the rollover (buzzerbeater-salary-model skill), then rerun `calculator_vs_market.py` against it. Prioritize PF/C with Shot Blocking ≥ 12 and anyone with Jump Range ≥ 15, where the price is least certain.
4. **Export the 15 decay histories** into the repo (one CSV), so the decay curve can be refit with the Season 73 step removed.
