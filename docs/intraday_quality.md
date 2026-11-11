# Intraday data quality — CME futures, 1-minute bars (Databento GLBX.MDP3)

One row per instrument per weekday. 'Trading days' = days the S&P future traded a full session. Nothing in the raw files is altered; the flags in `processed/intraday_quality.parquet` decide which days a test may use.
Rules: usable session = ≥ 90% of the 390 session minutes present and no gap over 5 minutes; usable 08:30 window = ≥ 12 of 15 minutes; usable 14:00 window = ≥ 28 of 35 minutes.

| instrument | trading days | days missing entirely | median session minutes (of 390) | usable session | usable 08:30 | usable 14:00 | invalid bars | duplicate times | moves > 1% | spikes | daily move vs ETF: correlation / days differing > 0.5% |
|---|---|---|---|---|---|---|---|---|---|---|---|
| NQ | 4,028 | 0 | 390 | 99.8% | 99.3% | 99.9% | 0 | 0 | 59 | 240 | +0.86 with SOXX / 55% |
| ES | 4,028 | 0 | 390 | 99.9% | 99.9% | 100.0% | 0 | 0 | 51 | 183 | +0.99 with SPY / 1% |
| GC | 3,904 | 124 | 9 | 0.8% | 2.5% | 1.1% | 0 | 0 | 8 | 9 | +0.93 with GLD / 12% |
| GCv | 4,028 | 0 | 390 | 97.6% | 99.1% | 97.9% | 0 | 0 | 27 | 78 | +0.98 with GLD / 2% |
| ZN | 4,027 | 1 | 389 | 77.3% | 82.2% | 78.1% | 0 | 0 | 1 | 4 | +0.84 with TLT / 39% |
| ZNv | 4,027 | 1 | 390 | 98.9% | 100.0% | 99.2% | 0 | 0 | 1 | 2 | +0.84 with TLT / 38% |

## By year — share of trading days with a usable session

| year | NQ | ES | GC | GCv | ZN | ZNv |
|---|---|---|---|---|---|---|
| 2010 | 100% (median 390 min) | 100% (median 390 min) | 1% (median 19 min) | 99% (median 389 min) | 73% (median 389 min) | 98% (median 389 min) |
| 2011 | 100% (median 390 min) | 100% (median 390 min) | 2% (median 22 min) | 99% (median 390 min) | 79% (median 389 min) | 99% (median 389 min) |
| 2012 | 99% (median 390 min) | 100% (median 390 min) | 2% (median 13 min) | 98% (median 390 min) | 78% (median 388 min) | 98% (median 389 min) |
| 2013 | 100% (median 390 min) | 100% (median 390 min) | 2% (median 17 min) | 98% (median 390 min) | 78% (median 388 min) | 99% (median 388 min) |
| 2014 | 100% (median 390 min) | 100% (median 390 min) | 2% (median 14 min) | 98% (median 389 min) | 76% (median 387 min) | 99% (median 388 min) |
| 2015 | 100% (median 390 min) | 100% (median 390 min) | 1% (median 13 min) | 98% (median 390 min) | 78% (median 389 min) | 100% (median 389 min) |
| 2016 | 100% (median 390 min) | 100% (median 390 min) | 1% (median 12 min) | 98% (median 390 min) | 77% (median 389 min) | 98% (median 389 min) |
| 2017 | 100% (median 390 min) | 100% (median 390 min) | 0% (median 9 min) | 97% (median 390 min) | 77% (median 389 min) | 98% (median 389 min) |
| 2018 | 100% (median 390 min) | 100% (median 390 min) | 0% (median 4 min) | 96% (median 390 min) | 80% (median 389 min) | 99% (median 389 min) |
| 2019 | 100% (median 390 min) | 100% (median 390 min) | 1% (median 6 min) | 98% (median 390 min) | 78% (median 390 min) | 99% (median 390 min) |
| 2020 | 98% (median 390 min) | 98% (median 390 min) | 0% (median 9 min) | 97% (median 390 min) | 76% (median 390 min) | 98% (median 390 min) |
| 2021 | 100% (median 390 min) | 100% (median 390 min) | 0% (median 8 min) | 97% (median 390 min) | 77% (median 390 min) | 99% (median 390 min) |
| 2022 | 100% (median 390 min) | 100% (median 390 min) | 0% (median 6 min) | 98% (median 390 min) | 77% (median 390 min) | 100% (median 390 min) |
| 2023 | 100% (median 390 min) | 100% (median 390 min) | 0% (median 4 min) | 97% (median 390 min) | 77% (median 390 min) | 99% (median 390 min) |
| 2024 | 100% (median 390 min) | 100% (median 390 min) | 0% (median 4 min) | 98% (median 390 min) | 77% (median 390 min) | 99% (median 390 min) |
| 2025 | 100% (median 390 min) | 100% (median 390 min) | 0% (median 10 min) | 98% (median 390 min) | 76% (median 390 min) | 99% (median 390 min) |
| 2026 | 100% (median 390 min) | 100% (median 390 min) | 0% (median 5 min) | 98% (median 390 min) | 79% (median 390 min) | 100% (median 390 min) |

## Databento's own 'degraded' days

- NQ: 17 degraded trading days — usable session 100% (other days 100%); median session minutes 390 vs 390; of the days the tests need, 5 are degraded and 0 of those fail the session rule
- ES: 17 degraded trading days — usable session 100% (other days 100%); median session minutes 390 vs 390; of the days the tests need, 5 are degraded and 0 of those fail the session rule
- GC: 16 degraded trading days — usable session 0% (other days 1%); median session minutes 2 vs 9; of the days the tests need, 5 are degraded and 5 of those fail the session rule
- GCv: 17 degraded trading days — usable session 82% (other days 98%); median session minutes 390 vs 390; of the days the tests need, 5 are degraded and 1 of those fail the session rule
- ZN: 17 degraded trading days — usable session 53% (other days 77%); median session minutes 385 vs 389; of the days the tests need, 5 are degraded and 3 of those fail the session rule
- ZNv: 17 degraded trading days — usable session 82% (other days 99%); median session minutes 390 vs 390; of the days the tests need, 5 are degraded and 1 of those fail the session rule

Degraded days that the tests need (5): 2019-01-15, 2020-02-27, 2024-09-18, 2025-09-17, 2026-04-10

## The days the tests need (Fed statement days, document days, event days; from June 2010)

| instrument | needed days with data | usable session | usable 08:30 | usable 14:00 |
|---|---|---|---|---|
| NQ | 673 of 675 | 98.5% | 98.4% | 99.1% |
| ES | 673 of 675 | 98.5% | 99.6% | 99.1% |
| GC | 648 of 675 | 0.5% | 2.3% | 1.1% |
| GCv | 673 of 675 | 97.6% | 99.3% | 98.2% |
| ZN | 673 of 675 | 66.6% | 71.3% | 67.3% |
| ZNv | 673 of 675 | 99.3% | 100.0% | 99.4% |

## Days with the most spikes (a jump taken back within a minute)

| instrument | date | spikes | largest one-minute move |
|---|---|---|---|
| NQ | 2020-03-17 | 22 | 0.94% |
| ES | 2020-03-17 | 21 | 1.79% |
| NQ | 2020-03-18 | 17 | 1.72% |
| NQ | 2020-03-13 | 17 | 1.12% |
| ES | 2020-03-23 | 16 | 1.22% |
| ES | 2020-03-13 | 16 | 1.03% |
| ES | 2020-03-18 | 15 | 1.33% |
| NQ | 2020-03-19 | 12 | 0.84% |
| NQ | 2025-04-07 | 11 | 1.77% |
| ES | 2020-03-16 | 10 | 1.26% |
