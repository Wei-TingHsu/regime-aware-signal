# T13 case A — blind-spot backfill

*Run 2026-10-08 16:28. Registered in `docs/prereg_blindspot.md`. 1995-01-03 → 2026-10-08; big move = |z| > 2.0; chain rule W2-seq: oil ≥ +8%/5s & dollar ≥ +0.9%/5s with the 2-year < +10 bp at the shock, confirming ≥ +10 bp within 5 sessions.*

## A1 — state shares on big-move days (reports from `outputs/reports_backfill/48a6c4e879a1_n2617`)

| market | big-move days | A blind | B wrong | C seen |
|---|---|---|---|---|
| SPY | 100 | 48% | 31% | 21% |
| TLT | 82 | 76% | 17% | 7% |
| GLD | 101 | 70% | 16% | 14% |
| UUP | 89 | 65% | 15% | 20% |
| USO | 80 | 86% | 6% | 8% |

*Only document days have reports, so these shares describe big moves on days the engine wrote a report; big moves on days with no documents at all are state A by definition and are counted in A2's denominator, not here.*

## A2 — chain alerts and gold's forward return

Chain alert runs: **2** (2022-03-07, 2026-03-05)

| horizon | n | mean gold return after alert | one-sided p vs random dates |
|---|---|---|---|
| 20 sessions | 2 | -5.750% | — |
| 60 sessions | 2 | -10.218% | 0.0080 |

## Verdict A2: **INCONCLUSIVE** (registered prior: INCONCLUSIVE — held)

A PASS is the only verdict under which the gold card's chain alert may carry a direction. The rule was calibrated to fire inside both named wars (2022-03-01→confirm 2022-03-07; 2026-03-03→confirm 2026-03-05) and on no rates-first episode; see docs/chain_calibration_round2.md.
