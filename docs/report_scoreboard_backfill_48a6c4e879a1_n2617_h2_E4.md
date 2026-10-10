# Report-level scoreboard — backfill 48a6c4e879a1_n2617_h2_E4

*Generated 2026-10-09 23:47:11 +0800. Registered in `docs/prereg_report_scoreboard.md`. Primary horizon h*=2; minimum 30 non-overlap rows before any figure is printed. Only the primary cell is tested; every other cell and every breakdown is reported, not tested.*

## Coverage — before any metric

- report dates scored: **1532**
- dates with ≥1 document: 567
- dates with ≥1 net view (a call): 373
- per (date, asset): abstain 673, call 653, divergence 14, no_document 6320

| asset | call | no_document | abstain | divergence | zero_direction | tiers (1/2/3) |
|---|---|---|---|---|---|---|
| GLD | 107 | 1272 | 151 | 2 | 0 | 1/54/52 |
| SPY | 204 | 1192 | 129 | 7 | 0 | 13/21/170 |
| TLT | 154 | 1239 | 138 | 1 | 0 | 2/57/95 |
| USO | 65 | 1373 | 94 | 0 | 0 | 6/25/34 |
| UUP | 123 | 1244 | 161 | 4 | 0 | 3/29/91 |

## Verdict (primary cell, h*=2, close-to-close, non-overlap)

**FAIL**

## Cells

| cell | rows (naive / non-overlap) | hit-rate (naive / non-overlap) | asymmetry | mean signed | null q95 | p | asym 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| h2_primary **(primary)** | 653 / 328 | 52.8% / 54.3% | 1.128 | 0.1431% | 56.1% | 0.1907 | [0.899, 1.490] | FAIL |
| h2_tradeable | 653 / 328 | 52.7% / 54.0% | 1.133 | 0.1509% | — | — | — | reported, not tested |
| h3_primary | 653 / 219 | 55.0% / 53.0% | 1.080 | 0.1295% | — | — | — | reported, not tested |
| h3_tradeable | 653 / 219 | 51.1% / 48.9% | 1.097 | 0.0342% | — | — | — | reported, not tested |
| h5_primary | 653 / 132 | 52.5% / 54.5% | 1.334 | 0.3482% | — | — | — | reported, not tested |
| h5_tradeable | 653 / 132 | 49.0% / 56.1% | 1.562 | 0.5211% | — | — | — | reported, not tested |
| h20_primary | 649 / 36 | 54.4% / 50.0% | 2.469 | 2.3140% | — | — | — | reported, not tested |
| h20_tradeable | 649 / 36 | 55.8% / 55.6% | 1.939 | 2.1662% | — | — | — | reported, not tested |

## Breakdowns at h*=2 (close-to-close, non-overlap) — reported, not tested

### by asset

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| GLD | 54 | 48.1% | 1.596 | 0.2631% |
| SPY | 102 | 54.9% | 0.769 | -0.0281% |
| TLT | 77 | 53.2% | 1.152 | 0.1304% |
| USO | 33 | 63.6% | 0.913 | 0.4214% |
| UUP | 62 | 54.8% | 1.936 | 0.1881% |

### by tier

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 1.0 | 14 | too few | — | — |
| 2.0 | 95 | 53.7% | 1.261 | 0.1791% |
| 3.0 | 222 | 53.2% | 0.788 | -0.0551% |

### by dominant_source

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| earnings_8k | 63 | 50.8% | 0.846 | -0.0706% |
| fomc_minutes | 98 | 56.1% | 0.966 | 0.1034% |
| fomc_statement | 91 | 47.3% | 1.097 | -0.0112% |
| political_order | 76 | 50.0% | 1.073 | 0.0256% |
| political_other | 2 | too few | — | — |

### by regime

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 0 | 116 | 52.6% | 0.671 | -0.1596% |
| 1 | 44 | 54.5% | 0.758 | -0.0403% |
| 2 | 59 | 47.5% | 0.981 | -0.0734% |
| 3 | 111 | 48.6% | 1.300 | 0.1161% |
