# T1 — exposure dial, Test A

*Run 2026-10-07 23:40. Registered in `docs/prereg_exposure_dial.md`. Five model ETFs, 2006-01-03 → 2026-10-07; target 10%, EWMA λ 0.94, γ 3, confirm 3, band 0.05, lag 2; 10,000 bootstrap resamples, 10,000 label shifts; EFFR from the FRED cache; variant 4 NOT RUN — the frozen pipeline exposes labels, not posteriors (amendment to be recorded).*

## SPY

| variant | CER gross | CER 1× | CER 3× | Sharpe 1× | max DD (log) | turnover /yr |
|---|---|---|---|---|---|---|
| 1 | +0.0331 | +0.0331 | +0.0331 | 0.46 | -0.833 | 0.00 |
| 2 | +0.0431 | +0.0423 | +0.0408 | 0.57 | -0.292 | 2.49 |
| 3 | +0.0432 | +0.0424 | +0.0409 | 0.57 | -0.293 | 2.55 |

| comparison | CER diff 1× | 95% interval | first half | second half | stability | shift-null p | verdict |
|---|---|---|---|---|---|---|---|
| (i) 2 vs 1 | +0.0092 | [-0.0372, +0.0640] | +0.0293 | -0.0135 | -0.46 | — | **INCONCLUSIVE** |
| (ii) 3 vs 2 | +0.0001 | [-0.0039, +0.0040] | -0.0006 | +0.0009 | -1.48 | 0.532 | **INCONCLUSIVE** |

## TLT

| variant | CER gross | CER 1× | CER 3× | Sharpe 1× | max DD (log) | turnover /yr |
|---|---|---|---|---|---|---|
| 1 | -0.0273 | -0.0273 | -0.0273 | 0.04 | -0.801 | 0.00 |
| 2 | -0.0090 | -0.0096 | -0.0109 | 0.05 | -0.573 | 2.17 |
| 3 | -0.0086 | -0.0093 | -0.0105 | 0.06 | -0.562 | 2.10 |

| comparison | CER diff 1× | 95% interval | first half | second half | stability | shift-null p | verdict |
|---|---|---|---|---|---|---|---|
| (i) 2 vs 1 | +0.0177 | [-0.0056, +0.0396] | +0.0018 | +0.0357 | 20.28 | — | **INCONCLUSIVE** |
| (ii) 3 vs 2 | +0.0003 | [-0.0025, +0.0032] | -0.0015 | +0.0024 | -1.60 | 0.413 | **INCONCLUSIVE** |

## GLD

| variant | CER gross | CER 1× | CER 3× | Sharpe 1× | max DD (log) | turnover /yr |
|---|---|---|---|---|---|---|
| 1 | +0.0260 | +0.0260 | +0.0260 | 0.42 | -0.613 | 0.00 |
| 2 | +0.0335 | +0.0328 | +0.0313 | 0.47 | -0.483 | 2.49 |
| 3 | +0.0321 | +0.0313 | +0.0298 | 0.46 | -0.493 | 2.64 |

| comparison | CER diff 1× | 95% interval | first half | second half | stability | shift-null p | verdict |
|---|---|---|---|---|---|---|---|
| (i) 2 vs 1 | +0.0068 | [-0.0280, +0.0425] | +0.0124 | +0.0004 | 0.04 | — | **INCONCLUSIVE** |
| (ii) 3 vs 2 | -0.0014 | [-0.0058, +0.0031] | -0.0011 | -0.0018 | 1.62 | 0.724 | **FAIL** |

## UUP

| variant | CER gross | CER 1× | CER 3× | Sharpe 1× | max DD (log) | turnover /yr |
|---|---|---|---|---|---|---|
| 1 | -0.0082 | -0.0082 | -0.0082 | 0.02 | -0.255 | 0.00 |
| 2 | -0.0069 | -0.0072 | -0.0077 | 0.01 | -0.250 | 0.54 |
| 3 | -0.0069 | -0.0071 | -0.0076 | 0.01 | -0.243 | 0.53 |

| comparison | CER diff 1× | 95% interval | first half | second half | stability | shift-null p | verdict |
|---|---|---|---|---|---|---|---|
| (i) 2 vs 1 | +0.0010 | [-0.0039, +0.0055] | +0.0008 | +0.0012 | 1.51 | — | **INCONCLUSIVE** |
| (ii) 3 vs 2 | +0.0001 | [-0.0018, +0.0021] | -0.0001 | +0.0003 | -2.08 | 0.651 | **INCONCLUSIVE** |

## USO

| variant | CER gross | CER 1× | CER 3× | Sharpe 1× | max DD (log) | turnover /yr |
|---|---|---|---|---|---|---|
| 1 | -0.2937 | -0.2937 | -0.2937 | -0.22 | -4.082 | 0.00 |
| 2 | -0.0393 | -0.0399 | -0.0411 | -0.22 | -1.007 | 1.16 |
| 3 | -0.0414 | -0.0420 | -0.0432 | -0.23 | -1.065 | 1.22 |

| comparison | CER diff 1× | 95% interval | first half | second half | stability | shift-null p | verdict |
|---|---|---|---|---|---|---|---|
| (i) 2 vs 1 | +0.2538 | [+0.0942, +0.4450] | +0.2898 | +0.2140 | 0.74 | — | **PASS** |
| (ii) 3 vs 2 | -0.0021 | [-0.0067, +0.0024] | -0.0058 | +0.0020 | -0.34 | 0.511 | **FAIL** |

## Tree-level verdict (prereg §5)

- (i) vol targeting enters the product: **NO** — PASS on 1 of 5 (USO). Registered prior: PASS on SPY and USO.
- (ii) regime tilt enters the product: **NO** — PASS on 0 of 5 (none). Registered prior: INCONCLUSIVE/FAIL on all five.
