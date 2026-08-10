"""
src/regime_event_alignment.py

Non-circular validation of the regime engine against independent GDELT event data.

Tests, for each candidate regime count (3, 4, 5):
  Test A - Transition alignment: do regime-transition days show higher GDELT
           event density (monetary + stress) than non-transition days?
  Test B - Stress-regime alignment: does the regime with the highest mean PC2
           (the "stress" regime) sit on days with elevated GDELT stress density?
  Test C - FOMC overlay: do the GDELT monetary spikes land on real FOMC dates?
           (FOMC dates are USER-VERIFIED against federalreserve.gov, not assumed.)

The regime count that aligns best with independent events is the empirically
supported choice - this is the tie-breaker for the n decision.

Run from project root:
    python -m src.regime_event_alignment --gdelt path/to/gdelt_2024_clean.csv
"""

import argparse
import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

from src.data_io import load_config, PROCESSED_DIR

CLUSTERING_PCS = ["PC1", "PC2", "PC3"]

# 2024 FOMC decision dates (second day of each meeting).
# *** USER MUST VERIFY these against federalreserve.gov before trusting results. ***
FOMC_2024 = [
    "2024-01-31", "2024-03-20", "2024-05-01", "2024-06-12",
    "2024-07-31", "2024-09-18", "2024-11-07", "2024-12-18",
]


def load_gdelt(path):
    df = pd.read_csv(path, parse_dates=["day"])
    df = df.set_index("day").sort_index()
    # z-score the event densities for comparability
    for c in ["monetary_count", "stress_count"]:
        df[c + "_z"] = (df[c] - df[c].mean()) / df[c].std()
    df["event_z"] = df[["monetary_count_z", "stress_count_z"]].max(axis=1)
    return df


def load_scores_2024():
    scores = pd.read_parquet(PROCESSED_DIR / "macro_pca_scores.parquet")
    scores = scores[(scores.index >= "2024-01-01") & (scores.index <= "2024-12-31")]
    return scores[CLUSTERING_PCS]


def fit_labels(scores, n, cfg):
    gmm = GaussianMixture(
        n_components=n,
        covariance_type=cfg["regime"]["covariance_type"],
        max_iter=cfg["regime"]["max_iter"],
        n_init=cfg["regime"]["n_init"],
        random_state=cfg["project"]["random_seed"],
    )
    return pd.Series(gmm.fit_predict(scores.values), index=scores.index), gmm


def test_transition_alignment(labels, gdelt):
    """Test A: regime-transition days vs non-transition days, event density."""
    changed = labels != labels.shift(1)
    changed.iloc[0] = False
    # align to gdelt dates (business days present in both)
    common = labels.index.intersection(gdelt.index)
    ch = changed.reindex(common).fillna(False)
    ev = gdelt.loc[common, "event_z"]
    dens_trans = ev[ch].mean()
    dens_stable = ev[~ch].mean()
    n_trans = int(ch.sum())
    return dens_trans, dens_stable, n_trans


def test_stress_regime(labels, scores, gdelt):
    """Test B: does the high-PC2 regime sit on high GDELT stress density?"""
    means = {r: scores.loc[labels == r, "PC2"].mean() for r in labels.unique()}
    stress_regime = max(means, key=means.get)
    stress_days = labels == stress_regime
    common = labels.index.intersection(gdelt.index)
    sd = stress_days.reindex(common).fillna(False)
    stress_dens = gdelt.loc[common, "stress_count"]
    dens_in = stress_dens[sd].mean()
    dens_out = stress_dens[~sd].mean()
    return stress_regime, dens_in, dens_out, int(sd.sum())


def test_fomc_overlay(gdelt, tol_days=1):
    """Test C: do GDELT monetary spikes land near USER-VERIFIED FOMC dates?"""
    fomc = [pd.Timestamp(d) for d in FOMC_2024]
    # top-10 monetary days
    top = gdelt.nlargest(10, "monetary_count").index
    hits = 0
    for d in top:
        if any(abs((d - f).days) <= tol_days for f in fomc):
            hits += 1
    return hits, len(top)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gdelt", required=True, help="path to gdelt 2024 clean csv")
    args = ap.parse_args()

    cfg = load_config()
    gdelt = load_gdelt(args.gdelt)
    scores = load_scores_2024()

    print("=" * 72)
    print("REGIME <-> EVENT ALIGNMENT  (2024, independent GDELT validation)")
    print("=" * 72)
    print(f"GDELT days: {len(gdelt)} | PCA-score days in 2024: {len(scores)}")
    print(f"Overlap used: {len(scores.index.intersection(gdelt.index))} days")

    # FOMC overlay (independent of n)
    hits, total = test_fomc_overlay(gdelt)
    print(f"\nTest C - FOMC overlay: {hits}/{total} of top-10 GDELT monetary-spike "
          f"days land within +/-1d of a (user-verified) 2024 FOMC date.")
    print("  *** verify FOMC_2024 against federalreserve.gov before trusting this ***")

    print(f"\n{'n':>3} | {'A: trans vs stable event-z':<32} | {'B: stress-regime density ratio':<34}")
    print("-" * 72)
    results = {}
    for n in [3, 4, 5]:
        labels, gmm = fit_labels(scores, n, cfg)
        dt, ds, nt = test_transition_alignment(labels, gdelt)
        sr, din, dout, nsd = test_stress_regime(labels, scores, gdelt)
        ratio = din / dout if dout else float("nan")
        results[n] = {"trans_lift": dt - ds, "stress_ratio": ratio}
        print(f"{n:>3} | trans {dt:+.2f} vs stable {ds:+.2f} (n_tr={nt:>2}) "
              f"    | stress regime {sr}: {din:.0f} vs {dout:.0f}  ratio={ratio:.2f}")

    print("\n" + "=" * 72)
    print("READING:")
    print("  Test A: higher event-z on transition days than stable days (positive")
    print("          'trans - stable' lift) => regime changes track real events.")
    print("  Test B: stress-regime density ratio > 1 => the stress regime genuinely")
    print("          sits on high-stress-news days (falsifiable check).")
    print("  The n with the strongest lift AND ratio>1 is the event-supported choice.")
    print("=" * 72)


if __name__ == "__main__":
    main()
