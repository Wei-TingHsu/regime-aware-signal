# Target range — Stage 1 calibration (registered test)

*2026-10-22 23:21. h = 60; targets ±5%, ±10%; years 2012–2025; Brier skill of regime-conditional reach probabilities over unconditional ones, walk-forward. PASS: skill ≥ 0.05 and better in ≥ 60% of years; FAIL: skill ≤ 0. 24 cells — about 2 could pass by chance.*

| market | target | side | years | cases | Brier skill | years better | verdict |
|---|---|---|---|---|---|---|---|
| SPY | 5% | up | 14 | 70 | -0.001 | 64% | FAIL |
| SPY | 5% | down | 14 | 70 | -0.080 | 43% | FAIL |
| SPY | 10% | up | 14 | 70 | -0.129 | 29% | FAIL |
| SPY | 10% | down | 14 | 70 | -0.157 | 29% | FAIL |
| TLT | 5% | up | 14 | 70 | -0.148 | 36% | FAIL |
| TLT | 5% | down | 14 | 70 | +0.008 | 50% | INCONCLUSIVE |
| TLT | 10% | up | 14 | 70 | -0.069 | 43% | FAIL |
| TLT | 10% | down | 14 | 70 | -0.025 | 43% | FAIL |
| GLD | 5% | up | 14 | 70 | +0.044 | 43% | INCONCLUSIVE |
| GLD | 5% | down | 14 | 70 | +0.004 | 50% | INCONCLUSIVE |
| GLD | 10% | up | 14 | 70 | +0.037 | 50% | INCONCLUSIVE |
| GLD | 10% | down | 14 | 70 | -0.034 | 50% | FAIL |
| UUP | 5% | up | 14 | 70 | -0.091 | 36% | FAIL |
| UUP | 5% | down | 14 | 70 | -0.098 | 36% | FAIL |
| UUP | 10% | up | 14 | 70 | -0.007 | 50% | FAIL |
| UUP | 10% | down | 14 | 70 | -0.486 | 50% | FAIL |
| USO | 5% | up | 14 | 70 | -0.012 | 43% | FAIL |
| USO | 5% | down | 14 | 70 | +0.006 | 50% | INCONCLUSIVE |
| USO | 10% | up | 14 | 70 | +0.005 | 57% | INCONCLUSIVE |
| USO | 10% | down | 14 | 70 | -0.027 | 43% | FAIL |
| WTI_SPOT | 5% | up | 14 | 68 | -0.055 | 36% | FAIL |
| WTI_SPOT | 5% | down | 14 | 68 | +0.008 | 43% | INCONCLUSIVE |
| WTI_SPOT | 10% | up | 14 | 68 | +0.021 | 43% | INCONCLUSIVE |
| WTI_SPOT | 10% | down | 14 | 68 | +0.026 | 50% | INCONCLUSIVE |

Verdict counts: {'FAIL': 15, 'INCONCLUSIVE': 9}. Per market, majority PASS: GLD: no, SPY: no, TLT: no, USO: no, UUP: no, WTI_SPOT: no
