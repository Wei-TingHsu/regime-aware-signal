# T13 A3c — how much the history supports holding

*2026-10-16. L_hist = min(5, 20% ÷ q90), q90 = 90th percentile of the unlevered worst interim loss over 60 sessions across p8 shocks, for a position in the direction of the pool's median f60 (short if negative: the loss of a short is the price's best gain). T1 exposure = min(1, 10% ÷ EWMA(0.94) vol) on the latest session. Two readings of 'capped by T1' (registration wording, founder to pick): (a) literal L = min(L_hist, T1) ≤ 1; (b) multiplier L = L_hist × T1. Not a guarantee: the next drawdown can exceed any past one.*

| market | direction (pool median f60) | median worst loss | q90 worst loss | L_hist | T1 exposure today | (a) min | (b) product | worst past case at (b) |
|---|---|---|---|---|---|---|---|---|
| SPY | long | 3.6% | 13.8% | 1.45× | 1.00 | 1.00× | 1.45× | 69.0% |
| TLT | short | 3.3% | 9.4% | 2.12× | 1.00 | 1.00× | 2.12× | 55.5% |
| GLD | long | 3.7% | 12.5% | 1.60× | 0.46 | 0.46× | 0.74× | 17.9% |
| UUP | long | 2.0% | 6.5% | 3.07× | 1.00 | 1.00× | 3.07× | 23.8% |
| USO | long | 8.9% | 31.8% | 0.63× | 0.26 | 0.26× | 0.16× | 15.2% |
| WTI_SPOT | long | 11.1% | 31.6% | 0.63× | 0.15 | 0.15× | 0.09× | 10.1% |

The leverage number is informational until A3b passes for that market (prereg §3b, app rule).
