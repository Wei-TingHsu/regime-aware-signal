# Pre-registration — asymmetry levers, engine side (TRACK §3.16)

*Registered 2026-10-09, before any code. Asymmetry at h* = 2 is 1.008 (`48a6c4e879a1_n2617_h2`). Five filters on
which calls the engine makes; each runs beside the incumbent estimator on the same backfill and is scored by the
same referee. E4 first.*

## 1. Criterion, fixed for every lever

Against the incumbent on the same 1,532 report days:

- **PASS** — non-overlap asymmetry rises by ≥ 0.20 **and** the non-overlap hit-rate is not below its own
  permutation null **and** the lever still issues ≥ 30 non-overlapping calls;
- **INCONCLUSIVE** — asymmetry rises by ≥ 0.20 but one of the other two fails;
- **FAIL** — otherwise.

The second clause exists because abstaining on everything raises asymmetry trivially; the third because a lever
that leaves too few calls to score has not been tested. Asymmetry's 95% bootstrap interval is reported; a PASS
whose interval includes the incumbent's point value is reported as PASS-weak.

## 2. E4 — event-bin alignment (first)

**Mechanism.** The 9 Oct attribution states found that on SPY's big-move days 23 of 100 "wrong" readings came from a
document in the *other* half of the day from the move — the document was not the driver. Those readings enter the net
view today and produce calls that read backwards.

**Rule.** A document counts toward a market's net view only if, among that document class's precedents on the
asset, the move in the document's own bin (overnight for prints, 8-Ks, orders; intraday for FOMC) had the sign of the
reading at least as often as the other bin did. Computed on the expanding history through t−1; a class with fewer
than 30 precedents is counted as aligned (no evidence to exclude it).

**Prior.** PASS on SPY and GLD (where "not the driver" was largest); INCONCLUSIVE on TLT (the print source is new
and its precedents thin); no effect on USO.

## 3. E1 — ESS floor by expected move (second)

**Rule.** Abstain unless ESS ≥ 8 *and* the median |forward return| of the precedent pool ≥ the asset's own median
|2-session return| over the expanding history. **Prior.** PASS-weak: asymmetry up, n down sharply.

## 4. E3, E2, E5 — registered, run in that order after E1

- **E3** precedent dispersion: call only when the pool's τ² is below the asset's median τ² over history.
- **E2** specificity gate at the source's own median specificity rather than the veto level.
- **E5** estimate scaled by the earned influence weight for source × regime (`docs/attribution_influence.md`),
  zero where none earned; waits until ≥ 10 cells have earned a weight.

## 5. What a PASS permits

A PASS lever becomes a candidate for the estimator through the registered source-expansion rule, never by direct
substitution; the app shows both referee lines (incumbent, lever) until the comparison is recorded. No lever
changes the forward ledger.

## 6. Amendments

| date | change | reason |
|---|---|---|
| 2026-10-09 | **E4 result recorded, no rule change.** Backfill `48a6c4e879a1_n2617_h2_E4`, 1,532 report days, 10,000 permutations. Non-overlap: 328 calls (incumbent 534), hit-rate 54.3% (incumbent 54.9%) against its own null 56.1%, p 0.19; asymmetry 1.128 [0.899, 1.490] (incumbent 1.008 [0.853, 1.232]). Clause 1: +0.12 < 0.20, not met. Clause 2: 54.3% < 56.1% null, not met. Clause 3: 328 ≥ 30, met. **FAIL.** The lever dropped a document on 644 asset-days (SPY 547, USO 80, TLT 77, GLD 29, UUP 10) — it acts almost only on SPY. Prior (PASS on SPY and GLD) wrong. Asymmetry's interval includes the incumbent's point value, so even the +0.12 is not distinguishable from noise. Next: E1 as registered. | Result, scored against §1 as written |
| 2026-10-10 | **E1 result recorded, no rule change.** Backfill `48a6c4e879a1_n2617_h2_E1`, 1,532 report days, 10,000 permutations. Non-overlap: 198 calls (incumbent 534), hit-rate 48.5% against its own null 54.5%, p 0.90; asymmetry 1.052 [0.842, 1.383] (incumbent 1.008 [0.853, 1.232]); mean signed move −0.006% (incumbent +0.10%). Clause 1: +0.04 < 0.20, not met. Clause 2: 48.5% < 54.5% null, not met. Clause 3: 198 ≥ 30, met. **FAIL.** The gate kept the days whose precedents moved most and the engine was wrong more often on them: expected move does not filter direction; it belongs in sizing (T2). Prior (PASS-weak) wrong, #41. Next: E3 as registered. | Result, scored against §1 as written |
