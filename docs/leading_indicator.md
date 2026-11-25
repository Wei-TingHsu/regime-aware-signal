# Test LI-1: which market leads semiconductor shares, and in which market condition?

Registered in TRACK 3.118 before running. Target: the semiconductor fund SOXX, 2007 to 2026-11-24. For each candidate: the link between its change over the last L sessions and the fund's move over the NEXT H sessions. 'Link' is a correlation: 0 = no link, +1 or -1 = a perfect one; the sign says whether the fund follows a rise of the candidate upward (+) or downward (-). 'Chance' = the share of 5,000 copies, with the candidate slid along the calendar, that show a link at least as strong. **LEADS** = chance under 0.00089 (0.05 / 56 tests). 'The other way round' = the fund's move over the last L sessions against the candidate's change over the next H: do chip shares lead it? Single AI borrowers' credit default swap spreads are sold data and are not here.

| candidate (what a rise means) | look-back L | look-ahead H | link (chance) | link with the fund measured against the S&P 500 (chance) | the other way round: chip shares first (chance) | days | verdict |
|---|---|---|---|---|---|---|---|
| high-yield bonds against Treasuries (HYG / IEF) (credit calmer) | 1 | 1 | -0.069 (0.0002) | -0.025 (0.0806) | -0.008 (0.5844) | 4880 | **LEADS** |
| share volatility (VIX) (more fear) | 1 | 1 | +0.061 (0.0002) | +0.043 (0.0036) | +0.055 (0.0010) | 4880 | **LEADS** |
| high-yield bonds against Treasuries (HYG / IEF) (credit calmer) | 1 | 5 | -0.049 (0.0010) | -0.025 (0.0658) | +0.021 (0.1119) | 4876 | no |
| share volatility (VIX) (more fear) | 1 | 5 | +0.042 (0.0010) | +0.038 (0.0032) | +0.079 (0.0010) | 4876 | no |
| bank loans (BKLN) (credit calmer) | 1 | 1 | -0.063 (0.0012) | -0.058 (0.0014) | +0.003 (0.8861) | 3955 | no |
| high-yield bonds against Treasuries (HYG / IEF) (credit calmer) | 5 | 1 | -0.048 (0.0016) | -0.025 (0.0662) | +0.022 (0.1289) | 4876 | no |
| bank loans (BKLN) (credit calmer) | 1 | 5 | -0.057 (0.0016) | -0.057 (0.0054) | +0.073 (0.0020) | 3951 | no |
| share volatility (VIX) (more fear) | 5 | 1 | +0.046 (0.0018) | +0.042 (0.0024) | +0.076 (0.0010) | 4876 | no |
| bank loans (BKLN) (credit calmer) | 5 | 1 | -0.047 (0.0020) | -0.047 (0.0038) | +0.090 (0.0010) | 3951 | no |
| investment-grade bonds against Treasuries (LQD / IEF) (credit calmer) | 1 | 1 | -0.046 (0.0040) | -0.027 (0.0564) | -0.009 (0.5504) | 4880 | no |
| private-credit lenders against the market (BIZD / SPY) (lenders stronger) | 1 | 1 | +0.047 (0.0080) | +0.047 (0.0074) | +0.138 (0.0010) | 3466 | no |
| investment-grade bonds against Treasuries (LQD / IEF) (credit calmer) | 5 | 1 | -0.029 (0.0264) | -0.021 (0.1218) | +0.043 (0.0070) | 4876 | no |
| investment-grade bonds against Treasuries (LQD / IEF) (credit calmer) | 1 | 5 | -0.029 (0.0288) | -0.020 (0.1276) | +0.043 (0.0030) | 4876 | no |
| 10-year minus 2-year yield (curve steeper) | 5 | 5 | -0.053 (0.0390) | -0.022 (0.3825) | -0.090 (0.0040) | 4871 | no |
| high-yield bonds against Treasuries (HYG / IEF) (credit calmer) | 5 | 5 | -0.052 (0.0392) | -0.035 (0.1644) | +0.032 (0.2018) | 4872 | no |
| share volatility (VIX) (more fear) | 5 | 5 | +0.050 (0.0402) | +0.044 (0.0700) | +0.131 (0.0010) | 4872 | no |
| private-credit lenders against the market (BIZD / SPY) (lenders stronger) | 5 | 1 | +0.031 (0.0458) | +0.028 (0.0754) | +0.100 (0.0010) | 3462 | no |
| bank loans (BKLN) (credit calmer) | 5 | 5 | -0.056 (0.0482) | -0.042 (0.1334) | +0.084 (0.0150) | 3947 | no |
| bond volatility (MOVE) (more fear in bonds) | 1 | 1 | +0.027 (0.0554) | +0.020 (0.1508) | -0.058 (0.0010) | 4877 | no |
| private-credit lenders against the market (BIZD / SPY) (lenders stronger) | 1 | 5 | +0.030 (0.0584) | +0.027 (0.0882) | +0.096 (0.0010) | 3462 | no |
| Oracle against the market (ORCL / SPY) (the largest AI borrower stronger) | 1 | 1 | -0.024 (0.0898) | -0.036 (0.0108) | -0.025 (0.0689) | 4880 | no |
| funding stress (SOFR minus the rate on reserves) (cash dearer) | 1 | 5 | -0.037 (0.1232) | -0.024 (0.2897) | +0.066 (0.1092) | 1331 | no |
| funding stress (SOFR minus the rate on reserves) (cash dearer) | 5 | 1 | -0.039 (0.1388) | -0.026 (0.3479) | +0.057 (0.1281) | 1331 | no |
| bond volatility (MOVE) (more fear in bonds) | 5 | 1 | +0.019 (0.1532) | +0.011 (0.3777) | -0.042 (0.0020) | 4872 | no |
| bond volatility (MOVE) (more fear in bonds) | 1 | 5 | +0.017 (0.1846) | +0.009 (0.4481) | -0.042 (0.0020) | 4873 | no |
| funding stress (SOFR minus the rate on reserves) (cash dearer) | 1 | 1 | -0.037 (0.1852) | -0.044 (0.1202) | +0.022 (0.6433) | 1335 | no |
| Oracle against the market (ORCL / SPY) (the largest AI borrower stronger) | 5 | 1 | -0.015 (0.2615) | -0.020 (0.1246) | -0.019 (0.2058) | 4876 | no |
| bond volatility (MOVE) (more fear in bonds) | 5 | 5 | +0.025 (0.2947) | +0.010 (0.6631) | -0.031 (0.1958) | 4868 | no |
| private-credit lenders against the market (BIZD / SPY) (lenders stronger) | 5 | 5 | -0.030 (0.3129) | -0.002 (0.9474) | +0.081 (0.0240) | 3458 | no |
| Oracle against the market (ORCL / SPY) (the largest AI borrower stronger) | 1 | 5 | -0.014 (0.3253) | -0.019 (0.1610) | -0.016 (0.2228) | 4876 | no |
| regional banks against the market (KRE / SPY) (banks stronger) | 5 | 5 | -0.024 (0.3349) | -0.013 (0.6011) | +0.017 (0.5325) | 4872 | no |
| investment-grade credit spread (FRED) (credit tighter) | 1 | 1 | +0.033 (0.3527) | +0.023 (0.5251) | -0.356 (0.0051) | 749 | no |
| 10-year minus 2-year yield (curve steeper) | 1 | 5 | -0.012 (0.3857) | -0.000 (0.9938) | +0.011 (0.4396) | 4875 | no |
| 10-year minus 2-year yield (curve steeper) | 5 | 1 | -0.012 (0.3911) | -0.000 (0.9978) | +0.011 (0.4595) | 4875 | no |
| regional banks against the market (KRE / SPY) (banks stronger) | 1 | 5 | -0.011 (0.4461) | -0.012 (0.3781) | -0.010 (0.4805) | 4876 | no |
| regional banks against the market (KRE / SPY) (banks stronger) | 1 | 1 | -0.011 (0.4603) | -0.002 (0.8660) | -0.033 (0.0260) | 4880 | no |
| regional banks against the market (KRE / SPY) (banks stronger) | 5 | 1 | -0.009 (0.4921) | -0.010 (0.4379) | -0.009 (0.4945) | 4876 | no |
| investment-grade bonds against Treasuries (LQD / IEF) (credit calmer) | 5 | 5 | -0.014 (0.5751) | -0.010 (0.7001) | +0.082 (0.0040) | 4872 | no |
| CCC credit spread (FRED) (weakest borrowers tighter) | 5 | 1 | -0.017 (0.5989) | -0.024 (0.4645) | -0.259 (0.0045) | 745 | no |
| 10-year minus 2-year yield (curve steeper) | 1 | 1 | +0.007 (0.6065) | -0.009 (0.5539) | +0.076 (0.0010) | 4879 | no |
| CCC credit spread (FRED) (weakest borrowers tighter) | 5 | 5 | -0.026 (0.6961) | -0.029 (0.6431) | -0.134 (0.2275) | 741 | no |
| BBB credit spread (FRED) (credit tighter) | 1 | 1 | +0.014 (0.7077) | +0.001 (0.9876) | -0.383 (0.0051) | 749 | no |
| BBB credit spread (FRED) (credit tighter) | 1 | 5 | +0.013 (0.7738) | -0.001 (0.9744) | -0.203 (0.0054) | 745 | no |
| BBB credit spread (FRED) (credit tighter) | 5 | 5 | +0.018 (0.7752) | +0.009 (0.8822) | -0.169 (0.0893) | 741 | no |
| investment-grade credit spread (FRED) (credit tighter) | 5 | 5 | +0.017 (0.8044) | +0.011 (0.8676) | -0.151 (0.0927) | 741 | no |
| investment-grade credit spread (FRED) (credit tighter) | 1 | 5 | +0.011 (0.8102) | -0.001 (0.9810) | -0.193 (0.0056) | 745 | no |
| high-yield credit spread (FRED) (credit tighter) | 5 | 5 | +0.016 (0.8116) | +0.011 (0.8534) | -0.065 (0.4791) | 741 | no |
| funding stress (SOFR minus the rate on reserves) (cash dearer) | 5 | 5 | +0.010 (0.8326) | +0.032 (0.4643) | +0.005 (0.9452) | 1327 | no |
| CCC credit spread (FRED) (weakest borrowers tighter) | 1 | 5 | -0.009 (0.8336) | -0.013 (0.7365) | -0.200 (0.0044) | 745 | no |
| high-yield credit spread (FRED) (credit tighter) | 5 | 1 | -0.006 (0.8526) | -0.017 (0.6265) | -0.244 (0.0042) | 745 | no |
| high-yield credit spread (FRED) (credit tighter) | 1 | 1 | -0.005 (0.8946) | -0.011 (0.7592) | -0.503 (0.0050) | 749 | no |
| high-yield credit spread (FRED) (credit tighter) | 1 | 5 | +0.003 (0.9338) | -0.005 (0.8852) | -0.209 (0.0051) | 745 | no |
| CCC credit spread (FRED) (weakest borrowers tighter) | 1 | 1 | -0.002 (0.9548) | -0.010 (0.7936) | -0.408 (0.0045) | 749 | no |
| Oracle against the market (ORCL / SPY) (the largest AI borrower stronger) | 5 | 5 | +0.001 (0.9766) | -0.006 (0.8122) | -0.010 (0.7303) | 4872 | no |
| investment-grade credit spread (FRED) (credit tighter) | 5 | 1 | -0.000 (0.9920) | -0.011 (0.7287) | -0.265 (0.0050) | 745 | no |
| BBB credit spread (FRED) (credit tighter) | 5 | 1 | +0.000 (0.9950) | -0.013 (0.6961) | -0.279 (0.0047) | 745 | no |

**2 of 14 candidates lead in at least one of the four (L, H) pairs; 2 of 56 tests are under the limit.**

## By the main page's market condition

The same link inside each condition (days of that condition only), for the strongest (L, H) pair of each candidate. Fewer days, so chance is counted on fewer copies; read the SIZE of the link across conditions.

| candidate | L, H | all days | A steep curve, low short-term rates | Low long-term rates, low or negative real rates | A flat or inverted curve, a strong dollar | Rapid money growth, a high policy rate | strongest in |
|---|---|---|---|---|---|---|---|
| high-yield bonds against Treasuries (HYG / IEF) | 1, 1 | -0.069 (0.0002) | -0.028 (0.1948; 2167 days) | -0.168 (0.0010; 1003 days) | -0.116 (0.0010; 938 days) | -0.028 (0.4855; 644 days) | Low long-term rates, low or negative real rates |
| investment-grade bonds against Treasuries (LQD / IEF) | 1, 1 | -0.046 (0.0040) | -0.046 (0.0290; 2167 days) | -0.114 (0.0020; 1003 days) | -0.002 (0.9471; 938 days) | -0.048 (0.2058; 644 days) | Low long-term rates, low or negative real rates |
| bank loans (BKLN) | 1, 1 | -0.063 (0.0012) | +0.060 (0.0200; 1515 days) | -0.174 (0.0010; 928 days) | -0.027 (0.4216; 868 days) | -0.091 (0.0170; 644 days) | Low long-term rates, low or negative real rates |
| private-credit lenders against the market (BIZD / SPY) | 1, 1 | +0.047 (0.0080) | +0.008 (0.8202; 1093 days) | +0.085 (0.0160; 869 days) | +0.023 (0.5125; 860 days) | +0.056 (0.1419; 644 days) | Low long-term rates, low or negative real rates |
| regional banks against the market (KRE / SPY) | 5, 5 | -0.024 (0.3349) | -0.087 (0.0150; 2167 days) | -0.030 (0.5874; 1003 days) | +0.067 (0.2408; 938 days) | -0.020 (0.7902; 640 days) | A steep curve, low short-term rates |
| share volatility (VIX) | 1, 1 | +0.061 (0.0002) | +0.011 (0.6074; 2167 days) | +0.116 (0.0020; 1003 days) | +0.055 (0.1029; 938 days) | +0.094 (0.0250; 644 days) | Low long-term rates, low or negative real rates |
| bond volatility (MOVE) | 1, 1 | +0.027 (0.0554) | +0.012 (0.5874; 2164 days) | +0.046 (0.1169; 1003 days) | +0.008 (0.8242; 938 days) | +0.056 (0.1638; 644 days) | Rapid money growth, a high policy rate |
| Oracle against the market (ORCL / SPY) | 1, 1 | -0.024 (0.0898) | -0.038 (0.0819; 2167 days) | +0.004 (0.9151; 1003 days) | -0.011 (0.7073; 938 days) | -0.034 (0.4006; 644 days) | A steep curve, low short-term rates |
| high-yield credit spread (FRED) | 5, 5 | +0.016 (0.8116) | n/a (n/a; 0 days) | n/a (n/a; 8 days) | n/a (n/a; 93 days) | +0.003 (0.9540; 640 days) | Rapid money growth, a high policy rate |
| investment-grade credit spread (FRED) | 1, 1 | +0.033 (0.3527) | n/a (n/a; 0 days) | n/a (n/a; 8 days) | n/a (n/a; 97 days) | -0.015 (0.6783; 644 days) | Rapid money growth, a high policy rate |
| CCC credit spread (FRED) | 5, 1 | -0.017 (0.5989) | n/a (n/a; 0 days) | n/a (n/a; 8 days) | n/a (n/a; 93 days) | -0.084 (0.0210; 644 days) | Rapid money growth, a high policy rate |
| BBB credit spread (FRED) | 1, 1 | +0.014 (0.7077) | n/a (n/a; 0 days) | n/a (n/a; 8 days) | n/a (n/a; 97 days) | -0.032 (0.4106; 644 days) | Rapid money growth, a high policy rate |
| funding stress (SOFR minus the rate on reserves) | 1, 5 | -0.037 (0.1232) | n/a (n/a; 136 days) | n/a (n/a; 28 days) | -0.095 (0.0230; 527 days) | -0.033 (0.3187; 640 days) | A flat or inverted curve, a strong dollar |
| 10-year minus 2-year yield | 5, 5 | -0.053 (0.0390) | -0.123 (0.0030; 2167 days) | +0.110 (0.0480; 1003 days) | -0.037 (0.4925; 938 days) | -0.059 (0.4156; 640 days) | A steep curve, low short-term rates |

How to read a 'LEADS': it says the link is too strong to be chance, not that it is large. A link of 0.05 explains a quarter of one per cent of the fund's moves. Whether it can be traded is a separate test (entry at the next open, the real cost).
