"""
Window-robustness sweep for the n=4 event-alignment result.

Re-runs the circular-rotation permutation test at several rolling windows for
each n, on identical regime labels, reporting observed z_in-z_out and its p.
Read down the n=4 column: robust if p stays small across windows.

v2: stress regime selected via the DATA-DRIVEN stress axis
(src.stress_axis.stress_regime_id) instead of hard-coded 'PC2'.

Run:
    python -m src.regime_event_window_sweep --gdelt processed/gdelt_2024_clean.csv
Optional: --windows 10,15,20,25,30,40,60  --iters 5000  --nlist 3,4,5
"""
import argparse

import numpy as np
import pandas as pd

from src.regime_event_alignment import (
    load_config,
    load_gdelt,
    load_scores_range,
    fit_labels,
)
from src.stress_axis import stress_regime_id


def pick_stress_regime(labels, scores):
    return stress_regime_id(labels, scores)


def z_series(raw, w):
    w = max(w, 5)
    rm = raw.rolling(w, min_periods=max(5, w // 2)).mean()
    rs = raw.rolling(w, min_periods=max(5, w // 2)).std()
    return (raw - rm) / rs.replace(0, np.nan)


def z_diff(zvals, mask):
    return np.nanmean(zvals[mask]) - np.nanmean(zvals[~mask])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gdelt", required=True)
    ap.add_argument("--windows", default="10,15,20,25,30,40,60")
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--nlist", default="3,4,5")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--start", default=None, help="override window start (YYYY-MM-DD)")
    ap.add_argument("--end", default=None, help="override window end (YYYY-MM-DD)")
    args = ap.parse_args()
    windows = [int(x) for x in args.windows.split(",")]
    nlist = [int(x) for x in args.nlist.split(",")]
    rng = np.random.default_rng(args.seed)

    cfg = load_config()
    gdelt = load_gdelt(args.gdelt).sort_index().copy()
    start = args.start or gdelt.index.min()
    end = args.end or gdelt.index.max()
    scores = load_scores_range(start, end)
    raw = gdelt["stress_count"].astype(float)

    print("=" * 78)
    print(f"WINDOW-ROBUSTNESS SWEEP  (z_in - z_out, {args.iters} rotations per cell)")
    print("  (stress regime selected via data-driven VIX axis)")
    print("=" * 78)
    print(f"window {pd.Timestamp(start).date()} -> {pd.Timestamp(end).date()}  |  "
          f"overlap {len(scores.index.intersection(gdelt.index))}d")
    print("cell = observed z-diff  (permutation p);  * p<.05   ** p<.008 (strict)")
    header = "window | " + " | ".join(f"     n={n}      " for n in nlist)
    print(header)
    print("-" * len(header))

    per_n = {}
    for n in nlist:
        labels, _ = fit_labels(scores, n, cfg)
        sr = pick_stress_regime(labels, scores)
        stress_days = (labels == sr)
        common = labels.index.intersection(gdelt.index)
        sd = stress_days.reindex(common).fillna(False).to_numpy()
        per_n[n] = (common, sd)

    clears05 = {n: 0 for n in nlist}
    clears_strict = {n: 0 for n in nlist}

    for w in windows:
        zc_full = z_series(raw, w)
        row_cells = []
        for n in nlist:
            common, sd = per_n[n]
            zvals = zc_full.loc[common].to_numpy()
            obs = z_diff(zvals, sd)
            m = len(sd)
            offsets = rng.integers(1, m, size=args.iters)
            null = np.empty(args.iters)
            for i, off in enumerate(offsets):
                null[i] = z_diff(zvals, np.roll(sd, off))
            p = (np.sum(null >= obs) + 1) / (args.iters + 1)
            if p < 0.008:
                star = "**"; clears_strict[n] += 1; clears05[n] += 1
            elif p < 0.05:
                star = "* "; clears05[n] += 1
            else:
                star = "  "
            row_cells.append(f"{obs:+.3f} ({p:.3f}){star}")
        print(f"{w:>6} | " + " | ".join(row_cells))

    print("-" * len(header))
    print(f"{'clears p<.05':>6} | " + " | ".join(
        f"  {clears05[n]}/{len(windows)} windows " for n in nlist))
    print(f"{'p<.008':>6} | " + " | ".join(
        f"  {clears_strict[n]}/{len(windows)} windows " for n in nlist))
    print("\n" + "=" * 78)
    print("Read DOWN a column. Robust finding stays significant across windows.")
    print("=" * 78)


if __name__ == "__main__":
    main()
