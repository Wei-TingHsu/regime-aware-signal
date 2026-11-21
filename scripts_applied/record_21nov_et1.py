"""record_21nov_et1.py -- TRACK 3.90: ET-1 results (company announcements by type), priors #179-#181 scored; tab buttons rounded. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.90 ET-1 results: no type of company announcement passes; one near miss (21 Nov 15:00)
`docs/ai_event_types.md` (commit 73f4764). 276 events of the US filers from May 2018 with material 0.2 or more. Five families had 30 or more events; bar p < 0.0100; cost 30 bp.
| family | events | best cell | average before cost | after 30 bp | right on | family p | four periods (bp) | verdict |
|---|---|---|---|---|---|---|---|---|
| financing or capital return | 111 | sell when uncertainty rises; next regular session, hold 30 min | +19.1 bp | -10.9 | 63% of 109 | 0.8805 | 4.8, 13.6, 52.6, 5.9 | does not pass |
| acquisition or disposal | 54 | sell when uncertainty rises; 5 min after the stamp to the next 09:35 | -56.7 bp (prices moved AGAINST the score) | -86.7 | 31% of 42 | 0.0795 | -61.6, -86.0, -76.0, 0.4 | does not pass |
| leadership change | 37 | sell when uncertainty rises; next regular session, hold 30 min | +38.0 bp | +8.0 | 60% of 35 | 0.2620 | 44.6, -35.7, 38.4, 112.9 | does not pass |
| GROUP business news | 34 | own_stock; 1 min after the stamp, hold 15 min | +78.5 bp | +48.5 | 71% of 31 | 0.4215 | 114.8, 78.6, 8.0, 117.3 | does not pass |
| GROUP trouble (legal, cyber, accounting, restructuring, leadership) | 72 | own_stock; 1 min after the stamp, hold 15 min | +44.5 bp | +14.5 | 56% of 48 | **0.0155** | 5.7, 83.0, 52.0, 37.1 | does not pass (near miss: bar 0.0100) |
Not tested (under 30): legal or regulatory 25, contract or partnership 16, guidance update 16, restructuring 8, other 5, product or technology 2, accounting 1, cyber incident 1.
**Priors.** #179 RIGHT: no type becomes a candidate. #180 RIGHT: guidance update has 16 events. #181 WRONG: the strongest family by t is the 'trouble' group (t +2.93), not one of the two largest types; acquisitions moved against the uncertainty signal.
**Reading.** The limit is the number of events: twelve companies produce about 30 material announcements a year, so a single type cannot reach a verdict. Two things worth keeping as hypotheses, not rules: (a) 'trouble' news -- own_stock score, one minute after the stamp, held 15 minutes: positive in all four periods, +14.5 bp after cost, p 0.0155 against a bar of 0.0100; (b) 'business news' -- +78.5 bp in the same window on only 31 trades (p 0.42: indistinguishable from luck at that size). Both use the first minutes after the stamp -- the same place where the Strong-results rule lives. **What would make these testable is more companies, not more slicing**: the same reader on the announcements of the 100 largest US stocks would give roughly eight times the events (a reading cost to be counted first; minute prices for them are NOT on disk and paid data is banned, so the price side would have to be the forward record or daily prices). Recorded as an open route for the founder's decision; nothing started.
**Page.** The tab buttons are rounded, frosted, and lift under the cursor like the five market cards; the line under the selected tab is removed (`src/live_page.py`, the style app.py already loads).
"""
if "### 3.90 ET-1 results" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.90 added")
else: print("  TRACK.md: 3.90 already there -- skipped")
