# N1 v3c — reversal SIZE vs contradiction score, one joint test per group

Statistic: mean rank correlation across windows 3, 5, 10 × horizons 1, 3, 5, 10 (cells with n ≥ 30). p: share of 2,000 shuffles of the outcomes whose mean is at least as large (one-sided: a contradicting document goes with a larger reversal). Primary = all documents; Fed-only and BLS-only are measured beside it. Bar p < 0.0125.

| family | index | direction | events | cells | mean rank corr | p | before 2020 | from 2020 |
|---|---|---|---|---|---|---|---|---|
| all | SOX | fall | 229 | 12 | +0.117 | 0.0215 | +0.061 | +0.139 |
| all | SOX | rise | 217 | 12 | +0.121 | 0.0230 | +0.050 | +0.161 |
| all | SPX | fall | 48 | 8 | +0.020 | 0.4275 | +nan | +nan |
| fed | SOX | fall | 229 | 12 | +0.224 | 0.0010 | +0.165 | +0.285 |
| fed | SOX | rise | 217 | 12 | +0.078 | 0.1655 | +0.152 | -0.028 |
| fed | SPX | fall | 48 | 4 | +0.019 | 0.4485 | +nan | +nan |
| bls | SOX | fall | 229 | 12 | +0.008 | 0.4690 | -0.003 | +0.003 |
| bls | SOX | rise | 217 | 12 | +0.089 | 0.1055 | -0.068 | +0.188 |
| bls | SPX | fall | 48 | 4 | -0.200 | 0.9435 | +nan | +nan |

## What the score is worth in returns (all documents, window 5; reversal return over the next 5 sessions, by third of the contradiction score)

| index | direction | lowest third | middle third | highest third | n |
|---|---|---|---|---|---|
| SOX | fall | -2.25% | +2.73% | +1.42% | 121 |
| SOX | rise | +0.05% | -1.22% | +1.26% | 116 |
| SPX | fall | -1.16% | -0.18% | +1.28% | 34 |
