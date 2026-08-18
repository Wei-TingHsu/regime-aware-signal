"""
src/regime_classifier.py

Fit a Gaussian Mixture Model on the macro PCA scores to discover market
regimes. The regime count is PINNED in config (`regime.n_regimes`), chosen on
stability / persistence / separation -- NOT on BIC, which decreases monotonically
to the edge of the n=2..10 sweep and therefore always prefers more components.
The candidate counts are still fitted so the BIC audit table remains available
as a diagnostic, but they do not select anything.

Run from project root:
    python -m src.regime_classifier
"""

import numpy as np
import pandas as pd
import joblib
from sklearn.mixture import GaussianMixture

from src.data_io import load_config, PROCESSED_DIR, OUTPUTS_DIR, RAW_DIR


# -----------------------------------------------------------------------------
# Which PCs to cluster on
# -----------------------------------------------------------------------------
CLUSTERING_PCS = ["PC1", "PC2", "PC3"]  # top 3 components — interpretable, stable


# -----------------------------------------------------------------------------
# Load PCA scores and prepare for clustering
# -----------------------------------------------------------------------------
def load_scores() -> pd.DataFrame:
    """Load the projected PCA scores from processed/."""
    path = PROCESSED_DIR / "macro_pca_scores.parquet"
    scores = pd.read_parquet(path)
    print(f"Loaded PCA scores: {scores.shape[0]} dates × {scores.shape[1]} components")
    print(f"Date range: {scores.index.min().date()} → {scores.index.max().date()}")
    return scores


# -----------------------------------------------------------------------------
# Fit candidate GMMs and select by BIC
# -----------------------------------------------------------------------------
def fit_candidate_gmms(X: np.ndarray, candidate_n: list, cfg: dict) -> dict:
    """
    Fit GMMs for each candidate regime count, return dict keyed by n_regimes.

    Each fit uses the config's covariance type, max_iter, n_init, and the
    project's random_seed for reproducibility.
    """
    results = {}
    for n in candidate_n:
        gmm = GaussianMixture(
            n_components=n,
            covariance_type=cfg["regime"]["covariance_type"],
            max_iter=cfg["regime"]["max_iter"],
            n_init=cfg["regime"]["n_init"],
            random_state=cfg["project"]["random_seed"],
        )
        gmm.fit(X)
        bic = gmm.bic(X)
        aic = gmm.aic(X)
        results[n] = {"gmm": gmm, "bic": bic, "aic": aic}
        print(f"  n_regimes={n}:  BIC={bic:>10.1f}   AIC={aic:>10.1f}   "
              f"converged={gmm.converged_}")
    return results


def select_best_by_bic(results: dict) -> int:
    """Lowest-BIC n. Reported for the audit trail ONLY -- never used to select.

    See the module docstring: BIC keeps falling to the edge of the sweep, so it
    is not a usable selector here.
    """
    return min(results, key=lambda n: results[n]["bic"])


# -----------------------------------------------------------------------------
# Characterize each regime
# -----------------------------------------------------------------------------
def characterize_regimes(
    labels: pd.Series,
    scores: pd.DataFrame,
    macro_panel: pd.DataFrame,
    gmm: GaussianMixture,
) -> pd.DataFrame:
    """
    Build a per-regime summary table: PC means, raw-macro means, and durations.
    """
    rows = []
    for regime_id in sorted(labels.unique()):
        mask = labels == regime_id
        regime_dates = labels[mask].index

        # PC-space centroid (from the GMM, not the sample mean — cleaner)
        pc_centroid = gmm.means_[regime_id]

        # Raw-macro mean values on the dates in this regime
        macro_in_regime = macro_panel.loc[regime_dates]
        macro_means = macro_in_regime.mean()

        # Duration statistics: contiguous runs
        run_lengths = _compute_run_lengths(labels, regime_id)

        row = {"regime_id": regime_id, "n_days": int(mask.sum())}
        for i, pc in enumerate(CLUSTERING_PCS):
            row[f"mean_{pc}"] = pc_centroid[i]
        for col in macro_panel.columns:
            row[f"mean_{col}"] = macro_means[col]
        row["mean_run_length"] = float(np.mean(run_lengths)) if run_lengths else 0.0
        row["max_run_length"] = int(max(run_lengths)) if run_lengths else 0
        row["n_runs"] = len(run_lengths)
        rows.append(row)

    return pd.DataFrame(rows).set_index("regime_id")


def _compute_run_lengths(labels: pd.Series, regime_id: int) -> list:
    """Length of each contiguous run of `regime_id` in the label series."""
    in_regime = (labels == regime_id).values
    runs = []
    current = 0
    for is_in in in_regime:
        if is_in:
            current += 1
        else:
            if current > 0:
                runs.append(current)
                current = 0
    if current > 0:
        runs.append(current)
    return runs


# -----------------------------------------------------------------------------
# Interpret regimes for the console
# -----------------------------------------------------------------------------
def interpret_regimes(characterization: pd.DataFrame) -> None:
    """
    Plain-language description of each regime from its RAW MACRO means, not from
    fixed PC positions -- so it stays correct after a PCA refit renumbers the
    components. Each proxy is z-scored ACROSS regimes to decide high/low/neutral.
    """
    print("\n=== Regime interpretation (macro-based, PC-renumbering-proof) ===")
    proxies = {
        "mean_VIXCLS":   ("STRESSED (high VIX)",    "CALM (low VIX)"),
        "mean_DGS2":     ("TIGHT policy (high 2Y)", "EASY policy (low 2Y)"),
        "mean_DGS10":    ("HIGH 10Y yield",         "LOW 10Y yield"),
        "mean_T10Y2Y":   ("STEEP curve",            "FLAT / inverted curve"),
        "mean_DTWEXBGS": ("STRONG USD",             "WEAK USD"),
    }
    present = {k: v for k, v in proxies.items() if k in characterization.columns}
    zc = {}
    for k in present:
        col = characterization[k].astype(float)
        sd = col.std()
        zc[k] = (col - col.mean()) / sd if sd else col * 0.0

    def w(z, hi, lo, thr=0.6):
        return hi if z > thr else (lo if z < -thr else None)

    for regime_id, row in characterization.iterrows():
        tags = [w(zc[k].loc[regime_id], hi, lo) for k, (hi, lo) in present.items()]
        tags = [t for t in tags if t] or ["neutral / mixed"]
        print(f"  Regime {regime_id} ({int(row['n_days'])} days, "
              f"mean run={row['mean_run_length']:.0f}, "
              f"max run={int(row['max_run_length'])}): " + "; ".join(tags))
        bits = []
        if "mean_VIXCLS" in row:   bits.append(f"VIX={row['mean_VIXCLS']:.1f}")
        if "mean_DGS10" in row:    bits.append(f"10Y={row['mean_DGS10']:.2f}%")
        if "mean_DTWEXBGS" in row: bits.append(f"USD={row['mean_DTWEXBGS']:.1f}")
        if bits:
            print("      " + "   ".join(bits))


# -----------------------------------------------------------------------------
# Save artifacts
# -----------------------------------------------------------------------------
def save_artifacts(
    best_gmm: GaussianMixture,
    best_n: int,
    labels: pd.Series,
    characterization: pd.DataFrame,
    bic_summary: pd.DataFrame,
    columns_used: list,
) -> None:
    """Save the fitted model, labels, characterization, and BIC audit."""
    models_dir = OUTPUTS_DIR / "models"
    diag_dir = OUTPUTS_DIR / "diagnostics"
    models_dir.mkdir(parents=True, exist_ok=True)
    diag_dir.mkdir(parents=True, exist_ok=True)

    # Bundle the model with the columns it was fit on and the selected n
    bundle = {
        "gmm": best_gmm,
        "n_regimes": best_n,
        "clustering_pcs": columns_used,
    }
    joblib.dump(bundle, models_dir / "regime_gmm.pkl")
    print(f"\nSaved fitted GMM → {models_dir / 'regime_gmm.pkl'}")

    # Labels — one per date
    labels_path = PROCESSED_DIR / "regime_labels.parquet"
    labels.to_frame(name="regime_id").to_parquet(labels_path)
    print(f"Saved regime labels → {labels_path}")

    # Characterization
    char_path = diag_dir / "regime_characterization.csv"
    characterization.to_csv(char_path)
    print(f"Saved regime characterization → {char_path}")

    # BIC audit
    bic_path = diag_dir / "regime_bic.csv"
    bic_summary.to_csv(bic_path, index=False)
    print(f"Saved BIC audit → {bic_path}")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> None:
    cfg = load_config()
    n_regimes = int(cfg["regime"]["n_regimes"])          # PINNED -- the decision
    candidates = cfg["regime"]["candidate_n_regimes"]    # diagnostic sweep only
    # always fit the pinned count, even if it is absent from the sweep list
    fit_ns = sorted(set(candidates) | {n_regimes})

    # Load PCA scores
    scores = load_scores()

    # Cluster only on the top PCs
    X = scores[CLUSTERING_PCS].values
    print(f"Clustering on {len(CLUSTERING_PCS)} components: {CLUSTERING_PCS}")

    # Fit candidate GMMs
    print(f"\nFitting GMMs (n_regimes = {fit_ns})...")
    results = fit_candidate_gmms(X, fit_ns, cfg)

    # Use the PINNED count. BIC is reported, never obeyed.
    best_n = n_regimes
    best_gmm = results[best_n]["gmm"]
    bic_pick = select_best_by_bic(results)
    print(f"\n=> PINNED n_regimes = {best_n}  (config: regime.n_regimes)")
    if bic_pick != best_n:
        print(f"   note: lowest BIC in this sweep is n={bic_pick}, NOT used. BIC keeps "
              f"decreasing to the edge of the n=2..10 range (see verify_regimes.py), "
              f"so it always prefers more components. n={best_n} stands on seed "
              f"stability, run-length persistence, and cluster separation.")

    # Build BIC summary table
    bic_summary = pd.DataFrame([
        {"n_regimes": n, "bic": r["bic"], "aic": r["aic"], "converged": r["gmm"].converged_}
        for n, r in results.items()
    ])

    # Assign labels to every date
    labels_array = best_gmm.predict(X)
    labels = pd.Series(labels_array, index=scores.index, name="regime_id")

    # Load raw macro panel (for characterization)
    macro_panel = pd.read_parquet(PROCESSED_DIR / "macro_panel.parquet")
    macro_panel = macro_panel.loc[scores.index]  # align to PCA sample

    # Characterize each regime
    characterization = characterize_regimes(labels, scores, macro_panel, best_gmm)

    # Print interpretation
    interpret_regimes(characterization)

    # Save everything
    save_artifacts(best_gmm, best_n, labels, characterization, bic_summary, CLUSTERING_PCS)

    # Show current regime
    latest_date = labels.index.max()
    latest_regime = labels.loc[latest_date]
    print(f"\nCurrent regime (as of {latest_date.date()}): Regime {latest_regime}")

    print("\nDone.")


if __name__ == "__main__":
    main()