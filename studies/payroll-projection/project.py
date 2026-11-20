"""Project Sharpshooters' weekly payroll after the next season-start salary
recalculation, and compare it with Division II payrolls and the manual's
minimum-payroll rule.

Inputs (all in this repo):
  salary-model/players.csv          266 transfer-list players with skills + salary
  docs/report.db  state.roster_xml  our current roster (API XML)
  docs/report.db  snapshots         weekly economy ledger (playerSalaries, tvMoney)
  studies/salary-by-division/teams.csv  Brazil Div I-III payrolls, season 73

Model: log(salary) = a + sum(b_i * skill_i) over the 10 skills that price
(Stamina and Free Throw excluded; Age excluded, see salary-model/formula-history.md).
Ordinary least squares, numpy only.
"""
import csv, json, math, sqlite3, statistics, sys
import xml.etree.ElementTree as ET
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SK_CSV = ["Jump Shot", "Jump Range", "Outside Def", "Handling", "Driving",
          "Passing", "Inside Shot", "Inside Def", "Rebounding", "Shot Blocking"]
SK_XML = ["jumpShot", "range", "outsideDef", "handling", "driving",
          "passing", "insideShot", "insideDef", "rebound", "block"]

def fit():
    X, y = [], []
    for r in csv.DictReader(open(ROOT / "salary-model/players.csv", encoding="utf-8")):
        try:
            X.append([1.0] + [float(r[s]) for s in SK_CSV]); y.append(math.log(float(r["Weekly Salary"])))
        except (ValueError, KeyError):
            continue
    X, y = np.array(X), np.array(y)
    b, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ b
    r2 = 1 - (res ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return b, r2, float(res.std(ddof=X.shape[1])), len(y)

def roster():
    db = sqlite3.connect(ROOT / "docs/report.db")
    xml = db.execute("select roster_xml from state").fetchone()[0]
    root = ET.fromstring(xml)
    retrieved = root.find("roster").get("retrieved")
    out = []
    for p in root.iter("player"):
        s = p.find("skills")
        out.append({
            "name": f'{p.findtext("firstName")} {p.findtext("lastName")}',
            "id": p.get("id"), "age": int(p.findtext("age")),
            "salary": int(p.findtext("salary")),
            "skills": [int(s.findtext(k)) for k in SK_XML],
        })
    return retrieved, out

def ledger():
    db = sqlite3.connect(ROOT / "docs/report.db")
    seen = {}
    for (dj,) in db.execute("select data_json from snapshots order by fetched_at"):
        for t in (json.loads(dj).get("economy") or {}).get("transactions", []):
            if t["tag"] in ("playerSalaries", "tvMoney"):
                seen[(t["date"][:10], t["tag"])] = t["amount"]
    days = sorted({d for d, _ in seen})
    return [(d, -seen.get((d, "playerSalaries"), 0), seen.get((d, "tvMoney"))) for d in days]

def capacity():
    """Payroll the current Division III income could carry, from the ledger.

    Season view: all dated transactions since the first payday on record
    (2026-08-17); income = TV + merchandise + gate; fixed costs = staff + scouting.
    Run-rate view: the last 8 weeks (from 2026-09-21), after newbie income ended.
    """
    db = sqlite3.connect(ROOT / "docs/report.db")
    seen = {}
    for (dj,) in db.execute("select data_json from snapshots order by fetched_at"):
        for t in (json.loads(dj).get("economy") or {}).get("transactions", []):
            seen[(t["date"], t["tag"], t["amount"])] = True
    def tot(since):
        out = {}
        for d, tag, a in seen:
            if d >= since:
                out[tag] = out.get(tag, 0) + a
        return out
    season = tot("2026-08-10")
    paydays = sum(1 for d, tag, _ in seen if tag == "tvMoney" and d >= "2026-08-10")
    inc = season.get("tvMoney", 0) + season.get("merchandise", 0) + season.get("matchRevenue", 0)
    fixed = -(season.get("staffSalaries", 0) + season.get("scouting", 0))
    rs = -season.get("revenueSharing", 0)
    recent = tot("2026-09-21")
    weeks = 8
    run = {k: recent.get(k, 0) / weeks for k in ("tvMoney", "merchandise", "matchRevenue", "staffSalaries", "scouting")}
    return {
        "season_paydays_on_record": paydays,
        "season_totals": {k: round(v) for k, v in sorted(season.items())},
        "season_breakeven_payroll": round((inc - fixed) / paydays),
        "season_breakeven_after_revenue_sharing": round((inc - fixed - rs) / paydays),
        "run_rate_weeks": weeks,
        "run_rate": {k: round(v) for k, v in run.items()},
        "run_rate_breakeven_payroll": round(sum(run.values())),
    }

def div_payrolls(level):
    return sorted(int(r["payroll"]) for r in csv.DictReader(open(ROOT / "studies/salary-by-division/teams.csv"))
                  if r["level"] == str(level) and r["is_bot"] == "0" and int(r["n_players"]) >= 5)

def main():
    b, r2, sd, n = fit()
    retrieved, players = roster()
    rows = []
    for p in players:
        pred = math.exp(b[0] + sum(c * v for c, v in zip(b[1:], p["skills"])))
        rows.append({**p, "pred": pred})
    rows.sort(key=lambda r: -r["pred"])
    cur = sum(r["salary"] for r in rows)
    proj = sum(r["pred"] for r in rows)
    # Interval: scale whole-roster projection by exp(+-1 residual SD) - correlated-error worst case
    lo, hi = proj * math.exp(-sd), proj * math.exp(sd)
    d2 = div_payrolls(2); d3 = div_payrolls(3)
    lad = json.load(open(ROOT / "studies/salary-by-division/summary.json"))["levels"]["2"]["payroll"]
    pct = lambda xs, v: 100 * sum(x <= v for x in xs) / len(xs)
    out = {
        "model": {"n": n, "r2": round(r2, 3), "resid_sd_log": round(sd, 3),
                  "coef": dict(zip(["intercept"] + SK_CSV, [round(float(x), 4) for x in b]))},
        "roster_retrieved": retrieved,
        "current_payroll": cur, "projected_payroll": round(proj), "projected_band": [round(lo), round(hi)],
        "players": [{"name": r["name"], "age": r["age"], "salary": r["salary"], "projected": round(r["pred"])} for r in rows],
        "ledger": [{"payday": d, "player_salaries": ps, "tv_money": tv,
                    "salaries_over_tv": round(ps / tv, 3) if tv else None} for d, ps, tv in ledger()],
        "div2": {"n": len(d2), "min": lad["min"], "p10": lad["p10"], "median": lad["median"],
                 "gap_to_p10": round(lad["p10"] - proj),
                 "projected_percentile": round(pct(d2, proj), 1)},
        "capacity": capacity(),
        "div3_projected_percentile": round(pct(d3, proj), 1),
    }
    json.dump(out, sys.stdout, indent=1, ensure_ascii=False)

if __name__ == "__main__":
    main()
