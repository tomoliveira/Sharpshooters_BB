"""Layer 2 of the ratings-impact study: do team match ratings explain and
predict the scoreboard, and how many points is one rating point worth?

Reads docs/report.db (table match_ratings), keeps matches where both teams'
rows are cached, and writes layer2_results.json next to this script.

Run from the repo root:  python3 studies/ratings-impact/layer2_team_ratings.py
Needs only numpy and pandas.
"""
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "docs" / "report.db"
OUT = Path(__file__).resolve().parent / "layer2_results.json"

RATINGS = ["outside_scoring", "inside_scoring", "outside_defense",
           "inside_defense", "rebounding", "offensive_flow"]
SEED = 20261110
CV_REPEATS = 200
CV_FOLDS = 5
TEST_SHARE = 0.30          # chronological holdout: last 30% of matches
MIN_PRIOR_GAMES = 3        # pre-game forecast needs this many earlier games per team


def load_pairs():
    con = sqlite3.connect(DB)
    d = pd.read_sql("SELECT * FROM match_ratings", con)
    con.close()
    both = d.groupby("matchid").filter(lambda t: len(t) == 2)
    home = both[both.is_home == 1].set_index("matchid")
    away = both[both.is_home == 0].set_index("matchid")
    m = home.join(away, lsuffix="_h", rsuffix="_a", how="inner")
    assert (m.team_score_h == m.opp_score_a).all() and (m.opp_score_h == m.team_score_a).all()
    m["margin"] = m.team_score_h - m.team_score_a
    for r in RATINGS:
        m["d_" + r] = m[r + "_h"] - m[r + "_a"]
    m = m.reset_index().sort_values(["match_date_h", "matchid"]).reset_index(drop=True)
    return d, m


def ols(X, y):
    """OLS with intercept column already in X. Returns beta, se, residuals."""
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    n, k = X.shape
    sigma2 = resid @ resid / (n - k)
    se = np.sqrt(np.diag(sigma2 * np.linalg.inv(X.T @ X)))
    return beta, se, resid


def design(df, cols):
    return np.column_stack([np.ones(len(df))] + [df[c].to_numpy(float) for c in cols])


def metrics(y, pred):
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return {
        "r2": 1 - ss_res / ss_tot,
        "rmse": float(np.sqrt(ss_res / len(y))),
        "mae": float(np.abs(y - pred).mean()),
        "winner_accuracy": float(((pred > 0) == (y > 0)).mean()),
        "n": int(len(y)),
    }


MODELS = {
    "home_only": [],
    "sum_of_rating_diffs": ["d_sum"],            # equal weight on all six
    "six_rating_diffs": ["d_" + r for r in RATINGS],
}


def cross_validate(m, cols, rng):
    y = m.margin.to_numpy(float)
    X = design(m, cols)
    preds_all = []
    for _ in range(CV_REPEATS):
        idx = rng.permutation(len(m))
        pred = np.empty(len(m))
        for f in range(CV_FOLDS):
            test = idx[f::CV_FOLDS]
            train = np.setdiff1d(idx, test)
            b, *_ = np.linalg.lstsq(X[train], y[train], rcond=None)
            pred[test] = X[test] @ b
        preds_all.append(metrics(y, pred))
    keys = ["r2", "rmse", "mae", "winner_accuracy"]
    return {k: {"mean": float(np.mean([p[k] for p in preds_all])),
                "p05": float(np.percentile([p[k] for p in preds_all], 5)),
                "p95": float(np.percentile([p[k] for p in preds_all], 95))} for k in keys}


def chrono_holdout(m, cols):
    # split on a date boundary so no match day sits in both sets
    cut_date = m.match_date_h.iloc[int(round(len(m) * (1 - TEST_SHARE)))]
    train, test = m[m.match_date_h < cut_date], m[m.match_date_h >= cut_date]
    b, *_ = np.linalg.lstsq(design(train, cols), train.margin.to_numpy(float), rcond=None)
    pred = design(test, cols) @ b
    out = metrics(test.margin.to_numpy(float), pred)
    out["train_dates"] = [train.match_date_h.min(), train.match_date_h.max()]
    out["test_dates"] = [test.match_date_h.min(), test.match_date_h.max()]
    return out


def pregame_forecast(rows, m):
    """Walk-forward: before each match, average each team's ratings over its
    earlier games in the table (any opponent, unpaired rows included), take
    home-minus-away differences, and apply six-rating coefficients fitted only
    on matches played before that date. Baseline: difference in each team's
    average point margin over those same earlier games, plus home edge."""
    rows = rows.copy()
    rows["pm"] = rows.team_score - rows.opp_score
    out = []
    cols = ["d_" + r for r in RATINGS]
    for _, g in m.iterrows():
        date = g.match_date_h
        prev_h = rows[(rows.team_id == g.team_id_h) & (rows.match_date < date)]
        prev_a = rows[(rows.team_id == g.team_id_a) & (rows.match_date < date)]
        train = m[m.match_date_h < date]
        if len(prev_h) < MIN_PRIOR_GAMES or len(prev_a) < MIN_PRIOR_GAMES or len(train) < 40:
            continue
        b, *_ = np.linalg.lstsq(design(train, cols), train.margin.to_numpy(float), rcond=None)
        x = np.r_[1.0, [prev_h[r].mean() - prev_a[r].mean() for r in RATINGS]]
        home_edge = float(train.margin.mean())
        out.append({
            "matchid": g.matchid,
            "margin": g.margin,
            "pred_ratings": float(x @ b),
            "pred_point_diff": home_edge + prev_h.pm.mean() - prev_a.pm.mean(),
        })
    f = pd.DataFrame(out)
    y = f.margin.to_numpy(float)
    return {
        "ratings_model": metrics(y, f.pred_ratings.to_numpy()),
        "point_diff_baseline": metrics(y, f.pred_point_diff.to_numpy()),
        "first_date": m[m.matchid.isin(f.matchid)].match_date_h.min(),
    }


def main():
    rows, m = load_pairs()
    m["d_sum"] = m[["d_" + r for r in RATINGS]].sum(axis=1)
    rng = np.random.default_rng(SEED)
    y = m.margin.to_numpy(float)

    res = {"data": {
        "paired_matches": int(len(m)),
        "team_game_rows": int(len(rows)),
        "teams": int(rows.team_id.nunique()),
        "date_range": [m.match_date_h.min(), m.match_date_h.max()],
        "match_types": m.match_type_h.value_counts().to_dict(),
        "margin_sd": float(m.margin.std()),
        "home_win_share": float((m.margin > 0).mean()),
    }}

    cols = ["d_" + r for r in RATINGS]
    b, se, resid = ols(design(m, cols), y)
    sd = m[cols].std().to_numpy()
    res["full_sample_fit"] = {
        "in_sample": metrics(y, y - resid),
        "intercept_home_edge": {"coef": float(b[0]), "se": float(se[0])},
        "points_per_rating_point": {
            r: {"coef": float(b[i + 1]), "se": float(se[i + 1]),
                "ci95": [float(b[i + 1] - 1.96 * se[i + 1]), float(b[i + 1] + 1.96 * se[i + 1])],
                "points_per_1sd_of_diff": float(b[i + 1] * sd[i])}
            for i, r in enumerate(RATINGS)},
        "residual_sd": float(np.sqrt(resid @ resid / (len(y) - len(b)))),
    }
    bs, ses, rs = ols(design(m, ["d_sum"]), y)
    res["full_sample_fit"]["sum_model_points_per_rating_point"] = {"coef": float(bs[1]), "se": float(ses[1])}
    # bootstrap: how stable is the ranking of the six coefficients?
    X6 = design(m, cols)
    boots = []
    for _ in range(2000):
        i = rng.integers(0, len(m), len(m))
        bb, *_ = np.linalg.lstsq(X6[i], y[i], rcond=None)
        boots.append(bb[1:])
    boots = np.array(boots)
    res["bootstrap_coefficients"] = {
        r: {"p05": float(np.percentile(boots[:, j], 5)), "median": float(np.median(boots[:, j])),
            "p95": float(np.percentile(boots[:, j], 95)),
            "share_largest": float((boots.argmax(axis=1) == j).mean()),
            "share_below_zero": float((boots[:, j] < 0).mean())}
        for j, r in enumerate(RATINGS)}
    # rating-sum gap needed for a given in-game win probability (normal residuals)
    k, s_ = float(bs[1]), float(np.sqrt(rs @ rs / (len(y) - 2)))
    z = {"60%": 0.2533, "75%": 0.6745, "90%": 1.2816, "95%": 1.6449}
    res["sum_gap_for_win_probability"] = {p_: round(zz * s_ / k, 2) for p_, zz in z.items()}
    # each team's season-average ratings vs the league average, in points/game
    league = rows[RATINGS].mean()
    teams = {}
    # group by id: some ids carry several names over the season (renames)
    for _, g in rows.sort_values("match_date").groupby("team_id"):
        name = g.team_name.iloc[-1]
        gap = g[RATINGS].mean() - league
        teams[name] = {
            "games": int(len(g)),
            "names_seen": sorted(g.team_name.unique().tolist()),
            "avg_margin": float((g.team_score - g.opp_score).mean()),
            "rating_gap_vs_league": {r: round(float(gap[r]), 2) for r in RATINGS},
            "points_vs_league": {r: round(float(gap[r] * b[i + 1]), 1) for i, r in enumerate(RATINGS)},
        }
    res["team_profiles"] = teams
    res["rating_diff_correlations"] = m[cols].corr().round(2).to_dict()

    res["cv_5fold_x200"] = {name: cross_validate(m, c, rng) for name, c in MODELS.items()}
    res["chronological_holdout"] = {name: chrono_holdout(m, c) for name, c in MODELS.items()}
    res["pregame_forecast_walk_forward"] = pregame_forecast(rows, m)

    OUT.write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps(res, indent=2, default=str))


if __name__ == "__main__":
    main()
