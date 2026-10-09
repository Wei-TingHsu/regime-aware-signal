# Report-level scoreboard — backfill 48a6c4e879a1_n2617_h2

*Generated 2026-10-09 22:44:36 +0800. Registered in `docs/prereg_report_scoreboard.md`. Primary horizon h*=2; minimum 30 non-overlap rows before any figure is printed. Only the primary cell is tested; every other cell and every breakdown is reported, not tested.*

## Coverage — before any metric

- report dates scored: **1532**
- dates with ≥1 document: 806
- dates with ≥1 net view (a call): 602
- per (date, asset): abstain 830, call 1064, divergence 46, no_document 5720

| asset | call | no_document | abstain | divergence | zero_direction | tiers (1/2/3) |
|---|---|---|---|---|---|---|
| GLD | 117 | 1245 | 167 | 3 | 0 | 2/60/55 |
| SPY | 521 | 755 | 222 | 34 | 0 | 21/46/454 |
| TLT | 187 | 1178 | 163 | 4 | 0 | 2/80/105 |
| USO | 109 | 1307 | 116 | 0 | 0 | 6/53/50 |
| UUP | 130 | 1235 | 162 | 5 | 0 | 3/29/98 |

## Verdict (primary cell, h*=2, close-to-close, non-overlap)

**FAIL**

## Cells

| cell | rows (naive / non-overlap) | hit-rate (naive / non-overlap) | asymmetry | mean signed | null q95 | p | asym 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| h2_primary **(primary)** | 1064 / 534 | 55.2% / 54.9% | 1.008 | 0.1028% | 57.5% | 0.4003 | [0.853, 1.232] | FAIL |
| h2_tradeable | 1064 / 534 | 54.4% / 54.9% | 1.007 | 0.1156% | — | — | — | reported, not tested |
| h3_primary | 1064 / 357 | 57.3% / 61.3% | 0.969 | 0.2614% | — | — | — | reported, not tested |
| h3_tradeable | 1064 / 357 | 53.5% / 57.1% | 1.160 | 0.2900% | — | — | — | reported, not tested |
| h5_primary | 1064 / 215 | 55.5% / 53.0% | 0.831 | -0.0531% | — | — | — | reported, not tested |
| h5_tradeable | 1064 / 215 | 51.1% / 51.2% | 0.901 | -0.0520% | — | — | — | reported, not tested |
| h20_primary | 1059 / 55 | 55.8% / 52.7% | 1.114 | 0.4764% | — | — | — | reported, not tested |
| h20_tradeable | 1059 / 55 | 57.0% / 56.4% | 1.007 | 0.5829% | — | — | — | reported, not tested |

## Breakdowns at h*=2 (close-to-close, non-overlap) — reported, not tested

### by asset

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| GLD | 59 | 45.8% | 0.970 | -0.1202% |
| SPY | 261 | 54.8% | 0.970 | 0.0769% |
| TLT | 94 | 58.5% | 1.099 | 0.1992% |
| USO | 55 | 65.5% | 0.744 | 0.3243% |
| UUP | 65 | 49.2% | 1.490 | 0.0825% |

### by tier

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 1.0 | 18 | too few | — | — |
| 2.0 | 135 | 57.8% | 1.599 | 0.4550% |
| 3.0 | 382 | 55.8% | 1.046 | 0.1365% |

### by dominant_source

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| earnings_8k | 178 | 61.2% | 1.042 | 0.2403% |
| fomc_minutes | 114 | 58.8% | 0.901 | 0.1213% |
| fomc_statement | 117 | 48.7% | 1.039 | -0.0081% |
| political_order | 125 | 52.0% | 0.984 | 0.0325% |
| political_other | 2 | too few | — | — |

### by regime

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 0 | 139 | 57.6% | 0.769 | 0.0182% |
| 1 | 82 | 53.7% | 0.653 | -0.1486% |
| 2 | 122 | 54.1% | 0.955 | 0.0666% |
| 3 | 194 | 53.1% | 0.958 | 0.0435% |
