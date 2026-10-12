# T1 — exposure dial, Test A

*Run 2026-10-13 01:19. Registered in `docs/prereg_exposure_dial.md`. Five model ETFs, 2006-01-03 → 2026-10-12; target 10%, EWMA λ 0.94, γ 3, confirm 3, band 0.05, lag 2; 10,000 bootstrap resamples, 10,000 label shifts; EFFR from the FRED cache; variant 4 NOT RUN — the frozen pipeline exposes labels, not posteriors (amendment to be recorded).*

## SPY

| variant | CER gross | CER 1× | CER 3× | Sharpe 1× | max DD (log) | turnover /yr |
|---|---|---|---|---|---|---|
| 1 | +0.0333 | +0.0333 | +0.0333 | 0.46 | -0.833 | 0.00 |
| 2 | +0.0432 | +0.0425 | +0.0410 | 0.57 | -0.292 | 2.49 |
| 3 | +0.0433 | +0.0426 | +0.0410 | 0.57 | -0.293 | 2.55 |

| comparison | CER diff 1× | 95% interval | first half | second half | stability | shift-null p | verdict |
|---|---|---|---|---|---|---|---|
| (i) 2 vs 1 | +0.0092 | [-0.0373, +0.0660] | +0.0293 | -0.0135 | -0.46 | — | **INCONCLUSIVE** |
| (ii) 3 vs 2 | +0.0001 | [-0.0039, +0.0040] | -0.0005 | +0.0008 | -1.52 | 0.525 | **INCONCLUSIVE** |

## TLT

| variant | CER gross | CER 1× | CER 3× | Sharpe 1× | max DD (log) | turnover /yr |
|---|---|---|---|---|---|---|
| 1 | -0.0264 | -0.0264 | -0.0264 | 0.04 | -0.792 | 0.00 |
| 2 | -0.0081 | -0.0087 | -0.0100 | 0.06 | -0.565 | 2.17 |
| 3 | -0.0075 | -0.0081 | -0.0094 | 0.07 | -0.546 | 2.11 |

| comparison | CER diff 1× | 95% interval | first half | second half | stability | shift-null p | verdict |
|---|---|---|---|---|---|---|---|
| (i) 2 vs 1 | +0.0176 | [-0.0053, +0.0401] | +0.0018 | +0.0355 | 20.18 | — | **INCONCLUSIVE** |
| (ii) 3 vs 2 | +0.0006 | [-0.0023, +0.0035] | -0.0016 | +0.0031 | -1.91 | 0.359 | **INCONCLUSIVE** |

## GLD

| variant | CER gross | CER 1× | CER 3× | Sharpe 1× | max DD (log) | turnover /yr |
|---|---|---|---|---|---|---|
| 1 | +0.0272 | +0.0272 | +0.0272 | 0.43 | -0.613 | 0.00 |
| 2 | +0.0340 | +0.0333 | +0.0318 | 0.48 | -0.483 | 2.48 |
| 3 | +0.0323 | +0.0316 | +0.0300 | 0.46 | -0.497 | 2.64 |

| comparison | CER diff 1× | 95% interval | first half | second half | stability | shift-null p | verdict |
|---|---|---|---|---|---|---|---|
| (i) 2 vs 1 | +0.0060 | [-0.0282, +0.0419] | +0.0124 | -0.0011 | -0.09 | — | **INCONCLUSIVE** |
| (ii) 3 vs 2 | -0.0017 | [-0.0061, +0.0028] | -0.0014 | -0.0021 | 1.49 | 0.739 | **FAIL** |

## UUP

| variant | CER gross | CER 1× | CER 3× | Sharpe 1× | max DD (log) | turnover /yr |
|---|---|---|---|---|---|---|
| 1 | -0.0083 | -0.0083 | -0.0083 | 0.02 | -0.255 | 0.00 |
| 2 | -0.0070 | -0.0073 | -0.0078 | 0.01 | -0.250 | 0.54 |
| 3 | -0.0070 | -0.0072 | -0.0077 | 0.01 | -0.243 | 0.53 |

| comparison | CER diff 1× | 95% interval | first half | second half | stability | shift-null p | verdict |
|---|---|---|---|---|---|---|---|
| (i) 2 vs 1 | +0.0010 | [-0.0040, +0.0056] | +0.0008 | +0.0012 | 1.52 | — | **INCONCLUSIVE** |
| (ii) 3 vs 2 | +0.0001 | [-0.0018, +0.0021] | -0.0001 | +0.0002 | -1.95 | 0.659 | **INCONCLUSIVE** |

## USO

| variant | CER gross | CER 1× | CER 3× | Sharpe 1× | max DD (log) | turnover /yr |
|---|---|---|---|---|---|---|
| 1 | -0.3288 | -0.3288 | -0.3288 | 0.01 | -2.870 | 0.00 |
| 2 | -0.0268 | -0.0273 | -0.0284 | -0.09 | -0.658 | 1.09 |
| 3 | -0.0255 | -0.0261 | -0.0272 | -0.08 | -0.681 | 1.14 |

| comparison | CER diff 1× | 95% interval | first half | second half | stability | shift-null p | verdict |
|---|---|---|---|---|---|---|---|
| (i) 2 vs 1 | +0.3015 | [+0.0865, +0.5823] | +0.2185 | +0.3949 | 1.81 | — | **PASS** |
| (ii) 3 vs 2 | +0.0012 | [-0.0052, +0.0084] | -0.0059 | +0.0092 | -1.58 | 0.310 | **INCONCLUSIVE** |

## Tree-level verdict (prereg §5)

- (i) vol targeting enters the product: **NO** — PASS on 1 of 5 (USO). Registered prior: PASS on SPY and USO.
- (ii) regime tilt enters the product: **NO** — PASS on 0 of 5 (none). Registered prior: INCONCLUSIVE/FAIL on all five.
