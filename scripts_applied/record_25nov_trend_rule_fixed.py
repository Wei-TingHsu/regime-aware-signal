"""record_25nov_trend_rule_fixed.py -- TRACK 3.117 and an added part in docs/POOL_PLAN.md: the trend rule the founder confirmed on nine stocks is fixed. Idempotent."""
from pathlib import Path
RULE = """

## Part 3. The trend rule, confirmed by the founder on 25 Nov 2026 and fixed

Founder, 25 Nov 21:41: 'nvda aapl amd amzn tsm goog MU SNDK ORCL are now all perfect matching my eyes' decision. I think the rule is fitted correctly.' Five of these nine stocks were used to fit the rule (AAPL, AMD, NVDA, SNDK, TSM); four were not (AMZN, GOOG, MU, ORCL). This replaces the first row ('Length') of the table in Part 2.

**The rule (`src/trend_finder.py`), in words.**
1. The stock's *usual daily move* on a day = the spread of its daily moves over the 250 sessions up to that day.
2. A *crest* is confirmed when the price has fallen back from its highest point since the last trough by 5 usual daily moves. A *trough* is confirmed the same way upward. (K = 5, fitted on the founder's first marks and fixed.)
3. A *trend* is the swing from one turn to the next. Every swing is a trend, fast or slow, of any length. A move against the swing smaller than 5 usual daily moves is part of the swing. The last swing is 'running'.
4. *Sideways.* If the best price reached in the first part of a swing is already within 1.5 usual daily moves of the swing's final extreme, and the part after it is at least 10 sessions and at least a third of the swing, the trend ends at that earlier price and the part after it is 'sideways' -- not a trend.
5. For each trend the code also gives its size in usual daily moves, how fast it is, and *the first day it could have been recognised with the prices known that day* (the day its starting turn was confirmed).

**What is fixed and what is not.** The four numbers (250 sessions; 5 usual moves; 1.5 usual moves; 10 sessions and a third) are fixed from here on; they change only by a dated entry in TRACK. The rule draws trends AFTER the fact: a crest is known only once the price has fallen 5 usual moves from it. Anything the product says on a live day must use 'first seen' dates, never the drawn ends.
"""
p = Path("docs/POOL_PLAN.md"); x = p.read_text()
if "## Part 3. The trend rule, confirmed by the founder" in x: print("  POOL_PLAN.md: Part 3 already there -- skipped")
else: p.write_text(x.rstrip("\n") + RULE); print("  POOL_PLAN.md: Part 3 added (Parts 1 and 2 untouched)")
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.117 The trend rule is confirmed by the founder on nine stocks and fixed (25 Nov 22:00)
**Founder, 25 Nov 21:41:** 'nvda aapl amd amzn tsm goog MU SNDK ORCL are now all perfect matching my eyes' decision. I think the rule is fitted correctly.' Five of the nine were used to fit the rule (AAPL, AMD, NVDA, SNDK, TSM); **four were not (AMZN, GOOG, MU, ORCL) and match as well** -- the check asked for in 3.115. Eleven of the twenty pool stocks have not been looked at.
**The rule as fixed** (`src/trend_finder.py`; full text in `docs/POOL_PLAN.md`, Part 3): usual daily move = the spread of daily moves over 250 sessions; a crest or trough is confirmed when the price has come back 5 usual moves (K = 5); a trend is the swing between two turns, of any length; a swing whose first part already reached within 1.5 usual moves of its final extreme, followed by at least 10 sessions and a third of the swing, ends at that earlier price and the rest is sideways. The numbers change only by a dated entry here.
**How it was reached, for the record:** four versions in one evening. (1) 'Unusually strong stretches' -- missed slow swings, counted small counter-moves (founder's first marks). (2) 'Strongest stretch first' -- written by Claude before the marks arrived, went the wrong way, never published. (3) Swings between crests and troughs, K chosen by the marks -- accepted for AAPL and TSM; NVIDIA's two long swings ran into sideways stretches. (4) A sideways rule on 'highest strength from the start', with K re-chosen at each run -- spoiled four accepted stocks; withdrawn. (5) K fixed at 5 and the conservative sideways rule -- confirmed.
**What the rule is not.** It is a drawing of the past: a crest is known only after the price has fallen 5 usual moves from it. No claim about the future follows from it. The pool's tests (docs/POOL_PLAN.md, 'what still has to be tested') start from here: turns and news, support levels that held or broke, always with the 'first seen' day and never the drawn end.
"""
if "### 3.117 The trend rule is confirmed" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.117 added")
else: print("  TRACK.md: 3.117 already there -- skipped")
