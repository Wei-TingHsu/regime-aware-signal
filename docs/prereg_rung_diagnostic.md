# PRE-REGISTRATION — rung-level selection diagnostic, and the Engine B
# no-decay vs incumbent spread test

*Written 2026-08-24, AFTER the recency ladder was run and its Sharpes were read,
BEFORE either measurement below was computed. That ordering is stated plainly
because it is weaker than the ladder's own registration and a reader is entitled
to know which is which.*

*What was already seen: the full ladder for both engines (`docs/recency_sweep_results.md`,
`processed/recency_sweep.json`). What has NOT been seen: any of the quantities
registered here, at any rung, for either engine — with one exception recorded in
§2.3.*

---

## 1. WHY THESE TWO MEASUREMENTS

The ladder returned **opposite verdicts on the same day, same panel, same
criterion**:

| long-history Sharpe | ∞ (control) | 16y | 8y | **4y (primary)** | 2y |
|---|---|---|---|---|---|
| Engine A `analog_core` | 0.2526 | 0.2338 | 0.2495 | **0.3205** | 0.4194 |
| Engine B `analog_backtest` | **0.3800** | 0.2400 | 0.2900 | **0.3200** | 0.3000 |

Engine A: POSITIVE. Engine B: NULL, and its best rung is no-decay.

The engines differ in three things: feature basis (z-scored vs raw PCs), GMM
refit policy (frozen vs expanding every 20 sessions), and their decay default.
A result that flips on those is **basis-carried, not phenomenon-carried** — the
pattern already recorded across the first three entries of the wrong-prior tally.

**Neither verdict is reportable as a finding about recency until we know what λ
is actually doing to analog selection.** These two measurements decide that.

---

## 2. MEASUREMENT A — rung-level selection diagnostic

### 2.1 What is computed

For every rung HL ∈ {2, 4, 8, 16, ∞}, on each engine, at every rebalance:

1. **weighted mean analog age** — `Σ(w · age_years) / Σw` after top-k selection
   and normalisation.
2. **ESS** — `(Σw)² / Σw²` on the normalised top-k weights. Range 1 to topk=100.
3. **top-k overlap vs the ∞ control** — `|S_HL ∩ S_∞| / topk`, where S is the set
   of selected analog indices at that rebalance.

Reported as the **median across rebalances**, plus the 10th and 90th percentiles.

**No forward return enters any of these.** They are properties of the weighting
and selection alone, so they cannot be tuned against an outcome.

### 2.2 The registered question and its threshold

The 2026-08-18 locked design describes the recency term as *"gentle recency decay
breaks ties among them"* — i.e. λ is supposed to reorder analogs that similarity
has already selected, leaving the SET largely intact.

> **REGISTERED THRESHOLD, written before any rung was measured:**
>
> **Tie-breaking** if median top-k overlap vs the ∞ control is **≥ 0.90** at the
> primary rung (HL=4y).
>
> **Reselection** if it is **< 0.90**. In that case λ is choosing WHICH analogs
> enter the average, not merely how they are weighted, and the engine is
> operating as a recency filter with a regime gate rather than as the
> similarity-dominant analog engine the design claims.

Secondary, reported but not criterial: if weighted mean analog age at HL=2y is
**less than half** the ∞ control's, recency dominates the selection outright.

### 2.3 WHAT IS ALREADY KNOWN — declared so this is not presented as novel

`docs/prereg_recency_kernel.md` §4 already reports, for **Engine A at HL=4y
only**: top-k overlap **0.80**, weighted mean analog age 0.24y vs 0.40y no-decay,
median ESS 99.9 vs 100.0.

**0.80 is below the 0.90 threshold registered above.** The threshold is therefore
registered in the knowledge that the one cell already measured fails it. That is
declared rather than hidden. What remains genuinely unmeasured: **every other
rung on Engine A, and every rung on Engine B** — and Engine B is the engine whose
verdict is NULL, so its numbers are the ones that discriminate between the two.

### 2.4 What the outcomes mean, stated in advance

- **Overlap high on both engines** → λ is tie-breaking as designed. The
  A/B disagreement must then be explained by feature basis or refit policy, and
  the ladder result stands as basis-sensitive but mechanically as intended.
- **Overlap low on both engines** → λ is reselecting on both. Neither ladder
  measures "does gentle recency decay improve analog quality"; both measure
  "does restricting to recent history improve returns". **The report must say
  the latter.** Engine A's POSITIVE is then a recency-filter result, not an
  analog result.
- **Overlap low on one engine only** → the disagreement is located, and the
  engine where λ reselects is the one whose ladder is uninterpretable.

### 2.5 Reported regardless

All five rungs, both engines, all three quantities, both universes where
applicable. No rung omitted for any reason.

---

## 3. MEASUREMENT B — is Engine B's 0.38 different from its 0.25?

### 3.1 The claim under test

Engine B long-history: **∞ (no decay) 0.3800** vs **incumbent λ=0.0008
(HL 3.438y) 0.2500**. Removing an unregistered hyperparameter with no recorded
provenance appears to raise Sharpe by half. That claim will be challenged and
currently rests on two numbers with no test between them.

### 3.2 Test

**Paired permutation on the per-rebalance spread series.** The two runs share
rebalance dates, so the series are paired. Statistic: the difference in mean
spread. Null: sign-flip the per-rebalance difference 10,000 times.

> **REGISTERED CRITERION:** the difference is called real at **p < 0.05
> two-sided**. Above that it is reported as *"not distinguishable at this sample
> size"*, NOT as evidence they are equal.

### 3.3 The interior-dip check, registered as a separate question

The incumbent's HL of 3.438y lies **between** the 4y and 2y rungs, whose
long-history Sharpes are 0.3200 and 0.3000. It scores **0.2500** — below both
neighbours. Sharpe is deterministic given λ, so a smooth parameter cannot produce
an interior dip; discrete `topk=100` membership changes can.

> **REGISTERED:** if measurement A shows top-k overlap changing sharply between
> HL=2y and HL=4y on Engine B, the dip is attributed to selection discreteness.
> If overlap is flat across that interval, the dip is **unexplained** and must be
> reported as such rather than rationalised after the fact.

### 3.4 Power

Engine B has 836 rebalances. This is the largest paired sample anywhere in the
project. No MDE concern is raised; if this test is underpowered, nothing in the
project is powered.

---

## 4. AMENDMENT TO `prereg_recency_kernel.md` §6, RECORDED HERE

§6's criterion requires improvement *"monotone or stable across at least three
adjacent rungs"*. **"Stable" was never given a numeric definition.**
`recency_sweep.verdict()` supplied an unregistered ±0.02 tolerance, and the count
it prints depends on that undeclared parameter:

| tolerance | Engine A adjacent-rung count |
|---|---|
| 0.02 (as coded, unregistered) | 5 |
| strictly monotone, no tolerance | **4** (16y → 8y → 4y → 2y) |

The verdict is POSITIVE under both, since both exceed three. But the printed
figure of 5 requires a tolerance ≥ 0.0188 that appears in no registration.

> **REGISTERED CORRECTION:** the reported count is the **strictly monotone** run,
> with no tolerance. Engine A's is **4**. Any tolerance-based count is reported
> separately and labelled as such.

*(Recorded here rather than silently: an earlier reading in conversation gave
this count as 3, which was also wrong. Both the code's 5 and that 3 are
superseded by 4.)*

---

## 5. AMENDMENTS

| date | change | reason |
|---|---|---|
| | | |
