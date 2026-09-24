"""Download BuzzerBeater season start/finish dates to data/seasons.csv.

Needs the official API login in the environment: BB_LOGIN and BB_CODE.
"""
import csv
import os
import re
from pathlib import Path

import requests

OUT = Path(__file__).resolve().parent.parent / "data" / "seasons.csv"

s = requests.Session()
s.get("https://bbapi.buzzerbeater.com/login.aspx",
      params={"login": os.environ["BB_LOGIN"], "code": os.environ["BB_CODE"]}, timeout=30)
xml = s.get("https://bbapi.buzzerbeater.com/seasons.aspx", timeout=30).text
rows = re.findall(r"<season id='(\d+)'>\s*<start>(.*?)</start>\s*(?:<finish>(.*?)</finish>)?", xml)
with open(OUT, "w", encoding="utf-8", newline="") as f:
    w = csv.writer(f)
    w.writerow(["season", "start", "finish"])
    w.writerows(rows)
print(f"{len(rows)} seasons -> {OUT}")
