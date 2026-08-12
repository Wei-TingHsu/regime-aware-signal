# Pipeline map — what runs, in what order, and what each file is for

*A navigation guide for anyone reading this repo (Dr. Lee or other reviewers).
It separates the **canonical pipeline** you run to reproduce everything from
the **one-off analysis scripts** that produced specific results, and from the
**shared helpers** that are imported rather than run. Research findings live in
`docs/regime_event_validation.md` and the methodology log, not here — this file
is purely a map of the code.*

---

## 1. Reproduce-from-scratch order

Everything downstream regenerates deterministically (seed in `config.yaml`).
Run these four, in order, from the repo root:

```bash
python -m src.download_data     # 1. pull asset prices (yfinance) + FRED series into the raw cache
python -m src.build_panel       # 2. assemble processed/asset_returns.parquet + macro_panel.parquet
python -m src.pca_macro         # 3. fit PCA on the macro panel -> macro_pca_scores.parquet + model
python -m src.regime_classifier # 4. fit GMM regimes -> processed/regime_labels.parquet + characterization
```

After that, any analysis script in Section 3 can be run independently.

---

## 2. Core pipeline modules (the canonical path)

| File | Role | Run as |
|---|---|---|
| `src/download_data.py` | Pulls every asset price and FRED macro series named in `config.yaml` into the raw cache (cache-first, so re-runs are cheap). | `python -m src.download_data` |
| `src/build_panel.py` | Cleans + aligns the raw pulls into `asset_returns.parquet` (47 assets) and `macro_panel.parquet` (FRED series). | `python -m src.build_panel` |
| `src/pca_macro.py` | Fits PCA on the standardized macro panel; writes `macro_pca_scores.parquet`, the fitted model, and loadings/variance diagnostics. | `python -m src.pca_macro` |
| `src/regime_classifier.py` | Fits the GMM regime model on the PCA scores, characterizes + interprets each regime (macro-based, PC-renumbering-proof), saves `regime_labels.parquet`. | `python -m src.regime_classifier` |

---

## 3. Analysis scripts (evidence for the report — run individually, not part of the reproduce chain)

**Regime-count verification**
| File | What it shows |
|---|---|
| `src/verify_regimes.py` | Five-step audit for choosing the regime count *n*: data-driven PC-axis identification, BIC/AIC sweep, silhouette, seed-stability (ARI), temporal held-out generalization gap, run-length sanity. |
| `src/short_run_events.py` | Tests whether short (<=2-day) regime runs are genuine fast-shock events (landing near FOMC dates / known 2018-2026 shocks) or boundary noise. `python -m src.short_run_events [--n 4]` |

**Problem 1 — safe-haven inversion**
| File | What it shows |
|---|---|
| `src/liquidity_classifier.py` | Builds + validates the liquidity-stress states (2-component GMM on cross-asset correlation breadth + realized vol); saves `liquidity_states.parquet`. |
| `src/safe_haven_test.py` | GLD-SPY rolling-correlation compared across liquidity states (+ n=4 macro-regime cross-check), permutation-tested. |
| `src/safe_haven_robustness.py` | Robustness sweep: correlation windows 5/10/20/60 x raw-vs-Fisher-z. |
| `src/sofr_vs_effr_diagnostic.py` | One-off decision aid that justified dropping SOFR from the macro panel (redundant with EFFR: R^2 ~ 0.998). |

**Regime <-> event alignment (GDELT 2024 validation)**
| File | What it shows |
|---|---|
| `src/regime_event_alignment.py` | Main alignment tests (transition alignment, stress-regime density, FOMC overlay) against 2024 GDELT. |
| `src/regime_event_alignment_normalized.py` | De-baselined stress measure (share of news + rolling z-score). |
| `src/regime_event_permutation.py` | Circular-rotation permutation test for the alignment. |
| `src/regime_event_window_sweep.py` | Window-robustness sweep of the alignment across n and window lengths. |

**Problem 2 — rotation chain**
| File | What it shows |
|---|---|
| `src/chain_rotation.py` | Stage 1: residualized lead-lag order discovery + thesis comparison + permutation + sub-period stability. **Result: null / anti-stable** — which motivated the event-conditioned reframe (see the product-vision notes). Kept as the record of that finding. |

---

## 4. Shared helpers (imported by the above, not run directly)

| File | Role |
|---|---|
| `src/data_io.py` | Cache-first fetcher with exponential-backoff retry; `load_config()`; `PROCESSED_DIR` / `OUTPUTS_DIR` path constants. |
| `src/market_calendar.py` | Early-close-aware NYSE trading-day calendar utility. |
| `src/stress_axis.py` | Data-driven identification of the risk-stress principal component (the PC most correlated with VIX), so no script hard-codes a PC index. Used wherever a "stress regime" is selected. |

---

## 5. Status / to verify

- Two `UNNEST ... .xlsx` files currently sit in `src/`. These are raw GDELT data, not code — they belong in `raw/` (gitignored), not `src/`.

---

## 6. Data + output locations

| Path | Contents | In git? |
|---|---|---|
| `config/` | `config.yaml` (single source of truth: universe, FRED series, hyperparameters, crisis episodes) and `gdelt_theme_mapping.yaml`. | yes |
| `raw/` | Untouched API pulls. | gitignored, regenerable |
| `processed/` | Cleaned panels + scores + labels: `asset_returns.parquet`, `macro_panel.parquet`, `macro_pca_scores.parquet`, `regime_labels.parquet`, `liquidity_states.parquet`, `gdelt_2024_clean.csv`. | gitignored, regenerable |
| `outputs/` | Fitted models, diagnostics (CSVs), figures. | gitignored |
| `docs/` | Methodology log, validation explainer, learning journal, this map. | yes |
| `hypotheses/` | Pre-registered hypotheses. | yes |

---

## 7. One caveat a reviewer should know

The saved `regime_labels.parquet` is fit at the count the classifier auto-selects
by **BIC**, which prefers more components (it keeps decreasing toward n=10). The
**documented regime count is n=4**, chosen on stability / persistence / separation
grounds (see `verify_regimes.py` output and the methodology log), *not* on BIC. A
follow-up will pin the pipeline to n=4 so the saved labels match the documented
choice. Until then, treat n=4 as canonical regardless of what the raw BIC selection
saves.
