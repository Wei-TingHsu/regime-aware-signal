# T13 case A — blind-spot backfill

*Run 2026-10-08 16:07. Registered in `docs/prereg_blindspot.md`. 1995-01-03 → 2026-10-08; big move = |z| > 2.0; chain window 5 sessions, DGS2 ≥ 10 bp.*

## A1 — state shares on big-move days (reports from `outputs/reports_backfill/48a6c4e879a1_n2617_altinstr`)

| market | big-move days | A blind | B wrong | C seen |
|---|---|---|---|---|
| SPY | 100 | 100% | 0% | 0% |
| TLT | 82 | 100% | 0% | 0% |
| GLD | 101 | 100% | 0% | 0% |
| UUP | 89 | 100% | 0% | 0% |
| USO | 80 | 100% | 0% | 0% |

*Only document days have reports, so these shares describe big moves on days the engine wrote a report; big moves on days with no documents at all are state A by definition and are counted in A2's denominator, not here.*

## A2 — chain alerts and gold's forward return

Chain alert runs: **23** (2006-04-12, 2007-12-13, 2007-12-18, 2008-02-20, 2008-06-09, 2009-07-30, 2014-12-19, 2015-08-31, 2015-10-29, 2015-11-02, 2016-11-15, 2016-11-17, 2016-11-23, 2018-04-19, 2018-04-23, 2022-03-07, 2023-10-03, 2023-10-17, 2024-05-28, 2025-01-10 …)

| horizon | n | mean gold return after alert | one-sided p vs random dates |
|---|---|---|---|
| 20 sessions | 23 | +0.516% | — |
| 60 sessions | 23 | +0.849% | 0.2829 |

## Verdict A2: **FAIL** (registered prior: INCONCLUSIVE — wrong)

A PASS is the only verdict under which the gold card's chain alert may carry a direction. Named precedents: 2022-03 (Ukraine) and 2026-03 (Iran) — reported whether or not they fall inside the alert set.
