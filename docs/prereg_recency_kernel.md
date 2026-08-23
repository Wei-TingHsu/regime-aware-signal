# PRE-REGISTRATION — Recency kernel (λ) in the macro analog engine

**Status: REGISTERED, UNRUN.** Committed before any backtest is run with decay
enabled. Git timestamp is the evidence.

---

## 1. What this restores

The 2026-08-18 design session locked a two-axis analog weight:

```
w_t = exp(-λ(T-t)) · exp(-‖z_t - z_now‖² / 2σ²)
      \___________/   \__________________________/
      recency kernel        similarity kernel
```

described as *"similarity-dominant (tight σ so only true analogs get weight;
gentle recency decay breaks ties among them) — an explicit, documented choice."*

`analog_core._kw()` implemented only the similarity half. No λ existed anywhere
in the codebase. The gap was found 2026-08-23, five days after the design was
locked, and only because it was asked about directly.

## 2. Functional form: EXPONENTIAL

`recency = exp(-ln2 · age_years / HL)`, with age measured in years (sessions/252).

Chosen over the alternatives on structural grounds, decided from
`recency_diagnostic.py` **before any return was computed**:

| form | weight retained at 4× the half-life |
|---|---|
| **exponential** | **6%** |
| power law | 30% |
| half-Gaussian | ~0% |

Exponential is the only form that retains a small-but-nonzero tail on distant
history. Power law keeps too much (a 30% weight on 16-year-old analogs is not a
"tie-break"); half-Gaussian truncates entirely, discarding crisis precedents that
may be the only relevant ones.

It is also memoryless — the weight ratio between a 2y and 3y analog equals that
between a 12y and 13y one. **Recorded as an assumption, not a claim.** It sits in
mild tension with the economic reasoning below, which implies relevance drops at
discrete policy transitions rather than smoothly. A step or regime-boundary form
is the natural alternative and is NOT tested here.

## 3. Half-life: 4 YEARS primary

**Economic reasoning (Steven's, recorded verbatim in intent):** a US presidential
term is four years, and policy — fiscal, regulatory, and by appointment
monetary — turns over on that cadence. An analog drawn from a different
administration is worth materially less than one from this one.

**Two competing anchors, recorded because they disagree and were not chosen:**

- **Fed chair tenure ~8y** (Greenspan 19, Bernanke 8, Yellen 4, Powell 8+). Since
  the state being matched is *macro*, and monetary policy is set by the chair
  rather than the president, this is arguably the better anchor.
- **Business cycle ~5–6y** (NBER post-war expansions average ~5y). Macro analogs
  are substantially cycle-phase analogs.

The ladder below spans all three. The primary is 4y on the stated reasoning; it
is not claimed to be the best-fitting value, and it was fixed before any Sharpe
was observed.

**Ladder: {2, 4, 8, 16, ∞}.** Log-uniform, spanning all three anchors, with ∞
(no decay) as the control — the current frozen behaviour. **All five rungs
reported regardless of outcome.** No rung may be promoted to primary afterwards.

## 4. Characterisation recorded BEFORE the sweep

From `recency_diagnostic.py` on the real panel, 120 sampled rebalance dates from
2012:

| | no decay | exponential HL=4y |
|---|---|---|
| median ESS (of top-k 100) | **100.0** | **99.9** |
| weighted mean analog age | **0.40y** | **0.24y** |
| top-k overlap vs no-decay | 1.00 | **0.80** |

**Three things follow, and they limit what any result here can mean:**

1. **The engine already draws almost entirely from the recent past.** Mean analog
   age with NO recency weighting is five months. λ at HL=4y moves that to three
   months. The recency kernel is close to redundant on this data, because macro
   states are persistent — same-regime days near in PC space are also near in time.
2. **ESS is 100 out of top-k 100.** Weights across the selected analogs are
   effectively uniform: σ=1.5 is wide enough that the Gaussian kernel barely
   discriminates. The "similarity-dominant" weighting in the locked design is
   therefore **not occurring** — similarity picks *which* 100, then weights them
   almost equally.
3. Taken together the engine behaves closer to **"average the recent same-regime
   past"** than to "find the 2008 analog and learn from it." This is a
   characterisation, not a bug — nothing computes incorrectly — but the word
   *analog* currently promises more than the mechanism delivers, and the report
   must say so.

**The lever for genuine long-history analog behaviour is σ, not λ.** Tightening σ
is NOT done here: σ is frozen in `models.yaml` for the live forward test.

## 5. What must not change

`config/models.yaml` is frozen pre-registration (`ce18d34`, 2026-08-17) for the
running forward test. `half_life_years` defaults to `None`, which yields
`exp(0)=1` and reproduces prior weights **bit-identically** (verified in
`recency_patch.py`). model_1/2/3 are **not edited**. Any recency-weighted model is
a NEW entry.

## 6. Success criterion — written before the answer

> **A recency-weighted model supersedes the no-decay control only if it beats it
> on the long-history (survivorship-controlled) universe, at the primary rung,
> AND the improvement is monotone or stable across at least three adjacent rungs
> of the ladder.**

A single rung outperforming is a grid winner, not a finding. Given §4, the
registered expectation is **little or no improvement**: at HL=4y the analog set
overlaps 80% with no-decay and mean age moves five months to three. Any large
Sharpe change would be surprising and should be treated as suspect rather than
as success.

**All results here are IN-SAMPLE** on data used throughout this project. Nothing
in this sweep may be promoted to a live model without forward-test evidence.

## 7. Amendments

*(none)*

| date | change | reason |
|---|---|---|
| | | |
