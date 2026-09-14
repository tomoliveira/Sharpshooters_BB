# Reference cases: salary floor + season-73 game-wide deflation

Added 2026-09-14. Two independent players with every skill at the absolute minimum (1 = atrocious, except Free Throw which is a confirmed zero-effect skill) — skills that literally cannot decay any further, at ages 94 and 85.

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

## The finding: a season-73 game-wide deflation, not skill decay

Both players' skills are at the absolute minimum rating (1) and physically cannot decline further, yet **both** show an almost identical drop at season 73: Gintaras −8.41%, Costante −8.37%. Since neither player's skills changed, this cannot be skill-based decay — it points to a **periodic, game-wide salary deflation** applied at season 73, independent of any individual player's stats. This matches the general concept (though not necessarily the exact coefficients) in the bb-salary-calc spreadsheet's "Deflation" section (Normal1/Normal2/Monster1/Monster2 constants) — see `skill-curves-reference.md` in this same folder.

### Cross-check against Sandoval Mustafa (48787579)

Sandoval (see `sandoval-48787579.md`, still actively declining, not at the floor) also dropped at season 73: −15.0%, larger than the two floor players' ~−8.4%. Decomposing his combined change assuming the same ~8.4% deflation applies to him too:

```
(1 + skill_only_change) × (1 − 0.084) = (1 − 0.150)
skill_only_change = 0.850 / 0.916 − 1 ≈ −7.2%
```

A −7.2% skill-only decline for Sandoval that season is consistent with the deceleration already observed in his prior seasons (−30.8% → this decomposed −7.2%), reinforcing the earlier read that his decline is flattening as his skills approach their own floors — the season-73 number looked steeper than it really was only because the game-wide deflation stacked on top of it.

## Implication for the model going forward

**Any season-over-season salary comparison must account for this deflation before attributing a change to skill decay.** A single confirmed data point (season 73, ~−8.4%) isn't enough to know if this is a one-off adjustment, a recurring per-season deflation, or tied to some other game event — flag this as an open question and watch for it recurring in future season-history pulls. If it recurs with a different magnitude each time, the deflation coefficient itself would need to be estimated per season rather than assumed constant.
