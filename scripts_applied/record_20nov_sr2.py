"""record_20nov_sr2.py -- (1) TRACK 3.77: SR-2 first-run results (public calls by well-known investors), priors #162-#164 scored, faults stated;
(2) TRACK 3.78: SR-2b registered BEFORE it is run -- the parts of the move a user could have traded; priors #165-#168;
(3) docs/SOURCE_CANDIDATES.md: status of the public-calls row. Idempotent: running it twice changes nothing."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.77 SR-2 first run: public calls by well-known investors (20 Nov 22:00)
`docs/public_calls_test.md` (commit ec21dda). **Data.** 11,805 dated headlines from Google News' free search feed, January 2018 to November 2026; Claude read 644 batches (about US$5.09 by the program's count); 1,317 headlines report a call -> 827 separate calls (523 positive, 304 negative) on 256 securities; 733 priced (35 securities have no prices on Yahoo, mostly delisted: Twitter, Activision, Silicon Valley Bank, First Republic and others). Calls: Cathie Wood 201, Warren Buffett 186, Michael Burry 116, Bill Ackman 88, Carl Icahn 65, Ray Dalio 40, George Soros 37.
**Result (average move in the direction of the call, minus the S&P 500; p from 200 sets of other dates; bar p < 0.0063).**
| group | calls | day 0 | +1 | +2 to +7 (each alone) | day 0 to +7 |
|---|---|---|---|---|---|
| all investors | 733 | +65 bp, p 0.005, PASS | +54 bp, p 0.000, PASS | none passes (+1, +6, -14, +4, -12, -13 bp) | +91 bp, p 0.025, no |
| positive calls | 460 | +83 bp, PASS | +96 bp, PASS | none passes | +196 bp, right 54%, PASS |
| negative calls | 273 | +35 bp, p 0.010, no | -17 bp, no | none; +3 and +6 are -38 and -55 bp (price ROSE) | -85 bp, p 0.875, no |
| Bill Ackman | 88 | +234 bp, PASS | +86 bp, PASS | none | +437 bp, right 57%, PASS |
| Warren Buffett | 186 | +86 bp, PASS | +53 bp, PASS | none | +90 bp, p 0.040, no |
| Carl Icahn | 65 | +69 bp, p 0.040, no | +41 bp, no | none | +174 bp, p 0.055, no |
| Ray Dalio | 40 | +88 bp, p 0.015, no | +22 bp, no | none | +145 bp, p 0.080, no |
| George Soros | 37 | +90 bp, p 0.035, no | +44 bp, no | none | -25 bp, no |
| Michael Burry | 116 | +17 bp, no | +49 bp, p 0.010, no | none; +6 is -97 bp | -105 bp, no |
| Cathie Wood | 201 | -11 bp, no | +55 bp, p 0.040, no | +3 is +73 bp, p 0.010, no | +39 bp, no |
| clusters (second investor, same direction, two weeks) | 12 | not judged (under 30) | | | |
**Priors.** #162 (pooled day 0 moves with the call and passes): RIGHT. #163 (no later session passes in the pooled group): **WRONG** -- session +1 passes (+54 bp; +96 bp after positive calls). #164 (fewer than 30 clusters): RIGHT, 12 -- the founder's 'sensational fear' hypothesis cannot be judged on these seven investors; it needs more investors or the short-report publishers (SR-1).
**What it supports and what it does not.** Supports: a positive call by these investors comes with a rise on the day and on the next session; nothing after session +1. Does not support: that negative calls push the price down -- no cell passes for negative calls, and over eight sessions the price went the other way (-85 bp against the call). Michael Burry and Cathie Wood: no cell passes. The share of calls that went the right way is 54-59% where the average is large, so a minority of big moves carries the averages.
**Limits (as registered).** Day 0 is close to close, so part of it happened before the headline and cannot be traded; headlines often appear because the price moved. Session +1 (buy at the close of day 0, sell at the next close) is the only cell here a user could have traded as measured.
**Faults (Claude's).** (a) Cost estimate US$2.70, counted US$5.09: the estimator guessed the answers shorter than they were. (b) 33 batches were not read (answers cut off or not valid JSON), almost all 2025-2026 months for Ackman, Buffett, Burry and Wood, so recent calls are under-counted in this first run. Fixed: more room for the answer and a batch that fails is read again in two halves; the test is re-run on the full list and that second table replaces this one in `docs/public_calls_test.md` (this section keeps the first-run numbers).
**Listener, second fix.** The same SK Hynix article was scored ten times on 20 Nov under pieces of its headline; an item with the same address, or whose headline is contained in one already seen from that source, is now skipped.
"""
B = """

### 3.78 SR-2b registered: public calls -- the parts a user could have traded (20 Nov 22:30, before running)
`python -m src.public_calls follow` -> `docs/public_calls_follow.md`. **Why.** SR-2's day 0 is close to close and mixes what was gone before anyone could act with what could be traded. Free daily OPEN and close prices (Yahoo) split it. **Pieces**, each minus the S&P 500's same piece, in the direction of the call: (G) previous close to the open of day 0 -- already in the price, description only; (A) open to close of day 0 -- buy at the open, only for calls whose first headline was out before that open; (B) close of day 0 to close of +1 -- all calls; (C) open of day 0 to close of +1 -- A and B together. **Main groups (judged):** all, positive, negative, each of the seven investors. Null: the same securities and directions on 2,000 sets of other dates. Bar: p < 0.0017 (0.05 / 10 groups / 3 pieces); 30 calls needed. For each cell also: the middle call (median), the average without the 5% largest and 5% smallest, the share right, and the average after 30 bp of cost (the average round trip measured on IBKR for the AI-chain list -- an assumption for these securities). **Splits (description, no bar):** positive calls in 2018-2021 and 2022-2026; by kind (statement, filing, media report); reported as that day's news; without the five most-called securities; each investor's positive calls.
**Rule for a candidate, fixed now.** A piece becomes a registered candidate rule (QUANT category: rule-based, held one session) only if it passes the bar in a main group AND the middle call is above zero AND the average after 30 bp is above zero AND it is positive in both halves of the years. Otherwise it is recorded as 'moves on average, not a rule'.
**Priors.** #165: for positive calls, piece B still passes with 2,000 sets, but its middle call is under +30 bp (a minority of large moves carries the +96 bp). #166: for positive calls, piece A is positive but does not pass -- most of day 0 is gone before the open. #167: for negative calls, no tradable piece passes. #168: piece B after positive calls is smaller in 2022-2026 than in 2018-2021.
**Limits.** The first headline found is not always the first anywhere; the open is an auction price and a market order there costs more than 30 bp in small names; daily prices only.
"""
add = ""
if "### 3.77 SR-2 first run" not in s: add += A
if "### 3.78 SR-2b registered" not in s: add += B
if add: t.write_text(s.rstrip("\n") + add); print("  TRACK.md: " + ("3.77 " if "3.77" in add else "") + ("3.78 " if "3.78" in add else "") + "added")
else: print("  TRACK.md: 3.77 and 3.78 already there -- skipped")
c = Path("docs/SOURCE_CANDIDATES.md"); x = c.read_text(); old = "| registered 20 Nov; needs a dated list of calls |"
new = "| FIRST RUN 20 Nov (TRACK 3.77): positive calls come with a rise on the day and the next session (+96 bp next session); negative calls: no support; clusters: only 12, not judged. Follow-up SR-2b registered (TRACK 3.78). Not read live yet. |"
if old in x: c.write_text(x.replace(old, new)); print("  SOURCE_CANDIDATES.md: public-calls row updated")
else: print("  SOURCE_CANDIDATES.md: row already updated or not found -- unchanged")
