"""Scrape each flipped player's weekly salary by season from his public history page.

Reads mloty_stargard_teen_flips.csv, writes data/salary_history.json as
{player_id: [[season, weekly_salary], ...]}. No login needed.
"""
import csv
import json
import re
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(ROOT / "mloty_stargard_teen_flips.csv", encoding="utf-8")))

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0"
out = {}
for r in rows:
    pid = r["Player ID"]
    html = s.get(f"https://buzzerbeater.com/player/{pid}/history.aspx", timeout=30).text
    m = re.search(r"data\.addRows\((\[\[.*?\]\])\)", html)
    out[pid] = json.loads(m.group(1)) if m else None
    time.sleep(0.8)

json.dump(out, open(ROOT / "data" / "salary_history.json", "w"))
print(f"{sum(v is not None for v in out.values())} of {len(out)} players have salary history")
