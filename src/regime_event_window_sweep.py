"""
Window-robustness sweep for the n=4 event-alignment result.

Why this exists
---------------
The significant result (n=4, z_in-z_out, p=0.000) used a 20-day trailing
window to define "unusually high stress news." 20 was an arbitrary choice.
A real signal should survive nearby choices; a knife-edge artifact won't.

This re-runs the SAME circular-rotation permutation test at several windows
(10, 15, 20, 25, 30, 40, 60 by default) for each n, on identical regime
labels, and reports observed z_in-z_out and its permutation p-value in one
grid. Read down the n=4 column: if p stays small across windows, the finding
is robust to the window choice; if only window=20 is small, it's fragile.

NOTE ON MULTIPLE TESTS: this grid is a *stability check* of one already-
established result across a nuisance knob -- it is NOT 21 fresh hypotheses.
Don't Bonferroni-correct across the whole grid; the question is whether the
n=4 conclusion holds as the window moves, not whether some cell somewhere
dips below a line.

Run:
    python -m src.regime_event_window_sweep --gdelt processed/gdelt_2024_clean.csv
Optional:
    --windows 10,15,20,25,30,40,60
    --iters 5000
    --nlist 3,4,5
"""
import argparse

import numpy as np
import pandas as pd

from src.regime_event_alignment import (
    load_config,
    load_gdelt,
    load_scores_2024,
    fit_labels,
)


def pick_stress_regime(labels, scores):
    means = {r: scores.loc[labels == r, "PC2"].mean() for r in labels.unique()}
    return max(means, key=means.get)


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
    args = ap.parse_args()
    windows = [int(x) for x in args.windows.split(",")]
    nlist = [int(x) for x in args.nlist.split(",")]
    rng = np.random.default_rng(args.seed)

    cfg = load_config()
    gdelt = load_gdelt(args.gdelt).sort_index().copy()
    scores = load_scores_2024()
    raw = gdelt["stress_count"].astype(float)

    print("=" * 78)
    print(f"WINDOW-ROBUSTNESS SWEEP  (z_in - z_out, {args.iters} rotations per cell)")
    print("=" * 78)
    print("cell = observed z-diff  (permutation p);  * p<.05   ** p<.008 (strict)")
    header = "window | " + " | ".join(f"     n={n}      " for n in nlist)
    print(header)
    print("-" * len(header))

    # cache labels + stress mask per n (GMM fit once per n)
    per_n = {}
    for n in nlist:
        labels, _ = fit_labels(scores, n, cfg)
        sr = pick_stress_regime(labels, scores)
        stress_days = (labels == sr)
        common = labels.index.intersection(gdelt.index)
        sd = stress_days.reindex(common).fillna(False).to_numpy()
        per_n[n] = (common, sd)

    # track how many windows each n clears
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
                star = "**"
                clears_strict[n] += 1
                clears05[n] += 1
            elif p < 0.05:
                star = "* "
                clears05[n] += 1
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
    print("HOW TO READ")
    print("  Read DOWN a column. A robust finding stays significant across windows;")
    print("  a fragile one lights up at only one window.")
    print("  * p<.05 (standard)   ** p<.008 (strict, survives 6-way correction)")
    print("  This is a stability check of the n=4 result, NOT 21 new hypotheses --")
    print("  judge by whether the n=4 column holds, not by any single lucky cell.")
    print("=" * 78)


if __name__ == "__main__":
    main()
