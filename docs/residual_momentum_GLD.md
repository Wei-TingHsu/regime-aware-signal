# T-H residual momentum / reversal — GLD

*2026-10-23 16:43. Residual from a rolling 252-session fit of the named reasons (refit every 20). Signal = past-w cumulative residual; forward = next-h return; non-overlapping samples. IC = rank correlation; positive = continuation, negative = reversal. Best cell by |IC| judged against the best |IC| of the same grid on 200 shifted residual series; PASS also needs |IC| ≥ plain momentum's + 0.02 on the same cell.*

**Best cell: w 60 → h 60: IC -0.190 (reversal), hit 42%, long-short Sharpe -0.45, n 45; null best |IC| median 0.239, p = 0.770; plain momentum on the same cell IC +0.035 → FAIL**

## Residual: IC by window (rows) × horizon (columns); sign hit-rate in brackets

| w \\ h | 5 | 10 | 20 | 40 | 60 |
|---|---|---|---|---|---|
| 5 | -0.039 (47%) | +0.018 (51%) | -0.001 (51%) | +0.136 (58%) | -0.053 (46%) |
| 10 | -0.018 (50%) | -0.039 (48%) | -0.048 (48%) | -0.015 (52%) | -0.079 (41%) |
| 20 | -0.026 (50%) | +0.010 (50%) | +0.118 (51%) | -0.096 (46%) | -0.170 (41%) |
| 40 | +0.024 (53%) | +0.037 (54%) | +0.072 (50%) | -0.084 (44%) | -0.084 (47%) |
| 60 | -0.033 (50%) | -0.030 (50%) | +0.013 (52%) | -0.116 (51%) | -0.190 (42%) |

## Plain momentum (total return) on the same grid

| w \\ h | 5 | 10 | 20 | 40 | 60 |
|---|---|---|---|---|---|
| 5 | -0.036 (49%) | +0.052 (54%) | -0.008 (50%) | +0.071 (52%) | -0.092 (46%) |
| 10 | +0.006 (50%) | -0.031 (50%) | -0.031 (45%) | -0.067 (45%) | -0.098 (39%) |
| 20 | -0.011 (48%) | -0.014 (48%) | +0.088 (53%) | -0.098 (48%) | -0.073 (50%) |
| 40 | +0.024 (53%) | +0.033 (55%) | +0.082 (53%) | -0.056 (49%) | +0.054 (51%) |
| 60 | -0.010 (54%) | -0.001 (55%) | +0.069 (57%) | +0.038 (63%) | +0.035 (62%) |

Shape across the grid: 8 cells continuation, 17 reversal. Reading: continuation at short horizons with reversal at long ones is the slow-information-then-unwind pattern; reversal everywhere is price pressure unwinding; nothing clearing the null means the residual is not predictable at these horizons — whatever caused it.
Verdicts: PASS = predictable beyond noise AND better than plain momentum; INCONCLUSIVE = predictable but no better than the price trend itself; FAIL = not distinguishable from noise.
