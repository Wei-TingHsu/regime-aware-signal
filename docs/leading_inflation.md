# Test LI-1b: which market leads semiconductor shares, and in which market condition?

Registered in TRACK 3.119 before running. Target: the semiconductor fund SOXX, 2007 to 2026-11-24. For each candidate: the link between its change over the last L sessions and the fund's move over the NEXT H sessions. 'Link' is a correlation: 0 = no link, +1 or -1 = a perfect one; the sign says whether the fund follows a rise of the candidate upward (+) or downward (-). 'Chance' = the share of 5,000 copies, with the candidate slid along the calendar, that show a link at least as strong. **LEADS** = chance under 0.00313 (0.05 / 16 tests). 'The other way round' = the fund's move over the last L sessions against the candidate's change over the next H: do chip shares lead it? Single AI borrowers' credit default swap spreads are sold data and are not here.

| candidate (what a rise means) | look-back L | look-ahead H | link (chance) | link with the fund measured against the S&P 500 (chance) | the other way round: chip shares first (chance) | days | verdict |
|---|---|---|---|---|---|---|---|
| 5-year expected inflation (breakeven, FRED) (more inflation expected) | 1 | 1 | +0.031 (0.0310) | +0.021 (0.1492) | +0.149 (0.0010) | 4879 | no |
| inflation-protected against ordinary Treasuries (TIP / IEF) (more inflation expected) | 1 | 1 | -0.024 (0.0746) | +0.001 (0.9298) | +0.056 (0.0010) | 4880 | no |
| 10-year expected inflation (breakeven, FRED) (more inflation expected) | 1 | 1 | +0.020 (0.1524) | -0.004 (0.7932) | +0.235 (0.0010) | 4879 | no |
| expected inflation 5 to 10 years ahead (FRED) (more inflation expected far ahead) | 5 | 5 | -0.024 (0.3267) | -0.037 (0.1390) | +0.002 (0.9321) | 4871 | no |
| expected inflation 5 to 10 years ahead (FRED) (more inflation expected far ahead) | 5 | 1 | -0.009 (0.4663) | -0.011 (0.3897) | +0.071 (0.0010) | 4875 | no |
| expected inflation 5 to 10 years ahead (FRED) (more inflation expected far ahead) | 1 | 5 | -0.009 (0.4905) | -0.011 (0.3949) | +0.072 (0.0010) | 4875 | no |
| inflation-protected against ordinary Treasuries (TIP / IEF) (more inflation expected) | 1 | 5 | -0.009 (0.5721) | -0.010 (0.5113) | +0.040 (0.0070) | 4876 | no |
| inflation-protected against ordinary Treasuries (TIP / IEF) (more inflation expected) | 5 | 1 | -0.007 (0.5817) | -0.008 (0.5553) | +0.046 (0.0040) | 4876 | no |
| 5-year expected inflation (breakeven, FRED) (more inflation expected) | 5 | 5 | +0.012 (0.6241) | +0.029 (0.2515) | +0.153 (0.0010) | 4871 | no |
| inflation-protected against ordinary Treasuries (TIP / IEF) (more inflation expected) | 5 | 5 | -0.012 (0.6287) | -0.010 (0.6719) | +0.057 (0.0310) | 4872 | no |
| expected inflation 5 to 10 years ahead (FRED) (more inflation expected far ahead) | 1 | 1 | -0.005 (0.7057) | -0.026 (0.0684) | +0.164 (0.0010) | 4879 | no |
| 5-year expected inflation (breakeven, FRED) (more inflation expected) | 5 | 1 | +0.005 (0.7265) | +0.003 (0.8052) | +0.150 (0.0010) | 4875 | no |
| 5-year expected inflation (breakeven, FRED) (more inflation expected) | 1 | 5 | +0.005 (0.7421) | +0.003 (0.8398) | +0.131 (0.0010) | 4875 | no |
| 10-year expected inflation (breakeven, FRED) (more inflation expected) | 5 | 5 | -0.006 (0.8242) | -0.002 (0.9480) | +0.117 (0.0010) | 4871 | no |
| 10-year expected inflation (breakeven, FRED) (more inflation expected) | 1 | 5 | -0.003 (0.8616) | -0.006 (0.7021) | +0.145 (0.0010) | 4875 | no |
| 10-year expected inflation (breakeven, FRED) (more inflation expected) | 5 | 1 | -0.002 (0.8724) | -0.005 (0.7097) | +0.167 (0.0010) | 4875 | no |

**0 of 4 candidates lead in at least one of the four (L, H) pairs; 0 of 16 tests are under the limit.**

## By the main page's market condition

The same link inside each condition (days of that condition only), for the strongest (L, H) pair of each candidate. Fewer days, so chance is counted on fewer copies; read the SIZE of the link across conditions.

| candidate | L, H | all days | A steep curve, low short-term rates | Low long-term rates, low or negative real rates | A flat or inverted curve, a strong dollar | Rapid money growth, a high policy rate | strongest in |
|---|---|---|---|---|---|---|---|
| 5-year expected inflation (breakeven, FRED) | 1, 1 | +0.031 (0.0310) | +0.014 (0.4625; 2167 days) | +0.065 (0.0420; 1003 days) | +0.072 (0.0210; 938 days) | +0.014 (0.7373; 644 days) | A flat or inverted curve, a strong dollar |
| 10-year expected inflation (breakeven, FRED) | 1, 1 | +0.020 (0.1524) | -0.020 (0.3427; 2167 days) | +0.065 (0.0470; 1003 days) | +0.086 (0.0130; 938 days) | -0.010 (0.8252; 644 days) | A flat or inverted curve, a strong dollar |
| expected inflation 5 to 10 years ahead (FRED) | 5, 5 | -0.024 (0.3267) | -0.071 (0.0500; 2167 days) | -0.031 (0.5355; 1003 days) | +0.093 (0.0919; 938 days) | +0.022 (0.7443; 640 days) | A flat or inverted curve, a strong dollar |
| inflation-protected against ordinary Treasuries (TIP / IEF) | 1, 1 | -0.024 (0.0746) | -0.055 (0.0090; 2167 days) | -0.035 (0.2837; 1003 days) | +0.005 (0.8691; 938 days) | +0.055 (0.1578; 644 days) | A steep curve, low short-term rates |

How to read a 'LEADS': it says the link is too strong to be chance, not that it is large. A link of 0.05 explains a quarter of one per cent of the fund's moves. Whether it can be traded is a separate test (entry at the next open, the real cost).

## How well each daily stand-in follows core PCE (description)

Core PCE inflation over 12 months, monthly, against the monthly average of each stand-in: the link between their levels and between their changes over 3 months (1 = they move together perfectly, 0 = not at all).

| stand-in | link of levels | link of 3-month changes | months | since |
|---|---|---|---|---|
| 5-year expected inflation (breakeven, FRED) | +0.64 | +0.31 | 286 | 2003-01 |
| 10-year expected inflation (breakeven, FRED) | +0.52 | +0.32 | 286 | 2003-01 |
| expected inflation 5 to 10 years ahead (FRED) | +0.14 | +0.20 | 286 | 2003-01 |
| inflation-protected against ordinary Treasuries (TIP / IEF) | +0.54 | +0.42 | 250 | 2006-01 |
