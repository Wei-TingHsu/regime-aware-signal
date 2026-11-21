"""record_21nov_sr2c_page.py -- TRACK 3.81: SR-2c results (public calls, only what comes after the headline for certain), priors #169-#170 scored,
the verdict on reading these investors live; the page's row colours (founder, 21 Nov). SOURCE_CANDIDATES row. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.81 SR-2c results: nothing is left after the public can act; row colours on the page (21 Nov 12:00)
`docs/public_calls_safe.md` (commit 143cfdf). 1,011 calls priced; 952 carry a date and no time of day. Day 0 = first session on or after the headline's date; bar p < 0.0025; 2,000 sets.
| group | overnight into +1 (not tradable) | open to close of +1 | open of +1 to close of +2 |
|---|---|---|---|
| all investors | +36 bp | +8 bp, middle +4, right 51%, -22 after cost, p 0.1345, no | +3 bp, p 0.3610, no |
| positive calls | +65 bp | +11 bp, middle +6, right 51%, -19 after cost, p 0.1105, no | +5 bp, middle -14, p 0.3960, no |
| negative calls | -9 bp | +2 bp, p 0.4105, no | +0 bp, p 0.4040, no |
| Bill Ackman | +47 bp | +10 bp, p 0.2790, no | +64 bp, middle +4, p 0.0195, no |
| Michael Burry | +14 bp | +26 bp, middle +28, right 56%, -4 after cost, p 0.0470, no | +39 bp, middle +40, +9 after cost, p 0.0540, no |
| Warren Buffett | +64 bp | -9 bp, p 0.7795, no | -12 bp, p 0.7425, no |
| Carl Icahn, Cathie Wood, Ray Dalio, George Soros | +37, +33, +9, +4 bp | +4, +12, +11, -15 bp; none passes | +8, -27, +31, -38 bp; none passes |
**No main group passes either piece.** Splits (description): positive calls 2018-2021 overnight +189 bp then -25 bp open to close; 2022-2026 overnight +39 bp then +18 bp (p 0.04); by kind for positive calls the overnight piece is +82 bp (filings), +68 bp (media reports), +27 bp (statements) and the open-to-close piece +8, +17, +8 bp; Warren Buffett's positive calls: overnight +100 bp, then -29 bp open to close (right 43%) -- buying at the open after a Buffett purchase is reported LOST on average; Bill Ackman's positive calls open of +1 to close of +2 +106 bp, middle +16, p 0.0045 (a split, not judged; five of the seven investors have under 30 calls in 2018-2021 so the two-halves condition cannot be checked for them).
**Priors.** #169 RIGHT: for positive calls the overnight piece (+65 bp) is about six times the open-to-close piece (+11 bp) -- the 'next close' gain of SR-2 (+87 bp) is the jump at the open. #170 RIGHT: no main group passes.
**Verdict on SR-2 as a whole (TRACK 3.76-3.81).** Public calls by these seven investors come with a move in their direction on the day the headline is dated, and positive calls with a further jump by the next open. From the next open onward -- the first moment that is after the headline for certain -- nothing passes, and after 30 bp of cost every main group's open-to-close average is negative. **These headlines are not admitted as a paid source and get no rule.** 'Sensational fear' (two investors, same direction, two weeks): 34 cases, not supported. What is NOT shown: whether the minutes right after a call are tradable -- that needs the true minute of each call (for filings the SEC's acceptance time, free) and prices outside regular hours (free only for the last 30 days, so only as a forward record). Recorded as an open route, not started. Total reading cost of SR-2: about US$6.91.
**Page (founder, 21 Nov).** In 'Scored news, newest first' a row is red for its first 5 minutes on the page, yellow from 5 to 10, green from 10 to 15, then the usual background; a first column 'On the page for' shows the minutes; 'on the page' is counted from the moment the listener saw the item plus the seconds Claude took to score it.
"""
if "### 3.81 SR-2c results" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.81 added")
else: print("  TRACK.md: 3.81 already there -- skipped")
c = Path("docs/SOURCE_CANDIDATES.md"); x = c.read_text(); i = x.find("| TESTED 20 Nov (TRACK 3.77, 3.79)")
new = "| TESTED, NOT ADMITTED (TRACK 3.76-3.81, 21 Nov): the price moves with the call on the day and jumps by the next open; from the next open onward nothing passes and the average is negative after cost; clusters (34): not supported. No rule; not read live. Open route: true minute of each call (SEC filing times) as a forward record. |"
if i != -1: j = x.find("\n", i); c.write_text(x[:i] + new + x[j:]); print("  SOURCE_CANDIDATES.md: public-calls row updated")
elif "TESTED, NOT ADMITTED (TRACK 3.76-3.81" in x: print("  SOURCE_CANDIDATES.md: already updated")
else: print("  SOURCE_CANDIDATES.md: row not found -- unchanged. Tell Claude.")
