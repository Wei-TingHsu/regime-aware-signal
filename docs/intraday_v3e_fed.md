# E1 — Fed statement days, minute by minute

132 statement days 2011-01-26 → 2026-10-28. Release time = whichever of 12:30, 14:00, 14:15 shows the largest 5-minute move in the 10-year note (14:00 on 78% of days from 2013). Returns in basis points.

## (a) When does the day's move happen?

Each asset's move, signed by the direction of the 10-year note's move over the whole day (note up = yields down; gold and equities counted as predicted up). This is the same-day link of the daily tests, cut into the parts of the day.

| asset | whole day (prior close → close) | before the release (prior close → release) | first 5 minutes | minutes 5–30 | 30 minutes after → close | share of the day's move that comes AFTER the first 5 minutes |
|---|---|---|---|---|---|---|
| gold | +48.3 (n 130) | +11.2 | +10.1 | +9.1 | +17.9 | 56% |
| S&P 500 | -0.5 (n 130) | -5.8 | +1.6 | +1.0 | +2.8 | -758% |
| Nasdaq-100 | +8.2 (n 130) | -0.0 | +1.3 | +0.9 | +6.0 | 85% |
| 10-year note | +35.7 (n 130) | +15.1 | +5.1 | +4.0 | +11.6 | 44% |

## (b) Is anything left for someone who enters after the release?

Rule: watch the 10-year note for k minutes after the release; enter the asset at that minute in the direction the note moved (note up → buy gold / buy equities / buy the note); hold x minutes or to the close. Mean per trade in basis points before a 2 bp round-trip cost. Family p: the best cell against the best cell when the notes' directions are shuffled across days (2,000 draws). Placebo: the same rule at 14:00 on days with no statement.

### gold

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +5.9 bp (t +2.0, hit 52%, n 132) | +4.5 bp (t +1.3, hit 48%, n 132) | +5.2 bp (t +0.9, hit 48%, n 132) | +10.9 bp (t +1.6, hit 50%, n 132) |
| 5 min | +1.4 bp (t +0.6, hit 50%, n 132) | +4.4 bp (t +1.4, hit 54%, n 132) | +1.8 bp (t +0.4, hit 48%, n 132) | +4.6 bp (t +0.7, hit 54%, n 132) |
| 15 min | +0.7 bp (t +0.3, hit 50%, n 132) | +2.1 bp (t +0.5, hit 46%, n 132) | +2.5 bp (t +0.5, hit 49%, n 132) | +1.6 bp (t +0.3, hit 55%, n 132) |
| 30 min | +0.3 bp (t +0.1, hit 51%, n 132) | -0.8 bp (t -0.2, hit 48%, n 132) | -0.7 bp (t -0.1, hit 52%, n 132) | -2.3 bp (t -0.4, hit 51%, n 132) |

Best cell: enter 1 min after, hold 15 min: **+5.9 bp** before cost (+3.9 after), t +1.98, hit 52%, n 132; **family p 0.359**; placebo days: mean +0.5 bp, 5%–95% range for 132 days -0.7 … +1.7, p vs placebo 0.000. **not shown.**

### S&P 500

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | -0.7 bp (t -0.2, hit 45%, n 132) | +1.4 bp (t +0.3, hit 45%, n 132) | +1.0 bp (t +0.2, hit 48%, n 132) | -8.7 bp (t -1.1, hit 42%, n 132) |
| 5 min | -1.1 bp (t -0.4, hit 45%, n 132) | +2.2 bp (t +0.6, hit 52%, n 132) | +0.2 bp (t +0.0, hit 55%, n 132) | -6.1 bp (t -0.8, hit 49%, n 132) |
| 15 min | +2.1 bp (t +0.7, hit 49%, n 132) | +0.1 bp (t +0.0, hit 45%, n 132) | +0.2 bp (t +0.0, hit 48%, n 132) | -4.2 bp (t -0.6, hit 47%, n 132) |
| 30 min | -2.0 bp (t -0.6, hit 53%, n 132) | -3.8 bp (t -0.8, hit 44%, n 132) | -9.6 bp (t -1.4, hit 43%, n 132) | -9.7 bp (t -1.1, hit 46%, n 132) |

Best cell: enter 30 min after, hold 60 min: **-9.6 bp** before cost (-7.6 after), t -1.44, hit 43%, n 132; **family p 0.805**; placebo days: mean +0.8 bp, 5%–95% range for 132 days -2.6 … +4.4, p vs placebo 0.000. **not shown.**

### Nasdaq-100

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | -0.8 bp (t -0.2, hit 46%, n 132) | +2.0 bp (t +0.4, hit 48%, n 132) | +0.3 bp (t +0.0, hit 48%, n 132) | -12.9 bp (t -1.5, hit 45%, n 132) |
| 5 min | -1.5 bp (t -0.5, hit 48%, n 132) | +3.5 bp (t +0.9, hit 55%, n 132) | -0.7 bp (t -0.1, hit 52%, n 132) | -10.9 bp (t -1.2, hit 49%, n 132) |
| 15 min | +4.1 bp (t +1.2, hit 52%, n 132) | +1.4 bp (t +0.3, hit 50%, n 132) | +0.9 bp (t +0.1, hit 48%, n 132) | -5.9 bp (t -0.7, hit 45%, n 132) |
| 30 min | -3.1 bp (t -0.7, hit 52%, n 132) | -5.2 bp (t -0.9, hit 45%, n 132) | -12.6 bp (t -1.7, hit 46%, n 132) | -14.3 bp (t -1.5, hit 42%, n 132) |

Best cell: enter 30 min after, hold 60 min: **-12.6 bp** before cost (-10.6 after), t -1.68, hit 46%, n 132; **family p 0.617**; placebo days: mean +1.0 bp, 5%–95% range for 132 days -3.0 … +5.1, p vs placebo 0.000. **not shown.**

### 10-year note

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +0.6 bp (t +0.5, hit 42%, n 132) | +0.5 bp (t +0.4, hit 44%, n 132) | +0.4 bp (t +0.2, hit 43%, n 132) | +2.1 bp (t +0.9, hit 47%, n 132) |
| 5 min | -0.4 bp (t -0.4, hit 42%, n 132) | -0.8 bp (t -0.7, hit 47%, n 132) | +0.1 bp (t +0.1, hit 48%, n 132) | +0.0 bp (t +0.0, hit 46%, n 132) |
| 15 min | +0.4 bp (t +0.6, hit 46%, n 132) | +1.5 bp (t +0.9, hit 48%, n 132) | +2.5 bp (t +1.3, hit 54%, n 132) | +1.8 bp (t +0.8, hit 53%, n 132) |
| 30 min | +0.4 bp (t +0.3, hit 48%, n 132) | +0.5 bp (t +0.3, hit 48%, n 132) | +0.3 bp (t +0.2, hit 50%, n 132) | -0.4 bp (t -0.2, hit 50%, n 132) |

Best cell: enter 15 min after, hold 60 min: **+2.5 bp** before cost (+0.5 after), t +1.29, hit 54%, n 132; **family p 0.830**; placebo days: mean -0.1 bp, 5%–95% range for 132 days -1.0 … +0.8, p vs placebo 0.000. **not shown.**

## (c) Statement days signed by the document's own score (what the statement means for stocks, −1 … +1)

Rule: enter the Nasdaq future k minutes after the release in the direction of the document's score; hold x minutes or to the close. The score is known only once the document is read, so k = 1 assumes a reader that scores it within a minute.

### all statement days with a score (45 days), Nasdaq-100

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +14.3 bp (t +1.9, hit 49%, n 45) | +18.6 bp (t +1.7, hit 58%, n 45) | +27.8 bp (t +2.1, hit 49%, n 45) | +45.0 bp (t +2.4, hit 53%, n 45) |
| 5 min | +3.8 bp (t +0.5, hit 40%, n 45) | +14.0 bp (t +1.4, hit 53%, n 45) | +23.1 bp (t +1.5, hit 44%, n 45) | +38.5 bp (t +2.1, hit 51%, n 45) |
| 15 min | -1.5 bp (t -0.2, hit 44%, n 45) | +2.1 bp (t +0.2, hit 44%, n 45) | +10.1 bp (t +0.7, hit 42%, n 45) | +27.6 bp (t +1.6, hit 49%, n 45) |
| 30 min | +3.6 bp (t +0.3, hit 47%, n 45) | +9.2 bp (t +0.7, hit 47%, n 45) | +21.8 bp (t +1.2, hit 47%, n 45) | +29.1 bp (t +1.3, hit 44%, n 45) |

Best cell +45.0 bp, t +2.40; family p 0.136.

### statement days within 10 sessions after a ≥ 4% semiconductor fall (29 days), Nasdaq-100

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +19.3 bp (t +1.9, hit 48%, n 29) | +22.9 bp (t +1.5, hit 59%, n 29) | +31.2 bp (t +1.7, hit 48%, n 29) | +55.7 bp (t +2.4, hit 52%, n 29) |
| 5 min | +1.8 bp (t +0.2, hit 34%, n 29) | +12.7 bp (t +0.9, hit 59%, n 29) | +24.5 bp (t +1.1, hit 48%, n 29) | +45.1 bp (t +1.9, hit 52%, n 29) |
| 15 min | -5.3 bp (t -0.4, hit 45%, n 29) | -6.6 bp (t -0.4, hit 41%, n 29) | +12.2 bp (t +0.6, hit 41%, n 29) | +31.1 bp (t +1.4, hit 45%, n 29) |
| 30 min | -1.3 bp (t -0.1, hit 41%, n 29) | +8.5 bp (t +0.4, hit 41%, n 29) | +24.2 bp (t +0.9, hit 38%, n 29) | +36.5 bp (t +1.2, hit 41%, n 29) |

Best cell +55.7 bp, t +2.42; family p 0.124.

## Days left out

No 10-year-note price at any candidate release time: none. Inside each cell, a day is left out only when the entry or exit minute has no price within 5 minutes (a halt or a closed market); the cell's n shows how many days it used.
