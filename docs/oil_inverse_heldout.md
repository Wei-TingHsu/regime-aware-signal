# USO inverse — held-out check on the +5%-only shocks

*2026-10-16. Shocks in the +5% pool that are not within 20 sessions of any +8% shock: 63 USO rows, never used in A3b or the diagnostic. Same kernel and ESS floor; walk-forward from the 16th. Criterion (prereg 16 Oct): PASS if inverse hit ≥ 60%, one-sided binomial p < 0.05, n ≥ 30.*

| scored | inverse hit | pool-median hit | binomial p | verdict |
|---|---|---|---|---|
| 34 | 47% | 53% | 0.696 | **FAIL** |

Reading: milder shocks (+5% to +8% in a week) are a different population from the +8% pool, so a pass here says the pattern is not specific to the big shocks; a fail says it may be. Either way the forward test decides.
