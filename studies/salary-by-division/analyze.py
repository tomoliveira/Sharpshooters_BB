import csv, sys, statistics as st, json
from pathlib import Path
D = Path(sys.argv[1]); OURS = "32988"
teams = list(csv.DictReader(open(D/"teams.csv", encoding="utf-8")))
players = list(csv.DictReader(open(D/"players.csv", encoding="utf-8")))
def q(xs, p):
    xs = sorted(xs); i = (len(xs)-1)*p; lo = int(i); hi = min(lo+1, len(xs)-1)
    return xs[lo] + (xs[hi]-xs[lo])*(i-lo)
def pearson(a, b):
    ma, mb = st.mean(a), st.mean(b); c = sum((x-ma)*(y-mb) for x, y in zip(a, b))
    sa = sum((x-ma)**2 for x in a)**.5; sb = sum((y-mb)**2 for y in b)**.5
    return c/(sa*sb) if sa and sb else 0
out = {"levels": {}}
human = [t for t in teams if t["is_bot"] == "0" and int(t["n_players"]) >= 5]
bots = [t for t in teams if t["is_bot"] != "0"]
print(f"teams {len(teams)}  human {len(human)}  bots {len(bots)}  players {len(players)}")
for lv in "12345":
    T = [t for t in human if t["level"] == lv]; Tb = [t for t in teams if t["level"] == lv]
    if not T: continue
    pay = [int(t["payroll"]) for t in T]
    P = [int(p["salary"]) for p in players if p["level"] == lv and p["is_bot"] == "0"]
    top = [int(t["max_salary"]) for t in T]
    top3 = []
    for t in T:
        s = sorted((int(p["salary"]) for p in players if p["team_id"] == t["team_id"]), reverse=True)
        top3.append(sum(s[:3])/sum(s) if sum(s) else 0)
    wp = [int(t["wins"])/max(1, int(t["wins"])+int(t["losses"])) for t in T]
    r = dict(n_leagues=len({t["league_id"] for t in Tb}), n_teams=len(T), n_bots=len(Tb)-len(T),
             payroll={k: round(q(pay, p)) for k, p in [("min",0),("p10",.1),("p25",.25),("median",.5),("p75",.75),("p90",.9),("max",1)]},
             payroll_mean=round(st.mean(pay)), payroll_cv=round(st.pstdev(pay)/st.mean(pay), 2),
             player_salary={k: round(q(P, p)) for k, p in [("p25",.25),("median",.5),("p75",.75),("p90",.9),("max",1)]},
             n_players=len(P), share_players_over_180k=round(sum(x > 180000 for x in P)/len(P), 3),
             top_player_median=round(st.median(top)), top3_share_median=round(st.median(top3), 2),
             corr_payroll_winpct=round(pearson(pay, wp), 2),
             roster_size_median=st.median(int(t["n_players"]) for t in T))
    out["levels"][lv] = r
    print(f"\nLEVEL {lv}: {r['n_teams']} human teams ({r['n_bots']} bots) in {r['n_leagues']} leagues")
    print("  payroll", r["payroll"], "mean", r["payroll_mean"], "cv", r["payroll_cv"])
    print("  player salary", r["player_salary"], ">180k share", r["share_players_over_180k"])
    print("  top player median", r["top_player_median"], "top3 share", r["top3_share_median"], "corr(pay,win%)", r["corr_payroll_winpct"])
us = next((t for t in teams if t["team_id"] == OURS), None)
if us:
    up = int(us["payroll"]); out["ours"] = {"payroll": up, "max_salary": int(us["max_salary"]), "pct_by_level": {}}
    for lv in "12345":
        pay = [int(t["payroll"]) for t in human if t["level"] == lv]
        if pay: out["ours"]["pct_by_level"][lv] = round(100*sum(x < up for x in pay)/len(pay))
    print("\nSharpshooters payroll", up, "percentile by level", out["ours"]["pct_by_level"])
json.dump(out, open(D/"summary.json", "w"), indent=1)
