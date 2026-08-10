"""
Permutation test for the de-baselined Test B lean.

Question it answers
-------------------
The de-baselined run showed the stress regime sitting on proportionally
stress-heavier days, strongest at n=4 (share ratio 1.031, z_in-z_out 0.261).
Those effects are small. This asks: is that bigger than you'd get by chance
from ANY day-set of the same size and clustering?

Null model (circular rotation)
-------------------------------
For each n we take the REAL stress-day mask, then rotate it by a random
offset around the calendar many times. Rotation preserves exactly:
  * the number of stress days, and
  * their run-length structure (autocorrelation / clustering),
while destroying their alignment to the GDELT stress series. So the null is
"a stress-shaped block of days placed at a random point in 2024." If the real
placement scores above almost all rotations, the alignment to news-stress is
real, not an artifact of how many/how clustered the stress days are.

Reports, per n, for BOTH the share ratio and the z_in-z_out difference:
  observed value, null mean, and one-sided empirical p = P(null >= observed).

Run:
    python -m src.regime_event_permutation --gdelt processed/gdelt_2024_clean.csv
Optional:
    --iters 5000     number of rotations (default 5000)
    --window 20      rolling window for the z-score (match the other script)
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
    args = ap.parse_args()
    nlist = [int(x) for x in args.nlist.split(",")]
    rng = np.random.default_rng(args.seed)

    cfg = load_config()
    gdelt = load_gdelt(args.gdelt).sort_index().copy()
    scores = load_scores_2024()

    # de-baselined measures, same construction as the normalized script
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
    print("=" * 78)
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

        # observed
        obs_share = share_ratio(pd.Series(share_c), pd.Series(sd))
        obs_z = z_diff(pd.Series(z_c), pd.Series(sd))

        # null via circular rotation of the real mask
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
    print("  p<.05  : the stress regime's alignment to news-stress is real, not a")
    print("           by-product of how many or how clustered the stress days are.")
    print("  p>.10  : the small lean is within chance -> report GENUINE DISTINCTNESS")
    print("           (macro regimes capture a different axis than news attention).")
    print("  Rotation preserves count + run-structure, so this null is honest about")
    print("  the autocorrelation the earlier CAVEAT warned about.")
    print("=" * 78)


if __name__ == "__main__":
    main()
