# T-H residual momentum / reversal — NVDA

*2026-10-23 16:43. Residual from a rolling 252-session fit of the named reasons (refit every 20). Signal = past-w cumulative residual; forward = next-h return; non-overlapping samples. IC = rank correlation; positive = continuation, negative = reversal. Best cell by |IC| judged against the best |IC| of the same grid on 200 shifted residual series; PASS also needs |IC| ≥ plain momentum's + 0.02 on the same cell.*

**Best cell: w 20 → h 60: IC +0.253 (continuation), hit 51%, long-short Sharpe +0.44, n 82; null best |IC| median 0.181, p = 0.190; plain momentum on the same cell IC +0.203 → FAIL**

## Residual: IC by window (rows) × horizon (columns); sign hit-rate in brackets

| w \\ h | 5 | 10 | 20 | 40 | 60 |
|---|---|---|---|---|---|
| 5 | +0.014 (52%) | -0.006 (51%) | -0.037 (49%) | +0.111 (55%) | +0.013 (44%) |
| 10 | +0.007 (50%) | +0.035 (52%) | -0.035 (48%) | +0.102 (51%) | +0.011 (48%) |
| 20 | +0.019 (52%) | +0.029 (51%) | +0.036 (51%) | -0.024 (51%) | +0.253 (51%) |
| 40 | +0.002 (51%) | +0.040 (52%) | +0.038 (50%) | +0.062 (47%) | +0.222 (57%) |
| 60 | +0.028 (52%) | +0.078 (53%) | +0.085 (51%) | +0.175 (57%) | +0.099 (46%) |

## Plain momentum (total return) on the same grid

| w \\ h | 5 | 10 | 20 | 40 | 60 |
|---|---|---|---|---|---|
| 5 | -0.052 (50%) | -0.064 (49%) | -0.097 (46%) | +0.021 (56%) | -0.044 (50%) |
| 10 | -0.005 (50%) | +0.058 (55%) | -0.032 (50%) | +0.108 (57%) | -0.003 (56%) |
| 20 | +0.020 (53%) | +0.070 (55%) | +0.107 (56%) | +0.002 (56%) | +0.203 (60%) |
| 40 | -0.000 (53%) | +0.065 (56%) | +0.071 (55%) | +0.065 (59%) | +0.217 (68%) |
| 60 | +0.018 (53%) | +0.083 (56%) | +0.115 (56%) | +0.199 (62%) | +0.072 (60%) |

Shape across the grid: 21 cells continuation, 4 reversal. Reading: continuation at short horizons with reversal at long ones is the slow-information-then-unwind pattern; reversal everywhere is price pressure unwinding; nothing clearing the null means the residual is not predictable at these horizons — whatever caused it.
Verdicts: PASS = predictable beyond noise AND better than plain momentum; INCONCLUSIVE = predictable but no better than the price trend itself; FAIL = not distinguishable from noise.
