"""record_21nov_release_colours.py -- TRACK 3.82: why some items reach the listener hours late (read from the live log), the row colours now
counted from the release, late items shown as missed. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.82 Why some items arrive hours late; colours counted from the release; late items are 'missed', not suggestions (21 Nov 12:30)
**Founder (21 Nov):** if the rule buys one minute after the release and the lag from publication to the listener is 20,000 seconds, no profit is possible; the colours must count from the release, not from the time on the page.
**What the live log shows (`data_provenance/live/events.jsonl`, 16-20 Nov, 54 rows).** Every lag above about 1,000 seconds was logged within seconds of a moment the listener was STARTED (17 Nov 18:12 UTC: six items, 15,145 to 83,571 s; 19 Nov 16:32: two items; 20 Nov 09:52: twelve items, 8,043 to 49,939 s): they were published while the listener was off and were seen when it came back. While the listener was running: SEC filings 55 and 83 s; PR Newswire 112 and 174 s; NVIDIA's own newsroom 290 to 450 s (its feed is about five minutes behind -- NVIDIA's results on 17 Nov came by the SEC route at 83 s and by the newsroom at 329 s). Two cases not explained by a start: AMD's investor page 2,895 s (16 Nov) and Hunterbrook 5,418 s (19 Nov) -- either a restart not visible in the log or a slow feed; to be measured.
**So the lag has two causes with different cures.** (1) The listener was off (laptop closed, restarts): cure = a machine that is always on. (2) A source's own feed is slow: cure = a faster address for that source (the SEC and the news wires are the fast routes; company newsrooms are slow), and checking more often than every 30 seconds.
**Page.** Row colours now count from the release: red under 5 minutes, yellow 5 to 10, green 10 to 15, none after; first column 'Since release'. An item that arrives late is therefore never red. **Suggestions:** a rule was tested entering one minute after the release; when the score is ready more than 5 minutes after that entry time the page shows 'Arrived too late' instead of a suggestion (5 minutes is a chosen limit, not a tested one); when it is ready a little after, the suggestion states by how many seconds.
**Fault (Claude's):** the colours were first built on time-on-the-page, which hid lateness instead of showing it.
"""
if "### 3.82 Why some items arrive hours late" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.82 added")
else: print("  TRACK.md: 3.82 already there -- skipped")
