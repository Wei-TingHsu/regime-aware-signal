# Backtest evidence — the six items in §3.3

*Run 2026-08-28 13:28:35 +0800. 200 permutations. Nothing in `src/analog_backtest.py` was changed; the walk-forward, expanding refit, kernel and recency decay are reproduced identically.*

## The one table

| | ALL 47 | LONG-HISTORY 35 |
|---|---|---|
| Rebalances (effective n) | 837 | 837 |
| First out-of-sample | 2010-01-04 | 2010-01-04 |
| Last out-of-sample | 2026-08-18 | 2026-08-18 |
| Gross weekly spread | +0.295% | +0.129% |
| Gross Sharpe (annualised) | +0.51 | +0.25 |
| Long-leg turnover per rebalance | 23% | 24% |
| Short-leg turnover per rebalance | 25% | 25% |
| Break-even cost (bps/side) | 60.6 | 26.3 |
| Long-only Sharpe | +0.83 | +0.71 |
| iid Sharpe t | 2.04 | 0.99 |
| Block-permutation p | 0.0448 | 0.1841 |
| Exceedances | 8 | 36 |

## Net of costs

| cost per side | ALL net Sharpe | LONG-HISTORY net Sharpe |
|---|---|---|
| 0 bps | +0.51 | +0.25 |
| 5 bps | +0.47 | +0.20 |
| 10 bps | +0.43 | +0.15 |
| 20 bps | +0.34 | +0.06 |
| 50 bps | +0.09 | -0.22 |

## Short-leg borrow

| borrow (bps/yr) | ALL net Sharpe | LONG-HISTORY net Sharpe |
|---|---|---|
| 0 | +0.51 | +0.25 |
| 50 | +0.49 | +0.23 |
| 100 | +0.48 | +0.21 |
| 300 | +0.41 | +0.14 |

## Family-level test

54 grid cells. Best observed Sharpe **+0.73** at H=5, N=5, topk=200, σ=2.0. Under the block-sign null the BEST cell averages +0.56 with a 95th percentile of +0.77. Exceedances 17 of 200; **family p = 0.0896**.

The grid-selected model's own p-value is not evidence after selection. This is the test that is.

## What is still not claimed

- **Market impact is not modelled.** The cost ladder is a spread and commission drag applied to measured turnover, nothing more.
- **Capacity is unresolved.** Dollar-volume history is not in this repository; the names ever held are listed in the JSON so the constraint can be computed once volume data is pulled.
- **Borrow is a flat annualised rate**, not security-by-security. A historical borrow curve per name is not available here and inventing one would be worse than saying so.

