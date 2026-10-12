# Report-level scoreboard — backfill 48a6c4e879a1_n2617_h2_wtifut

*Generated 2026-10-12 13:50:58 +0800. Registered in `docs/prereg_report_scoreboard.md`. Primary horizon h*=2; minimum 30 non-overlap rows before any figure is printed. Only the primary cell is tested; every other cell and every breakdown is reported, not tested.*

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
| USO | 109 | 1307 | 116 | 0 | 0 | 15/54/40 |
| UUP | 130 | 1235 | 162 | 5 | 0 | 3/29/98 |

## Verdict (primary cell, h*=2, close-to-close, non-overlap)

**FAIL**

## Cells

| cell | rows (naive / non-overlap) | hit-rate (naive / non-overlap) | asymmetry | mean signed | null q95 | p | asym 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| h2_primary **(primary)** | 1064 / 534 | 55.1% / 54.3% | 1.061 | 0.1174% | 57.3% | 0.5025 | [0.896, 1.296] | FAIL |
| h2_tradeable | 1064 / 534 | 54.4% / 54.9% | 1.007 | 0.1156% | — | — | — | reported, not tested |
| h3_primary | 1064 / 357 | 57.3% / 61.3% | 0.966 | 0.2654% | — | — | — | reported, not tested |
| h3_tradeable | 1064 / 357 | 53.5% / 57.1% | 1.160 | 0.2900% | — | — | — | reported, not tested |
| h5_primary | 1064 / 215 | 55.0% / 52.6% | 0.823 | -0.0794% | — | — | — | reported, not tested |
| h5_tradeable | 1064 / 215 | 51.1% / 51.2% | 0.901 | -0.0520% | — | — | — | reported, not tested |
| h20_primary | 1059 / 55 | 55.7% / 52.7% | 1.103 | 0.4557% | — | — | — | reported, not tested |
| h20_tradeable | 1059 / 55 | 57.0% / 56.4% | 1.007 | 0.5829% | — | — | — | reported, not tested |

## Breakdowns at h*=2 (close-to-close, non-overlap) — reported, not tested

### by asset

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| GLD | 59 | 45.8% | 0.970 | -0.1202% |
| SPY | 261 | 54.8% | 0.970 | 0.0769% |
| TLT | 94 | 58.5% | 1.099 | 0.1992% |
| USO | 55 | 60.0% | 1.089 | 0.4656% |
| UUP | 65 | 49.2% | 1.490 | 0.0825% |

### by tier

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 1.0 | 23 | too few | — | — |
| 2.0 | 135 | 53.3% | 1.365 | 0.2847% |
| 3.0 | 377 | 55.4% | 1.045 | 0.1326% |

### by dominant_source

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| earnings_8k | 178 | 61.2% | 1.046 | 0.2419% |
| fomc_minutes | 114 | 57.9% | 0.918 | 0.1106% |
| fomc_statement | 117 | 47.9% | 1.048 | -0.0238% |
| political_order | 125 | 51.2% | 1.060 | 0.0540% |
| political_other | 2 | too few | — | — |

### by regime

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 0 | 139 | 56.8% | 0.796 | 0.0208% |
| 1 | 82 | 53.7% | 0.631 | -0.1659% |
| 2 | 122 | 54.1% | 1.005 | 0.0958% |
| 3 | 194 | 54.1% | 0.941 | 0.0560% |
