# Report-level scoreboard — backfill 48a6c4e879a1_n2617_h2_E1

*Generated 2026-10-10 17:17:02 +0800. Registered in `docs/prereg_report_scoreboard.md`. Primary horizon h*=2; minimum 30 non-overlap rows before any figure is printed. Only the primary cell is tested; every other cell and every breakdown is reported, not tested.*

## Coverage — before any metric

- report dates scored: **1532**
- dates with ≥1 document: 806
- dates with ≥1 net view (a call): 246
- per (date, asset): abstain 1532, call 395, divergence 13, no_document 5720

| asset | call | no_document | abstain | divergence | zero_direction | tiers (1/2/3) |
|---|---|---|---|---|---|---|
| GLD | 60 | 1245 | 227 | 0 | 0 | 1/40/19 |
| SPY | 78 | 755 | 692 | 7 | 0 | 17/23/38 |
| TLT | 139 | 1178 | 212 | 3 | 0 | 2/60/77 |
| USO | 52 | 1307 | 173 | 0 | 0 | 3/16/33 |
| UUP | 66 | 1235 | 228 | 3 | 0 | 1/18/47 |

## Verdict (primary cell, h*=2, close-to-close, non-overlap)

**FAIL**

## Cells

| cell | rows (naive / non-overlap) | hit-rate (naive / non-overlap) | asymmetry | mean signed | null q95 | p | asym 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| h2_primary **(primary)** | 395 / 198 | 50.4% / 48.5% | 1.052 | -0.0055% | 54.5% | 0.9026 | [0.842, 1.383] | FAIL |
| h2_tradeable | 395 / 198 | 49.6% / 45.5% | 0.942 | -0.1395% | — | — | — | reported, not tested |
| h3_primary | 395 / 133 | 50.6% / 42.9% | 1.332 | -0.0009% | — | — | — | reported, not tested |
| h3_tradeable | 395 / 133 | 47.6% / 43.6% | 1.322 | 0.0156% | — | — | — | reported, not tested |
| h5_primary | 395 / 81 | 51.6% / 54.3% | 1.203 | 0.2870% | — | — | — | reported, not tested |
| h5_tradeable | 395 / 81 | 47.1% / 50.6% | 1.408 | 0.3256% | — | — | — | reported, not tested |
| h20_primary | 392 / 21 | too few to report | — | — | — | — | — | — |
| h20_tradeable | 392 / 21 | too few to report | — | — | — | — | — | — |

## Breakdowns at h*=2 (close-to-close, non-overlap) — reported, not tested

### by asset

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| GLD | 30 | 50.0% | 0.712 | -0.2092% |
| SPY | 39 | 41.0% | 1.458 | 0.0083% |
| TLT | 70 | 55.7% | 0.901 | 0.0638% |
| USO | 26 | too few | — | — |
| UUP | 33 | 36.4% | 1.381 | -0.0566% |

### by tier

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 1.0 | 14 | too few | — | — |
| 2.0 | 79 | 57.0% | 0.975 | 0.1358% |
| 3.0 | 109 | 49.5% | 0.782 | -0.1421% |

### by dominant_source

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| earnings_8k | 33 | 39.4% | 2.237 | 0.2442% |
| fomc_minutes | 59 | 61.0% | 1.435 | 0.3846% |
| fomc_statement | 56 | 44.6% | 1.077 | -0.0906% |
| political_order | 55 | 60.0% | 1.068 | 0.1970% |

### by regime

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 0 | 43 | 58.1% | 0.652 | -0.0569% |
| 1 | 29 | too few | — | — |
| 2 | 42 | 50.0% | 1.016 | 0.0096% |
| 3 | 88 | 48.9% | 1.348 | 0.1293% |
