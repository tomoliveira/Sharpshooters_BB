#!/usr/bin/env python3
"""One-time historical correction: backdates already-recorded "drafted"
(home-grown, no transfer record) player_transactions to a real known
acquisition date, and backfills their cumulative_salary_paid to match -
same idea as scripts/seed_state.py, but for a correction after the fact
rather than an initial seed.

Context: when a drafted/home-grown player is first seen with no purchase
record, bbapi_lib.py has no choice but to date their $0 acquisition entry
at "the day this ledger first noticed them" (see update_investment_ledger
in bbapi_lib.py) - a reasonable default for a genuinely new arrival, but
wrong for a team that already existed before tracking began. For
Sharpshooters, all such players were actually already on the roster since
2026-08-25 (when the current management took over) - this script corrects
that specific historical fact once, rather than changing the general
fallback (which would then wrongly backdate any *future* home-grown
arrival to a stale franchise-takeover date too).

Usage:
    python scripts/fix_drafted_acquisition_date.py --db docs/report.db \\
        --team-key sharpshooters --acquired-date 2026-08-25
"""
import argparse
from pathlib import Path

import bbapi_lib as lib


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", required=True)
    p.add_argument("--team-key", required=True)
    p.add_argument("--acquired-date", required=True, help="YYYY-MM-DD - the real acquisition date to backdate to")
    args = p.parse_args()

    import sqlite3
    db_path = Path(args.db)
    conn = sqlite3.connect(db_path)
    lib.init_db(conn)

    ledger = lib.load_investment_ledger(conn, args.team_key)
    acquired_dt = lib._parse_date(args.acquired_date)
    if acquired_dt is None:
        raise SystemExit(f"Could not parse --acquired-date {args.acquired_date!r}")

    fixed = []
    for t in ledger["player_transactions"]:
        if t.get("acquisition") != "drafted":
            continue
        t["date"] = args.acquired_date
        pid = t["playerid"]
        entry = ledger["player_snapshots"].get(pid)
        if entry is None:
            continue
        salary = float(entry.get("latest", {}).get("salary") or 0)
        accrual_date = entry.get("salary_accrual_date")
        accrual_dt = lib._parse_date(accrual_date) if accrual_date else None
        if accrual_dt is None:
            continue
        days = max((accrual_dt - acquired_dt).days, 0)
        entry["cumulative_salary_paid"] = salary * days / 7
        fixed.append((t["name"], days, entry["cumulative_salary_paid"]))

    lib.save_investment_ledger(conn, args.team_key, ledger)
    conn.close()

    if not fixed:
        print(f"No 'drafted' transactions found for team '{args.team_key}' - nothing to fix.")
        return
    print(f"Backdated to {args.acquired_date} and backfilled salary for {len(fixed)} player(s):")
    for name, days, paid in fixed:
        print(f"  {name}: {days} days -> ${paid:,.2f} cumulative salary paid")


if __name__ == "__main__":
    main()
