# Live outcomes: the forward record of the candidate rules

Each row is one live event seen and scored by `src/news_listener.py`, priced afterwards. The rules and their cells were fixed before any row existed (TRACK 3.64). Returns in bp (1 bp = 0.01%) in the direction of the trade, before cost. None of these is yet a confirmed signal.

## Running totals

| rule | what | trades with a price | average, before cost | assumed cost | right on | backtest said |
|---|---|---|---|---|---|---|
| FA-1 | Fed statement score -> Nasdaq future, 1 min after the release, hold 60 min | 0 | | 2 bp | | +30.0 bp, 74% of 101 |
| FA-2 | Fed day: gold's move from the release to 15:15 -> held to the next 09:30 | 0 | | 2 bp | | +40.3 bp, 67% of 132 |
| FA-3 | results: market score -> own stock, 5 min after, hold 30 min | 0 | | 10 bp | | +41.4 bp, 58% of 330 |
| FA-4 | results, step rule: own-stock score of 0.7 or more in size -> own stock, 1 min after, hold 60 min | 0 | | 10 bp | | +141.5 bp per trade on 140 trades, 2020-2026, thresholds fitted on earlier years |
| QC-3 | results after the close: results against prior guidance -> Nasdaq future, 5 min after, to the next 09:35 | 0 | | 2 bp | | +16.7 bp, 61% of 294 |
| CV-1 | customer view: own-stock score -> own stock, 1 min after the score was ready, hold 60 min | 0 | | 10 bp | | no backtest at this clock (own-stock score from the SEC stamp + 1 min: +64.9 bp, 58% of 365) |

A verdict needs at least 30 trades per rule; before that the totals are only a record.

## Every event

| date (New York) | who | rule | direction | entry | result, before cost | note |
|---|---|---|---|---|---|---|
| 2026-11-17 | NVDA | FA-3 | buy | 16:26 |  | no price yet |
| 2026-11-17 | NVDA | FA-4 | buy | 16:22 |  | no price yet |
| 2026-11-17 | NVDA | QC-3 | buy | 16:26 |  | no price yet |
| 2026-11-17 | NVDA | CV-1 | not counted |  |  | the live read failed; the score was made after the fact, so no user could have acted on it |
