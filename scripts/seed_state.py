#!/usr/bin/env python3
"""One-time seeding: loads a legacy investments.json + .last_roster.xml (from
the older buzzerbeater-report skill's local reports/<team_key>/ directory)
into this repo's SQLite `state` table, so the investment ledger and
roster-diff baseline aren't lost when switching to this pipeline.

Usage:
    python scripts/seed_state.py --db docs/report.db --team-key sharpshooters \\
        --ledger /path/to/investments.json --roster-xml /path/to/.last_roster.xml
"""
import argparse
import sqlite3
from pathlib import Path

import bbapi_lib as lib


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True)
    p.add_argument("--team-key", required=True)
    p.add_argument("--ledger", required=True, help="Path to the legacy investments.json")
    p.add_argument("--roster-xml", required=True, help="Path to the legacy .last_roster.xml")
    args = p.parse_args()

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    lib.init_db(conn)

    import json
    ledger = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    lib.save_investment_ledger(conn, args.team_key, ledger)

    roster_xml = Path(args.roster_xml).read_text(encoding="utf-8")
    conn.execute(
        "INSERT INTO state (team_key, roster_xml) VALUES (?, ?) "
        "ON CONFLICT(team_key) DO UPDATE SET roster_xml=excluded.roster_xml",
        (args.team_key, roster_xml),
    )
    conn.commit()
    conn.close()
    print(f"Seeded ledger + roster baseline for '{args.team_key}' into {db_path}")


if __name__ == "__main__":
    main()
