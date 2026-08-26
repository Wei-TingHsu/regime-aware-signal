# AMENDMENT 2 to `prereg_analog_event.md` — the agreement flag

**Filed 2026-08-26. Written and committed BEFORE the step 3 unblinding was run.**

*Timing declaration: at the moment of writing, the registered pooled
leave-one-out test on the real event–return correspondence has NOT been
executed. No number from it has been seen by anyone. What HAS been seen, and
what motivates this amendment, is the cross-source read audit of 2026-08-25
(`docs/read_audit_results.md`) — specifically that `direction` is an
impoverished field on political sources because the five macro axes cannot
represent a sector shock, while `specificity` and `stance` discriminate well.
That audit says nothing about whether the estimator works.*

---

## 1. WHAT WAS ORIGINALLY REGISTERED

`prereg_analog_event.md` §7.3, registered 2026-08-24 in commit `74b88dc`:

> The agreement flag is **display-only** and is **never weighted**. It does not
> enter the estimator, the precision blend, or `k`.

## 2. WHAT THIS AMENDMENT CHANGES

The flag may now set a **conviction label** shown in the step 6 decision report.
It still does not enter the estimator.

Precisely:

**PERMITTED by this amendment**

- The step 6 report may display a conviction label with three levels, determined
  solely by the sign relationship between the reader's `direction` on the
  relevant axis and the sign of the step 3 point estimate:
  - `CONCORDANT` — both non-negligible and the same sign
  - `DISCORDANT` — both non-negligible and opposite signs
  - `UNINFORMATIVE` — either is negligible (|value| ≤ 0.05), or the document
    read abstained
- The label may be rendered prominently, in words, adjacent to the estimate.
- The label may be used to order or filter what a user sees.

**STILL PROHIBITED, unchanged from §7.3**

- The flag does not enter the estimator at any point.
- It does not change `k`, the precision weights, τ², or the DerSimonian–Laird
  blend.
- It does not narrow, widen or shift the confidence interval.
- **A `CONCORDANT` label must never be rendered as a higher confidence number.**
  The interval on a concordant case is the same interval it would have had
  without the reader.

## 3. WHY THE PROHIBITION SURVIVES THE AMENDMENT

The reader's direction and the historical estimate are **keyed to the same
event**. They are not two independent measurements that happen to agree; they
are two readings of one occurrence, one from its text and one from what followed
similar macro states. Treating their agreement as confirmation double-counts a
single observation.

The failure mode this guards against is specific and this project has already
produced its analogue: in Week 14 the spillover INTRA effect went from +2.319%
(p 0.0002) to +0.012% (p 0.976) once entry used only tradeable information. A
number that looks strong because it has been counted twice is the same species
of error as a number that looks strong because it saw the future.

So: **the label describes a relationship between two outputs. The interval
describes the evidence. The amendment lets the first be shown; it does not let
the first modify the second.**

## 4. THE TEST THIS AMENDMENT REGISTERS

A conviction label that a user acts on is a claim about the world, and it must
be falsifiable. Registered here, before unblinding, so that it cannot be
specified after its answer is known.

**Hypothesis.** Cases labelled `CONCORDANT` have better realised outcomes than
cases labelled `DISCORDANT`.

**Statistic.** For each event with a step 3 estimate and a non-negligible reader
direction, the *signed realised return* — realised return multiplied by the sign
of the step 3 point estimate — at the registered primary horizon. Positive means
the estimate pointed the right way.

**Comparison.** Mean signed realised return, `CONCORDANT` versus `DISCORDANT`,
with a two-sided permutation test on the label assignment (10,000 permutations,
seed 42), reported with a bootstrap 95% CI on the difference.

**Criterion, registered now.** The conviction label ships in the product only if
the `CONCORDANT` mean exceeds the `DISCORDANT` mean **and** the permutation
p < 0.05. Otherwise the label is removed from step 6 and §7.3 reverts to
display-only in full. Either outcome is reported.

**Expected n is small** — it is bounded by events that have both a reader
direction above the negligibility floor and enough precedents for an estimate.
If either arm has n < 20 the test is reported as UNDERPOWERED and the label does
not ship, regardless of the point difference. This clause exists because n is
not yet known and I do not want the option of deciding what counts as enough
after seeing it.

**Ordering.** This test can only be run after unblinding. It is registered
before. Its result does not affect the step 3 estimate itself under any outcome.

## 5. WHY AMEND AT ALL

Customer discovery in Week 6 found that users ignore an unexplained signal and
read a structured explanation. The agreement relationship is explanation: it
tells a user that the document said one thing and the history said the same
thing, which is information they can weigh themselves. Suppressing it entirely
makes the product less useful without making it more honest.

What would make it dishonest is presenting agreement as extra evidence. This
amendment permits the first and forbids the second, and registers a test of
whether the label deserves to exist at all.
