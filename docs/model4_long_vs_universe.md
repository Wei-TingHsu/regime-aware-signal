# Model 4 — long top-N against the equal-weight universe

*Run 2026-09-08 17:04 +0800. 200 permutations. Score identical to model_1; only the benchmark changes.*

**Verdict: FAIL.**

| | ALL 47 | LONG-HISTORY 35 |
|---|---|---|
| Spread (top-5 − universe), weekly | +0.206% | +0.099% |
| Sharpe | +0.54 | +0.32 |
| Block-permutation p | 0.0348 | 0.0995 |
| Exceedances | 6 | 19 |
| Split ratio | 9.08× | 3.87× |

Criteria: R1 ALL p<0.05 · R2 LONG-HISTORY p<0.05 · R3 split sign-agree and ≤3× on both. All three or nothing.

