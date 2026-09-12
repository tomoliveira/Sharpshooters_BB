"""
Analysis of the 336-team Brazil league dataset (Liga Nacional + Div II + Div III),
scraped from public buzzerbeater.com pages. Two purposes:

1. Test whether arena fill rate is related to team performance (win%, point diff),
   as opposed to being purely a price/demand signal -- per Tom's note that fill
   and price elasticity are likely confounded with how well a team is doing.
2. Build a same-division (Division III) benchmark for Sharpshooters, which is a
   much closer comp than the earlier 64-team top-division "BuzzerBeater's Best" set.

Read-only analysis. Nothing submitted to buzzerbeater.com.
"""

import csv
import statistics as stats
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "brazil_leagues_all.csv"


def load():
    rows = []
    with open(DATA, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            row["division"] = (
                "Liga Nacional" if row["league"] == "Liga Nacional"
                else "II" if row["league"].startswith("II.")
                else "III"
            )
            for k in ("bleachers_capacity", "bleachers_price", "lower_tier_capacity", "lower_tier_price",
                       "courtside_capacity", "courtside_price", "luxury_capacity", "luxury_price",
                       "total_capacity", "avg_est_revenue_per_game", "avg_fill_pct", "W", "L", "PF", "PA",
                       "point_diff"):
                row[k] = int(row[k])
            row["win_pct"] = float(row["win_pct"])
            rows.append(row)
    return rows


def pearson(xs, ys):
    n = len(xs)
    mx, my = stats.mean(xs), stats.mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sx = (sum((x - mx) ** 2 for x in xs)) ** 0.5
    sy = (sum((y - my) ** 2 for y in ys)) ** 0.5
    if sx == 0 or sy == 0:
        return 0.0
    return cov / (sx * sy)


def main():
    rows = load()
    print(f"Loaded {len(rows)} teams across Liga Nacional / Div II / Div III (Brazil)\n")

    # ------------------------------------------------------------------
    # 1. Performance vs fill rate
    # ------------------------------------------------------------------
    print("=" * 78)
    print("PERFORMANCE vs ARENA FILL RATE")
    print("=" * 78)

    win = [r["win_pct"] for r in rows]
    fill = [r["avg_fill_pct"] for r in rows]
    pd_ = [r["point_diff"] for r in rows]
    r_win_fill = pearson(win, fill)
    r_pd_fill = pearson(pd_, fill)
    print(f"All 336 teams: corr(win_pct, fill%) = {r_win_fill:+.3f}   corr(point_diff, fill%) = {r_pd_fill:+.3f}")

    for div in ("Liga Nacional", "II", "III"):
        sub = [r for r in rows if r["division"] == div]
        w = [r["win_pct"] for r in sub]
        f = [r["avg_fill_pct"] for r in sub]
        p = [r["point_diff"] for r in sub]
        print(f"  {div:14s} (n={len(sub):3d}): corr(win_pct, fill%) = {pearson(w, f):+.3f}   "
              f"corr(point_diff, fill%) = {pearson(p, f):+.3f}   mean fill = {stats.mean(f):.1f}%")

    # bucket comparison: winning vs losing teams, mean fill
    winners = [r["avg_fill_pct"] for r in rows if r["win_pct"] >= 0.6]
    losers = [r["avg_fill_pct"] for r in rows if r["win_pct"] <= 0.4]
    print(f"\n  Teams with win_pct >= 0.6 (n={len(winners)}): mean fill = {stats.mean(winners):.1f}%")
    print(f"  Teams with win_pct <= 0.4 (n={len(losers)}): mean fill = {stats.mean(losers):.1f}%")
    print(f"  -> gap = {stats.mean(winners) - stats.mean(losers):+.1f} percentage points of fill,"
          f" independent of price (this is a same-snapshot comparison, not causal, but the gap")
    print(f"     is exactly the kind of performance confound Tom flagged -- a fill swing could be")
    print(f"     forma/standings, not price sensitivity.")

    # ------------------------------------------------------------------
    # 2. Price vs fill, controlling loosely for performance tercile
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("BLEACHERS PRICE vs FILL, SPLIT BY PERFORMANCE (Division III only, n=" +
          str(len([r for r in rows if r['division'] == 'III'])) + ")")
    print("=" * 78)
    d3 = [r for r in rows if r["division"] == "III"]
    d3_sorted_perf = sorted(d3, key=lambda r: -r["win_pct"])
    third = len(d3_sorted_perf) // 3
    top_perf = d3_sorted_perf[:third]
    bot_perf = d3_sorted_perf[-third:]
    for label, group in (("Top third by win%", top_perf), ("Bottom third by win%", bot_perf)):
        bp = [r["bleachers_price"] for r in group]
        bf = [r["avg_fill_pct"] for r in group]
        print(f"  {label:22s} (n={len(group)}): corr(bleachers_price, fill%) = {pearson(bp, bf):+.3f}  "
              f"mean price ${stats.mean(bp):.1f}  mean fill {stats.mean(bf):.1f}%")

    # ------------------------------------------------------------------
    # 3. Division III benchmark (Sharpshooters' real peer group)
    # ------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("DIVISION III BENCHMARK (Sharpshooters' actual peer group, n=" + str(len(d3)) + ")")
    print("=" * 78)
    for tier in ("bleachers", "lower_tier", "courtside", "luxury"):
        prices = sorted(r[f"{tier}_price"] for r in d3)
        print(f"  {tier:12s} price: min ${prices[0]}  median ${stats.median(prices):.0f}  "
              f"mean ${stats.mean(prices):.1f}  max ${prices[-1]}")
    revs = [r["avg_est_revenue_per_game"] for r in d3]
    fills = [r["avg_fill_pct"] for r in d3]
    caps = [r["total_capacity"] for r in d3]
    print(f"  {'total_capacity':12s}: min {min(caps)}  median {stats.median(caps):.0f}  "
          f"mean {stats.mean(caps):.0f}  max {max(caps)}")
    print(f"  {'revenue/game':12s}: median ${stats.median(revs):,.0f}  mean ${stats.mean(revs):,.0f}")
    print(f"  {'fill%':12s}: median {stats.median(fills):.0f}%  mean {stats.mean(fills):.1f}%")

    sh = next(r for r in rows if r["team_id"] == "32988")
    print(f"\n  Sharpshooters: win_pct={sh['win_pct']:.3f} (rank context: {sh['W']}-{sh['L']}), "
          f"revenue/game ${sh['avg_est_revenue_per_game']:,d}, fill {sh['avg_fill_pct']}%")
    print(f"  Sharpshooters win_pct percentile within Div III: "
          f"{100*sum(1 for r in d3 if r['win_pct'] < sh['win_pct'])/len(d3):.0f}th")
    print(f"  Sharpshooters revenue/game percentile within Div III: "
          f"{100*sum(1 for r in d3 if r['avg_est_revenue_per_game'] < sh['avg_est_revenue_per_game'])/len(d3):.0f}th")

    # best Div III models: high revenue AND high fill
    good_models = [r for r in d3 if r["avg_fill_pct"] >= 85]
    good_models.sort(key=lambda r: -r["avg_est_revenue_per_game"])
    print("\n  Best Division III models (fill >= 85%), by revenue/game:")
    for r in good_models[:8]:
        print(f"    {r['team_name']:28s} ({r['league']})  ${r['avg_est_revenue_per_game']:>7,d}/game  "
              f"{r['avg_fill_pct']:>3d}% fill  {r['win_pct']:.3f} win%  cap {r['total_capacity']:,d}")


if __name__ == "__main__":
    main()
