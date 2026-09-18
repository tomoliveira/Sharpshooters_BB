# BuzzerBeater — Training Type Skill Coefficients

Source: `Weekly Training Amounts.webp` in this same folder (Tom's own
capture; not pulled from a live BuzzerBeater page or the official API —
treat as a reference/community-derived breakdown of the training
mechanic, not official documentation).

Each row is one (training type, position combo) pair from the
training.aspx "Choose Training" flow (see `training_dropdown_map.md` in
this same folder for the full list of available combos per type). The
coefficients are the per-week skill-point gain rate for each skill the
combo touches, for a player who clears their weekly minutes threshold at
that position; "Sum" is those coefficients added together — a rough
"how much total skill development per week" efficiency number for
comparing combos within the same training type. Skill abbreviations:
JS = Jump Shot, JR = Jump Range, OD = Outside Defense, Ha = Handling,
Dr = Driving, Pa = Passing, IS = Inside Shot (Inside Scoring),
ID = Inside Defense, Rb = Rebounding, SB = Shot Blocking.

| Training type | Position combo | Coefficients | Sum |
|---|---|---|---|
| Jump Shot | PG/SG, SG/SF | 0.5 JS, 0.1 JR, 0.05 Ha, 0.05 Dr | 0.70 |
| Jump Shot | SF/PF | 0.4 JS, 0.2 IS, 0.05 JR | 0.65 |
| Jump Shot | Team | 0.22 JS, 0.04 JR, 0.02 Ha, 0.02 Dr | 0.30 |
| Outside Shooting | SG | 0.4 JR, 0.2 JS, 0.05 Ha, 0.05 Dr | 0.70 |
| Outside Shooting | PG/SG, SG/SF | 0.3 JR, 0.15 JS, 0.04 Ha, 0.04 Dr | 0.53 |
| Outside Shooting | Team | 0.1 JR, 0.05 JS, 0.01 Ha, 0.01 Dr | 0.17 |
| Pressure (Outside Def.) | PG | 0.5 OD, 0.1 ID, 0.05 Ha, 0.05 Dr | 0.70 |
| Pressure (Outside Def.) | PG/SG | 0.38 OD, 0.08 ID, 0.04 Ha, 0.04 Dr | 0.54 |
| Pressure (Outside Def.) | PG/SG/SF | 0.2 OD, 0.04 ID, 0.02 Ha, 0.02 Dr | 0.28 |
| One on One | PG/SG | 0.5 Dr, 0.4 Ha, 0.4 JS | 1.30 |
| One on One | SF/PF | 0.5 Dr, 0.4 Ha, 0.2 JS, 0.2 IS | 1.30 |
| One on One | Team | 0.16 Dr, 0.15 Ha, 0.09 JS, 0.09 IS | 0.49 |
| Ball Handling | PG | 0.5 Ha, 0.4 Dr, 0.1 OD | 1.00 |
| Ball Handling | PG/SG | 0.38 Ha, 0.3 Dr, 0.08 OD | 0.76 |
| Ball Handling | PG/SG/SF | 0.2 Ha, 0.16 Dr, 0.04 OD | 0.40 |
| Passing | PG | 0.6 Pa, 0.16 Ha, 0.16 Dr | 0.92 |
| Passing | PG/SG | 0.45 Pa, 0.12 Ha, 0.12 Dr | 0.69 |
| Passing | Team | 0.15 Pa, 0.04 Ha, 0.04 Dr | 0.23 |
| Inside Scoring | C | 0.5 IS, 0.1 JS, 0.05 ID | 0.65 |
| Inside Scoring | PF/C | 0.38 IS, 0.08 JS, 0.04 ID | 0.50 |
| Inside Scoring | SF/PF/C | 0.2 IS, 0.04 JS, 0.02 ID | 0.26 |
| Inside Defense | C | 0.5 ID, 0.10 SB, 0.05 IS | 0.65 |
| Inside Defense | PF/C | 0.38 ID, 0.08 SB, 0.04 IS | 0.50 |
| Inside Defense | SF/PF/C | 0.2 ID, 0.04 SB, 0.02 IS | 0.26 |
| Rebounding | PF/C | 0.5 Rb, 0.05 IS, 0.05 ID | 0.60 |
| Rebounding | Team | 0.22 Rb, 0.02 IS, 0.02 ID | 0.26 |
| Shot Blocking | C | 0.5 SB, 0.2 ID, 0.1 Rb | 0.80 |
| Shot Blocking | PF/C | 0.38 SB, 0.15 ID, 0.08 Rb | 0.61 |
| Shot Blocking | SF/PF/C | 0.2 SB, 0.08 ID, 0.04 Rb | 0.32 |

**Reading it:** the narrowest position combo (single position, e.g. "C"
or "PG") always has the highest Sum for its training type — spreading a
training focus across more positions dilutes the per-player rate, which
matches BuzzerBeater's own effectiveness-percentage discounts on the
training.aspx dropdowns (see `training_dropdown_map.md`). A training
type's primary skill (e.g. SB for Shot Blocking, ID for Inside Defense)
always carries the largest single coefficient in its row, with the
other 1-2 skills listed as secondary/incidental gains from the same
training.

## How this could be used in the report

`docs/sharpshooters/index.html`'s Training Strategy tab has a static
card transcribing this table (not live-computed — this is training
mechanics, not a per-player stat), placed under "General training
priorities" as a quantitative complement to the hand-written doctrine
there.
