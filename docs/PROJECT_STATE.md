# PROJECT STATE — briefing document

*Upload this file (or the `briefing.md` bundle) at the start of a new conversation to
resume without re-explaining. Last updated: 2026-08-18 (late evening SGT). Keep it
updated after each workstream closes.*

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

### Regime engine — DONE, and now pinned in code
- PCA on **8 FRED series, 2006-01-02 → present** (SOFR dropped: redundant with EFFR,
  R²=0.998; HY spread dropped earlier, intentionally). DTWEXBGS is the binding series.
  Current panel: 5,382 dates × 5 components.
- **n=4 regimes**, chosen on **stability / persistence / separation**, NOT on BIC.
  As of 2026-08-18 this is **pinned in `config.yaml` as `regime.n_regimes: 4`** and read
  by every consumer; the pipeline no longer BIC-selects. `candidate_n_regimes` survives
  as diagnostic sweep input only, explicitly commented as a non-selector.
- BIC on the current panel: n=3 → 47282.9, n=4 → 44844.6, n=5 → 42148.1. BIC would pick
  n=5 and keeps falling to n=10 in the wider `verify_regimes.py` sweep, which is exactly
  why it is not used. `regime_classifier.py` now reports this and states why it is
  ignored, rather than silently obeying it.
- Regime character on the current fit (from `regime_classifier.py`):

  | regime | days | mean run | character | VIX | 10Y | USD |
  |---|---|---|---|---|---|---|
  | 0 | 1796 | 359 | STRESSED, easy policy, steep curve, weak USD | 22.5 | 2.80% | 92.8 |
  | 1 | 1023 | 512 | TIGHT policy, high 10Y, flat/inverted, strong USD | 17.9 | 4.16% | 121.8 |
  | 2 | 538 | 269 | CALM, tight policy, high 10Y, weak USD | 15.4 | 4.69% | 96.0 |
  | 3 | 2025 | 405 | EASY policy, low 10Y | 18.5 | 2.02% | 113.7 |

  Current regime as of 2026-08-18: **Regime 1**. (Note these are *mean* run lengths,
  inflated by very long maxima; the documented **median 52.5d** comes from
  `verify_regimes.py` and is a different statistic — do not compare them directly.)
- Re-validated after the panel extension (full re-run, not a spot-check):
  - Still favours n=4: seed ARI **1.000** (n=5 fragile at 0.774), run-length median
    **52.5d** (n=3 flickers at 3d), best silhouette.
  - **Weakened:** generalization gap now mildly favours fewer regimes; the 2024 GDELT
    event-alignment **no longer corroborates** n=4 (p≈0.32, 0/7 windows; was p<0.001,
    6/7 windows on the old panel). n=4 now stands on **internal structure alone**.
    Documented honestly in `docs/regime_event_validation.md`.
- **PCA renumbering hazard:** refits renumber components (stress axis moved PC2→PC3).
  `src/stress_axis.py` identifies the stress axis **data-drivenly** (PC most correlated
  with VIX; currently PC3, corr +0.963). Never hard-code a PC index. **This hazard
  recurred on 2026-08-18** — see the Problem 1 entry below.

### Problem 1 (safe-haven inversion) — DONE, clean NULL, now internally consistent
No inversion under either state definition, robust across windows 5/10/20/60 and
raw-vs-Fisher-z. Current figures (2026-08-18 re-run):

- **Liquidity sub-classifier (primary):** gap **+0.017**, p=0.441 (677 stress days of
  5,419 overlap). Sweep: raw +0.003/+0.001/+0.017/+0.001, Fisher-z −0.002/+0.005/
  +0.028/+0.006 — **no cell significant at any window or transform.**
- **VIX-stress macro regime (cross-check):** gap **+0.167** (opposite direction to the
  hypothesis), p=0.081 in the positive direction (1,084 stress days of 5,186 overlap).
  Sweep: raw +0.148/+0.162/+0.167/+0.139, Fisher-z +0.206/+0.201/+0.192/+0.152 — **all
  eight cells positive.**

Gold does **not** decouple from equities in stress — it co-moves at least as much
(dash-for-cash). A defensible negative finding contradicting popular intuition.

*Reading the p-values correctly:* `p` in the sweep is one-sided, P(null ≤ obs). p=0.915
means inversion is **unsupported**; it does not mean co-movement is significant. The
other tail is ≈0.085. The honest claim is: gold co-moves *more* in macro stress, and
that co-movement is **marginal, not significant at 5%**.

#### ⚠ Stress-axis bug found and fixed 2026-08-18

`safe_haven_robustness.py` was still selecting its cross-check stress regime by
**hard-coded PC2** — the hazard `stress_axis.py` exists to prevent. `safe_haven_test.py`
had been ported; this file was missed. The two scripts had been reporting **opposite
signs for the same statistic on the same data**, undetected:

| script | axis | stress days | gap @20d |
|---|---|---|---|
| `safe_haven_test.py` | PC3 (data-driven) | 1,084 | **+0.167** |
| `safe_haven_robustness.py` | PC2 (hard-coded) | 1,816 | **−0.209** |

The bug erred in the **flattering** direction: gaps of −0.20 at p 0.10–0.13 read as
marginal support for safe-haven inversion. After the port, p=0.915 *against* inversion,
and the 20d cell matches `safe_haven_test` to three decimals.

**Net effect on the documented result: it got stronger, not weaker.** The conclusion is
unchanged; what changed is that the robustness sweep stopped contradicting the headline
test. The primary liquidity block never reads the PCA scores and is untouched.

**Standing procedural lesson:** when a hazard is fixed in one script, grep for every
other consumer of the same hazard in the same commit. One-file fixes leave silent twins.

### Problem 1 ENGINE (macro analog) — BUILT + VALIDATED
Expanding-window walk-forward, 2010-01-01 → 2026-08-07, no look-ahead, non-overlapping
weekly rebalances. **Figures re-run 2026-08-18 (712 rebalances):**

| universe | spread/reb | ~/yr | Sharpe | hit | payoff | p |
|---|---|---|---|---|---|---|
| all 47 | +0.330% | ~17.1% | 0.57 | 51.3% | 0.99 | 0.0010 |
| long-history (35, ≥8y) | +0.214% | ~11.1% | 0.40 | 51.3% | 0.96 | 0.0040 |

Survives dropping recent-inception tickers → **not just an AI-boom artifact**.
Character: **long-tilt** (short leg +0.072%, still positive — no real short edge) and
**symmetric payoff** — the edge is a small *frequency* advantage, not fat tails.
A ~0.4 Sharpe standalone signal is one **ingredient**; the route to a presentable
number is the **ensemble**, not torturing this engine.

**Note on drift from previously documented figures.** This doc previously recorded 706
rebalances, Sharpe 0.60 / 0.43, spread +0.345% / +0.226%. The current run gives 712
rebalances and Sharpe 0.57 / 0.40. **This is ~6 weeks of additional data, not a
methodology change** — the n=4 pin was value-preserving by construction (a literal `4`
replaced by a config read whose value is `4`). No decision rests on the difference. A
policy is still needed on whether documented figures are frozen with an as-of date or
re-run at fixed checkpoints; silently drifting numbers are the thing to avoid.

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
  *direction*, not just level). Nearly doubled the baseline Sharpe and became
  significant. Hypothesis confirmed.
- **model_3** is a deliberate **control group**: best-in-sample of 48, explicitly
  labelled a cherry-pick. Stated hypothesis: its lead shrinks or inverts live.

### ⚠ Ledger history — first log was invalid and was WIPED

Launched 2026-08-17; its first six rows were computed from **stale and empty data** and
were **deleted**. Two bugs: `forward_log` called `download_data` without `--force` (the
cache-first fetcher served stale data while reporting success), and the signal date was
taken as the last index row (the macro panel is forward-filled, so PCA scores existed on
days with zero price coverage). Both fixed; the valid log restarted **2026-08-18**.

**Do not retro-fill skipped days.** The credibility of the forward test rests on entries
being timestamped (via git) *before* outcomes exist. Gaps are honest.

### 2026-08-17 vendor gap — corrected diagnosis

An earlier version of this document recorded 08-17 as returning "volume present but
Close/High/Low/Open all NaN." **That was wrong.** Verified directly against the vendor
(`yf.download("SPY", ...)`, bypassing the cache): **Open / High / Low / Volume are all
present; only Close and Adj Close are NaN.** All 47 assets affected (0/47 coverage).

**It has not self-healed** across three `--force` full re-pulls over ~24 hours, so the
earlier note that "Yahoo usually backfills within a day" is too optimistic as a general
expectation. Returns derive from Close, so `build_panel` correctly yields no return —
this is a genuine vendor gap, not a pipeline bug.

### Window integrity — IMPLEMENTED 2026-08-18 (commit 7352dd1)

Pre-registered while the ledger stood at **0 matured / 3 pending**, then implemented the
same day, before any row could mature.

> A row is scored `matured` only if **every session** of its H-day window has a return
> for **every picked asset** (strict). Incomplete windows are marked `short_window` with
> their realised session count, excluded from the headline summary, and remain visible
> in the full log. **Entry dates and picks are frozen at log time and never reassigned.**

What was actually broken, and why it mattered:

1. **Horizons were counted in panel index rows, not sessions.** `build_panel` uses
   `pd.bdate_range` (Mon–Fri, **holidays included as all-NaN rows**) and never imports
   `market_calendar`. So a market holiday looked identical to a data gap. Labor Day
   **2026-09-07** falls inside the live H=20 window. `forward_log` now counts **NYSE
   trading days** via a new `market_calendar.trading_days()` helper.
2. **`np.log1p(...).sum()` uses pandas' default `skipna=True`**, so a missing day inside
   a window was dropped silently and the trade was reported as a clean H-day result.
3. Maturation now additionally requires the window to end on or before the signal date,
   so windows extending past usable price data are not scored early.
4. `entry_date` was re-derived every run (stable only by accident). Now frozen.
5. `--dry-run` wrote to disk on days with no new US close — the guard sat inside the
   "new picks" branch and was unreachable on skip days. Fixed.

`short_window` rows **stay eligible for upgrade** to `matured` if the vendor backfills:
the window is a fixed set of sessions, so healing means those same sessions gain data,
not that the window slides. Entry date and picks never change.

**Status: implemented and pushed, but never yet exercised.** No row has matured, so the
`short_window` path is untested against live data. First real test is **~2026-08-24**
when model_1's rows mature — expect `4/5 sessions` flagged if 08-17's Close never
returns.

### Current ledger state (2026-08-18, evening SGT)

- Signal still **2026-08-14** (4 days stale). Ledger: **3 rows, 0 matured, 3 pending,
  0 short_window.**
- **Staleness clock:** halts with `MANUAL INTERVENTION NEEDED` at >5 days →
  **Thursday 2026-08-20** if no new usable close arrives.

### Daily command
```bash
cd ~/Projects/regime-aware-signal && source .venv/bin/activate
python -m src.forward_log
```
Run once daily after ~05:00 SGT. Skips if no new US close. Safe to run twice. Then
commit `docs/forward_scoreboard.md` — the git timestamp is what makes entries
pre-registered. The ledger CSV is gitignored machine state.

Watch for, in priority order: `MANUAL INTERVENTION NEEDED`; `SHORT WINDOW:`; whether the
signal date advanced; the three-way counter line.

---

## Architecture decisions (full detail in `docs/architecture_decisions.md`)

1. **One shared daily clock** for all engines. Signal = last completed US close with
   real prices; **entry = next US session**; exit = H trading days later. Duplicate
   same-day runs skip.
2. **Aggregation in position space**: each engine emits a target exposure in [−1,+1]
   that *persists* between its own updates; a Sharpe-weighted combiner nets them per
   asset. This is where the noise-cancellation that lifts ensemble Sharpe comes from.
3. **Event engine scope**: trade the **post-gap multi-day drift** only; concede the
   overnight gap as uncapturable. Side benefit: event checks run **once daily**.
4. **PEAD is a hypothesis, not a licence**: classic PEAD is earnings-surprise based and
   has weakened since the 1990s; whether it extends to GDELT news-density triggers is
   **open**. Stage 1 must be a **drift-existence test** before any trading claim.

---

## Open threads (ordered)

1. **Event engine Stage 1 — drift-existence test.** GDELT event days; returns at
   1/5/10/20d entered next-open; permutation-tested vs matched non-event days.
   **Power caveat:** the 2024 pilot yields ~30 event days — the same sample size whose
   fragility collapsed the regime–event alignment under a basis change. A null on 2024
   alone would be uninterpretable (no drift vs underpowered), which argues for extending
   GDELT toward the ~2015 tagged floor **before** running Stage 1.

2. **`analog_core._forward` counts index rows, not sessions.** Same bug class as the one
   fixed in `forward_log` on 2026-08-18, still open in the backtest path: a documented
   "20-day horizon" is sometimes 19 sessions plus a holiday NaN, and `skipna` hides it.
   **Hypothesis (untested):** the effect is small and roughly uniform across configs, so
   model *ranking* is unchanged even if levels shift slightly. **Test:** re-run
   `model_grid.py` with a session-counted horizon and compare the ranking, not just the
   Sharpes. Must be settled before the backtest figures go in the report.

3. **Policy on documented figures.** Backtest numbers drift as the panel grows (706 →
   712 rebalances between doc-write and re-run). Decide: freeze with an as-of date, or
   re-run at fixed checkpoints. Currently they drift silently.

4. **Data amendments:** extend GDELT beyond the 2024 pilot (tagged floor ~2015); add
   **company/entity-level** events (earnings line-items, fireside chats, tech
   breakpoints like a DeepSeek-style release) — current mapping is macro-only.

5. **Problem 2 Stage 2:** conditional lead-lag *within* event episodes.

6. **Ensemble combiner** (position-space, Sharpe-weighted).

7. **Problem 3:** LLM/RAG scenario layer (ChromaDB + SQLite + GitHub raw text).

8. **Streamlit MVP**, then integration/backtest phases.

### Closed 2026-08-18
- ~~Implement window integrity in `forward_log.py`~~ → done, commit 7352dd1.
- ~~Pin the pipeline to n=4~~ → done, commit 5ec014e. `regime_labels.parquet`
  regenerated at n=4. Verified by grep beforehand that **no script consumes that
  parquet** — every regime consumer fits its own GMM — so this was a
  documentation-integrity fix, not a correctness fix, and the commit message says so.
- ~~Port `safe_haven_robustness.py` to the data-driven stress axis~~ → done (see the
  Problem 1 entry). This one **was** a correctness fix.

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
- Identify axes by **economic meaning, never by index** — and when that hazard is fixed
  in one script, **grep for every other consumer in the same commit**.
- **Re-validate rather than assume** when the substrate changes.
- **Correct the record** when new evidence weakens a prior claim — including when the
  correction is to this document's own earlier description of a fact.
- **Verify before asserting in a commit message.** "No result changes" was an assumption
  until the consumer grep established it.
- **State the prediction before running the check.** The axis port was predicted to flip
  the cross-check sign, drop stress days to ~1,084, and match +0.167 at 20d. All three
  held, which is what makes the port *verified* rather than merely *different*.
- **Fail loud rather than log something plausible** (staleness guard; window integrity).
- Operational rules affecting the forward test are **pre-registered while the affected
  rows are still pending**, never after outcomes are visible.
- The **repo is the source of truth**, not model memory.
