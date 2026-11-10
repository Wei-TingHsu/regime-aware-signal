# N1 v3 — does the SIZE of the reversal line up with the contradiction score?

Reversal return = −event sign × the next h sessions' return (positive = prices went back). rank_corr = Spearman correlation with the strongest contradiction score in the window, among events that had a document in the window; p from 1,000 shuffles. The last two columns: mean contradiction score in the largest quarter of reversals vs the rest.

| index | direction | window | h | n | rank corr | p | contra, big reversals | contra, rest |
|---|---|---|---|---|---|---|---|---|
| SOX | fall | 3 | 1 | 102 | +0.17 | 0.100 | +0.13 | -0.09 |
| SOX | fall | 3 | 3 | 102 | +0.22 | 0.033 | +0.10 | -0.08 |
| SOX | fall | 3 | 5 | 101 | +0.17 | 0.097 | +0.15 | -0.12 |
| SOX | fall | 3 | 10 | 100 | +0.13 | 0.185 | +0.06 | -0.09 |
| SOX | fall | 5 | 1 | 122 | +0.14 | 0.107 | +0.30 | +0.06 |
| SOX | fall | 5 | 3 | 122 | +0.13 | 0.164 | +0.25 | +0.08 |
| SOX | fall | 5 | 5 | 121 | +0.16 | 0.080 | +0.24 | +0.07 |
| SOX | fall | 5 | 10 | 120 | +0.15 | 0.109 | +0.18 | +0.09 |
| SOX | fall | 10 | 1 | 149 | +0.13 | 0.115 | +0.47 | +0.26 |
| SOX | fall | 10 | 3 | 149 | -0.04 | 0.672 | +0.34 | +0.31 |
| SOX | fall | 10 | 5 | 148 | -0.03 | 0.755 | +0.31 | +0.31 |
| SOX | fall | 10 | 10 | 147 | +0.05 | 0.529 | +0.40 | +0.27 |
| SOX | rise | 3 | 1 | 97 | +0.11 | 0.301 | +0.43 | +0.25 |
| SOX | rise | 3 | 3 | 97 | +0.12 | 0.253 | +0.43 | +0.26 |
| SOX | rise | 3 | 5 | 97 | -0.04 | 0.724 | +0.39 | +0.27 |
| SOX | rise | 3 | 10 | 97 | +0.05 | 0.616 | +0.38 | +0.27 |
| SOX | rise | 5 | 1 | 116 | +0.18 | 0.043 | +0.48 | +0.26 |
| SOX | rise | 5 | 3 | 116 | +0.09 | 0.301 | +0.43 | +0.28 |
| SOX | rise | 5 | 5 | 116 | +0.08 | 0.384 | +0.52 | +0.25 |
| SOX | rise | 5 | 10 | 116 | +0.16 | 0.076 | +0.44 | +0.27 |
| SOX | rise | 10 | 1 | 134 | +0.12 | 0.177 | +0.69 | +0.50 |
| SOX | rise | 10 | 3 | 134 | +0.13 | 0.136 | +0.71 | +0.49 |
| SOX | rise | 10 | 5 | 134 | +0.20 | 0.017 | +0.76 | +0.47 |
| SOX | rise | 10 | 10 | 134 | +0.24 | 0.008 | +0.76 | +0.47 |
| SPX | fall | 5 | 1 | 35 | -0.05 | 0.796 | +0.02 | +0.21 |
| SPX | fall | 5 | 3 | 35 | +0.18 | 0.344 | +0.38 | +0.09 |
| SPX | fall | 5 | 5 | 34 | +0.23 | 0.182 | +0.26 | +0.10 |
| SPX | fall | 5 | 10 | 34 | +0.20 | 0.251 | +0.09 | +0.16 |
| SPX | fall | 10 | 1 | 40 | -0.09 | 0.562 | +0.27 | +0.43 |
| SPX | fall | 10 | 3 | 40 | -0.11 | 0.509 | +0.41 | +0.38 |
| SPX | fall | 10 | 5 | 39 | -0.12 | 0.439 | +0.31 | +0.40 |
| SPX | fall | 10 | 10 | 39 | -0.05 | 0.781 | +0.33 | +0.39 |

Cells with p < 0.05: 4 of 32; about 1.6 expected by chance.
