"""
Permutation test for the de-baselined Test B lean.

For each n we take the REAL stress-day mask, rotate it by a random offset
around the calendar many times, and compare the observed share-ratio and
z_in-z_out gap against that null. p = P(null >= obs); small p => the stress
regime's alignment to news-stress is real, not an artifact of clustering.

v2: the stress regime is selected via the DATA-DRIVEN stress axis
(src.stress_axis.stress_regime_id) -- the PC most correlated with VIX --
instead of a hard-coded 'PC2', so it survives PCA renumbering.

Run:
    python -m src.regime_event_permutation --gdelt processed/gdelt_2024_clean.csv
Optional: --iters 5000  --window 20  --nlist 3,4,5
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
    # data-driven: stress = regime highest on the VIX-correlated PC
    return stress_regime_id(labels, scores)


def share_ratio(measure, mask):
    a = measure[mask].mean()
    b = measure[~mask].mean()
    return a / b if b else np.nan


def z_diff(z, mask):
    return z[mask].mean() - z[~mask].mean()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gdelt", required=True)
    ap.add_argument("--iters", type=int, default=5000)
    ap.add_argument("--window", type=int, default=20)
    ap.add_argument("--nlist", default="3,4,5")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--start", default=None, help="override window start (YYYY-MM-DD)")
    ap.add_argument("--end", default=None, help="override window end (YYYY-MM-DD)")
    args = ap.parse_args()
    nlist = [int(x) for x in args.nlist.split(",")]
    rng = np.random.default_rng(args.seed)

    cfg = load_config()
    gdelt = load_gdelt(args.gdelt).sort_index().copy()
    start = args.start or gdelt.index.min()
    end = args.end or gdelt.index.max()
    scores = load_scores_range(start, end)

    raw = gdelt["stress_count"].astype(float)
    if "total_docs" in gdelt.columns and (gdelt["total_docs"] > 0).any():
        share = raw / gdelt["total_docs"].replace(0, np.nan).astype(float)
    else:
        raise SystemExit("total_docs missing/zero -> cannot build share measure.")
    w = max(args.window, 5)
    rm = raw.rolling(w, min_periods=max(5, w // 2)).mean()
    rs = raw.rolling(w, min_periods=max(5, w // 2)).std()
    zc = (raw - rm) / rs.replace(0, np.nan)

    print("=" * 78)
    print(f"PERMUTATION TEST (circular rotation, {args.iters} iters) -- de-baselined Test B")
    print("  (stress regime selected via data-driven VIX axis)")
    print("=" * 78)
    print(f"window {pd.Timestamp(start).date()} -> {pd.Timestamp(end).date()}  |  "
          f"gdelt {len(gdelt)}d, scores {len(scores)}d, "
          f"overlap {len(scores.index.intersection(gdelt.index))}d")
    print("-" * 78)
    print(f"{'n':>3} | {'measure':<12} | {'observed':>9} | {'null mean':>9} | "
          f"{'p (>=obs)':>9} | verdict")
    print("-" * 78)

    for n in nlist:
        labels, _ = fit_labels(scores, n, cfg)
        sr = pick_stress_regime(labels, scores)
        stress_days = (labels == sr)

        common = labels.index.intersection(gdelt.index)
        sd = stress_days.reindex(common).fillna(False).to_numpy()
        share_c = share.loc[common].to_numpy()
        z_c = zc.loc[common].to_numpy()
        m = len(common)

        obs_share = share_ratio(pd.Series(share_c), pd.Series(sd))
        obs_z = z_diff(pd.Series(z_c), pd.Series(sd))

        null_share = np.empty(args.iters)
        null_z = np.empty(args.iters)
        offsets = rng.integers(1, m, size=args.iters)
        share_ser = pd.Series(share_c)
        z_ser = pd.Series(z_c)
        for i, off in enumerate(offsets):
            rot = np.roll(sd, off)
            rmask = pd.Series(rot)
            null_share[i] = share_ratio(share_ser, rmask)
            null_z[i] = z_diff(z_ser, rmask)

        p_share = (np.sum(null_share >= obs_share) + 1) / (args.iters + 1)
        p_z = (np.sum(null_z >= obs_z) + 1) / (args.iters + 1)

        def verdict(p):
            if p < 0.05:
                return "significant (p<.05)"
            if p < 0.10:
                return "marginal (p<.10)"
            return "not distinguishable from chance"

        print(f"{n:>3} | {'share ratio':<12} | {obs_share:>9.3f} | "
              f"{np.nanmean(null_share):>9.3f} | {p_share:>9.3f} | {verdict(p_share)}")
        print(f"{n:>3} | {'z_in - z_out':<12} | {obs_z:>9.3f} | "
              f"{np.nanmean(null_z):>9.3f} | {p_z:>9.3f} | {verdict(p_z)}")
        print("-" * 78)

    print("HOW TO READ")
    print("  p = fraction of random rotations scoring >= the real placement.")
    print("  p<.05 : alignment to news-stress is real, not a clustering artifact.")
    print("=" * 78)


if __name__ == "__main__":
    main()
