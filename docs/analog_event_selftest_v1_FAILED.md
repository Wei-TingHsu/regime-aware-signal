# Analog-event estimator — blind acceptance tests

*Run 2026-08-24 22:58:33 +0800.*

Registered in `docs/prereg_analog_event.md` §9.2. Real macro panel, regimes, and return series; only the event-date ↔ return correspondence is destroyed. **No real conditional estimate was computed in this run.**

Test 5: 200 replications × 500 permutations.

| test | result | detail |
|---|---|---|
| 1 recovery | **PASS** | estimate +0.017% +/- 2.826%, ESS 2.4, sigma 0.591 (median ESS 17.8 vs target 18.0) |
| 2 precedent count | **PASS** | reported matched-event counts equal planted counts at n=25,60,140 |
| 3 tier labelling | **PASS** | tier matches the w/ESS boundaries at every n | n=10: ESS 6.1 w 0.62 tier 3; n=20: ESS 3.2 w 0.11 tier 3; n=40: ESS 2.6 w 0.00 tier 3; n=80: ESS 2.2 w 0.00 tier 3; n=160: ESS 2.3 w 0.05 tier 3 |
| 4 abstention | **PASS** | 6 matched events -> ESS 3.6 < 8, abstain=True, tier 3 |
| 5 null calibration | **FAIL** | 200 reps x 500 perms, no effect planted: rejection at alpha=0.05 is 0.005 (registered band [0.02, 0.08]); median p 0.906 |
| 6 tau2=0 path | **PASS** | identical cell means -> tau2 0.00e+00, w 0.00, tier 3, estimate == unconditional: True |

**Not all tests pass. Unblinding is NOT authorised.**

