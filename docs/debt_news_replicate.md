# Test DN-3: does the fall after a debt deal repeat on companies that were NOT used to find it?

Registered in TRACK 3.139 before running. Deals of AAPL, AMD, AVGO, CSCO, IBM, INTC, MU, NVDA, QCOM, TXN since 2018: 133; within 3 sessions of the company's own results filing: 30; clean: 103. 'Difference' = the company's own share in the window, minus its average on all other days. The whole-day windows are counted from the day of the filing; the TRADABLE windows start at the first open after the filing became public. The registered verdict looks at TWO cells only, fixed beforehand from DN-2: clean deals, 2018 to now, the two tradable windows. It REPEATS if at least one of them is negative with a chance under 0.025 (0.05 / 2). Everything else is description.

**Verdict on the clean deals: does NOT repeat**

| which deals | period | window | deals | difference, % | chance of this cell |
|---|---|---|---|---|---|
| clean deals (not within 3 sessions of results) | 2018 to now | day 0, whole day (not tradable) | 103 | -0.11 | 0.6941 |
| clean deals (not within 3 sessions of results) | 2018 to now | the session after, whole day | 103 | +0.39 | 0.1621 |
| clean deals (not within 3 sessions of results) | 2018 to now | TRADABLE: first open after the filing to that day's close | 103 | -0.14 | 0.5388 |
| clean deals (not within 3 sessions of results) | 2018 to now | TRADABLE: first open after the filing to the next day's close | 103 | +0.25 | 0.4247 |
| clean deals (not within 3 sessions of results) | 2025 to now (the AI build-out) | day 0, whole day (not tradable) | 25 | +0.29 | 0.7055 |
| clean deals (not within 3 sessions of results) | 2025 to now (the AI build-out) | the session after, whole day | 25 | -0.06 | 0.9406 |
| clean deals (not within 3 sessions of results) | 2025 to now (the AI build-out) | TRADABLE: first open after the filing to that day's close | 25 | +0.31 | 0.5662 |
| clean deals (not within 3 sessions of results) | 2025 to now (the AI build-out) | TRADABLE: first open after the filing to the next day's close | 25 | -0.20 | 0.8219 |
| deals within 3 sessions of results | 2018 to now | day 0, whole day (not tradable) | 21 | +1.12 | 0.0776 |
| deals within 3 sessions of results | 2018 to now | the session after, whole day | 26 | +0.34 | 0.4703 |
| deals within 3 sessions of results | 2018 to now | TRADABLE: first open after the filing to that day's close | 26 | +0.61 | 0.1347 |
| deals within 3 sessions of results | 2018 to now | TRADABLE: first open after the filing to the next day's close | 26 | +0.98 | 0.1324 |
| deals within 3 sessions of results | 2025 to now (the AI build-out) | day 0, whole day (not tradable) | 6 | n/a | too few |
| deals within 3 sessions of results | 2025 to now (the AI build-out) | the session after, whole day | 6 | n/a | too few |
| deals within 3 sessions of results | 2025 to now (the AI build-out) | TRADABLE: first open after the filing to that day's close | 6 | n/a | too few |
| deals within 3 sessions of results | 2025 to now (the AI build-out) | TRADABLE: first open after the filing to the next day's close | 6 | n/a | too few |

## Every deal since 2025

| filed (New York) | company | near results? | day 0 | the session after | first open after the filing -> that close | -> the next close |
|---|---|---|---|---|---|---|
| 2025-01-06 08:31 | AVGO | no | +1.7% | -3.3% | -0.0% | -3.3% |
| 2025-01-13 08:40 | MU | no | -4.3% | +2.4% | -0.8% | +1.6% |
| 2025-02-05 06:00 | IBM | no | -0.4% | -3.7% | -0.9% | -4.6% |
| 2025-02-19 08:17 | CSCO | no | +0.4% | -0.3% | +0.5% | +0.2% |
| 2025-03-10 08:43 | AMD | no | -3.7% | +0.1% | -2.0% | -1.8% |
| 2025-03-12 16:05 | MU | no | -0.8% | +6.2% | +0.7% | +6.9% |
| 2025-03-24 16:17 | AMD | no | +0.8% | -4.0% | +1.4% | -2.7% |
| 2025-04-24 08:31 | MU | no | +6.2% | +3.0% | +3.8% | +7.0% |
| 2025-05-05 08:16 | AAPL | YES | -3.1% | -0.2% | -2.1% | -2.3% |
| 2025-05-19 09:06 | QCOM | no | +0.8% | +0.1% | +2.1% | +2.2% |
| 2025-05-20 08:36 | TXN | no | +0.2% | -1.7% | +0.2% | -1.6% |
| 2025-06-20 17:00 | IBM | no | +2.9% | +1.6% | +2.7% | +4.3% |
| 2025-07-07 08:42 | AVGO | no | -0.4% | -0.9% | -0.3% | -1.2% |
| 2025-09-18 16:23 | AVGO | no | -0.2% | -0.1% | +0.1% | -1.5% |
| 2026-01-06 08:49 | AVGO | no | +0.1% | -0.1% | +0.0% | -0.0% |
| 2026-01-29 06:53 | IBM | YES | +5.1% | -0.8% | -2.7% | -3.5% |
| 2026-04-27 09:20 | INTC | YES | +3.0% | -0.6% | +1.6% | +1.0% |
| 2026-05-15 16:12 | AMD | no | -0.7% | -1.6% | -2.0% | -3.6% |
| 2026-06-15 07:44 | NVDA | no | +3.5% | -2.4% | +1.7% | -0.7% |
| 2026-06-17 16:14 | AVGO | no | +4.3% | +4.7% | +0.4% | -4.1% |
| 2026-06-23 16:18 | IBM | no | -0.7% | -1.8% | +0.4% | -1.4% |
| 2026-08-10 08:08 | INTC | no | -4.1% | +0.2% | -0.8% | -0.6% |
| 2026-08-10 08:43 | IBM | no | +0.3% | +0.9% | +0.6% | +1.5% |
| 2026-08-13 09:01 | AMD | no | +0.0% | +6.5% | +0.0% | +6.5% |
| 2026-08-17 08:41 | NVDA | no | -0.1% | -2.3% | -0.4% | -2.8% |
| 2026-09-18 16:17 | AVGO | no | +3.0% | +1.6% | +1.1% | +1.6% |
| 2026-10-26 09:03 | TXN | YES | +4.7% | +3.6% | +3.2% | +6.9% |
| 2026-10-27 16:23 | AVGO | no | +2.8% | -1.9% | +0.7% | -1.2% |
| 2026-11-05 08:14 | AAPL | YES | -1.5% | -0.5% | -2.7% | -3.3% |
| 2026-11-09 08:01 | IBM | no | +0.5% | +0.0% | +0.0% | +0.1% |
| 2026-11-09 08:47 | QCOM | YES | +3.7% | +1.2% | +4.0% | +5.2% |

Source: SEC EDGAR submissions (public domain). A filing says debt was raised, not how much; deals of every size count the same.
