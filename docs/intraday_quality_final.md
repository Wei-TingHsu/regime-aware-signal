# Intraday data — the final table the tests use

Main file or patch file per day (never both inside a day). Usable session = at least 90% of the 390 session minutes; trading halts are kept. 'Needed' = Fed statement days, document days and event days from June 2010.

| instrument | trading days | usable session | on needed days: usable session | usable 08:30 window | usable 14:00 window | days from the patch file |
|---|---|---|---|---|---|---|
| NQ | 4,112 | 99.56% | 100.00% (0 fail of 673) | 99.11% | 100.00% | 141 |
| ES | 4,112 | 99.56% | 100.00% (0 fail of 673) | 99.55% | 100.00% | 85 |
| GC | 4,113 | 99.76% | 99.85% (1 fail of 673) | 100.00% | 99.85% | 89 |
| ZN | 4,117 | 99.66% | 99.85% (1 fail of 673) | 100.00% | 99.85% | 40 |

## Needed days still short on the session or a release window (11 instrument-days)

| instrument | date | session minutes | 08:30 window minutes (of 15) | 14:00 window minutes (of 35) | longest gap | source | vendor flag |
|---|---|---|---|---|---|---|---|
| NQ | 2015-09-17 | 390 | 9 | 35 | 0 | main | available |
| NQ | 2016-06-15 | 390 | 9 | 35 | 0 | main | available |
| GC | 2020-02-27 | 231 | 15 | 0 | 159 | main | degraded |
| ZN | 2020-02-27 | 231 | 15 | 0 | 159 | patch | degraded |
| NQ | 2020-03-09 | 376 | 6 | 35 | 13 | main | available |
| ES | 2020-03-13 | 390 | 10 | 35 | 0 | main | available |
| NQ | 2020-03-13 | 390 | 5 | 35 | 0 | main | available |
| ES | 2020-03-16 | 376 | 5 | 35 | 14 | main | available |
| NQ | 2020-03-16 | 376 | 0 | 35 | 14 | main | available |
| ES | 2020-03-18 | 377 | 8 | 35 | 13 | main | available |
| NQ | 2020-03-18 | 377 | 0 | 35 | 13 | main | available |
