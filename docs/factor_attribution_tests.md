# Factor attribution — tests for GLD

*2026-10-23 00:30. T-A: betas from the prior 504 sessions, R² on each next 20-session block from 2006 (walk-forward, joint fit). Bar 0.20. T-B: sign of each factor's beta across rolling windows (step 63); stable if the same sign in ≥ 70%.*

**T-A:** median out-of-sample R² **0.177** over 235 blocks → **FAIL**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 235 | 54% | UNSTABLE — not quotable |
| rate-hike speculation (2-yr yield minus fed funds) | 235 | 66% | UNSTABLE — not quotable |
| real 10-yr yield | 235 | 63% | UNSTABLE — not quotable |
| US dollar (broad index) | 235 | 100% | stable |
| oil (WTI spot) | 235 | 90% | stable |
| equity volatility (VIX) | 235 | 59% | UNSTABLE — not quotable |
| macro state, PCA line 1 | 235 | 83% | stable |
| macro state, PCA line 2 | 235 | 88% | stable |
