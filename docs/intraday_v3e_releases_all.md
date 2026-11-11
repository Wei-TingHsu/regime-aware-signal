# E2 — the 08:30 data releases, minute by minute

974 release days (jobs, consumer prices, producer prices, job openings, import/export prices) that fall within ten sessions after a ≥ 4% move and have a composition score. Returns in basis points; cost 2 bp round trip. Placebo: the same rule at 08:30 on days without such a release (some of those days carry other 08:30 releases, so the placebo is a strict one).

First 5 minutes of the S&P future: mean absolute move 15.1 bp. The first move has the same sign as the document's composition score on **61%** of days (n 605; 50% = the score says nothing about the first move).

## Rule: enter in the direction of the S&P future's own first k minutes (+ = the first move continues, − = it reverses)

### S&P 500 (974 days)

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +0.6 bp (t +1.2, hit 45%, n 974) | +1.0 bp (t +1.5, hit 47%, n 974) | +0.9 bp (t +1.2, hit 45%, n 969) | -1.1 bp (t -0.4, hit 47%, n 967) |
| 5 min | +0.2 bp (t +0.3, hit 46%, n 974) | -0.0 bp (t -0.1, hit 46%, n 974) | -0.5 bp (t -0.7, hit 44%, n 969) | -2.7 bp (t -1.0, hit 47%, n 967) |
| 15 min | +0.3 bp (t +0.7, hit 45%, n 974) | +0.4 bp (t +0.7, hit 45%, n 974) | +0.0 bp (t +0.0, hit 45%, n 968) | -3.4 bp (t -1.3, hit 48%, n 967) |
| 30 min | +0.1 bp (t +0.2, hit 45%, n 974) | -0.2 bp (t -0.5, hit 47%, n 968) | -1.2 bp (t -1.1, hit 48%, n 969) | -5.4 bp (t -2.1, hit 47%, n 967) |

Best cell: enter 30 min, hold close: -5.4 bp, t -2.11, hit 47%; **family p 0.326**; placebo days +0.2 bp, p vs placebo 0.011.

### Nasdaq-100 (974 days)

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +0.8 bp (t +1.3, hit 47%, n 974) | +1.3 bp (t +1.6, hit 47%, n 974) | +1.6 bp (t +1.7, hit 47%, n 969) | -2.2 bp (t -0.7, hit 47%, n 967) |
| 5 min | +0.1 bp (t +0.2, hit 48%, n 974) | +0.0 bp (t +0.1, hit 49%, n 974) | -0.9 bp (t -0.9, hit 47%, n 969) | -4.7 bp (t -1.4, hit 46%, n 967) |
| 15 min | +0.4 bp (t +0.9, hit 46%, n 974) | +0.6 bp (t +0.9, hit 47%, n 974) | -1.4 bp (t -1.2, hit 45%, n 968) | -6.0 bp (t -1.9, hit 46%, n 967) |
| 30 min | +0.1 bp (t +0.2, hit 47%, n 974) | -0.5 bp (t -1.0, hit 47%, n 969) | -3.0 bp (t -2.1, hit 45%, n 969) | -7.9 bp (t -2.5, hit 46%, n 967) |

Best cell: enter 30 min, hold close: -7.9 bp, t -2.46, hit 46%; **family p 0.170**; placebo days -1.0 bp, p vs placebo 0.013.

## Rule: enter in the direction of the document's composition score

### S&P 500 (974 days)

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +1.1 bp (t +2.5, hit 32%, n 974) | +1.5 bp (t +2.5, hit 33%, n 974) | +1.2 bp (t +1.7, hit 34%, n 969) | +1.2 bp (t +0.5, hit 32%, n 967) |
| 5 min | +1.1 bp (t +2.9, hit 33%, n 974) | +1.1 bp (t +2.2, hit 32%, n 974) | +1.1 bp (t +1.6, hit 33%, n 969) | +0.9 bp (t +0.4, hit 32%, n 967) |
| 15 min | +0.6 bp (t +1.7, hit 32%, n 974) | +0.7 bp (t +1.5, hit 33%, n 974) | +0.2 bp (t +0.3, hit 31%, n 968) | +0.3 bp (t +0.1, hit 32%, n 967) |
| 30 min | +0.1 bp (t +0.4, hit 30%, n 974) | -0.2 bp (t -0.7, hit 30%, n 968) | +0.2 bp (t +0.2, hit 33%, n 969) | -0.3 bp (t -0.1, hit 31%, n 967) |

Best cell: enter 5 min, hold 15: +1.1 bp, t +2.86, hit 33%; **family p 0.033**.

### Nasdaq-100 (974 days)

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +1.0 bp (t +1.9, hit 33%, n 974) | +1.7 bp (t +2.5, hit 34%, n 974) | +2.1 bp (t +2.5, hit 34%, n 969) | +1.7 bp (t +0.6, hit 32%, n 967) |
| 5 min | +1.2 bp (t +2.5, hit 33%, n 974) | +1.5 bp (t +2.4, hit 33%, n 974) | +1.9 bp (t +2.3, hit 33%, n 969) | +1.3 bp (t +0.5, hit 31%, n 967) |
| 15 min | +0.9 bp (t +2.4, hit 34%, n 974) | +1.4 bp (t +2.7, hit 34%, n 974) | +1.3 bp (t +1.4, hit 33%, n 968) | +0.8 bp (t +0.3, hit 32%, n 967) |
| 30 min | +0.5 bp (t +1.4, hit 31%, n 974) | +0.4 bp (t +0.9, hit 32%, n 969) | +0.5 bp (t +0.5, hit 31%, n 969) | -0.0 bp (t -0.0, hit 31%, n 967) |

Best cell: enter 15 min, hold 30: +1.4 bp, t +2.75, hit 34%; **family p 0.057**.

## Rule: only days where the first 5 minutes went AGAINST the score: enter in the direction of the score (does the price come round to the document?)

### S&P 500 (235 days)

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 5 min | +2.3 bp (t +2.4, hit 52%, n 235) | +3.0 bp (t +2.4, hit 49%, n 235) | +5.1 bp (t +2.8, hit 58%, n 235) | +10.8 bp (t +1.9, hit 53%, n 234) |
| 15 min | +1.0 bp (t +1.2, hit 51%, n 235) | +2.0 bp (t +1.9, hit 54%, n 235) | +4.2 bp (t +2.2, hit 58%, n 234) | +9.0 bp (t +1.6, hit 53%, n 234) |
| 30 min | +1.1 bp (t +1.7, hit 51%, n 235) | +1.0 bp (t +1.2, hit 49%, n 234) | +4.1 bp (t +1.9, hit 55%, n 235) | +8.1 bp (t +1.4, hit 51%, n 234) |

Best cell: enter 5 min, hold 60: +5.1 bp, t +2.82, hit 58%; **family p 0.033**.

### Nasdaq-100 (235 days)

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 5 min | +2.8 bp (t +2.5, hit 53%, n 235) | +4.0 bp (t +2.6, hit 52%, n 235) | +7.9 bp (t +3.6, hit 60%, n 235) | +15.8 bp (t +2.2, hit 55%, n 234) |
| 15 min | +1.6 bp (t +1.7, hit 55%, n 235) | +3.4 bp (t +2.8, hit 56%, n 235) | +8.8 bp (t +3.6, hit 61%, n 234) | +13.9 bp (t +2.0, hit 56%, n 234) |
| 30 min | +1.9 bp (t +2.4, hit 54%, n 235) | +2.3 bp (t +2.2, hit 55%, n 235) | +8.0 bp (t +2.7, hit 54%, n 235) | +12.3 bp (t +1.7, hit 56%, n 234) |

Best cell: enter 5 min, hold 60: +7.9 bp, t +3.63, hit 60%; **family p 0.002**.

## Replication on NEW days only (release days that were not in the first run)

The first run used the 303 release days within ten sessions after a ≥ 4% move. The 671 other release days were never looked at. The exact cells the first run pointed to are tested on them alone — no search over cells, one-sided p from 2,000 shuffles of the scores.

| rule (fixed from the first run) | future | days | mean | t | hit | p |
|---|---|---|---|---|---|---|
| first 5 minutes against the score → enter with the score at 5 min, hold 60 | Nasdaq-100 | 144 | +3.7 bp | +1.79 | 60% | 0.028 |
| same | S&P 500 | 144 | +3.1 bp | +1.96 | 56% | 0.024 |
| enter with the score at 5 min, hold 30 (all days) | Nasdaq-100 | 392 | +0.6 bp | +0.58 | 52% | 0.234 |
| same | S&P 500 | 392 | +0.6 bp | +0.60 | 51% | 0.215 |

## Days left out

No S&P future price at 08:30 or 08:35 (overnight price-limit halts): none.
