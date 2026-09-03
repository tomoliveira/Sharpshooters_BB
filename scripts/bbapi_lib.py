#!/usr/bin/env python3
"""BuzzerBeater fetch + render logic, ported from the buzzerbeater-report
skill's bbapi_report.py. Behavior is unchanged from that script except for
persistence: the original kept two pieces of state on local disk
(reports/<team>/.last_roster.xml and investments.json), which doesn't
survive between GitHub Actions runs. Here that state lives in the same
SQLite database this module writes report snapshots into (see init_db,
load_investment_ledger/save_investment_ledger, load_prev_roster_root/
save_roster_xml) - a `state` table keyed by team_key, updated after each
successful run.
"""
import html, json, os, re, sys, xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
import requests
from dotenv import load_dotenv

BASE = "https://bbapi.buzzerbeater.com"
SCRIPT_DIR = Path(__file__).resolve().parent
TRAINING_REMINDER = "Training report not available via API - check https://buzzerbeater.com/manage/training.aspx manually."
SKILL_TAGS = ["jumpShot", "range", "outsideDef", "handling", "driving", "passing",
              "insideShot", "insideDef", "rebound", "block", "stamina", "freeThrow"]

# The training cohort itself (who + why) is Tom's own manually-reasoned selection,
# recorded as static analysis elsewhere in this report. These are just their player
# IDs, so the card rendering below can pull fresh live data for exactly those four
# each run without re-doing the selection logic. Overridden per-team by
# teams/<team_key>.json's "training_cohort".
TRAINING_COHORT_IDS = {
    "56146672": "Lauro Mendonça", "56146678": "Élder Landim",
    "56146681": "Fiorindo Valença", "55910729": "Gunnar Støen",
}
# Training focus itself still has no API endpoint (training.aspx is a plain web
# page) - carried over from the last check it was confirmed by screenshot.
# TRAINING_FOCUS_POSITIONS must be kept in sync with CURRENT_TRAINING_FOCUS by
# hand - per Tom, only minutes played AT one of these positions count toward
# the training threshold; minutes at any other position (e.g. a C/PF trainee
# subbed in at PG) don't count even though the player is still on the floor.
CURRENT_TRAINING_FOCUS = "Rebounding, C / PF"
TRAINING_FOCUS_POSITIONS = ["PF", "C"]

def training_threshold(age):
    try: age = int(age)
    except (TypeError, ValueError): return None
    if age <= 19: return 45
    if age <= 26: return 48
    return 40

def build_training_minutes_status(position_minutes, roster_root):
    """Weekly minutes come live from boxscore.aspx (see
    fetch_weekly_position_minutes) - genuinely this week's total, not carried
    over. Per Tom, only minutes at TRAINING_FOCUS_POSITIONS count toward the
    threshold. The Clears/Short/Well-short bucketing itself is our own
    heuristic (gap <=10 -> "Short by N", else "Well short"), not an official
    in-game label - the game likely just shows a binary clears-or-not
    indicator."""
    out = {}
    for p in roster_root.findall(".//player"):
        pid = p.get("id")
        threshold = training_threshold(p.findtext("age"))
        if pid is None or threshold is None: continue
        minutes = round(total_minutes(position_minutes.get(pid, {}), TRAINING_FOCUS_POSITIONS))
        gap = threshold - minutes
        status = "Clears" if gap <= 0 else (f"Short by {gap}" if gap <= 10 else "Well short")
        out[pid] = {"minutes": minutes, "threshold": threshold, "status": status}
    return out

def build_minutes_vs_money(position_minutes, roster_root):
    """Total minutes (any position) this training-week, live via boxscore.aspx,
    against salary - a gut check on whether the highest earners are actually
    playing, independent of the training-position filter above."""
    rows = []
    for p in roster_root.findall(".//player"):
        pid = p.get("id")
        name = f"{p.findtext('firstName') or ''} {p.findtext('lastName') or ''}".strip()
        try: salary = float(p.findtext("salary") or 0)
        except (TypeError, ValueError): salary = 0
        minutes = round(total_minutes(position_minutes.get(pid, {})))
        rows.append({"playerid": pid, "name": name, "salary": salary, "minutes": minutes})
    rows.sort(key=lambda r: -r["salary"])
    for i, r in enumerate(rows, start=1):
        r["salary_rank"] = i
    return rows[:6]

# Full potential-adjective scale, verbatim from the Game Manual (rules.aspx?nav=Nomenclature).
POTENTIAL_WORD_SCALE = {0: "announcer", 1: "bench warmer", 2: "role player", 3: "6th man",
                         4: "starter", 5: "star", 6: "allstar", 7: "perennial allstar",
                         8: "superstar", 9: "MVP", 10: "hall of famer", 11: "all-time great"}

load_dotenv(SCRIPT_DIR.parent / ".env")
load_dotenv(SCRIPT_DIR / ".env", override=True)
LOGIN = os.environ.get("BB_LOGIN")
CODE = os.environ.get("BB_CODE")
TEAM_KEY = "default"

def load_team_config(config_path):
    """Apply a per-team config JSON over the module-level defaults above.
    Must run before build_report()/login() - everything it touches is read
    from these globals at call time, not at import time, so reassigning here
    is safe as long as it happens first."""
    global CURRENT_TRAINING_FOCUS, TRAINING_FOCUS_POSITIONS, TRAINING_COHORT_IDS
    global LOGIN, CODE, TEAM_KEY
    cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
    CURRENT_TRAINING_FOCUS = cfg.get("current_training_focus", CURRENT_TRAINING_FOCUS)
    TRAINING_FOCUS_POSITIONS = cfg.get("training_focus_positions", TRAINING_FOCUS_POSITIONS)
    TRAINING_COHORT_IDS = cfg.get("training_cohort", TRAINING_COHORT_IDS)
    TEAM_KEY = cfg.get("team_key") or Path(config_path).stem
    # Separate env var names let one environment hold credentials for several
    # teams at once (each BuzzerBeater login owns exactly one team, so a
    # multi-team setup needs one BB_LOGIN/BB_CODE pair per team). Defaults to
    # the plain BB_LOGIN/BB_CODE so a single-team setup needs no config at all.
    LOGIN = os.environ.get(cfg.get("bb_login_env", "BB_LOGIN"))
    CODE = os.environ.get(cfg.get("bb_code_env", "BB_CODE"))
    return cfg

class BBApiError(Exception): pass

def get_xml(session, endpoint, params=None):
    resp = session.get(f"{BASE}/{endpoint}", params=params, timeout=30)
    resp.raise_for_status()
    return ET.fromstring(resp.content)

def login(session):
    if not LOGIN or not CODE:
        raise BBApiError("BB_LOGIN / BB_CODE not set.")
    root = get_xml(session, "login.aspx", {"login": LOGIN, "code": CODE})
    err = root.find("error")
    if err is not None:
        raise BBApiError(f"Login failed: {err.get('message')}")

def fetch(session, endpoint, params=None, _retried=False):
    root = get_xml(session, endpoint, params)
    err = root.find("error")
    if err is not None:
        if err.get("message") == "NotAuthorized" and not _retried:
            login(session)
            return fetch(session, endpoint, params, _retried=True)
        raise BBApiError(f"{endpoint}: {err.get('message')}")
    return root

# staff.aspx's skilllevel is a plain 1-7 index into this list - confirmed
# verbatim against the Game Manual's "Staff Skill Levels" section.
STAFF_LEVEL_WORDS = ["minimal", "basic", "competent", "advanced", "superior", "exceptional", "world-renowned"]
STAFF_TYPES = {0: "Doctor", 1: "Trainer", 2: "PR Manager"}

def fetch_staff(session):
    out = []
    for type_id, role in STAFF_TYPES.items():
        try:
            root = fetch(session, "staff.aspx", {"type": type_id})
        except (BBApiError, requests.RequestException):
            continue
        s = root.find("staff")
        if s is None:
            continue
        name = f"{s.findtext('firstName') or ''} {s.findtext('lastName') or ''}".strip()
        try: level = int(s.findtext("skilllevel"))
        except (TypeError, ValueError): level = None
        specialty = s.findtext("specialty")
        out.append({
            "role": role, "name": name,
            "level": level, "level_word": STAFF_LEVEL_WORDS[level - 1] if level and 1 <= level <= 7 else None,
            "specialty": specialty, "salary": s.findtext("salaryPrev"),
        })
    return out

def money(v):
    try: return f"{float(v):,.0f}"
    except (TypeError, ValueError): return str(v)

def signed_money(v):
    try: return f"{float(v):+,.0f}"
    except (TypeError, ValueError): return str(v)

def humanize(tag):
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", tag).lower()

def team_name(elem):
    text = elem.findtext("teamName") if elem is not None else None
    return html.unescape(text) if text else text

def aggregate_week(week):
    initial = week.findtext("initial")
    totals = {}
    for child in week:
        if child.tag in ("initial", "final", "current"): continue
        try: totals[child.tag] = totals.get(child.tag, 0) + float(child.text)
        except (TypeError, ValueError): continue
    final = week.findtext("final")
    if final is None:
        try: final = str(float(initial) + sum(totals.values()))
        except (TypeError, ValueError): final = week.findtext("current")
    return initial, final, totals

def parse_week_items(week):
    items = []
    for child in week:
        if child.tag in ("initial", "final", "current"):
            continue
        try:
            amt = float(child.text)
        except (TypeError, ValueError):
            continue
        if amt == 0:
            continue
        items.append({"date": child.get("date", ""), "tag": child.tag, "amount": amt})
    return items


def parse_roster(root):
    players = {}
    for p in root.findall(".//player"):
        pid = p.get("id")
        if not pid: continue
        name = f"{p.findtext('firstName') or ''} {p.findtext('lastName') or ''}".strip()
        players[pid] = {"name": name or f"player {pid}", "salary": p.findtext("salary")}
    return players

def player_snapshot(p):
    skills = p.find("skills")
    skill_sum = None
    if skills is not None:
        vals = []
        for tag in SKILL_TAGS:
            v = skills.findtext(tag)
            try: vals.append(float(v))
            except (TypeError, ValueError): pass
        if vals: skill_sum = sum(vals)
    name = f"{p.findtext('firstName') or ''} {p.findtext('lastName') or ''}".strip()
    return {"name": name, "age": p.findtext("age"), "position": p.findtext("bestPosition"),
            "potential": skills.findtext("potential") if skills is not None else None,
            "salary": p.findtext("salary"), "skill_sum": skill_sum}

# Full 20-level skill-adjective scale, verbatim from the Game Manual.
SKILL_WORD_SCALE = {
    1: "atrocious", 2: "pitiful", 3: "awful", 4: "inept", 5: "mediocre",
    6: "average", 7: "respectable", 8: "strong", 9: "proficient", 10: "prominent",
    11: "prolific", 12: "sensational", 13: "tremendous", 14: "wondrous", 15: "marvelous",
    16: "prodigious", 17: "stupendous", 18: "phenomenal", 19: "colossal", 20: "legendary",
}
SKILL_DISPLAY_COLUMNS = [
    ("jumpShot", "Jump Shot"), ("range", "Jump Range"), ("outsideDef", "Outside Def."),
    ("handling", "Handling"), ("driving", "Driving"), ("passing", "Passing"),
    ("insideShot", "Inside Shot"), ("insideDef", "Inside Def."), ("rebound", "Rebounding"),
    ("block", "Shot Blocking"), ("stamina", "Stamina"), ("freeThrow", "Free Throw"),
]

# Grouping for the full-roster skill table, matching the OSP/ISP split
# already used in this report's own training doctrine. Per Tom: Driving and
# Passing are OSP (guard) skills, not unaffiliated - only Stamina and Free
# Throw don't cleanly belong to either group.
SKILL_GROUPS = [
    ("OSP", [("jumpShot", "Jump Shot"), ("range", "Jump Range"), ("outsideDef", "Outside Def."), ("handling", "Handling"),
              ("driving", "Driving"), ("passing", "Passing")]),
    ("ISP", [("insideShot", "Inside Shot"), ("insideDef", "Inside Def."), ("rebound", "Rebounding"), ("block", "Shot Blocking")]),
    ("Other", [("stamina", "Stamina"), ("freeThrow", "Free Throw")]),
]

def skill_number_only(v):
    """Colored number only, no word - the word is still available on hover via
    title, for the roster-wide table where 12 full "word (n)" labels per row
    made the table too wide to scan."""
    try: n = int(v)
    except (TypeError, ValueError): return esc(v)
    word = SKILL_WORD_SCALE.get(n)
    color = SKILL_COLOR_SCALE.get(n)
    title_attr = f' title="{esc(word)}"' if word else ""
    style = f' style="color:var({color}); font-weight:600;"' if color else ""
    return f'<span{title_attr}{style}>{n}</span>'

# Exact game colors, extracted from contentbox.css (.lev1-.lev20). Rendered
# via the --lev1..--lev20 custom properties defined in the template.
SKILL_COLOR_SCALE = {n: f"--lev{n}" for n in range(1, 21)}

# The Potential scale reuses the same 20-color ramp, but offset - per the
# manual, potential's 12 levels (0-11) map to lev5..lev17 (skipping lev14).
POTENTIAL_COLOR_LEV = {0: 5, 1: 6, 2: 7, 3: 8, 4: 9, 5: 10, 6: 11,
                        7: 12, 8: 13, 9: 15, 10: 16, 11: 17}

def skill_label(v):
    try: n = int(v)
    except (TypeError, ValueError): return esc(v)
    word = SKILL_WORD_SCALE.get(n)
    if word is None: return str(n)
    text = f'{word} ({n})'
    color = SKILL_COLOR_SCALE.get(n)
    return f'<span style="color:var({color})">{text}</span>' if color else text

def potential_label(v):
    try: n = int(v)
    except (TypeError, ValueError): return esc(v)
    word = POTENTIAL_WORD_SCALE.get(n)
    if word is None: return str(n)
    text = f'{n} &middot; {word}'
    lev = POTENTIAL_COLOR_LEV.get(n)
    return f'<span style="color:var(--lev{lev})">{text}</span>' if lev else text

def height_str(inches):
    try: inches = float(inches)
    except (TypeError, ValueError): return "—"
    ft, rem = divmod(round(inches), 12)
    cm = round(inches * 2.54)
    return f'{ft}\'{rem}" / {cm} cm'

def build_training_cohort_cards(roster_root):
    cards = []
    for pid, known_name in TRAINING_COHORT_IDS.items():
        p = roster_root.find(f".//player[@id='{pid}']")
        if p is None:
            cards.append({"playerid": pid, "name": known_name, "on_roster": False})
            continue
        skills = p.find("skills")
        name = f"{p.findtext('firstName') or ''} {p.findtext('lastName') or ''}".strip()
        cards.append({
            "playerid": pid, "name": name, "on_roster": True,
            "position": p.findtext("bestPosition"), "age": p.findtext("age"),
            "height": p.findtext("height"), "dmi": p.findtext("dmi"), "salary": p.findtext("salary"),
            "potential": skills.findtext("potential") if skills is not None else None,
            "game_shape": skills.findtext("gameShape") if skills is not None else None,
            "experience": skills.findtext("experience") if skills is not None else None,
            "skills": {tag: {"value": skills.findtext(tag), "pop": skills.find(tag).get("pop") if skills.find(tag) is not None else None}
                       for tag in SKILL_TAGS} if skills is not None else {},
        })
    return cards

def build_roster_skills_table(roster_root):
    rows = []
    for p in roster_root.findall(".//player"):
        skills = p.find("skills")
        if skills is None: continue
        name = f"{p.findtext('firstName') or ''} {p.findtext('lastName') or ''}".strip()
        row = {"playerid": p.get("id"), "name": name, "position": p.findtext("bestPosition"),
               "age": p.findtext("age"), "potential": skills.findtext("potential")}
        for tag, _ in SKILL_DISPLAY_COLUMNS:
            el_text = skills.findtext(tag)
            pop = skills.find(tag).get("pop") if skills.find(tag) is not None else None
            row[tag] = {"value": el_text, "pop": pop}
        rows.append(row)
    return {"rows": rows}

# ---------------------------------------------------------------------------
# Persistence: SQLite instead of local reports/<team_key>/ files. Everything
# below replaces bbapi_report.py's load_investment_ledger/save_investment_ledger
# and the ROSTER_CACHE read/write, keeping the exact same ledger schema and
# update logic - only where it's stored changed, so an ephemeral GitHub
# Actions runner keeps full continuity across runs.
# ---------------------------------------------------------------------------

def init_db(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS snapshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_key TEXT NOT NULL,
        fetched_at TEXT NOT NULL,
        data_json TEXT NOT NULL,
        fragments_json TEXT NOT NULL
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_team_time ON snapshots(team_key, fetched_at)")
    conn.execute("""CREATE TABLE IF NOT EXISTS state (
        team_key TEXT PRIMARY KEY,
        roster_xml TEXT,
        ledger_json TEXT
    )""")
    conn.commit()

def load_investment_ledger(conn, team_key):
    row = conn.execute("SELECT ledger_json FROM state WHERE team_key=?", (team_key,)).fetchone()
    if row and row[0]:
        try: ledger = json.loads(row[0])
        except json.JSONDecodeError: ledger = {}
    else:
        ledger = {}
    ledger.setdefault("player_transactions", [])
    ledger.setdefault("capex", [])
    ledger.setdefault("player_snapshots", {})
    ledger.setdefault("match_revenue", [])
    ledger.setdefault("arena_snapshots", [])
    return ledger

def save_investment_ledger(conn, team_key, ledger):
    conn.execute(
        "INSERT INTO state (team_key, ledger_json) VALUES (?, ?) "
        "ON CONFLICT(team_key) DO UPDATE SET ledger_json=excluded.ledger_json",
        (team_key, json.dumps(ledger, ensure_ascii=False)),
    )
    conn.commit()

def load_prev_roster_root(conn, team_key):
    row = conn.execute("SELECT roster_xml FROM state WHERE team_key=?", (team_key,)).fetchone()
    if not row or not row[0]:
        return None
    try:
        return ET.fromstring(row[0])
    except ET.ParseError:
        return None

def save_roster_xml(conn, team_key, roster_root):
    xml_str = ET.tostring(roster_root, encoding="unicode")
    conn.execute(
        "INSERT INTO state (team_key, roster_xml) VALUES (?, ?) "
        "ON CONFLICT(team_key) DO UPDATE SET roster_xml=excluded.roster_xml",
        (team_key, xml_str),
    )
    conn.commit()

ARENA_SEAT_TIERS = ["bleachers", "lowerTier", "courtside", "luxury"]

def arena_snapshot(arena_root, run_date):
    seats_el = arena_root.find(".//seats")
    if seats_el is None: return None
    seats, prices = {}, {}
    for tier in ARENA_SEAT_TIERS:
        el = seats_el.find(tier)
        if el is None: continue
        try: seats[tier] = int(el.text)
        except (TypeError, ValueError): continue
        try: prices[tier] = float(el.get("price"))
        except (TypeError, ValueError): continue
    if not seats: return None
    return {"date": run_date, "seats": seats, "prices": prices, "total_seats": sum(seats.values())}

CAPEX_TAGS = {"arenaExpansion": "Arena expansion"}

def _parse_date(d):
    try: return datetime.strptime(d[:10], "%Y-%m-%d")
    except (TypeError, ValueError): return None

def update_investment_ledger(ledger, economy_root, roster_root, arena_root, run_date, our_team_id):
    name_by_id = {p.get("id"): player_snapshot(p) for p in roster_root.findall(".//player") if p.get("id")}

    seen_txn = {(t["date"], t["playerid"], t["amount"]) for t in ledger["player_transactions"]}
    seen_capex = {(c["date"], c["tag"], c["amount"]) for c in ledger["capex"]}
    seen_matchrev = {m["matchid"] for m in ledger["match_revenue"]}

    for week in economy_root.findall(".//lastWeek") + economy_root.findall(".//thisWeek"):
        for el in week.findall("transfer"):
            pid = el.get("playerid")
            date = el.get("date", "")
            try: amount = float(el.text)
            except (TypeError, ValueError): continue
            key = (date, pid, amount)
            if key in seen_txn: continue
            seen_txn.add(key)
            snap = name_by_id.get(pid)
            ledger["player_transactions"].append({
                "date": date, "playerid": pid, "amount": amount,
                "name": snap["name"] if snap else ledger.get("player_snapshots", {}).get(pid, {}).get("latest", {}).get("name", f"player {pid}"),
            })
        for tag, label in CAPEX_TAGS.items():
            for el in week.findall(tag):
                date = el.get("date", "")
                try: amount = float(el.text)
                except (TypeError, ValueError): continue
                key = (date, tag, amount)
                if key in seen_capex: continue
                seen_capex.add(key)
                ledger["capex"].append({"date": date, "tag": tag, "label": label, "amount": amount})
        for el in week.findall("matchRevenue"):
            matchid = el.get("matchid")
            date = el.get("date", "")
            try: amount = float(el.text)
            except (TypeError, ValueError): continue
            if amount <= 0 or matchid in seen_matchrev: continue
            seen_matchrev.add(matchid)
            ledger["match_revenue"].append({"matchid": matchid, "date": date, "amount": amount})

    # Players this team drafted itself (roster.aspx's teamDrafted == our own
    # id) never show up in economy.aspx's transfer log - there's no purchase
    # to record. Per Tom, they should still appear in the investments table,
    # just at $0 acquisition cost, rather than being silently omitted. Only
    # added once per player (seen_any_buy/seen_drafted guards), so this
    # doesn't re-fire (or overwrite a real purchase) on every run.
    seen_any_buy = {t["playerid"] for t in ledger["player_transactions"] if t["amount"] < 0}
    seen_drafted = {t["playerid"] for t in ledger["player_transactions"] if t.get("acquisition") == "drafted"}
    for pid, snap in name_by_id.items():
        if pid in seen_any_buy or pid in seen_drafted:
            continue
        p = roster_root.find(f".//player[@id='{pid}']")
        if p is None or p.findtext("teamDrafted") != our_team_id:
            continue
        ledger["player_transactions"].append({
            "date": run_date, "playerid": pid, "amount": 0.0,
            "name": snap["name"], "acquisition": "drafted",
        })

    if arena_root is not None:
        snap = arena_snapshot(arena_root, run_date)
        if snap is not None:
            last = ledger["arena_snapshots"][-1] if ledger["arena_snapshots"] else None
            if last is None or last["seats"] != snap["seats"] or last["prices"] != snap["prices"]:
                ledger["arena_snapshots"].append(snap)

    for pid, snap in name_by_id.items():
        entry = ledger["player_snapshots"].setdefault(pid, {})
        if "baseline" not in entry:
            entry["baseline"] = {**snap, "date": run_date}
        entry["latest"] = {**snap, "date": run_date}

    record_weekly_salary_payments(ledger, name_by_id)

    return ledger

def most_recent_monday_reset(now_utc):
    """The economy week - and, per Tom, the actual salary payment - resets
    Monday, at the same 05:00:01 UTC time observed for other weekly resets
    in this report (see most_recent_training_week_start's Friday reset)."""
    days_since_monday = now_utc.weekday()  # Mon=0 ... Sun=6
    candidate = now_utc.replace(hour=5, minute=0, second=1, microsecond=0) - timedelta(days=days_since_monday)
    if candidate > now_utc:
        candidate -= timedelta(days=7)
    return candidate

def record_weekly_salary_payments(ledger, name_by_id):
    """Salaries are paid once a week, on the Monday reset - not continuously
    day by day. Each player gets one ledger["player_snapshots"][pid]
    ["salary_payments"] entry per Monday since their acquisition date (the
    matching buy/drafted transaction in ledger["player_transactions"]),
    recorded at THAT week's observed salary - so a later raise or
    skill-driven salary change doesn't retroactively change what earlier
    weeks are recorded as having cost, unlike a single running total
    recomputed from today's salary would. A week this job didn't run for
    gets backfilled using the salary observed on the run that catches up,
    same limitation any accrual scheme has for a week never actually
    observed - including everything before this ledger started tracking,
    where the acquisition date itself may already be an estimate (see the
    "(estimated)" rows in the investments table)."""
    current_monday = most_recent_monday_reset(datetime.now(timezone.utc)).strftime("%Y-%m-%d")
    for pid, snap in name_by_id.items():
        entry = ledger["player_snapshots"].setdefault(pid, {})
        payments = entry.setdefault("salary_payments", [])
        paid = {p["date"] for p in payments}
        if current_monday in paid:
            continue
        txn = next((t for t in ledger["player_transactions"]
                    if t["playerid"] == pid and (t["amount"] < 0 or t.get("acquisition") == "drafted")), None)
        acquired_dt = _parse_date(txn["date"]) if txn else _parse_date(entry.get("baseline", {}).get("date"))
        current_monday_dt = _parse_date(current_monday)
        if acquired_dt is None or current_monday_dt is None:
            continue
        offset = (7 - acquired_dt.weekday()) % 7  # days from acquisition to the next Monday (0 if already Monday)
        monday = acquired_dt + timedelta(days=offset)
        salary = float(snap.get("salary") or 0)
        while monday <= current_monday_dt:
            mstr = monday.strftime("%Y-%m-%d")
            if mstr not in paid:
                payments.append({"date": mstr, "amount": salary})
                paid.add(mstr)
            monday += timedelta(days=7)

def build_investments_summary(ledger):
    buys = [t for t in ledger["player_transactions"] if t["amount"] < 0 or t.get("acquisition") == "drafted"]
    sells = [t for t in ledger["player_transactions"] if t["amount"] > 0]
    total_buys = sum(-t["amount"] for t in buys)
    total_sells = sum(t["amount"] for t in sells)
    total_capex = sum(-c["amount"] for c in ledger["capex"])
    rows = []
    for t in sorted(buys, key=lambda t: -(-t["amount"])):
        pid = t["playerid"]
        snap = ledger["player_snapshots"].get(pid, {})
        baseline, latest = snap.get("baseline"), snap.get("latest")
        sale = next((s for s in sells if s["playerid"] == pid), None)
        price = -t["amount"] or 0.0  # avoid "-0" from a $0 drafted-player row
        payments = snap.get("salary_payments", [])
        salary_paid = sum(p["amount"] for p in payments)
        tco = price + salary_paid
        # TCO/week: weeks owned = actual Monday salary payments recorded so
        # far (floored at 1), not a fractional day count - matches how
        # salary is really paid (see record_weekly_salary_payments), so a
        # player acquired mid-week doesn't get an inflated rate before their
        # first payday has even happened.
        weeks_owned = max(len(payments), 1)
        tco_per_week = tco / weeks_owned
        skill_now = latest.get("skill_sum") if latest else None
        tco_per_skill = (tco / skill_now) if skill_now else None
        rows.append({"name": t["name"], "playerid": pid, "date": t["date"], "price": price,
                     "salary_paid": salary_paid, "tco": tco, "tco_per_week": tco_per_week,
                     "skill_now": skill_now, "tco_per_skill": tco_per_skill, "baseline": baseline,
                     "latest": latest, "sale": sale, "acquisition": t.get("acquisition")})
    return {"rows": rows, "total_buys": total_buys, "total_sells": total_sells,
            "total_capex": total_capex, "capex": list(ledger["capex"]), "count": len(rows)}

def build_arena_investment_summary(ledger):
    snapshots = sorted(ledger["arena_snapshots"], key=lambda s: s["date"])
    revenue = sorted(ledger["match_revenue"], key=lambda m: m["date"])
    regimes = []
    for i, snap in enumerate(snapshots):
        start = snap["date"]
        end = snapshots[i + 1]["date"] if i + 1 < len(snapshots) else None
        regimes.append({"snapshot": snap, "start": start, "end": end, "matches": []})
    pre_tracking = []
    for m in revenue:
        placed = False
        for regime in reversed(regimes):
            if m["date"][:10] >= regime["start"][:10] and (regime["end"] is None or m["date"][:10] < regime["end"][:10]):
                regime["matches"].append(m)
                placed = True
                break
        if not placed:
            pre_tracking.append(m)
    for regime in regimes:
        ms = regime["matches"]
        regime["count"] = len(ms)
        regime["total"] = sum(m["amount"] for m in ms)
        regime["avg"] = regime["total"] / len(ms) if ms else None
        regime["max_sellout"] = sum(n * regime["snapshot"]["prices"].get(tier, 0)
                                     for tier, n in regime["snapshot"]["seats"].items())
    for i, regime in enumerate(regimes):
        prev_avg = regimes[i - 1]["avg"] if i > 0 else None
        regime["delta_vs_prev"] = (regime["avg"] - prev_avg) if (regime["avg"] is not None and prev_avg is not None) else None
    pre_avg = (sum(m["amount"] for m in pre_tracking) / len(pre_tracking)) if pre_tracking else None
    return {"regimes": regimes, "pre_tracking": pre_tracking, "pre_tracking_avg": pre_avg,
            "pre_tracking_count": len(pre_tracking)}

def extract_data(conn, team_key, teaminfo, roster, economy, schedule, standings, arena, our_team_id, position_minutes, staff_list):
    team = teaminfo.find(".//team")
    data = {
        "now": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "team": {"id": our_team_id, "name": team_name(team) or our_team_id if team is not None else our_team_id,
                 "owner": team.findtext("owner") if team is not None else None,
                 "league": team.find("league").text if team is not None and team.find("league") is not None else None},
        "economy": {"weeks": []}, "schedule": {"upcoming": [], "recent": []},
        "standings": {"found": False, "rows": []}, "roster": {},
    }
    transactions = []
    for label, tag in (("Last week", "lastWeek"), ("This week", "thisWeek")):
        week = economy.find(f".//{tag}")
        if week is None: continue
        initial, final, totals = aggregate_week(week)
        data["economy"]["weeks"].append({"label": label, "initial": initial, "final": final, "totals": totals})
        for item in parse_week_items(week):
            item["week_label"] = label
            transactions.append(item)
    data["economy"]["transactions"] = transactions
    ledger = load_investment_ledger(conn, team_key)
    ledger = update_investment_ledger(ledger, economy, roster, arena, data["now"][:10], our_team_id)
    save_investment_ledger(conn, team_key, ledger)
    data["investments"] = build_investments_summary(ledger)
    data["investments"]["arena"] = build_arena_investment_summary(ledger)
    current_roster_ids = {p.get("id") for p in roster.findall(".//player") if p.get("id")}
    for row in data["investments"]["rows"]:
        row["on_roster"] = row["playerid"] in current_roster_ids
    data["roster_skills"] = build_roster_skills_table(roster)
    data["training_cards"] = build_training_cohort_cards(roster)
    data["training_minutes"] = build_training_minutes_status(position_minutes, roster)
    # Raw per-player, per-position weekly minutes (not just the total already
    # filtered to this team's configured training focus) - exported so the
    # report page's training-position calculator can recompute minutes for
    # *any* position combo the user picks client-side, without a re-fetch.
    data["position_minutes"] = position_minutes
    data["staff"] = staff_list
    data["minutes_vs_money"] = build_minutes_vs_money(position_minutes, roster)
    arena_snap = arena_snapshot(arena, data["now"][:10])
    if arena_snap:
        arena_snap["max_sellout"] = sum(n * arena_snap["prices"].get(tier, 0) for tier, n in arena_snap["seats"].items())
    data["arena_live"] = arena_snap
    matches = schedule.findall(".//match")
    upcoming, recent = [], []
    for m in matches:
        start = m.get("start", "")
        away, home = m.find("awayTeam"), m.find("homeTeam")
        away_name = team_name(away) or "?"
        home_name = team_name(home) or "?"
        away_score = away.findtext("score") if away is not None else None
        home_score = home.findtext("score") if home is not None else None
        row = {"start": start, "away": away_name, "home": home_name}
        if away_score is not None and home_score is not None:
            recent.append({**row, "away_score": away_score, "home_score": home_score})
        else:
            upcoming.append(row)
    data["schedule"]["upcoming"] = sorted(upcoming, key=lambda r: r["start"])[:5]
    data["schedule"]["recent"] = sorted(recent, key=lambda r: r["start"])[-5:]
    for conf in standings.findall(".//conference"):
        teams = conf.findall("team")
        if any(t.get("id") == our_team_id for t in teams):
            for i, t in enumerate(teams, start=1):
                try: diff = int(t.findtext("pf")) - int(t.findtext("pa"))
                except (TypeError, ValueError): diff = None
                data["standings"]["rows"].append({"rank": i, "name": team_name(t), "wins": t.findtext("wins"),
                                                     "losses": t.findtext("losses"), "diff": diff,
                                                     "is_us": t.get("id") == our_team_id})
            data["standings"]["found"] = True
            break
    division_rows = []
    for conf in standings.findall(".//conference"):
        for t in conf.findall("team"):
            try: diff = int(t.findtext("pf")) - int(t.findtext("pa"))
            except (TypeError, ValueError): diff = None
            division_rows.append({"name": team_name(t), "wins": t.findtext("wins"), "losses": t.findtext("losses"),
                                   "diff": diff, "is_us": t.get("id") == our_team_id})
    division_rows_ranked = sorted((r for r in division_rows if r["diff"] is not None), key=lambda r: -r["diff"])
    for i, r in enumerate(division_rows_ranked, start=1):
        r["diff_rank"] = i
    data["division_rows"] = division_rows_ranked
    current = parse_roster(roster)
    data["roster"]["size"] = len(current)
    prev_root = load_prev_roster_root(conn, team_key)
    if prev_root is not None:
        prev = parse_roster(prev_root)
        data["roster"]["baseline"] = False
        data["roster"]["added"] = [current[pid]["name"] for pid in current if pid not in prev]
        data["roster"]["removed"] = [prev[pid]["name"] for pid in prev if pid not in current]
    else:
        data["roster"]["baseline"] = True
        data["roster"]["added"] = []
        data["roster"]["removed"] = []
    return data

def sorted_totals(totals):
    return [(cat, amt) for cat, amt in sorted(totals.items(), key=lambda kv: -abs(kv[1])) if amt]

def render_text(data):
    lines = [f"BuzzerBeater Weekly Report - {data['now']}", "=" * 40, "", "TEAM INFO"]
    team = data["team"]
    lines.append(f"  Team: {team['name']}")
    if team["owner"]: lines.append(f"  Owner: {team['owner']}")
    if team["league"]: lines.append(f"  League: {team['league']}")
    lines += ["", "FINANCES"]
    if data["economy"]["weeks"]:
        for week in data["economy"]["weeks"]:
            lines.append(f"  {week['label']}: {money(week['initial'])} -> {money(week['final'])}")
            for cat, amt in sorted_totals(week["totals"]):
                lines.append(f"    {humanize(cat)}: {signed_money(amt)}")
    else: lines.append("  (no economy data found)")
    lines += ["", "SCHEDULE"]
    sched = data["schedule"]
    if sched["upcoming"] or sched["recent"]:
        if sched["upcoming"]:
            lines.append("  Upcoming:")
            for r in sched["upcoming"]: lines.append(f"    {r['start']}  {r['away']} @ {r['home']}")
        if sched["recent"]:
            lines.append("  Recent results:")
            for r in sched["recent"]: lines.append(f"    {r['start']}  {r['away']} @ {r['home']}  ({r['away_score']}-{r['home_score']})")
    else: lines.append("  (no matches found)")
    lines += ["", "STANDINGS"]
    if data["standings"]["found"]:
        lines.append("  Standings (your conference):")
        for row in data["standings"]["rows"]:
            marker = "  <-- you" if row["is_us"] else ""
            lines.append(f"    {row['rank']}. {row['name']} ({row['wins']}-{row['losses']}){marker}")
    else: lines.append("  (could not locate your team in the standings response)")
    lines += ["", "ROSTER CHANGES"]
    roster = data["roster"]
    lines.append(f"  Roster size: {roster['size']} players")
    if roster["baseline"]: lines.append("  (no previous roster cached - this is the baseline run)")
    else:
        if roster["added"]: lines.append(f"  New on roster: {', '.join(roster['added'])}")
        if roster["removed"]: lines.append(f"  No longer on roster: {', '.join(roster['removed'])}")
        if not (roster["added"] or roster["removed"]): lines.append("  No roster changes since last run.")
    lines += ["", TRAINING_REMINDER]
    return "\n".join(lines)

AUTO_MARKERS = ["META", "OVERVIEW_STATS", "RECOMMENDATIONS", "INVESTMENTS", "ROSTER_SKILLS", "ROSTER_BY_POSITION",
                "TRAINING_CARDS", "TRANSACTION_LEDGER", "SCHEDULE_STANDINGS", "FINANCE_WEEKLY", "ROSTER_CHANGES",
                "STAFF", "MINUTES_VS_MONEY", "ARENA_GLANCE", "ARENA_PRICE_BARS", "DIVISION_STANDINGS"]

def esc(v):
    return html.escape(str(v)) if v is not None else ""

def money_html(v):
    try: v = float(v)
    except (TypeError, ValueError): return esc(v)
    if v == 0: v = 0.0  # avoid "-0" from formatting a -0.0 (e.g. a $0 drafted-player row)
    return f"-${abs(v):,.0f}" if v < 0 else f"${v:,.0f}"

def finance_card_html(week):
    rows = sorted_totals(week["totals"])
    body = "".join(f'<tr><td>{esc(humanize(cat))}</td><td class="num {"credit" if amt >= 0 else "debit"}">'
                    f'{signed_money(amt).replace("+", "+$").replace("-", "-$")}</td></tr>' for cat, amt in rows)
    try:
        net = float(week["final"]) - float(week["initial"])
        net_str = f'{"+$" if net >= 0 else "-$"}{abs(net):,.0f}'
        net_class = "credit" if net >= 0 else "debit"
    except (TypeError, ValueError): net_str, net_class = "N/A", ""
    return (f'<div class="card"><div class="eyebrow" style="margin-bottom:10px;">{esc(week["label"])} · '
            f'{money_html(week["initial"])} &rarr; {money_html(week["final"])}</div><table style="min-width:0;">'
            f'<tbody>{body if body else "<tr><td colspan=2 class=sub>no transactions</td></tr>"}'
            f'<tr class="total"><td>Net change</td><td class="num {net_class}">{net_str}</td></tr></tbody></table></div>')

def auto_transaction_ledger_html(data):
    weeks_by_label = {w["label"]: w for w in data["economy"]["weeks"]}
    txns_by_label = {}
    for t in data["economy"]["transactions"]:
        txns_by_label.setdefault(t["week_label"], []).append(t)

    blocks = []
    for label in ("This week", "Last week"):
        week = weeks_by_label.get(label)
        if not week:
            continue
        items = txns_by_label.get(label, [])
        rows = "".join(
            '<tr><td>' + esc(t["date"][:10]) + '</td><td>' + esc(humanize(t["tag"])) + '</td>'
            '<td class="num ' + ("credit" if t["amount"] >= 0 else "debit") + '">'
            + signed_money(t["amount"]).replace("+", "+$").replace("-", "-$") + '</td></tr>'
            for t in reversed(items)
        )
        variance_html = ""
        try:
            week_change = float(week["final"]) - float(week["initial"])
            item_sum = sum(t["amount"] for t in items)
            variance = week_change - item_sum
        except (TypeError, ValueError):
            variance = None
        if variance is not None and abs(variance) >= 1:
            variance_html = (
                '<p class="block-note" style="margin-top:8px;">'
                '<span class="tag tag-rec">[Inference]</span> Itemized rows above sum to '
                + signed_money(item_sum).replace("+", "+$").replace("-", "-$") + ', but the official '
                'opening/closing balance implies ' + signed_money(week_change).replace("+", "+$").replace("-", "-$")
                + ' &mdash; a ' + money_html(abs(variance)) + ' gap the API doesn\'t break into any category. '
                'Worth checking the in-game ledger directly if this matters.</p>'
            )
        blocks.append(
            '<div class="card" style="margin-bottom:16px;">'
            '<div class="eyebrow" style="margin-bottom:8px;">' + esc(label) + ' &middot; ' + money_html(week['initial']) + ' &rarr; ' + money_html(week['final']) + '</div>'
            '<div class="tbl-scroll"><table><thead><tr><th>Date</th><th>Transaction</th><th class="num">Amount</th></tr></thead>'
            '<tbody>' + (rows if rows else '<tr><td colspan="3" class="sub">no itemized transactions</td></tr>') + '</tbody></table></div>'
            + variance_html + '</div>'
        )
    return "".join(blocks) if blocks else '<p class="block-note">No economy data returned.</p>'


def auto_meta_html(data):
    return f'<span class="auto-badge">Auto-updated</span> {esc(data["now"])}'

def auto_overview_stats_html(data):
    weeks = data["economy"]["weeks"]
    this_week = next((w for w in weeks if w["label"] == "This week"), None)
    cash_now = this_week["final"] if this_week else None
    try: cash_val = float(cash_now)
    except (TypeError, ValueError): cash_val = None
    try: net_change = float(this_week["final"]) - float(this_week["initial"]) if this_week else None
    except (TypeError, ValueError): net_change = None
    record_row = next((r for r in data["standings"]["rows"] if r["is_us"]), None)
    total_teams = len(data["standings"]["rows"])
    next_game = data["schedule"]["upcoming"][0] if data["schedule"]["upcoming"] else None
    cash_class = "neg" if (cash_val is not None and cash_val < 0) else ""
    net_class = "pos" if (net_change is not None and net_change >= 0) else "neg"
    net_str = signed_money(net_change).replace("+", "+$").replace("-", "-$") if net_change is not None else "N/A"
    record_str = f"{record_row['wins']}-{record_row['losses']}" if record_row else "N/A"
    record_foot = f"rank {record_row['rank']} of {total_teams} in conference" if record_row else "not found"
    next_game_str = f"{esc(next_game['away'])} @ {esc(next_game['home'])}" if next_game else "none scheduled"
    next_game_foot = next_game["start"][:10] if next_game else ""
    return (f'<div class="stat-row" style="margin-top:12px;">'
            f'<div class="stat-card {"alert" if cash_class == "neg" else ""}"><div class="label">Cash on hand</div>'
            f'<div class="value {cash_class}">{money_html(cash_now) if cash_now is not None else "N/A"}</div>'
            f'<div class="foot">as of {esc(data["now"])}</div></div>'
            f'<div class="stat-card"><div class="label">This week\'s net change</div>'
            f'<div class="value {net_class}">{net_str}</div><div class="foot">all confirmed income &amp; expenses</div></div>'
            f'<div class="stat-card"><div class="label">League record</div><div class="value">{esc(record_str)}</div>'
            f'<div class="foot">{esc(record_foot)}</div></div>'
            f'<div class="stat-card"><div class="label">Next game</div>'
            f'<div class="value" style="font-size:16px;">{next_game_str}</div><div class="foot">{esc(next_game_foot)}</div></div></div>')

def auto_recommendations_html(data):
    weeks = data["economy"]["weeks"]
    this_week = next((w for w in weeks if w["label"] == "This week"), None)
    cash_now = this_week["final"] if this_week else None
    try: cash_val = float(cash_now)
    except (TypeError, ValueError): cash_val = None
    try: net_change = float(this_week["final"]) - float(this_week["initial"]) if this_week else None
    except (TypeError, ValueError): net_change = None
    weekly_expenses = sum(-v for v in this_week["totals"].values() if v < 0) if this_week else None
    items = []
    if cash_val is not None and cash_val < 0:
        items.append((True, "Cash balance is negative", "Current balance is <b class=\"mono\" style=\"color:var(--negative)\">" + money_html(cash_now) + "</b>. Hold off on any new spending — bids, signings, staff changes — until this recovers."))
    elif cash_val is not None and weekly_expenses and cash_val < weekly_expenses:
        items.append((True, "Cash reserves are thin", "Cash on hand (<b class=\"mono\">" + money_html(cash_now) + "</b>) is less than one week's confirmed expenses (<b class=\"mono\">" + money_html(weekly_expenses) + "</b>). Worth watching before any new commitment."))
    if net_change is not None:
        if net_change < 0:
            items.append((False, "Expenses outpaced income this week", "Net change: <b class=\"mono\" style=\"color:var(--negative)\">-" + money_html(abs(net_change)) + "</b>, balance now " + money_html(cash_now) + "."))
        else:
            items.append((False, "Cash position improved this week", "Net change: <b class=\"mono\" style=\"color:var(--positive)\">+" + money_html(net_change) + "</b>, balance now " + money_html(cash_now) + "."))
    next_game = data["schedule"]["upcoming"][0] if data["schedule"]["upcoming"] else None
    if next_game:
        date = next_game["start"][:10]
        is_home = next_game["home"] == data["team"]["name"]
        if is_home:
            items.append((False, "Home game coming up", esc(next_game["away"]) + " @ " + esc(next_game["home"]) + " on " + date + " — home gate revenue should help this week's finances."))
        else:
            items.append((False, "No home gate this week", "Next game (" + date + ") is away at " + esc(next_game["away"]) + " — confirmed revenue stays limited to TV until the next home date."))
    roster = data["roster"]
    if not roster["baseline"]:
        if roster["added"]:
            items.append((False, "New roster additions", "Newly listed: " + esc(", ".join(roster["added"])) + ". Worth watching their early minutes as they integrate."))
        if roster["removed"]:
            items.append((False, "Players left the roster", "No longer listed: " + esc(", ".join(roster["removed"])) + "."))
    record_row = next((r for r in data["standings"]["rows"] if r["is_us"]), None)
    total_teams = len(data["standings"]["rows"])
    if record_row and total_teams:
        if record_row["rank"] > total_teams / 2:
            items.append((False, "Standings still rough", esc(record_row["wins"]) + "-" + esc(record_row["losses"]) + " record, " + str(record_row["rank"]) + " of " + str(total_teams) + " in your conference."))
    if not items:
        items.append((False, "No urgent flags from the numbers", "Cash, schedule, and roster all look steady based on today's data."))
    alert_html = ""
    if items[0][0]:
        alert_html = '<div class="alert-card"><div class="eyebrow">' + esc(items[0][1]) + '</div><p><span class="tag tag-calc">Calculated</span>&nbsp; ' + items[0][2] + '</p></div>'
    rec_html = "".join('<div class="rec' + (' urgent' if urgent else '') + '"><div class="idx">' + str(i) + '</div><div><h3>' + esc(title) + '</h3><p><span class="tag tag-calc">Calculated</span> ' + body + '</p></div></div>' for i, (urgent, title, body) in enumerate(items, start=1))
    return alert_html + '<section class="block" style="margin-top:8px;"><div class="block-head"><h2>What I\'d look at next</h2><span class="auto-badge">Auto-updated daily</span></div><div class="rec-list">' + rec_html + '</div></section>'


def auto_schedule_standings_html(data):
    def sched_rows(entries, with_score):
        if not entries: return '<tr><td colspan="{}" class="sub">none</td></tr>'.format(3 if with_score else 2)
        out = []
        for r in entries:
            if with_score:
                out.append(f'<tr><td>{r["start"][:10]}</td><td>{esc(r["away"])} @ {esc(r["home"])}</td>'
                            f'<td class="num">{esc(r["away_score"])}-{esc(r["home_score"])}</td></tr>')
            else:
                out.append(f'<tr><td>{r["start"][:16].replace("T", " ")}</td><td>{esc(r["away"])} @ {esc(r["home"])}</td></tr>')
        return "".join(out)
    schedule_html = (f'<div class="two-col"><div><div class="eyebrow" style="margin-bottom:10px;">Upcoming</div>'
                      f'<div class="tbl-scroll"><table style="min-width:0;"><tbody>{sched_rows(data["schedule"]["upcoming"], False)}</tbody></table></div></div>'
                      f'<div><div class="eyebrow" style="margin-bottom:10px;">Recent results</div>'
                      f'<div class="tbl-scroll"><table style="min-width:0;"><tbody>{sched_rows(data["schedule"]["recent"], True)}</tbody></table></div></div></div>')
    if data["standings"]["found"]:
        rows_html = "".join(f'<tr class="{"us" if r["is_us"] else ""}"><td>{r["rank"]}</td><td>{esc(r["name"])}'
                             f'{" <span class=sub>(you)</span>" if r["is_us"] else ""}</td>'
                             f'<td class="num">{esc(r["wins"])}-{esc(r["losses"])}</td></tr>' for r in data["standings"]["rows"])
    else:
        rows_html = '<tr><td colspan="3" class="sub">could not locate your team in the standings response</td></tr>'
    standings_html = (f'<div class="tbl-scroll" style="margin-top:20px;"><table><thead><tr><th>#</th><th>Team</th>'
                       f'<th class="num">W-L</th></tr></thead><tbody>{rows_html}</tbody></table></div>')
    return schedule_html + standings_html

def auto_finance_weekly_html(data):
    weeks = data["economy"]["weeks"]
    this_week = next((w for w in weeks if w["label"] == "This week"), None)
    last_week = next((w for w in weeks if w["label"] == "Last week"), None)
    if not (this_week or last_week): return '<p class="block-note">No economy data returned.</p>'
    cols = [finance_card_html(w) for w in ([this_week, last_week] if this_week and last_week else weeks)]
    return f'<div class="two-col">{"".join(cols)}</div>'

def auto_roster_changes_html(data):
    roster = data["roster"]
    if roster["baseline"]: note = "No previous roster cached — this is the baseline run."
    elif roster["added"] or roster["removed"]:
        parts = []
        if roster["added"]: parts.append(f'<p style="margin:0 0 6px;"><b>New on roster:</b> {esc(", ".join(roster["added"]))}</p>')
        if roster["removed"]: parts.append(f'<p style="margin:0;"><b>No longer on roster:</b> {esc(", ".join(roster["removed"]))}</p>')
        note = "".join(parts)
    else: note = "No roster changes since last run."
    return (f'<div class="card"><div class="eyebrow" style="margin-bottom:8px;">{roster["size"]} players on roster</div>'
            f'<div class="block-note" style="margin:0;">{note}</div></div>')

def auto_division_standings_html(data):
    rows = data["division_rows"]
    us = next((r for r in rows if r["is_us"]), None)
    if not us:
        return '<p class="block-note">Could not locate this team in the standings response.</p>'
    total = len(rows)
    next_worst = next((r for r in reversed(rows) if not r["is_us"]), None)
    is_worst = us["diff_rank"] == total
    worst_str = (f' — worst in the {total}-team league (next-worst is {esc(next_worst["name"])} at {next_worst["diff"]:+d})'
                 if is_worst and next_worst else f' — {ordinal(us["diff_rank"])} of {total} teams by point differential')
    return (
        f'<p class="block-note" style="margin-top:8px;"><span class="tag tag-official">Official · standings.aspx, live</span>&nbsp; '
        f'{esc(data["team"]["name"])} is <b style="color:var(--ink)">{esc(us["wins"])}–{esc(us["losses"])}</b> with a '
        f'<b style="color:var(--negative)">{us["diff"]:+d}</b> point differential{worst_str}.</p>'
    )

def ordinal(n):
    if 10 <= n % 100 <= 20: suffix = "th"
    else: suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"

def auto_staff_html(data):
    staff = data["staff"]
    if not staff:
        return '<p class="block-note">No staff data returned.</p>'
    cards = ""
    for s in staff:
        level_cell = f'{esc(s["level_word"])}' if s["level_word"] else (esc(s["level"]) if s["level"] is not None else "—")
        specialty_row = ""
        if s["role"] == "Trainer":
            spec = "none" if s["specialty"] in (None, "0") else s["specialty"]
            specialty_row = f'<div class="row"><span>Specialty</span><b>{esc(spec)}</b></div>'
        cards += (
            f'<div class="staff-card"><div class="role">{esc(s["role"])}</div>'
            f'<div class="who">{esc(s["name"]) or "—"}</div>'
            f'<div class="row"><span>Skill</span><b>{level_cell}</b></div>'
            f'{specialty_row}'
            f'<div class="row"><span>Weekly cost</span><b>{money_html(s["salary"])}</b></div></div>'
        )
    return f'<div class="staff-grid">{cards}</div>'

def auto_minutes_vs_money_html(data):
    rows = data["minutes_vs_money"]
    if not rows:
        return '<p class="block-note">No minutes data returned.</p>'
    bars = ""
    max_minutes = max((r["minutes"] for r in rows), default=1) or 1
    for r in rows:
        pct = min(100, round(100 * r["minutes"] / max_minutes)) if max_minutes else 0
        fill_class = "full" if r["minutes"] >= 45 else ""
        bars += (
            f'<div class="bar-row"><span class="lbl">{esc(r["name"])} <span class="sub">{money_html(r["salary"])}/wk, #{r["salary_rank"]} salary</span></span>'
            f'<div class="bar-track"><div class="bar-fill {fill_class}" style="width:{pct}%"></div></div><span class="val">{r["minutes"]} min</span></div>'
        )
    return (
        f'<div class="card">{bars}'
        '<p class="block-note" style="margin-top:14px;"><span class="tag tag-calc">Calculated</span> Live total minutes (any position) this training week vs. each player\'s salary, sorted by salary — a quick check on whether the highest earners are actually playing. This resets on the Friday training-week boundary, same as the training-threshold minutes elsewhere in this report.</p>'
        '</div>'
    )

def auto_arena_glance_html(data):
    snap = data.get("arena_live")
    if not snap:
        return '<p class="block-note">No arena data returned.</p>'
    total_seats = snap["total_seats"]
    prices = snap["prices"]
    price_str = " / ".join(f'${prices.get(tier, 0):,.0f}' for tier in ARENA_SEAT_TIERS)
    return (
        f'<p class="block-note">{total_seats:,}-seat arena today. Ticket prices ({price_str}, Bleachers/Lower Tier/Courtside/Luxury). '
        f'Full-house ceiling at these prices: <b style="color:var(--ink)">{money_html(snap["max_sellout"])}</b>.</p>'
    )

def auto_arena_price_bars_html(data):
    snap = data.get("arena_live")
    if not snap:
        return '<p class="block-note">No arena data returned.</p>'
    prices = snap["prices"]
    # Max caps are fixed game-rule ceilings per tier, not exposed by arena.aspx.
    max_caps = {"bleachers": 20, "lowerTier": 70, "courtside": 200, "luxury": 1600}
    labels = {"bleachers": "Bleachers", "lowerTier": "Lower Tier", "courtside": "Courtside", "luxury": "Luxury Boxes"}
    bars = ""
    for tier in ARENA_SEAT_TIERS:
        price, cap = prices.get(tier, 0), max_caps[tier]
        pct = min(100, round(100 * price / cap)) if cap else 0
        bars += (
            f'<div class="price-bar"><span class="lbl">{labels[tier]}</span><div class="price-track">'
            f'<div class="price-fill" style="width:{pct}%"></div></div>'
            f'<div class="price-range">${price:,.0f} <span style="color:var(--ink-faint)">/ max ${cap:,.0f}</span></div></div>'
        )
    return bars

def auto_investments_html(data):
    inv = data["investments"]
    rows = inv["rows"]
    total_capex = inv["total_capex"]
    total_invested = inv["total_buys"] + total_capex

    stat_row = (
        '<div class="stat-row" style="margin-top:12px;">'
        f'<div class="stat-card"><div class="label">Total capital deployed</div><div class="value">{money_html(-total_invested)}</div>'
        f'<div class="foot">tracked since {esc(min((r["date"][:10] for r in rows), default="—"))}</div></div>'
        f'<div class="stat-card"><div class="label">Player acquisitions</div><div class="value">{money_html(-inv["total_buys"])}</div>'
        f'<div class="foot">{inv["count"]} purchase{"s" if inv["count"] != 1 else ""} tracked</div></div>'
        f'<div class="stat-card"><div class="label">Facility &amp; capex spend</div><div class="value">{money_html(-total_capex)}</div>'
        f'<div class="foot">{len(inv["capex"])} item{"s" if len(inv["capex"]) != 1 else ""} tracked</div></div>'
        f'<div class="stat-card"><div class="label">Realized from sales</div><div class="value{" pos" if inv["total_sells"] else ""}">{money_html(inv["total_sells"]) if inv["total_sells"] else "$0"}</div>'
        f'<div class="foot">{"since tracking began" if inv["total_sells"] else "no sales recorded yet"}</div></div></div>'
    )

    if rows:
        body = ""
        for r in rows:
            if r["sale"]:
                gain = r["sale"]["amount"] - r["tco"]
                sale_cell = (f'{money_html(r["sale"]["amount"])} <span style="color:var({"--positive" if gain >= 0 else "--negative"})">'
                             f'({"+" if gain >= 0 else ""}{money_html(gain)} vs TCO)</span>')
                status = (f'<span class="tag" style="background:var({"--positive-soft" if gain >= 0 else "--negative-soft"}); '
                          f'color:var({"--positive" if gain >= 0 else "--negative"});">Sold {esc(r["sale"]["date"][:10])}</span>')
            elif r["on_roster"]:
                sale_cell = '<span class="sub">still held</span>'
                status = '<span class="tag tag-official" style="background:var(--positive-soft); color:var(--positive);">On roster</span>'
            else:
                sale_cell = '<span class="sub">still held</span>'
                status = '<span class="tag" style="background:var(--warning-soft); color:var(--warning);">Off roster (release/trade, no sale recorded)</span>'
            skill_cell = f'{r["skill_now"]:g}' if r["skill_now"] is not None else "—"
            tco_per_skill_cell = f'${r["tco_per_skill"]:,.0f}' if r["tco_per_skill"] else "—"
            acquired_cell = esc(r["date"][:10])
            if r.get("acquisition") == "drafted":
                acquired_cell += ' <span class="sub" title="Drafted/home-grown - BuzzerBeater has no official transfer record for these, so this date is the best available estimate (a manually-supplied date, or failing that the day this ledger first tracked them), not an official acquisition date.">(estimated)</span>'
            body += (
                f'<tr><td class="name-cell">{esc(r["name"])}</td><td>{acquired_cell}</td>'
                f'<td class="num">{money_html(r["price"])}</td>'
                f'<td class="num">{money_html(r["salary_paid"])}</td>'
                f'<td class="num">{money_html(r["tco"])}</td>'
                f'<td class="num">{money_html(r["tco_per_week"])}</td>'
                f'<td class="num">{skill_cell}</td>'
                f'<td class="num">{tco_per_skill_cell}</td>'
                f'<td class="num">{sale_cell}</td><td>{status}</td></tr>'
            )
        table = (
            '<div class="tbl-scroll"><table><thead><tr><th>Player</th><th>Acquired</th><th class="num">Price paid</th>'
            '<th class="num">Salary paid since</th><th class="num">TCO</th><th class="num">TCO / week</th>'
            '<th class="num">Skill total now (TSP proxy)</th>'
            '<th class="num">TCO / skill pt</th><th class="num">Sale price</th><th>Status</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>'
            '<p class="block-note" style="margin-top:10px;"><span class="tag tag-calc">Calculated</span> TCO = price paid + salary paid while owned. '
            'Salary is paid weekly, not continuously - one payment per Monday reset since acquisition, each recorded at that week\'s own salary (from the official API), so a later raise or skill-driven salary change doesn\'t retroactively change what earlier weeks cost. '
            'TCO/week divides TCO by the number of weekly payments recorded so far (floored at 1) - a run-rate figure comparable across players regardless of how long each has been tracked. '
            '<span class="tag tag-rec">[Inference]</span> "Skill total" is a self-computed sum of the 12 rated skills from the official API, standing in for Buzzer Manager\'s '
            'proprietary TSP figure. Treat skill total as a progress signal, not a market valuation. '
            '<span class="tag tag-rec">[Inference]</span> Rows marked "(estimated)" are drafted/home-grown players with no purchase to date from - salary-paid and TCO accrue from a manually-supplied acquisition date where one is known '
            '(e.g. a franchise takeover date), otherwise from the day this ledger first tracked them, so treat those figures as approximate rather than an official record.</p>'
        )
    else:
        table = '<p class="block-note">No player purchases captured in the ledger yet.</p>'

    if inv["capex"]:
        capex_rows = "".join(
            f'<tr><td>{esc(c["date"][:10])}</td><td>{esc(c["label"])}</td><td class="num debit">{money_html(c["amount"])}</td></tr>'
            for c in sorted(inv["capex"], key=lambda c: c["date"], reverse=True)
        )
        capex_html = (
            f'<div class="card" style="margin-top:16px;"><div class="eyebrow" style="margin-bottom:10px;">Facility &amp; capex spend</div>'
            f'<div class="tbl-scroll" style="box-shadow:none;"><table style="min-width:0;">'
            f'<thead><tr><th>Date</th><th>Item</th><th class="num">Amount</th></tr></thead><tbody>{capex_rows}</tbody></table></div></div>'
        )
    else:
        capex_html = ""

    return stat_row + '<div style="margin-top:16px;">' + table + '</div>' + capex_html + auto_arena_revenue_html(data)

def auto_arena_revenue_html(data):
    arena = data["investments"]["arena"]
    regimes, pre = arena["regimes"], arena["pre_tracking"]

    pre_html = ""
    if pre:
        pre_html = (
            '<div class="price-bar" style="grid-template-columns: 1fr 140px;">'
            f'<span class="lbl">Before automated tracking began <span class="sub">({len(pre)} home date{"s" if len(pre) != 1 else ""}, revenue only, capacity/prices at the time unknown)</span></span>'
            f'<span class="val mono">{money_html(arena["pre_tracking_avg"])}/date</span></div>'
        )

    regime_html = ""
    if regimes:
        rows = ""
        for r in regimes:
            snap = r["snapshot"]
            seats_str = f'{snap["total_seats"]:,} seats'
            window = f'{esc(r["start"][:10])} &rarr; {esc(r["end"][:10]) if r["end"] else "now"}'
            avg_str = money_html(r["avg"]) if r["avg"] is not None else "<span class=\"sub\">no home dates yet</span>"
            delta_str = ""
            if r["delta_vs_prev"] is not None:
                d = r["delta_vs_prev"]
                delta_str = f' <span style="color:var({"--positive" if d >= 0 else "--negative"})">({"+" if d >= 0 else ""}{money_html(d)} vs prior capacity)</span>'
            rows += (
                f'<tr><td>{window}</td><td class="num">{seats_str}</td><td class="num">{r["count"]}</td>'
                f'<td class="num">{avg_str}{delta_str}</td><td class="num">{money_html(r["max_sellout"])}</td></tr>'
            )
        regime_html = (
            '<div class="tbl-scroll" style="margin-top:10px;"><table style="min-width:0;">'
            '<thead><tr><th>Capacity window</th><th class="num">Seats</th><th class="num">Home dates</th>'
            '<th class="num">Avg. gate revenue</th><th class="num">Full-house ceiling</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>'
        )
    else:
        regime_html = '<p class="block-note" style="margin-top:10px;">No arena capacity snapshot recorded yet.</p>'

    return (
        '<div class="card" style="margin-top:16px;">'
        '<div class="eyebrow" style="margin-bottom:10px;">Ticket revenue tracked since each expansion</div>'
        '<p class="block-note" style="margin:0 0 4px;"><span class="tag tag-official">Official · economy.aspx + arena.aspx, live each run</span>&nbsp; '
        'Every home game\'s actual gate revenue, bucketed by which capacity/price regime was in effect that night. A new regime opens automatically the moment arena.aspx reports a change in seat counts or prices.</p>'
        + pre_html + regime_html +
        '<p class="block-note" style="margin-top:10px;"><span class="tag tag-rec">[Inference]</span> Capacity regimes are detected from this ledger\'s own snapshots. "Full-house ceiling" is every seat at that regime\'s prices, sold out.</p>'
        '</div>'
    )

def auto_roster_skills_html(data):
    rs = data["roster_skills"]
    rows = rs["rows"]
    if not rows:
        return '<p class="block-note">No roster data returned.</p>'
    group_header_cells = "".join(
        f'<th colspan="{len(tags)}" class="group-header{" grp-start" if gi else ""}">{esc(group_name)}</th>'
        for gi, (group_name, tags) in enumerate(SKILL_GROUPS)
    )
    skill_header_cells = "".join(
        f'<th class="num{" grp-start" if (gi and ti == 0) else ""}">{esc(label)}</th>'
        for gi, (_, tags) in enumerate(SKILL_GROUPS) for ti, (_, label) in enumerate(tags)
    )
    body = ""
    for r in sorted(rows, key=lambda r: r["name"]):
        cells = ""
        for gi, (_, tags) in enumerate(SKILL_GROUPS):
            for ti, (tag, _) in enumerate(tags):
                cell = r[tag]
                label = skill_number_only(cell["value"]) if cell["value"] is not None else "—"
                pop = f' <span style="color:var(--positive)">{esc(cell["pop"])}</span>' if cell.get("pop") else ""
                grp_class = " grp-start" if (gi and ti == 0) else ""
                cells += f'<td class="num{grp_class}">{label}{pop}</td>'
        # Train?/Minutes/Status are placeholders, deliberately left for the
        # page's own JS to fill in after load - see ssbbApplyTrainingColumns
        # in docs/sharpshooters/index.html. This table is otherwise plain
        # server-rendered HTML with no knowledge of which training combo is
        # currently selected (that's a client-only, interactive choice), so
        # data-playerid is what lets the JS find the right row without
        # re-deriving or duplicating any of the skill-rendering logic above.
        body += (f'<tr data-playerid="{esc(r["playerid"])}"><td class="name-cell">{esc(r["name"])}</td><td>{esc(r["position"])}</td>'
                 f'<td class="num">{esc(r["age"])}</td><td class="num">{potential_label(r["potential"])}</td>'
                 f'<td class="js-train-cell">—</td>{cells}'
                 f'<td class="num js-minutes-cell">—</td><td class="js-status-cell">—</td></tr>')
    table = (
        '<div class="tbl-scroll"><table class="freeze-first-col" style="min-width:1200px;">'
        '<thead>'
        f'<tr><th rowspan="2">Player</th><th rowspan="2">Pos</th><th rowspan="2" class="num">Age</th><th rowspan="2" class="num">Potential</th>'
        f'<th rowspan="2">Train?</th>{group_header_cells}'
        '<th rowspan="2" class="num">Minutes / threshold</th><th rowspan="2">Status</th></tr>'
        f'<tr>{skill_header_cells}</tr>'
        '</thead>'
        f'<tbody>{body}</tbody></table></div>'
    )
    gap_note = (
        '<p class="block-note" style="margin-top:10px;"><span class="tag tag-official">Official · Game Manual, rules.aspx?nav=Nomenclature + contentbox.css</span> '
        'Word labels (on hover) are the manual\'s verbatim 1&ndash;20 adjective scale; colors are the exact hex values from the game\'s own stylesheet (.lev1&ndash;.lev20). '
        'Dark-mode colors are lightness-boosted for legibility, since the game has no dark theme of its own to match. '
        '<span class="tag tag-calc">Calculated</span> The trailing Train?/Minutes/Status columns are filled in live by this page\'s own script from whichever training combo is currently selected above (see the training minutes calculator, Training Strategy tab) - not part of the daily snapshot.</p>'
    )
    return (
        '<p class="block-note">Same 12 skills, word scale, and color coding the game itself shows on a player card, pulled live from the official API for the full roster — grouped OSP/ISP/Other and shown as numbers only (hover a value for its word) to keep the table scannable.</p>'
        + table + gap_note
    )

# Option 3 from the roster-readability discussion: split into narrower,
# position-specific tables so each only shows the skills that matter for that
# group's training doctrine - shorter tables, no horizontal scroll.
POSITION_GROUPS = [
    ("Guards", ["PG", "SG"], [
        ("jumpShot", "Jump Shot"), ("range", "Jump Range"), ("outsideDef", "Outside Def."),
        ("handling", "Handling"), ("passing", "Passing"), ("insideShot", "Inside Shot"),
        ("rebound", "Rebounding"), ("stamina", "Stamina"), ("freeThrow", "Free Throw"),
    ]),
    ("Forwards / Centers", ["SF", "PF", "C"], [
        ("insideShot", "Inside Shot"), ("insideDef", "Inside Def."), ("rebound", "Rebounding"),
        ("block", "Shot Blocking"), ("passing", "Passing"), ("driving", "Driving"),
        ("jumpShot", "Jump Shot"), ("outsideDef", "Outside Def."), ("stamina", "Stamina"), ("freeThrow", "Free Throw"),
    ]),
]

def auto_roster_by_position_html(data):
    rs = data["roster_skills"]
    rows = rs["rows"]
    if not rows:
        return '<p class="block-note">No roster data returned.</p>'
    sections = []
    for group_name, positions, cols in POSITION_GROUPS:
        group_rows = sorted((r for r in rows if r["position"] in positions), key=lambda r: r["name"])
        header_cells = "".join(f'<th class="num">{esc(label)}</th>' for _, label in cols)
        if group_rows:
            body = ""
            for r in group_rows:
                cells = ""
                for tag, _ in cols:
                    cell = r[tag]
                    label = skill_number_only(cell["value"]) if cell["value"] is not None else "—"
                    pop = f' <span style="color:var(--positive)">{esc(cell["pop"])}</span>' if cell.get("pop") else ""
                    cells += f'<td class="num">{label}{pop}</td>'
                body += (f'<tr><td class="name-cell">{esc(r["name"])}</td><td>{esc(r["position"])}</td>'
                         f'<td class="num">{esc(r["age"])}</td><td class="num">{potential_label(r["potential"])}</td>{cells}</tr>')
        else:
            body = f'<tr><td colspan="{4 + len(cols)}" class="sub">No players on roster at this position right now.</td></tr>'
        table = (
            '<div class="tbl-scroll"><table>'
            f'<thead><tr><th>Player</th><th>Pos</th><th class="num">Age</th><th class="num">Potential</th>{header_cells}</tr></thead>'
            f'<tbody>{body}</tbody></table></div>'
        )
        sections.append(
            f'<div class="eyebrow" style="margin:{"0" if group_name == POSITION_GROUPS[0][0] else "20px"} 0 8px;">{esc(group_name)}</div>'
            + table
        )
    gap_note = (
        '<p class="block-note" style="margin-top:10px;">Same live values as the grouped table above, split into narrower per-position tables so nothing scrolls horizontally.</p>'
    )
    return "".join(sections) + gap_note

CLEARS_CHECK_SVG = (
    '<svg viewBox="0 0 24 24" width="30" height="30" role="img" aria-label="Clears training minutes threshold">'
    '<circle cx="12" cy="12" r="12" fill="var(--positive)"/>'
    '<path d="M7 12.5l3 3 7-7" stroke="var(--surface)" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)

def training_status_html(playerid, minutes_map):
    m = minutes_map.get(playerid)
    if not m: status_color = "--ink-soft"
    elif m["status"] == "Clears": status_color = "--positive"
    elif m["status"].startswith("Short by"): status_color = "--warning"
    else: status_color = "--negative"
    minutes_html = (
        f'<span>{m["minutes"]} / {m["threshold"]} min &nbsp;'
        f'<span class="tag" style="background:var({status_color}-soft); color:var({status_color});">{esc(m["status"])}</span></span>'
    ) if m else '<span class="sub">minutes not tracked</span>'
    return (
        '<div style="display:flex; flex-wrap:wrap; gap:6px 18px; align-items:center; font-size:13px; color:var(--ink-soft); '
        'padding:6px 0 10px; margin-top:2px; border-bottom:1px solid var(--line);">'
        f'<span>Training: <b style="color:var(--ink)">{esc(CURRENT_TRAINING_FOCUS)}</b></span>'
        f'{minutes_html}'
        '</div>'
    )

def auto_training_cards_html(data):
    cards = data["training_cards"]
    out = []
    for c in cards:
        if not c["on_roster"]:
            out.append(
                f'<div class="card" style="border-color:var(--warning);"><div class="eyebrow" style="color:var(--warning); margin-bottom:6px;">{esc(c["name"])}</div>'
                '<p class="block-note" style="margin:0;">No longer on the roster — dropped from live tracking.</p></div>'
            )
            continue
        left_tags = ["jumpShot", "outsideDef", "driving", "insideShot", "rebound", "stamina"]
        right_tags = ["range", "handling", "passing", "insideDef", "block", "freeThrow"]
        skill_labels = dict(SKILL_DISPLAY_COLUMNS)

        def skill_cell(tag):
            s = c["skills"].get(tag, {})
            label = skill_label(s.get("value")) if s.get("value") is not None else "—"
            pop = f' <span style="color:var(--positive)">{esc(s["pop"])}</span>' if s.get("pop") else ""
            return f'<div style="padding:3px 0;">{esc(skill_labels[tag])}: <b>{label}</b>{pop}</div>'

        skill_rows = "".join(skill_cell(lt) + skill_cell(rt) for lt, rt in zip(left_tags, right_tags))
        minutes_map = data["training_minutes"]
        clears = minutes_map.get(c["playerid"], {}).get("status") == "Clears"
        card_style = "position:relative;" + (" border-color:var(--positive);" if clears else "")
        check_badge = f'<div style="position:absolute; top:14px; right:14px;">{CLEARS_CHECK_SVG}</div>' if clears else ""
        out.append(
            f'<div class="card" style="{card_style}">'
            + check_badge +
            f'<div class="who" style="font-size:17px; font-weight:700; padding-right:38px;">{esc(c["name"])} <span class="sub">&middot; {esc(c["position"])}</span></div>'
            + training_status_html(c["playerid"], minutes_map) +
            f'<div class="sub" style="margin:8px 0 8px;">Owner: {esc(data["team"]["name"])}</div>'
            '<div style="display:grid; grid-template-columns:1fr 1fr; gap:2px 18px; font-size:13px; color:var(--ink-soft); margin-bottom:10px;">'
            f'<span>Weekly salary: <b style="color:var(--ink)">{money_html(c["salary"])}</b></span>'
            f'<span>Game Shape: <b style="color:var(--ink)">{skill_label(c["game_shape"])}</b></span>'
            f'<span>DMI: <b style="color:var(--ink)">{esc(c["dmi"])}</b></span>'
            f'<span>Experience: <b style="color:var(--ink)">{skill_label(c["experience"])}</b></span>'
            f'<span>Age: <b style="color:var(--ink)">{esc(c["age"])}</b></span>'
            f'<span>Potential: <b style="color:var(--ink)">{potential_label(c["potential"])}</b></span>'
            f'<span>Height: <b style="color:var(--ink)">{esc(height_str(c["height"]))}</b></span>'
            '<span></span>'
            '</div>'
            f'<div style="display:grid; grid-template-columns:1fr 1fr; gap:3px 16px; font-size:13px; padding-top:8px; border-top:1px solid var(--line);">{skill_rows}</div>'
            '</div>'
        )
    return (
        '<div class="training-cards">' + "".join(out) + '</div>'
        '<p class="block-note" style="margin-top:12px;"><span class="tag tag-rec">[Inference]</span> Laid out like the in-game player page, live from the official API each run. '
        'A few fields shown in-game aren\'t exposed by the API and are left out rather than guessed. Word labels and colors use the Game Manual\'s exact 1&ndash;20 scale and stylesheet. '
        'Weekly minutes are computed live each run by summing boxscore.aspx across matches played since the most recent Friday reset. '
        '<span class="tag tag-rec">Per Tom</span> Only minutes played at one of the focused positions count toward the threshold. '
        'Training focus is still static, carried over from the last screenshot check, since training.aspx has no API endpoint. '
        'The Clears/Short/Well-short bucketing is our own heuristic, not an official in-game label.</p>'
    )

def build_fragments(data):
    """Same marker->generator mapping the original patch_template() used,
    but returns {marker_name: html} instead of substituting into a template
    string - the frontend does that substitution client-side against the
    static page it already has, using this dict fetched from the DB."""
    generators = {"META": auto_meta_html, "OVERVIEW_STATS": auto_overview_stats_html,
                  "RECOMMENDATIONS": auto_recommendations_html,
                  "INVESTMENTS": auto_investments_html,
                  "ROSTER_SKILLS": auto_roster_skills_html,
                  "ROSTER_BY_POSITION": auto_roster_by_position_html,
                  "TRAINING_CARDS": auto_training_cards_html,
                  "TRANSACTION_LEDGER": auto_transaction_ledger_html,
                  "SCHEDULE_STANDINGS": auto_schedule_standings_html, "FINANCE_WEEKLY": auto_finance_weekly_html,
                  "ROSTER_CHANGES": auto_roster_changes_html,
                  "STAFF": auto_staff_html, "MINUTES_VS_MONEY": auto_minutes_vs_money_html,
                  "ARENA_GLANCE": auto_arena_glance_html, "ARENA_PRICE_BARS": auto_arena_price_bars_html,
                  "DIVISION_STANDINGS": auto_division_standings_html}
    return {name: generators[name](data) for name in AUTO_MARKERS}

def most_recent_training_week_start(now_utc):
    """The training-minutes week resets Friday, per Tom - a different cycle
    than the Monday economy week (economy.aspx's thisWeek/lastWeek)."""
    days_since_friday = (now_utc.weekday() - 4) % 7  # Mon=0 ... Fri=4
    candidate = now_utc.replace(hour=5, minute=0, second=1, microsecond=0) - timedelta(days=days_since_friday)
    if candidate > now_utc:
        candidate -= timedelta(days=7)
    return candidate

ALL_POSITIONS = ["PG", "SG", "SF", "PF", "C"]

NON_TRAINING_MATCH_TYPES = {"bbm"}

def fetch_weekly_position_minutes(session, schedule_root, our_team_id):
    """Sum each player's minutes played, broken down by position, across this
    training-week's already-played matches, via boxscore.aspx per match.

    Per Tom (confirmed against the Game Manual): BBM matches (schedule.aspx
    match type "bbm") don't count toward training, unlike league games -
    excluded via NON_TRAINING_MATCH_TYPES rather than an allowlist, since
    cup/playoff minutes are still unconfirmed and shouldn't be silently
    excluded on a guess."""
    week_start = most_recent_training_week_start(datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    minutes = {}
    for m in schedule_root.findall(".//match"):
        start = m.get("start", "")
        if start < week_start:
            continue
        if m.get("type") in NON_TRAINING_MATCH_TYPES:
            continue
        away, home = m.find("awayTeam"), m.find("homeTeam")
        away_score = away.findtext("score") if away is not None else None
        home_score = home.findtext("score") if home is not None else None
        if away_score is None or home_score is None:
            continue  # not played yet
        matchid = m.get("id")
        if not matchid:
            continue
        try:
            box = fetch(session, "boxscore.aspx", {"matchid": matchid})
        except (BBApiError, requests.RequestException):
            continue
        for team_el in (box.find(".//awayTeam"), box.find(".//homeTeam")):
            if team_el is None or team_el.get("id") != our_team_id:
                continue
            for p in team_el.findall(".//boxscore/player"):
                pid = p.get("id")
                mins_el = p.find("minutes")
                if pid is None or mins_el is None:
                    continue
                by_pos = minutes.setdefault(pid, {pos: 0.0 for pos in ALL_POSITIONS})
                for pos in ALL_POSITIONS:
                    by_pos[pos] += float(mins_el.findtext(pos) or 0)
    return minutes

def total_minutes(position_minutes, positions=ALL_POSITIONS):
    return sum(position_minutes.get(pos, 0) for pos in positions)

def build_report(session, conn, team_key):
    teaminfo = fetch(session, "teaminfo.aspx")
    roster = fetch(session, "roster.aspx")
    economy = fetch(session, "economy.aspx")
    schedule = fetch(session, "schedule.aspx")
    standings = fetch(session, "standings.aspx")
    arena = fetch(session, "arena.aspx")
    our_team_id = teaminfo.find(".//team").get("id")
    position_minutes = fetch_weekly_position_minutes(session, schedule, our_team_id)
    staff_list = fetch_staff(session)
    data = extract_data(conn, team_key, teaminfo, roster, economy, schedule, standings, arena,
                         our_team_id, position_minutes, staff_list)
    # Only overwrite the persisted roster snapshot after a fully successful
    # run, so a failed run can't corrupt the diff baseline for next time.
    save_roster_xml(conn, team_key, roster)
    return data
