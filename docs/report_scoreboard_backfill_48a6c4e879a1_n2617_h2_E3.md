# Report-level scoreboard — backfill 48a6c4e879a1_n2617_h2_E3

*Generated 2026-10-10 18:10:56 +0800. Registered in `docs/prereg_report_scoreboard.md`. Primary horizon h*=2; minimum 30 non-overlap rows before any figure is printed. Only the primary cell is tested; every other cell and every breakdown is reported, not tested.*

## Coverage — before any metric

- report dates scored: **1532**
- dates with ≥1 document: 806
- dates with ≥1 net view (a call): 536
- per (date, asset): abstain 1151, call 752, divergence 37, no_document 5720

| asset | call | no_document | abstain | divergence | zero_direction | tiers (1/2/3) |
|---|---|---|---|---|---|---|
| GLD | 60 | 1245 | 224 | 3 | 0 | 0/7/53 |
| SPY | 452 | 755 | 296 | 29 | 0 | 0/0/452 |
| TLT | 93 | 1178 | 260 | 1 | 0 | 0/0/93 |
| USO | 60 | 1307 | 165 | 0 | 0 | 3/12/45 |
| UUP | 87 | 1235 | 206 | 4 | 0 | 1/4/82 |

## Verdict (primary cell, h*=2, close-to-close, non-overlap)

**FAIL**

## Cells

| cell | rows (naive / non-overlap) | hit-rate (naive / non-overlap) | asymmetry | mean signed | null q95 | p | asym 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| h2_primary **(primary)** | 752 / 377 | 57.2% / 54.6% | 0.852 | 0.0131% | 58.1% | 0.6292 | [0.696, 1.033] | FAIL |
| h2_tradeable | 752 / 377 | 57.3% / 55.7% | 0.907 | 0.0740% | — | — | — | reported, not tested |
| h3_primary | 752 / 251 | 61.2% / 57.8% | 0.787 | 0.0448% | — | — | — | reported, not tested |
| h3_tradeable | 752 / 251 | 55.9% / 54.6% | 0.955 | 0.0920% | — | — | — | reported, not tested |
| h5_primary | 752 / 152 | 57.6% / 60.5% | 1.030 | 0.3270% | — | — | — | reported, not tested |
| h5_tradeable | 752 / 152 | 54.1% / 55.3% | 1.243 | 0.3166% | — | — | — | reported, not tested |
| h20_primary | 750 / 39 | 61.2% / 46.2% | 1.240 | 0.0878% | — | — | — | reported, not tested |
| h20_tradeable | 750 / 39 | 62.5% / 53.8% | 1.034 | 0.2665% | — | — | — | reported, not tested |

## Breakdowns at h*=2 (close-to-close, non-overlap) — reported, not tested

### by asset

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| GLD | 30 | 46.7% | 0.581 | -0.4310% |
| SPY | 226 | 55.8% | 0.838 | 0.0245% |
| TLT | 47 | 53.2% | 1.190 | 0.1373% |
| USO | 30 | 53.3% | 0.837 | -0.0454% |
| UUP | 44 | 56.8% | 1.456 | 0.1641% |

### by tier

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 1.0 | 3 | too few | — | — |
| 2.0 | 12 | too few | — | — |
| 3.0 | 364 | 53.8% | 0.905 | 0.0269% |

### by dominant_source

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| earnings_8k | 154 | 63.6% | 1.155 | 0.3189% |
| fomc_minutes | 78 | 56.4% | 0.885 | 0.0632% |
| fomc_statement | 78 | 48.7% | 0.770 | -0.2001% |
| political_order | 69 | 58.0% | 1.203 | 0.1897% |
| political_other | 2 | too few | — | — |

### by regime

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 0 | 119 | 56.3% | 0.575 | -0.1365% |
| 1 | 57 | 61.4% | 0.762 | 0.1016% |
| 2 | 97 | 53.6% | 0.848 | -0.0095% |
| 3 | 109 | 59.6% | 0.905 | 0.1501% |
