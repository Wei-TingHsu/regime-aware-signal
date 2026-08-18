# PROJECT STATE — briefing document

*Upload this file (or the `briefing.md` bundle) at the start of a new conversation to
resume without re-explaining. Last updated: 2026-08-18 (evening SGT). Keep it updated
after each workstream closes.*

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
- **n=4 regimes**, chosen on **stability / persistence / separation**, NOT on BIC.
- Re-validated after the panel extension (full re-run, not a spot-check):
  - Still favours n=4: seed ARI **1.000** (n=5 fragile at 0.774), run-length median
    **52.5d** (n=3 flickers at 3d), best silhouette.
  - **Weakened:** generalization gap now mildly favours fewer regimes; the 2024 GDELT
    event-alignment **no longer corroborates** n=4 (p≈0.32, 0/7 windows; was p<0.001,
    6/7 windows on the old panel). n=4 now stands on **internal structure alone**.
    Documented honestly in `docs/regime_event_validation.md`.
- **PCA renumbering hazard:** refits renumber components (stress axis moved PC2→PC3).
  This had silently corrupted an earlier cross-check (a spurious −0.207 that vanished
  once corrected). `src/stress_axis.py` now identifies the stress axis **data-drivenly**
  (PC most correlated with VIX). Never hard-code a PC index.

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
  Stage 2 blocks on the event layer.

---

## Forward test — LIVE (valid log starts 2026-08-18)

Three models **pre-registered and frozen** in `config/models.yaml` before any live data.
All 48 grid configs recorded in `docs/model_grid_results.md` as the pre-registration
record. In-sample (frozen regimes):

| model | spec | Sharpe | ~/yr | hit | payoff | p |
|---|---|---|---|---|---|---|
| model_1_baseline | 5d, level, gauss σ1.5 | +0.21 | +5.4% | 51.1% | 0.93 | 0.0869 |
| model_2_horizon_trend | 10d, trend, gauss σ1.5 | +0.39 | +10.4% | 51.4% | 0.89 | 0.0190 |
| model_3_overfit | 20d, trend, gauss σ1.0 | +0.50 | +11.3% | 50.5% | 1.06 | 0.0390 |

- **model_2** is the *principled* amendment (trend-aware similarity = match macro
  *direction*, not just level — from the gold-vs-rising-rates insight). Nearly doubled
  the baseline Sharpe and became significant. Hypothesis confirmed.
- **model_3** is a deliberate **control group**: best-in-sample of 48, explicitly
  labelled a cherry-pick. Stated hypothesis: its lead shrinks or inverts live.

### ⚠ Ledger history — first log was invalid and was WIPED

The harness was launched 2026-08-17, but its first six rows were computed from **stale
and empty data** and were **deleted**. Two bugs caused it:

1. `forward_log` called `download_data` **without `--force`**, so the cache-first
   fetcher served **stale data while reporting success**.
2. The signal date was taken as the **last row of the index**. The macro panel is
   forward-filled, so PCA scores existed on days with **zero price coverage** — the
   engine computed picks from **empty bars**.

**Fixes applied** (`src/forward_log.py`):
- refresh now passes **`--force`**;
- signal date = **last bar with real price coverage** (≥40% of assets), not last index row;
- **staleness guard**: halts with `MANUAL INTERVENTION NEEDED` if the freshest usable
  data is >5 days old, rather than logging phantom picks.

The **valid** log restarted on **2026-08-18** (signal 2026-08-14 → entry 2026-08-17,
all three models pending). Nothing had matured, so the restart cost nothing.

**Do not retro-fill skipped days.** The credibility of the forward test rests on entries
being timestamped (via git) *before* outcomes exist. Gaps are honest.

### 2026-08-17 vendor gap — corrected diagnosis (supersedes earlier description)

An earlier version of this document recorded 08-17 as returning "volume present but
Close/High/Low/Open all NaN." **That was wrong and would misdirect a future reader.**
Verified directly against the vendor (`yf.download("SPY", ...)`, bypassing the cache):

| field | 2026-08-17 |
|---|---|
| Open / High / Low / Volume | **present** (SPY: 776.18 / 776.78 / 772.51 / 33.29M) |
| Close / Adj Close | **NaN** |

Only the Close is missing. All 47 assets are affected (0/47 coverage on that date).

**It did not self-heal.** The bar was still NaN after a `--force` full re-pull roughly a
day later, so the earlier note that "Yahoo usually backfills within a day" is too
optimistic as a general expectation. It may still repair before maturation (~08-24), in
which case `--force` heals the panel retroactively — but that is not to be assumed.

**Ruled out: a pipeline bug.** The 0/47 coverage initially looked too total for a vendor
gap, raising the hypothesis that `build_panel` was losing the row. The vendor probe
disproves it — Yahoo genuinely has no Close. `build_panel` is behaving correctly:
returns derive from Close (line 65), so a NaN Close correctly yields no return.

### Consequence for scoring — window integrity, not entry price

Scoring is **return-based, not price-based**. `forward_log.py:192` sets
`window = ret_dates[(ret_dates > entry)][:H]` — the H index dates strictly after entry —
and lines 195–196 compound daily returns over that window. **No entry price is ever
looked up**, so the missing 08-17 Close does not invalidate the entry date. An earlier
proposal to void rows on entry-price grounds was based on a mistaken reading and is
withdrawn.

The real exposure is one level down:

- The price path has **no forward-fill and no dropna** (`build_panel`: `ffill` is applied
  to `macro` only, line 109; returns are merely reindexed onto the business-day index,
  line 72). So the NaN Close on 08-17 **propagates into the 08-18 return** rather than
  being silently converted into a compounded 08-14→08-18 move sitting in a one-day slot.
  This is the cleaner of the two possible behaviours.
  *(Status: verified by implication — no `ffill`/`dropna` exists on the price path. The
  return-computation call itself was not located in `build_panel` under the searched
  names and has not been read directly. Worth a one-line confirmation.)*
- 08-17 occupies an index row with all-NaN values, so it **consumes a window slot while
  contributing nothing**. For the three pending rows (entry 08-17), model_1's H=5 window
  is 08-18/19/20/21/24, of which **08-18 is NaN**.
- `np.log1p(...).sum()` at line 195 uses pandas' default **`skipna=True`**, so that day is
  **silently dropped**: the row would be logged as a matured 5-day trade actually scored
  on 4 days. No error, no flag.

This is a **standing landmine**, not a one-off — any future vendor gap inside any future
window shortens it invisibly.

### Rule — window integrity (pre-registered 2026-08-18, before any row matured)

> A row is scored only if its H-day window has **full return coverage**. Windows with
> missing days are flagged with their **realised day count** and excluded from headline
> statistics; they remain visible in the full log. **Entry dates are never reassigned.**

Registered while the ledger stood at **0 matured / 3 pending**, so no outcome was visible
and the rule cannot be selection-on-results. **Not yet implemented** in
`src/forward_log.py` — implementation must land before model_1 matures (~2026-08-24).

The same principle as the staleness guard: **fail loud rather than log something
plausible.**

### Current ledger state (as of 2026-08-18, 17:00 SGT)

- Signal remains **2026-08-14** (4 days stale); the harness correctly skipped rather than
  logging a duplicate, since no new usable US close had landed.
- Ledger: **3 rows, 0 matured, 3 pending.**
- **Staleness clock:** halts with `MANUAL INTERVENTION NEEDED` at >5 days →
  **Thursday 2026-08-20** if no new usable close arrives. Tomorrow's run should advance
  the signal to 08-18 once tonight's US close lands, independently of whether 08-17's
  Close is ever repaired.

### Daily command
```bash
cd ~/Projects/regime-aware-signal && source .venv/bin/activate
python -m src.forward_log
```
Run once daily after ~05:00 SGT. Skips if no new US close. Scoreboard:
`docs/forward_scoreboard.md` (naive column + **NON-OVERLAP** column, the latter being
the statistically honest one).

*Housekeeping:* `forward_log.py:138` emits a `Pandas4Warning` — `pd.Timestamp.utcnow()`
is deprecated; use `pd.Timestamp.now("UTC").tz_localize(None)`.

---

## Architecture decisions (full detail in `docs/architecture_decisions.md`)

1. **One shared daily clock** for all engines. Signal = last completed US close with
   real prices; **entry = next US session** (never the signal bar); exit = H trading
   days later. Duplicate same-day runs skip.
2. **Aggregation in position space**: each engine emits a target exposure in [−1,+1]
   that *persists* between its own updates; a Sharpe-weighted combiner nets them per
   asset. This is what lets fast and slow engines coexist without separate clocks, and
   where the noise-cancellation that lifts ensemble Sharpe comes from.
3. **Event engine scope**: trade the **post-gap multi-day drift** only; concede the
   overnight gap as uncapturable and do **not** model it (needs microstructure /
   valuation work, out of scope). Side benefit: event checks run **once daily** — no
   token-burning live stream.
4. **PEAD is a hypothesis, not a licence**: classic PEAD is earnings-surprise based and
   has weakened since the 1990s; whether it extends to GDELT news-density triggers is
   **open**. Stage 1 must be a **drift-existence test** before any trading claim.

---

## Open threads (ordered)

0. **Implement the window-integrity rule** in `src/forward_log.py` (see above).
   **Deadline: before ~2026-08-24**, when model_1's first rows mature.

1. **Pin the pipeline to n=4.** `regime_classifier.py` auto-selects by lowest BIC among
   `candidate_n_regimes: [3, 4, 5]` and therefore **saves n=5**, contradicting the
   documented n=4. (`verify_regimes.py` sweeps n=2..10 where BIC keeps decreasing to the
   edge of the range — which is exactly why BIC is a poor selector here.)

   **Verified 2026-08-18 — this is a documentation-integrity fix, not a correctness fix.**
   `grep -rn "regime_labels" src/` returns no consumer outside `regime_classifier.py`;
   the only other reference is a docstring at `analog_engine.py:19` stating the engine
   deliberately refits rather than reading the saved parquet. Every regime consumer fits
   its own GMM: `analog_backtest.py:147` (n=4), `analog_engine.py:113` (n=4),
   `safe_haven_test.py:67` (n=4), `safe_haven_robustness.py:63` (n=4),
   `short_run_events.py:87` (`--n`), `regime_event_alignment.py:56` (swept),
   `analog_core.py:48` (from spec, default 4), `liquidity_classifier.py:133` (its own
   2-component model). **No documented result was computed on n=5 labels.** This must be
   stated in the commit message so history does not imply results were wrong.

   Scope, so it is done properly rather than quickly:
   - add `n_regimes: 4` to `config.yaml` with the stability/persistence/separation
     reasoning attached — an explicit pin, not a quiet narrowing of the candidate list;
   - comment `candidate_n_regimes` as **diagnostic sweep input for `verify_regimes.py`,
     not a selector**, so the two cannot drift apart;
   - `regime_classifier.py` reads the pin instead of BIC-selecting;
   - **replace the five hard-coded `n_components=4` literals** (listed above) with the
     config read — otherwise the pin is decorative and there are two sources of truth for
     the same parameter, the count-shaped version of the PC-index hazard `stress_axis.py`
     was built to eliminate;
   - **do not touch `config/models.yaml`** — the frozen specs carry their own
     `n_regimes` and are pre-registration evidence; `analog_core.py` keeps taking n from
     the spec, with config supplying only its default;
   - regenerate `regime_labels.parquet`;
   - update `analog_engine.py:19` (it names an n=5 parquet that will no longer exist);
   - remove caveat (a) from `docs/PIPELINE.md` §8.

   Substitutions are **value-preserving** (config says 4, literals said 4), so re-running
   `safe_haven_test.py` and `analog_backtest.py` must reproduce the documented numbers
   **exactly**. If any number moves, stop — something else is wrong.

2. **Event engine Stage 1 — drift-existence test.** GDELT event days; returns at
   1/5/10/20d entered next-open; permutation-tested vs matched non-event days.
   **Power caveat:** the 2024 pilot yields ~30 event days — the same sample size whose
   fragility collapsed the regime–event alignment under a basis change. A null on 2024
   alone would be uninterpretable (no drift vs underpowered), which argues for extending
   GDELT toward the ~2015 tagged floor **before** running Stage 1.

3. **Data amendments:** extend GDELT beyond the 2024 pilot (tagged floor ~2015);
   add **company/entity-level** events (earnings line-items, fireside chats, tech
   breakpoints like a DeepSeek-style release) — current mapping is macro-only.

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
  labelled a cherry-pick and forward-tested.
- Extend data by **removing redundancy, never by imputation**.
- Identify axes by **economic meaning, never by index**.
- **Re-validate rather than assume** when the substrate changes.
- **Correct the record** when new evidence weakens a prior claim — including when the
  correction is to this document's own earlier description of a fact (see the 08-17
  vendor-gap entry).
- **Verify before asserting in a commit message.** "No result changes" was an assumption
  until the consumer grep established it.
- **Fail loud rather than log something plausible** (staleness guard; window integrity).
- Operational rules affecting the forward test are **pre-registered while the affected
  rows are still pending**, never after outcomes are visible.
- The **repo is the source of truth**, not model memory.
