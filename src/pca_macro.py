"""
src/pca_macro.py

Fit PCA on the macro panel to discover the latent factors driving co-movement
across rates, spreads, volatility, money supply, and dollar.

The fitted PCA is saved and frozen; downstream code (regime classifier,
analog engine, live classification) projects new observations onto the same
components rather than refitting.

Run from project root:
    python -m src.pca_macro
"""

import numpy as np
import pandas as pd
import joblib
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from src.data_io import load_config, PROCESSED_DIR, OUTPUTS_DIR


# -----------------------------------------------------------------------------
# Load the macro panel and prepare it for PCA
# -----------------------------------------------------------------------------
def load_and_clean_macro(processed_path):
    """
    Load the macro panel and drop any rows that still have NaN after the
    forward-fill in build_panel.py. Pre-inception NaNs (e.g. SOFR before 2018,
    real yields before 2003) create rows that PCA cannot handle, because PCA
    requires a complete matrix. Dropping them means the effective PCA sample
    starts once all 10 variables have valid data.
    """
    macro = pd.read_parquet(processed_path)
    print(f"Raw macro panel shape: {macro.shape}")
    print(f"Raw date range: {macro.index.min().date()} → {macro.index.max().date()}")

    # Report per-column NaN counts
    print("\nNaN counts per variable (before dropping):")
    print(macro.isna().sum().to_string())

    # Drop rows where ANY variable is NaN — PCA needs a complete matrix
    macro_clean = macro.dropna()
    print(f"\nClean macro panel shape (rows with all 10 variables): {macro_clean.shape}")
    print(f"Effective PCA start date: {macro_clean.index.min().date()}")
    return macro_clean


# -----------------------------------------------------------------------------
# Standardize and fit PCA
# -----------------------------------------------------------------------------
def fit_pca(macro_clean, n_components, random_seed):
    """
    Standardize each variable (z-score) and fit PCA.

    Standardization is mandatory here because our variables live on wildly
    different scales: yields in percent (~4), M2 in trillions (~23000), VIX
    in index units (~15). Without standardization, M2 would dominate every
    component and yields would contribute almost nothing.
    """
    # Standardize: subtract mean, divide by standard deviation per column
    scaler = StandardScaler()
    macro_std = scaler.fit_transform(macro_clean.values)

    # Fit PCA on the standardized data
    pca = PCA(n_components=n_components, random_state=random_seed)
    pca.fit(macro_std)
    return pca, scaler, macro_std


# -----------------------------------------------------------------------------
# Reporting and interpretation
# -----------------------------------------------------------------------------
def report_variance(pca):
    """Print variance explained by each component and cumulative."""
    print("\n=== Variance explained ===")
    for i, (var, cum) in enumerate(zip(pca.explained_variance_ratio_,
                                       np.cumsum(pca.explained_variance_ratio_)), 1):
        print(f"  PC{i}: {var:.3f} ({var*100:.1f}%)   cumulative: {cum:.3f} ({cum*100:.1f}%)")


def report_loadings(pca, variable_names):
    """
    Print the loadings matrix — how each original variable contributes to
    each principal component. Absolute value indicates strength; sign indicates
    direction. Interpret each component by looking at which variables have
    large-magnitude loadings.
    """
    loadings = pd.DataFrame(
        pca.components_.T,  # transpose: rows = variables, columns = components
        index=variable_names,
        columns=[f"PC{i+1}" for i in range(pca.n_components_)]
    )
    print("\n=== Loadings (rows = variables, cols = components) ===")
    print(loadings.round(3).to_string())
    return loadings


# -----------------------------------------------------------------------------
# Save artifacts
# -----------------------------------------------------------------------------
def save_artifacts(pca, scaler, loadings, macro_clean_columns, macro_clean_index):
    """Save the fitted PCA, the scaler, the loadings, and the projected scores."""
    models_dir = OUTPUTS_DIR / "models"
    diag_dir = OUTPUTS_DIR / "diagnostics"
    models_dir.mkdir(parents=True, exist_ok=True)
    diag_dir.mkdir(parents=True, exist_ok=True)

    # Save the fitted PCA and scaler as one bundle — they must stay together
    joblib.dump({"pca": pca, "scaler": scaler, "columns": list(macro_clean_columns)},
                models_dir / "pca_macro.pkl")
    print(f"\nSaved fitted PCA + scaler → {models_dir / 'pca_macro.pkl'}")

    # Save loadings as CSV for readability
    loadings.to_csv(diag_dir / "pca_loadings.csv")
    print(f"Saved loadings → {diag_dir / 'pca_loadings.csv'}")

    # Save variance-explained summary
    var_df = pd.DataFrame({
        "component": [f"PC{i+1}" for i in range(pca.n_components_)],
        "variance_explained": pca.explained_variance_ratio_,
        "cumulative": np.cumsum(pca.explained_variance_ratio_),
    })
    var_df.to_csv(diag_dir / "pca_variance.csv", index=False)
    print(f"Saved variance summary → {diag_dir / 'pca_variance.csv'}")


# -----------------------------------------------------------------------------
# Project the macro panel onto components (for downstream regime classifier)
# -----------------------------------------------------------------------------
def project_and_save(pca, scaler, macro_clean):
    """
    Project the full clean macro panel onto the fitted components and save.
    This projected panel is what the regime classifier clusters on.
    """
    macro_std = scaler.transform(macro_clean.values)
    scores = pca.transform(macro_std)
    scores_df = pd.DataFrame(
        scores,
        index=macro_clean.index,
        columns=[f"PC{i+1}" for i in range(pca.n_components_)],
    )
    scores_path = PROCESSED_DIR / "macro_pca_scores.parquet"
    scores_df.to_parquet(scores_path)
    print(f"Saved projected scores → {scores_path}  shape: {scores_df.shape}")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    cfg = load_config()
    n_components = cfg["pca"]["n_components"]
    seed = cfg["project"]["random_seed"]

    macro_path = PROCESSED_DIR / "macro_panel.parquet"
    macro_clean = load_and_clean_macro(macro_path)

    pca, scaler, macro_std = fit_pca(macro_clean, n_components, seed)

    report_variance(pca)
    loadings = report_loadings(pca, macro_clean.columns)

    save_artifacts(pca, scaler, loadings, macro_clean.columns, macro_clean.index)
    project_and_save(pca, scaler, macro_clean)

    print("\nDone.")


if __name__ == "__main__":
    main()