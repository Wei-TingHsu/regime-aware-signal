# Test CDS-1: which market leads semiconductor shares, and in which market condition?

Registered in TRACK 3.128 before running. Target: the semiconductor fund SOXX, 2024 to 2026-11-24. For each candidate: the link between its change over the last L sessions and the fund's move over the NEXT H sessions. 'Link' is a correlation: 0 = no link, +1 or -1 = a perfect one; the sign says whether the fund follows a rise of the candidate upward (+) or downward (-). 'Chance' = the share of 5,000 copies, with the candidate slid along the calendar, that show a link at least as strong. **LEADS** = chance under 0.00625 (0.05 / 8 tests). 'The other way round' = the fund's move over the last L sessions against the candidate's change over the next H: do chip shares lead it? The candidates here ARE the credit default swap spreads of single companies, built from public trade reports.

| candidate (what a rise means) | look-back L | look-ahead H | link (chance) | link with the fund measured against the S&P 500 (chance) | the other way round: chip shares first (chance) | days | verdict |
|---|---|---|---|---|---|---|---|
| Oracle CDS spread against all other companies' CDS (its credit worse) | 1 | 1 | -0.049 (0.3821) | -0.038 (0.4513) | +0.038 (0.6068) | 365 | no |
| AI debt: CDS of Oracle, CoreWeave, Meta, Alphabet, Microsoft, Amazon against all other companies' CDS (AI borrowers' credit worse) | 5 | 5 | -0.071 (0.4977) | -0.074 (0.4461) | +0.036 (0.7656) | 330 | no |
| AI debt: CDS of Oracle, CoreWeave, Meta, Alphabet, Microsoft, Amazon against all other companies' CDS (AI borrowers' credit worse) | 1 | 5 | -0.030 (0.5213) | -0.033 (0.4671) | -0.001 (0.9701) | 349 | no |
| AI debt: CDS of Oracle, CoreWeave, Meta, Alphabet, Microsoft, Amazon against all other companies' CDS (AI borrowers' credit worse) | 5 | 1 | -0.034 (0.5627) | -0.029 (0.5889) | +0.014 (0.7489) | 334 | no |
| Oracle CDS spread against all other companies' CDS (its credit worse) | 5 | 1 | -0.027 (0.6483) | -0.019 (0.7405) | +0.013 (0.8566) | 347 | no |
| Oracle CDS spread against all other companies' CDS (its credit worse) | 1 | 5 | -0.012 (0.7836) | -0.018 (0.7071) | -0.012 (0.8795) | 361 | no |
| AI debt: CDS of Oracle, CoreWeave, Meta, Alphabet, Microsoft, Amazon against all other companies' CDS (AI borrowers' credit worse) | 1 | 1 | -0.010 (0.8526) | -0.005 (0.9304) | -0.008 (0.9296) | 353 | no |
| Oracle CDS spread against all other companies' CDS (its credit worse) | 5 | 5 | -0.005 (0.9696) | -0.019 (0.8548) | -0.064 (0.5628) | 343 | no |

**0 of 2 candidates lead in at least one of the four (L, H) pairs; 0 of 8 tests are under the limit.**

## By the main page's market condition

The same link inside each condition (days of that condition only), for the strongest (L, H) pair of each candidate. Fewer days, so chance is counted on fewer copies; read the SIZE of the link across conditions.

| candidate | L, H | all days | A steep curve, low short-term rates | Low long-term rates, low or negative real rates | A flat or inverted curve, a strong dollar | Rapid money growth, a high policy rate | strongest in |
|---|---|---|---|---|---|---|---|
| Oracle CDS spread against all other companies' CDS | 1, 1 | -0.049 (0.3821) | n/a (n/a; 0 days) | n/a (n/a; 0 days) | n/a (n/a; 0 days) | -0.049 (0.3706; 365 days) | Rapid money growth, a high policy rate |
| AI debt: CDS of Oracle, CoreWeave, Meta, Alphabet, Microsoft, Amazon against all other companies' CDS | 5, 5 | -0.071 (0.4977) | n/a (n/a; 0 days) | n/a (n/a; 0 days) | n/a (n/a; 0 days) | -0.071 (0.4755; 330 days) | Rapid money growth, a high policy rate |

How to read a 'LEADS': it says the link is too strong to be chance, not that it is large. A link of 0.05 explains a quarter of one per cent of the fund's moves. Whether it can be traded is a separate test (entry at the next open, the real cost).

## How the daily spreads were built

New trades of 5-year single-company CDS in US dollars, done before 16:00 New York time. A trade's spread is taken as given where the file gives it; where the trade is priced as a fixed yearly rate plus a one-off payment and its size is not hidden, the spread worth the same is worked out (interest 4%, recovery 40%; of the two possible answers the one nearer to the company's given spreads within 10 days is kept). Trades whose size is hidden behind the cap and that give no spread are not usable. The day's spread = the middle one of its trades. Each series is measured against the same day's move of all other single-company CDS, so that a move of the whole credit market is taken out.

| company | days with a spread | trades: spread given + worked out | first day | spread, first 20 days -> last 20 days (basis points) | in the test |
|---|---|---|---|---|---|
| Oracle | 266 of 583 | 355 + 387 | 2025-02-25 | 38 -> 298 | yes |
| Amazon | 147 of 583 | 237 + 88 | 2024-12-30 | 26 -> 95 | no (under 250 days) |
| Meta | 108 of 583 | 125 + 131 | 2026-04-06 | 70 -> 114 | no (under 250 days) |
| Intel | 103 of 583 | 93 + 97 | 2025-03-03 | 76 -> 89 | no (under 250 days) |
| IBM | 95 of 583 | 70 + 70 | 2025-03-05 | 38 -> 65 | no (under 250 days) |
| Microsoft | 90 of 583 | 114 + 64 | 2025-10-30 | 38 -> 53 | no (under 250 days) |
| Alphabet | 83 of 583 | 120 + 81 | 2026-04-15 | 52 -> 85 | no (under 250 days) |
| AMD | 74 of 583 | 95 + 61 | 2026-03-27 | 46 -> 136 | no (under 250 days) |
| Nvidia | 69 of 583 | 150 + 87 | 2026-06-24 | 71 -> 133 | no (under 250 days) |
| Cisco | 55 of 583 | 39 + 47 | 2025-03-20 | 33 -> 47 | no (under 250 days) |
| Apple | 21 of 583 | 26 + 5 | 2026-06-08 | 37 -> 38 | no (under 250 days) |
| Dell | 12 of 583 | 20 + 2 | 2026-09-21 | 82 -> 82 | no (under 250 days) |
| Netflix | 12 of 583 | 15 + 4 | 2026-09-21 | 48 -> 48 | no (under 250 days) |
| CoreWeave | 2 of 583 | 2 + 0 | 2026-05-11 | 120 -> 120 | no (under 250 days) |

The data: public trade reports under the SEC's Regulation SBSR, from DTCC's repository, 2 Sep 2024 onward (earlier days are no longer offered). Kept for our own testing in an ignored folder; not uploaded; not on the page (terms of re-use not settled, TRACK 3.127).
