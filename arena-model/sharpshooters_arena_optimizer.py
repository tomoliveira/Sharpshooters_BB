"""
Sharpshooters (team #32988, League III.15) arena pricing/expansion optimizer.

READ-ONLY / ANALYSIS ONLY. This script never touches buzzerbeater.com and never
submits anything. It only prints ranked recommendations for Tom to review and,
if he chooses, apply by hand on the site.

Data sources:
  - Sharpshooters' current arena state, price bounds, expansion costs and recent
    attendance: transcribed by hand from buzzerbeater.com/team/32988/arena.aspx
    (see sharpshooters_arena_optimizer_handoff.md, fetched 2026-09-11).
  - Benchmark set: bb_best_bracket_arenas.csv, 64 top-division "BuzzerBeater's
    Best" teams (Season 72 B3 knockout draw). Revenue/fill in that file are each
    team's own estimates (last ~5 games x current price), not official BB figures.

Everything below marked [ESTIMATE] or [INFERENCE] is a model output or a
judgment call, not a guaranteed outcome. Division III demand is almost
certainly less price-tolerant than this top-division benchmark set, so
benchmark comparisons are used only as *direction*, not as a target to match.
"""

import csv
import statistics as stats
from pathlib import Path

HERE = Path(__file__).parent
BENCHMARK_CSV = HERE / "bb_best_bracket_arenas.csv"

# ---------------------------------------------------------------------------
# 1. Sharpshooters' current state (hand-transcribed, see handoff doc)
# ---------------------------------------------------------------------------

TIERS = ["bleachers", "lower_tier", "courtside", "luxury"]

CURRENT = {
    "bleachers":  {"capacity": 6020, "price": 12,  "min": 5,  "max": 20,   "expand_cost": 200},
    "lower_tier": {"capacity": 560,  "price": 44,  "min": 18, "max": 70,   "expand_cost": 700},
    "courtside":  {"capacity": 108,  "price": 119, "min": 50, "max": 200,  "expand_cost": 2000},
    "luxury":     {"capacity": 8,    "price": 892, "min": 400,"max": 1600, "expand_cost": 16000},
}

# Recent attendance rows (date, bleachers, lower_tier, courtside, luxury).
# NOTE per handoff: Lower Tier/Courtside/Luxury capacity was expanded partway
# through this log (Lower Tier 500->560, Courtside 60->108, Luxury 2->8).
# Only the most recent row (9/8) was played at *today's* full capacity for
# those three tiers -- older rows are near-100% fill against a smaller arena
# that no longer exists and are NOT comparable fill-rate evidence for the
# current capacity. Bleachers capacity did not change, so all 5 rows are
# valid fill evidence for that tier.
ATTENDANCE_LOG = [
    # date, bleachers, lower_tier, courtside, luxury, note
    ("9/8",  5333, 542, 108, 5, "current capacity"),
    ("9/1",  3731, 500, 60,  2, "pre-expansion LT/CS/LX capacity"),
    ("8/25", 5438, 500, 60,  2, "pre-expansion LT/CS/LX capacity"),
    ("8/20", 5438, 500, 60,  2, "pre-expansion LT/CS/LX capacity (Cup)"),
    ("8/15", 4769, 500, 60,  2, "pre-expansion LT/CS/LX capacity"),
]

SEASON_TICKET_HOLDERS = 1125


def current_fill_rates():
    """Fill % per tier, using only rows valid for TODAY's capacity."""
    fills = {t: [] for t in TIERS}
    for date, b, lt, cs, lx, note in ATTENDANCE_LOG:
        fills["bleachers"].append(b / CURRENT["bleachers"]["capacity"])
        if note == "current capacity":
            fills["lower_tier"].append(lt / CURRENT["lower_tier"]["capacity"])
            fills["courtside"].append(cs / CURRENT["courtside"]["capacity"])
            fills["luxury"].append(lx / CURRENT["luxury"]["capacity"])
    return {
        t: {
            "mean_fill": stats.mean(v) if v else None,
            "n_games": len(v),
            "latest_fill": v[-1] if t == "bleachers" else (v[0] if v else None),
        }
        for t, v in fills.items()
    }


# ---------------------------------------------------------------------------
# 2. Benchmark set
# ---------------------------------------------------------------------------

def load_benchmark():
    rows = []
    with open(BENCHMARK_CSV, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if not row.get("team_id"):
                continue
            rows.append({
                "team_name": row["team_name"],
                "bleachers_price": int(row["bleachers_price"]),
                "lower_tier_price": int(row["lower_tier_price"]),
                "courtside_price": int(row["courtside_price"]),
                "luxury_price": int(row["luxury_price"]),
                "total_capacity": int(row["total_capacity"]),
                "avg_est_revenue_per_game": int(row["avg_est_revenue_per_game"]),
                "avg_fill_pct": int(row["avg_fill_pct"]),
            })
    return rows


def benchmark_summary(rows):
    out = {}
    for tier in TIERS:
        key = f"{tier}_price"
        vals = sorted(r[key] for r in rows)
        out[tier] = {
            "min": vals[0], "max": vals[-1],
            "mean": stats.mean(vals), "median": stats.median(vals),
        }
    return out


def percentile_rank(value, sorted_vals):
    below = sum(1 for v in sorted_vals if v < value)
    return round(100 * below / len(sorted_vals), 1)


# ---------------------------------------------------------------------------
# 3. Price-change scenarios (no capacity change)
#
# Two demand regimes, applied per tier based on observed current-capacity fill:
#   - SOLD OUT (fill >= ~98%, courtside here): demand exceeds supply at the
#     current price. A price increase is modeled as pure revenue gain at the
#     SAME attendance (capacity-constrained), until/unless it's raised so far
#     it no longer clears -- we cap the "safe" step at a conservative +25%
#     rather than jumping straight to the benchmark average, because we have
#     zero evidence of where Division III demand actually breaks.
#   - NOT SOLD OUT (bleachers, lower tier, luxury): apply a conservative
#     elasticity assumption (-0.4, i.e. a 10% price rise costs ~4% of fill).
#     This is a standard rough services elasticity, NOT fitted from this
#     data -- flagged as an assumption. Luxury gets a wider fill floor because
#     it just quadrupled in capacity and only has 1 data point.
# ---------------------------------------------------------------------------

ELASTICITY = -0.4  # assumed, not fitted -- see note above

def revenue_at_price(tier, new_price, fill_info):
    cap = CURRENT[tier]["capacity"]
    cur_price = CURRENT[tier]["price"]
    fill = fill_info[tier]["mean_fill"]
    if fill is None:
        return None, None
    if tier == "courtside":  # sold out -> capacity constrained, not price constrained
        attendance = cap  # stays full up to the tested price ceiling
    else:
        pct_change = (new_price - cur_price) / cur_price
        new_fill = max(0.05, min(1.0, fill * (1 + ELASTICITY * pct_change)))
        attendance = new_fill * cap
    return attendance, attendance * new_price


def price_scenarios(fill_info):
    scenarios = []
    for tier in TIERS:
        cur_price = CURRENT[tier]["price"]
        cur_att, cur_rev = revenue_at_price(tier, cur_price, fill_info)
        if cur_rev is None:
            continue
        lo, hi = CURRENT[tier]["min"], CURRENT[tier]["max"]
        for step_pct in (0.10, 0.20, 0.30):
            for direction in (1, -1):
                test_price = round(cur_price * (1 + direction * step_pct))
                test_price = max(lo, min(hi, test_price))
                if test_price == cur_price:
                    continue
                att, rev = revenue_at_price(tier, test_price, fill_info)
                scenarios.append({
                    "tier": tier,
                    "from_price": cur_price,
                    "to_price": test_price,
                    "delta_pct": round(100 * (test_price - cur_price) / cur_price, 1),
                    "est_attendance": round(att),
                    "est_revenue_per_game": round(rev),
                    "delta_revenue_per_game": round(rev - cur_rev),
                })
    return scenarios


# ---------------------------------------------------------------------------
# 4. Expansion scenarios (budget tiers)
# ---------------------------------------------------------------------------

BUDGET_TIERS = [50_000, 150_000, 500_000]

def expansion_scenarios(fill_info):
    """
    Priority order, informed by observed fill:
      1. Courtside -- only tier at 100% fill (sold out) at current capacity
         and current price. Highest $/seat revenue of any tier. Best
         expansion ROI candidate.
      2. Bleachers -- healthy 80-90% fill, cheap to build ($200/seat), large
         volume lever.
      3. Lower Tier -- 96.8% fill on the single post-expansion data point --
         promising but thin evidence (1 game). Small suggested increments.
      4. Luxury -- explicitly DEPRIORITIZED: fill dropped to 62.5% right after
         capacity was quadrupled (2->8). Adding more luxury boxes before that
         fill recovers risks compounding an oversupply, not fixing one.
    """
    priority = ["courtside", "bleachers", "lower_tier"]  # luxury excluded by default
    results = {}
    for budget in BUDGET_TIERS:
        remaining = budget
        plan = []
        for tier in priority:
            cost_per_seat = CURRENT[tier]["expand_cost"]
            fill = fill_info[tier]["mean_fill"] or 0
            # only worth expanding a tier that's actually near full
            if fill < 0.85 and tier != "courtside":
                continue
            max_affordable = remaining // cost_per_seat
            if max_affordable <= 0:
                continue
            # don't blow the whole budget on one tier -- cap each tier's grab
            # at roughly what plausibly sells at current fill trend
            cap_seats = {
                "courtside": 40,     # ~+37% capacity, still small in absolute $
                "bleachers": 2000,
                "lower_tier": 150,
            }[tier]
            seats = min(max_affordable, cap_seats)
            spend = seats * cost_per_seat
            remaining -= spend
            price = CURRENT[tier]["price"]
            added_revenue_per_game = seats * price * (1.0 if tier == "courtside" else fill)
            plan.append({
                "tier": tier,
                "seats_added": int(seats),
                "spend": int(spend),
                "est_added_revenue_per_game": round(added_revenue_per_game),
            })
        results[budget] = {
            "plan": plan,
            "total_spend": budget - remaining,
            "total_added_revenue_per_game": round(sum(p["est_added_revenue_per_game"] for p in plan)),
        }
    return results


# ---------------------------------------------------------------------------
# 5. Report
# ---------------------------------------------------------------------------

def main():
    bench = load_benchmark()
    bsum = benchmark_summary(bench)
    fill_info = current_fill_rates()

    print("=" * 78)
    print("SHARPSHOOTERS ARENA OPTIMIZER -- ANALYSIS ONLY, NOTHING SUBMITTED TO BB.COM")
    print("=" * 78)

    print("\n--- Current fill rates (only rows valid for TODAY's capacity) ---")
    for t in TIERS:
        fi = fill_info[t]
        mf = f"{fi['mean_fill']*100:.1f}%" if fi["mean_fill"] is not None else "n/a"
        print(f"  {t:12s} fill={mf:>7s}  (n={fi['n_games']} game(s) at current capacity)")

    print("\n--- Where Sharpshooters' prices sit vs. the 64-team benchmark ---")
    for t in TIERS:
        key = f"{t}_price"
        sorted_vals = sorted(r[key] for r in bench)
        pct = percentile_rank(CURRENT[t]["price"], sorted_vals)
        b = bsum[t]
        print(f"  {t:12s} ${CURRENT[t]['price']:>5d}  "
              f"(benchmark: min ${b['min']}, median ${b['median']:.0f}, mean ${b['mean']:.0f}, max ${b['max']} | "
              f"Sharpshooters at the {pct:.0f}th percentile) [top-division set, directional only]")

    print("\n--- Ranked price-change scenarios (top 10 by estimated revenue gain/game) ---")
    print("    [ESTIMATE] courtside: capacity-constrained (sold out) -> same attendance, new price")
    print(f"    [ESTIMATE] other tiers: elasticity={ELASTICITY} assumed, NOT fitted from data")
    scenarios = sorted(price_scenarios(fill_info), key=lambda s: -s["delta_revenue_per_game"])
    for s in scenarios[:10]:
        print(f"  {s['tier']:12s} ${s['from_price']:>4d} -> ${s['to_price']:<4d} "
              f"({s['delta_pct']:+.0f}%)  est. attendance {s['est_attendance']:>5d}  "
              f"est. revenue/game ${s['est_revenue_per_game']:>7,d}  "
              f"(delta ${s['delta_revenue_per_game']:+,d}/game)")

    print("\n--- Expansion scenarios by budget tier ---")
    print("    [ESTIMATE] Luxury excluded from all tiers -- fill dropped to 62.5% right after")
    print("    quadrupling capacity; adding more before that recovers is not recommended.")
    exp = expansion_scenarios(fill_info)
    for budget, data in exp.items():
        print(f"\n  Budget: ${budget:,d}  (spent ${data['total_spend']:,d})")
        if not data["plan"]:
            print("    No tier both near-full and affordable at this budget -- hold.")
        for p in data["plan"]:
            print(f"    + {p['seats_added']:>4d} {p['tier']:12s} seats  "
                  f"(${p['spend']:,d})  est. +${p['est_added_revenue_per_game']:,d}/game")
        print(f"    Total est. added revenue/game: ${data['total_added_revenue_per_game']:,d}")

    print("\n" + "=" * 78)
    print("STANDING REMINDER: read-only analysis. No price/expansion change has been")
    print("submitted. Tom must apply anything he wants live, by hand, on buzzerbeater.com.")
    print("=" * 78)


if __name__ == "__main__":
    main()
