# N1 v3d — is the effect on the document's release day, and does it fade?

Span after day 0 in this file: days +1..+1 (the columns headed +1..+5 below are over this span).

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
| all | SOX | fall | 531 | 354 | +0.169 | 0.0040 | +0.214 | 0.0195 | -0.045 | 0.7425 | +0.020 | 0.6155 |
| all | SOX | rise | 476 | 343 | +0.092 | 0.0760 | +0.124 | 0.0960 | -0.032 | 0.6855 | +0.032 | 0.4285 |
| all | SPX | fall | 137 | 71 | +0.047 | 0.3680 | +0.115 | 0.3195 | -0.068 | 0.6640 | +0.055 | 0.5610 |
| all | SPX | rise | 81 | 55 | -0.029 | 0.5775 | +0.032 | 0.4585 | -0.061 | 0.6365 | +0.025 | 0.7985 |
| fed | SOX | fall | 194 | 134 | +0.382 | 0.0005 | +0.404 | 0.0070 | -0.022 | 0.5670 | +0.073 | 0.3240 |
| fed | SOX | rise | 178 | 129 | +0.214 | 0.0170 | +0.328 | 0.0135 | -0.114 | 0.8595 | +0.028 | 0.6700 |
| fed | SPX | fall | 54 | 27 | +0.385 | 0.0390 | +0.349 | 0.1890 | +0.037 | 0.4505 | -0.083 | 0.5235 |
| bls | SOX | fall | 387 | 255 | +0.123 | 0.0545 | +0.188 | 0.0610 | -0.065 | 0.8020 | -0.016 | 0.7420 |
| bls | SOX | rise | 349 | 250 | +0.061 | 0.2030 | +0.071 | 0.2710 | -0.010 | 0.5555 | +0.039 | 0.4160 |
| bls | SPX | fall | 101 | 52 | -0.067 | 0.6615 | -0.015 | 0.5315 | -0.052 | 0.6055 | +0.128 | 0.2395 |
| bls | SPX | rise | 59 | 42 | -0.010 | 0.5005 | +0.037 | 0.4555 | -0.046 | 0.5825 | -0.010 | 0.9425 |

## Returns by third of the score (lowest / middle / highest)

| family | index | direction | day 0 | days +1..+5 cumulative |
|---|---|---|---|---|
| all | SOX | fall | -0.40% / -0.28% / +0.70% | +0.38% / -0.48% / +0.01% |
| all | SOX | rise | -0.25% / -0.18% / +0.23% | -0.15% / +0.32% / -0.50% |
| all | SPX | fall | -0.35% / -2.41% / +0.34% | +1.25% / -1.37% / -0.93% |
| all | SPX | rise | +1.10% / +0.51% / +0.91% | -0.16% / +2.55% / -0.56% |
| fed | SOX | fall | -2.93% / -0.30% / +0.83% | +0.61% / +0.50% / +0.49% |
| fed | SOX | rise | -0.54% / -0.03% / +0.85% | +0.35% / +0.00% / -1.06% |
| fed | SPX | fall | -5.04% / -2.63% / +0.20% | +0.26% / +0.45% / +0.23% |
| bls | SOX | fall | +0.08% / -0.15% / +0.82% | +0.24% / -1.15% / -0.13% |
| bls | SOX | rise | -0.32% / -0.24% / -0.14% | -0.33% / +0.73% / -0.16% |
| bls | SPX | fall | +0.39% / -1.48% / -0.42% | +1.05% / -2.60% / -1.29% |
| bls | SPX | rise | +0.74% / +1.15% / -0.14% | +0.71% / +3.65% / -0.92% |
