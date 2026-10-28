# Report-level scoreboard — backfill 97d9bf07dd2c_n5793

*Generated 2026-10-28 04:11:10 +0800. Registered in `docs/prereg_report_scoreboard.md`. Primary horizon h*=2; minimum 30 non-overlap rows before any figure is printed. Only the primary cell is tested; every other cell and every breakdown is reported, not tested.*

## Coverage — before any metric

- report dates scored: **2486**
- dates with ≥1 document: 1085
- dates with ≥1 net view (a call): 860
- per (date, asset): abstain 826, call 1646, divergence 85, no_document 9873

| asset | call | no_document | abstain | divergence | zero_direction | tiers (1/2/3) |
|---|---|---|---|---|---|---|
| GLD | 209 | 2109 | 164 | 4 | 0 | 7/74/128 |
| SPY | 722 | 1481 | 223 | 60 | 0 | 0/69/653 |
| TLT | 316 | 2019 | 141 | 10 | 0 | 0/33/283 |
| USO | 189 | 2149 | 144 | 4 | 0 | 12/27/150 |
| UUP | 210 | 2115 | 154 | 7 | 0 | 0/20/190 |

## Verdict (primary cell, h*=2, close-to-close, non-overlap)

**FAIL**

## Cells

| cell | rows (naive / non-overlap) | hit-rate (naive / non-overlap) | asymmetry | mean signed | null q95 | p | asym 95% CI | verdict |
|---|---|---|---|---|---|---|---|---|
| h2_primary **(primary)** | 1646 / 824 | 55.3% / 54.4% | 1.014 | 0.0970% | 57.3% | 0.6189 | [0.881, 1.193] | FAIL |
| h2_tradeable | 1645 / 824 | 53.9% / 52.4% | 1.100 | 0.1090% | — | — | — | reported, not tested |
| h3_primary | 1645 / 550 | 56.5% / 55.5% | 0.967 | 0.1123% | — | — | — | reported, not tested |
| h3_tradeable | 1641 / 548 | 53.7% / 52.7% | 0.989 | 0.0699% | — | — | — | reported, not tested |
| h5_primary | 1641 / 329 | 54.1% / 52.9% | 0.985 | 0.0821% | — | — | — | reported, not tested |
| h5_tradeable | 1641 / 329 | 51.9% / 51.4% | 0.965 | 0.0165% | — | — | — | reported, not tested |
| h20_primary | 1627 / 84 | 57.0% / 60.7% | 1.083 | 0.8462% | — | — | — | reported, not tested |
| h20_tradeable | 1627 / 84 | 57.5% / 60.7% | 0.882 | 0.5270% | — | — | — | reported, not tested |

## Breakdowns at h*=2 (close-to-close, non-overlap) — reported, not tested

### by asset

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| GLD | 105 | 52.4% | 1.041 | 0.0871% |
| SPY | 361 | 55.4% | 0.863 | 0.0303% |
| TLT | 158 | 51.3% | 1.066 | 0.0529% |
| USO | 95 | 56.8% | 1.133 | 0.4241% |
| UUP | 105 | 55.2% | 1.289 | 0.1065% |

### by tier

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 1.0 | 10 | too few | — | — |
| 2.0 | 113 | 47.8% | 1.166 | 0.0392% |
| 3.0 | 703 | 56.9% | 1.005 | 0.1344% |

### by dominant_source

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| earnings_8k | 286 | 54.5% | 1.058 | 0.1097% |
| fomc_minutes | 150 | 54.7% | 1.219 | 0.1679% |
| fomc_statement | 145 | 53.1% | 1.079 | 0.1088% |
| political_order | 152 | 58.6% | 0.839 | 0.0877% |
| political_other | 95 | 64.2% | 1.230 | 0.4496% |

### by regime

| value | n | hit-rate | asymmetry | mean signed |
|---|---|---|---|---|
| 0 | 213 | 52.1% | 0.808 | -0.0649% |
| 1 | 164 | 57.3% | 0.772 | 0.0164% |
| 2 | 188 | 59.0% | 1.143 | 0.2555% |
| 3 | 264 | 54.9% | 1.181 | 0.2272% |
