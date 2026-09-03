# Sharpshooters_BB

Live BuzzerBeater team report for the Sharpshooters, built from three pieces:

1. **`scripts/`** — a Python job (`update_db.py`, built on the fetch/render
   logic from the original `buzzerbeater-report` skill) that logs into the
   official BuzzerBeater API and writes one snapshot per run into
   `docs/report.db`, a SQLite database.
2. **`.github/workflows/daily-update.yml`** — a GitHub Actions cron job that
   runs that script once a day and commits the updated `docs/report.db` back
   to the repo.
3. **`docs/index.html`** — a static report page (served by GitHub Pages)
   that fetches `report.db` client-side with [sql.js](https://sql.js.org/)
   and patches the latest snapshot's pre-rendered HTML fragments into itself.
   The page is never regenerated — only the database changes.
4. **`mcp-server/`** — a local stdio MCP server, so Claude (or any MCP
   client) can query the same report data as structured tool calls instead
   of scraping the page.

## One-time setup

### 1. Add BuzzerBeater credentials as secrets

`BB_LOGIN` / `BB_CODE` currently live as environment secrets under
`github-pages` (Settings → Environments → github-pages → Add secret) — the
environment GitHub auto-creates for Pages deploys. The `update-sharpshooters`
job in `.github/workflows/daily-update.yml` declares `environment:
github-pages` so it can read them; a job targeting an environment sees both
that environment's secrets and plain repo-level ones (Settings → Secrets
and variables → Actions), with the environment's value winning on a name
collision — so either location works, and you can drop the `environment:`
line if you'd rather keep everything at the repo level instead.

(These match `teams/sharpshooters.json`'s `bb_login_env`/`bb_code_env`. For
a second team, add a new team config with different env var names and a
second secret pair — see "Adding another team" below.)

### 2. Enable GitHub Pages

Settings → Pages → Source: **Deploy from a branch** → Branch: `main`,
folder: **/docs**. The report will be live at
`https://<your-username>.github.io/Sharpshooters_BB/`.

### 3. Seed the investment ledger (already done for Sharpshooters)

`docs/report.db` in this repo already ships seeded with the real historical
ledger (player purchases, arena capex, match revenue) and roster baseline
carried over from the original skill's local `investments.json` /
`.last_roster.xml`, via:

```bash
python scripts/seed_state.py --db docs/report.db --team-key sharpshooters \
  --ledger /path/to/investments.json --roster-xml /path/to/.last_roster.xml
```

Only re-run this if you're onboarding a team that already has history
tracked elsewhere.

### 4. Trigger the first run

Actions tab → "Daily BuzzerBeater update" → Run workflow (or just wait for
the daily cron). Check `docs/report.db` got committed, then load the Pages
URL.

## Running the update script by hand

```bash
cd scripts
pip install -r requirements.txt
BB_LOGIN=... BB_CODE=... python update_db.py --config ../teams/sharpshooters.json --db ../docs/report.db
```

## Using the MCP server

```bash
cd mcp-server
npm install
```

Then register it with Claude Code:

```bash
claude mcp add sharpshooters-bb -- node /absolute/path/to/Sharpshooters_BB/mcp-server/index.js
```

It reads `docs/report.db` over HTTP from the live GitHub Pages URL (no
BuzzerBeater credentials needed - it's read-only against already-published
data). Override the source with `REPORT_DB_URL` if you fork this or rename
the repo. Tools exposed: `get_report_snapshot`, `get_report_section`,
`list_snapshots`.

## Adding another team

1. Copy `teams/sharpshooters.json` to `teams/<team_key>.json`, filling in
   that team's `training_cohort`, `current_training_focus`, and distinct
   `bb_login_env`/`bb_code_env` names (e.g. `BB_LOGIN_TEAM2`).
2. Add the matching secrets in repo settings.
3. Add a second step (or job) to `.github/workflows/daily-update.yml` that
   runs `update_db.py --config ../teams/<team_key>.json --db ../docs/report.db`
   with that team's env vars — snapshots for different teams live in the
   same database, keyed by `team_key`.
4. Duplicate `docs/index.html` (e.g. `docs/<team_key>.html`) with `TEAM_KEY`
   in its loader script changed, and copy over that team's own manual
   analysis sections.

## What's live vs. manual

Every section tagged **"Auto-updated daily"** on the report page is filled
in from the daily snapshot. Everything else (fan sentiment, the division
$/player comparison, training-doctrine narrative, arena-expansion
commentary) is hand-written prose with no API source — edit
`docs/index.html` directly when you want to refresh those, the same as the
original skill's template.

## Credit

Fetch logic, the game's skill-color scale, and the report's design system
are carried over from Tom's `buzzerbeater-report` Claude Code skill
(`tomoliveira/buzzerbeater-report-skill`) - this repo replaces that skill's
"run on demand, republish the whole HTML" workflow with an always-on daily
pipeline + a static page that only pulls new data, never regenerates.
