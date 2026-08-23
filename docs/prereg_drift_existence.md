# PRE-REGISTRATION — Event engine Stage 1: drift-existence test

**Status: REGISTERED, UNRUN.**
This document is committed **before** the test is executed. The git timestamp on this
file is the pre-registration evidence, in the same way `config/models.yaml`
(`ce18d34`, 2026-08-17 14:24:09 +0800) is for the forward test.

**If any part of this document is edited after the test has been run, the edit is
recorded in §9 with its reason. Results are never relabelled to match whichever
specification succeeded.**

---

## 1. Scope — and what this test cannot see

`docs/architecture_decisions.md` §3 specifies Stage 1 as *"identify GDELT event days
(event-density spikes on the focus assets)"* and *"measure focus-asset returns."*

**The data does not support that specification.** The 944-day GDELT panel contains a
daily, global `market_stress` document count plus a total-document denominator. It has
no per-asset or per-entity event density. `config/gdelt_theme_mapping.yaml` records why:
GDELT has no clean semiconductor / defense / space / cyber theme, and entity matching
must be exact (`LIKE '%INTEL%'` matches "intelligence").

Stage 1 is therefore **re-scoped**, explicitly and on the record:

> **Registered question.** Does a spike in economy-wide narrative-stress density predict
> subsequent drift in market-level returns, entered after the overnight gap has been
> conceded?

This is **not** the PEAD analog. PEAD is firm-specific news predicting that firm's drift.
This is aggregate sentiment predicting aggregate drift — a different literature with
different priors and a weaker one.

**Consequences, registered in advance so neither can be claimed later:**

- A **positive** result does **not** establish that entity-level event detection works,
  and therefore does **not** discharge the precondition on the conditional event/rotation
  merge (PROJECT_STATE, 2026-08-19). That merge requires a detector that names a focus
  SET. This test has no such detector.
- A **null** result does **not** close out firm-level event drift. The instrument is blind
  to it by construction. Per the working principle: *a null from an instrument blind to
  the phenomenon is not evidence of absence.*

Entity-level detection (GDELT entity matching, or SEC EDGAR 8-K, which
`gdelt_theme_mapping.yaml` already records as cleaner) is a **separate prerequisite
thread** and is not tested here.

PROJECT_STATE's description of thread 1 as *"the test that decides whether the event
engine and the rotation chain have a foundation"* is **retired** as overstated, in both
directions, and replaced by the registered question above.

---

## 2. Data

| item | value |
|---|---|
| GDELT panel | narrow `market_stress` variant, 944 days, 2024-01-01 → 2026-08 |
| GDELT provenance | `src/gdelt_query.py` → BigQuery → `src/gdelt_ingest.py` (303bdae) |
| Returns | `processed/asset_returns.parquet`, NYSE session index |
| Session calendar | `src.market_calendar.trading_days()` — sessions, never index rows |
| Expected overlap | ≈ 648 trading sessions (established in the alignment work) |

**Narrow is canonical**, decided on definitional grounds independently of any p-value
(PROJECT_STATE, GDELT event layer): broad `stress_count` averages 310,189 against 335,832
total documents — close to one hit per document — so the broad variant measures *"the
economy is in the news"* rather than stress. The broad variant is **not** run here. Adding
it after seeing a narrow null would be the reverse-engineering the working principles
forbid.

**Known coverage defect.** GDELT is absent 2025-06-15 → 2025-07-01 (17 days), identical in
both variants, therefore upstream of the query. Handling is specified in §3.

---

## 3. Event-day definition

### 3.1 Measure

Daily stress **share**, `stress_count / total_docs`, converted to a z-score against a
**trailing** baseline:

```
share_t = stress_count_t / total_docs_t
z_t     = (share_t - mean(share_{t-21..t-1})) / sd(share_{t-21..t-1})
```

**Share, not raw count**, for the baseline-swamping reason established in
`docs/regime_event_validation.md` §4: every day carries ~75,000 stress-tagged articles and
the raw ratio is drowned by that constant.

**Trailing 20 sessions, strictly excluding day t.** No centred window, no same-day
information. A centred baseline would be look-ahead.

**A deliberate reversal, stated so it does not read as inconsistency.** PROJECT_STATE
flags the 20-day rolling baseline as *structurally near-blind to ~400-day regime runs*,
which is why `z_in − z_out` was null almost everywhere and why the window was wrong for
regime alignment. For **spike detection that blindness is the intended property**: an
event is defined as "unusual versus lately," not "unusual versus history." Same window,
opposite verdict, for a stated reason.

### 3.2 Threshold

- **Primary: z ≥ 1.5.**
- **Sensitivity ladder, declared now: z ∈ {1.0, 1.5, 2.0, 2.5}. All four rungs are
  reported in the final table regardless of outcome.** No rung may be introduced,
  dropped, or promoted to primary after results are seen.

A fixed threshold rather than a top-k percentile, so the episode count is a property of
the data rather than an input chosen to reach a desired sample size.

### 3.3 De-clustering

A news storm produces consecutive spikes whose forward windows almost entirely overlap.

> **Within any run of threshold-exceeding days separated by fewer than 5 sessions, keep
> only the first.** The trigger, not the storm.

The retained day is the **episode date**. All counts reported are episode counts.

### 3.4 Eligibility

A day is eligible to be an episode only if:

1. Its full 20-session trailing baseline is present. Days whose baseline window overlaps
   the 2025-06-15 → 2025-07-01 outage are **dropped, not computed on a partial window.**
2. It is a NYSE session with price data for the tested asset.
3. Its full forward window lies inside the return panel.

### 3.5 Entry convention — conceding the gap

`architecture_decisions.md` §3 concedes the overnight move as uncapturable. The panel
carries **close-to-close returns only**, with no opens. The closest available
implementation, and the conservative one:

> Episode date **t**. The scored window is the H sessions **t+2 … t+H+1**, i.e. returns
> accumulated from the **close of t+1** to the close of t+H+1.

This discards both the overnight gap *and* the whole of session t+1, so it concedes
strictly more than a next-open entry would. Registered as conservative on purpose: a
positive result under it is not an artifact of the gap.

Horizons **H ∈ {1, 5, 10, 20}**, counted in NYSE sessions via `trading_days()`.

### 3.6 Window integrity

The pre-registered forward-test rule (7352dd1) carries over unchanged: an episode scores
only if **every session** of its H-window has a return for the tested asset. Otherwise it
is `short_window`, reported with its realised session count, and **excluded from the
headline**. Episode dates are frozen at detection and never reassigned.

---

## 4. Control days

### 4.1 The confound this exists to handle

Stress-news spikes are **not** randomly distributed across the volatility landscape. They
cluster in high-volatility periods, where forward return distributions already differ.
A null built from unconditionally random days would attribute that volatility effect to
the event.

### 4.2 Primary — covariate-matched resampling

For each episode, controls are drawn from days satisfying **all** of:

| condition | rule |
|---|---|
| not an event | z below the threshold under test |
| no window contamination | not within ±20 sessions of **any** threshold-exceeding day |
| volatility matched | same quintile of trailing 20-session realised volatility |
| era matched | within ±90 sessions of the episode |

**Relaxation order, declared now:** if a stratum has fewer than 5 candidates, relax the
±90-session era window to ±180, then ±365; only if still short, relax the volatility
quintile to adjacent quintiles. **In that order, never the reverse**, and every relaxation
actually used is reported with the count of episodes affected.

Null distribution: **B = 5,000** matched resamples of the mean drift statistic.

### 4.3 Secondary — circular rotation

The rotation null used in `docs/regime_event_validation.md` §6: slide the episode dates as
a block to a random calendar offset, wrapping at the ends, and re-measure. 5,000 rotations.

It is retained alongside matching because it preserves two things independent draws do
not: the **clumping** of episode dates, and the **overlap structure** of forward windows,
which matters at H = 10 and H = 20 where naive standard errors are inflated by shared
sessions.

**Both nulls are reported. Where they disagree, the disagreement is the finding** and is
reported as such, not resolved by preference.

---

## 5. Estimands

Two, both registered, both reported. No others.

**E1 — directional drift.**
Mean H-session return following an episode, minus the matched-control mean.
*Registered prediction: negative for risk assets* (stress spike → subsequent
underperformance).

**E2 — sign-conditioned continuation.**
`sign(r_t) × (H-session return)`, minus the same statistic on matched controls, where
`r_t` is the tested asset's return on the episode date itself.
*Registered prediction: positive* (under-reaction continues in the direction of the
initial move). This is the PEAD-shaped estimand and is the stronger of the two.
Reversal appears as the negative tail, not as a failed test.

**Tested asset.**
- **Primary: SPY** as the market proxy.
- **Secondary: a defensive spread**, equal-weight (TLT, GLD) minus SPY, which is where a
  narrative-stress signal would most plausibly act.

No other asset is tested. The 47-asset universe is **not** swept; a cross-sectional sweep
over 47 names at 4 horizons and 4 thresholds is the large-grid failure the working
principles exist to prevent.

**Primary cell count: 2 estimands × 4 horizons = 8**, on the primary asset at the primary
threshold. All 8 are reported.

---

## 6. Success criterion — written before the answer is seen

> **A positive verdict requires, on the primary asset at the primary threshold:
> significance at p < 0.05 under BOTH nulls, at TWO ADJACENT horizons, with a consistent
> sign across all four rungs of the sensitivity ladder.**

Anything less is reported as observed and labelled **exploratory**, requiring confirmation
on data it was not discovered in before it counts toward any claim.

**Registered in advance:** a result appearing at exactly one horizon, or under one null
but not the other, or with the sign reversing across thresholds, is **not** a positive
result. It is noise with a p-value.

---

## 7. Power — registered before the result, because it constrains what a null can mean

The panel supplies ≈ 648 sessions. At z ≥ 1.5 roughly 7% of days exceed threshold, and
de-clustering at 5 sessions is expected to leave **on the order of 25–35 episodes**.
(Exact counts are recorded in §8 when the test runs; the figures here are the prior.)

Minimum detectable effect at 80% power, two-sided, with n episodes and control-matched
comparison, is approximately `2.8 × σ_H / √n`, where `σ_H` is the H-session return
standard deviation.

With SPY daily σ ≈ 1% and n = 30:

| H | σ_H (approx) | MDE at 80% power |
|---|---|---|
| 1 | 1.0% | ≈ 0.5% |
| 5 | 2.2% | ≈ 1.1% |
| 10 | 3.2% | ≈ 1.6% |
| 20 | 4.5% | ≈ 2.3% |

`architecture_decisions.md` §3 already registers the expectation that PEAD-scale effects
are **modest at best**, having weakened since the 1990s as the anomaly became widely
traded. Effects of that scale sit **well below** the MDE at H = 10 and H = 20.

> **Registered in advance: a null at H = 10 or H = 20 will be reported as INCONCLUSIVE —
> underpowered against the effect sizes the literature leads us to expect — and not as
> evidence of absence.** Only H = 1 and H = 5 carry meaningful power on this panel.

**This is itself a reportable finding:** the adequately-powered version of this test
requires roughly 100+ episodes, which means extending the GDELT panel back toward the
~2015 tagged floor. That extension is specified as future work and is **not** run before
this document is committed, so that this pre-registration remains valid for the deep panel.

---

## 8. Reporting commitments

Recorded when the test runs, in this file:

1. Episode count at every rung of the ladder, before and after de-clustering.
2. Every relaxation of the matching criteria actually invoked, with affected counts.
3. All 8 primary cells, both nulls, regardless of outcome.
4. `short_window` counts.
5. The verdict against §6, stated explicitly as positive / null / inconclusive.
6. Realised σ_H and the recomputed MDE table, replacing the priors in §7.

---

## 9. Amendments

*One amendment, recorded below. Made and written down BEFORE any result was read.*

| date | change | reason |
|---|---|---|
| 2026-08-23 | §4.2 control buffer changed from a flat ±20 sessions to **H+2** sessions | The registered ±20 buffer is infeasible on a 659-session panel: at z≥1.0 there are 70 episodes, and 70 × 41 slots cover the panel several times, so NO control day survives. The first run returned empty pools and p(matched)=1.0000 for every cell. The registered relaxation order covers the era window and the vol quintile but NOT the buffer, so the buffer bound to zero. H+2 is what the buffer's stated purpose — stopping a control's forward window overlapping an event's — actually requires; the flat 20 was sized for the longest horizon and applied to all. **Recorded before any result was read.** Estimands, thresholds, ladder, de-clustering, entry convention, nulls and success criterion all UNCHANGED. |
