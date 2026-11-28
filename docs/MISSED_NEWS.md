# News the listener missed

Every piece of news that moved (or may have moved) a watched stock or the market and that the listener did not record. Started 28 Nov 2026 (TRACK 3.144).
Rows are added by hand for now. The automatic detector (a search layer that finds what the feeds miss; founder's idea of 20 Nov, TRACK 3.73-3.74) is planned, not built; when built it adds rows here by itself.
A row here is information only. A source named in the last column is read for money only after a test shows that its items move prices (founder's rule, 20 Nov).

| date (New York) | what happened | who published it first | found how | why the listener missed it | what would have caught it |
|---|---|---|---|---|---|
| 2026-11-25, about 11:00 | Shares, gold and the 10-year note turned together in the same half hour after a hawkish PCE release | no cause identified; the 7-year auction result came at 11:33, after the turn | the founder saw it on the chart; `src/reversal_check.py` (TRACK 3.119-3.120) | nothing dated at that minute was in any connected source | unknown; market-wide headlines are collected since 26 Nov (`src/market_wire.py`) |
| 2026-11-26 | Nvidia told manufacturing partners to pause server shipments to Malaysia, Singapore, Thailand and Indonesia | Wall Street Journal (press report; repeated by TechCrunch, Forbes, Semafor). No Nvidia release or SEC filing found | the founder read it; checked 28 Nov with `python -m src.reversal_check engine` | the listener reads company newsrooms, SEC filings, PR Newswire and US-government sources; it has no newspaper source | a licensed news source, or a search layer over news headlines (test SR-3 for media is registered, not run) |
