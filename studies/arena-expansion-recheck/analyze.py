"""Recheck the payback of every Sharpshooters arena expansion with the real
attendance per seat tier, and estimate ticket-price elasticity from the
attendance and price history in docs/report.db.

Run from the repo root:  python studies/arena-expansion-recheck/analyze.py
Writes matches.csv, expansions.csv, elasticity.csv and summary.json next to
this script. Read-only on report.db; no network access.
"""
import csv, json, math, sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TEAM = "32988"
TIERS = ["bleachers", "lowerTier", "courtside", "luxury"]
COST = {"bleachers": 200, "lowerTier": 700, "courtside": 2000, "luxury": 16000}  # handoff.md
PLAYOFF = ("league.quarterfinal", "league.semifinal", "league.final")
HOME_LEAGUE_GAMES = 11      # 22 league games, half at home (game manual)
PLAYOFF_HOME_EQUIV = 1.5    # this season: 3 home playoff games at a 50/50 split

db = sqlite3.connect(ROOT / "docs" / "report.db")
snap = json.loads(db.execute(
    "select data_json from snapshots where team_key='sharpshooters' order by id desc limit 1").fetchone()[0])
inv = snap["investments"]
actual = {m["matchid"]: m["amount"] for r in inv["arena"]["regimes"] for m in r["matches"]}
actual.update({m["matchid"]: m["amount"] for m in inv["arena"]["pre_tracking"]})

hist = [(d, json.loads(s), json.loads(p)) for d, s, p in db.execute(
    "select date, seats_json, prices_json from league_arena_prices where team_id=? order by date", (TEAM,))]

# ---- 1. Our home games: verify the prices in effect against the real gate revenue
matches = []
for mid, date, mtype, att in db.execute(
        "select matchid, match_date, match_type, attendance_json from match_attendance "
        "where home_team_id=? order by match_date", (TEAM,)):
    att = json.loads(att)
    share = 0.5 if mtype in PLAYOFF else 1.0
    before = [h for h in hist if h[0] <= date]
    # candidates: the last snapshot on/before the game, then the next one (price set
    # changed on game day before tip-off). Keep the one that reproduces the real amount.
    cands = ([before[-1]] if before else []) + [h for h in hist if h[0] > date][:1]
    chosen, verified = None, False
    for h in cands:
        rev = share * sum(att[t] * h[2][t] for t in TIERS)
        if actual.get(mid) is not None and abs(rev - actual[mid]) < 1:
            chosen, verified = h, True
            break
    if chosen is None:
        chosen = cands[0]
    # Capacity in effect: last capacity on/before the game (expansions finish between snapshots)
    seats = (before[-1] if before else hist[0])[1]
    matches.append(dict(matchid=mid, date=date, type=mtype, share=share,
                        seats=seats, prices=chosen[2], att=att,
                        price_date=chosen[0], verified=verified,
                        actual=actual.get(mid)))

# ---- 2. Expansion layers: capacity before/after each purchase
capex = [x for x in inv["capex"] if x["tag"] == "arenaExpansion"]
caps = []  # distinct capacity states in order
for d, s, p in hist:
    if not caps or s != caps[-1][1]:
        caps.append((d, s))
layers = []
for i, x in enumerate(capex):
    if i + 1 < len(caps):
        live, after = caps[i + 1]
        before = caps[i][1]
        added = {t: after[t] - before[t] for t in TIERS}
        cost_check = sum(added[t] * COST[t] for t in TIERS)
    else:
        live, before, after, added, cost_check = None, caps[-1][1], None, None, None
    layers.append(dict(n=i + 1, bought=x["date"][:10], cost=-x["amount"], live=live,
                       before=before, after=after, added=added, cost_check=cost_check))

def layer_revenue(m, L):
    """Gate revenue from the seats one expansion added, in one game. Fans fill a
    tier's older seats first, so a layer only earns when attendance passes the
    capacity it was built on top of."""
    if L["after"] is None or m["date"] < L["live"]:
        return None, {}
    rev, seats_used = 0.0, {}
    for t in TIERS:
        lo, hi = L["before"][t], L["after"][t]
        used = max(0, min(m["att"][t], hi) - lo)
        seats_used[t] = used
        rev += used * m["prices"][t]
    return rev * m["share"], seats_used

exp_rows = []
for L in layers:
    games, total, full_equiv, used_tot = 0, 0.0, 0.0, {t: 0 for t in TIERS}
    for m in matches:
        r, used = layer_revenue(m, L)
        if r is None:
            continue
        games += 1; total += r; full_equiv += m["share"]
        for t in TIERS:
            used_tot[t] += used[t]
    per_full = total / full_equiv if full_equiv else None
    fill = {t: (used_tot[t] / (L["added"][t] * games) if L["added"] and L["added"][t] > 0 and games else None)
            for t in TIERS}
    base = per_full * HOME_LEAGUE_GAMES if per_full else None
    deep = per_full * (HOME_LEAGUE_GAMES + PLAYOFF_HOME_EQUIV) if per_full else None
    exp_rows.append(dict(
        expansion=L["n"], bought=L["bought"], live_by=L["live"], cost=L["cost"],
        cost_matches_seats=(L["cost_check"] == L["cost"]) if L["cost_check"] is not None else None,
        added_bleachers=L["added"] and L["added"]["bleachers"],
        added_lowerTier=L["added"] and L["added"]["lowerTier"],
        added_courtside=L["added"] and L["added"]["courtside"],
        added_luxury=L["added"] and L["added"]["luxury"],
        games_since_live=games, revenue_so_far=round(total),
        recovered_pct=round(100 * total / L["cost"], 1),
        rev_per_full_game=round(per_full) if per_full else None,
        fill_bleachers=fill["bleachers"] and round(fill["bleachers"], 3),
        fill_lowerTier=fill["lowerTier"] and round(fill["lowerTier"], 3),
        fill_courtside=fill["courtside"] and round(fill["courtside"], 3),
        fill_luxury=fill["luxury"] and round(fill["luxury"], 3),
        payback_seasons_baseline=round(L["cost"] / base, 2) if base else None,
        payback_seasons_deep_run=round(L["cost"] / deep, 2) if deep else None))

# ---- 2b. Per tier: what one added seat actually earned, and its payback
tier_rows = []
for t in TIERS:
    seats_added = cost = rev = seat_games = 0.0
    for L in layers:
        if not L["added"] or L["added"][t] <= 0:
            continue
        seats_added += L["added"][t]; cost += L["added"][t] * COST[t]
        for m in matches:
            if m["date"] < L["live"]:
                continue
            used = max(0, min(m["att"][t], L["after"][t]) - L["before"][t])
            rev += used * m["prices"][t] * m["share"]
            seat_games += L["added"][t] * m["share"]
    per_seat_game = rev / seat_games if seat_games else None
    tier_rows.append(dict(tier=t, seats_added=int(seats_added), cost=int(cost),
                          cost_per_seat=COST[t],
                          rev_per_added_seat_per_full_game=round(per_seat_game, 2) if per_seat_game else None,
                          payback_seasons_baseline=round(COST[t] / (per_seat_game * HOME_LEAGUE_GAMES), 2) if per_seat_game else None))

# ---- 3. Price elasticity
# 3a. Does the league give any price variation to fit on?
league_price_sets = {}
for t_id, p in db.execute("select team_id, prices_json from league_arena_prices"):
    league_price_sets.setdefault(t_id, set()).add(p)
variation = {k: len(v) for k, v in league_price_sets.items()}

# 3b. Our own games: log-log fit per tier on uncensored games (attendance < capacity),
# with a playoff dummy. Sold-out games only bound demand from below.
def ols(X, y):
    n, k = len(X), len(X[0])
    XtX = [[sum(X[r][i] * X[r][j] for r in range(n)) for j in range(k)] for i in range(k)]
    Xty = [sum(X[r][i] * y[r] for r in range(n)) for i in range(k)]
    # Gauss-Jordan
    A = [row[:] + [Xty[i]] for i, row in enumerate(XtX)]
    for i in range(k):
        piv = max(range(i, k), key=lambda r: abs(A[r][i]))
        A[i], A[piv] = A[piv], A[i]
        if abs(A[i][i]) < 1e-12:
            return None
        for r in range(k):
            if r != i:
                f = A[r][i] / A[i][i]
                A[r] = [a - f * b for a, b in zip(A[r], A[i])]
    return [A[i][k] / A[i][i] for i in range(k)]

el_rows = []
verified = [m for m in matches if m["verified"]]
for t in TIERS:
    unc = [m for m in verified if m["att"][t] < m["seats"][t]]
    soldout = [m for m in verified if m["att"][t] >= m["seats"][t]]
    fit = None
    has_po = len({m["share"] for m in unc}) > 1
    if len({m["prices"][t] for m in unc}) >= 2 and len(unc) >= (4 if has_po else 3):
        X = [[1.0, math.log(m["prices"][t])] + ([1.0 if m["share"] < 1 else 0.0] if has_po else []) for m in unc]
        y = [math.log(m["att"][t]) for m in unc]
        fit = ols(X, y)
    el_rows.append(dict(tier=t, uncensored_games=len(unc), sold_out_games=len(soldout),
                        elasticity=round(fit[1], 2) if fit else None,
                        playoff_effect=round(fit[2], 2) if fit and has_po else None))

# 3c. Same-period regular-season pair: 2026-10-13 vs 2026-10-17 (same capacity, 4 days apart)
pair = {m["date"]: m for m in verified}
pairs = []
for a, b in [("2026-10-13", "2026-10-17"), ("2026-09-15", "2026-09-26")]:
    if a in pair and b in pair:
        ma, mb = pair[a], pair[b]
        for t in TIERS:
            pa, pb = ma["prices"][t], mb["prices"][t]
            qa, qb = ma["att"][t], mb["att"][t]
            ca, cb = qa >= ma["seats"][t], qb >= mb["seats"][t]
            if pa == pb or (ca and cb):
                continue  # no price change, or sold out both times: no information
            e = math.log(qb / qa) / math.log(pb / pa)
            # A sold-out game only shows demand was at least its attendance.
            cheap_sold_out = (ca and pa < pb) or (cb and pb < pa)
            reading = "at least this elastic" if cheap_sold_out else (
                "at most this elastic" if (ca or cb) else "point estimate")
            pairs.append(dict(games=f"{a} vs {b}", tier=t, prices=f"{pa:g} -> {pb:g}",
                              attendance=f"{qa} -> {qb}", arc_elasticity=round(e, 2),
                              reading=reading))

# ---- write outputs
with open(OUT / "matches.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["matchid", "date", "type", "gate_share", "price_snapshot", "prices_verified",
                "actual_revenue"] + [f"cap_{t}" for t in TIERS] + [f"price_{t}" for t in TIERS]
               + [f"att_{t}" for t in TIERS] + [f"fill_{t}" for t in TIERS])
    for m in matches:
        w.writerow([m["matchid"], m["date"], m["type"], m["share"], m["price_date"], m["verified"],
                    m["actual"]] + [m["seats"][t] for t in TIERS] + [m["prices"][t] for t in TIERS]
                   + [m["att"][t] for t in TIERS]
                   + [round(m["att"][t] / m["seats"][t], 3) for t in TIERS])
for name, rows in (("expansions.csv", exp_rows), ("tiers.csv", tier_rows), ("elasticity.csv", el_rows), ("elasticity_pairs.csv", pairs)):
    with open(OUT / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)

summary = dict(
    source_snapshot=snap["now"], total_arena_capex=sum(L["cost"] for L in layers),
    expansions=len(layers), league_teams_with_one_price_set=sum(1 for v in variation.values() if v == 1),
    league_teams=len(variation), price_sets_per_team=variation,
    verified_games=len(verified), home_games=len(matches),
    unverified_games=[m["date"] for m in matches if not m["verified"]],
    built_expansions_cost=sum(L["cost"] for L in layers if L["after"]),
    built_expansions_rev_per_full_game=round(sum(r["rev_per_full_game"] or 0 for r in exp_rows)),
    built_expansions_payback_seasons_baseline=round(
        sum(L["cost"] for L in layers if L["after"]) /
        (sum(r["rev_per_full_game"] or 0 for r in exp_rows) * HOME_LEAGUE_GAMES), 2))
(OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

for rows in (exp_rows, tier_rows, el_rows, pairs):
    for r in rows:
        print(r)
print(json.dumps(summary, indent=2))
