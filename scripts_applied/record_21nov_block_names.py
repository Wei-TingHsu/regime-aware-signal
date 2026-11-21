"""record_21nov_block_names.py -- TRACK 3.87: the three blocks at the top of the live tab get names (founder, 21 Nov). Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.87 The three blocks of the live tab are named (21 Nov 13:45)
**Founder (21 Nov):** asked under what rule each block shows an item, then asked for names: 'Current High-Executive Suggestions', 'Current Low-executive Suggestions', 'Past Suggestions (as Reference)'.
**Rules of the blocks (from `src/live_view.py`).** (1) Top: an item with a tested rule -- company results with an own-stock score of 0.7 or more in size (Strong-results rule), or a Fed statement with a non-zero score (Fed-statement rule) -- from the release until the rule's hour ends; not shown if the score reached us more than 5 minutes after the entry time. (2) Middle: scored items of the last 24 hours with no rule (or under the rule's threshold) whose own-stock score is 0.3 or more in size or whose 'material' score is 0.5 or more; at most six. (3) Bottom: the three most recent items where a rule fired and the hour is over, or that arrived too late. The 0.3 / 0.5 limits, the 24 hours and 'three' are display choices, not test results.
**Names applied:** 'Current High-Confidence Suggestions'; 'Current Low-Confidence Alerts (no tested rule)'; 'Past Suggestions (Reference)'. Two departures from the founder's wording, both told to him: 'confidence' instead of 'executive' (plain English for what he meant); and the middle block is called ALERTS, not suggestions, because no test supports trading on it -- SR-1 and SR-2 found that such news moved the price before a user could act. The top block's caption says the rules are still candidates until 30 live trades.
"""
if "### 3.87 The three blocks of the live tab" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.87 added")
else: print("  TRACK.md: 3.87 already there -- skipped")
