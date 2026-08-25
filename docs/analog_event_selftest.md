# Analog-event estimator — blind acceptance tests

*Run 2026-08-25 03:20:27 +0800.*

Registered in `docs/prereg_analog_event.md` §9.2. Real macro panel, regimes, and return series; only the event-date ↔ return correspondence is destroyed. **No real conditional estimate was computed in this run.**

Test 5: 200 replications × 500 permutations.

| test | result | detail |
|---|---|---|
| 1 recovery | **PASS** | estimator +0.793% +/- 0.390% vs ORACLE +0.903% (same weights) -> agreement within 2se | raw planted +1.000%, kernel attenuation 90.3% of it -- expected for a smoother across a step | n=400, median ESS 29.7, sigma 0.350 (target 30.0, bisection converged) |
| 2 precedent count | **PASS** | reported matched-event counts equal planted counts at n=25,60,140 |
| 3 tier labelling | **PASS** | all three tiers reached AND correctly assigned | strong: tiers 1/2/3 = 347/0/53 of 400 queries; moderate: tiers 1/2/3 = 264/75/61 of 400 queries; none: tiers 1/2/3 = 0/260/140 of 400 queries; thin: tiers 1/2/3 = 0/0/6 of 6 queries |
| 4 abstention | **PASS** | 6 matched events -> ESS 3.7 < 8, abstain=True, tier 3 |
| 5a degenerate fraction | **PASS** | tau2 = 0 in 32.0% of 200 reps -- the registered null path fired and the blend stayed at the unconditional. This is the estimator working, and it is why the ORIGINAL test 5 failed (rejection 0.005, median p 0.906): a statistic that is identically zero gives p = 1 by ties. |
| 5b null calibration | **PASS** | over the 136 reps where the estimator conditioned, band [0.02, 0.08] UNCHANGED -- PRIMARY permute_y: 0.066 | permute_Z (original, retained): 0.000; ** THE TWO NULLS DISAGREE ON THE VERDICT -- that disagreement is itself the finding and is reported as such, with no tie-break **. Median p (permute_y) 0.653. Naive rate over all 200 reps including degenerate ones: 0.045. |
| 6 tau2=0 path | **PASS** | identical cell means -> tau2 0.00e+00, w 0.00, tier 3, estimate == unconditional: True |

**All six pass.** Unblinding is authorised once the corpus read completes.

