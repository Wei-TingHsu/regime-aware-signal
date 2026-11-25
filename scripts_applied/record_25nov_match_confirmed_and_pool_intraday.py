"""record_25nov_match_confirmed_and_pool_intraday.py -- TRACK 3.122: the first forward match confirmed with all prices; the download of 1-minute prices for the 20 pool stocks. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.122 The first forward match confirmed; 1-minute prices for the 20 pool stocks (25 Nov 23:50)
**The SanDisk match of 3.121 is confirmed (commit 8aebe3f; run of 25 Nov 10:05 New York).** The fixed daily check got all 121 prices (Yahoo refused 32 at first; the retries got them) and SS-2a still matches SNDK (-11.1% on 24 Nov). The caveat of 3.121 is closed: a real match, not a product of the fault. Entry under the rule: the open of 25 Nov; exit: the close of Fri 27 Nov (13:00 New York). The founder's way: short with US$35,000. Result after Friday's close. The same day AMD, NVDA, MU, TXN and INTC fell 5% or more and met no rule.
**Founder, 25 Nov 23:33:** 'okay, what is the next step. let's continue. But give me the task which needs to run for a few hours, because i am going to bed'.
**The overnight task: 1-minute prices of the 20 pool stocks (`src/pool_intraday.py`). A download, not a test.** Databento, dataset XNAS.ITCH, 1-minute bars, May 2018 to now, the 20 stocks of docs/POOL_PLAN.md; one file per stock per year in `data_provenance/intraday/eq/` (ignored by git: licensed data is not uploaded; the same layout as the earlier AI-chain download, so nothing is paid twice). The price is quoted before anything is downloaded and the download stops at the founder's limit.
**Why this and not something else.** The founder's assumption 'turns are caused by news' (POOL_PLAN point 4) and his points on publication time need prices at the minute the news came out; the SEC gives the acceptance minute of every filing, daily prices cannot use it. Everything else waiting is either short (the daily-level test of turns against news runs in minutes) or needs Anthropic credit (the reading), which is used up.
**What is NOT yet registered:** any test on these prices. The daily-level test of turns against news is built next; the minute-level test is registered when it is written, before it runs.
"""
if "### 3.122 The first forward match confirmed" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.122 added")
else: print("  TRACK.md: 3.122 already there -- skipped")
