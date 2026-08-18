# Pipeline map — what runs, in what order, and what each file is for

*A navigation guide for anyone reading this repo (Dr. Lee or other reviewers).
It separates the **canonical pipeline** you run to reproduce everything, the
**live daily process**, the **one-off analysis scripts** that produced specific
results, and the **shared helpers** that are imported rather than run. Research
findings live in `docs/regime_event_validation.md`, `docs/PROJECT_STATE.md` and
the methodology log — this file is purely a map of the code.*

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

`download_data` is **cache-first**: re-runs are cheap but serve cached data.
Pass **`--force`** to actually re-pull from the network (required for anything
live — see Section 3).

After that, any analysis script in Section 4 can be run independently.

---

## 2. Core pipeline modules (the canonical path)

| File | Role | Run as |
|---|---|---|
| `src/download_data.py` | Pulls every asset price and FRED macro series named in `config.yaml` into the raw cache. Cache-first; **`--force`** re-pulls full history. | `python -m src.download_data [--force]` |
| `src/build_panel.py` | Cleans + aligns the raw pulls into `asset_returns.parquet` (47 assets) and `macro_panel.parquet` (FRED series). | `python -m src.build_panel` |
| `src/pca_macro.py` | Fits PCA on the standardized macro panel; writes `macro_pca_scores.parquet`, the fitted model, and loadings/variance diagnostics. | `python -m src.pca_macro` |
| `src/regime_classifier.py` | Fits the GMM regime model on the PCA scores, characterizes + interprets each regime (macro-based, PC-renumbering-proof), saves `regime_labels.parquet`. See the caveat in Section 8. | `python -m src.regime_classifier` |

---

## 3. Live daily process (the forward test)

| File | Role | Run as |
|---|---|---|
| `src/forward_log.py` | **One self-contained daily command.** Force-refreshes data, computes all three pre-registered models' picks, appends to the ledger, back-fills matured trades, rewrites the scoreboard. Fails loud (`MANUAL INTERVENTION NEEDED`) rather than logging bad data. | `python -m src.forward_log` |

Run once daily, any time after ~05:00 SGT (so the prior US close has landed).

Safeguards built in, each the result of a bug found on 2026-08-18:
- refresh passes **`--force`** — the cache-first fetcher otherwise serves **stale
  data while reporting success**;
- signal date = **last bar with real price coverage** (≥40% of assets), *not* the
  last index row — the macro panel is forward-filled, so PCA scores exist on days
  with zero prices and the engine would otherwise compute picks from empty bars;
- **staleness guard** halts if the freshest usable data is >5 days old;
- duplicate runs on the same US close are **skipped**, not double-logged.

Outputs: `processed/forward_ledger.csv` (machine state, gitignored) and
`docs/forward_scoreboard.md` (readable table, committed).

Model specs are frozen in **`config/models.yaml`** — pre-registered before any
live data existed. Do not edit; add new models instead.

---

## 4. Analysis scripts (evidence for the report — run individually, not part of the reproduce chain)

**Regime-count verification**
| File | What it shows |
|---|---|
| `src/verify_regimes.py` | Five-step audit for choosing the regime count *n*: data-driven PC-axis identification, BIC/AIC sweep (n=2..10), silhouette, seed-stability (ARI), temporal held-out generalization gap, run-length sanity. |
| `src/short_run_events.py` | Tests whether short (<=2-day) regime runs are genuine fast-shock events (landing near FOMC dates / known 2018-2026 shocks) or boundary noise. `python -m src.short_run_events [--n 4]` |

**Problem 1 — safe-haven inversion (result: clean null)**
| File | What it shows |
|---|---|
| `src/liquidity_classifier.py` | Builds + validates the liquidity-stress states (2-component GMM on cross-asset correlation breadth + realized vol); saves `liquidity_states.parquet`. |
| `src/safe_haven_test.py` | GLD-SPY rolling-correlation compared across liquidity states (+ n=4 macro-regime cross-check), permutation-tested. |
| `src/safe_haven_robustness.py` | Robustness sweep: correlation windows 5/10/20/60 x raw-vs-Fisher-z. |
| `src/sofr_vs_effr_diagnostic.py` | One-off decision aid that justified dropping SOFR from the macro panel (redundant with EFFR: R^2 ~ 0.998), which extended panel history back to 2006. |

**Problem 1 engine — macro analog (result: real but modest edge)**
| File | What it shows |
|---|---|
| `src/analog_core.py` | **Shared parameterized engine.** One implementation driven by a spec dict (horizon, level-vs-trend similarity, kernel, sigma, regime count, basket size), so every model and the live harness run identical code. Helper only — not run directly. |
| `src/analog_engine.py` | Prints the engine's **current call** as of the latest data: ranked long/short candidates with expected move, confidence, and macro-factor attribution. |
| `src/analog_backtest.py` | Expanding-window walk-forward backtest (no look-ahead), non-overlapping weekly rebalances. Reports spread, Sharpe, hit-rate, win/loss asymmetry, permutation p — for **all assets** and for a **long-history-only** universe (the survivorship-bias check). |
| `src/model_grid.py` | Runs the 48-config in-sample grid that **defines `model_3_overfit`** (best-in-sample, explicitly cherry-picked as a control group), and scores the three pre-registered models on identical footing. Writes `docs/model_grid_results.md` — the pre-registration record of every configuration tried. |

**Regime <-> event alignment (GDELT 2024 validation)**
| File | What it shows |
|---|---|
| `src/regime_event_alignment.py` | Main alignment tests (transition alignment, stress-regime density, FOMC overlay) against 2024 GDELT. |
| `src/regime_event_alignment_normalized.py` | De-baselined stress measure (share of news + rolling z-score). |
| `src/regime_event_permutation.py` | Circular-rotation permutation test for the alignment. |
| `src/regime_event_window_sweep.py` | Window-robustness sweep of the alignment across n and window lengths. |

**Problem 2 — rotation chain (result: null / anti-stable)**
| File | What it shows |
|---|---|
| `src/chain_rotation.py` | Stage 1: residualized lead-lag order discovery + thesis comparison + permutation + sub-period stability. **Result: null / anti-stable** — which motivated the event-conditioned reframe (see `docs/PROJECT_STATE.md`). Kept as the record of that finding. |

---

## 5. Shared helpers (imported by the above, not run directly)

| File | Role |
|---|---|
| `src/data_io.py` | Cache-first fetcher with exponential-backoff retry; `load_config()`; `PROCESSED_DIR` / `OUTPUTS_DIR` path constants. |
| `src/market_calendar.py` | Early-close-aware NYSE trading-day calendar utility. |
| `src/stress_axis.py` | Data-driven identification of the risk-stress principal component (the PC most correlated with VIX), so no script hard-codes a PC index. Used wherever a "stress regime" is selected. |
| `src/analog_core.py` | (see Section 4) the shared engine implementation. |

---

## 6. Data + output locations

| Path | Contents | In git? |
|---|---|---|
| `config/` | `config.yaml` (single source of truth: universe, FRED series, hyperparameters, crisis episodes), `gdelt_theme_mapping.yaml`, and `models.yaml` (frozen pre-registered forward-test specs). | yes |
| `raw/` | Untouched API pulls, plus the raw GDELT `.xlsx` exports. | gitignored, regenerable |
| `processed/` | Cleaned panels + scores + labels: `asset_returns.parquet`, `macro_panel.parquet`, `macro_pca_scores.parquet`, `regime_labels.parquet`, `liquidity_states.parquet`, `gdelt_2024_clean.csv`, `forward_ledger.csv`. | gitignored, regenerable |
| `outputs/` | Fitted models, diagnostics (CSVs), figures. | gitignored |
| `docs/` | `PROJECT_STATE.md` (the briefing), `architecture_decisions.md`, `regime_event_validation.md`, `model_grid_results.md`, `forward_scoreboard.md`, the methodology log, the learning journal, and this map. | yes |
| `hypotheses/` | Pre-registered hypotheses. | yes |

---

## 7. Cross-session continuity

The **repo is the source of truth**, not model memory. To brief a fresh session,
bundle every doc into one file and share it:

```bash
for f in docs/*.md; do echo "===== $f ====="; cat "$f"; echo; done > ~/Downloads/briefing.md
```

Regenerate it each time — it is a snapshot, not a live link.

---

## 8. Two caveats a reviewer should know

**(a) The saved regime count does not match the documented one.**
`regime_classifier.py` auto-selects by **lowest BIC** among the candidates in
`config.yaml` (`candidate_n_regimes: [3, 4, 5]`), which currently resolves to
**n=5**. The **documented regime count is n=4**, chosen on stability /
persistence / separation grounds (see `verify_regimes.py` output and the
methodology log), *not* on BIC.

Why BIC is not trusted here: `verify_regimes.py` sweeps n = 2..10 and BIC **keeps
decreasing all the way to the edge of that range** (minimum at n=10). A criterion
that always prefers more components is not a usable selector for this data.

A follow-up will pin the pipeline to n=4. **Until then, treat n=4 as canonical
regardless of what the raw BIC selection saves.** Note that the analog engine and
the forward-test harness already **refit n=4 on the fly**, so the live models are
unaffected by this discrepancy.

**(b) Data vendor gaps are expected.**
Yahoo occasionally returns a **partial bar** (volume present, OHLC all NaN) for a
recent trading day. The forward-test harness handles this by falling back to the
last bar with real prices and saying so; skipped days are left as honest gaps and
are **not** retro-filled, because the forward test's credibility depends on
entries being timestamped before outcomes exist.
