# T13 A3b — the conditional estimate, walk-forward

*2026-10-16. Pool p8, 116 shocks; estimate for shock k uses shocks whose 60-session outcome closed before k; kernel on standardised legs (dollar 5s, DGS2 5s bp, oil 5s) with half weight on a regime mismatch and a 10-year recency half-life; ESS floor 8; criterion prereg_blindspot §3b: (i) sign at 20 sessions ≥ 60% where ESS ≥ 8, vs the pool median's share; (ii) time-to-extreme within ±10 sessions ≥ 50%. Permutation null for (i): leg vectors shuffled across shocks, 10,000 draws.*

| market | shocks scored (ESS ≥ 8) | (i) conditional sign hit | pool-median sign hit | null q95 | p | (ii) timing within ±10 | verdict |
|---|---|---|---|---|---|---|---|
| SPY | 67 | 42% | 55% | 54% | 0.920 | 3% | **FAIL** |
| TLT | 67 | 51% | 49% | 63% | 0.734 | 22% | **FAIL** |
| GLD | 59 | 44% | 56% | 55% | 0.789 | 7% | **FAIL** |
| UUP | 47 | 51% | 57% | 64% | 0.736 | 66% | **FAIL** |
| USO | 50 | 30% | 46% | 60% | 0.990 | 54% | **FAIL** |
| WTI_SPOT | 65 | 45% | 55% | 48% | 0.258 | 8% | **FAIL** |

Reading: (i) asks whether knowing the legs and the regime at the shock tells you gold's (or any market's) direction 20 sessions on better than just knowing 'an oil shock happened'. (ii) asks the same for when the move peaks. UNTESTED = fewer than 15 shocks with enough comparable precedents. Prior: (i) PASS-weak 60–65%, (ii) FAIL.

Verdicts: {'SPY': 'FAIL', 'TLT': 'FAIL', 'GLD': 'FAIL', 'UUP': 'FAIL', 'USO': 'FAIL', 'WTI_SPOT': 'FAIL'}
