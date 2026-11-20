"""register_20nov_public_calls.py -- TRACK 3.76: test SR-2 (public calls by well-known investors) registered before any price is touched; priors
#162-#164; the founder's order of work and his standing instruction on command blocks. Idempotent."""
from pathlib import Path
T = """
### 3.76 SR-2 registered: public calls by well-known investors (20 Nov 18:45)
`src/public_calls.py`. **Founder (20 Nov):** order of work -- public calls first, then short reports, then the sell-off study (with the 100 largest US stocks added if the counts are small). Investors: Michael Burry, Warren Buffett, George Soros, Bill Ackman, Ray Dalio, Cathie Wood, Carl Icahn. His hypothesis: one call alone may make no ripple; two or more in the same direction within two weeks may bring 'sensational fear'. Reaction to be measured on the day and on EACH of the next 1-7 sessions separately, because a position may be closed before seven sessions.
**Data (no prices yet).** Headlines about each investor (and the fund they run) from Google News' free search feed, month by month from January 2018; a word filter drops headlines with no market word; Claude (`calls-v1-2026-11-20`) reads them in batches of 40 and lists the calls: security, direction (+1 buys / adds / praises; -1 shorts / puts / sells / warns), kind (statement, filing, media report), and whether the headline reports it as that day's news. Headlines about the same investor, security and direction within 10 days are one call; its date is the first headline.
**Test, fixed here.** Day 0 = the first session whose close comes after the first headline (a headline after 16:00 New York belongs to the next session). Return = the security's close-to-close return minus the S&P 500's (for a call on an index itself: the raw return), in the direction of the call. Cells: day 0; each of sessions +1 to +7 on its own; and the total from day 0 to +7. Groups: each investor; all pooled; negative calls only; calls reported as that day's news only; **clusters** (a call that follows, within 10 sessions, a call in the same direction on the same security by a DIFFERENT investor) against single calls. A group needs 30 calls. Null: the same securities and directions on 200 sets of other dates (at least 20 sessions from any call); p = how often a placebo set does as well; a group counts at p < 0.006 (0.05 / 8 groups).
**Priors.** #162: pooled, day 0 moves with the call (the news and the move come together) and passes. #163: none of sessions +1 to +7 taken alone passes in the pooled group -- the move is on the day. #164: fewer than 30 clusters exist, so the 'sensational fear' hypothesis cannot be judged on this list.
**Limits stated before running.** A headline often appears BECAUSE the stock moved, so a day-0 link does not show the call caused the move; a position disclosed in a quarterly filing is up to 45 days old when the public learns of it; the media report some investors far more than others; the date is the first headline found, which may not be the first anywhere; daily closes only (free prices), so the minutes after a call are not seen.
"""
RULE = """
- **Command blocks** (founder, 20 Nov): before every block of commands, say whether it stops by itself and whether the listener must be stopped or restarted. Working arrangement: Window 1 = the listener only; Window 2 = the app only; Window 3 = every other command.
"""
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.76 SR-2 registered: public calls" in s: print("  TRACK: 3.76 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + T); print("  TRACK: 3.76 appended (SR-2 registered; priors #162-#164)")
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "**Command blocks** (founder, 20 Nov)" in s: print("  PROJECT_MASTER: rule already present -- skipped")
else: m.write_text(s.rstrip("\n") + "\n" + RULE); print("  PROJECT_MASTER: command-block rule recorded")
