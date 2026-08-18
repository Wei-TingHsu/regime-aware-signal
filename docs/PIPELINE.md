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
| `src/build_panel.py` | Cleans + aligns the raw pulls into `asset_returns.parquet` (47 assets) and `macro_panel.parquet` (FRED series), both indexed on the **NYSE session calendar** (see Section 8a). | `python -m src.build_panel` |
| `src/pca_macro.py` | Fits PCA on the standardized macro panel; writes `macro_pca_scores.parquet`, the fitted model, and loadings/variance diagnostics. | `python -m src.pca_macro` |
| `src/regime_classifier.py` | Fits the GMM at the **config-pinned** count (`regime.n_regimes`, currently 4), characterizes + interprets each regime (macro-based, PC-renumbering-proof), saves `regime_labels.parquet`. Still fits the candidate sweep so the BIC audit CSV survives as a diagnostic, and reports what BIC *would* have chosen and why that is not obeyed. | `python -m src.regime_classifier` |

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
- duplicate runs on the same US close are **skipped**, not double-logged;
- **window integrity**: a row is scored `matured` only if **every session** of its
  H-day window has a return for **every picked asset**. Otherwise it is marked
  `short_window` with its realised session count, excluded from the headline
  summary, and left visible in the full log. Previously `np.log1p(...).sum()`
  dropped missing days via `skipna=True` and reported an H-day trade scored on
  fewer days;
- horizons count **NYSE sessions** via `market_calendar.trading_days()`. (Since
  the panel index is itself the session calendar this is now a no-op, but it is
  kept as a guard against the index ever changing again);
- `entry_date` is **frozen** once written, never re-derived;
- `--dry-run` is inert on days with no new US close — the guard previously sat
  inside the "new picks" branch and was unreachable on skip days.

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
| `src/safe_haven_robustness.py` | Robustness sweep: correlation windows 5/10/20/60 x raw-vs-Fisher-z. Stress axis identified **data-drivenly** (was hard-coded PC2 until 2026-08-18; the two safe-haven scripts had been reporting opposite signs for the same statistic). |
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
| `src/market_calendar.py` | NYSE calendar utilities. `trading_days(start, end)` returns the session index used by `build_panel` (and, defensively, by `forward_log`); `to_market_day` / `is_market_open` bucket arbitrary timestamps to a session. Requires `pandas_market_calendars`. |
| `src/stress_axis.py` | Data-driven identification of the risk-stress principal component (the PC most correlated with VIX), so no script hard-codes a PC index. Used wherever a "stress regime" is selected. |
| `src/analog_core.py` | (see Section 4) the shared engine implementation. |

---

## 6. Data + output locations

| Path | Contents | In git? |
|---|---|---|
| `config/` | `config.yaml` (single source of truth: universe, FRED series, hyperparameters incl. the **pinned `regime.n_regimes`**, crisis episodes), `gdelt_theme_mapping.yaml`, and `models.yaml` (frozen pre-registered forward-test specs — **never edit**). | yes |
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

## 8. Three things a reviewer should know

**(a) The panel index is the NYSE session calendar, not `pd.bdate_range`.**
Changed 2026-08-18. `bdate_range` is Mon–Fri **including market holidays**, which
put **194 rows into the 2006+ panel that carry no asset returns at all** — yet
still entered the PCA and the GMM, because those are macro-only. The macro side
was forward-filled onto them, so the large majority were exact duplicates of the
preceding row: manufactured data, in a project whose standing rule is *extend data
by removing redundancy, never by imputation*.

The trade is **not free**: a minority of those rows (Good Fridays — Fed open, NYSE
closed — plus unscheduled closures such as Hurricane Sandy 2012) carry genuinely
new macro values, at most 46 per series. Dropping them is still correct, because a
macro state with no trading session is one no engine can act on and it contributes
zero return information.

Effect: the 2006+ panel went **5,382 → 5,188 rows**, and the count of rows with
zero asset coverage fell from ~196 to **2** — meaning "no prices" now reliably
signals a genuine vendor gap rather than a closed market. That distinction is what
makes the `short_window` flag in Section 3 meaningful.

*Side effect:* `analog_core._forward` compounds `rolling(H)` over index rows.
Because the index is now sessions, this is automatically session-counting; the
horizon bug it previously carried is resolved without a code change.

**(b) The regime count is pinned, not selected.**
`config.yaml` sets `regime.n_regimes: 4`, chosen on **persistence and economic
structure**, NOT on BIC. `candidate_n_regimes` is retained as **diagnostic sweep
input only** and selects nothing.

Why BIC is not trusted: `verify_regimes.py` sweeps n = 2..10 and BIC **keeps
decreasing to the edge of the range** (minimum at n=10). A criterion that always
prefers more components is not a usable selector here.

Read `docs/PROJECT_STATE.md` for the honest current strength of the n=4 case — on
the session panel the seed-stability argument **no longer discriminates** (every
candidate scores ARI 1.000) and the silhouette margin over n=2 is 0.001. n=4 now
rests on run-length persistence plus an economic argument, not on three
converging lines.

**(c) Data vendor gaps are expected.**
Yahoo occasionally returns a **partial bar** for a recent trading day. On
2026-08-17 it returned Open/High/Low/Volume normally with **only Close and
Adj Close NaN**, for all 47 assets, and had not healed after three `--force`
re-pulls in ~24 hours — so "Yahoo backfills within a day" is too optimistic.
Returns derive from Close, so the row correctly yields no return. The harness
falls back to the last bar with real prices and says so; skipped days are left as
honest gaps and are **not** retro-filled, because the forward test's credibility
depends on entries being timestamped before outcomes exist.
