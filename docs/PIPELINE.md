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

| File | Role | Run as |
|---|---|---|
| `app.py` | **Demonstration terminal** (repo root, not `src/`). Eight tabs; every live tab reads its numbers from `processed/*.json`, `forward_ledger.csv` and file counts under `data_provenance/` at run time, and says so when a results file is missing rather than showing a stale figure. **Shows no predictions** — steps 3–6 are registered but not unblinded. Tab 2 is a **labelled UI specimen** with invented numbers that doubles as the step 6 specification (`prereg_analog_event.md` §8). See `CURRENT_STATE` §16. | `streamlit run app.py` |

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

**Regime labels are canonically ordered by ascending mean PC1 from 2026-08-25**
(open thread 3). Rows logged before that date carry the old arbitrary GMM
component ordering, so the `regime` column is comparable **within each era and
not across the boundary**. Historical rows are not retro-relabelled. Picks are
unaffected — candidate selection uses label *equality*, which is invariant under
relabelling, verified bit-identical on 826 rebalances.

`config/models.frozen.sha256` holds a canonical checksum of the frozen `models:`
block (yaml → sorted JSON → sha256, so comments and key order may change but a
hyperparameter may not). `forward_log` and `model_grid` **verify it and refuse to
run on mismatch**, and refuse any entry carrying `half_life_years` under
`models:`. This replaced a comment reading "never edit this file" — an invariant
already broken on 08-23, when four backtest-only recency variants were added
under `models:` where the live harness would have logged them.

### 3a. The corpus read (API-bound, not daily)

`./run_corpus.sh` reads every unread document through `doc_read`. **Not part of
the reproduce chain and not a daily job** — run it when new documents are
fetched. Cached reads are skipped and never re-billed, so a re-run costs only
the remainder. The script uses `set -e`: `doc_read` exits 1 on a fatal error, and
without it the script would proceed to the next source against the same
exhausted balance.

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
| `src/analog_backtest.py` | Expanding-window walk-forward backtest (no look-ahead), non-overlapping weekly rebalances. Reports spread, Sharpe, hit-rate, win/loss asymmetry, permutation p — for **all assets** and for a **long-history-only** universe (the survivorship-bias check). **Applies recency decay** at `analog.recency_decay_lambda` (0.0008/session, HL ≈ 3.44y) and matches on **raw** PC values, not z-scored — so it is a different estimator from `analog_core`/`model_grid` and reports different numbers (0.25 vs 0.40 on the frozen baseline spec). The reported headline 0.51 / 0.25 come from **this** script. |
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

**Step 1 closure — what λ, σ and the scaling basis actually do (2026-08-24/25)**

*Every script below writes a `docs/*_results.md` and a `processed/*.json`. Read
the results files, not this table, for the numbers.*

| File | What it shows |
|---|---|
| `src/recency_sweep.py` | The pre-registered λ ladder {2,4,8,16,∞} on **both engines**. Runs the ∞ control first and asserts it reproduces `model_1_baseline` **element-wise on the spread series**, refusing to run a decayed rung otherwise. `--rederive` recomputes verdicts from the saved JSON without re-running. Engine A POSITIVE, Engine B NULL — **reframed exploratory**, see `rung_diagnostic`. |
| `src/rung_diagnostic.py` | What λ does to *selection*: weighted mean analog age, ESS, and top-k overlap against the no-decay control, per rung, per engine. **No forward return enters any quantity**, so nothing here can be tuned to an outcome. Registered threshold ≥0.90 overlap = tie-breaking. Measured 0.765 / 0.850 → **RESELECTION on both engines**. |
| `src/fine_lambda_sweep.py` | Exploratory, post-hoc, **no registered criterion** — maps the Sharpe surface across λ 0.0004–0.0014 to characterise the unexplained dip at the incumbent. Surface is **jagged**: 0.30 / 0.25 / 0.22 / 0.29 across steps of 1e-4. |
| `src/scaling_check.py` | Quantifies the **declared `_z()` full-panel look-ahead** (open thread 12) by running both scaling bases side by side on all three frozen models, paired sign-flip on the spread series, with candidate-pool counts so a smaller pool cannot be mistaken for a scaling effect. Small for level, **large for both trend models**. |
| `src/trend_check.py` | Isolates the trend effect at **fixed horizon** (thread 8's confound), on both scaling bases. Trend advantage +0.1137 full-panel, **−0.1213** with the look-ahead removed: on this panel **the trend advantage IS the look-ahead**. |
| `src/engine_b_paired.py` | Paired sign-flip on 836 shared rebalances: `analog_backtest` no-decay vs the incumbent λ. **p = 0.485 — not distinguishable**, retiring the claim that removing λ raised Sharpe 0.25→0.38. Uses `analog_backtest --dump-spreads`. |

**Problem 3 — the LLM document layer (steps 1–2 built; 3–6 registered, unbuilt)**

| File | What it shows |
|---|---|
| `src/fetch_sources.py` | Fetches every document source into the drop folder. **EDGAR**: for Item 2.02 the release text is in **EX-99**, not the primary document — the primary is a one-page cover page. Two passes: filename match, then a **content scan** of every other document in the accession keeping whatever contains reported figures, because issuers share no naming convention. Prints the accession's filenames when both fail. **Federal Register**: presidential documents by type. Filed/publication date is the **public** date, which is the correct event date. |
| `src/doc_read.py` | Reads any source into **ONE common schema** (direction per asset class, magnitude, horizon, specificity, novelty, confidence, evidence) via source-specific prompts. **The model never predicts returns** — it classifies content; what a direction *did* is answered by data in step 3. Aborts the whole run on a credit or auth error rather than retrying it; transient errors get one retry. Cached reads are keyed by prompt version and never re-billed. |
| `src/gate_check.py` | Does `specificity` **discriminate between sources**? Amended criterion: lower bound of a 95% bootstrap CI on the between-source spread must exceed 0.25, plus an ordering clause. Reports the **read condition per source**, so a cross-source comparison that is also a cross-prompt comparison cannot pass unnoticed. **PASS** at n=60×4: spread 0.363, CI [0.279, 0.453]. |
| `src/analog_event.py` | **Steps 3+4 as ONE estimator.** `ŷ = w·conditional + (1−w)·unconditional`, `w = ESS/(ESS+k)`; step 4 is the `w=0` limit. **k is estimated, not chosen** (DerSimonian–Laird τ² across regime cells, re-estimated inside every LOO fold); τ²=0 → w=0 is a **registered null**. Abstains below ESS 8. Runs on the **live basis** — expanding-window scaling and expanding canonically-ordered regime labels — because a deployed system has no future data. `--self-test` only: no real conditional estimate is computed until all six blind acceptance tests pass. |

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
| `data_provenance/docs/<source>/` | The **drop folder**: dated source text as `YYYYMMDD[_id].txt`, one directory per source type. Anything in that layout is readable — fetched by a script or saved by hand. Files are dated by **publication date**, not event date; dating FOMC minutes by meeting date would build look-ahead into a filename. `earnings_8k_coverpages/` retains the 307 SEC cover pages fetched before the EX-99 fix, as evidence. | gitignored, re-fetchable |
| `data_provenance/doc_reads/` | One JSON per document per prompt version, `<source>__<stem>__<version>.json`. **Committed** — these cost API spend and are not deterministically regenerable, so unlike the raw documents they cannot simply be re-pulled. Also the cache: a hit means zero tokens. | **yes** |
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

**(d) The document corpus has two properties that decide what it can support.**

*Dating.* Every file is dated by when the document became **public**, never by
when the event occurred. FOMC minutes are released about three weeks after the
meeting; dating them by meeting date would build look-ahead into a filename.

*Coverage.* Federal Register carries presidential documents only. Executive
orders and determinations (`political_order`) are decided policy;
proclamations, notices and memoranda (`political_other`) are largely ceremonial
or administrative — that split uses the **government's own type tag**, not a
judgement applied per document. Statements, posts and rhetoric outside the
Federal Register are **not covered**, and their absence in any result is a
**coverage gap, not evidence** that rhetoric does not move markets. Closing it is
a purchasing decision. `bank_research` and `transcript` have no free structured
feed and stand at zero documents.

*Foreign issuers* file 6-K with the whole submission as a single document and no
separate exhibits, so the EX-99 route that works for domestic 8-K yields little
for TSM and ASML. Cross-firm comparison must account for the asymmetry.

**(c) Data vendor gaps are expected.**
Yahoo occasionally returns a **partial bar** for a recent trading day. On
2026-08-17 it returned Open/High/Low/Volume normally with **only Close and
Adj Close NaN**, for all 47 assets, and had not healed after three `--force`
re-pulls in ~24 hours — so "Yahoo backfills within a day" is too optimistic.
Returns derive from Close, so the row correctly yields no return. The harness
falls back to the last bar with real prices and says so; skipped days are left as
honest gaps and are **not** retro-filled, because the forward test's credibility
depends on entries being timestamped before outcomes exist.
