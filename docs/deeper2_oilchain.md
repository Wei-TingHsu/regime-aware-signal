# Deeper test oilchain — 2026-11-05 20:54

226 oil shocks (GLD rows). The founder's chain, 5 Nov: oil up → inflation expectations → hawkish policy → higher real rates → gold down. Each link measured separately.

## D5b gold after an oil shock, conditioned on whether rates/real yields rose afterwards — net Sharpe (sign +1 long gold)

Best cell `{'h': 'f20', 'series': 'DFII10', 'rate_h': 20, 'rates': 'down', 'sign': 1}`: statistic +2.04 on n = 114; null 95th percentile +1.58; **p_family = 0.005**; survivors 4.

## Link 1 — do rates rise after an oil shock?

| series | horizon (sessions) | n | mean change (bp) | share up | t |
|---|---|---|---|---|---|
| DGS2 | 5 | 226 | -0.7 | 44% | -0.73 |
| DGS2 | 10 | 226 | +0.6 | 51% | +0.48 |
| DGS2 | 20 | 226 | +1.7 | 53% | +0.94 |
| DFII10 | 5 | 226 | +0.0 | 46% | +0.01 |
| DFII10 | 10 | 226 | +1.0 | 51% | +1.00 |
| DFII10 | 20 | 226 | +0.8 | 50% | +0.49 |

Link 2 (rates up → gold down) is the standing T9b/T-B result. Link 3 is the sweep above: gold after shocks where rates DID rise versus where they did not.

