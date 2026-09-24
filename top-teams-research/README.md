# Top teams research

How long-run BuzzerBeater winners are built, and what it means for Sharpshooters (#32988).

- [BB_Top_Teams_Strategy_Report.md](BB_Top_Teams_Strategy_Report.md): the full report (Venomous Scorpions, I Love Tehran, Młoty Stargard, and Młoty's teenage flips priced against salaries).
- [Mloty_Stargard_teen_flips.xlsx](Mloty_Stargard_teen_flips.xlsx) / [.csv](mloty_stargard_teen_flips.csv): the 134 flips with prices and salaries.

## Rebuilding the data

```bash
pip install requests openpyxl
python scripts/fetch_salary_history.py    # public player pages, no login
BB_LOGIN=... BB_CODE=... python scripts/fetch_seasons.py   # official API
python scripts/add_salary_columns.py      # adds salary columns to the CSV and workbook
python scripts/salary_vs_price.py         # prints the report's section 5 figures
```
