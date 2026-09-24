# Report-level scoreboard — backfill 48a6c4e879a1_n2617

*Generated 2026-09-24 15:54:10 +0800. Registered in `docs/prereg_report_scoreboard.md`. Primary horizon h*=3; minimum 30 non-overlap rows before any figure is printed. Only the primary cell is tested; every other cell and every breakdown is reported, not tested.*

## Coverage — before any metric

- report dates scored: **1532**
- dates with ≥1 document: 806
- dates with ≥1 net view (a call): 597
- per (date, asset): abstain 835, call 1060, divergence 45, no_document 5720

| asset | call | no_document | abstain | divergence | zero_direction | tiers (1/2/3) |
|---|---|---|---|---|---|---|
| GLD | 117 | 1245 | 168 | 2 | 0 | 1/47/69 |
| SPY | 517 | 755 | 226 | 34 | 0 | 0/20/497 |
| TLT | 186 | 1178 | 164 | 4 | 0 | 3/31/152 |
| USO | 108 | 1307 | 117 | 0 | 0 | 0/8/100 |
| UUP | 132 | 1235 | 160 | 5 | 0 | 9/68/55 |

## Verdict (primary cell, h*=3, close-to-close, non-overlap)

**FAIL**

## Cells

| cell | rows (naive / non-overlap) | hit-rate (naive / non-overlap) | asymmetry | mean signed | null q95 | p | asym 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| h3_primary **(primary)** | 1060 / 354 | 57.5% / 58.2% | 0.880 | 0.1206% | 58.8% | 0.0879 | [0.710, 1.141] | FAIL |
| h3_tradeable | 1059 / 354 | 53.5% / 54.2% | 1.192 | 0.2160% | — | — | — | reported, not tested |
| h5_primary | 1055 / 214 | 55.5% / 61.2% | 0.945 | 0.3260% | — | — | — | reported, not tested |
| h5_tradeable | 1055 / 214 | 51.0% / 50.5% | 1.357 | 0.2765% | — | — | — | reported, not tested |
| h20_primary | 1055 / 55 | 55.9% / 60.0% | 1.505 | 1.2021% | — | — | — | reported, not tested |
| h20_tradeable | 1055 / 55 | 57.1% / 65.5% | 1.326 | 1.3917% | — | — | — | reported, not tested |

## Breakdowns at h*=3 (close-to-close, non-overlap) — reported, not tested

### by asset

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| GLD | 39 | 61.5% | 1.303 | 0.4433% |
| SPY | 173 | 61.8% | 0.859 | 0.1863% |
| TLT | 62 | 53.2% | 0.845 | -0.0193% |
| USO | 36 | 55.6% | 0.748 | -0.0877% |
| UUP | 44 | 50.0% | 0.792 | -0.0558% |

### by tier

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 1.0 | 5 | too few | — | — |
| 2.0 | 60 | 53.3% | 0.494 | -0.2857% |
| 3.0 | 293 | 58.7% | 1.001 | 0.2124% |

### by dominant_source

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| earnings_8k | 120 | 65.8% | 1.180 | 0.4538% |
| fomc_minutes | 77 | 53.2% | 1.110 | 0.1419% |
| fomc_statement | 80 | 52.5% | 0.838 | -0.0647% |
| political_order | 84 | 48.8% | 0.806 | -0.1612% |
| political_other | 1 | too few | — | — |

### by regime

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 0 | 95 | 61.1% | 0.641 | 0.0022% |
| 1 | 54 | 59.3% | 0.749 | 0.0540% |
| 2 | 83 | 57.8% | 1.187 | 0.2881% |
| 3 | 130 | 56.2% | 0.994 | 0.1617% |
