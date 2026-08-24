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

`analog_core._kw()` implemented only the similarity half. The gap was found
2026-08-23, five days after the design was locked, and only because it was asked
about directly.

> **CORRECTED 2026-08-24 (see §7, Amendment 1).** The original text of this
> section read *"No λ existed anywhere in the codebase."* **That was false.**
> `config/config.yaml` carries `analog.recency_decay_lambda: 0.0008` and
> `src/analog_backtest.py` applies it as
> `exp(-lam * (pos - cand))` with age in **sessions** — an effective half-life of
> ln2/0.0008 = 866 sessions = **3.44 years**.
>
> `analog_backtest.py` is the script that produced the reported **0.51 / 0.25**
> (835 rebalances, 2010-01-04 → 2026-08-11, 35-asset ≥8y cut). **Those figures
> were computed WITH recency decay at HL ≈ 3.44y, not without it.**
>
> The gap was real but narrower than stated: λ was missing from `analog_core`
> (the frozen-model and live-harness path), not from the project. The two engines
> differ in three further respects — `analog_core` z-scores the PCs, freezes one
> GMM on all history, and applies no decay; `analog_backtest` uses raw PC values
> so PC1 dominates the distance, refits the GMM expanding-window every 20
> sessions, and decays. They are different estimators and legitimately report
> different numbers (0.40 vs 0.25).
>
> **Consequence for this registration: the ladder runs on BOTH engines.** See §7.
> The value 0.0008 has no recorded provenance anywhere in `docs/`; it is off the
> registered ladder and is reported as **the incumbent, not a rung**.

## 2. Functional form: EXPONENTIAL

`recency = exp(-ln2 · age_years / HL)`, with age measured in years (sessions/252).

> **SCOPE NOTE (2026-08-24).** `recency_diagnostic.py` characterised
> `analog_core`, whose default is genuinely no-decay. It did **not** characterise
> `analog_backtest`, which already decays at HL ≈ 3.44y. Every "no decay" column
> in §4 therefore describes the frozen-model engine, **not** the engine behind
> the reported 0.51 / 0.25.

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

*One amendment, recorded below. Written BEFORE any rung of the ladder was run,
and before any Sharpe under decay was observed.*

| date | change | reason |
|---|---|---|
| 2026-08-24 | §1's claim that "no λ existed anywhere in the codebase" is retracted as **false**. λ has been present in `config/config.yaml` as `analog.recency_decay_lambda: 0.0008` and applied in `src/analog_backtest.py`, giving HL ≈ 3.44y in session units. The reported 0.51 / 0.25 carry that decay. | The premise was wrong on a checkable fact. Recording it as an amendment rather than editing §1 silently, so the error and its correction are both visible. |
| 2026-08-24 | **The ladder now runs on BOTH engines.** Engine A = `analog_core` (frozen-model path, genuine no-decay default); Engine B = `analog_backtest` (headline path, incumbent λ=0.0008). Rungs {2,4,8,16,∞} on each. On Engine B, HL is converted to per-session λ as `ln2/(HL×252)` and ∞ is `λ=0`. | One engine's ladder cannot speak for the other. Engine B at ∞ is a number that has never been computed, and it is the only way to learn what the headline result owes to an unregistered hyperparameter. |
| 2026-08-24 | λ=0.0008 (HL≈3.44y) is reported as **the incumbent, off-ladder**, never as a rung and never promotable. | §3 forbids promoting a rung after the fact; an unregistered value with no recorded provenance has weaker standing still. Its only role is reproducing the recorded 0.51 / 0.25. |

**Unchanged by this amendment:** the functional form (exponential), the primary
half-life (4y, presidential-term grounds), the ladder values, and the §6 success
criterion. Only the count of engines the ladder runs on has changed.

**Note on 4y vs 3.44y.** The primary rung was fixed on stated economic grounds
before this discovery, and it sits close to the incumbent's effective half-life.
That proximity is **coincidence, not corroboration** — 0.0008 has no recorded
reasoning behind it. Neither value may be cited as evidence for the other.
