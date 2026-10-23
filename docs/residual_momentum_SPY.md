# T-H residual momentum / reversal — SPY

*2026-10-23 16:43. Residual from a rolling 252-session fit of the named reasons (refit every 20). Signal = past-w cumulative residual; forward = next-h return; non-overlapping samples. IC = rank correlation; positive = continuation, negative = reversal. Best cell by |IC| judged against the best |IC| of the same grid on 200 shifted residual series; PASS also needs |IC| ≥ plain momentum's + 0.02 on the same cell.*

**Best cell: w 20 → h 60: IC -0.208 (reversal), hit 45%, long-short Sharpe -0.49, n 82; null best |IC| median 0.174, p = 0.310; plain momentum on the same cell IC -0.152 → FAIL**

## Residual: IC by window (rows) × horizon (columns); sign hit-rate in brackets

| w \\ h | 5 | 10 | 20 | 40 | 60 |
|---|---|---|---|---|---|
| 5 | -0.055 (48%) | -0.058 (51%) | -0.166 (47%) | -0.092 (52%) | -0.208 (46%) |
| 10 | -0.034 (51%) | -0.033 (51%) | -0.163 (44%) | +0.030 (52%) | -0.175 (49%) |
| 20 | -0.047 (50%) | -0.060 (50%) | -0.097 (47%) | -0.057 (47%) | -0.208 (45%) |
| 40 | -0.046 (51%) | -0.069 (46%) | -0.129 (46%) | -0.169 (45%) | -0.028 (51%) |
| 60 | -0.068 (49%) | -0.062 (47%) | -0.098 (43%) | -0.064 (50%) | +0.010 (53%) |

## Plain momentum (total return) on the same grid

| w \\ h | 5 | 10 | 20 | 40 | 60 |
|---|---|---|---|---|---|
| 5 | -0.115 (50%) | -0.057 (57%) | -0.086 (53%) | -0.049 (54%) | -0.048 (59%) |
| 10 | -0.080 (51%) | -0.060 (53%) | -0.082 (50%) | +0.037 (55%) | -0.130 (57%) |
| 20 | -0.060 (54%) | -0.039 (56%) | -0.049 (54%) | -0.067 (47%) | -0.152 (57%) |
| 40 | -0.070 (55%) | -0.078 (56%) | -0.092 (57%) | +0.012 (63%) | -0.024 (62%) |
| 60 | -0.089 (55%) | -0.101 (56%) | -0.088 (58%) | -0.057 (61%) | -0.013 (63%) |

Shape across the grid: 2 cells continuation, 23 reversal. Reading: continuation at short horizons with reversal at long ones is the slow-information-then-unwind pattern; reversal everywhere is price pressure unwinding; nothing clearing the null means the residual is not predictable at these horizons — whatever caused it.
Verdicts: PASS = predictable beyond noise AND better than plain momentum; INCONCLUSIVE = predictable but no better than the price trend itself; FAIL = not distinguishable from noise.
