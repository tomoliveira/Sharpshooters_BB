"""Collect Brazil team rosters (salary per player) by division level via BB API. Read-only."""
import os, requests, re, csv, random, time, sys
import xml.etree.ElementTree as ET
from pathlib import Path
OUT = Path(sys.argv[1])
env = {"BB_LOGIN": os.environ["BB_LOGIN"], "BB_CODE": os.environ["BB_CODE"]}  # repo is public: credentials come from the environment
s = requests.Session(); B="https://bbapi.buzzerbeater.com/"
def login(): s.get(B+"login.aspx", params={"login":env["BB_LOGIN"],"code":env["BB_CODE"]})
def get(ep, **p):
    for i in range(4):
        try:
            r = s.get(B+ep, params=p, timeout=30); root = ET.fromstring(r.content)
            if root.find("error") is not None and "login" in (root.find("error").get("message","")+r.text).lower():
                login(); continue
            time.sleep(0.25); return root
        except Exception as e:
            time.sleep(2); login()
    return None
login(); random.seed(73)
leagues = []
for lv in range(1,6):
    root = get("leagues.aspx", countryid=3, level=lv)
    ids = [(l.get("id"), (l.findtext("leagueName") or l.text or "").strip()) for l in root.iter("league")]
    if lv >= 4: ids = random.sample(ids, 16)
    leagues += [(lv, i, n) for i, n in ids]
print("leagues:", len(leagues), flush=True)
teams_f = open(OUT/"teams.csv","w",newline="",encoding="utf-8"); tw = csv.writer(teams_f)
tw.writerow(["level","league_id","league","team_id","team","is_bot","wins","losses","pf","pa","n_players","payroll","max_salary","median_salary","total_dmi"])
pl_f = open(OUT/"players.csv","w",newline="",encoding="utf-8"); pw = csv.writer(pl_f)
pw.writerow(["level","league_id","team_id","is_bot","player_id","age","pos","salary","dmi","potential"])
for k,(lv,lid,lname) in enumerate(leagues):
    st = get("standings.aspx", leagueid=lid)
    if st is None: continue
    lname = st.findtext(".//league") or lname
    for t in st.iter("team"):
        tid = t.get("id"); bot = t.findtext("isBot")
        ro = get("roster.aspx", teamid=tid)
        sal=[]; dmi=0
        for p in (ro.iter("player") if ro is not None else []):
            sv=int(p.findtext("salary") or 0); dv=int(p.findtext("dmi") or 0); sal.append(sv); dmi+=dv
            pw.writerow([lv,lid,tid,bot,p.get("id"),p.findtext("age"),p.findtext("bestPosition"),sv,dv,p.findtext("skills/potential")])
        ss=sorted(sal)
        tw.writerow([lv,lid,lname,tid,t.findtext("teamName"),bot,t.findtext("wins"),t.findtext("losses"),t.findtext("pf"),t.findtext("pa"),
                     len(sal),sum(sal),max(sal) if sal else 0,ss[len(ss)//2] if ss else 0,dmi])
    teams_f.flush(); pl_f.flush()
    print(f"{k+1}/{len(leagues)} L{lv} {lname}", flush=True)
print("DONE", flush=True)
