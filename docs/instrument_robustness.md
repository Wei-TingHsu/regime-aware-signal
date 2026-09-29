# Instrument robustness — result

*Run 2026-09-29 16:13. Registered in `docs/prereg_instrument_robustness.md`. Baseline `48a6c4e879a1_n2617` vs alternative `48a6c4e879a1_n2617_altinstr` (^GSPC, GC=F, CL=F, DX-Y.NYB, ^TNX price proxy with D=8.0).*

| criterion | baseline | alternative | threshold | met |
|---|---|---|---|---|
| C1 primary verdict | FAIL | FAIL | identical | yes |
| C2 row-level hit/miss agreement | — | 94.8% on 1,060 shared rows | ≥ 90% | yes |
| C3 non-overlap hit-rate | 58.2% | 56.5% | within 2.0 pts | yes |
| C4 asymmetry | 0.880 | 0.951 | within 0.15 | yes |

## Verdict: **CONSISTENT**

The app may state: *Modelled on SPY, TLT, GLD, UUP and USO; shown as the S&P 500, the 10-year yield, gold futures, DXY and WTI. Verdicts are unchanged on the alternative panel.*

## Attribution (reported whichever way the verdict fell)

| asset | shared rows | agreement | flips |
|---|---|---|---|
| SPY | 517 | 98.1% | 10 |
| TLT | 186 | 90.9% | 17 |
| GLD | 117 | 89.7% | 12 |
| UUP | 132 | 94.7% | 7 |
| USO | 108 | 91.7% | 9 |

Flip rate on FOMC statement days: **5.8%** (n=257) vs other days **5.0%** (n=803). A large gap points at settlement timing (GLD 4 pm vs GC=F 1:30 pm ET against a 2 pm statement).
