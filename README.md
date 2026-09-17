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

### 5. (Optional) Set up the "Update now" button's token

The report page has an "Update now" button (top-right, next to Dark mode)
that triggers `daily-update.yml` directly from the browser via GitHub's
REST API. Since the repo and page are public, it can't ship a credential of
its own - the first click prompts for a personal access token, which is
saved only in that browser's `localStorage`, never committed anywhere.

To create one: GitHub → Settings → Developer settings → Personal access
tokens → **Fine-grained tokens** → Generate new token, scoped to just this
repository, with **Actions: Read and write** permission and nothing else.
Paste it when the button prompts. Shift-click the button to replace a
saved token later (e.g. after rotating it). A rejected token (expired,
revoked, wrong scope) clears itself automatically rather than silently
retrying.

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

## Season-end cash projection

Finances tab: projects current cash forward at a flat weekly run rate
(this week's net change, plus a 2-week-average alternative shown for
context) across however many of the season's 13 Monday resets remain.
Unlike Trainee Score's `pops_so_far`, weeks-remaining doesn't need manual
upkeep - it's derived each run from the schedule's own last currently-listed
match (`schedule.aspx` returns the whole season, not just a handful of
upcoming fixtures), so it self-updates and even grows if the league adds
more fixtures later (a deep cup or playoff run). A `season_weeks_remaining`
value in team config is only consulted as a fallback, if the schedule ever
returns no usable match date.

## What I'd look at next

Overview tab, below the flagged alert/recommendations list. Three
auto-updated sub-sections, all part of the same `AUTO:RECOMMENDATIONS`
fragment:

- **Financial changes** - this week vs. last week's biggest revenue/expense
  category movers, plus how the season-end projection has moved since
  yesterday's snapshot (diffed against the previous row in `snapshots`,
  since the projection's numeric result is itself stored in each
  snapshot's `data_json` under `projection`).
- **Training overview** - pops AND drops for the training cohort
  (`config.json`'s `training_cohort`), tracked two ways: this training
  week (since the most recent Friday 05:00:01 UTC reset), and a
  season-to-date count broken down by which skills changed and how many
  times. Reads roster.aspx's own live `pop` attribute on each skill (a
  signed delta like `+1` or `-1`, net since the current training week's
  reset) directly, rather than diffing our own previously-observed
  values - an earlier version tried the diff approach and missed real
  changes whenever the game's change had already landed before a
  pre-change baseline was ever captured (including this tracking's own
  first run), and could never see drops at all (a diff only fires on
  increases). The live flag doesn't have either gap. Stored per (player,
  training week) in `state.ledger_json`'s `skill_pops` key
  (`update_skill_pop_tracking` writes it, overwriting - not
  double-counting - if a later run the same week sees an updated value;
  `summarize_training_pops` reads it back for display). Season totals
  only cover training weeks observed since this tracking started
  (2026-09-11) - the game's own flag resets every Friday, so a week that
  finished before that has no way to be recovered after the fact.
- **League power rankings** - per Tom, every team in the conference gets a
  weighted **Power score (0-100)**, not just a top-6 cut:
  `POWER_WEIGHT_RATINGS` **50%** overall rating (recent-form boxscore
  ratings - outside/inside scoring, outside/inside defense, rebounding,
  offensive flow, averaged over each team's last up to 5 competitive
  games: league, cup, playoffs, TV-flagged league games, B3; friendlies
  and BBM scrimmages excluded - then min-max normalized across the whole
  conference so the best-rated team scores 100 and the worst scores 0),
  `POWER_WEIGHT_RECENT_RECORD` **15%** win% over those same last 5 games,
  `POWER_WEIGHT_VS_TOP_RECORD` **35%** win% specifically against the "Top
  6" group. `compute_power_scores` blends these; a team missing a
  component (most often "vs Top 6" - it hasn't played all of them yet)
  has that weight redistributed proportionally across whatever components
  it does have, rather than scoring 0% on a record it hasn't had the
  chance to build. Each finished game's boxscore is fetched once and
  cached forever in the `match_ratings` table (keyed by matchid + team) -
  only matches played since the last run ever trigger a new
  `boxscore.aspx` call.

  The "Top 6" group itself (badged in the table) is still selected
  separately from the Power score, by `compute_top_group_by_head_to_head`:
  bootstrapped iteratively - seed a group from naive season diff,
  recompute each team's average point diff using only games against the
  current group, re-rank, repeat until the group stops changing. Eligible
  candidates for that selection are capped to the top `max(top_n * 2, 10)`
  teams by naive season diff, not the whole conference - without that
  cap, a team with a genuinely poor record could still enter "Top 6" on
  one small/noisy head-to-head sample (caught live 2026-09-17: a team
  ranked 13th of 16 briefly displaced a much stronger team on a single
  game).

  Each candidate's selection score blends its head-to-head point diff vs
  the current group (min-max normalized to 0-100 across the pool) 50/50
  with its own recent-form composite rating (same normalization). A team
  with no games yet against the current group has that 50% head-to-head
  weight transfer entirely to its rating instead of falling back to a
  differently-scaled number - per Tom (2026-09-17, after "Why is Honda
  Fever in the top 6?" surfaced a team with a real-but-bad head-to-head
  number outranking clearly stronger teams that simply hadn't played the
  current group yet): a team with no data shouldn't be penalized against
  one with bad data. A team with no head-to-head games is flagged with a
  `*` in the table (`used_fallback_diff`) - this only affects "Top 6"
  membership, not the Power score itself.

  Our own team's row uses the same rating window "You (avg)" on the
  outlier cards uses (`own_rating_since`, when set - not necessarily the
  same last-5-games window the rest of the table uses), and its rating
  cells are shown in plain color rather than red/green, since comparing
  our own values to our own average isn't a threat signal the way an
  opponent's rating is. Every other team's rating cell is colored against
  `compute_overall_avg(our_rating)` - red above it (they outgun us there),
  green below it (we're already ahead). Our **next scheduled league
  opponent** (regular season or playoff - not friendly/cup/B3/etc.,
  resolved from the full schedule in `extract_data` as
  `next_league_opponent_id`) is highlighted and badged in the table even
  when they're well outside the Top 6.
  - **Teams to watch**, above the ranked table, in priority order: **new
    big hires** first (there's no transfer/bidding API for other teams, so
    this is inferred by diffing each conference team's `roster.aspx`
    against what was last seen and flagging a newly-appeared player paid
    at least 2x that team's prior roster median - disclaimed as inferred,
    not confirmed, in the UI itself), then **one card per rating
    category** (icon + label header): the #1 team shown emphasized as the
    card's headline value, the next two teams as smaller-font runners-up
    below (reusing the site's existing `.stat-card`/`.foot` styling, so no
    new CSS was needed), a lightning-bolt badge on the leader when it's a
    genuine statistical outlier (more than 1.25 population standard
    deviations above the ranked pool's mean in that category), and a
    separate red "weakest" callout when some team is a severe *negative*
    outlier in that category. `compute_ratings_watchlist` builds the
    per-category data, `_teams_to_watch_html` renders the cards. Player
    injuries aren't exposed anywhere in the BuzzerBeater API, so they're
    not part of any of this - check a team's roster page by hand if that
    matters. Each card also shows **"You (avg)"** - our own team's rating
    in that category, averaged over our own recent games, so the
    leader's number always has something of ours to compare against even
    on weeks we're not in the top-6 group ourselves. Normally the same
    last-5-games window as everyone else; `config.json`'s
    `own_rating_since` (a `YYYY-MM-DD` string) overrides that to "every
    competitive game since this date" instead - a one-season judgment
    call (per Tom, for the current season only), not a permanent rule,
    so it's left unset for a fresh season rather than defaulting to
    always-on. (The card label itself doesn't call out which window is
    active - per Tom, that's not worth surfacing in the UI.)

## Methodology tooltips

Per Tom: the "Calculated"/"[Inference]" methodology paragraphs that used
to sit as always-visible text under most sections are now a small (i)
icon next to that section's own title instead - hover, or tap/focus on
touch, to see the note. `info_tip(html)` (`scripts/bbapi_lib.py`) builds
one; the CSS (`.info-tip`/`.tip-bubble`) lives in
`docs/<team_key>/index.html`. Two ways it's wired up, depending on
whether the section's title is itself auto-updated data or static page
furniture:
- **Python-owned heading** (e.g. "Training overview", "League power
  rankings" - both rendered inside the RECOMMENDATIONS fragment): the
  tip is built and appended to the heading string in the same function
  that renders the heading.
- **Static heading in index.html** (e.g. "Investment tracker", "Minutes
  vs. money"): if the caveat text is pure static prose (no per-run
  data), the tip is hand-written directly into that `<h2>` in
  index.html and the corresponding paragraph was deleted from the
  Python side entirely. If the caveat embeds live or per-team-config
  values (e.g. the season projection's weeks-remaining count, or
  Trainee Score's `trainee_score_pops_so_far`), it stays Python-rendered
  and is instead attached to a stat-card label or table column header
  that Python already controls within that section, rather than the
  static `<h2>` it can't reach.

## Per-item reports (Investments tab)

Each player row and each facility/capex row has a **Report** link
(`.report-link`, handled by a delegated click listener in index.html that
opens and scrolls to the matching `<details>`) leading to a collapsed
report further down the page:

- **Player reports** (`_player_reports_html`, one `<details id="player-
  report-<playerid>">` per player with a tracked purchase) - acquisition
  cost plus every individual salary payment recorded for that player
  (date + amount), not just the summed total already shown in the main
  table. Built from `payments` on each investments row (the same
  `salary_payments` list `record_weekly_salary_payments` already
  maintains per player in the ledger).
- **Expansion reports** (`_expansion_reports_html`, one `<details
  id="expansion-report-<i>">` per capex entry, index assigned in
  date-ascending order) - the expansion's cost plus every individual home
  game's gate revenue since it took effect. Pairs each capex entry with
  the arena capacity "regime" it opened (`build_arena_investment_summary`
  already groups `match_revenue` by capacity window; this just renders
  the per-game rows that summary only aggregates elsewhere). The regime
  before any tracked expansion (the original capacity) has no capex entry
  to pair with, so it's excluded.

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
