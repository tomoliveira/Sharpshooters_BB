# Training strategy notes — promotion-era priorities

## Tom's stated preference (2026-09-19)

> III division is pretty easy and I don't want to accumulate much salary
> before promoting. I'm willing to maximize these players' training as
> much as possible while keeping their salary low while they carry my
> team to a promotion.

**Standing interpretation:** while Sharpshooters are in an "easy"
Division III conference, prioritize **cheap, fast skill development**
over the hand-written training doctrine's textbook priority order (see
`docs/sharpshooters/index.html`'s "General training priorities" section
- Bigs: ISP first; Guards: OSP first). Salary payroll matters far less
right now than it will post-promotion, since a harder conference will
both demand more from the roster and make payroll discipline matter
more. **Revisit this once promoted** - re-check whether doctrine-priority
training (which optimizes for what actually helps a player's on-court
role) should retake priority over pure salary efficiency.

This preference is now a selectable mode in the report itself (Training
Strategy tab, "Training focus recommendation" card) rather than
something only captured here - **"Minimize salary" is the default mode**
for a first-ever visit to the report, reflecting this preference; "Doctrine
priority" is still available as a toggle for whenever that's the more
useful lens again.

## The $-efficiency methodology

For each training type + position combo with reference data (see
`training_coefficients.md` in this folder), score it as:

```
score = sum over every skill it touches of (weekly coefficient / salary multiplier)
```

using the 1→20 salary multipliers from the report's "Training priority"
card (Investments tab - ground-truth curves from buzzer-manager.com's
salary estimator, cross-validated against a 266-player market
regression). A higher score means more skill development per unit of
salary cost. The training type with the highest score, among those with
reference data for the candidates' actual position combo, is the
recommendation.

**Why this beats a naive "biggest Sum" comparison:** the Training type
efficiency table's "Sum" column treats every skill point as equally
valuable, but skills don't cost the same in salary. Two training types
can have similar Sums while one trains cheap skills (Driving 1.23×,
gentle throughout) and the other trains the single most expensive skill
in the game (Jump Shot 5.21×, steep past ~8) - the $-efficiency score
separates those cases the Sum column can't.

## Worked example: Rebounding vs. One on One vs. everything else, for forwards

This is the analysis that led to building the "Minimize salary" mode,
computed for the SF/PF combo (a pure forwards group, no true center):

| Training (combo) | $-efficiency score | vs. best |
|---|---|---|
| **One on One (SF/PF)** | **0.75** | — |
| Shot Blocking (PF/C) | 0.29 | 2.5× worse |
| Inside Defense (PF/C) | 0.18 | 4.2× worse |
| Jump Shot (SF/PF) | 0.17 | 4.5× worse |
| Inside Scoring (PF/C) | 0.16 | 4.8× worse |
| Rebounding (PF/C) | 0.15 | 5.2× worse |

One on One wins by a wide margin: its two dominant skills, Driving
(1.23×, gentle throughout - the second-cheapest skill in the game) and
Handling (1.70×, steep only past ~12), are both cheap, and the
Sharpshooters' training cohort sits well below both skills' steep
breakpoints today (Driving avg ~2.3, Handling avg ~4.5 as of
2026-09-18). Rebounding, by contrast, is the one skill with **no cheap
floor at all** - it costs the full 4.42× rate from rating 1 onward.

**Important caveat, confirmed live in the report (2026-09-19):** this
SF/PF-specific result does NOT directly apply to the actual current
training cohort, which is C/PF (Lauro Mendonça is a true center, not a
forward) - `TRAINING_COEFFICIENTS` has no captured One on One or Jump
Shot entry at the "C/PF" combo (only "SF/PF"), so the report's
"Minimize salary" mode correctly excludes them for that cohort rather
than guessing, and currently recommends **Shot Blocking (C/PF)** instead
(score 0.294 - still the best of what's actually documented for that
exact combo). One on One becomes the top pick again specifically once
the cohort is SF/PF (forwards without a true center), or if
`training_coefficients.md` is ever extended with a captured
One-on-One/Jump-Shot row at C/PF.

## Where this lives in the report

`docs/sharpshooters/index.html`'s Training Strategy tab, "Training focus
recommendation" card - `ssbbBuildTrainingRecommendations(mode)` /
`ssbbRankTrainingBySalaryEfficiency(comboKey)` / `SALARY_MULTIPLIERS` in
the page's own JS. Mode is a per-browser toggle (`ssbb-recommendation-
mode` in localStorage, defaults to `"salary"`), independent of the
calculator's own type/combo selection above it.
