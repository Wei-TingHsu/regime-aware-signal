"""record_13nov_stockdata.py -- TRACK 3.60: stock minute data on disk; stage A of the AI-chain earnings test started. Idempotent."""
from pathlib import Path
TRACK = """
### 3.60 Stock minute data on disk; AI-chain earnings test, stage A (13 Nov 00:50)
**Bought:** Databento XNAS.ITCH (trades on the Nasdaq exchange, 04:00–20:00 New York), 1-minute bars, 1 May 2018 → 11 Nov 2026, quoted US$12.65: AMD, NVDA, MU, INTC, AVGO, SNDK, ORCL, TSM, CRWD, GOOG, META (and FB, its ticker to June 2022), AMZN, MSFT, plus SOXX, SMH, QQQ — about 20 million bars under `data_provenance/intraday/eq/` (ignored folder; not uploaded). Databento total US$115.33 of the US$125 free credit. SK Hynix (founder: Nasdaq-listed since 6 July 2026) was left out of that request by Claude and is fetched by rerunning the same command. A second free-credit account is not used. Limits: one exchange's trades only; history from 2018 (the Nasdaq-100 future runs from 2010); prices not adjusted for share splits (immaterial inside a day).
**Founder's clarification (12 Nov), recorded:** the company list is the list of whose NEWS is read. Part 1 measures the reaction on the Nasdaq-100 future already on disk ("one report can alter the whole market's basic logic") and needs no purchase; Part 2 measures each company's own stock and the spill-over to the other thirteen, on the data above. Short-history names (SanDisk, SK Hynix; later Anthropic and OpenAI once listed) are included and simply contribute few events at first.
**Stage A (no LLM, no cost):** `src/ai_earnings.py filings` — every 8-K Item 2.02 from June 2010 for the US filers on the list, with the SEC acceptance time to the second and the text of the attached release; `times` — when in the day they arrive. Foreign filers (6-K) are counted and handled in stage B. Stage B: sample check of the reader on results releases → registration with priors → scores → tests.
"""
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.60 Stock minute data on disk" in s: print("  TRACK: 3.60 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.60 appended")
