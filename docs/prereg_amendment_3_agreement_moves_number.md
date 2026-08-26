# AMENDMENT 3 to `prereg_analog_event.md` — the agreement flag MAY move the number

**Filed 2026-08-26. Written and committed BEFORE the step 3 unblinding was run.**

*Timing declaration, unchanged from Amendment 2: at the moment of writing, the
registered pooled leave-one-out test on the real event–return correspondence has
NOT been executed and no number from it has been seen. What HAS been seen is the
cross-source read audit of 2026-08-25 (`docs/read_audit_results.md`), which
concerns the reader's internal consistency and says nothing about whether the
estimator works.*

**Relationship to Amendment 2.** Amendment 2 was filed earlier today and
permitted a conviction label while prohibiting any effect on the number. This
amendment supersedes that prohibition. **Amendment 2 is left in the repository
unaltered**, per the project's rule that superseded text is not rewritten — the
sequence of decisions, including the one that was reversed within the day, is
part of the record.

---

## 1. WHAT CHANGES

Amendment 2 §2 read: *"A `CONCORDANT` label must never be rendered as a higher
confidence number. The interval on a concordant case is the same interval it
would have had without the reader."*

That prohibition is **lifted, conditionally**. The agreement relationship may
narrow the reported interval, subject to every constraint in §2–§5 below.

## 2. WHAT MAY MOVE, AND WHAT MAY NOT

**The interval may move. The point estimate may not.**

The step 3 point estimate is what comparable macro history did. The reader
carries a *sign* and a *specificity*, not a magnitude — nothing in the v1 schema
estimates how far an asset moves. Letting a field with no magnitude information
shift a magnitude would be attributing precision the instrument does not have.

What the reader plausibly carries is information about whether the estimate's
**sign** is right, and that is a statement about dispersion. So:

- `direction_point` — **unchanged** under all labels.
- `interval_halfwidth` — multiplied by ρ̂, defined in §3.
- `k`, τ², the DerSimonian–Laird weights — **unchanged**. The blend is computed
  first and the adjustment applied to its output, so the estimator itself is
  untouched and the frozen code does not change.

## 3. THE ADJUSTMENT IS ESTIMATED, NEVER CHOSEN

This is the load-bearing clause. Neither I nor anyone else picks a number like
"narrow by 20% when concordant". The magnitude is whatever the data supports.

**Definition.** ρ = the ratio of residual dispersion of the signed realised
return among `CONCORDANT` events to the pooled residual dispersion across all
labels, at the registered primary horizon.

**Estimation.** ρ̂ is computed **inside each leave-one-out fold**, from that
fold's training events only, exactly as `k` already is under
`prereg_analog_event.md` §5. An event's own outcome never contributes to the ρ̂
applied to it. Estimating ρ on all events and then applying it to those same
events would be the in-sample error this whole project is built to avoid.

**Clipping.** ρ̂ is clipped to **[0.70, 1.30]**. A concordant case can be
narrowed by at most 30% and a discordant case widened by at most 30%. The clip
exists because a dispersion ratio estimated on a small arm is unstable, and an
unclipped estimate could produce an interval narrow enough to be actively
misleading. The bound is registered now, before n is known.

**`UNINFORMATIVE` label:** ρ̂ = 1 by construction. No movement.

## 4. THE GATE — NO MOVEMENT UNLESS THE TEST PASSES FIRST

The falsification test registered in **Amendment 2 §4** is unchanged and runs
first:

> Mean signed realised return, `CONCORDANT` versus `DISCORDANT`, two-sided
> permutation test on label assignment (10,000 permutations, seed 42), bootstrap
> 95% CI on the difference. Ships only if `CONCORDANT` mean exceeds `DISCORDANT`
> mean and p < 0.05. If either arm has n < 20, the result is UNDERPOWERED.

Applied to this amendment:

| test outcome | what ships |
|---|---|
| **PASS** | ρ̂ applied as in §3; label displayed; interval moves |
| **FAIL** | ρ = 1. Label displayed, display-only. Amendment 2's regime stands |
| **UNDERPOWERED** (n < 20 either arm) | ρ = 1. Label displayed, display-only |

**A failed or underpowered test does not become a reason to loosen the
criterion.** The criterion is fixed by this document. Both outcomes are reported
in the step 6 documentation and in the final report.

## 5. THE COVERAGE CHECK — REGISTERED, AND IT CAN REVOKE THE ADJUSTMENT

The concern that motivated Amendment 2's prohibition is real and does not
disappear because the prohibition was lifted: **the reader's direction and the
historical estimate are keyed to the same event.** They are not independent
measurements, and treating their agreement as confirmation risks counting one
observation twice.

Amendment 2 addressed that by assertion. This amendment addresses it by
measurement, which is stronger.

**Test.** After ρ̂ is applied, compute empirical coverage of the adjusted
intervals: the fraction of events whose realised return falls inside their own
adjusted 95% interval, computed out-of-fold.

**Criterion, registered now.** Empirical coverage of the adjusted intervals must
be **≥ 0.90**. If it falls below 0.90, the adjustment is producing intervals
narrower than the evidence supports — which is exactly what double-counting one
observation would look like — and **ρ reverts to 1 for all labels**, permanently,
with the measured coverage reported.

Coverage of the *unadjusted* intervals is computed and reported alongside, as
the baseline. If the unadjusted intervals are themselves below 0.90, that is a
finding about the estimator and is reported as such, independently of anything
to do with the agreement flag.

## 6. WHAT A USER SEES

- The conviction label, in words.
- The point estimate, identical under every label.
- The interval, adjusted or not according to §3–§5.
- A one-line statement of whether the adjustment is active, and the measured
  ρ̂ and coverage if it is.

The last item is not optional. A product that silently narrows its own error
bars is the thing this amendment is designed not to be. If the interval moved,
the report says so and says by how much.

## 7. HONEST NOTE ON THE DECISION

My recommendation was display-only, on the grounds in §5. The decision to permit
movement was Steven's, taken on 2026-08-26 after that recommendation was given
and the reasoning was on the table. It is recorded here rather than absorbed
silently, because a reader of the report should be able to see that this was a
choice, who made it, and what was argued against it.

The design in §3–§5 is what makes the choice defensible rather than merely
permitted: the adjustment is estimated out-of-fold, clipped, gated on a
pre-registered test, and revocable by a coverage check that the data itself can
trigger. If agreement is worth something, the data will say how much. If it is
not, three separate registered clauses set ρ to 1.
