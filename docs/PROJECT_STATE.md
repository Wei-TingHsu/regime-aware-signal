# PROJECT STATE — briefing document

*Upload this file at the start of a new conversation to resume without re-explaining.
Last updated: 2026-08-17. Keep it updated after each workstream closes.*

---

## What this project is

**Regime-Aware Cross-Asset Signal Framework.** Three research problems + a product
vision: engines that (a) read the macro state and issue directional calls, (b) detect
event-triggered rotation cascades, (c) narrate scenarios via an LLM layer. The
47-asset universe is an **MVP baseline and must stay expandable** — never hard-code 47.

**Product vision (settled).** Rotation is **event-initiated**, but the event names the
**focus SET, not the ORDER**. So: GDELT/text detects the trigger and the set; price
statistics determine the sequence and timing **within** event episodes. Core value is
bridging information-quiet gaps — once a cascade fires, position along it between
headlines.

---

## Current status by workstream

### Regime engine — DONE (with an honest caveat)
- PCA on **8 FRED series, 2006+** (SOFR dropped: redundant with EFFR, R²=0.998; HY
  spread dropped earlier, intentionally). DTWEXBGS is now the binding series.
- **n=4 regimes**, chosen on **stability / persistence / separation**, NOT on BIC
  (BIC decreases monotonically toward n=10 and is not a reliable selector here).
- Re-validated after the panel extension (Option B, full re-run):
  - Still favours n=4: seed ARI **1.000** (n=5 fragile at 0.774), run-length median
    **52.5d** (n=3 flickers at 3d), best silhouette.
  - **Weakened:** generalization gap now favours fewer regimes; the 2024 GDELT
    event-alignment **no longer corroborates** n=4 (p=0.32, 0/7 windows; was p<0.001
    on the old panel). Documented honestly in `docs/regime_event_validation.md`.
- **PCA renumbering hazard:** refits renumber components (stress axis moved PC2→PC3).
  `src/stress_axis.py` identifies the stress axis **data-drivenly** (PC most correlated
  with VIX). Never hard-code a PC index.

### Problem 1 (safe-haven inversion) — DONE, clean NULL
No inversion under either state definition, robust across windows 5/10/20/60 and
raw-vs-Fisher-z:
- Liquidity sub-classifier: gap **+0.017**, p=0.44
- VIX-stress macro regime: gap **+0.16** (opposite direction), p≈0.09

Gold does **not** decouple from equities in stress — it co-moves at least as much
(dash-for-cash). A defensible negative finding contradicting popular intuition.

### Problem 1 ENGINE (macro analog) — BUILT + VALIDATED
Expanding-window walk-forward, 2010–2026, 706 non-overlapping weekly rebalances,
no look-ahead:

| universe | spread/wk | Sharpe | hit | payoff | p |
|---|---|---|---|---|---|
| all 47 | +0.345% (~18%/yr) | 0.60 | 51.3% | 1.00 | 0.0010 |
| long-history (35, ≥8y) | +0.226% (~11.8%/yr) | 0.43 | 51.3% | 0.97 | 0.0010 |

Survives dropping recent-inception tickers → **not just an AI-boom artifact**.
Character: **long-tilt** (short leg +0.071%, still positive — no real short edge) and
**symmetric payoff** — the edge is a small *frequency* advantage, not fat tails.
A ~0.4 Sharpe standalone signal is one **ingredient**; the route to a presentable
number is the **ensemble**, not torturing this engine.

### Problem 2 (rotation chain) — Stage 1 NULL, reframed
Chain NVDA/TSM/ASML/MU/INTC, leave-one-out residualization to strip shared semi beta.
- Discovered order ASML→TSM→MU→INTC→NVDA; vs thesis (NVDA→TSM→ASML→MU→INTC)
  Spearman **−0.100**, permutation **p=0.597**
- Sub-period stability **−0.250** → **anti-stable**, no persistent order
- **Reason:** the test was unconditional across all history. Rotation is
  event-initiated, so lead-lag must be measured **within event-triggered episodes**.
  Stage 2 waits on the event layer.

### Forward test — LIVE since 2026-08-17
Three models **pre-registered and frozen** in `config/models.yaml` before any live data.
In-sample (frozen regimes, `docs/model_grid_results.md` records all 48 configs tried):

| model | spec | Sharpe | ~/yr | hit | payoff | p |
|---|---|---|---|---|---|---|
| model_1_baseline | 5d, level, gauss σ1.5 | +0.21 | +5.4% | 51.1% | 0.93 | 0.0869 |
| model_2_horizon_trend | 10d, trend, gauss σ1.5 | +0.39 | +10.4% | 51.4% | 0.89 | 0.0190 |
| model_3_overfit | 20d, trend, gauss σ1.0 | +0.50 | +11.3% | 50.5% | 1.06 | 0.0390 |

- **model_2** is the *principled* amendment (trend-aware similarity = match macro
  *direction* not just level, per the gold-vs-rising-rates insight). It nearly doubled
  the baseline Sharpe and became significant — hypothesis confirmed.
- **model_3** is a deliberate **control group**: best-in-sample of 48 configs,
  explicitly cherry-picked. Hypothesis: its lead shrinks or inverts live.

---

## Architecture decisions (full detail in `docs/architecture_decisions.md`)

1. **One shared daily clock** for all engines. Signal = last completed US close;
   **entry = next US session** (never the signal bar); exit = H trading days later.
   Run after ~05:00 SGT. Duplicate runs on the same US day are skipped.
2. **Aggregation in position space**: each engine emits a target exposure in [−1,+1]
   that *persists* between its own updates; a Sharpe-weighted combiner nets them into
   one position per asset. Different update speeds therefore do **not** break the
   ensemble.
3. **Event engine scope**: trade the **post-gap multi-day drift** (PEAD), do **not**
   model the overnight gap (out of scope, needs microstructure/valuation modelling).
   This also keeps event checking to **once daily** — no token-burning live stream.
4. **PEAD is a hypothesis, not a licence**: classic PEAD is earnings-surprise based;
   whether it extends to GDELT news-density triggers is an **open empirical question**.
   The event engine's Stage 1 must be a **drift-existence test** before any trading claim.

---

## Open threads (ordered)

1. **Event engine Stage 1 — drift-existence test.** Do GDELT event days show
   significant post-gap drift at 1/5/10/20d vs matched non-event days (permutation)?
2. **Data amendments:** extend GDELT beyond the 2024 pilot (tagged floor ~2015);
   add **company/entity-level** events (earnings line-items, fireside chats, tech
   breakpoints like a DeepSeek-style release) — current mapping is macro-only.
3. **Pin the pipeline to n=4** so saved `regime_labels.parquet` matches the documented
   count (it currently auto-selects n=5 by BIC).
4. **Problem 2 Stage 2:** conditional lead-lag *within* event episodes.
5. **Ensemble combiner** (position-space, Sharpe-weighted).
6. **Problem 3:** LLM/RAG scenario layer (ChromaDB + SQLite + GitHub raw text).
7. **Streamlit MVP**, then integration/backtest phases.

---

## Working principles (established, keep following)

- Every claim about project data must come from data actually run. Hypotheses must be
  labelled as hypotheses with the test proposed.
- Null results are findings; document them rather than softening.
- Permutation tests over raw p-values; check robustness across specifications.
- Judge signals by **risk-adjusted return**, never hit-rate alone.
- Few, principled hypotheses beat large grids — and if a grid is run, the winner is
  labelled as a cherry-pick and forward-tested.
- The **repo is the source of truth**, not model memory.
