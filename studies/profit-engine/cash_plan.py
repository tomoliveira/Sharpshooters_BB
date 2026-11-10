"""Cash plan for one winning stint: how much it costs and how many seasons of saving it takes.

All inputs are copied from other studies (sources in the article); nothing is fetched.
Writes cash_plan.csv next to this script.
"""
import csv
from pathlib import Path

PAYDAYS = 13                       # season-structure.md: 13 Monday paydays per season
BREAK_EVEN = (178_000, 197_000)    # payroll-projection.md (PR #10): payroll Div III income carries, per payday
SAVE_PAYROLL = 109_000             # payroll-projection.md: projected payroll after recalculation
PROMOTION_BONUS = 750_000          # game-manual.md: one-time bonus for promoting into Div II
CASH_NOW = 283_141                 # docs/report.db, snapshot 2026-11-09 17:40, projection.current_cash
STINT_SEASONS = 2

TARGETS = {                        # salary-by-division.md, Brazil S73 human teams, weekly payroll
    "Div III league winner (median)": 245_000,
    "Div II p10 (survive)": 276_000,
    "Div II median (contend)": 388_000,
}
FLIP_INCOME = {                    # per season; flip_trend.json medians x flips
    "no flips": 0,
    "3 flips at 2024-26 median profit ($78k)": 3 * 78_000,
    "3 flips at 2021-23 median profit ($135k)": 3 * 135_000,
}

def season_surplus(payroll, be):  # positive = cash added per season
    return (be - payroll) * PAYDAYS

rows = []
for tname, tpay in TARGETS.items():
    for fname, flips in FLIP_INCOME.items():
        for be in BREAK_EVEN:
            save = season_surplus(SAVE_PAYROLL, be) + flips
            stint_cost = -season_surplus(tpay, be) * STINT_SEASONS - flips * STINT_SEASONS
            bonus = PROMOTION_BONUS if tname.startswith("Div II ") else 0  # paid on promotion into Div II
            need = max(stint_cost - bonus - CASH_NOW, 0)
            rows.append(dict(target=tname, target_payroll=tpay, flips=fname, break_even=be,
                             save_per_season=round(save), stint_cost_2_seasons=round(stint_cost),
                             promotion_bonus=bonus, cash_needed_after_bonus_and_cash_now=round(need),
                             seasons_of_saving=round(need / save, 2)))
out = Path(__file__).with_name("cash_plan.csv")
with open(out, "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
for r in rows:
    print(f"{r['target']:32} {r['flips']:42} be={r['break_even']:>7,} save={r['save_per_season']:>10,} "
          f"cost={r['stint_cost_2_seasons']:>10,} need={r['cash_needed_after_bonus_and_cash_now']:>10,} seasons={r['seasons_of_saving']}")
