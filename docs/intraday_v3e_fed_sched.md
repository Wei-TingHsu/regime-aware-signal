# E1 — Fed statement days, minute by minute

132 statement days 2011-01-26 → 2026-10-28. Release time = whichever of 12:30, 14:00, 14:15 shows the largest 5-minute move in the 10-year note (14:00 on 99% of days from 2013). Returns in basis points.

## (a) When does the day's move happen?

Each asset's move, signed by the direction of the 10-year note's move over the whole day (note up = yields down; gold and equities counted as predicted up). This is the same-day link of the daily tests, cut into the parts of the day.

| asset | whole day (prior close → close) | before the release (prior close → release) | first 5 minutes | minutes 5–30 | 30 minutes after → close | share of the day's move that comes AFTER the first 5 minutes |
|---|---|---|---|---|---|---|
| gold | +48.3 (n 130) | +13.6 | +10.2 | +5.5 | +19.1 | 51% |
| S&P 500 | -0.5 (n 130) | -4.9 | +1.8 | -2.1 | +4.8 | -540% |
| Nasdaq-100 | +8.2 (n 130) | +1.3 | +1.8 | -2.2 | +7.3 | 62% |
| 10-year note | +35.7 (n 130) | +15.1 | +5.3 | +3.0 | +12.3 | 43% |

## (b) Is anything left for someone who enters after the release?

Rule: watch the 10-year note for k minutes after the release; enter the asset at that minute in the direction the note moved (note up → buy gold / buy equities / buy the note); hold x minutes or to the close. Mean per trade in basis points before a 2 bp round-trip cost. Family p: the best cell against the best cell when the notes' directions are shuffled across days (2,000 draws). Placebo: the same rule at 14:00 on days with no statement.

### gold

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +7.2 bp (t +2.4, hit 55%, n 132) | +4.0 bp (t +1.1, hit 51%, n 132) | +6.2 bp (t +1.1, hit 51%, n 132) | +12.1 bp (t +1.7, hit 55%, n 132) |
| 5 min | +4.3 bp (t +1.8, hit 52%, n 132) | +5.5 bp (t +1.8, hit 51%, n 132) | +2.7 bp (t +0.5, hit 47%, n 132) | +3.3 bp (t +0.5, hit 50%, n 132) |
| 15 min | +0.3 bp (t +0.1, hit 47%, n 132) | -1.6 bp (t -0.4, hit 41%, n 132) | -1.7 bp (t -0.4, hit 48%, n 132) | -3.7 bp (t -0.6, hit 52%, n 132) |
| 30 min | -2.1 bp (t -0.7, hit 47%, n 132) | -3.0 bp (t -0.7, hit 47%, n 132) | -5.3 bp (t -1.0, hit 48%, n 132) | -7.5 bp (t -1.3, hit 47%, n 132) |

Best cell: enter 1 min after, hold 15 min: **+7.2 bp** before cost (+5.2 after), t +2.36, hit 55%, n 132; **family p 0.160**; placebo days: mean +0.5 bp, 5%–95% range for 132 days -0.7 … +1.7, p vs placebo 0.000. **not shown.**

### S&P 500

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | -1.1 bp (t -0.4, hit 44%, n 132) | +0.0 bp (t +0.0, hit 42%, n 132) | -0.9 bp (t -0.2, hit 45%, n 132) | -9.9 bp (t -1.3, hit 43%, n 132) |
| 5 min | +0.6 bp (t +0.3, hit 45%, n 132) | +2.5 bp (t +0.7, hit 47%, n 132) | -1.9 bp (t -0.4, hit 45%, n 132) | -4.8 bp (t -0.6, hit 45%, n 132) |
| 15 min | -0.4 bp (t -0.1, hit 45%, n 132) | -2.9 bp (t -0.8, hit 46%, n 132) | -1.8 bp (t -0.4, hit 45%, n 132) | -5.6 bp (t -0.8, hit 48%, n 132) |
| 30 min | -3.1 bp (t -0.9, hit 48%, n 132) | -2.2 bp (t -0.5, hit 45%, n 132) | -3.4 bp (t -0.5, hit 45%, n 132) | -4.4 bp (t -0.5, hit 46%, n 132) |

Best cell: enter 1 min after, hold close: **-9.9 bp** before cost (-7.9 after), t -1.26, hit 43%, n 132; **family p 0.903**; placebo days: mean +0.1 bp, 5%–95% range for 132 days -5.2 … +5.6, p vs placebo 0.002. **not shown.**

### Nasdaq-100

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | -1.6 bp (t -0.5, hit 42%, n 132) | -0.1 bp (t -0.0, hit 45%, n 132) | -1.0 bp (t -0.2, hit 45%, n 132) | -13.1 bp (t -1.5, hit 44%, n 132) |
| 5 min | +0.0 bp (t +0.0, hit 48%, n 132) | +3.3 bp (t +0.9, hit 51%, n 132) | -2.8 bp (t -0.4, hit 45%, n 132) | -8.8 bp (t -1.0, hit 44%, n 132) |
| 15 min | +0.7 bp (t +0.2, hit 50%, n 132) | -2.3 bp (t -0.5, hit 49%, n 132) | -1.0 bp (t -0.2, hit 47%, n 132) | -7.9 bp (t -0.9, hit 45%, n 132) |
| 30 min | -3.6 bp (t -0.8, hit 50%, n 132) | -2.3 bp (t -0.4, hit 46%, n 132) | -4.7 bp (t -0.6, hit 48%, n 132) | -8.7 bp (t -0.9, hit 42%, n 132) |

Best cell: enter 1 min after, hold close: **-13.1 bp** before cost (-11.1 after), t -1.46, hit 44%, n 132; **family p 0.778**; placebo days: mean +0.2 bp, 5%–95% range for 132 days -5.6 … +6.2, p vs placebo 0.001. **not shown.**

### 10-year note

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +0.1 bp (t +0.1, hit 42%, n 132) | -0.3 bp (t -0.2, hit 45%, n 132) | +0.6 bp (t +0.3, hit 48%, n 132) | +2.8 bp (t +1.1, hit 51%, n 132) |
| 5 min | +0.3 bp (t +0.4, hit 43%, n 132) | -0.2 bp (t -0.2, hit 47%, n 132) | +1.4 bp (t +0.7, hit 46%, n 132) | +1.2 bp (t +0.5, hit 44%, n 132) |
| 15 min | +0.2 bp (t +0.2, hit 45%, n 132) | +0.3 bp (t +0.2, hit 47%, n 132) | +1.5 bp (t +0.8, hit 48%, n 132) | +0.8 bp (t +0.4, hit 52%, n 132) |
| 30 min | +0.5 bp (t +0.4, hit 48%, n 132) | +1.0 bp (t +0.6, hit 52%, n 132) | +0.6 bp (t +0.3, hit 51%, n 132) | -0.2 bp (t -0.1, hit 52%, n 132) |

Best cell: enter 1 min after, hold close: **+2.8 bp** before cost (+0.8 after), t +1.13, hit 51%, n 132; **family p 0.916**; placebo days: mean -0.1 bp, 5%–95% range for 132 days -1.2 … +1.0, p vs placebo 0.000. **not shown.**

## (c) Statement days signed by the document's own score (what the statement means for stocks, −1 … +1)

Rule: enter the Nasdaq future k minutes after the release in the direction of the document's score; hold x minutes or to the close. The score is known only once the document is read, so k = 1 assumes a reader that scores it within a minute.

### all statement days with a score (132 days), Nasdaq-100

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +10.1 bp (t +3.5, hit 52%, n 132) | +11.0 bp (t +2.9, hit 55%, n 132) | +23.0 bp (t +4.4, hit 57%, n 132) | +25.5 bp (t +3.2, hit 52%, n 132) |
| 5 min | +3.0 bp (t +1.2, hit 42%, n 132) | +4.9 bp (t +1.3, hit 45%, n 132) | +17.6 bp (t +3.0, hit 51%, n 132) | +19.6 bp (t +2.6, hit 48%, n 132) |
| 15 min | +0.8 bp (t +0.2, hit 46%, n 132) | +6.1 bp (t +1.5, hit 50%, n 132) | +13.4 bp (t +2.5, hit 52%, n 132) | +16.2 bp (t +2.2, hit 48%, n 132) |
| 30 min | +5.3 bp (t +1.4, hit 48%, n 132) | +11.5 bp (t +2.3, hit 47%, n 132) | +15.9 bp (t +2.3, hit 52%, n 132) | +15.5 bp (t +1.8, hit 45%, n 132) |

Best cell +23.0 bp, t +4.44; family p 0.000.

### statement days within 10 sessions after a ≥ 4% semiconductor fall (29 days), Nasdaq-100

| enter after | hold 15 min | hold 30 min | hold 60 min | hold to the close |
|---|---|---|---|---|
| 1 min | +16.1 bp (t +2.1, hit 55%, n 29) | +8.5 bp (t +0.7, hit 55%, n 29) | +27.6 bp (t +1.8, hit 48%, n 29) | +52.3 bp (t +2.4, hit 52%, n 29) |
| 5 min | +1.8 bp (t +0.2, hit 38%, n 29) | -2.2 bp (t -0.2, hit 52%, n 29) | +24.3 bp (t +1.2, hit 48%, n 29) | +43.9 bp (t +1.9, hit 52%, n 29) |
| 15 min | -12.7 bp (t -1.1, hit 41%, n 29) | -12.4 bp (t -0.9, hit 48%, n 29) | +14.3 bp (t +0.8, hit 41%, n 29) | +33.3 bp (t +1.4, hit 48%, n 29) |
| 30 min | +0.4 bp (t +0.0, hit 41%, n 29) | +16.9 bp (t +0.9, hit 41%, n 29) | +23.1 bp (t +0.9, hit 38%, n 29) | +46.1 bp (t +1.5, hit 48%, n 29) |

Best cell +52.3 bp, t +2.39; family p 0.143.

## Days left out

No 10-year-note price at any candidate release time: none. Inside each cell, a day is left out only when the entry or exit minute has no price within 5 minutes (a halt or a closed market); the cell's n shows how many days it used.
