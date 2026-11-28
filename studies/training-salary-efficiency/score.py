"""Score every documented training option by skill points gained per dollar of
future weekly salary, for the players currently on the Sharpshooters roster.

Inputs (all already in this repo, nothing is downloaded):
  - references/training_coefficients.md   weekly gain per skill, per training row
  - salary-model/skill-curves-reference.md salary at each rating 1-20, per skill
  - docs/report.db (table `state`)        latest roster XML from the BB API

Method: for each player a training row trains, the added salary of one week
is sum over touched skills of coef * (curve[r+1] - curve[r]) / curve[r] * the
player's current salary, where r is the player's current rating in that skill.
That is the skill's own marginal cost at the player's level, instead of the
flat 1->20 multiplier the report's "Minimize salary" mode uses.

Run from the repo root:  python studies/training-salary-efficiency/score.py
Writes studies/training-salary-efficiency/scores.csv and prints a summary.
"""

import csv
import re
import sqlite3
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent / "scores.csv"
MAX_AGE = 21  # the young training cohort; older players are listed but not ranked

# skill-curve row name / coefficient abbreviation -> roster XML tag
CURVE_NAMES = {
    "Jump Shot": "jumpShot", "Jump Range": "range", "Perimeter Def": "outsideDef",
    "Handling": "handling", "Driving": "driving", "Passing": "passing",
    "Inside Shot": "insideShot", "Inside Def": "insideDef", "Rebounding": "rebound",
    "Shot Blocking": "block",
}
ABBR = {
    "JS": "jumpShot", "JR": "range", "OD": "outsideDef", "Ha": "handling",
    "Dr": "driving", "Pa": "passing", "IS": "insideShot", "ID": "insideDef",
    "Rb": "rebound", "SB": "block",
}
ALL_POS = {"PG", "SG", "SF", "PF", "C"}


def load_curves():
    curves = {}
    text = (ROOT / "salary-model/skill-curves-reference.md").read_text()
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0] in CURVE_NAMES and len(cells) == 21:
            try:
                curves[CURVE_NAMES[cells[0]]] = [float(c) for c in cells[1:]]
            except ValueError:
                pass
    assert len(curves) == 10, f"expected 10 priced skills, got {sorted(curves)}"
    return curves


def load_training_rows():
    rows = []
    text = (ROOT / "references/training_coefficients.md").read_text()
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 6 or not re.match(r"^\d", cells[3]):
            continue
        ttype, combos, coefs = cells[0], cells[1], cells[2]
        coef = {}
        for m in re.finditer(r"([\d.]+)\s+([A-Za-z]{2})", coefs):
            coef[ABBR[m.group(2)]] = float(m.group(1))
        for combo in [c.strip() for c in combos.split(",")]:
            pos = ALL_POS if combo == "Team" else set(combo.split("/"))
            rows.append({"type": ttype, "combo": combo, "positions": pos, "coef": coef})
    # [Inference] estimates: training.aspx lists "C / PF (90%)" for One on One and
    # Jump Shot (references/training_dropdown_map.md), but the coefficient capture has
    # no C/PF row. Estimate it as 90% of the SF/PF row, and label it so.
    for r in list(rows):
        if r["type"] in ("One on One", "Jump Shot") and r["combo"] == "SF/PF":
            rows.append({"type": r["type"], "combo": "C/PF est.", "positions": {"C", "PF"},
                         "coef": {k: 0.9 * v for k, v in r["coef"].items()}})
    return rows


def load_roster():
    con = sqlite3.connect(ROOT / "docs/report.db")
    xml = con.execute("select roster_xml from state").fetchone()[0]
    root = ET.fromstring(xml)
    players = []
    for p in root.iter("player"):
        s = p.find("skills")
        players.append({
            "name": f"{p.findtext('firstName')} {p.findtext('lastName')}",
            "age": int(p.findtext("age")),
            "pos": p.findtext("bestPosition"),
            "salary": float(p.findtext("salary")),
            "skills": {e.tag: int(e.text) for e in s},
        })
    return root.find("roster").get("retrieved"), players


def marginal_rate(curve, rating):
    """Relative salary increase for +1 rating point from `rating` (1-20)."""
    r = max(1, min(rating, 19))
    return (curve[r] - curve[r - 1]) / curve[r - 1]


def main():
    curves = load_curves()
    rows = load_training_rows()
    retrieved, players = load_roster()
    cohort = [p for p in players if p["age"] <= MAX_AGE]

    results = []
    for row in rows:
        trained = [p for p in cohort if p["pos"] in row["positions"]]
        pts = 0.0
        dollars = 0.0
        for p in trained:
            for skill, c in row["coef"].items():
                pts += c
                dollars += c * marginal_rate(curves[skill], p["skills"][skill]) * p["salary"]
        results.append({
            "training": row["type"], "combo": row["combo"],
            "players_trained": len(trained),
            "points_per_week": round(pts, 3),
            "salary_added_per_week": round(dollars, 2),
            "points_per_100_dollars": round(100 * pts / dollars, 2) if dollars else "",
            "trained": "; ".join(p["name"] for p in trained),
        })

    results.sort(key=lambda r: -(r["points_per_100_dollars"] or 0))
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(results[0]))
        w.writeheader()
        w.writerows(results)

    print(f"Roster retrieved {retrieved}; cohort = age <= {MAX_AGE}: {len(cohort)} players")
    for p in cohort:
        print(f"  {p['name']:<28} {p['age']} {p['pos']:<2} ${p['salary']:>7,.0f}")
    print(f"\n{'training':<24}{'combo':<10}{'n':>3}{'pts/wk':>8}{'$ added/wk':>12}{'pts/$100':>10}")
    for r in results:
        if r["players_trained"]:
            print(f"{r['training']:<24}{r['combo']:<10}{r['players_trained']:>3}"
                  f"{r['points_per_week']:>8.2f}{r['salary_added_per_week']:>12.2f}"
                  f"{r['points_per_100_dollars']:>10}")
    print(f"\nWrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
