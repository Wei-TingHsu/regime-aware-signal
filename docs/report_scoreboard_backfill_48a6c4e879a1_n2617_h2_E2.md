# Report-level scoreboard — backfill 48a6c4e879a1_n2617_h2_E2

*Generated 2026-10-10 18:35:16 +0800. Registered in `docs/prereg_report_scoreboard.md`. Primary horizon h*=2; minimum 30 non-overlap rows before any figure is printed. Only the primary cell is tested; every other cell and every breakdown is reported, not tested.*

## Coverage — before any metric

- report dates scored: **1532**
- dates with ≥1 document: 557
- dates with ≥1 net view (a call): 415
- per (date, asset): abstain 605, call 755, divergence 18, no_document 6282

| asset | call | no_document | abstain | divergence | zero_direction | tiers (1/2/3) |
|---|---|---|---|---|---|---|
| GLD | 88 | 1317 | 126 | 1 | 0 | 2/40/46 |
| SPY | 365 | 996 | 158 | 13 | 0 | 17/28/320 |
| TLT | 133 | 1275 | 121 | 3 | 0 | 2/52/79 |
| USO | 74 | 1375 | 83 | 0 | 0 | 5/34/35 |
| UUP | 95 | 1319 | 117 | 1 | 0 | 3/12/80 |

## Verdict (primary cell, h*=2, close-to-close, non-overlap)

**FAIL**

## Cells

| cell | rows (naive / non-overlap) | hit-rate (naive / non-overlap) | asymmetry | mean signed | null q95 | p | asym 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| h2_primary **(primary)** | 755 / 379 | 55.0% / 54.1% | 1.056 | 0.1159% | 55.9% | 0.2084 | [0.866, 1.314] | FAIL |
| h2_tradeable | 755 / 379 | 52.8% / 52.0% | 1.044 | 0.0697% | — | — | — | reported, not tested |
| h3_primary | 755 / 254 | 55.9% / 57.9% | 1.186 | 0.2791% | — | — | — | reported, not tested |
| h3_tradeable | 755 / 254 | 52.5% / 53.5% | 1.138 | 0.1803% | — | — | — | reported, not tested |
| h5_primary | 755 / 152 | 52.8% / 54.6% | 1.156 | 0.2670% | — | — | — | reported, not tested |
| h5_tradeable | 755 / 152 | 49.3% / 52.6% | 1.193 | 0.2179% | — | — | — | reported, not tested |
| h20_primary | 750 / 40 | 56.8% / 55.0% | 1.619 | 0.8037% | — | — | — | reported, not tested |
| h20_tradeable | 750 / 40 | 59.1% / 57.5% | 1.018 | 0.4463% | — | — | — | reported, not tested |

## Breakdowns at h*=2 (close-to-close, non-overlap) — reported, not tested

### by asset

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| GLD | 44 | 54.5% | 1.263 | 0.2608% |
| SPY | 183 | 54.1% | 1.260 | 0.2061% |
| TLT | 67 | 59.7% | 0.875 | 0.1128% |
| USO | 37 | 45.9% | 0.772 | -0.4004% |
| UUP | 48 | 52.1% | 1.078 | 0.0416% |

### by tier

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 1.0 | 16 | too few | — | — |
| 2.0 | 83 | 54.2% | 1.167 | 0.1843% |
| 3.0 | 281 | 56.9% | 0.939 | 0.1035% |

### by dominant_source

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| earnings_8k | 146 | 59.6% | 1.001 | 0.1841% |
| fomc_minutes | 83 | 57.8% | 0.929 | 0.1161% |
| fomc_statement | 78 | 48.7% | 0.625 | -0.2929% |
| political_order | 74 | 48.6% | 0.884 | -0.0866% |
| political_other | 2 | too few | — | — |

### by regime

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 0 | 101 | 53.5% | 0.635 | -0.1561% |
| 1 | 50 | 52.0% | 0.640 | -0.1703% |
| 2 | 91 | 53.8% | 0.818 | -0.0234% |
| 3 | 140 | 56.4% | 1.131 | 0.1865% |
