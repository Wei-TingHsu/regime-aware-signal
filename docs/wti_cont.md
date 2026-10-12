# WTI_CONT beside USO — oil column re-runs (TRACK §3.13)

*2026-10-12. Columns: USO (model instrument), WTI_SPOT = FRED DCOILWTICO, WTI_FUT = Yahoo CL=F as spliced. Sessions with all three: 5147 (2006-04-11 → 2026-10-08).*

## 1. The instrument itself

Daily correlation USO–spot 0.821, USO–CL=F 0.886, spot–CL=F 0.929. Cumulative over 20.5 years: USO ×0.24, spot ×1.40, CL=F ×1.14; USO's drag against spot -8.7% a year. What this measures: the level drift of the ETF against the commodity. What it does not: the day-to-day direction, which is what the engine's calls are scored on — see §3.

## 2. Chain alerts (W2-seq) by oil column

| column | firings | dates |
|---|---|---|
| USO | 2 | 2022-03-07, 2026-03-05 |
| WTI_SPOT | 4 | 2009-01-26, 2009-02-24, 2022-03-07, 2026-03-05 |
| WTI_FUT | 5 | 2009-01-26, 2009-02-24, 2022-03-07, 2022-08-25, 2026-03-05 |

The rule was calibrated on USO (8 Oct). Same dates on all three = the rule is about oil, not about the ETF.

**A2 on each column's firings (gold forward):**

| column | firing | gold +20 sessions | gold +60 sessions |
|---|---|---|---|
| USO | 2022-03-07 | -3.2% | -7.6% |
| USO | 2026-03-05 | -7.9% | -11.8% |
| USO | **mean, n=2** | | **-9.7%, p 0.009 -> INCONCLUSIVE** |
| WTI_SPOT | 2009-01-26 | +6.5% | -1.8% |
| WTI_SPOT | 2009-02-24 | -4.0% | -2.6% |
| WTI_SPOT | 2022-03-07 | -3.2% | -7.6% |
| WTI_SPOT | 2026-03-05 | -7.9% | -11.8% |
| WTI_SPOT | **mean, n=4** | | **-6.0%, p 0.009 -> INCONCLUSIVE** |
| WTI_FUT | 2009-01-26 | +6.5% | -1.8% |
| WTI_FUT | 2009-02-24 | -4.0% | -2.6% |
| WTI_FUT | 2022-03-07 | -3.2% | -7.6% |
| WTI_FUT | 2022-08-25 | -6.6% | -0.6% |
| WTI_FUT | 2026-03-05 | -7.9% | -11.8% |
| WTI_FUT | **mean, n=5** | | **-5.0%, p 0.011 -> INCONCLUSIVE** |

## 3. Referee — the USO cell with each column (h = 2, 10,000 permutations, USO column swapped only)

**USO (baseline)** — `48a6c4e879a1_n2617_h2`

| USO | 109 | 1307 | 116 | 0 | 0 | 6/53/50 |
| h2_primary **(primary)** | 1064 / 534 | 55.2% / 54.9% | 1.008 | 0.1028% | 57.5% | 0.4003 | [0.853, 1.232] | FAIL |
| USO | 55 | 65.5% | 0.744 | 0.3243% |

**WTI_SPOT** — `48a6c4e879a1_n2617_h2_wtispot`

| USO | 105 | 1307 | 120 | 0 | 0 | 17/1/87 |
| h2_primary **(primary)** | 1060 / 532 | 54.9% / 53.9% | 1.097 | 0.1249% | 57.3% | 0.6107 | [0.917, 1.334] | FAIL |
| USO | 53 | 56.6% | 1.434 | 0.5540% |

**WTI_FUT** — `48a6c4e879a1_n2617_h2_wtifut`

| USO | 109 | 1307 | 116 | 0 | 0 | 15/54/40 |
| h2_primary **(primary)** | 1064 / 534 | 55.1% / 54.3% | 1.061 | 0.1174% | 57.3% | 0.5025 | [0.896, 1.296] | FAIL |
| USO | 55 | 60.0% | 1.089 | 0.4656% |

Read against the 29 Sep criteria C1–C4 (prereg_instrument_robustness): verdict class unchanged, hit-rate within the stated band, same sign. Status: measured, this file; T1's USO cell on the new column is the next registered step; the oil amendment is complete when that is in.

## 4. C1–C4 at h = 2 (criteria as registered 29 Sep)

**WTI_SPOT** (`48a6c4e879a1_n2617_h2_wtispot`) — **CONSISTENT**

| criterion | USO baseline | WTI_SPOT | threshold | met |
|---|---|---|---|---|
| C1 primary verdict | FAIL | FAIL | identical | yes |
| C2 row-level hit/miss agreement | — | 98.4% on 1,060 shared rows | ≥ 90% | yes |
| C3 non-overlap hit-rate | 54.9% | 53.9% | within 2.0 pts | yes |
| C4 asymmetry | 1.008 | 1.097 | within 0.15 | yes |

| asset | shared rows | agreement | flips |
|---|---|---|---|
| SPY | 521 | 100.0% | 0 |
| TLT | 187 | 100.0% | 0 |
| GLD | 117 | 100.0% | 0 |
| UUP | 130 | 100.0% | 0 |
| USO | 105 | 83.8% | 17 |

**WTI_FUT** (`48a6c4e879a1_n2617_h2_wtifut`) — **CONSISTENT**

| criterion | USO baseline | WTI_FUT | threshold | met |
|---|---|---|---|---|
| C1 primary verdict | FAIL | FAIL | identical | yes |
| C2 row-level hit/miss agreement | — | 98.8% on 1,064 shared rows | ≥ 90% | yes |
| C3 non-overlap hit-rate | 54.9% | 54.3% | within 2.0 pts | yes |
| C4 asymmetry | 1.008 | 1.061 | within 0.15 | yes |

| asset | shared rows | agreement | flips |
|---|---|---|---|
| SPY | 521 | 100.0% | 0 |
| TLT | 187 | 100.0% | 0 |
| GLD | 117 | 100.0% | 0 |
| UUP | 130 | 100.0% | 0 |
| USO | 109 | 88.1% | 13 |

Only the USO column was swapped, so every flip is an oil row: the other four assets must show 100% agreement, and the USO line is the whole result. What C1–C4 measure: whether the panel-level verdict depends on the oil instrument. What they do not: whether the oil cell itself is tradeable (n ≈ 55).
