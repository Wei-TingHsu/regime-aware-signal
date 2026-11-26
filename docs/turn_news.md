# Test TN-1: do trends turn on news? (the founder's assumption, POOL_PLAN point 4)

Registered in TRACK 3.141 before running. 20 pool stocks, sessions from 2018-06-01; 947 turns of the fixed trend rule (K = 5 usual daily moves). News dates on file: 8-K filings of 19 of these companies, 133 Fed decision days, 1217 TrendForce release days. 'Share of turns' = the turns that have such news in the window. 'Ordinary' = the same share when each stock's turns are slid along its own calendar. 'Chance' = the share of the 409 slid copies with at least as many. **PASSES** = chance under 0.0033 (0.05 / 15 cells).

| kind of news | window around the turn | turns | with such news | share of turns | ordinary | times the ordinary | chance | verdict | tops / bottoms with such news |
|---|---|---|---|---|---|---|---|---|---|
| the company's own results | the session after the turn (+1) | 903 | 38 | 4.2% | 1.7% | 2.53 | 0.0024 | **PASSES** | 23 of 456 / 15 of 447 |
| the company's own results | the turn day or the session after (0, +1) | 903 | 64 | 7.1% | 3.3% | 2.14 | 0.0024 | **PASSES** | 35 of 456 / 29 of 447 |
| the company's own results | from the session before to two after (-1 .. +2) | 903 | 115 | 12.7% | 6.6% | 1.92 | 0.0024 | **PASSES** | 60 of 456 / 55 of 447 |
| the company's other 8-K filings | the session after the turn (+1) | 903 | 35 | 3.9% | 3.1% | 1.24 | 0.1146 | no | 21 of 456 / 14 of 447 |
| the company's other 8-K filings | the turn day or the session after (0, +1) | 903 | 65 | 7.2% | 6.1% | 1.18 | 0.0976 | no | 36 of 456 / 29 of 447 |
| the company's other 8-K filings | from the session before to two after (-1 .. +2) | 903 | 125 | 13.8% | 11.7% | 1.19 | 0.0171 | no | 71 of 456 / 54 of 447 |
| any 8-K of the company | the session after the turn (+1) | 903 | 73 | 8.1% | 4.7% | 1.72 | 0.0049 | no | 44 of 456 / 29 of 447 |
| any 8-K of the company | the turn day or the session after (0, +1) | 903 | 127 | 14.1% | 9.2% | 1.54 | 0.0024 | **PASSES** | 70 of 456 / 57 of 447 |
| any 8-K of the company | from the session before to two after (-1 .. +2) | 903 | 225 | 24.9% | 17.5% | 1.43 | 0.0024 | **PASSES** | 122 of 456 / 103 of 447 |
| a Fed decision day | the session after the turn (+1) | 947 | 41 | 4.3% | 3.5% | 1.25 | 0.1707 | no | 24 of 478 / 17 of 469 |
| a Fed decision day | the turn day or the session after (0, +1) | 947 | 96 | 10.1% | 6.9% | 1.46 | 0.0195 | no | 46 of 478 / 50 of 469 |
| a Fed decision day | from the session before to two after (-1 .. +2) | 947 | 172 | 18.2% | 13.9% | 1.31 | 0.0171 | no | 78 of 478 / 94 of 469 |
| a TrendForce release (chip companies) | the session after the turn (+1) | 413 | 132 | 32.0% | 29.7% | 1.07 | 0.2610 | no | 55 of 209 / 77 of 204 |
| a TrendForce release (chip companies) | the turn day or the session after (0, +1) | 413 | 241 | 58.4% | 51.1% | 1.14 | 0.0195 | no | 112 of 209 / 129 of 204 |
| a TrendForce release (chip companies) | from the session before to two after (-1 .. +2) | 413 | 326 | 78.9% | 76.8% | 1.03 | 0.2341 | no | 154 of 209 / 172 of 204 |

## How many turns have ANY dated news near them (any 8-K of the company, a Fed decision, a TrendForce release)

| window | turns | with any dated news | share | ordinary |
|---|---|---|---|---|
| the session after the turn (+1) | 947 | 229 | 24.2% | 19.7% |
| the turn day or the session after (0, +1) | 947 | 397 | 41.9% | 33.6% |
| from the session before to two after (-1 .. +2) | 947 | 562 | 59.3% | 51.7% |

Stocks: AAPL: 50 turns; AMD: 51 turns; AMZN: 56 turns; AVGO: 45 turns; CRWD: 42 turns; CSCO: 47 turns; EMR: 50 turns; GE: 49 turns; GOOG: 43 turns; IBM: 56 turns; INTC: 53 turns; META: 39 turns; MSFT: 55 turns; MU: 52 turns; NVDA: 53 turns; ORCL: 47 turns; QCOM: 55 turns; SNDK: 5 turns; TSM: 44 turns (no 8-K list); TXN: 55 turns

What this cannot say: news without a date on file is not counted (press reports, analyst changes, product launches, news of OTHER companies -- a customer's or a rival's results); a turn is only known afterwards (the rule confirms it some sessions later), so this is about causes, not about a trade; a turn that has news near it need not be caused by it.
Sources: SEC EDGAR (8-K lists), the Federal Reserve (statement dates), TrendForce press centre (release dates).
