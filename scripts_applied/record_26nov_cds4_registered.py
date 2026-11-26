"""record_26nov_cds4_registered.py -- TRACK 3.135: test CDS-4 (one question on Oracle's own share) and its forward record, registered BEFORE it runs. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.135 Test CDS-4 registered: after a jump in Oracle's CDS, is Oracle's share weaker the next session? (26 Nov 18:00)
**Founder, 26 Nov 16:13:** 'yes after' -- YES to the follow-up proposed in 3.134; the tests 'debt news of the AI spenders -> shares' and 'turns are caused by news' come after it.
**Test CDS-4 (`python -m src.cds_oracle test`), fixed before it runs. ONE test, limit: chance under 0.05.**
1. Oracle's spread of a day = the middle one of that day's 5-year CDS trades whose spread is GIVEN in the public file, done before 16:00 New York (rules of 3.128, without the worked-out spreads -- they produced false jumps, 3.134).
2. A jump = that spread 5% or more above Oracle's last day with one, at most 5 sessions back. The size 5% is the one of the strongest cells of CDS-3 -- chosen after seeing that grid, which is why this test alone cannot settle the matter and a forward record follows.
3. For each jump day: Oracle's share over the NEXT session (close to close), minus the average next-session move of the 10 other days of the period on which the share moved most nearly the same amount on the day itself and there was no jump ('look-alike days'). This takes out 'a bad day is followed by a bad day'.
4. The measure = the average of those differences. Chance = the share of copies, with the jump days slid along the calendar by 20 sessions or more, whose difference is at least as large. PASSES = chance under 0.05 and the difference negative. Under 15 jumps: too few to judge.
5. Result with every jump listed: `docs/cds_oracle.md`.
**The forward record (`python -m src.cds_oracle forward`, part of the daily block from now on).** Every jump on or after 27 Nov 2026, with the share's next session and the look-alike days' next session; verdict at 20 jumps with a result. Jumps on given spreads are rare, so this may take a year or more -- stated now. Only dates, share moves and counts go to `docs/cds_oracle_forward.md`; the trades stay in the ignored folder.
**What a pass would still not be.** A trading rule: the trades are timed when done, not when made public; the share would have to be sold at the close of the jump day. And it is about Oracle's share, not about semiconductor shares -- for those CDS-1 to CDS-3 found nothing.
**Priors.** #238: fewer than 30 jumps on given spreads. #239: the difference is negative but does not pass -- most of the effect seen in CDS-3 is 'a bad day follows a bad day'. #240: Oracle's share on the jump day itself averages below -1%.
"""
if "### 3.135 Test CDS-4 registered" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.135 added")
else: print("  TRACK.md: 3.135 already there -- skipped")
