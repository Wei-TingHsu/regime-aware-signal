"""record_25nov_sideways.py -- TRACK 3.116: the third trend charts, the founder's second marks (sideways), and the sideways rule. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.116 The swing charts; the founder's second marks; the sideways rule (25 Nov 22:10)
**Third version, first run** (commit 6a4189e; a first attempt crashed on SNDK, which has 447 sessions where the code assumed 620 -- Claude's test had no short history; fixed). 342 swings on 20 stocks, about 17 a stock. Of the 18 swings taken from the founder's first marks, 14 are reproduced within 9 days at both ends; the 4 not reproduced are near misses on dates (AAPL two, TSM one, AMD one).
**The founder's second marks (25 Nov 21:18), word for word:** 'NVDA has a mistake on 5, which should actually end in the middle of that area, because the later part of the 5th's area is sideway movements. 10th also has the same problem, should have ended at the trough before 2026 Jan, the remaining part is also sideway movements. AAPL is correct. TSM also correct.' (NVDA 5: up 6 Sep 2024 to 6 Jan 2025, 83 sessions, +45%, strength 1.28; NVDA 10: down 29 Oct 2025 to 30 Mar 2026, 103 sessions, -20%, strength 0.71.)
**What they say.** A swing runs to the most extreme price, and a long flat stretch can end on a price slightly more extreme than where the move really ended. His eye ends the trend where the move ended and calls the rest sideways.
**The sideways rule (Claude's proposal, to be confirmed on the next charts).** Inside a swing, the move 'ended' on the day up to which its strength, counted from the swing's start, is highest (strength = the move divided by how far a price drifts by chance in that many sessions). What follows is cut off and marked 'sideways' only when it lasts at least 5 sessions AND its own move is smaller than one chance drift for its length (strength under 1). Only the end of a swing is tested, because that is what was marked. A sideways stretch is not a trend; the next trend still starts at the swing's true extreme. Two numbers are in this rule (5 sessions; one chance drift) and both are Claude's; if the charts show the rule cutting trends he accepted, they change.
"""
if "### 3.116 The swing charts" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.116 added")
else: print("  TRACK.md: 3.116 already there -- skipped")
