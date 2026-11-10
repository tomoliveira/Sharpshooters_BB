"""List every weekly-salary change for our own players across the daily snapshots.

Salaries are recalculated once per season, so a change that hits most of the roster on
the same day marks the season rollover. Season 74 is expected to bring back the
Season-72 salary formula (see calculator-vs-market.md), so the rollover is a clean
test: same players, near-identical skills, new formula.
Run: python3 salary-model/analysis/salary_rollover.py
"""
import json, sqlite3, pathlib, collections

DB = pathlib.Path(__file__).resolve().parents[2] / "docs" / "report.db"
rows = sqlite3.connect(DB).execute(
    "select fetched_at, data_json from snapshots order by fetched_at").fetchall()

seen = collections.defaultdict(list)  # playerid -> [(date, salary, name)]
for fetched, blob in rows:
    for p in json.loads(blob).get("minutes_vs_money") or []:
        seen[p["playerid"]].append((fetched[:16], int(float(p["salary"])), p["name"]))

print(f"{len(rows)} snapshots, {rows[0][0][:10]} to {rows[-1][0][:10]}")
changes = 0
for pid, s in seen.items():
    for (t0, a, _), (t1, b, name) in zip(s, s[1:]):
        if a != b:
            changes += 1
            print(f"{name:<24} {t0} ${a:>7,} -> {t1} ${b:>7,}  {b / a - 1:+.1%}")
print(f"{changes} salary changes across {len(seen)} players")
