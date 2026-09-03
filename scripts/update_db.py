#!/usr/bin/env python3
"""Daily entrypoint, run by .github/workflows/daily-update.yml (and runnable
by hand for testing). Logs into BuzzerBeater, fetches live data for one team,
and writes a new snapshot row into the shared SQLite database at --db
(docs/report.db by default in this repo, so it's served by GitHub Pages and
committed back to the repo by the workflow).
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

import requests

import bbapi_lib as lib


def main():
    parser = argparse.ArgumentParser(description="Fetch live BuzzerBeater data and store a snapshot in the report database.")
    parser.add_argument("--config", required=True, help="Path to teams/<team_key>.json")
    parser.add_argument("--db", required=True, help="Path to the SQLite database (e.g. docs/report.db)")
    parser.add_argument("--keep", type=int, default=180, help="Snapshots to retain per team (default: 180, ~6 months daily)")
    args = parser.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass

    cfg = lib.load_team_config(args.config)
    team_key = cfg.get("team_key") or Path(args.config).stem

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    lib.init_db(conn)

    session = requests.Session()
    try:
        lib.login(session)
        data = lib.build_report(session, conn, team_key)
    except lib.BBApiError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        conn.close()
        sys.exit(1)

    print(lib.render_text(data))

    fragments = lib.build_fragments(data)
    conn.execute(
        "INSERT INTO snapshots (team_key, fetched_at, data_json, fragments_json) VALUES (?, ?, ?, ?)",
        (team_key, data["now"], json.dumps(data, ensure_ascii=False, default=str), json.dumps(fragments, ensure_ascii=False)),
    )
    conn.execute(
        "DELETE FROM snapshots WHERE team_key = ? AND id NOT IN "
        "(SELECT id FROM snapshots WHERE team_key = ? ORDER BY fetched_at DESC LIMIT ?)",
        (team_key, team_key, args.keep),
    )
    conn.commit()
    conn.close()
    print(f"\nSnapshot written for '{team_key}' at {data['now']} -> {db_path}")


if __name__ == "__main__":
    main()
