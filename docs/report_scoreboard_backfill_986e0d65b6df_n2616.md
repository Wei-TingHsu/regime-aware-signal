# Report-level scoreboard — backfill 986e0d65b6df_n2616

*Generated 2026-09-14 14:30:20 +0800. Registered in `docs/prereg_report_scoreboard.md`. Primary horizon h*=3; minimum 30 non-overlap rows before any figure is printed. Only the primary cell is tested; every other cell and every breakdown is reported, not tested.*

## Coverage — before any metric

- report dates scored: **1531**
- dates with ≥1 document: 803
- dates with ≥1 net view (a call): 585
- per (date, asset): abstain 844, call 1026, divergence 51, no_document 5734

| asset | call | no_document | abstain | divergence | zero_direction | tiers (1/2/3) |
|---|---|---|---|---|---|---|
| GLD | 112 | 1248 | 168 | 3 | 0 | 0/65/47 |
| SPY | 511 | 756 | 229 | 35 | 0 | 0/15/496 |
| TLT | 172 | 1184 | 168 | 7 | 0 | 1/48/123 |
| USO | 106 | 1304 | 121 | 0 | 0 | 0/3/103 |
| UUP | 125 | 1242 | 158 | 6 | 0 | 15/65/45 |

## Verdict (primary cell, h*=3, close-to-close, non-overlap)

**INCONCLUSIVE**

## Cells

| cell | rows (naive / non-overlap) | hit-rate (naive / non-overlap) | asymmetry | mean signed | null q95 | p | asym 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| h3_primary **(primary)** | 1026 / 345 | 56.5% / 59.4% | 1.116 | 0.3111% | 59.1% | 0.0497 | [0.910, 1.402] | INCONCLUSIVE |
| h3_tradeable | 1026 / 345 | 52.0% / 57.1% | 1.194 | 0.3183% | — | — | — | reported, not tested |
| h5_primary | 1026 / 208 | 54.3% / 54.3% | 0.895 | 0.0506% | — | — | — | reported, not tested |
| h5_tradeable | 1026 / 208 | 49.8% / 49.5% | 0.963 | -0.0476% | — | — | — | reported, not tested |
| h20_primary | 1020 / 54 | 55.6% / 59.3% | 1.321 | 1.2542% | — | — | — | reported, not tested |
| h20_tradeable | 1020 / 54 | 56.7% / 61.1% | 0.979 | 0.8939% | — | — | — | reported, not tested |

## Breakdowns at h*=3 (close-to-close, non-overlap) — reported, not tested

### by asset

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| GLD | 38 | 44.7% | 0.960 | -0.2146% |
| SPY | 171 | 68.4% | 1.052 | 0.4406% |
| TLT | 58 | 53.4% | 0.871 | 0.0003% |
| USO | 36 | 55.6% | 2.391 | 1.2582% |
| UUP | 42 | 47.6% | 0.666 | -0.1234% |

### by tier

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 1.0 | 6 | too few | — | — |
| 2.0 | 66 | 51.5% | 0.790 | -0.0912% |
| 3.0 | 273 | 57.5% | 1.063 | 0.2379% |

### by dominant_source

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| earnings_8k | 117 | 62.4% | 0.940 | 0.2286% |
| fomc_minutes | 74 | 37.8% | 0.983 | -0.3130% |
| fomc_statement | 73 | 54.8% | 0.698 | -0.1087% |
| political_order | 82 | 53.7% | 1.037 | 0.0981% |
| political_other | 1 | too few | — | — |

### by regime

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 0 | 92 | 58.7% | 1.322 | 0.4028% |
| 1 | 50 | 66.0% | 1.376 | 0.5355% |
| 2 | 78 | 60.3% | 0.723 | 0.0649% |
| 3 | 127 | 55.1% | 0.960 | 0.1006% |
