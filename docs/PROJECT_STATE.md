# PROJECT STATE — briefing document

*Upload this file (or the `briefing.md` bundle) at the start of a new conversation to
resume without re-explaining. Last updated: 2026-08-19. Keep it updated after each
workstream closes.*

> ## CASCADE STATUS — nearly complete
>
> The panel index was migrated from `pd.bdate_range` to the **NYSE session calendar**
> on 2026-08-18. Everything downstream has been re-run except two scripts.
>
> | artefact | state |
> |---|---|
> | `asset_returns`, `macro_panel`, `macro_pca_scores` | **REGENERATED** (sessions) |
> | `verify_regimes` — n=4 re-earned | **FRESH** |
> | `regime_labels.parquet` | **REGENERATED** |
> | `liquidity_states.parquet` | **REGENERATED** |
> | Problem 1 (safe-haven + robustness) | **RE-RUN** |
> | GDELT alignment (4 scripts) | **RE-RUN** |
> | `analog_backtest` | **RE-RUN — figures revised down, see below** |
> | forward test | **RESTARTED** on the new basis, 3 live rows |
> | `model_grid` | **STALE** |
> | `chain_rotation` | **STALE** |

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

**Where the three engines actually stand (plain statement, 2026-08-19).**
1. **Macro engine — measured and thin.** Sharpe **0.25–0.51 depending on universe**
   (see below). This engine is *done being measured*. It does not get "made thicker":
   re-tuning it until the number improves is the overfitting failure the working
   principles exist to prevent.
2. **Event engine — its real test has not happened.** The drift-existence test is
   unrun, and the 2024 pilot is underpowered for it.
3. **Rotation chain — its first test asked the wrong question.** Stage 1 tested for a
   *permanent* lead-lag order across all history. Rotation is event-triggered, so that
   test averaged brief cascade episodes together with long stretches of noise. The
   correct test is conditional on event episodes, and it **blocks on the event engine**.

The system thesis is that three engines with different data, horizons and failure modes
combine to something better than any one of them — error cancellation, not addition.
**That correlation has never been measured.** So "each engine is individually modest"
and "the system does not work" remain genuinely different claims until the ensemble step
runs. Equally: if the event engine finds no drift on an adequately powered sample *and*
the conditional rotation test is null, the signal-sensing product has no foundation and
the correct response is to say so. Three documented nulls with rigorous method remain a
legitimate capstone; that is a weaker *business*, not a failed *project*.

---

## The calendar migration (2026-08-18)

`build_panel.business_day_index()` used `pd.bdate_range` — Mon–Fri **including market
holidays**. Those rows had no asset returns at all, but the macro side was
forward-filled onto them, so they entered the PCA and the GMM as near-duplicates of the
preceding row. Manufactured data, against the standing rule *extend by removing
redundancy, never by imputation*.

| 2006+ panel | before | after |
|---|---|---|
| rows | 5,382 | **5,188** |
| rows with zero asset coverage | ~196 | **2** |
| non-session rows | 194 | **0** |

"No prices" now reliably means **genuinely missing data** rather than *market was shut*.
Independently confirmed by `liquidity_classifier`, which dropped 3 all-NaN rows where it
would previously have dropped ~293.

**Not free.** Of the 194 removed rows a minority carried genuinely new macro values
(≤46 per series; Good Fridays — Fed open, NYSE closed — plus unscheduled closures such
as Hurricane Sandy 2012). Still correct: a macro state with no session cannot be traded
and carries no return information.

**Free side effect.** `analog_core._forward` compounds `rolling(H)` over index rows.
With a session index that *is* session counting, so the horizon bug logged as an open
thread is resolved with no code change — fix (b) subsuming fix (a).

### Which results were exposed and which were immune — the key structural finding

**Problem 1 was structurally immune.** `rolling_corr` does `.dropna(how="all").dropna()`
before computing, so all-NaN holiday rows were *already* being discarded. The GLD–SPY
correlation series reports 5,458 days and mean +0.069 both before and after, identically.
Overlap arithmetic: 5,382 − 194 − 2 = 5,186 before; 5,188 − 2 = 5,186 after. The same
number for mechanical reasons.

**The backtest had no such protection.** `analog_core` reindexes returns onto the score
index without dropping, so `_forward` was compounding across holiday NaNs and
`skipna=True` silently shortened horizons.

**Therefore: Problem 1's stability is NOT evidence that the migration was
inconsequential. It is evidence that Problem 1 was never exposed.** The backtest is
where the error actually lived, and it moved.

### n=4 re-earned on the session panel — hypothesis NOT falsified, case narrowed

Registered with falsification conditions stated before running.

| criterion | old panel | session panel | verdict |
|---|---|---|---|
| seed ARI n=4 | 1.000 (n=5 fragile 0.774) | **1.000** — n=3 and n=5 also 1.000 | **leg lost** |
| silhouette | peaks n=4 | n=4 **0.4689** vs n=2 0.4678, n=6 0.4641 | **tie, not support** |
| run-length median | 52.5d | **51.0d**, 12 runs (n=3: 3d/87 runs; n=5: 5d; n=7: 3d) | **holds decisively** |
| generalization gap | n=4 +4.89 | **n=4 +5.130**, n=3 +0.507, n=5 +6.173 | **against n=4, widened** |

Direct n=2 probe (never tested by `verify_regimes` on persistence/holdout — a
pre-existing blind spot, closed here): median run **4.0** vs n=4's 51.0; gap **−0.080**
vs n=4's +5.130; ARI 1.000 both. Pre-registered rule required n=2 to win **both** to
displace n=4. It won one. **n=4 stands.**

**The honest state of the n=4 case: one quantitative line plus an economic argument.**
1. **Run-length persistence** — n=4 is the only count producing macro-scale segments;
   every alternative flickers at 3–7 day medians.
2. **Economic structure** — PC1 (rates, 52.3%) + PC2 (money/dollar, 27.2%) = 79.6% of
   variance. A 2-regime split collapses two distinct macro axes into one risk-on/risk-off
   dimension. Four states let the engine condition on rate and stress structure
   separately, which is its premise.

"Three converging lines" was retired when GDELT alignment collapsed; seed stability and
silhouette no longer support it either. **Two mild signals now favour n=5** — it became
perfectly seed-stable on this panel, and it is the only count approaching significance in
the GDELT permutation (p=0.079). Neither is decisive; both are recorded rather than
omitted.

**A registered prior that was wrong.** The prior was that removing duplicate rows would
*reduce* persistence and leave ARI intact. The opposite happened: persistence barely
moved (52.5 → 51.0) while the duplicates turned out to have been *destabilising the n=5
fit*. **The old "n=5 fragile at 0.774" finding was partly an artifact of holiday rows**
and must be struck wherever it appears. Only a stated prior made this visible.

### PCA on the session panel (5,188 × 8, from 2006-01-03)

| PC | variance | best proxy | corr |
|---|---|---|---|
| PC1 | 52.3% | DGS2 (rates/tightness) | +0.984 |
| PC2 | 27.2% | M2SL (money supply) | +0.813 |
| PC3 | 12.8% | VIXCLS (risk stress) | +0.964 |
| PC4 | 5.0% | T10Y2Y (curve) | +0.402 (weak) |
| PC5 | 1.9% | DTWEXBGS (USD) | +0.245 (weak) |

Top 3 = 92.3%. **No renumbering this refit** — stress axis stays PC3.

---

## Current status by workstream

### Regime engine — DONE on the session basis
- PCA on **8 FRED series, 2006-01-03 → present**, NYSE sessions. DTWEXBGS binding
  (5,188 observations = the full 2006+ session count).
- **n=4 pinned** in `config.yaml` as `regime.n_regimes: 4`; read by every consumer.
  BIC reported, never obeyed (it decreases to n=10 at the edge of the sweep).
- Regime structure barely moved across the migration — each regime shrank 3–4%, matching
  the row removal, and macro character is unchanged to two decimals:

  | regime | days (was) | mean run | VIX | 10Y | USD | character |
  |---|---|---|---|---|---|---|
  | 0 | 1735 (1796) | 434 | 22.5 | 2.80% | 92.7 | STRESSED, easy policy, steep, weak USD |
  | 1 | 984 (1023) | 492 | 18.0 | 4.16% | 121.8 | TIGHT policy, high 10Y, flat/inverted, strong USD |
  | 2 | 516 (538) | 258 | 15.4 | 4.69% | 96.0 | CALM, tight policy, high 10Y, weak USD |
  | 3 | 1953 (2025) | 488 | 18.5 | 2.02% | 113.7 | EASY policy, low 10Y |

  Current regime as of 2026-08-18: **Regime 1**.
- **Classifier and verifier agree exactly**: 12 runs, median 51.0, mean 432.3 — the same
  numbers from two independently written code paths on the same model and data.
- **PCA renumbering hazard:** `src/stress_axis.py` identifies the stress axis
  data-drivenly (PC most correlated with VIX). Never hard-code a PC index. This hazard
  **recurred and was caught on 2026-08-18** — see Problem 1.

### Problem 1 (safe-haven inversion) — DONE, clean NULL, confirmed basis-independent

| | pre-migration | session panel |
|---|---|---|
| liquidity gap | +0.017, p 0.441 | **+0.011, p 0.488** (581 stress days / 5,448 overlap) |
| macro gap | +0.167, p 0.081 | **+0.167, p 0.0814** (1,084 / 5,186) |
| stress axis | PC3, VIX +0.963 | PC3, VIX **+0.964** |

Robustness sweep: **cross-check block identical to three decimals** across all eight
cells (raw +0.148/+0.162/+0.167/+0.139; Fisher-z +0.206/+0.201/+0.192/+0.152). Primary
block shifted only via the liquidity refit and remains non-significant everywhere
(p 0.415–0.537).

**One phrasing correction.** Three of four primary raw cells are now mildly *negative*
(−0.006/−0.004/−0.007) rather than mildly positive. These are noise around zero —
magnitudes an order below the cross-check, p-values dead centre of the null. The summary
line "if anything it co-moves slightly more" is now carried by the **cross-check** block,
not the primary one, and should be written that way.

Gold does **not** decouple from equities in stress — it co-moves at least as much
(dash-for-cash). A defensible negative finding contradicting popular intuition.

*Reading the p-values:* one-sided, P(null ≤ obs). p=0.915 means inversion is
**unsupported**; it does not mean co-movement is significant. Honest claim: gold
co-moves *more* in macro stress, **marginally, not significantly at 5%**.

#### Stress-axis bug found and fixed 2026-08-18
`safe_haven_robustness.py` selected its cross-check stress regime by **hard-coded PC2**.
`safe_haven_test.py` had been ported to `stress_axis.py`; this file was missed. The two
had been reporting **opposite signs for the same statistic on the same data**:

| script | axis | stress days | gap @20d |
|---|---|---|---|
| `safe_haven_test.py` | PC3 (data-driven) | 1,084 | **+0.167** |
| `safe_haven_robustness.py` | PC2 (hard-coded) | 1,816 | **−0.209** |

The bug erred in the **flattering** direction: −0.20 at p 0.10–0.13 reads as marginal
support for inversion; corrected, p=0.915 *against*. After the port the two agree to
three decimals and the documented result got **stronger** — the sweep stopped
contradicting the headline test.

**Standing procedural lesson:** when a hazard is fixed in one script, grep for every
other consumer of the same hazard **in the same commit**. One-file fixes leave silent
twins.

### Problem 1 ENGINE (macro analog) — REVISED DOWN on the session basis

Expanding-window walk-forward, 2010-01-04 → 2026-08-11, no look-ahead, non-overlapping
weekly rebalances, **835 rebalances**:

| universe | spread/reb | ~/yr | Sharpe | hit | payoff | p |
|---|---|---|---|---|---|---|
| all 47 | +0.292% | ~15.2% | **0.51** | 50.3% | 1.04 | 0.0010 |
| long-history (35, ≥8y) | +0.129% | ~6.7% | **0.25** | 49.7% | 1.01 | 0.0380 |

**Comparison to the pre-migration figures, which were wrong:**

| | before | after | change |
|---|---|---|---|
| rebalances | 712 | 835 | +123 |
| ALL-47 Sharpe | 0.57 | 0.51 | −11% |
| long-hist Sharpe | 0.40 | **0.25** | **−38%** |
| long-hist p | 0.0040 | **0.0380** | 10× weaker |
| long-hist hit-rate | 51.3% | **49.7%** | below 50% |

**What this means, stated plainly.** The all-asset block survives (p=0.0010). **The
survivorship-bias check is what degraded.** That block exists precisely to answer *"is
this just recent AI-boom tickers?"* The pre-migration answer was a confident no. The
honest answer now: **the edge weakens substantially once recent-inception tickers are
removed, and what remains clears the 5% bar only just.** The previously documented claim
"survives dropping recent-inception tickers → not just an AI-boom artifact" is
**overstated and retired.**

**Why the direction is right, not a regression.** The old numbers were computed with
`_forward` compounding H index rows, where a holiday contributed a NaN that `skipna`
dropped — so a "5-day" forward return was sometimes 4 days of actual market movement,
understating realised volatility and flattering the Sharpe. The new figures are what the
strategy actually earns over five sessions. Lower and correct beats higher and wrong.

**Why rebalances rose while the panel shrank:** `rebs` steps by H=5 *index positions*.
Removing holidays also removed dead bars, so more usable rebalance points survive the
`min_analogs` filter.

**Character note:** payoff ratio moved 0.99/0.96 → 1.04/1.01, so the engine is now mildly
positively asymmetric rather than purely a frequency edge. Minor, but the old description
needs adjusting.

**Ensemble framing — REVISED.** The previous line "a ~0.4 Sharpe standalone signal is one
ingredient" **no longer describes either block** and is retired. The correct statement is
**0.25–0.51 depending on universe**, where the low end is the survivorship-controlled
universe and the drop from 0.40 to 0.25 is what the calendar fix revealed. The ingredient
is **thinner than previously recorded**. The route to a presentable number remains the
**ensemble**, not torturing this engine — and the ensemble case is now more load-bearing,
not less.

### GDELT regime↔event alignment — still NULL on the session basis

| | pre-migration | session panel |
|---|---|---|
| n=4 permutation (z-diff) | p≈0.32 | **p=0.261** |
| windows clearing p<.05 | 0/7 | **0/7** |
| FOMC overlay | 9/10 | **9/10** |

Same verdict, marginally stronger observed effect (+0.080 vs null −0.000), still nowhere
near significance. The FOMC check is the external-validity anchor and confirms the GDELT
file is intact — it validates against a real calendar, not against the panel.

**n=5, not n=4, is the count that flirts with significance** — z-diff p=0.079 (marginal),
and the lowest column throughout the window sweep (0.051/0.077/0.080/0.097/0.102). It
clears no window at p<0.05, so nothing changes, but a reader looking for event support
finds it pointing at n=5. Recorded, not omitted.

**Low power, stated either way:** 2024-only overlap, 252 days, ~30 stress days at n=4.

### Problem 2 (rotation chain) — Stage 1 NULL, reframed *(STALE — not re-run)*
Chain NVDA/TSM/ASML/MU/INTC, leave-one-out residualization to strip shared semi beta.
- Discovered order ASML→TSM→MU→INTC→NVDA; vs thesis Spearman **−0.100**, permutation
  **p=0.597**; sub-period stability **−0.250** → **anti-stable**
- **Why this was the wrong question:** it assumed a *permanent* pecking order. Rotation
  is event-triggered — an event fires, attention hits a group, money moves through it
  over days; between events there is only noise. Testing unconditionally mixes brief
  cascade episodes with long quiet stretches and the noise swamps the signal.
- **The right question (Stage 2):** within the days following an event naming this group,
  is there a sequence? Same chain, same statistics, measured inside episodes.
  **Blocks on the event engine** — episodes must be defined before they can be
  conditioned on.

---

## Forward test — RESTARTED 2026-08-19 on the session basis

Three models **pre-registered and frozen** in `config/models.yaml` before any live data.
All 48 grid configs in `docs/model_grid_results.md` as the pre-registration record.

| model | spec | Sharpe | ~/yr | hit | payoff | p |
|---|---|---|---|---|---|---|
| model_1_baseline | 5d, level, gauss σ1.5 | +0.21 | +5.4% | 51.1% | 0.93 | 0.0869 |
| model_2_horizon_trend | 10d, trend, gauss σ1.5 | +0.39 | +10.4% | 51.4% | 0.89 | 0.0190 |
| model_3_overfit | 20d, trend, gauss σ1.0 | +0.50 | +11.3% | 50.5% | 1.06 | 0.0390 |

*(In-sample figures on the PRE-migration basis — STALE. `model_grid.py` must be re-run.
The re-run is recorded **alongside** the original, never overwriting it: that file is the
pre-registration record for `model_3_overfit`, and the three frozen specs do not change
whatever the new grid says is best in-sample.)*

**Why the daily run matters even though the macro engine is finished being measured.**
Every backtest number above is in-sample in the honest sense: the specification was
chosen while looking at that history, across 48 configurations. The forward test is the
only evidence in the project that cannot be contaminated that way — specs frozen and
git-timestamped before the data existed. It also answers a question no re-run can:
`model_3_overfit` carries a pre-registered prediction that **its lead shrinks or inverts
live**. If it does, that demonstrates in-sample selection inflation with this project's
own evidence. And `forward_log` is the shared harness the event and rotation engines will
plug into — the window-integrity rule, frozen entry dates, session calendar and
honest-gaps policy are infrastructure, not macro-specific. **If the daily ritual becomes
a burden, automate it (cron). Do not stop it.**

### Wipe history
- **Wipe #1 (2026-08-17)** — first six rows computed from stale cache and empty bars.
  `download_data` called without `--force`; signal date taken as the last index row.
- **Wipe #2 (2026-08-18)** — deliberate, at 0 matured rows. The ledger held picks
  computed on the `bdate_range` basis while the scores parquet had moved to sessions;
  continuing would have mixed two bases in one ledger.

### Live rows (as of 2026-08-19)
Signal **2026-08-18** (45/47 coverage), entry **2026-08-19**, all three models in
**regime 1** — matching the classifier's current-regime output. 3 rows, 0 matured,
3 pending, 0 short_window. Entry sits on a session that has not closed yet, which is
correct: entry is prospective by design.

**Exposure note, recorded now so it is not reverse-engineered later.** Model 1 shorts
SPCX (43 days of history); model 2 shorts SPCX and FLY (256); all three go long DRAM
(92). The live models are actively trading **recent-inception tickers — the exact group
whose removal costs 40% of the long-history Sharpe.** This is pre-registered behaviour,
not a bug, but it means the forward test is heavily exposed to the question the
survivorship check just raised. If live results come in strong, the first follow-up must
be whether that is the newcomers again.

### Window integrity — IMPLEMENTED (commit 7352dd1), STILL UNEXERCISED

> A row is scored `matured` only if **every session** of its H-day window has a return
> for **every picked asset** (strict). Incomplete windows are marked `short_window` with
> their realised session count, excluded from the headline summary, and remain visible in
> the full log. **Entry dates and picks are frozen at log time and never reassigned.**

Pre-registered at 0 matured / 3 pending, implemented the same day. Fixed: horizons
counted index rows rather than sessions; `np.log1p(...).sum()` silently dropped missing
days via `skipna=True`; maturation could fire on windows extending past usable data;
`entry_date` was re-derived every run; `--dry-run` wrote to disk on skip days.

`short_window` rows stay eligible for upgrade to `matured` if a vendor backfills — the
window is a fixed set of sessions, so healing means those sessions gain data, not that
the window slides.

### 2026-08-17 vendor gap — CLOSED, and an earlier claim in this document corrected

Yahoo returned 08-17 with **Open/High/Low/Volume present and only Close/Adj Close NaN**,
all 47 assets — verified against the vendor directly, bypassing the cache. Ruled out as a
pipeline bug.

**This document previously stated it "has not self-healed across three `--force`
re-pulls in ~24 hours." It healed at roughly 48 hours** and 08-17 now shows 45/47 like
any other session. The claim was accurate when written and is now false. Correct
statement: **Yahoo can leave a Close missing for up to two days; the panel heals
retroactively via `--force`, but a forward-test entry for a skipped day stays skipped.**

The restart moved the entry to 08-18, so the incident never needed the `short_window`
rule. No permanent gap exists in the panel.

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

1. **Finish the cascade:** `model_grid` (record alongside, never overwrite) and
   `chain_rotation`.

2. **GDELT extension — forward first, then backward.** Decision after discussion
   2026-08-19:
   - **Extend 2024 → 2026 first.** Cheapest, feeds the live forward test, and it is the
     regime deployment would happen in. Event density is high (sustained political news
     flow).
   - **Then extend back toward the ~2015 tagged floor.** The forward window is
     essentially **one macro regime** (currently Regime 1: tight policy, strong USD).
     A positive drift result on that window alone cannot distinguish "drift exists" from
     "drift exists in high-attention tight-policy conditions", and there would be no
     other regime in-sample to check against. This project has already been bitten once
     by exactly that: the GDELT alignment was significant on 2018+ and null on 2006+.
     2015–16 China, 2018Q4, COVID and the 2022 rate shock supply the regime variety.
   - **Watch the control group.** If event density is very high, matched non-event days
     become scarce and the test loses power from the other direction.
   - If time forces forward-only, the write-up must state the result is **conditional on
     one regime**.

3. **Event engine Stage 1 — drift-existence test.** GDELT event days; returns at
   1/5/10/20d entered next-open; permutation-tested vs matched non-event days. Prior
   question to signal quality: does anything happen at all?

4. **Problem 2 Stage 2:** conditional lead-lag *within* event episodes. Blocks on (3).

5. **Ensemble combiner** (position-space, Sharpe-weighted). **This is the actual open
   question for the product** — the engines' correlation with each other has never been
   measured, and that measurement decides whether three modest signals make one good
   system.

6. **The n=4 generalization gap is a live concern.** +5.130 means the regime model
   transfers poorly to 2025–26 — the exact period the forward test runs in. **Test:**
   check which regimes 2025+ rows occupy and whether they sit in a low-density corner of
   the training distribution. If the live period is out-of-distribution for the fitted
   regimes, the analog engine's regime gate is selecting analogs from a state the present
   does not resemble.

7. **Doc/code accuracy fixes queued:**
   - `regime_classifier.py`'s console note still says n=4 stands on "seed stability,
     run-length persistence, and cluster separation" — two of those three are no longer
     true on this panel.
   - `regime_event_alignment_normalized.py` prints a VERDICT ("de-baselined signal
     APPEARS... firm up that n as the event-supported choice") that the permutation test
     in the next script directly contradicts. Written before the permutation existed.
   - `PIPELINE.md` §4 documents the four `regime_event_*` scripts without their
     **required `--gdelt` argument**; a reviewer following the doc hits an immediate
     error.
   - `PIPELINE.md` §1's reproduce-from-scratch chain has **no step producing
     `gdelt_2024_clean.csv`**. It came from a BigQuery pull plus manual cleanup that is
     neither scripted nor documented, so "reproduce everything" is currently false.

8. **Policy on documented figures.** Numbers drift as the panel grows. Decide: freeze
   with an as-of date, or re-run at fixed checkpoints.

9. **Data amendments:** company/entity-level events (earnings line-items, fireside chats,
   tech breakpoints like a DeepSeek-style release) — current mapping is macro-only.

10. **Problem 3:** LLM/RAG scenario layer (ChromaDB + SQLite + GitHub raw text).

11. **Streamlit MVP**, then integration/backtest phases.

### Closed 2026-08-18/19
- ~~Window integrity~~ → commit 7352dd1.
- ~~Pin the pipeline to n=4~~ → commit 5ec014e. Verified by grep beforehand that no
  script consumes `regime_labels.parquet`.
- ~~Port `safe_haven_robustness.py` to the data-driven stress axis~~ → a real correctness
  fix.
- ~~`analog_core._forward` counts index rows~~ → resolved by the calendar migration.
- ~~2026-08-17 vendor gap~~ → healed at ~48h; no permanent panel gap.

---

## Working principles (established, keep following)

- Every claim about project data must come from data actually run. Hypotheses must be
  labelled as hypotheses with the test proposed.
- Null results are findings; document them rather than softening.
- Permutation tests over raw p-values; check robustness across specifications.
- Judge signals by **risk-adjusted return**, never hit-rate alone.
- Few, principled hypotheses beat large grids — and if a grid is run, the winner is
  labelled a cherry-pick and forward-tested.
- Extend data by **removing redundancy, never by imputation** — including redundancy that
  enters through the *index* rather than through a fetcher.
- Identify axes by **economic meaning, never by index** — and when that hazard is fixed in
  one script, **grep for every other consumer in the same commit**.
- **Re-validate rather than assume** when the substrate changes — and **ask which results
  were actually exposed**. A result that survives may simply never have been at risk
  (Problem 1's `dropna`), which is not the same as robustness.
- **Correct the record** when new evidence weakens a prior claim — including corrections
  to this document's own earlier statements.
- **Verify before asserting in a commit message.**
- **State the prediction before running the check**, and **record priors that turn out
  wrong** — the n=5-fragility finding was an artifact, and only a stated prior made that
  visible.
- **Register falsification conditions before re-validating**, so the verdict cannot be
  reverse-engineered from the numbers.
- **Take the correct long-term fix over the contained one** when they conflict.
- **A measured engine is finished being measured.** Re-tuning until the number improves
  is the overfitting failure. What strengthens the system is engine *independence*, not a
  better version of a measured component.
- **Fail loud rather than log something plausible.**
- Operational rules affecting the forward test are **pre-registered while the affected
  rows are still pending**, never after outcomes are visible.
- The **repo is the source of truth**, not model memory.
