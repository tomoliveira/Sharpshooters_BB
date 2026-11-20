"""Tom's income target (2026-11-10): weekly income >= league minimum payroll + expenses + $100k.

Minimum payroll = a % of the league's TV money (game-manual.md). Income and expenses are the
last-8-payday averages from the payroll-projection ledger (PR #10). Nothing is fetched.
Writes income_target.csv next to this script.
"""
import csv
from pathlib import Path

TV, MERCH, GATE = 84_021, 31_712, 130_285      # Div III, per payday, 2026-09-21..2026-11-09
EXPENSES = 38_890 + 10_000                     # staff + scouting, per payday
MARGIN = 100_000                               # Tom's target margin
FLOOR = {"III": 1.30, "II (manual summary)": 1.87, "II (arena handoff)": 1.90,
         "I (manual summary)": 2.415}
income = TV + MERCH + GATE
rows = []
for div, pct in FLOOR.items():
    # Scale every income category by m (Tom: all are higher in upper leagues); expenses flat.
    # Target holds when m*income >= pct*m*TV + EXPENSES + MARGIN.
    m_needed = (EXPENSES + MARGIN) / (income - pct * TV)
    target_at_div3_tv = pct * TV + EXPENSES + MARGIN
    rows.append(dict(division=div, floor_pct_of_tv=pct,
                     target_income_if_tv_unchanged=round(target_at_div3_tv),
                     gap_vs_current_income=round(income - target_at_div3_tv),
                     income_multiple_needed_vs_div3=round(m_needed, 2)))
out = Path(__file__).with_name("income_target.csv")
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print(f"current income per payday: {income:,}; expenses {EXPENSES:,}")
for r in rows: print(r)
