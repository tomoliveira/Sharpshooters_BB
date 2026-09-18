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
comparing combos within the same training type. "Players" is a team-wide
multiplier (per Tom, 2026-09-18): a 2-position combo trains roughly
double the roster, a 3-position combo triple, Team training the full
five-player rotation — "Total pts/week" is Sum &times; Players, a
team-wide estimate rather than a per-player rate. Skill abbreviations:
JS = Jump Shot, JR = Jump Range, OD = Outside Defense, Ha = Handling,
Dr = Driving, Pa = Passing, IS = Inside Shot (Inside Scoring),
ID = Inside Defense, Rb = Rebounding, SB = Shot Blocking.

| Training type | Position combo | Coefficients | Sum | Players | Total pts/week |
|---|---|---|---|---|---|
| Jump Shot | PG/SG, SG/SF | 0.5 JS, 0.1 JR, 0.05 Ha, 0.05 Dr | 0.70 | x2 | 1.40 |
| Jump Shot | SF/PF | 0.4 JS, 0.2 IS, 0.05 JR | 0.65 | x2 | 1.30 |
| Jump Shot | Team | 0.22 JS, 0.04 JR, 0.02 Ha, 0.02 Dr | 0.30 | x5 | 1.50 |
| Outside Shooting | SG | 0.4 JR, 0.2 JS, 0.05 Ha, 0.05 Dr | 0.70 | x1 | 0.70 |
| Outside Shooting | PG/SG, SG/SF | 0.3 JR, 0.15 JS, 0.04 Ha, 0.04 Dr | 0.53 | x2 | 1.06 |
| Outside Shooting | Team | 0.1 JR, 0.05 JS, 0.01 Ha, 0.01 Dr | 0.17 | x5 | 0.85 |
| Pressure (Outside Def.) | PG | 0.5 OD, 0.1 ID, 0.05 Ha, 0.05 Dr | 0.70 | x1 | 0.70 |
| Pressure (Outside Def.) | PG/SG | 0.38 OD, 0.08 ID, 0.04 Ha, 0.04 Dr | 0.54 | x2 | 1.08 |
| Pressure (Outside Def.) | PG/SG/SF | 0.2 OD, 0.04 ID, 0.02 Ha, 0.02 Dr | 0.28 | x3 | 0.84 |
| One on One | PG/SG | 0.5 Dr, 0.4 Ha, 0.4 JS | 1.30 | x2 | 2.60 |
| One on One | SF/PF | 0.5 Dr, 0.4 Ha, 0.2 JS, 0.2 IS | 1.30 | x2 | 2.60 |
| One on One | Team | 0.16 Dr, 0.15 Ha, 0.09 JS, 0.09 IS | 0.49 | x5 | 2.45 |
| Ball Handling | PG | 0.5 Ha, 0.4 Dr, 0.1 OD | 1.00 | x1 | 1.00 |
| Ball Handling | PG/SG | 0.38 Ha, 0.3 Dr, 0.08 OD | 0.76 | x2 | 1.52 |
| Ball Handling | PG/SG/SF | 0.2 Ha, 0.16 Dr, 0.04 OD | 0.40 | x3 | 1.20 |
| Passing | PG | 0.6 Pa, 0.16 Ha, 0.16 Dr | 0.92 | x1 | 0.92 |
| Passing | PG/SG | 0.45 Pa, 0.12 Ha, 0.12 Dr | 0.69 | x2 | 1.38 |
| Passing | Team | 0.15 Pa, 0.04 Ha, 0.04 Dr | 0.23 | x5 | 1.15 |
| Inside Scoring | C | 0.5 IS, 0.1 JS, 0.05 ID | 0.65 | x1 | 0.65 |
| Inside Scoring | PF/C | 0.38 IS, 0.08 JS, 0.04 ID | 0.50 | x2 | 1.00 |
| Inside Scoring | SF/PF/C | 0.2 IS, 0.04 JS, 0.02 ID | 0.26 | x3 | 0.78 |
| Inside Defense | C | 0.5 ID, 0.10 SB, 0.05 IS | 0.65 | x1 | 0.65 |
| Inside Defense | PF/C | 0.38 ID, 0.08 SB, 0.04 IS | 0.50 | x2 | 1.00 |
| Inside Defense | SF/PF/C | 0.2 ID, 0.04 SB, 0.02 IS | 0.26 | x3 | 0.78 |
| Rebounding | PF/C | 0.5 Rb, 0.05 IS, 0.05 ID | 0.60 | x2 | 1.20 |
| Rebounding | Team | 0.22 Rb, 0.02 IS, 0.02 ID | 0.26 | x5 | 1.30 |
| Shot Blocking | C | 0.5 SB, 0.2 ID, 0.1 Rb | 0.80 | x1 | 0.80 |
| Shot Blocking | PF/C | 0.38 SB, 0.15 ID, 0.08 Rb | 0.61 | x2 | 1.22 |
| Shot Blocking | SF/PF/C | 0.2 SB, 0.08 ID, 0.04 Rb | 0.32 | x3 | 0.96 |

**Reading it:** the narrowest position combo (single position, e.g. "C"
or "PG") always has the highest Sum for its training type — spreading a
training focus across more positions dilutes the per-player rate, which
matches BuzzerBeater's own effectiveness-percentage discounts on the
training.aspx dropdowns (see `training_dropdown_map.md`). A training
type's primary skill (e.g. SB for Shot Blocking, ID for Inside Defense)
always carries the largest single coefficient in its row, with the
other 1-2 skills listed as secondary/incidental gains from the same
training. Total pts/week reverses the Sum ranking in several rows —
e.g. One on One (PG/SG) at 2.60 beats every other row despite a
middling Sum, because it's both a high-Sum combo *and* trains 2
players — since it rewards breadth of players trained as much as
depth of per-player rate.

## How this could be used in the report

`docs/sharpshooters/index.html`'s Training Strategy tab has a static
card transcribing this table (not live-computed — this is training
mechanics, not a per-player stat), placed under "General training
priorities" as a quantitative complement to the hand-written doctrine
there.
