# T13 A1 attribution — big-move days by state and day type

*Run 2026-10-09 16:26. Release dates from ALFRED vintage dates (NFP, CPI, claims, GDP, PCE, retail); FOMC from the decisions file; reports from `48a6c4e879a1_n2617`. Big move = |z| > 2.0. Document days only (the engine wrote a report).*

## SPY — 100 big-move document days

| state | FOMC day | data-print day | neither |
|---|---|---|---|
| A blind | 1 | 20 | 27 |
| B wrong | 6 | 7 | 18 |
| C seen | 6 | 6 | 9 |

## TLT — 82 big-move document days

| state | FOMC day | data-print day | neither |
|---|---|---|---|
| A blind | 0 | 26 | 36 |
| B wrong | 4 | 4 | 6 |
| C seen | 3 | 0 | 3 |

## GLD — 101 big-move document days

| state | FOMC day | data-print day | neither |
|---|---|---|---|
| A blind | 1 | 33 | 37 |
| B wrong | 9 | 3 | 4 |
| C seen | 9 | 1 | 4 |

## UUP — 89 big-move document days

| state | FOMC day | data-print day | neither |
|---|---|---|---|
| A blind | 1 | 37 | 20 |
| B wrong | 7 | 3 | 3 |
| C seen | 13 | 0 | 5 |

## USO — 80 big-move document days

| state | FOMC day | data-print day | neither |
|---|---|---|---|
| A blind | 6 | 19 | 44 |
| B wrong | 1 | 1 | 3 |
| C seen | 2 | 1 | 3 |

## Reading

- Across all five markets, **36%** of big-move document days are scheduled data-print days and **15%** are FOMC days; **49%** are neither (the move came from something outside both calendars).
- Of the **B (wrong)** days, 23% are print days — the document present was not the driver (misattribution, fixed by coverage), 34% are FOMC days — the reader scored the level, not the surprise (fixed by expectations), and 43% are neither (candidates for a genuine misread, or an uncovered driver).

Print-day detail (which releases) is in the per-day table below for the B days.

| asset | date | z | detail |
|---|---|---|---|
| SPY | 2008-06-05 | +2.2 | print:claims |
| SPY | 2008-07-16 | +2.0 | print:CPI |
| TLT | 2008-07-16 | -2.8 | print:CPI |
| GLD | 2011-03-15 | -2.4 | FOMC |
| SPY | 2011-06-01 | -3.4 | neither |
| TLT | 2012-03-13 | -2.1 | FOMC |
| USO | 2012-06-20 | -2.3 | FOMC |
| UUP | 2013-02-20 | +2.6 | neither |
| GLD | 2013-02-20 | -3.9 | neither |
| SPY | 2013-02-20 | -2.2 | neither |
| USO | 2013-02-20 | -2.7 | neither |
| SPY | 2013-05-31 | -2.3 | print:PCE+retail |
| TLT | 2013-11-20 | -2.2 | print:CPI+retail |
| GLD | 2013-11-20 | -2.3 | print:CPI+retail |
| GLD | 2014-03-19 | -2.1 | FOMC |
| SPY | 2014-12-17 | +2.6 | FOMC |
| UUP | 2015-03-18 | -3.1 | FOMC |
| GLD | 2015-03-18 | +2.1 | FOMC |
| SPY | 2015-07-08 | -2.4 | neither |
| TLT | 2016-05-18 | -2.1 | neither |
| GLD | 2016-09-21 | +2.1 | FOMC |
| SPY | 2016-12-07 | +2.5 | neither |
| SPY | 2017-03-15 | +2.0 | FOMC |
| UUP | 2017-03-15 | -2.8 | FOMC |
| GLD | 2017-03-15 | +3.1 | FOMC |
| SPY | 2017-04-24 | +2.4 | neither |
| TLT | 2017-06-14 | +3.0 | FOMC |
| UUP | 2017-11-22 | -2.3 | print:claims |
| UUP | 2017-12-13 | -2.3 | FOMC |
| UUP | 2018-03-21 | -2.0 | FOMC |
| GLD | 2018-03-21 | +3.2 | FOMC |
| SPY | 2018-10-24 | -3.0 | neither |
| TLT | 2018-12-19 | +2.5 | FOMC |
| SPY | 2019-07-31 | -2.0 | FOMC |
| UUP | 2019-07-31 | +2.0 | FOMC |
| SPY | 2019-10-02 | -2.2 | neither |
| SPY | 2020-03-12 | -3.1 | print:claims |
| SPY | 2020-03-16 | -2.7 | neither |
| GLD | 2020-08-11 | -5.4 | neither |
| UUP | 2020-08-19 | +2.1 | neither |
| TLT | 2020-08-27 | -2.5 | FOMC |
| TLT | 2021-01-06 | -3.4 | neither |
| SPY | 2021-01-27 | -3.5 | FOMC |
| GLD | 2021-06-16 | -2.3 | FOMC |
| UUP | 2021-06-16 | +2.6 | FOMC |
| SPY | 2021-09-28 | -3.0 | neither |
| GLD | 2021-10-13 | +2.3 | print:CPI |
| SPY | 2022-04-26 | -2.3 | neither |
| SPY | 2022-06-13 | -2.1 | neither |
| SPY | 2023-04-25 | -2.1 | neither |
| SPY | 2023-04-27 | +2.4 | print:claims+GDP |
| TLT | 2023-07-27 | -2.5 | print:claims+GDP |
| TLT | 2023-08-23 | +2.5 | neither |
| GLD | 2023-12-13 | +2.4 | FOMC |
| SPY | 2023-12-20 | -2.1 | neither |
| SPY | 2024-01-31 | -2.7 | FOMC |
| UUP | 2024-04-10 | +3.6 | print:CPI |
| TLT | 2024-04-10 | -2.6 | print:CPI |
| SPY | 2024-07-17 | -2.6 | neither |
| GLD | 2024-10-31 | -2.1 | print:claims+PCE |
| GLD | 2025-02-10 | +2.1 | neither |
| SPY | 2025-03-03 | -2.0 | neither |
| SPY | 2025-03-10 | -2.6 | neither |
| USO | 2025-04-03 | -5.2 | print:claims |
| UUP | 2025-04-03 | -4.5 | print:claims |
| SPY | 2025-04-03 | -4.6 | print:claims |
| TLT | 2025-04-07 | -3.9 | neither |
| GLD | 2025-04-07 | -2.2 | neither |
| SPY | 2025-04-09 | +4.8 | neither |
| USO | 2025-04-09 | +2.3 | neither |
| GLD | 2026-01-28 | +2.4 | FOMC |
| USO | 2026-04-08 | -2.3 | neither |
| SPY | 2026-04-08 | +2.4 | neither |
| SPY | 2026-06-05 | -3.9 | print:NFP |
| TLT | 2026-06-24 | +2.5 | neither |
| UUP | 2026-07-29 | -2.0 | FOMC |
| SPY | 2026-07-29 | -2.1 | FOMC |
| UUP | 2026-08-19 | -3.1 | neither |
| TLT | 2026-08-19 | +2.8 | neither |
