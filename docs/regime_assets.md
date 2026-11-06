# R5 — the environment → favoured-asset map, and whether it holds out of sample

Annualised Sharpe of each asset inside each regime (confirmed labels). Stability = rank correlation of the asset ranking between the first and second half of each regime's own sessions, averaged; null = labels permuted in 60-session blocks.

| regime | SPY | TLT | GLD | UUP | USO |
|---|---|---|---|---|---|
| 0 | +0.35 | +0.34 | +0.09 | +0.22 | -0.53 |
| 1 | +1.23 | -0.05 | +0.67 | -0.46 | +0.37 |
| 2 | +0.13 | -0.05 | +0.82 | +0.86 | -0.66 |
| 3 | +0.90 | +0.12 | +0.71 | +0.76 | +0.70 |

Ranking stability first half vs second half: **+0.25** (null 95th percentile +0.42, p 0.193). A map that holds (p < 0.05) is a discretionary input: 'in this season, these assets have led'. One that does not is a description of the past.
