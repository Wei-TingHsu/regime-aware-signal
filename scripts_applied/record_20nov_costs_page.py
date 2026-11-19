"""record_20nov_costs_page.py -- TRACK: measured IBKR costs (C result, prior #161 right) and the 'Event signals' page (3.71). Numbers from commit abc46db0. Idempotent."""
from pathlib import Path
C = """
**3.68 result, C: measured costs on Interactive Brokers (19 Nov; `docs/ai_chain_costs.md`).** 359 of 365 past trades with Nasdaq quotes at both ends (6 downloads timed out); download cost US$0.01. Round trip for US$10,000, in bp: spread when entering median 22.3 (average 32.7; nine in ten below 69.4); spread when leaving median 14.3 (average 21.1); spread cost of the round trip median 19.1, average 26.9; commission and fee 2.2; **total median 21.3, average 29.2, three in four below 34.2, nine in ten below 54.1.** #161 right. My earlier assumption of 10 bp was too low by a factor of two to three.
| rule | trades | before cost | cost | after cost | t after cost | right on after cost |
|---|---|---|---|---|---|---|
| every score, one unit | 359 | +64.8 bp | 29.2 bp | +35.5 bp | +1.93 | 54% |
| only scores of 0.8 or more | 132 | +132.8 bp | 29.0 bp | +103.8 bp | +3.13 | 60% |
**Reading.** Trading every score barely survives the real cost; trading only strong scores keeps about four fifths of its gain. This is the second independent reason for the step rule (FA-4). Limits: Nasdaq's own quotes for a small size (IBKR's routing can only do as well or better; a large order does worse); outside regular hours only limit orders are accepted, so a fill is not certain; the cost of selling short (borrow) is not included.
"""
P = """
### 3.71 'Event signals' page: the live view the founder asked for (20 Nov)
`pages/Event_signals.py`, `src/live_view.py`. **Founder (20 Nov):** show the live direction on the site so it can be used; the page must refresh itself every 30 seconds without pressing refresh; the news collection and scoring must run and check every 30 seconds; show the rule line ('enter 1 minute after, hold 60 minutes'), or whichever rule later tests crown.
**Built.** A second page of the Streamlit app, redrawn every 30 seconds: the rules in force with their evidence and measured cost (from a list at the top of `src/live_view.py`, so a later rule replaces it in one place); signal windows (BUY / SELL, entry and exit time in New York and local time, minutes left, open / closed); every scored item with its scores, figures and the other companies named; the forward record; items seen but not scored; whether the listener is running. The page only displays the listener's log -- the listener runs in its own terminal (`python -m src.news_listener run --poll 30`).
**First case shown.** NVIDIA, results of 17 Nov, own-stock score +0.7: the rule says buy at 16:22 and sell at 17:22 New York. Scored after the fact (3.69), so no live trade was possible; priced in the forward record once the vendor's bars are downloaded. No signal existed for AMD on 17-19 Nov.
**Gap named by the founder (20 Nov):** a short-seller's report on a listed company (he cites Hunterbrook on AMD) is not seen by the listener: its sources are the companies' own releases and filings, PR Newswire, the SEC and the Fed. Whether to add third-party publishers, labelled as an allegation by a party with a position, is the founder's decision; it would be a new source class with its own test.
"""
t = Path("docs/TRACK.md"); s = t.read_text()
for marker, text, msg in (("**3.68 result, C: measured costs on Interactive Brokers", C, "3.68 C result recorded (#161 right)"), ("### 3.71 'Event signals' page", P, "3.71 appended (Event signals page)")):
    if marker in s: print(f"  TRACK: {msg.split(' ')[0]} already present -- skipped")
    else: s = s.rstrip("\n") + "\n" + text; print(f"  TRACK: {msg}")
t.write_text(s)
