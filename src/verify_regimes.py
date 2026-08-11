"""
src/verify_regimes.py

Scientific verification of the regime-count choice and the PCA-axis naming,
run BEFORE freezing the regime model. Produces an auditable record of:

  0. PC-axis naming validation — correlate each PC score against an external
     uncontroversial proxy (does PC1 actually track policy tightness?)
  1. Extended BIC/AIC sweep, n = 2..10 — find where BIC actually bottoms out
  2. Silhouette score per n — cluster separation, independent of likelihood
  3. Seed stability — refit best n across seeds, measure label agreement (ARI)
  4. Temporal held-out check — fit 2018-2024, score 2025-2026 log-likelihood
  5. Run-length sanity per n — reject configs that flicker

Run from project root:
    python -m src.verify_regimes
"""

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, adjusted_rand_score

from src.data_io import load_config, PROCESSED_DIR, OUTPUTS_DIR


CLUSTERING_PCS = ["PC1", "PC2", "PC3"]


def load_inputs():
    scores = pd.read_parquet(PROCESSED_DIR / "macro_pca_scores.parquet")
    macro = pd.read_parquet(PROCESSED_DIR / "macro_panel.parquet").loc[scores.index]
    return scores, macro


# -----------------------------------------------------------------------------
# Step 0 — PC-axis naming validation
# -----------------------------------------------------------------------------
def validate_pc_naming(scores, macro):
    """
    Correlate each PC score series against external proxies to test whether
    the human names ('rates level', 'risk stress', 'reflation') are earned.

    PC1 hypothesis: tracks policy tightness  -> proxy = DGS2 (2y yield) or EFFR
    PC2 hypothesis: tracks risk stress        -> proxy = VIXCLS
    PC3 hypothesis: tracks curve steepness    -> proxy = T10Y2Y
    """
    print("\n" + "=" * 70)
    print("STEP 0 — PC-axis naming validation (correlation vs external proxy)")
    print("=" * 70)

    checks = [
        ("PC1", "proposed name 'rates level / tightness'", ["DGS2", "EFFR", "DGS10"]),
        ("PC2", "proposed name 'risk stress'",             ["VIXCLS"]),
        ("PC3", "proposed name 'reflation / curve slope'", ["T10Y2Y", "M2SL"]),
    ]
    for pc, name, proxies in checks:
        print(f"\n{pc} — {name}")
        for proxy in proxies:
            if proxy in macro.columns:
                r = np.corrcoef(scores[pc].values, macro[proxy].values)[0, 1]
                verdict = "STRONG" if abs(r) > 0.8 else ("MODERATE" if abs(r) > 0.5 else "WEAK")
                print(f"    corr({pc}, {proxy}) = {r:+.3f}   [{verdict}]")
    print("\n  Reading: a name is 'earned' when |corr| with its proxy is high (>0.8).")


# -----------------------------------------------------------------------------
# Step 1 — Extended BIC/AIC sweep
# -----------------------------------------------------------------------------
def extended_sweep(X, cfg, n_min=2, n_max=10):
    print("\n" + "=" * 70)
    print(f"STEP 1 — Extended BIC/AIC sweep, n = {n_min}..{n_max}")
    print("=" * 70)
    rows = []
    for n in range(n_min, n_max + 1):
        gmm = GaussianMixture(
            n_components=n,
            covariance_type=cfg["regime"]["covariance_type"],
            max_iter=cfg["regime"]["max_iter"],
            n_init=cfg["regime"]["n_init"],
            random_state=cfg["project"]["random_seed"],
        )
        gmm.fit(X)
        bic, aic = gmm.bic(X), gmm.aic(X)
        rows.append({"n": n, "bic": bic, "aic": aic, "converged": gmm.converged_})
    df = pd.DataFrame(rows)
    # Deltas: how much each added regime improves BIC
    df["bic_delta"] = df["bic"].diff()
    print(df.to_string(index=False))
    best_bic_n = int(df.loc[df["bic"].idxmin(), "n"])
    print(f"\n  BIC minimum at n = {best_bic_n}")
    # Elbow heuristic: where does the per-step BIC improvement collapse?
    print("  Per-step BIC improvement (bic_delta): look for where it flattens toward 0.")
    return df, best_bic_n


# -----------------------------------------------------------------------------
# Step 2 — Silhouette per n
# -----------------------------------------------------------------------------
def silhouette_sweep(X, cfg, n_min=2, n_max=10):
    print("\n" + "=" * 70)
    print(f"STEP 2 — Silhouette score per n (cluster separation, -1..+1)")
    print("=" * 70)
    rows = []
    for n in range(n_min, n_max + 1):
        gmm = GaussianMixture(
            n_components=n,
            covariance_type=cfg["regime"]["covariance_type"],
            max_iter=cfg["regime"]["max_iter"],
            n_init=cfg["regime"]["n_init"],
            random_state=cfg["project"]["random_seed"],
        )
        labels = gmm.fit_predict(X)
        sil = silhouette_score(X, labels)
        rows.append({"n": n, "silhouette": sil})
    df = pd.DataFrame(rows)
    print(df.to_string(index=False))
    best_sil_n = int(df.loc[df["silhouette"].idxmax(), "n"])
    print(f"\n  Silhouette peaks at n = {best_sil_n} "
          f"(higher = better-separated, more distinct regimes)")
    return df, best_sil_n


# -----------------------------------------------------------------------------
# Step 3 — Seed stability
# -----------------------------------------------------------------------------
def seed_stability(X, cfg, n, seeds=(42, 7, 123, 2024, 999)):
    print("\n" + "=" * 70)
    print(f"STEP 3 — Seed stability at n={n} (Adjusted Rand Index across seeds)")
    print("=" * 70)
    label_sets = []
    for s in seeds:
        gmm = GaussianMixture(
            n_components=n,
            covariance_type=cfg["regime"]["covariance_type"],
            max_iter=cfg["regime"]["max_iter"],
            n_init=cfg["regime"]["n_init"],
            random_state=s,
        )
        label_sets.append(gmm.fit_predict(X))
    # Pairwise ARI against the first seed
    print(f"  Reference seed: {seeds[0]}")
    aris = []
    for i, s in enumerate(seeds[1:], 1):
        ari = adjusted_rand_score(label_sets[0], label_sets[i])
        aris.append(ari)
        print(f"    ARI(seed {seeds[0]}, seed {s}) = {ari:.3f}")
    print(f"\n  Mean ARI = {np.mean(aris):.3f}  "
          f"(1.0 = identical regimes; >0.9 = very stable; <0.7 = fragile)")
    return np.mean(aris)


# -----------------------------------------------------------------------------
# Step 4 — Temporal held-out check
# -----------------------------------------------------------------------------
def temporal_holdout(scores, cfg, n, split_date="2025-01-01"):
    print("\n" + "=" * 70)
    print(f"STEP 4 — Temporal held-out at n={n} (fit pre-{split_date}, score after)")
    print("=" * 70)
    X = scores[CLUSTERING_PCS]
    train = X[X.index < split_date].values
    test = X[X.index >= split_date].values
    if len(test) < 20:
        print(f"  Only {len(test)} test rows — split too late; skipping.")
        return None
    gmm = GaussianMixture(
        n_components=n,
        covariance_type=cfg["regime"]["covariance_type"],
        max_iter=cfg["regime"]["max_iter"],
        n_init=cfg["regime"]["n_init"],
        random_state=cfg["project"]["random_seed"],
    )
    gmm.fit(train)
    train_ll = gmm.score(train)   # mean log-likelihood per sample
    test_ll = gmm.score(test)
    print(f"  Train rows: {len(train)}   Test rows: {len(test)}")
    print(f"  Mean log-likelihood — train: {train_ll:+.3f}   test: {test_ll:+.3f}")
    gap = train_ll - test_ll
    print(f"  Generalization gap (train - test): {gap:+.3f}  "
          f"(small gap = generalizes well; large gap = overfit)")
    return gap


# -----------------------------------------------------------------------------
# Step 5 — Run-length sanity per n
# -----------------------------------------------------------------------------
def run_length_sanity(X, cfg, n_values=(3, 4, 5, 6, 7)):
    print("\n" + "=" * 70)
    print("STEP 5 — Run-length sanity (mean contiguous days per regime)")
    print("=" * 70)
    print("  Real macro regimes persist weeks-to-months. Flickering (mean run")
    print("  of a few days) signals noise partitions, not genuine states.\n")
    for n in n_values:
        gmm = GaussianMixture(
            n_components=n,
            covariance_type=cfg["regime"]["covariance_type"],
            max_iter=cfg["regime"]["max_iter"],
            n_init=cfg["regime"]["n_init"],
            random_state=cfg["project"]["random_seed"],
        )
        labels = gmm.fit_predict(X)
        # overall mean run length across all regimes
        runs = []
        current, prev = 1, labels[0]
        for lab in labels[1:]:
            if lab == prev:
                current += 1
            else:
                runs.append(current)
                current, prev = 1, lab
        runs.append(current)
        print(f"  n={n}:  overall mean run = {np.mean(runs):6.1f} days   "
              f"median = {np.median(runs):5.1f}   n_runs = {len(runs)}")


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    cfg = load_config()
    scores, macro = load_inputs()
    X = scores[CLUSTERING_PCS].values

    validate_pc_naming(scores, macro)
    sweep_df, best_bic_n = extended_sweep(X, cfg)
    sil_df, best_sil_n = silhouette_sweep(X, cfg)

    # Save the sweep tables for the audit trail
    diag = OUTPUTS_DIR / "diagnostics"
    diag.mkdir(parents=True, exist_ok=True)
    sweep_df.to_csv(diag / "regime_bic_sweep.csv", index=False)
    sil_df.to_csv(diag / "regime_silhouette_sweep.csv", index=False)

    # Stability + holdout at the candidate n's worth examining
    for n in sorted({3, 4, 5, best_bic_n, best_sil_n}):
        seed_stability(X, cfg, n)
        temporal_holdout(scores, cfg, n)

    run_length_sanity(X, cfg)

    print("\n" + "=" * 70)
    print("VERIFICATION COMPLETE — read the five steps together before choosing n.")
    print("=" * 70)


if __name__ == "__main__":
    main()