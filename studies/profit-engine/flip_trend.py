"""Mloty Stargard teenage flips: trend by year, timing within the season, price by potential.

Reads top-teams-research/mloty_stargard_teen_flips.csv and data/seasons.csv (no network).
Writes flip_trend.json next to this script.
"""
import csv, json, statistics as st, datetime as dt
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TT = ROOT / "top-teams-research"
rows = list(csv.DictReader(open(TT / "mloty_stargard_teen_flips.csv", encoding="utf-8")))
starts = sorted((dt.datetime.fromisoformat(r[1][:19]), int(r[0]))
                for r in csv.reader(open(TT / "data" / "seasons.csv")) if r[0].isdigit() and r[1])

def f(x, k): return float(x[k])
def season_day(d):
    s = max(t for t in starts if t[0] <= d); return (d - s[0]).days

out = {"by_year": {}, "by_potential": {}, "by_period": {}}
by = defaultdict(list)
for x in rows: by[x["Bought on"][:4]].append(x)
for y in sorted(by):
    L = by[y]
    out["by_year"][y] = dict(n=len(L), median_buy=st.median(f(x, "Buy price ($)") for x in L),
        median_sale=st.median(f(x, "Sale price ($)") for x in L),
        median_profit=st.median(f(x, "Profit ($)") for x in L),
        total_profit=sum(f(x, "Profit ($)") for x in L),
        median_days=st.median(f(x, "Days held") for x in L))
periods = {"2017-2020": ("2017", "2020"), "2021-2023": ("2021", "2023"), "2024-2026": ("2024", "2026")}
for name, (a, b) in periods.items():
    L = [x for x in rows if a <= x["Bought on"][:4] <= b]
    yrs = int(b) - int(a) + 1
    out["by_period"][name] = dict(n=len(L), flips_per_year=round(len(L) / yrs, 1),
        median_buy=st.median(f(x, "Buy price ($)") for x in L),
        median_sale=st.median(f(x, "Sale price ($)") for x in L),
        median_profit=st.median(f(x, "Profit ($)") for x in L),
        profit_per_year=round(sum(f(x, "Profit ($)") for x in L) / yrs))
pot = defaultdict(list)
for x in rows: pot[x["Potential"]].append(x)
for p, L in pot.items():
    out["by_potential"][p] = dict(n=len(L), median_buy=st.median(f(x, "Buy price ($)") for x in L),
        median_sale=st.median(f(x, "Sale price ($)") for x in L))
buy_days = [season_day(dt.datetime.fromisoformat(x["Bought on"])) for x in rows]
sell_days = [season_day(dt.datetime.fromisoformat(x["Sold on"])) for x in rows]
out["timing"] = dict(
    median_buy_day_of_season=st.median(buy_days),
    share_bought_in_first_14_days=round(sum(d < 14 for d in buy_days) / len(buy_days), 3),
    median_sell_day_of_season=st.median(sell_days),
    sell_day_quartiles=st.quantiles(sell_days, n=4))
# season length, to date the next season start
lens = [(starts[i + 1][0] - starts[i][0]).days for i in range(len(starts) - 1)][-8:]
out["recent_season_length_days"] = lens
out["next_season_start_estimate"] = (starts[-1][0] + dt.timedelta(days=st.median(lens))).date().isoformat()
json.dump(out, open(Path(__file__).with_name("flip_trend.json"), "w"), indent=2)
print(json.dumps(out, indent=2))
