---
name: new-study
description: Scaffold a new BuzzerBeater study in this repo - the article in studies/, its data folder, and its docs/studies.json entry - following CLAUDE.md's conventions. Use when Tom wants to start, add or write up a new study, analysis or decision record.
---

# New study

1. **Get the basics.** Ask for anything not already given: the question the study answers, a short slug (kebab-case), the group (`strategy`, `research` or `reference`), and whether it needs data collection. Check `docs/studies.json` so the slug isn't taken.
2. **Write `studies/<slug>.md`** following CLAUDE.md's article conventions: title, `Added <today>.` line, main finding first (or the goal and status, if it's a plan), then method and data, with every claim labelled by source.
3. **If it collects data,** create `studies/<slug>/` and, before writing a collector:
   - re-check the current page/API structure (site changed 2026-11-10);
   - estimate the pull budget at max 30 pulls/min and save it as `studies/<slug>/pull_budget.csv`;
   - read credentials from `BB_LOGIN` / `BB_CODE` env vars only, sleep at least 2 s between requests, write raw downloads to `raw/`, fix random seeds.
   Show Tom the budget before running a collection longer than a few minutes.
4. **Add the `docs/studies.json` entry** (append to `articles`, keep 2-space formatting). The `summary` states the finding, or the status for a plan.
5. **Validate:** `python -m json.tool docs/studies.json > /dev/null`, and check that every relative link in the article points to a file that exists.
