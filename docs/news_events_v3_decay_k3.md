# N1 v3d — is the effect on the document's release day, and does it fade?

Span after day 0 in this file: days +1..+3 (the columns headed +1..+5 below are over this span).

Day 0 = the session the document was released. Returns are signed so that positive = back against the ≥ 4% event. rank corr = Spearman correlation between the contradiction score and that day's return across (event, document-day) pairs. p from 2,000 shuffles of the scores across document days, one-sided for day 0, decay and drift; two-sided for the placebo.

## Rank correlation by day

| family | index | direction | day -2 | day -1 | day +0 | day +1 | day +2 | day +3 | day +4 | day +5 |
|---|---|---|---|---|---|---|---|---|---|---|
| all | SOX | fall | -0.003 | +0.043 | +0.169 | -0.045 | +0.096 | -0.076 | -0.040 | -0.008 |
| all | SOX | rise | +0.034 | +0.031 | +0.092 | -0.032 | +0.009 | -0.087 | -0.053 | -0.010 |
| all | SPX | fall | -0.030 | +0.140 | +0.047 | -0.068 | +0.408 | +0.055 | -0.056 | +0.104 |
| all | SPX | rise | -0.068 | +0.118 | -0.029 | -0.061 | +0.339 | +0.047 | +0.106 | +0.096 |
| fed | SOX | fall | +0.161 | -0.015 | +0.382 | -0.022 | +0.026 | -0.072 | +0.022 | -0.043 |
| fed | SOX | rise | +0.125 | -0.069 | +0.214 | -0.114 | -0.076 | -0.080 | -0.046 | -0.004 |
| fed | SPX | fall | -0.158 | -0.009 | +0.385 | +0.037 | +0.390 | +0.047 | +0.003 | +0.110 |
| bls | SOX | fall | -0.060 | +0.028 | +0.123 | -0.065 | +0.104 | -0.065 | -0.068 | +0.006 |
| bls | SOX | rise | +0.023 | +0.055 | +0.061 | -0.010 | -0.005 | -0.084 | -0.039 | -0.037 |
| bls | SPX | fall | +0.120 | +0.137 | -0.067 | -0.052 | +0.331 | +0.083 | -0.163 | +0.024 |
| bls | SPX | rise | -0.061 | +0.041 | -0.010 | -0.046 | +0.317 | -0.032 | -0.064 | +0.041 |

## The three tests

| family | index | direction | pairs | document days | day 0 | p | decay (day 0 − mean of +1..+5) | p | drift (cumulative +1..+5) | p | placebo (days −2, −1) | p |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | SOX | fall | 531 | 354 | +0.169 | 0.0040 | +0.178 | 0.0115 | -0.007 | 0.5585 | +0.020 | 0.6155 |
| all | SOX | rise | 476 | 343 | +0.092 | 0.0760 | +0.129 | 0.0455 | -0.026 | 0.6600 | +0.032 | 0.4285 |
| all | SPX | fall | 137 | 71 | +0.047 | 0.3680 | -0.085 | 0.6555 | +0.099 | 0.2730 | +0.055 | 0.5610 |
| all | SPX | rise | 81 | 55 | -0.029 | 0.5775 | -0.137 | 0.7580 | +0.075 | 0.3380 | +0.025 | 0.7985 |
| fed | SOX | fall | 194 | 134 | +0.382 | 0.0005 | +0.405 | 0.0015 | -0.060 | 0.6995 | +0.073 | 0.3240 |
| fed | SOX | rise | 178 | 129 | +0.214 | 0.0170 | +0.304 | 0.0070 | -0.171 | 0.9510 | +0.028 | 0.6700 |
| fed | SPX | fall | 54 | 27 | +0.385 | 0.0390 | +0.227 | 0.2235 | +0.127 | 0.3165 | -0.083 | 0.5235 |
| bls | SOX | fall | 387 | 255 | +0.123 | 0.0545 | +0.132 | 0.0770 | +0.000 | 0.5015 | -0.016 | 0.7420 |
| bls | SOX | rise | 349 | 250 | +0.061 | 0.2030 | +0.094 | 0.1435 | -0.007 | 0.5375 | +0.039 | 0.4160 |
| bls | SPX | fall | 101 | 52 | -0.067 | 0.6615 | -0.187 | 0.8085 | +0.141 | 0.2010 | +0.128 | 0.2395 |
| bls | SPX | rise | 59 | 42 | -0.010 | 0.5005 | -0.089 | 0.6335 | +0.088 | 0.3155 | -0.010 | 0.9425 |

## Returns by third of the score (lowest / middle / highest)

| family | index | direction | day 0 | days +1..+5 cumulative |
|---|---|---|---|---|
| all | SOX | fall | -0.40% / -0.28% / +0.70% | +0.18% / +0.43% / +0.02% |
| all | SOX | rise | -0.25% / -0.18% / +0.23% | -0.32% / +0.51% / -0.86% |
| all | SPX | fall | -0.35% / -2.41% / +0.34% | -1.27% / +0.23% / +0.04% |
| all | SPX | rise | +1.10% / +0.51% / +0.91% | -1.46% / +3.13% / +1.58% |
| fed | SOX | fall | -2.93% / -0.30% / +0.83% | +1.04% / +0.96% / +0.59% |
| fed | SOX | rise | -0.54% / -0.03% / +0.85% | +0.37% / -0.83% / -1.97% |
| fed | SPX | fall | -5.04% / -2.63% / +0.20% | +1.97% / -0.33% / +4.54% |
| bls | SOX | fall | +0.08% / -0.15% / +0.82% | +0.05% / -0.40% / -0.06% |
| bls | SOX | rise | -0.32% / -0.24% / -0.14% | -0.52% / +1.37% / -0.35% |
| bls | SPX | fall | +0.39% / -1.48% / -0.42% | -2.04% / -1.36% / -1.06% |
| bls | SPX | rise | +0.74% / +1.15% / -0.14% | -0.36% / +5.89% / +1.23% |
