## 2026-09-11 — Position-split test, N=266 (no new players; same dataset as the first entry)

**Direction confirmed: future models should be fit per position, not pooled.** Following the bb-salary-calc spreadsheet lead (see `skill-curves-reference.md` and below), tested whether splitting the regression by position (PG/SG/SF/PF/C) improves the fit versus pooling everyone together.

**Also: Age is dropped from this and all future primary models** — confirmed by Tom (2026-09-11) to have zero effect on the real salary formula, along with Potential and Nationality. Any prior Age coefficient was a recalculation-lag artifact, not a real predictor.

### Simple TSP-only model (`log(Salary) = a + b·TSP`), pooled vs. per-position

| Scope | N | R² | obs/predictor |
|---|---|---|---|
| Pooled (no split) | 266 | 0.749 | 133.0 |
| PG | 77 | 0.869 | 38.5 |
| SG | 53 | 0.913 | 26.5 |
| SF | 58 | 0.895 | 29.0 |
| PF | 41 | 0.646 | 20.5 |
| C | 37 | 0.650 | 18.5 |

Splitting by position lifts R² substantially for guards and small forwards (0.75 pooled → 0.87–0.91 split) — real evidence that different positions price Total Skill Points differently, consistent with the bb-salary-calc spreadsheet's position-dependent weight tables. Bigs (PF/C) didn't improve, most likely smaller-N variance rather than a real "position doesn't matter for bigs" effect.

### Full 10-skill model per position — attempted, result discarded as overfit

Fitting the full 10-skill linear model (no Stamina/Free Throw, no Age) separately per position produced R²=0.987–0.995, but with obs/predictor ratios of only 3.4–7.0 (well under the 10× rule of thumb) — this is overfitting on noise, not a real result, and should **not** be treated as evidence of anything. Don't re-attempt a full per-position skill model until N is much larger — target roughly 500+ rows per position (2500+ total) before trying this again.

### Bottom line / what changes going forward

- Primary reference model stays the **pooled** 10-skill linear model (Stamina/Free Throw/Age excluded) until per-position sample sizes are large enough to support a full per-position skill model without overfitting.
- The **simple per-position TSP model** is now a legitimate secondary reference — report it alongside the pooled model, not as a replacement for it.
- As more players get added, re-run the per-position full-skill-model check periodically (it only makes sense once N/position climbs well past 10× the predictor count) — this is a placeholder for when that threshold is reached.
## 2026-09-11 — N=266 (first GitHub sync)

**⚠️ Age is not a real market driver.** BuzzerBeater recalculates salaries automatically once per season (at season start), purely from a player's current skills — there is no in-season "age premium." Younger/still-training players can look underpaid relative to current skills simply because their salary hasn't been recalculated since they trained up. Read the Age coefficient below as a proxy for *time since last recalculation*, not a real price the market pays for age.

**Methodology note:** per Tom, every skill is expected to price convexly, and the exponent should be *fitted*, not assumed to be 2. This entry's model lets Jump Range and Shot Blocking float (grid-searched over p ∈ [1.0, 3.5]); the other 10 skills are still linear. The rest of the skills generalizing to fitted exponents is the next step, pending more data — see SKILL.md "Target methodology."

### Primary model
`log(Weekly Salary) = 5.9748 + Σ(skill_i × coef_i) + 0.0303·Age + 0.0461·JumpRange^1.5 + 0.1132·ShotBlocking^1.2`

N = 266, R² = 0.8911, obs/predictor ≈ 17.73 (15 predictors: 12 linear skills + age + 2 fitted-exponent terms)

Linear skill coefficients, ranked highest → lowest:

| Skill | Coef |
|---|---|
| Rebounding | +0.0976 |
| Jump Shot | +0.0815 |
| Inside Def | +0.0673 |
| Outside Def | +0.0472 |
| Inside Shot | +0.0348 |
| Passing | +0.0287 |
| Driving | +0.0206 |
| Stamina | +0.0068 |
| Handling | −0.0038 |
| Free Throw | −0.0052 |
| Jump Range (linear term) | −0.1571 |
| Shot Blocking (linear term) | −0.1840 |

(Jump Range and Shot Blocking's linear coefficients are negative because their pricing is captured by the fitted-exponent term instead — net effect is convex-increasing, see marginal tables below.)

Fitted exponents (grid search, R² was flat across p ∈ [1.0, 3.5] — not strongly identified on this N):
- Jump Range exponent: 1.5 (best of grid; R² ranged 0.883–0.890 across the tested exponents)
- Shot Blocking exponent: 1.2 (best of grid; R² ranged 0.888–0.891 across the tested exponents)

Marginal salary effect (all else held at sample mean):

| Jump Range | Predicted Salary | Shot Blocking | Predicted Salary |
|---|---|---|---|
| 5 | $43,710 | 5 | $50,222 |
| 10 | $51,110 | 10 | $55,124 |
| 15 | $78,899 | 15 | $67,621 |
| 18 | $114,292 | 18 | $79,491 |
| 20 | $152,470 | 20 | $89,761 |

### Simpler reference model
`log(Weekly Salary) = 5.65 + 0.033·TSP + 0.056·Age` — R² = 0.787, N = 266

### Sanity check (3 random players, predicted vs. actual)
- Mitar Nikolić (53509265): actual $214,838, predicted $190,917
- Kazimierz Papierz (55116214): actual $17,294, predicted $23,123
- Ferruccio Anastasio (54045494): actual $67,302, predicted $46,110

No wild outliers; predictions within a reasonable range of actuals for a log-linear fit on noisy market data.

### Data source
Pulled live from Notion "BB Player Salaries" (data source `05d93a70-1d92-4755-9080-448eb7ed46c2`), all 266 existing rows (no new players added this run — this was a formula re-fit + first-ever GitHub sync, not a new transfer-list pull).
