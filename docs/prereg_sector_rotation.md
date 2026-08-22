# PRE-REGISTRATION — Sector rotation (semis as the leading indicator)

**Status: REGISTERED, UNRUN.** Committed before execution. The git timestamp is
the pre-registration evidence. Any post-run edit is recorded in §8 with its reason.

Separate document from the cross-asset registration by design: the two hypotheses
share an asset (GLD is in neither — but SPY appears in the cross-asset basket and
is the residualization factor here), and separate files prevent either from being
quietly reframed as the other after results are seen.

---

## 1. Hypothesis

Distinct from both the semiconductor chain (intra-sector information propagation,
closed as null) and cross-asset rotation (movement between asset *classes*). This
is movement between **industries within equity**, driven by business-cycle
expectations.

> **Registered order: SOXX → XAR → XLE → XLV → XLP.**
>
> Semiconductor orders lead the capital-expenditure cycle and are the classic
> early-cycle indicator. Defence and energy follow real-economy demand with a lag.
> Healthcare and staples are terminal — defensive sectors reprice last as capital
> completes its move out of cyclicals.

## 2. Prior — the base rate is against this, and that is registered up front

Sector rotation is the **most-tested and most-negative** hypothesis in this
literature:

- **Molchanov & Stangl** tested cross-sector predictability across **2,640
  t-statistics** and found scant evidence of sector rotation.
- **Jacobsen, Stangl & Visaltanachoti** granted *perfect foresight* of the
  business-cycle stage and still obtained at best ~2.3%/yr.
- This project's own Problem 1 found **no safe-haven correlation inversion in the
  high-VIX regime** (p 0.488 / 0.081), surviving a panel extension, a stress-axis
  correction and a calendar migration.

**A null here replicates published findings and is the expected outcome.** It is
registered as expected so that a null cannot later be presented as surprising, and
so that a positive result is understood to be running against a strong prior.

## 3. Assets and sample

`SOXX, XAR, XLE, XLV, XLP` — semiconductors, aerospace & defence, energy,
healthcare, staples.

**Panel constraint, registered honestly:** the 47-asset universe contains **no
financials, industrials, discretionary, utilities, or materials** ETFs. A classic
full business-cycle rotation test is **not available on this data**. This basket
is the closest constructible approximation, and the absence of five major sectors
limits what a null can establish.

**XAR chosen over IYW** on non-redundancy grounds: IYW is technology and
semiconductors are a large component of it, so SOXX→IYW would be close to
tautological. XAR is genuinely independent. Cost: sample starts ~2006 rather than
~2001.

## 4. Residualization: MARKET FACTOR (SPY)

`--residualize market --factor SPY`. Registered with reasoning:

All equity sectors share market beta. Without removing it the test would simply
detect that high-beta sectors move more on market days — a beta artifact, not
rotation. The leave-one-out mean is also unsuitable: five sectors are a poor proxy
for the market. An explicit SPY factor is the correct control.

The half-max statistic is normalised by each asset's own episode peak, so it
measures **when** an asset responds rather than **how much** — residual magnitude
differences cannot manufacture an apparent ordering.

## 5. Trigger: BOTH DIRECTIONS

`--trigger shock --shock-on SPY --shock-sign both --z 2.0`

Registered with reasoning, and **deliberately different from the cross-asset
registration**. The hypothesised mechanism — semis leading the capex cycle — is
**symmetric**: semiconductors lead both into and out of a cycle turn. Restricting
to risk-off would borrow a justification that applies to flight-to-quality but not
here, and would halve the sample for no mechanistic reason.

Each hypothesis's trigger is justified by its own mechanism, not by consistency
across hypotheses.

## 6. Design and success criterion

Design as `episode_rotation.py`: episode = eplen sessions after the trigger
(trigger day excluded); de-clustering gap = eplen; eplen **primary 15**, ladder
**{10, 15, 20}**, all rungs reported; window integrity enforced; statistics [1]
pooled within-episode lead-lag (k=1..3, max-over-k, Holm over 10 pairs) and [2]
order concentration (mean pairwise Kendall τ-b of half-max response orders);
null = independent per-name episode shuffle.

> **A positive verdict requires order concentration [2] to clear p < 0.05 at the
> primary rung AND at one adjacent rung, with the same sign.**

Statistic [1] is supporting evidence. Holm is applied within each rung, not across
the ladder — 30 pair-tests total, ~1.5 false positives expected at α=0.05. **A
lone significant pair is not a detection.**

## 7. Detection capability — demonstrated, not assumed

`--inject SOXX,XLE,1,0.3` is run on the **real** episodes before the real run and
must be recovered. Same limitation as recorded elsewhere: the injection validates
statistic **[1] only**; statistic [2] is validated on synthetic data but not on
this panel.

## 8. Amendments

*(none)*

| date | change | reason |
|---|---|---|
| | | |
