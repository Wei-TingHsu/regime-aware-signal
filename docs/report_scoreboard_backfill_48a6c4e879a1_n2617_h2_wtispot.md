# Report-level scoreboard — backfill 48a6c4e879a1_n2617_h2_wtispot

*Generated 2026-10-12 13:44:54 +0800. Registered in `docs/prereg_report_scoreboard.md`. Primary horizon h*=2; minimum 30 non-overlap rows before any figure is printed. Only the primary cell is tested; every other cell and every breakdown is reported, not tested.*

## Coverage — before any metric

- report dates scored: **1532**
- dates with ≥1 document: 806
- dates with ≥1 net view (a call): 599
- per (date, asset): abstain 834, call 1060, divergence 46, no_document 5720

| asset | call | no_document | abstain | divergence | zero_direction | tiers (1/2/3) |
|---|---|---|---|---|---|---|
| GLD | 117 | 1245 | 167 | 3 | 0 | 2/60/55 |
| SPY | 521 | 755 | 222 | 34 | 0 | 21/46/454 |
| TLT | 187 | 1178 | 163 | 4 | 0 | 2/80/105 |
| USO | 105 | 1307 | 120 | 0 | 0 | 17/1/87 |
| UUP | 130 | 1235 | 162 | 5 | 0 | 3/29/98 |

## Verdict (primary cell, h*=2, close-to-close, non-overlap)

**FAIL**

## Cells

| cell | rows (naive / non-overlap) | hit-rate (naive / non-overlap) | asymmetry | mean signed | null q95 | p | asym 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| h2_primary **(primary)** | 1060 / 532 | 54.9% / 53.9% | 1.097 | 0.1249% | 57.3% | 0.6107 | [0.917, 1.334] | FAIL |
| h2_tradeable | 1060 / 532 | 54.5% / 55.1% | 1.023 | 0.1271% | — | — | — | reported, not tested |
| h3_primary | 1060 / 355 | 57.4% / 60.3% | 0.903 | 0.1949% | — | — | — | reported, not tested |
| h3_tradeable | 1060 / 355 | 53.6% / 56.3% | 1.067 | 0.2109% | — | — | — | reported, not tested |
| h5_primary | 1060 / 214 | 55.4% / 53.3% | 0.876 | -0.0015% | — | — | — | reported, not tested |
| h5_tradeable | 1060 / 214 | 51.1% / 51.4% | 0.975 | 0.0274% | — | — | — | reported, not tested |
| h20_primary | 1055 / 55 | 55.8% / 49.1% | 0.550 | -1.4179% | — | — | — | reported, not tested |
| h20_tradeable | 1055 / 55 | 57.1% / 50.9% | 0.531 | -1.3362% | — | — | — | reported, not tested |

## Breakdowns at h*=2 (close-to-close, non-overlap) — reported, not tested

### by asset

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| GLD | 59 | 45.8% | 0.970 | -0.1202% |
| SPY | 261 | 54.8% | 0.970 | 0.0769% |
| TLT | 94 | 58.5% | 1.099 | 0.1992% |
| USO | 53 | 56.6% | 1.434 | 0.5540% |
| UUP | 65 | 49.2% | 1.490 | 0.0825% |

### by tier

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 1.0 | 24 | too few | — | — |
| 2.0 | 109 | 53.2% | 1.759 | 0.3819% |
| 3.0 | 401 | 54.9% | 0.984 | 0.0918% |

### by dominant_source

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| earnings_8k | 178 | 60.7% | 1.069 | 0.2410% |
| fomc_minutes | 114 | 57.0% | 0.981 | 0.1203% |
| fomc_statement | 116 | 48.3% | 1.170 | 0.0513% |
| political_order | 124 | 50.0% | 1.137 | 0.0597% |
| political_other | 2 | too few | — | — |

### by regime

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 0 | 137 | 55.5% | 0.885 | 0.0403% |
| 1 | 82 | 53.7% | 0.641 | -0.1578% |
| 2 | 122 | 54.1% | 0.990 | 0.0881% |
| 3 | 194 | 53.6% | 0.944 | 0.0458% |
