# T-H residual momentum / reversal — USO

*2026-10-23 16:43. Residual from a rolling 252-session fit of the named reasons (refit every 20). Signal = past-w cumulative residual; forward = next-h return; non-overlapping samples. IC = rank correlation; positive = continuation, negative = reversal. Best cell by |IC| judged against the best |IC| of the same grid on 200 shifted residual series; PASS also needs |IC| ≥ plain momentum's + 0.02 on the same cell.*

**Best cell: w 20 → h 20: IC +0.167 (continuation), hit 59%, long-short Sharpe +0.53, n 138; null best |IC| median 0.214, p = 0.820; plain momentum on the same cell IC +0.053 → FAIL**

## Residual: IC by window (rows) × horizon (columns); sign hit-rate in brackets

| w \\ h | 5 | 10 | 20 | 40 | 60 |
|---|---|---|---|---|---|
| 5 | -0.050 (49%) | +0.002 (51%) | +0.020 (51%) | -0.105 (51%) | -0.159 (39%) |
| 10 | -0.032 (50%) | +0.013 (49%) | -0.158 (43%) | -0.104 (46%) | +0.028 (52%) |
| 20 | -0.036 (50%) | -0.008 (51%) | +0.167 (59%) | +0.035 (55%) | -0.073 (46%) |
| 40 | +0.010 (51%) | +0.023 (53%) | +0.119 (55%) | +0.020 (47%) | -0.094 (51%) |
| 60 | -0.045 (50%) | -0.052 (49%) | -0.004 (51%) | -0.058 (50%) | +0.089 (53%) |

## Plain momentum (total return) on the same grid

| w \\ h | 5 | 10 | 20 | 40 | 60 |
|---|---|---|---|---|---|
| 5 | -0.078 (49%) | +0.043 (56%) | +0.073 (55%) | +0.054 (52%) | -0.068 (57%) |
| 10 | -0.058 (51%) | -0.001 (51%) | -0.007 (50%) | -0.020 (55%) | +0.076 (57%) |
| 20 | -0.013 (52%) | -0.008 (54%) | +0.053 (55%) | +0.040 (43%) | +0.054 (50%) |
| 40 | +0.012 (52%) | -0.004 (52%) | +0.033 (49%) | +0.019 (51%) | -0.150 (51%) |
| 60 | -0.030 (52%) | -0.091 (51%) | -0.047 (51%) | -0.098 (46%) | -0.059 (49%) |

Shape across the grid: 11 cells continuation, 14 reversal. Reading: continuation at short horizons with reversal at long ones is the slow-information-then-unwind pattern; reversal everywhere is price pressure unwinding; nothing clearing the null means the residual is not predictable at these horizons — whatever caused it.
Verdicts: PASS = predictable beyond noise AND better than plain momentum; INCONCLUSIVE = predictable but no better than the price trend itself; FAIL = not distinguishable from noise.
