# T-H residual momentum / reversal — SLV

*2026-10-23 16:43. Residual from a rolling 252-session fit of the named reasons (refit every 20). Signal = past-w cumulative residual; forward = next-h return; non-overlapping samples. IC = rank correlation; positive = continuation, negative = reversal. Best cell by |IC| judged against the best |IC| of the same grid on 200 shifted residual series; PASS also needs |IC| ≥ plain momentum's + 0.02 on the same cell.*

**Best cell: w 20 → h 60: IC -0.216 (reversal), hit 41%, long-short Sharpe -0.21, n 46; null best |IC| median 0.231, p = 0.555; plain momentum on the same cell IC -0.234 → FAIL**

## Residual: IC by window (rows) × horizon (columns); sign hit-rate in brackets

| w \\ h | 5 | 10 | 20 | 40 | 60 |
|---|---|---|---|---|---|
| 5 | +0.010 (51%) | -0.009 (49%) | -0.032 (47%) | +0.023 (49%) | +0.023 (43%) |
| 10 | -0.011 (49%) | -0.066 (51%) | -0.170 (41%) | -0.080 (42%) | -0.093 (39%) |
| 20 | -0.072 (48%) | -0.096 (46%) | +0.005 (48%) | -0.163 (39%) | -0.216 (41%) |
| 40 | -0.002 (49%) | -0.042 (49%) | -0.021 (49%) | -0.090 (49%) | -0.017 (44%) |
| 60 | -0.042 (45%) | -0.085 (44%) | -0.078 (43%) | -0.123 (38%) | -0.135 (47%) |

## Plain momentum (total return) on the same grid

| w \\ h | 5 | 10 | 20 | 40 | 60 |
|---|---|---|---|---|---|
| 5 | -0.005 (47%) | -0.011 (47%) | +0.001 (43%) | +0.152 (58%) | +0.143 (48%) |
| 10 | -0.013 (50%) | -0.044 (51%) | -0.066 (45%) | +0.127 (57%) | -0.038 (46%) |
| 20 | -0.070 (45%) | -0.066 (46%) | +0.019 (44%) | -0.044 (46%) | -0.234 (39%) |
| 40 | -0.030 (48%) | -0.043 (49%) | -0.063 (50%) | -0.159 (40%) | +0.039 (51%) |
| 60 | -0.062 (46%) | -0.085 (44%) | -0.073 (42%) | +0.075 (53%) | +0.058 (56%) |

Shape across the grid: 4 cells continuation, 21 reversal. Reading: continuation at short horizons with reversal at long ones is the slow-information-then-unwind pattern; reversal everywhere is price pressure unwinding; nothing clearing the null means the residual is not predictable at these horizons — whatever caused it.
Verdicts: PASS = predictable beyond noise AND better than plain momentum; INCONCLUSIVE = predictable but no better than the price trend itself; FAIL = not distinguishable from noise.
