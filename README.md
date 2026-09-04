# Sharpshooters_BB

Live BuzzerBeater team reports, built from four pieces:

1. **`teams/<team_key>/config.json`** — one folder per team: training
   doctrine, cohort, and which env vars hold that team's BuzzerBeater login.
2. **`scripts/`** — a Python job (`update_db.py`, built on the fetch/render
   logic from the original `buzzerbeater-report` skill) that logs into the
   official BuzzerBeater API for one team and writes a snapshot per run into
   `docs/report.db`, a single SQLite database shared by every team (rows are
   keyed by `team_key`).
3. **`.github/workflows/daily-update.yml`** — a GitHub Actions cron job that
   runs that script once a day per team and commits the updated
   `docs/report.db` back to the repo.
4. **`docs/<team_key>/`** — one folder per team, served by GitHub Pages:
   `index.html` fetches `report.db` client-side with
   [sql.js](https://sql.js.org/) and patches the latest snapshot's
   pre-rendered HTML fragments into itself (the page is never regenerated,
   only the database changes), and `images/` holds that team's logo/banner —
   see "Team images" below. `docs/index.html` is a redirect to the one team
   that exists so far; once a second team is onboarded, turn it into a real
   picker page.
5. **`mcp-server/`** — a local stdio MCP server, so Claude (or any MCP
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

(These match `teams/sharpshooters/config.json`'s `bb_login_env`/
`bb_code_env`. For a second team, add a new team config with different env
var names and a second secret pair — see "Adding another team" below.)

### 2. Enable GitHub Pages

Settings → Pages → Source: **Deploy from a branch** → Branch: `main`,
folder: **/docs**. The report will be live at
`https://<your-username>.github.io/Sharpshooters_BB/sharpshooters/`
(the bare repo URL redirects there).

### Team images

Drop `logo.png` and/or `banner.png` into `docs/<team_key>/images/` (e.g.
`docs/sharpshooters/images/logo.png`) through the GitHub web UI or a normal
git push — `index.html` already references both by that exact filename in
the masthead and removes the `<img>` on load if the file isn't there yet, so
nothing breaks with the folder empty. Use other filenames for anything else
(sponsor logos, arena photos) and reference them from `index.html` by hand,
same pattern (`./images/<name>.png`, with an `onerror="this.remove()"` if
you want it to degrade gracefully too).

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
BB_LOGIN=... BB_CODE=... python update_db.py --config ../teams/sharpshooters/config.json --db ../docs/report.db
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

1. Copy `teams/sharpshooters/config.json` to `teams/<team_key>/config.json`,
   filling in that team's `training_cohort`, `current_training_focus`,
   `trainee_score_pops_so_far` (see "Trainee Score" below), and distinct
   `bb_login_env`/`bb_code_env` names (e.g. `BB_LOGIN_TEAM2`).
2. Add the matching secrets in repo settings.
3. Add a second step (or job) to `.github/workflows/daily-update.yml` that
   runs `update_db.py --config ../teams/<team_key>/config.json --db ../docs/report.db`
   with that team's env vars — snapshots for different teams live in the
   same database, keyed by `team_key`.
4. Create `docs/<team_key>/` (with its own `images/` folder), copying
   `docs/sharpshooters/index.html` as a starting point: change `TEAM_KEY` in
   its loader script, update `../report.db`/`../favicon.png` paths (stay the
   same if the new folder sits directly under `docs/`), and replace the
   masthead text and manual-analysis sections with that team's own.
5. Turn `docs/index.html` from a hard redirect into a real picker linking to
   each team's folder.

## Trainee Score

A house metric (not an official BuzzerBeater figure) on the roster skill
table: how a player's current TSP (sum of the 12 rated skills) compares to
an "ideal trainee" bar - 60+ TSP at age 18, climbing ~10/season after that,
capped at 160 TSP since real growth decelerates with age. Potential only
matters below 6 (halves the score) - a placeholder until a proper TSP/
potential ratio replaces it. See `trainee_score()` in `scripts/bbapi_lib.py`
for the exact formula.

The one piece that goes stale during a season is `trainee_score_pops_so_far`
in that team's `config.json` - roughly how many skill pops have already
landed since the season started (a season adds ~8-12 total; nudge this
value up by hand every week or two as the season progresses, the same way
`current_training_focus` already needs occasional manual updates).

## What's live vs. manual

Every section tagged **"Auto-updated daily"** on the report page is filled
in from the daily snapshot. Everything else (fan sentiment, the division
$/player comparison, training-doctrine narrative, arena-expansion
commentary) is hand-written prose with no API source — edit
`docs/<team_key>/index.html` directly when you want to refresh those, the
same as the original skill's template.

## Credit

Fetch logic, the game's skill-color scale, and the report's design system
are carried over from Tom's `buzzerbeater-report` Claude Code skill
(`tomoliveira/buzzerbeater-report-skill`) - this repo replaces that skill's
"run on demand, republish the whole HTML" workflow with an always-on daily
pipeline + a static page that only pulls new data, never regenerates.
