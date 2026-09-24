# Game Manual: a manager's guide

A summary of the official [BuzzerBeater Game Manual](https://www.buzzerbeater.com/community/rules.aspx), written in our own words and focused on what matters for running the Sharpshooters. Read on 2026-09-24. The manual is BuzzerBeater's own text and this repo is public, so this is a guide to it, not a copy. Each section links to the official chapter, which is the authority whenever the two disagree.

Figures such as prizes, price limits and tax brackets are as the manual listed them on that date. Lines marked **[Inference]** are our reading of what a rule means for us, not something the manual says.

---

## Weekly rhythm · [Games](https://www.buzzerbeater.com/community/rules.aspx?nav=Matches) · [Weekly Schedule](https://www.buzzerbeater.com/community/rules.aspx?nav=WeeklySchedule)

- League games are on **Saturday and Tuesday**. **Thursday** is a cup game or a scrimmage. B3 and BuzzerBeater Madness games are on **Wednesday**.
- Three regular-season games each season are **televised**. They move fan sentiment more than normal games, in both directions.
- Lineups and tactics must be in **15 minutes before tip-off**. Without them the team plays default settings.
- Ticket price changes also need to be made 15 minutes before a game to apply to it.

## Standings, playoffs, promotion · [Standings](https://www.buzzerbeater.com/community/rules.aspx?nav=Standings)

- 22 league games. The **top four in each conference** reach the playoffs: 1 v 4 and 2 v 3 single games, a conference final, then a best-of-three final between the conference champions.
- The division champion is promoted. Extra promotion spots go to the best regular-season records (conference rank counts most), and further ones fill bot-controlled teams' places in the division above.
- Tie-breakers: fewest forfeits, then point differential, then points scored.
- **Relegation:** 8th seeds go straight down. Each conference's 5th plays the other conference's 7th, best of three (5th always has home court), and the two 6th seeds meet each other.
- Playoff and relegation gate revenue is **split 50/50** with the visitors.

| Prize or bonus | Div I | Div II | Div III | Div IV | Div V | Lower |
|---|---|---|---|---|---|---|
| League champion (runner-up gets half) | $400k | $250k | $150k | $100k | $80k | $60k |
| One-time bonus for promoting **into** | $1.5M | $750k | $450k | $300k | $225k | $225k |

The promotion bonus also comes with a boost to season-ticket holders and arena income.

**[Inference]** Promoting from Division III into Division II is worth **$750k plus the league prize**. That's the payoff behind the promotion-era strategy in [Training strategy](training_strategy_notes.md).

## Economy · [Economy](https://www.buzzerbeater.com/community/rules.aspx?nav=Economy)

- **Salaries are only paid in weeks with a competitive league game.** A team that misses the playoffs may pay none in the last two weeks of the season. This is the reason for the "13 Monday paydays" in [Season structure](../studies/season-structure.md).
- **Minimum payroll:** for a share of league TV money, you pay at least a set total salary, even if your players earn less:

  | Division | Minimum payroll |
  |---|---|
  | I | 241.5% of TV money |
  | II | 187% |
  | III | **130%** |
  | IV | 100% |
  | V, VI | 70% |

  **[Inference]** This limits the "keep salaries low" doctrine. Below 130% of our TV money, a lower payroll saves nothing, because the difference is charged anyway. Check our payroll against that floor on the Economy page before turning down a useful salary. After promotion the floor rises to 187%.
- **Merchandise** sales rise with winning, with domestic and self-drafted players (weighted by how good they are), with national-team call-ups, and with league-leading stats.
- **Debt:** a negative balance costs 5% a week. Below −$500k for two weekly updates, the whole roster is put on the transfer list at $0. If that doesn't recover the balance, the manager is fired.
- **Taxes:**
  - Hoarding tax: 10% a week on cash above **$25M**.
  - Overextension tax: charged on teams spending far more than they earn. Salary growth from players you trained is exempt.
- Money you've bid on the transfer list is held back from your available balance until the auction ends.

## Arena · [Arena](https://www.buzzerbeater.com/community/rules.aspx?nav=Arena)

- **Price limits:**

  | Seat type | Price range |
  |---|---|
  | Bleachers | $5–$20 |
  | Lower tier | $18–$70 |
  | Courtside | $50–$200 |
  | Luxury boxes | $400–$1,600 |

- **Capacity limits:** at most 500 courtside seats and 50 luxury boxes.
- Fans buy the most expensive ticket they can afford.
  - Buyers of the expensive seats come win or lose, but they're sensitive to price.
  - Cheap seats fill with fans who follow results.
- Expansion takes time: more seats and more expensive seats take longer to build, and the time estimates tend to be optimistic. Only one expansion can be under way at a time.
- **Arena designs** attract visitors and merchandise revenue even on non-game days, but pay back slowly. There are no refunds on redesigns.
- **Team infrastructure:** five buildings, each with three levels.
  - Buildings: Gym (more cross-training), Training Court (free throws trained during the season), Health & Recovery Center (faster healing), TV & Radio Station (fan spirit, season tickets), Merchandise Store.
  - Cost per building: $500k for level 1, then $300k, then $200k, plus **$5k a week maintenance per level**.
  - Downgrading refunds half the building cost.

See [Arena expansion payback](../studies/arena-expansion-payback.md) and [Arena pricing vs. Division III peers](../studies/arena-pricing-div3.md).

## Fan survey · [Fan Survey](https://www.buzzerbeater.com/community/rules.aspx?nav=FanSurvey)

- The PR manager surveys fans three times a week: 9 questions, rolled into a 0–5 basketball score.
- Fans weigh last season and this season, the cup (top-division fans punish early exits), recent games, the last TV game, and the last game against their chosen rival.
- They also judge transfer activity. Some dislike selling favorites; others dislike a roster that never changes.
- **Boycott:** a team that doesn't win at least one game in each third of the season sells fewer home tickets.
  - The cut depends on cash in the bank: none under $500k, then rising in 3-point steps to **30% above $10M**.
  - It eases by 3 points per home game, and repeat boycotts stack.

**[Inference]** A large cash pile makes a losing run more expensive at the gate.

## Training · [Training](https://www.buzzerbeater.com/community/rules.aspx?nav=Training)

- **Full training needs weekly minutes at the trained position:** 45 at age 18–19, 48 at 20–26, 40 at 27+. There's a one-minute allowance, so 44 is enough for the youngest group. Fewer minutes still train, just more slowly. These thresholds feed the report's training calculator.
- **Team Training** (Game Shape, Free Throws, Stamina) trains the whole roster whether or not players played.
- Training narrower position groups gives faster gains to fewer players. Wider groups spread smaller gains.
- **Faster learners:** younger players, and players already good at related skills. Height helps some skills and hurts others.
- **Potential is a soft cap.** Once a player reaches it, training slows sharply but doesn't stop. The scale runs 0 announcer … 11 all-time great.
- **Cross-training:** part of each week's gain spreads to unrelated skills, roughly 10% for an average player. More one-dimensional players lose more of their main-skill gain.
- **Game shape** suffers from playing too little and from playing too much, and changes build up over weeks. It measures form, not training effectiveness.
- The manual itself suggests training more players than you need and selling the extras.

See [Training doctrine](../studies/training-doctrine.md), [Training coefficients](training_coefficients.md) and [Skill salary costs](../studies/skill-salary-costs.md).

## Tactics and game engine · [Tactics](https://www.buzzerbeater.com/community/rules.aspx?nav=Tactics) · [Game Engine](https://www.buzzerbeater.com/community/rules.aspx?nav=GameEngine)

- **Offenses** differ in focus (inside, outside or balanced) and pace. Slower pace means fewer possessions and better shots, which keeps weaker teams closer. A focus only pays off where you really have the edge: it helps one area but costs the other more.
- **Defenses:**
  - Man-to-man is the baseline.
  - 2-3 zone: inside defense and rebounding at the cost of the perimeter.
  - 3-2 and 1-3-1 zones: the perimeter at the cost of inside defense.
  - Full-court press: forces turnovers at the cost of stamina, defense and rebounding.
  - Box-and-one: puts a man-to-man defender on the opponent's best inside or outside scorer.
- **Game-day preparation:** predicting the opponent's focus and pace correctly gives a real edge. A badly wrong guess hurts more than a near miss, and skipping it is neutral.
- **Coach adjustments** during a game are weaker than starting with the right tactics.
- **Depth chart and substitutions:** "Follow Depth Chart" gives the most control over training minutes.
  - A winning team whose opponent forfeits gets 36 minutes for starters, 10 for backups and 2 for reserves, per slot.
  - The forfeiting team gets no training minutes.
- **Enthusiasm** drifts back toward 5.
  - "Crunch Time" plays harder but costs enthusiasm for a week or two; "Take it Easy" banks some.
  - Playoff games only offer the playoff versions of those two.
  - The cup shares the same enthusiasm meter as the league.
- **Exhaustion** (since season 58): players aged 27+ who get too little rest before the 4th quarter can become exhausted and play far below their level. It doesn't cause injuries.
- **Team ratings by position:**
  - Outside: mostly the guards.
  - Inside: mostly C and PF.
  - Rebounding: C and PF, then SF.
  - Offensive flow: mostly the PG.
  - The matchup rating is points per 100 shots at each position.

## Staff · [Staff](https://www.buzzerbeater.com/community/rules.aspx?nav=Staff2)

- **Essential staff:**
  - Doctor: less severe injuries, slightly faster healing.
  - Trainer: better training.
  - PR manager: more fans and higher prices accepted.
- Levels run from minimal to world-renowned, with diminishing returns.
- **Possible specialties:**
  - Doctor: taping injuries, massage (less game-shape loss from heavy minutes).
  - Trainer: career extension (fewer skill drops for older players), fitness (smaller stamina drops).
  - PR manager: crowd involvement (stronger home advantage), national appeal (weaker opponent home advantage).
- **Secondary staff** (optional): youth trainer (extra training for 18–19-year-olds; only top levels make a real difference), sports psychologist (keeps form up), nutritionist (slows or stops stamina decay).
- **Costs:** replacing or firing staff costs one week's salary in severance. Staff ask for a small raise every week, so review them from time to time.

## Transfers and the draft · [Transfer List](https://www.buzzerbeater.com/community/rules.aspx?nav=TransferList) · [Draft](https://www.buzzerbeater.com/community/rules.aspx?nav=Draft)

- **Auctions** are first-price: you pay what you bid. Each new bid resets the clock to 3 minutes. Neither bids nor listings can be withdrawn.
- **Selling:**
  - Agent fees are lower the longer you've owned the player and the fewer sales you've made in the last 14 weeks.
  - A player must be on your team for 4 days before he can be listed.
  - Server downtime doesn't undo sales, so set the starting price at your true minimum.
- **Acquisition restriction:** players above a salary limit tied to your world rank won't accept your bids. The transfer list page shows the current limit.
- **Transfer price estimate:** based on recent sales of similar players. It's a market reading, not a judgment of the player's quality.
- **Draft scouting** (points carry over between seasons):
  - A scout costs 1 point and gives a box score and a better skill estimate.
  - An interview costs 2 more points and reveals skill grade, potential, height and age.
  - After the All-Star break, two 10-point options open up: the combine (ages and heights of all 48 draftees) and a group demonstration (a free scout of every 1–2 ball prospect).
- **Draft order:** the worst records pick first, and each forfeit costs a place.

The acquisition restriction is the rule behind the $116,779 limit noted in [How long-run winners are built](../top-teams-research/BB_Top_Teams_Strategy_Report.md). That report also covers the post-draft flip.

## Cups and international competitions · [National Tournament](https://www.buzzerbeater.com/community/rules.aspx?nav=Tournament) · [Scrimmages](https://www.buzzerbeater.com/community/rules.aspx?nav=Scrimmages) · [B3](https://www.buzzerbeater.com/community/rules.aspx?nav=B3) · [BB Madness](https://www.buzzerbeater.com/community/rules.aspx?nav=BuzzerMadness)

- **National cup:** single elimination on Thursdays against a random opponent and venue. It pays per win rather than through ticket sales:

  | Round won | Prize |
  |---|---|
  | Final | $300k |
  | Semi-final | $135k |
  | Quarter-final | $100k |
  | Round of 16 | $80k |
  | Round of 32 | $70k |
  | Round of 64 | $60k |
  | Earlier rounds | $50k |

- **Scrimmages:** once a week on Thursday, once you're out of the cup. They don't count in the standings, but they're extra training minutes and experience, and admission is free. Challenges close from Wednesday 12:00 to Friday 22:00 server time.
- **B3:** national champions, Division I league champions and earlier B3 winners (if ranked in the world top 500), plus runners-up to reach 128 teams.
  - Seven qualifier games, then a 64-team knockout, played on Wednesdays at a fixed enthusiasm of 12.
  - Minutes don't count for training or game shape, and there's no gate revenue.
  - Prizes range from $50k per qualifier win up to $500k for winning the final.
- **BuzzerBeater Madness:** every team not in B3, in tiers by world rank. The format and rules are the same as B3, with smaller prizes ($25k per qualifier win up to $200k). The top-tier winner qualifies for the next B3.

## Ratings scales · [Ratings](https://www.buzzerbeater.com/community/rules.aspx?nav=Nomenclature)

- **Skills** use a 20-step word scale, from atrocious (1) to legendary (20). The report's skill tables reproduce it with the game's own colors.
- **Potential** runs 0–11 and **enthusiasm** 1–15. **Staff** have seven levels.
- The manual itself warns that **DMI** and **best position** are rough guides and not to over-read them.

## Other chapters

Community and account rules, not strategy: [Rules of Conduct](https://www.buzzerbeater.com/community/rules.aspx?nav=RulesOfConduct), [Overview Page](https://www.buzzerbeater.com/community/rules.aspx?nav=Overview), [News](https://www.buzzerbeater.com/community/rules.aspx?nav=News), [Forums](https://www.buzzerbeater.com/community/rules.aspx?nav=Forums), [Roster](https://www.buzzerbeater.com/community/rules.aspx?nav=Roster), [Bookmarks](https://www.buzzerbeater.com/community/rules.aspx?nav=Bookmarks), [BB-Mail](https://www.buzzerbeater.com/community/rules.aspx?nav=Messages), [All-Star Game](https://www.buzzerbeater.com/community/rules.aspx?nav=AllStarGame), [National Teams](https://www.buzzerbeater.com/community/rules.aspx?nav=NationalTeams), [Utopia League](https://www.buzzerbeater.com/community/rules.aspx?nav=Utopia). The whole manual on one page: [All the goodies](https://www.buzzerbeater.com/community/rules.aspx?nav=everything).
