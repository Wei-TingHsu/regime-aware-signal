# Report-level scoreboard — backfill 48a6c4e879a1_n2617_altinstr

*Generated 2026-09-29 16:13:14 +0800. Registered in `docs/prereg_report_scoreboard.md`. Primary horizon h*=3; minimum 30 non-overlap rows before any figure is printed. Only the primary cell is tested; every other cell and every breakdown is reported, not tested.*

## Coverage — before any metric

- report dates scored: **1532**
- dates with ≥1 document: 806
- dates with ≥1 net view (a call): 597
- per (date, asset): abstain 835, call 1060, divergence 45, no_document 5720

| asset | call | no_document | abstain | divergence | zero_direction | tiers (1/2/3) |
|---|---|---|---|---|---|---|
| GLD | 117 | 1245 | 168 | 2 | 0 | 1/51/65 |
| SPY | 517 | 755 | 226 | 34 | 0 | 0/18/499 |
| TLT | 186 | 1178 | 164 | 4 | 0 | 5/36/145 |
| USO | 108 | 1307 | 117 | 0 | 0 | 3/20/85 |
| UUP | 132 | 1235 | 160 | 5 | 0 | 26/56/50 |

## Verdict (primary cell, h*=3, close-to-close, non-overlap)

**FAIL**

## Cells

| cell | rows (naive / non-overlap) | hit-rate (naive / non-overlap) | asymmetry | mean signed | null q95 | p | asym 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| h3_primary **(primary)** | 1060 / 354 | 56.9% / 56.5% | 0.951 | 0.1195% | 57.6% | 0.1260 | [0.770, 1.255] | FAIL |
| h3_tradeable | 1060 / 354 | 53.6% / 54.2% | 1.192 | 0.2160% | — | — | — | reported, not tested |
| h5_primary | 1060 / 215 | 53.8% / 58.1% | 1.049 | 0.2862% | — | — | — | reported, not tested |
| h5_tradeable | 1055 / 214 | 51.1% / 51.4% | 1.307 | 0.2765% | — | — | — | reported, not tested |
| h20_primary | 1055 / 55 | 56.0% / 58.2% | 1.364 | 0.8889% | — | — | — | reported, not tested |
| h20_tradeable | 1055 / 55 | 57.1% / 65.5% | 1.326 | 1.3917% | — | — | — | reported, not tested |

## Breakdowns at h*=3 (close-to-close, non-overlap) — reported, not tested

### by asset

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| GLD | 39 | 61.5% | 1.148 | 0.4192% |
| SPY | 173 | 60.1% | 0.899 | 0.1710% |
| TLT | 62 | 56.5% | 0.770 | -0.0004% |
| USO | 36 | 47.2% | 1.095 | -0.0284% |
| UUP | 44 | 45.5% | 0.945 | -0.0589% |

### by tier

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 1.0 | 13 | too few | — | — |
| 2.0 | 61 | 52.5% | 0.906 | -0.0002% |
| 3.0 | 284 | 59.5% | 1.072 | 0.2783% |

### by dominant_source

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| earnings_8k | 120 | 65.0% | 1.278 | 0.4436% |
| fomc_minutes | 77 | 51.9% | 1.035 | 0.0644% |
| fomc_statement | 80 | 51.2% | 0.916 | -0.0277% |
| political_order | 84 | 52.4% | 0.678 | -0.1687% |
| political_other | 1 | too few | — | — |

### by regime

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 0 | 95 | 57.9% | 0.714 | -0.0085% |
| 1 | 54 | 59.3% | 0.745 | 0.0451% |
| 2 | 83 | 60.2% | 1.204 | 0.3425% |
| 3 | 130 | 54.6% | 1.065 | 0.1588% |
