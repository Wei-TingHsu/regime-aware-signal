"""register_21nov_events100.py -- TRACK 3.91: ET-2 stage A registered (announcements of about 100 large US companies): what is collected, what can and
cannot be tested, and that the reading waits for a counted cost. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.91 ET-2 stage A: the announcement test widened to about 100 large US companies (21 Nov 15:30; no prices, nothing read)
**Founder (21 Nov):** 'widen, yes. And then sell-off study.' `src/events100.py`.
**Universe.** The S&P 100 companies: the index fund's own holdings file (iShares S&P 100 ETF) when it can be read, otherwise a fixed list written by Claude; which one was used is printed and saved (`processed/universe100_source.txt`). Never Wikipedia. The twelve US companies of the founder's list are left out (they are ET-1). **Stated bias:** today's list applied to past years -- companies that shrank or left the index since 2018 are missing.
**Collected, free.** Each company's 8-K filings since May 2018 that carry an event item (the same items as ET-1; results releases, Item 2.02, left out), with the SEC's acceptance time; then the text of each filing and of its press release if it has one.
**Reading (waits for the founder).** The same reader and prompt as ET-1 (ai-event-v2). One difference, stated: no results baseline is given for these companies (ET-1's reader was given the company's latest reported figures; reading 100 companies' results as well would cost several times more). `cost` counts the price on the downloaded texts, for all filings and for only those that carry a press release; nothing is read before the founder has seen that figure.
**What the price side can and cannot test.** Minute prices for these companies are not on disk and paid data is banned, so prices are free daily opens and closes. The SEC stamp is a real clock time, so each filing is placed before the open, during the session or after the close, and the pieces a user could trade at the open or the close are separated from what was already gone (the method of SR-1, TRACK 3.84). **Not testable this way: the first minutes after a filing -- which is where ET-1's near miss ('trouble' news, 1 minute after, held 15 minutes) sat.** Claude's expectation, written before any count: with about eight times the events, a daily-scale effect of the size ET-1 hinted at in its 'next session' cells (+19 to +38 bp before cost) would be detectable, but would not clear a 30 bp cost; the widening is more likely to settle the question as 'no' than to produce a rule. The exact cells, groups and priors are registered after the counts and before any price.
"""
if "### 3.91 ET-2 stage A" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.91 added")
else: print("  TRACK.md: 3.91 already there -- skipped")
