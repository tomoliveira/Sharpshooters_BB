# Handoff: Sharpshooters Arena Pricing/Capacity Optimizer

Context for a Claude Code session. Goal: build a script that recommends ticket-price and/or expansion changes for Tom's BuzzerBeater team (Sharpshooters, team #32988, League III.15, Brasil), using a benchmark dataset of 64 higher-division teams as reference "ideal" arenas.

**Standing constraint: this is analysis/code only. Any live change on buzzerbeater.com (price changes, arena expansion, anything submitted through the site) requires Tom's explicit go-ahead before it's executed — do not auto-apply recommendations.**

## 1. Sharpshooters' current arena state (fetched 2026-09-11)

Source: https://buzzerbeater.com/team/32988/arena.aspx

| Tier | Capacity | Current price | Allowed price range |
|---|---|---|---|
| Bleachers | 6,020 | $12 | $5 – $20 |
| Lower Tier | 560 | $44 | $18 – $70 |
| Courtside Seats | 108 | $119 | $50 – $200 |
| Luxury Boxes | 8 | $892 | $400 – $1,600 |

- Total capacity: 6,696. Season ticket holders: 1,125 (as of season start).
- Expansion costs (per additional seat): Bleachers $200, Lower Tier $700, Courtside $2,000, Luxury Boxes $16,000.
- **Capacity was recently expanded** — attendance history shows Lower Tier/Courtside/Luxury capacity jumped partway through the recent game log (e.g. Courtside went from 60 → 108, Luxury 2 → 8, Lower Tier 500 → 560). Any fill-rate calc from historical rows needs to use the capacity that was actually in effect for that game, not today's capacity — older rows will look like near-100% fill against a smaller arena that no longer exists.
- Estimated recent avg revenue/game (last 5 non-"Ticket Price Update" rows, attendance × *current* prices): **$92,273**.
- Recent attendance rows (date, opponent, bleachers, lower tier, courtside, luxury, total, type):
  - 9/8 M6ia Nov9 Club: 5333, 542, 108, 5 → 5,988
  - 9/1 Castelo Basquete: 3731, 500, 60, 2 → 4,293
  - 8/25 Braga Monsters: 5438, 500, 60, 2 → 6,000
  - 8/20 Pelicans São Raimundo (Cup): 5438, 500, 60, 2 → 6,000
  - 8/15 X-Salada: 4769, 500, 60, 2 → 5,331
  - (older rows in the source page go back to 7/7, all at the pre-expansion capacity)

## 2. Benchmark dataset

64 teams from the Season 72 "BuzzerBeater's Best" (B3) international knockout draw (top-division/competitive teams across many countries — much bigger than Sharpshooters' League III.15, so treat as an aspirational ceiling, not a same-league comp). Delivered alongside this brief as `bb_best_bracket_arenas.csv` — columns: team_id, team_name, arena_name, bleachers_capacity, bleachers_price, lower_tier_capacity, lower_tier_price, courtside_capacity, courtside_price, luxury_capacity, luxury_price, total_capacity, avg_est_revenue_per_game, avg_fill_pct.

Revenue/fill in that CSV are estimates (attendance from each team's last ~5 real games × that tier's *current* price), not BuzzerBeater's own reported figures.

Set-wide averages (n=64): Bleachers $18.1 | Lower Tier $46.8 | Courtside $184.5 | Luxury $1,003.6 | Total capacity 22,836 | Fill 79.3% | Est. revenue/game $524,333.

Best combined models (high revenue AND high fill ≥88%):
1. Vitoria Deluxe — $609,084/game @ 93% fill, 21,500 capacity (Bleachers 17,000/$19, Lower Tier 3,950/$54, Courtside 500/$192, Luxury 50/$980).
2. South Dragons — $595,866 @ 89%, 21,750 cap — unusual model: small Bleachers (12,500) + large cheap Lower Tier (8,700/$35).
3. dequestion — $591,475 @ 96% fill (highest in the set), 20,000 cap.
4. Rila — $590,293 @ 91%, 20,550 cap.
5-8. Isca Centurions, Olivik Vikings, Młoty Stargard, Silverbacks — $548k-573k @ 89-92%.

[Inference] Teams with big revenue but low fill (Jibou NRG $610k @ 69%, Venomous Scorpions $603k @ 48%) get there via oversized capacity, not efficient pricing — weaker models to copy. Lowest performers (Sant Mateu $301k @ 54%, Vieja Guardia $398k @ 59%) combine low prices with still-poor fill, suggesting fill isn't purely a pricing problem for them (could be team performance/market size/league tier) — worth keeping in mind since Sharpshooters is a lower-division team, so demand elasticity there may not transfer 1:1 from this top-division sample.

## 3. Relevant game-economy rules already on file (from the BuzzerBeater manual)

- Salary floor as % of league TV money: Div I 245%, Div II 190%, Div III 130%, Div IV 100%, Div V/VI 70%.
- Hoarding tax: 10%/week on balance above $25M. Overextension tax on spending far above season-average income.
- Merchandise income is boosted by winning, domestic/own-drafted player share, national-team games, league-leading stats — arena revenue is only one income stream, not the whole economy model.

## 4. Suggested scope for the optimizer script

Not prescriptive — use judgment, but a reasonable v1:

- Inputs: Sharpshooters' current tier capacities/prices/price-bounds, expansion costs, available budget (ask Tom — not known from this session), and the benchmark CSV.
- Core question: within Sharpshooters' price bounds and a given expansion budget, what price (and optionally capacity) changes plausibly increase total per-game revenue, informed by the benchmark set's price-vs-fill relationships (e.g. Lower Tier fill drops sharply above ~$50-55 in the benchmark data) rather than assuming Sharpshooters' demand curve matches a top-division team's exactly.
- Output: a ranked set of price-change (and, if budget allows, expansion) scenarios with estimated revenue impact, clearly labeled as estimates/inferences, not guaranteed outcomes.
- Flag clearly to Tom before any live action on buzzerbeater.com — per the standing instruction above, code should only prepare recommendations, never submit price/expansion changes automatically.

## 5. Open questions for Tom (the coding session should ask, not assume)

- Expansion budget available right now (current bank balance / how much he's willing to spend)?
- Is the goal pure ticket revenue, or account for knock-on effects (e.g. merchandise/attendance ties to team performance)?
- OK to use the top-division benchmark set as directional guidance despite the league-tier gap, or should the script instead try to find League III.15 (or similarly-sized) comps for a closer demand-curve match?
