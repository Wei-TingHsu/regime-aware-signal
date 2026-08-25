# PRE-REGISTRATION — Problem 3, steps 3–6
## The analog-conditioned event effect, the precision blend, and the decision report

*Committed 2026-08-24, BEFORE any document beyond the 131 FOMC statements has
been read, BEFORE the `specificity` gate has been checked, and BEFORE any
conditional return estimate has been computed on real data.*

*Nothing about the corpus is known at the time of writing: not how many
documents survive the gate, not how they distribute across regimes, not how many
same-day collisions exist. Every threshold below is therefore fixed in genuine
ignorance of what would make it pass.*

*Implementation proceeds BLIND (§9) so that code can be built in parallel with
the corpus read without any real number being seen.*

---

## 1. WHAT IS BEING BUILT

Steps 3–6 of the design confirmed 2026-08-23:

> 3. Ask what this kind of news did to each asset **in the macro-similar past**,
>    weighted by similarity and recency.
> 4. If no macro-matched precedent exists, fall back to the unconditional effect,
>    labelled weaker.
> 5. Weigh competing sources landing the same day into a net view per asset.
> 6. Emit a decision report.

Steps 3 and 4 are **one estimator**, not two. §3 makes that precise.

### 1.1 The evidence this registration is built on

Two measured results from 2026-08-24 constrain everything below.

**`docs/rung_diagnostic_results.md`** — on the 5,191-session macro panel, both
engines returned **RESELECTION**: median top-k overlap 0.765 (Engine A) and 0.850
(Engine B) at HL=4y, against a registered 0.90 threshold. ESS held at ~99.6 of
100 at every rung on both engines. Neither kernel discriminates; the engine picks
the 100 most recent same-regime days and averages them with near-uniform weight.
**σ=1.5 and the ladder's λ are therefore known not to transfer to this step, and
are not inherited.**

**`docs/fine_lambda_sweep_results.md`** — Engine B long-history Sharpe runs
0.30 → 0.25 → 0.22 → 0.29 across λ steps of 1e-4. The surface is jagged.
Rung-to-rung differences in the registered ladder are the same order as this
jitter, so **no single-λ result on that engine is stable**, and step 3 must not
be built on the assumption that one is.

---

## 2. THE ESTIMAND

For a query day `t` carrying document `d`, for each asset `a` and horizon `h`:

> the return of asset `a` over `h` sessions following days in the past that
> (i) carried a document of the same **content class** as `d`, and
> (ii) were **macro-similar** to `t`,
> weighted by macro similarity and recency.

**Entry convention: close of the document's public date.** Fixed by
`spillover_test.py`'s instant-propagation finding — 5/7 peers on GAP, 0/7 INTRA,
0/7 NEXT. Any later entry measures an empty window.

**Document dates are public-release dates, never event dates.** FOMC minutes are
released ~3 weeks after the meeting; dating by meeting date would build
look-ahead into a filename.

### 2.1 Content class

Two documents are the same content class, for asset `a`, if
`sign(direction[asset_class(a)])` agrees and both are non-zero.

Hard filter, binary, no free parameter. Registered in preference to a continuous
schema distance because the latter adds a second free width parameter and admits
weak matches invisibly. The count of matching documents is reported on every
call.

`specificity` enters the class definition **only if the gate in
`EXECUTION_PLAN.md` passes** (spread between highest and lowest source mean
> 0.25). If the gate fails, `specificity` is excluded here and that exclusion is
reported.

### 2.2 Macro conditioning — all three PCs

Conditioning uses **PC1, PC2 and PC3 together**. No per-source axis selection.

An earlier proposal was to condition each source on economically-chosen axes
(FOMC → rate + stress, etc.) to raise effective density. **Rejected before any
data was seen**: the mapping could not be checked afterwards without trying
mappings until one worked, which is the search this project exists to avoid. The
thinness that results is absorbed by the blend (§3), not by a bet.

**No hard regime gate.** On the macro panel the regime gate operates on ~5,000
candidates; here the pool is 10²–10³ events, and a hard gate would empty most
cells. Regime match is computed and **reported as a flag**, never used to
exclude.

### 2.3 Weights

```
w_i = exp(−‖z_i − z_t‖² / 2σ_d²) · exp(−ln2 · age_years_i / HL_d)
```

`σ_d` and `HL_d` are **step 3's own parameters**, declared here, and are NOT
inherited from `models.yaml` or `config.yaml`. The frozen live models are
untouched by anything in this document.

- **`HL_d` = 4 years.** Same economic ground as the ladder's primary rung (US
  presidential term). Single value, no ladder, no sweep — the fine λ sweep showed
  the Sharpe surface in λ is jagged, so a document-pool λ ladder would report
  noise.
- **`σ_d` by the registered procedure in §4.**

---

## 3. THE BLEND — steps 3 and 4 as one estimator

### 3.1 Form

```
ŷ = w · ŷ_conditional + (1 − w) · ŷ_unconditional
w = ESS / (ESS + k)
```

`ŷ_conditional` is the macro- and recency-weighted mean over same-content-class
past events. `ŷ_unconditional` is the plain mean over the same events with macro
and recency weights removed. **Step 4 is the `w = 0` limit of step 3**, which is
why it is not a separate module.

`ESS = (Σw)² / Σw²` over the matched events.

### 3.2 k is ESTIMATED, never chosen

k is the ratio of noise within a macro cell to real variation between cells:

```
k = σ²_within / τ²
```

Both are measurable, so **k has no registered value and no grid**. Choosing k by
trying values and taking the flattest point would be a one-parameter grid search
— the move `model_3_overfit` exists to demonstrate the cost of.

**Estimator: DerSimonian–Laird method of moments**, with macro cells given by the
regime labels (C = `regime.n_regimes` = 4, read from config, not hard-coded):

```
v_c   = σ²_within / n_c                    per-cell variance
W_c   = 1 / v_c
ȳ_F   = Σ W_c ȳ_c / Σ W_c                  fixed-effect mean
Q     = Σ W_c (ȳ_c − ȳ_F)²                 heterogeneity statistic
τ²    = max(0, (Q − (C−1)) / (Σ W_c − Σ W_c² / Σ W_c))
```

`σ²_within` is the pooled within-cell variance of individual event returns.

### 3.3 The τ² = 0 case, registered in advance

If `Q ≤ C − 1`, observed differences between macro cells are fully explained by
noise. Then **τ² = 0 → k = ∞ → w = 0**, the estimator returns the unconditional
mean, and:

> **this is registered as a NULL for that asset/horizon: macro conditioning adds
> nothing.** It is reported as a null. It is NOT a reason to try a different
> estimator, a different cell definition, or a different k.

### 3.4 Estimated inside each fold

k, τ² and σ²_within are re-estimated **within every leave-one-out fold**,
excluding the held-out event. Estimating once on the full sample would let a
held-out event inform its own shrinkage.

### 3.5 Abstention floor

`ESS < 8` → **no conditional claim is issued.** Tier 3 only (§6.2), with the
realised ESS shown. Below that count the conditional estimate is noise wearing a
precedent's clothes, and the blend alone would not make that visible enough.

---

## 4. σ_d — REGISTERED SELECTION PROCEDURE

σ_d is not a stated constant, because the right width depends on pool size, which
is unknown at registration. It is fixed by a procedure whose every element is
registered here.

```
target_ESS = clip(0.15 · n_pool, 8, 30)
```

σ_d is found by **bisection on σ ∈ [0.05, 5.0]** so that the *median ESS across
query days* equals `target_ESS`, tolerance 0.5, maximum 40 iterations.

- **Selection uses no returns.** ESS is a property of the weights alone, so σ_d
  cannot be tuned toward an outcome.
- Selected **once per content class per source**, on the training portion of each
  LOO fold.
- If bisection fails to converge, σ_d is set to the bound and **the failure is
  reported**, not silently accepted.
- Realised ESS is printed on **every** call and appears in every report.

### 4.1 The transfer check

The rung diagnostic (overlap vs a no-decay control, weighted mean analog age,
median ESS) is **re-run on the document pool** at the selected σ_d.

> **REGISTERED:** if median top-k overlap against the no-decay control is
> **< 0.90** on the document pool, then λ is reselecting here too, and the report
> must state that step 3 conditions on *recent same-class events* rather than on
> *macro-similar events* — the same correction forced on step 1.

---

## 5. THE REGISTERED TEST — pooled leave-one-out

### 5.1 Why not per-cell significance

Power arithmetic, done before any run. GLD 3-session volatility ≈ 1.6%. A cell at
ESS 20 has standard error ≈ 1.6/√20 ≈ **0.36%**. It cannot resolve a −0.3%
effect. **Per-cell p-values are therefore not computed and no per-cell claim is
permitted.** Cell estimates ship as estimates with intervals.

Pooled over 131 FOMC events, se ≈ 1.6/√131 ≈ **0.14%** — powered for effects at
the FOMC→GLD scale. Over the full corpus, comfortably so.

### 5.2 The criterion

For every event, predict using all *other* events, twice: once blended, once
unconditional. Pooled across all events:

> **The conditioned estimator must beat the unconditional estimator on BOTH
> lower MSE AND higher sign hit-rate, at p < 0.05 against the null in §5.3.**
>
> One of two is **not** a pass. Reported as inconclusive.

### 5.3 Null

Shuffle the macro-similarity weights across events, preserving group sizes and
every return path, destroying only the correspondence between macro state and
outcome. 10,000 draws. `conditional_order.py` already implements exactly this and
transfers directly.

### 5.4 Reported regardless of outcome

Every asset, every horizon, both metrics, realised ESS distribution, τ² and k
distributions, the count of cells hitting τ² = 0, and the count abstaining under
§3.5.

---

## 6. THE AGREEMENT FLAG, AND DIVERGENCE

### 6.1 Displayed, never weighted

The LLM's `direction` for an asset and the sign of the blended historical
estimate are compared and reported as **corroborated** or **divergent**.

> **REGISTERED: the flag never enters the estimate.** Feeding it back would be
> circular — the reader's opinion would be validating itself. It is display only.

Kept as display, it accumulates into a calibration record on the reader, which is
a deliverable in its own right.

### 6.2 On divergence: show both, flag, combine nothing

> **REGISTERED:** where the LLM reading and the historical estimate disagree in
> sign, the report shows **both numbers, side by side, with the divergence
> flagged, and issues no combined number for that asset.**

Considered and rejected: silently preferring the historical estimate (hides the
disagreement); and dropping the asset a tier (conflates disagreement with
thinness, which the tier field already measures). A system that surfaces the
conflict is more useful to a fiduciary than one that resolves it invisibly.

### 6.3 Tiers

| tier | condition | label |
|---|---|---|
| 1 | `w ≥ 0.6` and `ESS ≥ 8` | matched precedent |
| 2 | `0.2 ≤ w < 0.6` and `ESS ≥ 8` | partial precedent — precedent strength shown |
| 3 | `w < 0.2` or `ESS < 8` or `τ² = 0` | unconditional — weaker evidence |

`w` is reported as a number on every asset, not only as a tier.

---

## 7. STEP 5 — WEIGHING COMPETING SOURCES

### 7.1 Collision count first

The number of days carrying documents from **two or more different sources** is
counted and reported **before** any weighting rule runs.

> **REGISTERED:** if fewer than 50 such days exist, the fixed rule in §7.2 is
> used and the estimated alternative in §7.3 is not attempted. The count is
> reported either way.

### 7.2 Fixed rule

```
weight_d          = magnitude · specificity · novelty · confidence
net_direction[a]  = Σ(weight_d · direction_d[a]) / Σ(weight_d)
```

Straight product, so any near-zero field vetoes the document — the intended
behaviour for a low-specificity threat-to-act. **`specificity²` is NOT used**;
squaring is an unregistered strength parameter and it is not introduced.

If the §4 gate failed, `specificity` is dropped from this product and the
substitution is reported.

### 7.3 Estimated alternative — only above 50 collisions

Estimate from history which source dominated when sources disagreed. Requires its
own registration before running; it is **not** authorised by this document.

---

## 8. STEP 6 — THE DECISION REPORT

One Markdown file per day at `outputs/reports/YYYYMMDD.md` plus identical JSON,
**both emitted from one function** so they cannot diverge.

Every report contains:

1. macro state, regime, and **posterior confidence** — below 60% is printed as a
   warning, not a footnote;
2. every document read that day: source, direction, magnitude, specificity,
   novelty, confidence, evidence quotes;
3. per asset: the blended estimate, **realised ESS**, **precedent strength `w`**,
   matched-event count, and tier;
4. the **agreement flag**; on divergence, both numbers and no combined figure;
5. the net view per asset with the dominant source named;
6. **what the system cannot see** — the coverage gaps in `CURRENT_STATE` §8,
   printed in every report, not linked;
7. **no performance number that has not matured.**

---

## 9. BLIND BUILD PROTOCOL

Steps 3–6 are implemented and debugged **without any real conditional estimate
being computed.**

### 9.1 What is real in the blind harness

Real macro PCs, real regime labels, real document dates and schemas, real return
series with their real volatility, fat tails, cross-asset correlation, missing
values and NYSE holidays. **The only thing destroyed is the correspondence
between event dates and returns** — permuted — with a known effect planted on
top.

Debugging therefore happens against data carrying every awkward property the real
data has. Synthetic returns are **not** used; clean data would let real bugs
survive to unblinding.

### 9.2 Acceptance tests before unblinding

1. **Recovery** — a planted effect of known size is recovered within its interval.
2. **Precedent count** — reported matched-event counts equal the planted counts.
3. **Tier labelling** — planting ESS above and below each boundary produces the
   correct tier.
4. **Abstention** — planting fewer than 8 matched events triggers §3.5.
5. **Null calibration** — with no effect planted, the §5.3 null returns p
   approximately uniform; rejection rate at α=0.05 is within [0.02, 0.08] over
   200 replications.
6. **τ² = 0 path** — planting identical cell means drives w → 0 and the null
   label of §3.3.

> **REGISTERED: no real conditional estimate is computed until all six pass and
> this document is committed.**

---

## 10. WHAT WOULD MAKE THIS FAIL, STATED IN ADVANCE

- **§4.1 comes back < 0.90** → step 3 conditions on recency, not macro
  similarity. Reported as that, not as macro conditioning.
- **τ² = 0 across most cells** → macro conditioning adds nothing measurable.
  Reported as a null; the report still ships, with every asset at Tier 3.
- **§5.2 fails on one metric** → inconclusive, not a partial success.
- **Gate fails** → `specificity` drops out of §2.1 and §7.2, and both
  substitutions are reported.
- **Collisions < 50** → §7.3 is not attempted and step 5 ships on the fixed rule.

**None of these stops the product shipping.** The decision report's value is
graded evidence with declared precision and an abstention rule — an instrument,
not a signal. A null in §5 makes the tiers honest context rather than validated
signal; it does not make them useless, and it is the calibration record the
negative-results moat argument already rests on.

---

## 11. AMENDMENTS

*Five amendments, all made during 2026-08-24/25. Each records WHEN it was decided
relative to what had been seen, because that is the only thing distinguishing an
amendment from a rationalisation.*

| date | change | reason |
|---|---|---|
| 2026-08-24 | §3.2 gains two scale-relative numerical guards: `DEGENERATE_VAR = 1e-9` and `TAU2_REL_FLOOR = 1e-6`, and the registered `Q ≤ C−1 → τ²=0` rule is applied **before** the division rather than after. | Blind test 6 caught the registered null path **silently failing to fire**. `np.var` of 80 identical float64 values returns 4.76e-38, so `W = 4.2e38`, which amplified float noise into `Q ≈ 4.2 > 3` and produced `τ² = 2e-38 > 0` — a **Tier-1 label with w = 0.96 on data with no between-cell variation at all**. The guards make the registered rule fire; they do not change it. Written before any real estimate. |
| 2026-08-25 | `political` split by Federal Register document type into `political_order` and `political_other`. Gate criterion changes from a **point** spread > 0.25 to the **lower bound of a 95% bootstrap CI** > 0.25; pilot raised to n=60 per source. | **Both decided AFTER seeing a marginal point spread of 0.26 on n=20 — declared, not hidden.** The split uses the **government's own type tag**, an external taxonomy, and reassigns no document by judgement. The criterion change is a **tightening**: at n=20 the spread carried se ≈ 0.063, so 0.26 was indistinguishable from failing. Gate subsequently PASSED at 0.363, CI [0.279, 0.453]. |
| 2026-08-25 | §5.3's null gains a second implementation. **`permute_y`** becomes PRIMARY; **`permute_Z`** is retained and reported permanently. Registered in advance: a rejection rate below 0.02 means the null is conservative, and a step 3 null must then be reported as *"inconclusive at this power"*, never as *"macro conditioning has no effect"*. | `permute_Z` changes the ESS distribution — macro states are autocorrelated, so permuting Z breaks the alignment between similarity and recency and its draws are **not exchangeable** with the observed fit. `permute_y` destroys the state↔outcome correspondence and nothing else, which is what §5.3 registered **in words**. **THIRD change to test 5 after a failure — declared.** Both nulls reported every run; disagreement is a finding with **no tie-break**. Final: permute_y 0.066 (in band), permute_Z 0.000 (out). |
| 2026-08-25 | §2.2's conditioning switches to the **LIVE BASIS**: expanding-window standardisation and expanding-window regime labels, canonically ordered by ascending mean PC1. | Step 3 is a **live daily product**; a deployed system has no future data, so the full-panel basis is something it **cannot do**, and a backtest that cannot be run live is not a backtest of the product. **Not** justified by effect size — `scaling_check` measured the level basis at +0.012, p 0.94. **FIRST amendment changing the estimator rather than the reporting.** No real estimate had been computed. Also closes PROJECT_STATE thread 3. |
| 2026-08-25 | Documents longer than `--max-words` are **truncated and read** rather than skipped. Each read records `truncated`, `orig_words` and `max_words`, carried into the CSV. | Skipping dropped **189 of 834** earnings documents (23%), all 6-K complete submissions where the whole filing is one file because foreign issuers file no separate EX-99. Costed at Sonnet 5 rates: skip = free with a 23% gap; raise the cap = **$17.77** for those 189 alone; truncate = **~$7.60** with no gap. An earnings release's figures sit near the top; the tail is exhibits. **This changes the model's input**, so any specificity or direction difference between truncated and whole documents is a property of the pipeline, not the source — which is why `truncated` is recorded per document rather than assumed away. |

### 11.1 Effect of the live-basis switch, recorded

| | full-panel basis | live basis |
|---|---|---|
| test 1 kernel attenuation | 86.2% | 90.3% |
| τ²=0 degenerate fraction | 42.5% | 32.0% (200 reps) |
| "no planted structure" tiers 1/2/3 | 0/8/392 | 0/260/140 |
| `permute_y` rejection | 0.043 | 0.066 |

**The estimator conditions more often on the live basis.** `permute_y` stays
inside the registered band, so this is recorded as a property of the basis, not a
defect — and it is the first thing to re-check if any real step-3 result looks
strong.

