"""Print the salary-vs-price findings used in section 5 of the report.

Reads the salary columns added by add_salary_columns.py.
"""
import csv
import math
import statistics as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = list(csv.DictReader(open(ROOT / "mloty_stargard_teen_flips.csv", encoding="utf-8")))


def num(r, k):
    return float(r[k]) if r[k] else None


def spearman(a, b):
    def ranks(v):
        order = sorted(range(len(v)), key=v.__getitem__)
        out = [0] * len(v)
        for rank, i in enumerate(order):
            out[i] = rank
        return out
    ra, rb = ranks(a), ranks(b)
    ma, mb = st.mean(ra), st.mean(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    return cov / math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))


BUY, SALE = "Buy price ($)", "Sale price ($)"
SB, SS, PEAK = "Salary in season bought ($/wk)", "Salary in season sold ($/wk)", "Highest salary ($/wk)"

sb = [num(r, SB) for r in rows]
print(f"Salary in season bought: median ${st.median(sb):,.0f}, range ${min(sb):,.0f}-${max(sb):,.0f}")
print(f"Salary changed during hold: {sum(r[SB] != r[SS] for r in rows)} of {len(rows)}")
print(f"Buy / salary median {st.median(num(r, 'Buy ÷ salary') for r in rows):.1f}x, "
      f"sale / salary quartiles {[round(q) for q in st.quantiles([num(r, 'Sale ÷ salary') for r in rows], n=4)]}")
print(f"Spearman salary vs buy {spearman(sb, [num(r, BUY) for r in rows]):.2f}, "
      f"vs sale {spearman(sb, [num(r, SALE) for r in rows]):.2f}")

print("\nBy salary in season bought")
for lo, hi in [(0, 3000), (3000, 3600), (3600, 4000), (4000, 5000), (5000, math.inf)]:
    g = [r for r in rows if lo <= num(r, SB) < hi]
    print(f"  ${lo:,}-{'' if hi == math.inf else f'${hi:,}'}: n={len(g)}, "
          f"median buy ${st.median(num(r, BUY) for r in g):,.0f}, median sale ${st.median(num(r, SALE) for r in g):,.0f}")

old = [r for r in rows if r["Bought on"][:4] <= "2020"]
peak = [num(r, PEAK) for r in old]
print(f"\nBought 2020 or earlier (n={len(old)}): median highest salary ${st.median(peak):,.0f}, "
      f"quartiles {[round(q) for q in st.quantiles(peak, n=4)]}")
print(f"  reached $20k: {sum(p >= 20000 for p in peak)}, $50k: {sum(p >= 50000 for p in peak)}, "
      f"$100k: {sum(p >= 100000 for p in peak)}")
old.sort(key=lambda r: num(r, SALE))
n = len(old)
for i, name in enumerate(["bottom", "middle", "top"]):
    g = old[i * n // 3:(i + 1) * n // 3]
    print(f"  {name} third by sale price (${num(g[0], SALE):,.0f}-${num(g[-1], SALE):,.0f}): "
          f"median highest salary ${st.median(num(r, PEAK) for r in g):,.0f}")
