# AI-chain news: design questions (overlapping signals; the size of the score)

Registered in TRACK 3.67 before running. The first test traded one unit in the direction of the SIGN of each score, every signal on its own, returns before cost. This file asks what that design left out.

## D0. How often do signals on the same stock disagree?

- **A company's own signals** (results and material events, from May 2018): 561 signals; pairs on the same stock within 60 minutes: 2; of these pointing opposite ways: 0.
- **Other companies' releases naming a stock** (after 16:00): 1661 stock-afternoons with at least one mention; 147 with two or more; of these with BOTH a positive and a negative direction for the same stock: 57 (39%).
- **A stock that reports AND is named by another reporter the same afternoon:** 87 cases; the other company's release points the opposite way to the stock's own results score in 24 (28%).

## D1. Does the size of the score matter?

### F2: own_stock; 1 min after the stamp, hold 60 min

Every signal with one unit: **+64.9 bp** (n 365), before cost.

| size of the score | trades | average | right on |
|---|---|---|---|
| 0.0 to 0.3 | 93 | +5.9 bp | 53% |
| 0.3 to 0.6 | 108 | -0.5 bp | 51% |
| 0.6 to 0.9 | 57 | +203.2 bp | 70% |
| 0.9 to 1.0 | 107 | +108.6 bp | 62% |

- Trade only scores of 0.5 or more: +97.4 bp (n 239). Only 0.8 or more: +137.5 bp (n 135).
- Position sized by the score (a score of 1.0 trades twice the size of 0.5): +93.5 bp per unit of position.
- Do larger scores earn more? Rank correlation between the size of the score and the trade's return: +0.142; shuffled sizes reach this in 0.4% of 5,000 tries -> **larger scores earn more** (bar 0.0125).

### F2: market; 5 min after the stamp, hold 30 min

Every signal with one unit: **+41.4 bp** (n 330), before cost.

| size of the score | trades | average | right on |
|---|---|---|---|
| 0.0 to 0.3 | 229 | +31.5 bp | 55% |
| 0.3 to 0.6 | 71 | +72.6 bp | 68% |
| 0.6 to 0.9 | 1 | -26.9 bp | 0% |
| 0.9 to 1.0 | 29 | +45.6 bp | 55% |

- Trade only scores of 0.5 or more: +60.2 bp (n 61). Only 0.8 or more: +45.6 bp (n 29).
- Position sized by the score (a score of 1.0 trades twice the size of 0.5): +41.7 bp per unit of position.
- Do larger scores earn more? Rank correlation between the size of the score and the trade's return: +0.015; shuffled sizes reach this in 40.3% of 5,000 tries -> **no evidence that larger scores earn more** (bar 0.0125).

### F1: results_vs_prior_guidance; 5 min after the stamp, to the next 09:35

Every signal with one unit: **+16.7 bp** (n 294), before cost.

| size of the score | trades | average | right on |
|---|---|---|---|
| 0.0 to 0.3 | 66 | +11.5 bp | 61% |
| 0.3 to 0.6 | 105 | +27.0 bp | 64% |
| 0.6 to 0.9 | 47 | +10.0 bp | 57% |
| 0.9 to 1.0 | 76 | +11.3 bp | 58% |

- Trade only scores of 0.5 or more: +17.0 bp (n 198). Only 0.8 or more: +10.9 bp (n 109).
- Position sized by the score (a score of 1.0 trades twice the size of 0.5): +15.7 bp per unit of position.
- Do larger scores earn more? Rank correlation between the size of the score and the trade's return: -0.002; shuffled sizes reach this in 51.8% of 5,000 tries -> **no evidence that larger scores earn more** (bar 0.0125).

### F4: own_stock | material 0.2+; next regular session, hold 60 min

Every signal with one unit: **+12.1 bp** (n 245), before cost.

| size of the score | trades | average | right on |
|---|---|---|---|
| 0.0 to 0.3 | 198 | +9.1 bp | 54% |
| 0.3 to 0.6 | 37 | +34.9 bp | 59% |
| 0.6 to 0.9 | 10 | -13.0 bp | 50% |
| 0.9 to 1.0 | 0 |  | |

- Trade only scores of 0.5 or more: +1.0 bp (n 29). Only 0.8 or more: -68.2 bp (n 6).
- Position sized by the score (a score of 1.0 trades twice the size of 0.5): +13.3 bp per unit of position.
- Do larger scores earn more? Rank correlation between the size of the score and the trade's return: +0.017; shuffled sizes reach this in 39.0% of 5,000 tries -> **no evidence that larger scores earn more** (bar 0.0125).

