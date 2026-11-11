# E2 — the 08:30 data releases, minute by minute

303 release days (jobs, consumer prices, producer prices, job openings, import/export prices) that fall within ten sessions after a ≥ 4% move and have a composition score. Returns in basis points; cost 2 bp round trip. Placebo: the same rule at 08:30 on days without such a release (some of those days carry other 08:30 releases, so the placebo is a strict one).

First 5 minutes of the S&P future: mean absolute move 21.0 bp. The first move has the same sign as the document's composition score on **57%** of days (n 213; 50% = the score says nothing about the first move).

## Rule: enter in the direction of the S&P future's own first k minutes (+ = the first move continues, − = it reverses)

### S&P 500 (303 days)

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +0.4 bp (t +0.4, hit 49%, n 303) | +1.5 bp (t +0.9, hit 49%, n 303) | +2.0 bp (t +1.1, hit 48%, n 303) | -4.3 bp (t -0.7, hit 50%, n 303) |
| 5 min | -0.2 bp (t -0.1, hit 43%, n 303) | +0.4 bp (t +0.3, hit 49%, n 303) | -0.6 bp (t -0.3, hit 44%, n 303) | -4.4 bp (t -0.7, hit 48%, n 303) |
| 15 min | +1.5 bp (t +1.5, hit 50%, n 303) | +1.2 bp (t +1.0, hit 49%, n 303) | +2.9 bp (t +1.3, hit 50%, n 302) | -3.2 bp (t -0.5, hit 51%, n 303) |
| 30 min | -0.1 bp (t -0.1, hit 46%, n 303) | -0.2 bp (t -0.2, hit 48%, n 302) | -1.2 bp (t -0.5, hit 52%, n 303) | -11.3 bp (t -1.9, hit 47%, n 303) |

Best cell: enter 30 min, hold close: -11.3 bp, t -1.87, hit 47%; **family p 0.537**; placebo days -0.3 bp, p vs placebo 0.015.

### Nasdaq-100 (303 days)

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +0.5 bp (t +0.4, hit 49%, n 303) | +1.7 bp (t +0.9, hit 49%, n 303) | +1.9 bp (t +0.9, hit 49%, n 303) | -7.8 bp (t -1.0, hit 48%, n 303) |
| 5 min | -0.8 bp (t -0.6, hit 44%, n 303) | -0.4 bp (t -0.2, hit 48%, n 303) | -2.0 bp (t -0.9, hit 49%, n 303) | -9.4 bp (t -1.2, hit 45%, n 303) |
| 15 min | +1.4 bp (t +1.2, hit 50%, n 303) | +1.2 bp (t +0.9, hit 49%, n 303) | +1.8 bp (t +0.6, hit 50%, n 302) | -5.8 bp (t -0.8, hit 50%, n 303) |
| 30 min | -0.4 bp (t -0.4, hit 48%, n 303) | -1.1 bp (t -0.9, hit 49%, n 303) | -3.4 bp (t -1.0, hit 49%, n 303) | -15.4 bp (t -2.0, hit 45%, n 303) |

Best cell: enter 30 min, hold close: -15.4 bp, t -2.04, hit 45%; **family p 0.390**; placebo days -1.6 bp, p vs placebo 0.011.

## Rule: enter in the direction of the document's composition score

### S&P 500 (303 days)

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +1.9 bp (t +1.7, hit 38%, n 303) | +2.8 bp (t +2.0, hit 38%, n 303) | +2.9 bp (t +1.7, hit 42%, n 303) | -3.7 bp (t -0.7, hit 34%, n 303) |
| 5 min | +2.1 bp (t +2.2, hit 37%, n 303) | +2.9 bp (t +2.5, hit 38%, n 303) | +2.8 bp (t +1.7, hit 40%, n 303) | -4.0 bp (t -0.7, hit 35%, n 303) |
| 15 min | +1.6 bp (t +2.0, hit 37%, n 303) | +1.9 bp (t +1.7, hit 41%, n 303) | -0.4 bp (t -0.2, hit 36%, n 302) | -5.4 bp (t -1.0, hit 34%, n 303) |
| 30 min | +0.3 bp (t +0.4, hit 34%, n 303) | -0.2 bp (t -0.3, hit 34%, n 302) | -1.3 bp (t -0.6, hit 38%, n 303) | -6.9 bp (t -1.3, hit 33%, n 303) |

Best cell: enter 5 min, hold 30: +2.9 bp, t +2.45, hit 38%; **family p 0.115**.

### Nasdaq-100 (303 days)

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +1.7 bp (t +1.4, hit 39%, n 303) | +3.5 bp (t +2.1, hit 39%, n 303) | +4.2 bp (t +2.1, hit 41%, n 303) | -5.4 bp (t -0.8, hit 32%, n 303) |
| 5 min | +2.8 bp (t +2.3, hit 38%, n 303) | +4.1 bp (t +2.8, hit 38%, n 303) | +5.5 bp (t +2.7, hit 40%, n 303) | -5.3 bp (t -0.8, hit 32%, n 303) |
| 15 min | +2.4 bp (t +2.4, hit 40%, n 303) | +3.5 bp (t +2.7, hit 39%, n 303) | +2.1 bp (t +0.9, hit 38%, n 302) | -6.8 bp (t -1.0, hit 31%, n 303) |
| 30 min | +1.0 bp (t +1.2, hit 36%, n 303) | +0.5 bp (t +0.5, hit 37%, n 303) | +0.3 bp (t +0.1, hit 35%, n 303) | -9.2 bp (t -1.4, hit 33%, n 303) |

Best cell: enter 5 min, hold 30: +4.1 bp, t +2.78, hit 38%; **family p 0.052**.

## Rule: only days where the first 5 minutes went AGAINST the score: enter in the direction of the score (does the price come round to the document?)

### S&P 500 (91 days)

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 5 min | +3.4 bp (t +1.7, hit 55%, n 91) | +4.6 bp (t +1.8, hit 49%, n 91) | +8.2 bp (t +2.1, hit 63%, n 91) | +8.6 bp (t +0.7, hit 48%, n 91) |
| 15 min | +1.0 bp (t +0.6, hit 48%, n 91) | +3.5 bp (t +1.5, hit 57%, n 91) | +4.5 bp (t +1.1, hit 61%, n 90) | +5.5 bp (t +0.5, hit 47%, n 91) |
| 30 min | +2.5 bp (t +2.1, hit 52%, n 91) | +2.4 bp (t +1.6, hit 52%, n 90) | +5.4 bp (t +1.2, hit 56%, n 91) | +4.5 bp (t +0.4, hit 44%, n 91) |

Best cell: enter 5 min, hold 60: +8.2 bp, t +2.10, hit 63%; **family p 0.220**.

### Nasdaq-100 (91 days)

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 5 min | +5.2 bp (t +2.2, hit 57%, n 91) | +7.2 bp (t +2.3, hit 53%, n 91) | +14.6 bp (t +3.2, hit 62%, n 91) | +14.0 bp (t +0.9, hit 49%, n 91) |
| 15 min | +2.4 bp (t +1.2, hit 56%, n 91) | +6.2 bp (t +2.4, hit 55%, n 91) | +13.2 bp (t +2.5, hit 64%, n 90) | +9.9 bp (t +0.7, hit 48%, n 91) |
| 30 min | +3.8 bp (t +2.3, hit 54%, n 91) | +4.0 bp (t +1.9, hit 57%, n 91) | +12.3 bp (t +2.1, hit 55%, n 91) | +7.5 bp (t +0.5, hit 51%, n 91) |

Best cell: enter 5 min, hold 60: +14.6 bp, t +3.23, hit 62%; **family p 0.017**.

## Days left out

No S&P future price at 08:30 or 08:35 (overnight price-limit halts): none.
