"""era_resid.py -- T-H (residual momentum / reversal) by era, under the family null (prereg_subperiod_audit.md, group B, item B8).

T-H (23 Oct) asked whether the part of gold's move the named factors do not explain predicts the next move; it was pooled, FAIL on five
assets. This re-runs it with era as a grid axis and the best-of-sweep null, so 'the era in which the leftover predicts' is searched and judged.

  python -m src.era_resid --asset GLD [--drop-late]      # residual from a rolling 252-session factor fit refit every 20 sessions; signal = cumulative
                                                         # residual over w in {5,10,20,40,60}; forward h in {5,10,20,40,60}; non-overlapping; era axis;
                                                         # statistic = rank IC (continuation positive, reversal negative, |IC| searched); null = residual time-shifted
Output docs/era_resid_<asset>.md (+ _sweep.md, .json). Nothing here writes the register.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.sweep import grid, run, write_md, shift_null
from src.era_factors import ERAS, era_of, fit

DOCS = Path("docs")


def residuals(X: np.ndarray, y: np.ndarray, window: int = 252, refit: int = 20) -> np.ndarray:
    e = np.full(len(y), np.nan); b = None
    for s in range(window, len(y), refit):
        b, _, _ = fit(X[s - window:s], y[s - window:s]); a = y[s - window:s].mean() - X[s - window:s].mean(0) @ b
        hi = min(s + refit, len(y)); e[s:hi] = y[s:hi] - a - X[s:hi] @ b
    return e


def rank_ic(sig: np.ndarray, fut: np.ndarray) -> float:
    ok = np.isfinite(sig) & np.isfinite(fut)
    if ok.sum() < 30: return np.nan
    return float(pd.Series(sig[ok]).rank().corr(pd.Series(fut[ok]).rank()))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--asset", default="GLD"); ap.add_argument("--drop-late", action="store_true"); ap.add_argument("--n-null", type=int, default=200)
    a = ap.parse_args()
    from src.factor_attribution import factors, returns
    r = returns(a.asset); r.index = pd.to_datetime(r.index); F = factors(r.index); F.index = pd.to_datetime(F.index)
    if a.drop_late:
        late = [c for c in F.columns if F[c].first_valid_index() is not None and F[c].first_valid_index() > pd.Timestamp("2006-01-01")]; F = F.drop(columns=late); print("dropped:", late)
    d = pd.concat([r.rename("y"), F], axis=1).dropna(); names = [c for c in d.columns if c != "y"]; X, y, dates = d[names].to_numpy(float), d["y"].to_numpy(float), d.index
    e = residuals(X, y); era = np.array([era_of(t) for t in dates]); cum_y = np.concatenate([[0], np.cumsum(y)])
    n = len(y)
    def stat(dd, c):
        ee = np.asarray(dd["e"]); w, h = c["w"], c["h"]; cs = np.concatenate([[0], np.nancumsum(np.nan_to_num(ee))])
        starts = np.arange(w, n - h - 1, h)                                     # non-overlapping forward windows
        sig = cs[starts] - cs[starts - w]; fut = cum_y[starts + 1 + h] - cum_y[starts + 1]
        if c["era"] != "all": m = era[starts] == c["era"]; sig, fut = sig[m], fut[m]
        ic = rank_ic(sig, fut); return (abs(ic) if np.isfinite(ic) else np.nan), int(np.isfinite(sig).sum())
    cells = grid(w=[5, 10, 20, 40, 60], h=[5, 10, 20, 40, 60], era=["all"] + [x[0] for x in ERAS if (era == x[0]).sum() >= 250])
    sw = run(cells, stat, dict(e=e), shift_null("e", 250), n_null=a.n_null, seed=0, label=f"T-H by era — |rank IC| of the cumulative residual (w) on the next h sessions ({a.asset})")
    # signed table for the reading
    rows = []
    for c in cells:
        ee = e; cs = np.concatenate([[0], np.nancumsum(np.nan_to_num(ee))]); starts = np.arange(c["w"], n - c["h"] - 1, c["h"]); sig = cs[starts] - cs[starts - c["w"]]; fut = cum_y[starts + 1 + c["h"]] - cum_y[starts + 1]
        if c["era"] != "all": m = era[starts] == c["era"]; sig, fut = sig[m], fut[m]
        rows.append(dict(**c, ic=rank_ic(sig, fut), n=int(np.isfinite(sig).sum())))
    tab = pd.DataFrame(rows)
    out = DOCS / f"era_resid_{a.asset}.md"
    L = [f"# T-H by era — residual momentum / reversal, {a.asset} ({dates[0].date()} → {dates[-1].date()}; {len(names)} factors)", "",
         "Signal: the residual of a rolling 252-session factor fit (refit every 20 sessions) summed over the past w sessions. Target: the next h sessions, non-overlapping. Positive IC = continuation, negative = reversal; the search is over |IC| with era as an axis.", "",
         f"Best `{sw.best}` |IC| {sw.best_stat:.3f} vs best-of-sweep null q95 {sw.q95:.3f}; **p_family {sw.p_family:.3f}**; survivors {len(sw.survivors)}.", "",
         "## Signed rank IC (pooled)", "", "| w \\ h | " + " | ".join(str(h) for h in (5, 10, 20, 40, 60)) + " |", "|---|---|---|---|---|---|"]
    for w in (5, 10, 20, 40, 60):
        L.append(f"| {w} | " + " | ".join(f"{tab[(tab.w == w) & (tab.h == h) & (tab.era == 'all')]['ic'].iloc[0]:+.3f}" for h in (5, 10, 20, 40, 60)) + " |")
    L += ["", "Per-era signed values are in the JSON; the pooled T-H verdict of 23 Oct (FAIL ×5) stands unless a survivor appears above."]
    out.write_text("\n".join(L) + "\n"); write_md(sw, DOCS / f"era_resid_{a.asset}_sweep.md", axis_rows="w", axis_cols="h", fmt="{:.3f}")
    out.with_suffix(".json").write_text(json.dumps(dict(sweep=sw.to_json(), signed=json.loads(tab.to_json(orient="records"))), indent=1, default=float))
    print(f"T-H by era ({a.asset}): best {sw.best} |IC| {sw.best_stat:.3f}, q95 {sw.q95:.3f}, p_family {sw.p_family:.3f}, survivors {len(sw.survivors)} -> {out}")


if __name__ == "__main__":
    main()
