"""Test the buzzer-manager.com calculator curves against the 266 real salaries.

Model: ln(salary) = a + sum_i beta_i * f_i(skill_i), where f_i(s) = ln(calc_i(s) / 17609)
is the calculator's own curve for skill i (skill-curves-reference.md). If the calculator
is the game's formula, every beta_i is ~1. beta_i > 1 means the market (the real
post-S73 salaries) prices that skill more steeply than the calculator does.
Ratings above 20 are extrapolated at each curve's 19->20 log rate.
Run: python3 salary-model/analysis/calculator_vs_market.py
"""
import math, re, pathlib
import numpy as np, pandas as pd

ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = 17609
ref = (ROOT / "skill-curves-reference.md").read_text()
curves = {}
for line in ref.splitlines():
    cells = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(cells) == 21 and all(re.fullmatch(r"\d+", c) for c in cells[1:]):
        curves[cells[0]] = [int(c) for c in cells[1:]]
curves["Outside Def"] = curves.pop("Perimeter Def")  # same skill, CSV name
SK = ["Jump Shot", "Jump Range", "Outside Def", "Handling", "Driving", "Passing",
      "Inside Shot", "Inside Def", "Rebounding", "Shot Blocking"]  # ST/FT are flat

def f(skill, s):
    c = curves[skill]
    s = max(1, int(s))
    if s <= 20:
        return math.log(c[s - 1] / BASE)
    return math.log(c[19] / BASE) + (s - 20) * math.log(c[19] / c[18])

d = pd.read_csv(ROOT / "players.csv")
y = np.log(d["Weekly Salary"].values)
F = np.column_stack([[f(k, v) for v in d[k]] for k in SK])

def ols(X, y):
    X1 = np.column_stack([np.ones(len(y)), X])
    b, *_ = np.linalg.lstsq(X1, y, rcond=None)
    r = y - X1 @ b
    s2 = r @ r / (len(y) - X1.shape[1])
    se = np.sqrt(np.diag(s2 * np.linalg.inv(X1.T @ X1)))
    r2 = 1 - (r @ r) / ((y - y.mean()) @ (y - y.mean()))
    return b, se, r2

# 1. Calculator taken literally: predicted = 17609 * prod(calc_i / 17609)
pred = np.log(BASE) + F.sum(axis=1)
resid = y - pred
r2_lit = 1 - (resid @ resid) / ((y - y.mean()) @ (y - y.mean()))
print(f"Calculator taken literally: R2 = {r2_lit:.3f}, median actual/predicted = {np.exp(np.median(resid)):.2f}")
for pos in ["PG", "SG", "SF", "PF", "C"]:
    m = (d["Position"] == pos).values
    print(f"  {pos}: n={m.sum():3d}  median actual/predicted = {np.exp(np.median(resid[m])):.2f}")
hi = d["Weekly Salary"].values > 180000
print(f"  >$180k: n={hi.sum()}  median actual/predicted = {np.exp(np.median(resid[hi])):.2f}")
print(f"  <=$180k: n={(~hi).sum()}  median actual/predicted = {np.exp(np.median(resid[~hi])):.2f}")

# 2. Calibration: one beta per skill, pooled
b, se, r2 = ols(F, y)
print(f"\nPooled calibration (n={len(y)}, R2={r2:.3f}); beta=1 means the calculator is right")
print(f"{'Skill':<14}{'beta':>7}{'se':>7}{'calc 1->20':>11}{'market 1->20':>13}")
for k, bi, si in zip(SK, b[1:], se[1:]):
    span = math.log(curves[k][19] / curves[k][0])
    print(f"{k:<14}{bi:7.2f}{si:7.2f}{math.exp(span):10.2f}x{math.exp(bi * span):12.2f}x")

# 3. Shot Blocking by position group, others pooled
print("\nShot Blocking beta by position group (other skills share pooled betas)")
sb = SK.index("Shot Blocking")
groups = {"Guards (PG/SG)": ["PG", "SG"], "SF": ["SF"], "Bigs (PF/C)": ["PF", "C"]}
cols = [F[:, i] for i in range(len(SK)) if i != sb]
masks = {g: d["Position"].isin(p).values for g, p in groups.items()}
for g, m in masks.items():
    cols.append(F[:, sb] * m)
b, se, r2 = ols(np.column_stack(cols), y)
for (g, m), bi, si in zip(masks.items(), b[-3:], se[-3:]):
    sbv = d.loc[m, "Shot Blocking"]
    span = math.log(curves["Shot Blocking"][19] / curves["Shot Blocking"][0])
    print(f"  {g:<15} n={m.sum():3d}  SB mean={sbv.mean():4.1f} range {sbv.min()}-{sbv.max()}  beta={bi:.2f} (se {si:.2f})  market 1->20 = {math.exp(bi*span):.2f}x")
print(f"  R2={r2:.3f}")

# 4. Robustness: position intercepts, and bootstrap 90% intervals for each skill's market 1->20
print("\nWith position intercepts (C is baseline) + bootstrap 90% intervals, 2000 resamples")
P = pd.get_dummies(d["Position"])[["PG", "SG", "SF", "PF"]].values.astype(float)
X = np.column_stack([F, P])
b, se, r2 = ols(X, y)
rng = np.random.default_rng(73)
boot = []
for _ in range(2000):
    i = rng.integers(0, len(y), len(y))
    boot.append(ols(X[i], y[i])[0])
boot = np.array(boot)
print(f"R2={r2:.3f}")
for j, k in enumerate(SK):
    span = math.log(curves[k][19] / curves[k][0])
    lo, hi_ = np.percentile(boot[:, j + 1], [5, 95])
    print(f"  {k:<14} beta={b[j+1]:5.2f}  market 1->20 = {math.exp(b[j+1]*span):5.2f}x  (90% {math.exp(lo*span):.2f}x-{math.exp(hi_*span):.2f}x)  calc {math.exp(span):.2f}x")
for j, p in enumerate(["PG", "SG", "SF", "PF"]):
    print(f"  {p} vs C salary at same skills: {math.exp(b[len(SK)+1+j]):.2f}x")
big = d["Position"].isin(["PF", "C"])
print("\nCorrelation of Shot Blocking with other big-man skills, PF/C only:")
print(d.loc[big, ["Shot Blocking", "Inside Def", "Rebounding", "Inside Shot"]].corr().round(2).iloc[0].to_dict())
