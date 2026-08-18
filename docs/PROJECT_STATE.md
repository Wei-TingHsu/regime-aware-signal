# PROJECT STATE — briefing document

*Upload this file (or the `briefing.md` bundle) at the start of a new conversation to
resume without re-explaining. Last updated: 2026-08-18 (night SGT). Keep it updated
after each workstream closes.*

> ## ⚠ READ FIRST — THE REPO IS MID-CASCADE
>
> The panel index was migrated from `pd.bdate_range` to the **NYSE session calendar**
> on 2026-08-18. That change propagates through everything. As of this writing the
> rebuild is **partially complete**. Do not quote any figure below marked STALE.
>
> | artefact | state |
> |---|---|
> | `asset_returns.parquet`, `macro_panel.parquet` | **REGENERATED** (sessions) |
> | `macro_pca_scores.parquet` | **REGENERATED** |
> | `verify_regimes.py` findings | **FRESH** — see "n=4 re-earned" below |
> | `regime_labels.parquet` | **STALE** — old panel |
> | Problem 1 figures (safe-haven, robustness) | **STALE** |
> | `analog_backtest`, `model_grid` figures | **STALE** |
> | forward-test ledger | **WIPED** — see below |
>
> Remaining order: `regime_classifier` → `liquidity_classifier` → `safe_haven_test` →
> `safe_haven_robustness` → `regime_event_alignment` (+ normalized, permutation, window
> sweep) → `analog_backtest` → `model_grid` → `chain_rotation` → forward-test restart.

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

## The calendar migration (2026-08-18)

**What changed.** `build_panel.business_day_index()` used `pd.bdate_range` — Mon–Fri
**including market holidays**. Those holiday rows had no asset returns at all, but the
macro side was forward-filled onto them, so they entered the PCA and the GMM as
near-duplicates of the preceding row. Manufactured data, in a project whose standing
rule is *extend data by removing redundancy, never by imputation*.

**Measured effect on the 2006+ panel:**

| | before | after |
|---|---|---|
| rows | 5,382 | **5,188** |
| rows with zero asset coverage | ~196 | **2** |
| non-session rows | 194 | **0** |

The "2" are 2026-08-17 (vendor gap) and 2026-08-18 (session not yet closed). So *no
prices* now reliably means **genuinely missing data** rather than *market was shut* —
the distinction that makes the `short_window` flag meaningful.

**Not a free win, and the doc should not sell it as one.** Of the 194 removed rows, a
minority carried genuinely new macro values (at most 46 per series; Good Fridays, when
the Fed is open and the NYSE is not, plus unscheduled closures like Hurricane Sandy
2012). Dropping them is still right: a macro state with no session is one no engine can
act on, and it contributes zero return information.

**Free side effect.** `analog_core._forward` compounds `rolling(H)` over index rows.
With a session index that *is* session counting, so the horizon bug logged as open
thread #2 is resolved with no code change — fix (b) subsuming fix (a), as predicted.

### n=4 re-earned on the session panel — hypothesis NOT falsified, but the case narrowed

Registered before running, with falsification conditions stated in advance.

| criterion | old panel | session panel | verdict |
|---|---|---|---|
| seed ARI n=4 | 1.000 (n=5 fragile 0.774) | **1.000** — but n=3 and n=5 also 1.000 | **leg lost** |
| silhouette | peaks n=4 | peaks n=4 at **0.4689**, vs n=2 0.4678, n=6 0.4641 | **tie, not support** |
| run-length median | 52.5d (n=3: 3d) | **51.0d**, 12 runs (n=3: 3d/87 runs, n=5: 5d, n=6: 7d, n=7: 3d) | **holds, decisively** |
| generalization gap | n=3 +0.45, n=4 +4.89 | n=3 +0.507, **n=4 +5.130**, n=5 +6.173, n=10 +8.621 | **against n=4, widened** |

Direct n=2 probe (n=2 is untested by `verify_regimes` on persistence/holdout — a
pre-existing blind spot, closed here):

| | n=2 | n=4 |
|---|---|---|
| median run | 4.0 | **51.0** |
| mean run | 471.6 | 432.3 |
| n_runs | 11 | 12 |
| ARI | 1.000 | 1.000 |
| gen gap | **−0.080** | +5.130 |

Pre-registered rule: *n=2 displaces n=4 only if it beats n=4 on run-length persistence
**and** the generalization gap.* It wins the gap decisively and loses run-length
decisively, so **n=4 stands**.

**The honest state of the n=4 case.** It now rests on **one quantitative line plus an
economic argument**:
1. **Run-length persistence** — n=4 is the only count producing macro-scale segments
   (median 51d); every alternative flickers at 3–7 day medians. n=2's median of 4 days
   against a mean of 471 is a bimodal structure: a few multi-year epochs plus brief
   boundary artifacts.
2. **Economic structure** — PC1 (rates, 52.3%) and PC2 (money/dollar, 27.2%) carry
   79.6% of variance between them. A 2-regime split collapses two distinct macro axes
   into one risk-on/risk-off dimension. Four states let the analog engine condition on
   rate structure and stress structure separately, which is the engine's premise.

"Three independent lines converge on n=4" was retired when GDELT alignment collapsed;
after tonight, **seed stability and silhouette no longer support it either**. This is a
defensible choice, not a strongly corroborated one, and must be written up that way.

**A prior that was wrong, recorded.** The registered prior was that removing duplicate
rows would *reduce* apparent persistence and leave ARI intact. The opposite happened:
persistence barely moved (52.5 → 51.0), while the duplicates turned out to have been
*destabilising the n=5 fit*. Removing them made n=5 perfectly seed-stable and destroyed
the argument that had discriminated against it. **The old "n=5 is fragile at 0.774"
finding was partly an artifact of holiday rows** and must be struck wherever it appears.

### PCA on the session panel (5,188 × 8, from 2006-01-03)

| PC | variance | best proxy | corr |
|---|---|---|---|
| PC1 | 52.3% | DGS2 (rates/tightness) | +0.984 |
| PC2 | 27.2% | M2SL (money supply) | +0.813 |
| PC3 | 12.8% | VIXCLS (risk stress) | +0.964 |
| PC4 | 5.0% | T10Y2Y (curve) | +0.402 (weak) |
| PC5 | 1.9% | DTWEXBGS (USD) | +0.245 (weak) |

Top 3 = 92.3% of variance. **No renumbering this refit** — the stress axis stays PC3,
so axis-dependent results remain comparable to the pre-migration basis. `stress_axis.py`
continues to identify it data-drivenly regardless.

---

## Current status by workstream

### Regime engine — n=4 pinned in config, labels pending regeneration
- PCA on **8 FRED series, 2006-01-03 → present**, NYSE sessions (SOFR dropped:
  redundant with EFFR, R²=0.998; HY spread dropped earlier, intentionally). DTWEXBGS is
  the binding series (5,188 observations = the full 2006+ session count).
- **n=4**, pinned as `regime.n_regimes: 4` in `config.yaml` since commit 5ec014e and
  read by every consumer. `regime_classifier.py` no longer BIC-selects; it reports what
  BIC would have chosen (n=10 at the edge of the sweep) and why that is ignored.
- **2024 GDELT event-alignment does not corroborate n=4** on the extended panel
  (p≈0.32, 0/7 windows; was p<0.001, 6/7 on the original 2018+ panel). STALE — needs
  re-running on the session panel.
- **PCA renumbering hazard:** refits can renumber components. `src/stress_axis.py`
  identifies the stress axis data-drivenly (PC most correlated with VIX). Never
  hard-code a PC index. This hazard **recurred and was caught on 2026-08-18** — see
  Problem 1.

### Problem 1 (safe-haven inversion) — DONE, clean NULL *(figures STALE)*
No inversion under either state definition, robust across windows 5/10/20/60 and
raw-vs-Fisher-z. Pre-migration figures, to be re-run:
- Liquidity sub-classifier: gap **+0.017**, p=0.441 (677 stress days / 5,419 overlap)
- VIX-stress macro regime: gap **+0.167**, p=0.081 positive direction (1,084 / 5,186)
- Robustness sweep: primary block no significant cell at any window or transform; macro
  cross-check all eight cells positive

Gold does **not** decouple from equities in stress — it co-moves at least as much
(dash-for-cash). A defensible negative finding contradicting popular intuition.

*Reading the p-values:* `p` in the sweep is one-sided, P(null ≤ obs). p=0.915 means
inversion is **unsupported**; it does not mean co-movement is significant. The honest
claim: gold co-moves *more* in macro stress, **marginally, not significantly at 5%**.

#### Stress-axis bug found and fixed 2026-08-18
`safe_haven_robustness.py` selected its cross-check stress regime by **hard-coded PC2**
— the hazard `stress_axis.py` exists to prevent. `safe_haven_test.py` had been ported;
this file was missed. The two had been reporting **opposite signs for the same statistic
on the same data**, undetected:

| script | axis | stress days | gap @20d |
|---|---|---|---|
| `safe_haven_test.py` | PC3 (data-driven) | 1,084 | **+0.167** |
| `safe_haven_robustness.py` | PC2 (hard-coded) | 1,816 | **−0.209** |

The bug erred in the **flattering** direction: −0.20 at p 0.10–0.13 reads as marginal
support for inversion. Corrected, p=0.915 *against*. After the port the two scripts
agree to three decimals at 20d, and the documented result got **stronger** — the sweep
stopped contradicting the headline test.

**Standing procedural lesson:** when a hazard is fixed in one script, grep for every
other consumer of the same hazard **in the same commit**. One-file fixes leave silent
twins.

### Problem 1 ENGINE (macro analog) — BUILT + VALIDATED *(figures STALE)*
Expanding-window walk-forward, 2010 → 2026, no look-ahead, non-overlapping weekly
rebalances. Pre-migration (712 rebalances):

| universe | spread/reb | ~/yr | Sharpe | hit | payoff | p |
|---|---|---|---|---|---|---|
| all 47 | +0.330% | ~17.1% | 0.57 | 51.3% | 0.99 | 0.0010 |
| long-history (35, ≥8y) | +0.214% | ~11.1% | 0.40 | 51.3% | 0.96 | 0.0040 |

Survives dropping recent-inception tickers → **not just an AI-boom artifact**.
Character: **long-tilt** (short leg +0.072%, still positive — no real short edge) and
**symmetric payoff** — a small *frequency* advantage, not fat tails. A ~0.4 Sharpe
standalone signal is one **ingredient**; the route to a presentable number is the
**ensemble**, not torturing this engine.

*Earlier figures in this doc (706 rebalances, Sharpe 0.60/0.43) differed only by ~6
weeks of additional data. The n=4 pin was value-preserving by construction. The
calendar migration, by contrast, is expected to move these numbers for real.*

### Problem 2 (rotation chain) — Stage 1 NULL, reframed *(figures STALE)*
Chain NVDA/TSM/ASML/MU/INTC, leave-one-out residualization to strip shared semi beta.
- Discovered order ASML→TSM→MU→INTC→NVDA; vs thesis (NVDA→TSM→ASML→MU→INTC)
  Spearman **−0.100**, permutation **p=0.597**
- Sub-period stability **−0.250** → **anti-stable**, no persistent order
- **Reason:** the test was unconditional. Rotation is event-initiated, so lead-lag must
  be measured **within event-triggered episodes**. Stage 2 blocks on the event layer.

---

## Forward test — WIPED 2026-08-18 (second wipe), restart pending

Three models **pre-registered and frozen** in `config/models.yaml` before any live data.
All 48 grid configs in `docs/model_grid_results.md` as the pre-registration record.

| model | spec | Sharpe | ~/yr | hit | payoff | p |
|---|---|---|---|---|---|---|
| model_1_baseline | 5d, level, gauss σ1.5 | +0.21 | +5.4% | 51.1% | 0.93 | 0.0869 |
| model_2_horizon_trend | 10d, trend, gauss σ1.5 | +0.39 | +10.4% | 51.4% | 0.89 | 0.0190 |
| model_3_overfit | 20d, trend, gauss σ1.0 | +0.50 | +11.3% | 50.5% | 1.06 | 0.0390 |

*(In-sample figures computed on the pre-migration basis — STALE. `model_grid.py` must be
re-run on the session panel. The re-run is recorded **alongside** the original, never
overwriting it: `model_grid_results.md` is the pre-registration record for
`model_3_overfit` and the three frozen specs do not change whatever the new grid says.)*

### Wipe #1 — 2026-08-17 (stale + empty data)
First six rows were computed from stale cache and empty bars. Two bugs: `download_data`
called without `--force`, and signal date taken as the last index row. Both fixed.

### Wipe #2 — 2026-08-18 (basis change), DELIBERATE

The ledger held 3 rows (0 matured) computed on the **bdate_range** basis.
`macro_pca_scores.parquet` has since been regenerated on the **session** basis, and
`forward_log` refits regimes on the fly from that file. Continuing would have produced a
ledger mixing two bases with no way to attribute any result to either.

Deleted `processed/forward_ledger.csv` while **0 rows had matured**, so the restart cost
nothing — same situation as wipe #1. `forward_log` must not run again until the cascade
is committed; if a daily window passes first, **skip the day** rather than log against a
half-migrated repo. Gaps are honest.

**Do not retro-fill skipped days.** Credibility rests on entries being git-timestamped
*before* outcomes exist.

### Window integrity — IMPLEMENTED 2026-08-18 (commit 7352dd1), NOT YET EXERCISED

> A row is scored `matured` only if **every session** of its H-day window has a return
> for **every picked asset** (strict). Incomplete windows are marked `short_window` with
> their realised session count, excluded from the headline summary, and remain visible
> in the full log. **Entry dates and picks are frozen at log time and never reassigned.**

Pre-registered at 0 matured / 3 pending, implemented the same day. What was broken:
horizons counted panel index rows (holidays included) rather than sessions;
`np.log1p(...).sum()` silently dropped missing days via `skipna=True`; maturation could
fire on windows extending past usable data; `entry_date` was re-derived every run;
`--dry-run` wrote to disk on skip days. All fixed.

`short_window` rows **stay eligible for upgrade** to `matured` if a vendor backfills —
the window is a fixed set of sessions, so healing means those sessions gain data, not
that the window slides.

**Never exercised against live data.** The ledger is now empty, so the first real test
is whenever a vendor gap next lands inside a live window.

### 2026-08-17 vendor gap
Verified against the vendor directly (`yf.download("SPY", ...)`, bypassing cache):
**Open/High/Low/Volume present; only Close and Adj Close NaN**, all 47 assets. **Has not
self-healed** across three `--force` full re-pulls in ~24 hours, so "Yahoo backfills
within a day" is too optimistic. Returns derive from Close, so `build_panel` correctly
yields no return — a genuine vendor gap, not a pipeline bug.

### Daily command
```bash
cd ~/Projects/regime-aware-signal && source .venv/bin/activate
python -m src.forward_log
```
Once daily after ~05:00 SGT. Skips if no new US close. Safe to run twice. Then commit
`docs/forward_scoreboard.md` — the git timestamp is what makes entries pre-registered.
The ledger CSV is gitignored machine state.

Watch, in priority order: `MANUAL INTERVENTION NEEDED`; `SHORT WINDOW:`; whether the
signal date advanced; the three-way counter line.

---

## Architecture decisions (full detail in `docs/architecture_decisions.md`)

1. **One shared daily clock.** Signal = last completed US close with real prices;
   **entry = next US session**; exit = H sessions later. Duplicate same-day runs skip.
2. **Aggregation in position space**: each engine emits a target exposure in [−1,+1]
   that *persists* between its own updates; a Sharpe-weighted combiner nets them per
   asset. This is where ensemble noise-cancellation comes from.
3. **Event engine scope**: trade the **post-gap multi-day drift** only; concede the
   overnight gap. Side benefit: event checks run **once daily**.
4. **PEAD is a hypothesis, not a licence**: classic PEAD is earnings-surprise based and
   has weakened since the 1990s; whether it extends to GDELT news-density triggers is
   **open**. Stage 1 must be a **drift-existence test** before any trading claim.

---

## Open threads (ordered)

1. **Finish the cascade.** Order in the banner at the top of this document. Nothing
   should be quoted or committed as a result until it completes.

2. **Event engine Stage 1 — drift-existence test.** GDELT event days; returns at
   1/5/10/20d entered next-open; permutation-tested vs matched non-event days.
   **Power caveat:** the 2024 pilot yields ~30 event days — the sample size whose
   fragility collapsed the regime–event alignment under a basis change. A null on 2024
   alone would be uninterpretable, which argues for extending GDELT toward the ~2015
   tagged floor **before** running Stage 1.

3. **The n=4 generalization gap is a live concern, not an academic one.** +5.130 means
   the regime model transfers poorly to 2025–26 — the exact period the forward test is
   running in. **Test:** check which regimes 2025+ rows occupy and whether they sit in a
   low-density corner of the training distribution. If the live period is
   out-of-distribution for the fitted regimes, the analog engine's regime gate is
   selecting analogs from a state the present does not resemble.

4. **Policy on documented figures.** Numbers drift as the panel grows. Decide: freeze
   with an as-of date, or re-run at fixed checkpoints. Currently they drift silently.

5. **Data amendments:** extend GDELT beyond the 2024 pilot (tagged floor ~2015); add
   **company/entity-level** events — current mapping is macro-only.

6. **Problem 2 Stage 2:** conditional lead-lag *within* event episodes.

7. **Ensemble combiner** (position-space, Sharpe-weighted).

8. **Problem 3:** LLM/RAG scenario layer (ChromaDB + SQLite + GitHub raw text).

9. **Streamlit MVP**, then integration/backtest phases.

### Closed 2026-08-18
- ~~Implement window integrity~~ → commit 7352dd1.
- ~~Pin the pipeline to n=4~~ → commit 5ec014e. Verified by grep beforehand that **no
  script consumes `regime_labels.parquet`** — every consumer fits its own GMM — so this
  was a documentation-integrity fix, not a correctness fix.
- ~~Port `safe_haven_robustness.py` to the data-driven stress axis~~ → this one **was** a
  correctness fix.
- ~~`analog_core._forward` counts index rows, not sessions~~ → resolved by the calendar
  migration; no code change needed.

---

## Working principles (established, keep following)

- Every claim about project data must come from data actually run. Hypotheses must be
  labelled as hypotheses with the test proposed.
- Null results are findings; document them rather than softening.
- Permutation tests over raw p-values; check robustness across specifications.
- Judge signals by **risk-adjusted return**, never hit-rate alone.
- Few, principled hypotheses beat large grids — and if a grid is run, the winner is
  labelled a cherry-pick and forward-tested.
- Extend data by **removing redundancy, never by imputation** — including redundancy
  that enters through the *index* rather than through a fetcher.
- Identify axes by **economic meaning, never by index** — and when that hazard is fixed
  in one script, **grep for every other consumer in the same commit**.
- **Re-validate rather than assume** when the substrate changes.
- **Correct the record** when new evidence weakens a prior claim — including when the
  correction is to this document's own earlier description of a fact.
- **Verify before asserting in a commit message.**
- **State the prediction before running the check**, and **record priors that turn out
  wrong** — the n=5-fragility finding was an artifact, and only a stated prior made that
  visible.
- **Register falsification conditions before re-validating**, so the verdict cannot be
  reverse-engineered from whatever the numbers happen to say.
- **Take the correct long-term fix over the contained one** when they conflict. Fixing
  `_forward` alone would have been discarded work; fixing the panel subsumed it.
- **Fail loud rather than log something plausible.**
- Operational rules affecting the forward test are **pre-registered while the affected
  rows are still pending**, never after outcomes are visible.
- The **repo is the source of truth**, not model memory.
