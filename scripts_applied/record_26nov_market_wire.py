"""record_26nov_market_wire.py -- TRACK 3.125: market-wide headline sources -- the founder's YES, the candidates, the probe, the test MW-1 registered. Adds the row to docs/SOURCE_CANDIDATES.md. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.125 Market-wide headlines during the session: candidates, probe, test MW-1 registered (26 Nov 09:10)
**Founder, 26 Nov 07:52:** 'Since there is this kind of missing source, why dont we add it in to the readable pool?' -- YES to the gap named in 3.124.
**What is added, in the founder's own order of 20 Nov** ('a source is read and scored for money only after a test shows that its items move prices'): (1) probe which addresses answer; (2) collect their headlines with the minute, free, no paid model; (3) test MW-1; (4) only a kind of headline that passes is read and scored.
**Candidates (`src/market_wire.py`), 18 addresses:** the Federal Reserve Board (all press releases, speeches, testimony), the New York Fed (speeches), the Treasury (auction results from TreasuryDirect; press releases), the White House (presidential actions; briefings and statements), the Federal Register's list of documents filed for the next issues (tariff proclamations appear there before they are printed), the US Trade Representative, the Commerce Department, the SEC's press releases, BEA, BLS, the Energy Information Administration; and three central banks outside the US (ECB, Bank of England, Bank of Japan). The addresses are from Claude's memory and are unverified until the probe answers.
**Rights.** Works of the US federal government are not under copyright in the United States (17 U.S.C. 105), so their headlines may be collected and shown in a commercial product; Claude is not a lawyer. The three foreign central banks and the New York Fed have their own re-use terms: probed, admitted only after the terms are read. News agencies (Reuters, Bloomberg, Dow Jones) are licensed and are not candidates -- so a press report such as 'possible new tariffs' (25 Nov) stays outside the engine until the official document is filed.
**The probe (`python -m src.market_wire probe`, free):** per address -- does it answer, how many items, how many in the last 7 days, the newest, and on how many items a TIME OF DAY is given (a source that gives only the date cannot place a headline at 11:00). 'Usable now' = answers, a time of day on at least half of its items, a US federal work. Result: `docs/market_wire_probe.md`.
**Test MW-1, registered before any item is collected.** Question: after a market-wide headline of a given kind, do the four futures (S&P 500, Nasdaq-100, gold, 10-year note; 1-minute prices from Databento) move more in the next 5, 15, 30 and 60 minutes than at the same clock minutes of the 20 sessions before? One test per kind of source (Fed speech, auction result, White House action, filed Federal Register document, ...), per market, per window; the limit is 0.05 divided by the number of tests actually run; kinds with fewer than 30 timed items are 'too few to judge'. Items come from the live collection (from the day it starts) and, where a source gives past items with a time of day, from its archive. Priors when the kinds and counts are known (after the probe).
**Priors on the probe.** #224: at least 8 of the 18 answer. #225: fewer than half of those that answer give a time of day on most items. #226: the Treasury auction address and the Federal Register address both answer with a time of day.
**Minute prices of 25 Nov:** Databento's futures data ended 10:50 New York at the founder's second try; still to be run.
"""
if "### 3.125 Market-wide headlines" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.125 added")
else: print("  TRACK.md: 3.125 already there -- skipped")
p = Path("docs/SOURCE_CANDIDATES.md"); x = p.read_text()
row = "| Market-wide headlines during the session | Fed speeches and press releases, Treasury auction results, White House actions, documents filed for the Federal Register, USTR, Commerce (named after the turn of 25 Nov 2026; founder's YES 26 Nov) | MW-1: the four futures in the 5 to 60 minutes after a headline against the same minutes of the 20 sessions before; one test per kind of source | probe 26 Nov (TRACK 3.125); collected free once admitted; not read or scored until MW-1 passes |"
if "Market-wide headlines during the session" in x: print("  SOURCE_CANDIDATES.md: already there -- skipped")
else:
    L = x.split("\n"); k = next((i for i, l in enumerate(L) if l.startswith("| Market-research firms")), None)
    if k is None: L.append(row)
    else: L.insert(k + 1, row)
    p.write_text("\n".join(L)); print("  SOURCE_CANDIDATES.md: row added")
