# BuzzerBeater — Sharpshooters Training Dropdown Map

Source: https://buzzerbeater.com/manage/training.aspx (Choose Training section)
Captured: 2026-09-03

Method: for each option in the first ("Choose Training") dropdown, I selected it on the live page and read out the resulting options of the second (position/weighting) dropdown via the page's own DOM (`<select>`/`<option>` elements), then restored the page to its original selection (Inside Scoring / C-PF) afterward.

| # | Training type (1st dropdown) | 2nd dropdown options |
|---|---|---|
| 1 | Team Training | Game Shape, Free Throws, Stamina |
| 2 | Outside Defense | PG, SG (90%), SF (80%), PF (70%), C (60%), PG / SG, SG / SF (90%), SF / PF (80%), C / PF (70%), PG / SG / SF, SG / SF / PF (90%), C / PF / SF (80%) |
| 3 | Shot Blocking | C, PF (90%), SF (80%), SG (70%), PG (60%), C / PF, SF / PF (90%), SG / SF (80%), PG / SG (70%), C / PF / SF, SG / SF / PF (90%), PG / SG / SF (80%) |
| 4 | Inside Defense | C, PF (90%), SF (80%), SG (70%), PG (60%), C / PF, SF / PF (90%), SG / SF (80%), PG / SG (70%), C / PF / SF, SG / SF / PF (90%), PG / SG / SF (80%) |
| 5 | Rebounding | C / PF, SF / PF (90%), SG / SF (80%), PG / SG (70%), Team |
| 6 | Inside Scoring | C, PF (90%), SF (80%), SG (70%), PG (60%), C / PF, SF / PF (90%), SG / SF (80%), PG / SG (70%), C / PF / SF, SG / SF / PF (90%), PG / SG / SF (80%) |
| 7 | One on One | Guards, Wingmen (90%), Forwards, C / PF (90%), Team |
| 8 | Outside Shooting | SG, PG (90%), SF (90%), PF (80%), C (70%), PG / SG, SG / SF, SF / PF (90%), C / PF (80%), Team |
| 9 | Jump Shot | Guards, Forwards, Wingmen, C / PF (90%), Team |
| 10 | Ball Handling | PG, SG (90%), SF (80%), PF (70%), C (60%), PG / SG, SG / SF (90%), SF / PF (80%), C / PF (70%), PG / SG / SF, SG / SF / PF (90%), C / PF / SF (80%) |
| 11 | Passing | PG, SG (90%), SF (80%), PF (70%), C (60%), PG / SG, SG / SF (90%), SF / PF (80%), C / PF (70%), Team |

**Notes**

- "Guards" = PG/SG combined; "Wingmen" = SG/SF combined; "Forwards" = SF/PF combined (BuzzerBeater's own labels for these grouped trainings).
- The `%` figures are the site's own secondary-position training-effectiveness weights (e.g. "PF (90%)" means a player training C also gets 90% effectiveness credit toward PF).
- Inside Defense and Inside Scoring share an identical option set to Shot Blocking's pattern (C-centered, 12 options); Outside Defense, Ball Handling, and Passing share the PG-centered 10–12 option pattern; One on One and Jump Shot share the 5-option Guards/Wingmen/Forwards/C-PF/Team pattern.
- Team Training and page state were left as they were before this check (Inside Scoring / C-PF selected) once the mapping was captured.

## How this repo uses it

`docs/sharpshooters/index.html`'s training-minutes calculator (Training
Strategy tab) hardcodes this table verbatim as the JS `TRAINING_MAP`
constant. Each option label is parsed client-side: text before a trailing
`(NN%)` is split on `/` into the trained positions (or resolved via the
Guards/Wingmen/Forwards/Team group labels above), and the percentage - or
100% if none is given - is applied as a single weight across every position
in that option. Re-capture and update both this file and `TRAINING_MAP`
together if BuzzerBeater ever changes these dropdowns.
