"""
src/regime_classifier.py

Fit a Gaussian Mixture Model on the macro PCA scores to discover market
regimes. Candidate regime counts (3, 4, 5) are compared by BIC; the best
is frozen, applied to every historical date, and characterized by both
its PC-space centroid and its raw-macro-variable means.

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
    """Return the n_regimes with the lowest BIC."""
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
    Print a plain-language description of each regime based on its PC signature.

    Uses the PC1-PC2-PC3 interpretation we established:
      PC1 high = tight monetary policy; low = easy
      PC2 high = risk stress (VIX/M2/USD-up); low = calm
      PC3 high = reflation (steep curve, M2, low vol); low = compression
    """
    print("\n=== Regime interpretation ===")
    for regime_id, row in characterization.iterrows():
        pc1, pc2, pc3 = row["mean_PC1"], row["mean_PC2"], row["mean_PC3"]

        def label(val, high_word, low_word, threshold=0.5):
            if val > threshold:
                return high_word
            elif val < -threshold:
                return low_word
            else:
                return "neutral"

        rates = label(pc1, "TIGHT policy", "EASY policy")
        stress = label(pc2, "STRESSED", "CALM")
        reflation = label(pc3, "REFLATION", "COMPRESSION")

        print(f"  Regime {regime_id} ({int(row['n_days'])} days, "
              f"mean run={row['mean_run_length']:.0f}, max run={int(row['max_run_length'])}):")
        print(f"      PC1={pc1:+.2f} ({rates})   "
              f"PC2={pc2:+.2f} ({stress})   "
              f"PC3={pc3:+.2f} ({reflation})")
        print(f"      Mean 10Y={row['mean_DGS10']:.2f}%   "
              f"VIX={row['mean_VIXCLS']:.1f}   "
              f"USD idx={row['mean_DTWEXBGS']:.1f}")


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
    candidates = cfg["regime"]["candidate_n_regimes"]

    # Load PCA scores
    scores = load_scores()

    # Cluster only on the top PCs
    X = scores[CLUSTERING_PCS].values
    print(f"Clustering on {len(CLUSTERING_PCS)} components: {CLUSTERING_PCS}")

    # Fit candidate GMMs
    print(f"\nFitting candidate GMMs (n_regimes = {candidates})...")
    results = fit_candidate_gmms(X, candidates, cfg)

    # Select by BIC
    best_n = select_best_by_bic(results)
    best_gmm = results[best_n]["gmm"]
    print(f"\n=> BIC selects n_regimes = {best_n}")

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