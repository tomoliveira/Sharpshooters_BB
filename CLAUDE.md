# Sharpshooters_BB

Knowledge base and live report for Tom's BuzzerBeater team, Sharpshooters (#32988). How the daily report pipeline works is in `README.md`; this file covers how to work on **studies**.

The repo is **public**. Never commit BuzzerBeater credentials, tokens or `.env` files. Collectors read `BB_LOGIN` / `BB_CODE` from the environment.

## Where studies live

| Kind | Location |
|---|---|
| Study article | `studies/<slug>.md` |
| A study's data, collector and analysis scripts | `studies/<slug>/` (same slug as the article) |
| Older research projects | `top-teams-research/`, `salary-model/`, `arena-model/` |
| Game mechanics and lookup tables | `references/` |

An article only appears in the report's **Studies** tab once it has an entry in `docs/studies.json`: `id` (the slug), `group` (`strategy` = a decision Tom made, `research`, or `reference`), `title`, `date` (YYYY-MM-DD), `path`, and a one-line `summary` that states the main finding. Append to `articles`; keep the file's 2-space JSON formatting.

Use `/new-study` to scaffold a new one.

## Article conventions

- First line: `# <Title>`. Second paragraph: `Added YYYY-MM-DD.` plus what kind of document it is (e.g. "Static snapshot, not recomputed by the daily job.") and a link to its data folder if it has one.
- Label every claim by source, as the existing studies do:
  - **Official**: the BuzzerBeater API or the Game Manual. Link the page.
  - **Calculated.**: computed from data in this repo. Say from what.
  - **Community (unverified)**: forums or third-party tools. Link the source.
  - **[Inference]**: our own reasoning, not directly measured.
- State the main finding first, then the method and data.
- Link to other articles with relative paths (e.g. `[Season structure](season-structure.md)`); the Studies tab opens those in place.
- If a study is paused, say so near the top with the reason and what unblocks it.

## Data collection rules

- **Max 30 page pulls per minute** for any BuzzerBeater collection (at least 2 s between requests). This rule dates from 2026-11-10; `studies/salary-by-division/collect.py` predates it and pulls faster, so don't copy its 0.25 s delay.
- Prefer the official API (`https://bbapi.buzzerbeater.com/`) over page scraping. Read-only calls only.
- BuzzerBeater moved to a new website on 2026-11-10. Before reusing any scraper or field name, re-check the page or API structure.
- Estimate the pull budget before a large collection and record it in the study's data folder (see `studies/ratings-impact/pull_budget.csv`).
- Raw downloads go in a `raw/` folder, which `.gitignore` excludes. Commit only the cleaned CSV/JSON the article cites.
- Fix random seeds in sampling scripts so results can be reproduced.

## Checking a study locally

`python -m http.server` from the repo root, then open `/docs/sharpshooters/` and the Studies tab. On localhost, articles load from the working copy, so unmerged ones show up.
