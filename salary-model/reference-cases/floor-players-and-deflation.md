# Reference cases: salary floor + the season-73 salary formula replacement

Added 2026-09-14. Two independent players with every skill at the absolute minimum (1 = atrocious, except Free Throw which is a confirmed zero-effect skill) — skills that literally cannot decay any further, at ages 94 and 85.

**Update 2026-09-14 (later same day): the ~8.4% drop below is now confirmed as an official, one-time salary formula replacement, not a mystery periodic deflation.** See "Official explanation" section near the end — read that before drawing conclusions from the numbers below.

## Gintaras Selvinavicius (12588874) — SF, age 94

Skills: all 1 except Free Throw 14. TSP 10 (6 off + 4 def). Weekly Salary $207 (secondary $377). Owner: Pensionatas ''Atgrubnagiai''.

| Season | Salary | Change |
|---|---|---|
| 11 | $2,493 | — |
| 12 | $2,515 | +0.9% |
| 13 | $2,703 | +7.5% |
| 14 | $2,240 | −17.1% |
| 15 | $1,949 | −13.0% |
| 16 | $1,809 | −7.2% |
| 17 | $1,584 | −12.4% |
| 18 | $1,455 | −8.1% |
| 19 | $1,291 | −11.3% |
| 20 | $944 | −26.9% |
| 21 | $705 | −25.3% |
| 22 | $652 | −7.5% |
| 23 | $566 | −13.2% |
| 24 | $447 | −21.0% |
| 25 | $335 | −25.1% |
| 26–27 | $335 | flat |
| 28–32 | $330 → $316 | small annual decay |
| 33 | $267 | −15.5% |
| 34 | $279 | +4.5% |
| 35–46 | $262 → $227 | gradual decay, decelerating |
| 47–72 | **$226, flat for 26 straight seasons** | 0.0% every season |
| 73 (current) | **$207** | **−8.41%** |

## Costante Martellini (6769817) — PF, age 85

Skills: all 1 except Free Throw 15. TSP 10 (6 off + 4 def). Weekly Salary $208 (secondary $377). Owner: provatina united.

| Season | Salary | Change |
|---|---|---|
| 7 | $4,398 | — |
| 8–13 | $4,751 → $7,919 | rising (still had some skill early on) |
| 14–24 | $6,702 → $5,452 | decline |
| 25–32 | $4,106 → $801 | steep decline |
| 33–49 | $579 → $231 | decelerating decay |
| 50–64 | $230 → $226 | near-floor, tiny wobble |
| 65–72 | $228 → $227 | still near-floor |
| 73 (current) | **$208** | **−8.37%** |

## Fortunato Ravagnin (43354311) — C, age 52 (near-floor, third confirmation)

Skills: mostly 1, Rebounding 2, Stamina 2 (near-zero/zero-effect), Free Throw 14. TSP 11 (6 off + 5 def). Weekly Salary $349 (secondary $417). Owner: Minuto 92:48. Not fully flat yet, but close.

| Season | Salary | Change |
|---|---|---|
| 39–40 | $6,229 | flat |
| 41–55 | $10,307 → $19,613 (peak) | rising through prime |
| 56–72 | $17,480 → $384 | steady decelerating decline |
| 73 (current) | **$349** | **−9.11%** |

Decomposing out the ~8.4% deflation (same method as above): `(1 − 0.0911) / (1 − 0.084) − 1 ≈ −0.76%` implied skill-only change — his own decay has nearly flattened too, consistent with Sandoval's decomposed −7.2% and the general pattern of decay decelerating as a player's skills approach the floor.

## The finding: a season-73 game-wide change, not skill decay

Both players' skills are at the absolute minimum rating (1) and physically cannot decline further, yet **both** show an almost identical drop at season 73: Gintaras −8.41%, Costante −8.37%. Since neither player's skills changed, this cannot be skill-based decay — it pointed to a game-wide salary change applied at season 73, independent of any individual player's stats. This matches the general concept (though not the exact coefficients) in the bb-salary-calc spreadsheet's "Deflation" section (Normal1/Normal2/Monster1/Monster2 constants) — see `skill-curves-reference.md` in this same folder.

## Official explanation (per BB-Marin's season-73 patch notes, posted 2026-08-06)

BuzzerBeater shipped a **brand new salary formula at season 73**, replacing one that had accumulated 30 seasons of patches and become "impossible to tune." Key points from the official announcement:

- Measured against the old formula on identical players, the new formula lowers total salaries by **~2% on average**, and ~85% of teams pay less than before — **but this is not uniform.** It varies by skill, position, and salary tier, so don't treat our observed ~8.4% (from players with essentially zero skill) as representative of the whole population.
- **Shot Blocking was "very cheap" at every position under the old formula** — an exploit the new formula closes, pricing it up everywhere. **Inside Shot on guards was the other glaring case**, also repriced.
- **Centers as a group got slightly *more* expensive**; other positions got cheaper. Teams built around shot-blocking specialists now pay more, in proportion to how much they leaned on it.
- **Salary-tier dependent**: players earning **over $180k/week got more expensive**, everyone else got cheaper — an intentional design choice to level top-league vs. lower-division economics. Our reference-case players here are all under $400/wk, i.e. deep in the "got cheaper" end — don't extrapolate their ~8.4% to high earners.
- The initial rollout had a same-week bug (made Inside Shot *cheaper* for guards/SFs — backwards from intent — and didn't price Shot Blocking high enough for them either), caught by the community within 24 hours and fixed the next evening. Inside Shot for guards/SFs now sits slightly *above* the old formula's price.

This cleanly explains our floor-player result: with zero meaningful skills (including zero Shot Blocking), these three players mostly reflect whatever the new formula's base/floor component does at the very bottom of the salary range — not the SB/position/tier effects that matter for everyone else.

**Practical implication: don't expect this to recur next season by default.** This was a one-time structural break tied to an announced formula replacement, not a recurring periodic adjustment. Treat any *future* BB-Marin salary-formula announcement the same way — a new one-off event to recalibrate around — rather than assuming a fixed per-season deflation going forward.

**Timing note:** the buzzer-manager.com per-skill curves (`skill-curves-reference.md`, pulled "September 2026") and the Notion market regression (pulled 2026-09-11) were both pulled after this patch (and its next-day fix), so they should already reflect the *new* formula — no need to redo them on this account. The bb-salary-calc spreadsheet (dated 2011) reflects the *old*, now-replaced formula — a historical curiosity only, not even a rough approximation of current pricing.

### Cross-check against Sandoval Mustafa (48787579)

Sandoval (see `sandoval-48787579.md`, still actively declining, not at the floor) also dropped at season 73: −15.0%, larger than the two floor players' ~−8.4%. Decomposing his combined change assuming the same ~8.4% deflation applies to him too:

```
(1 + skill_only_change) × (1 − 0.084) = (1 − 0.150)
skill_only_change = 0.850 / 0.916 − 1 ≈ −7.2%
```

A −7.2% skill-only decline for Sandoval that season is consistent with the deceleration already observed in his prior seasons (−30.8% → this decomposed −7.2%), reinforcing the earlier read that his decline is flattening as his skills approach their own floors — the season-73 number looked steeper than it really was only because the game-wide deflation stacked on top of it.

## Implication for the model going forward

**Any comparison spanning season 73 must account for the formula replacement before attributing a change to skill decay — but season 73 is a one-time structural break, not an ongoing effect.** Season-to-season changes *within* the new formula (season 74 onward, until any future patch) should again be attributable to skill training/decay alone. Three independent players (two at the pure skill floor, one near it) all decomposed cleanly to a ~8.4% season-73 change plus a small, individually-plausible residual skill-only change, which is a nice sanity check that the decomposition method itself works — worth reusing if BB-Marin ever announces another formula change in the future.
