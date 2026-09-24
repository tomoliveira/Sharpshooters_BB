# Training priority: which skills are cheapest to develop, salary-wise

Added 2026-09-12. Moved here from the report's Investments tab on 2026-09-24.

Each skill point adds a different amount to weekly salary. The ground-truth curves come from buzzer-manager.com's salary estimator. Each of the 12 rated skills was queried at every rating from 1 to 20, holding age, nationality, potential and the other 11 skills fixed at 10. A separate 266-player real-market regression ranked the skills the same way.

Full data: [Skill-to-salary curves](../salary-model/skill-curves-reference.md) and [Salary model: formula history](../salary-model/formula-history.md).

| Skill | 1→20 salary multiplier | Shape |
|---|---|---|
| Jump Shot | 5.21× | Steep past about rating 8 |
| Rebounding | 4.42× | The only skill with a real slope at the low end: it costs something even at low ratings |
| Passing | 3.39× | Steep past about rating 11 |
| Inside Def | 3.28× | Steep past about rating 9 |
| Inside Shot | 2.93× | Steep past about rating 9 |
| Outside Def | 2.45× | Steep past about rating 10 |
| Jump Range | 2.38× | Three stages, with a mid-rate step around 10–14 |
| Handling | 1.70× | Steep only past about rating 12 |
| Shot Blocking | 1.65× | Gentle throughout |
| Driving | 1.23× | Gentle throughout |
| Stamina | 1.00× | No salary effect at any rating |
| Free Throw | 1.00× | No salary effect at any rating |

The report's "Minimize salary" training recommendation (Training Strategy tab) uses these multipliers.

## The shape of the curves

**Calculated.** Every skill except Stamina and Free Throw follows the same **two-regime shape**:

- a nearly flat "low regime" up to a skill-specific breakpoint,
- then a much steeper "high regime" for the rest of the range.

It is not a smooth power law. The baseline weekly salary with everything at rating 10 is **$17,609**. Every curve passes through that exact value, which confirms the single-skill queries are consistent with each other.

## What it means for training

**[Inference]**

- **Stamina and Free Throw training is essentially free**, salary-wise. Push them to the doctrine's 6–8 / 7+ targets without hesitation (see [Training doctrine](training-doctrine.md)).
- **Jump Shot and Rebounding** are where a big push has the largest, most convex salary effect. Time them deliberately: past each skill's breakpoint, concentrated pushes are better than a slow drip.
- **Age has no real effect** on salary once current skills are accounted for. The 266-player regression (pooled model, R² = 0.891) found no age effect. BuzzerBeater recalculates salary once a season from current skills only. An apparent "age discount" on a young player still in training is just salary that hasn't caught up with recent gains, not a market age premium.
