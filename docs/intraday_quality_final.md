# Intraday data — the final table the tests use

Main file or patch file per day (never both inside a day). Usable session = at least 90% of the 390 session minutes; trading halts are kept. 'Needed' = Fed statement days, document days and event days from June 2010.

| instrument | trading days | usable session | on needed days: usable session | usable 08:30 window | usable 14:00 window | days from the patch file |
|---|---|---|---|---|---|---|
| NQ | 4,028 | 99.90% | 100.00% (0 fail of 667) | 98.35% | 100.00% | 0 |
| ES | 4,028 | 100.00% | 100.00% (0 fail of 667) | 99.55% | 100.00% | 0 |
| GC | 4,028 | 97.67% | 97.60% (16 fail of 667) | 99.25% | 98.20% | 0 |
| ZN | 4,027 | 98.88% | 99.25% (5 fail of 667) | 100.00% | 99.40% | 0 |

## Needed days still short on the session or a release window (35 instrument-days)

| instrument | date | session minutes | 08:30 window minutes (of 15) | 14:00 window minutes (of 35) | longest gap | source | vendor flag |
|---|---|---|---|---|---|---|---|
| GC | 2011-11-30 | 205 | 13 | 11 | 9 | main | available |
| NQ | 2011-12-14 | 385 | 11 | 32 | 1 | main | available |
| ZN | 2012-06-01 | 322 | 15 | 24 | 6 | main | available |
| NQ | 2013-06-19 | 378 | 4 | 35 | 2 | main | available |
| GC | 2013-07-31 | 289 | 13 | 30 | 5 | main | available |
| NQ | 2013-09-18 | 386 | 11 | 35 | 1 | main | available |
| NQ | 2014-03-19 | 386 | 10 | 35 | 2 | main | available |
| NQ | 2014-06-18 | 389 | 11 | 35 | 1 | main | available |
| GC | 2015-03-30 | 345 | 15 | 35 | 5 | main | available |
| NQ | 2015-09-17 | 390 | 9 | 35 | 0 | main | available |
| GC | 2016-01-29 | 202 | 15 | 8 | 12 | main | available |
| NQ | 2016-06-15 | 390 | 9 | 35 | 0 | main | available |
| ZN | 2016-12-01 | 328 | 14 | 23 | 4 | main | available |
| GC | 2017-11-29 | 348 | 15 | 32 | 4 | main | available |
| GC | 2017-11-30 | 107 | 10 | 6 | 27 | main | available |
| ZN | 2017-11-30 | 340 | 15 | 34 | 3 | main | available |
| GC | 2018-01-31 | 89 | 4 | 17 | 36 | main | available |
| GC | 2019-01-30 | 332 | 15 | 33 | 5 | main | available |
| GC | 2019-07-31 | 128 | 7 | 20 | 16 | main | available |
| GC | 2020-02-27 | 231 | 15 | 0 | 159 | main | degraded |
| ZN | 2020-02-27 | 230 | 15 | 0 | 160 | main | degraded |
| NQ | 2020-03-09 | 376 | 6 | 35 | 13 | main | available |
| ES | 2020-03-13 | 390 | 10 | 35 | 0 | main | available |
| NQ | 2020-03-13 | 390 | 5 | 35 | 0 | main | available |
| ES | 2020-03-16 | 376 | 5 | 35 | 14 | main | available |
| NQ | 2020-03-16 | 376 | 0 | 35 | 14 | main | available |
| ES | 2020-03-18 | 377 | 8 | 35 | 13 | main | available |
| NQ | 2020-03-18 | 377 | 0 | 35 | 13 | main | available |
| GC | 2021-03-30 | 254 | 15 | 19 | 10 | main | available |
| GC | 2022-11-30 | 91 | 7 | 9 | 31 | main | available |
| GC | 2023-05-31 | 58 | 3 | 1 | 41 | main | available |
| ZN | 2023-05-31 | 274 | 13 | 17 | 6 | main | available |
| GC | 2024-07-30 | 203 | 12 | 9 | 35 | main | available |
| GC | 2025-07-30 | 202 | 15 | 11 | 15 | main | available |
| GC | 2026-07-30 | 142 | 12 | 2 | 36 | main | available |
