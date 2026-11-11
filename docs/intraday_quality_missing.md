# Intraday data — are the days that fail the quality rules the extreme days?

Instruments the tests use: NQ, ES, GCv, ZNv. 'Needed' = Fed statement days, official-document days and ≥ 4% event days from June 2010.

- NQ: 238 of 4258 weekdays fail the session rule (5.6%); causes: market-wide (early close or halt) 154, this instrument only 84. Median S&P move on failing days 0.39% vs 0.49% on passing days. Of the 207 largest-move days (top 5% by S&P move), 7 fail (3.4%). Needed days failing: 10.
- ES: 234 of 4258 weekdays fail the session rule (5.5%); causes: market-wide (early close or halt) 154, this instrument only 80. Median S&P move on failing days 0.39% vs 0.49% on passing days. Of the 207 largest-move days (top 5% by S&P move), 7 fail (3.4%). Needed days failing: 10.
- GCv: 247 of 4260 weekdays fail the session rule (5.8%); causes: market-wide (early close or halt) 146, this instrument only 98, vendor: degraded day 3. Median S&P move on failing days 0.51% vs 0.48% on passing days. Of the 207 largest-move days (top 5% by S&P move), 7 fail (3.4%). Needed days failing: 16.
- ZNv: 199 of 4263 weekdays fail the session rule (4.7%); causes: market-wide (early close or halt) 154, this instrument only 42, vendor: degraded day 3. Median S&P move on failing days 0.35% vs 0.49% on passing days. Of the 207 largest-move days (top 5% by S&P move), 5 fail (2.4%). Needed days failing: 5.

## Needed days that fail the session rule

| instrument | date | session minutes (of 390) | longest gap | 08:30 window ok | 14:00 window ok | vendor flag | cause | S&P move that day |
|---|---|---|---|---|---|---|---|---|
| GCv | 2011-11-30 | 205 | 9 | True | False | available | this instrument only | 4.03% |
| ZNv | 2012-06-01 | 322 | 6 | True | False | available | this instrument only | 2.55% |
| GCv | 2013-07-31 | 289 | 5 | True | True | available | this instrument only | 0.07% |
| GCv | 2015-03-30 | 345 | 5 | True | True | available | this instrument only | 1.21% |
| GCv | 2016-01-29 | 202 | 12 | True | False | available | this instrument only | 2.41% |
| ZNv | 2016-12-01 | 328 | 4 | True | False | available | this instrument only | 0.37% |
| GCv | 2017-11-29 | 348 | 4 | True | True | available | this instrument only | 0.06% |
| GCv | 2017-11-30 | 107 | 27 | False | False | available | this instrument only | 0.87% |
| ZNv | 2017-11-30 | 340 | 3 | True | True | available | this instrument only | 0.87% |
| GCv | 2018-01-31 | 89 | 36 | False | False | available | this instrument only | 0.05% |
| GCv | 2019-01-30 | 332 | 5 | True | True | available | this instrument only | 1.57% |
| GCv | 2019-07-31 | 128 | 16 | False | False | available | this instrument only | 1.10% |
| GCv | 2020-02-27 | 231 | 159 | True | False | degraded | vendor: degraded day | 4.60% |
| ZNv | 2020-02-27 | 230 | 160 | True | False | degraded | vendor: degraded day | 4.60% |
| ES | 2020-03-09 | 377 | 13 | True | True | available | this instrument only | 8.13% |
| NQ | 2020-03-09 | 376 | 13 | False | True | available | this instrument only | 8.13% |
| ES | 2020-03-12 | 377 | 13 | True | True | available | this instrument only | 10.06% |
| NQ | 2020-03-12 | 377 | 13 | True | True | available | this instrument only | 10.06% |
| ES | 2020-03-16 | 376 | 14 | False | True | available | this instrument only | 11.59% |
| NQ | 2020-03-16 | 376 | 14 | False | True | available | this instrument only | 11.59% |
| ES | 2020-03-18 | 377 | 13 | False | True | available | this instrument only | 5.20% |
| NQ | 2020-03-18 | 377 | 13 | False | True | available | this instrument only | 5.20% |
| ES | 2020-03-20 | 0 | 390 | True | False | available | this instrument only | 4.41% |
| NQ | 2020-03-20 | 0 | 390 | True | False | available | this instrument only | 4.41% |
| ES | 2020-06-19 | 0 | 390 | True | False | available | this instrument only | 0.57% |
| NQ | 2020-06-19 | 0 | 390 | True | False | available | this instrument only | 0.57% |
| GCv | 2021-03-30 | 254 | 10 | True | False | available | this instrument only | 0.27% |
| ES | 2022-06-17 | 0 | 390 | True | False | available | this instrument only | 0.22% |
| NQ | 2022-06-17 | 0 | 390 | True | False | available | this instrument only | 0.22% |
| GCv | 2022-11-30 | 91 | 31 | False | False | available | this instrument only | 3.10% |
| GCv | 2023-05-31 | 58 | 41 | False | False | available | this instrument only | 0.56% |
| ZNv | 2023-05-31 | 274 | 6 | True | False | available | this instrument only | 0.56% |
| ES | 2024-03-15 | 0 | 390 | True | False | available | this instrument only | 0.69% |
| NQ | 2024-03-15 | 0 | 390 | True | False | available | this instrument only | 0.69% |
| GCv | 2024-07-30 | 203 | 35 | True | False | available | this instrument only | 0.51% |
| GCv | 2025-07-30 | 202 | 15 | True | False | available | this instrument only | 0.13% |
| ES | 2026-06-18 | 0 | 390 | True | False | available | this instrument only | 1.03% |
| NQ | 2026-06-18 | 0 | 390 | True | False | available | this instrument only | 1.03% |
| GCv | 2026-07-30 | 142 | 36 | True | False | available | this instrument only | 1.66% |
| ES | 2026-09-18 | 0 | 390 | True | False | available | this instrument only | 0.13% |
| NQ | 2026-09-18 | 0 | 390 | True | False | available | this instrument only | 0.13% |
