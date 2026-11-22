"""register_22nov_cheapest_trendforce.py -- TRACK 3.104a (SO-T2 amended BEFORE it runs: the cheapest way of trading for the same exposure) and 3.105
(TrendForce admitted as a research source; collection first, the test registered after the counts). Adds TrendForce to the listener's research
publishers and to docs/SOURCE_CANDIDATES.md and docs/SOURCES.md. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.104a SO-T2 amended before it runs: the cheapest way of trading for the same exposure (22 Nov 23:30)
Founder, 22 Nov: 'whether trading on the short x1 or short x2 fund is cheaper than directly shorting the shares is to be calculated; use whichever is cheaper.' As first written (3.104), Part 2 put the whole US$70,000 into the fund and always preferred the 2x fund: that is a bet twice as large, not a cheaper way to make the same bet, and it did not choose by cost. **Added, Part 3.** For every signal the exposure is the same (that day's share of US$70,000) and three ways are costed: (a) the stock itself, sold short when it is expected lower -- fees, 2 basis points of spread per order, and 4.8% a year for the nights held (stand-in for the share-borrowing fee); (b) a 1x inverse fund bought with the same money -- fees and 10 basis points of spread per order; (c) a 2x fund bought with HALF the money -- fees and 10 basis points per order on half the amount. The way with the lowest cost that day is taken; the result is counted with that way's real prices. The fund's running cost and daily reset are inside its price, so inside the result, not in the comparison of costs. Reported: the average cost of each way in basis points of the exposure, how often each is the cheapest, and for each pattern the result with the cheapest way always taken, with the same PASS rule. Parts 1 and 2 stay as registered. **The order of the three ways depends on the two spread allowances, which are assumptions**; with the real spreads from the founder's trading screen the comparison can be redone. Prior #204: the stock itself is the cheapest way on most signals, because a 2x inverse fund exists for two stocks only.
"""
if "### 3.104a SO-T2 amended before it runs" not in s: s = s.rstrip("\n") + A; print("  TRACK.md: 3.104a added")
else: print("  TRACK.md: 3.104a already there -- skipped")
B = """

### 3.105 TrendForce admitted as a research source; its releases collected first, the test registered after the counts (22 Nov 23:30)
Founder, 22 Nov: add the institutional source TrendForce to the research-report test -- on 19 Nov 2026 it published 'NAND Flash Prices Set to Decline in 2027 as Chinese CSP Order Cuts Outweigh North American Demand Growth' (trendforce.com/presscenter/news/20261119-13314.html; read by Claude 22 Nov: contract prices expected to fall 0-5% in the first quarter of 2027 and all NAND products to be in a falling cycle from the second quarter; spot prices already down more than 20%). **What TrendForce is:** a market-research firm (memory, foundry, servers, displays) that sells research; a third party, claims unverified; it is not a short seller and states no position.
**What was checked (22 Nov).** Its press centre lists 1,316 releases under 'Semiconductors' (264 pages), with a date and no time of day; it offers a live feed for that section. **Two limits found before any test.** (1) No time of day, as with the public calls of SR-2: the test must enter at a time that is certainly after publication. The releases come out in Taiwan working hours (the picture in the 19 Nov release is stamped 11:53), i.e. before New York opens on the same date, so 'the New York open of the release date' is after publication -- to be confirmed on a sample before it is relied on. (2) **The release names no company.** The research-report tests so far (SR-1, the SemiAnalysis route) attach a report to the company it names; a TrendForce release is about a product market (NAND, DRAM, foundry). The test therefore needs a fixed mapping from subject to stocks (for NAND: the memory makers of the list), written down before prices are looked at.
**Step 1, free (`python -m src.trendforce collect`):** the list of releases (date, title, address) and counts by year and by subject words in the titles. Nothing is read by Claude; no price is looked at. **Step 2, after the counts:** the test (code TF-1) is registered with its mapping, its entry time and its horizons (one session to several weeks, each tested); if it needs Claude to read the releases, the cost is counted first and follows the founder's money rule.
**Live.** TrendForce is added to the listener's research publishers (the same handling as SemiAnalysis: information only, no rule). Known gap: the listener attaches an item to a company only when the text names one, so a release like the NAND one, which names none, is not shown until TF-1 fixes the subject-to-stock mapping.
"""
if "### 3.105 TrendForce admitted as a research source" not in s: s = s.rstrip("\n") + B; print("  TRACK.md: 3.105 added")
else: print("  TRACK.md: 3.105 already there -- skipped")
t.write_text(s)
p = Path("src/news_listener.py"); x = p.read_text(); key = 'dict(name="SemiAnalysis", kind="research"'
if 'name="TrendForce"' in x: print("  news_listener.py: TrendForce already there -- skipped")
elif key in x:
    i = x.index(key); j = x.index("\n", i); line = x[i:j]; ind = x[x.rfind("\n", 0, i) + 1:i]
    x = x[:j] + "\n" + ind + 'dict(name="TrendForce", kind="research", position="market-research firm (memory, foundry, servers, displays); sells research; states no position", urls=["https://www.trendforce.com/feed/Semiconductors.html"]),' + x[j:]; p.write_text(x); print("  news_listener.py: TrendForce added to the research publishers (restart the listener to use it)")
else: print("  news_listener.py: the SemiAnalysis line was not found -- NOT changed; tell Claude")
p = Path("docs/SOURCE_CANDIDATES.md"); x = p.read_text(); row = "| Market-research firms | TrendForce (named 22 Nov 2026) | TF-1: the memory, foundry and server stocks of the list after its releases, by subject and direction; one session to several weeks | list of releases being collected (TRACK 3.105); live as information only |"
if "TrendForce" in x: print("  SOURCE_CANDIDATES.md: TrendForce already there -- skipped")
else:
    k = x.find("| Research publishers |"); j = x.find("\n", k) if k >= 0 else -1
    x = (x[:j] + "\n" + row + x[j:]) if j >= 0 else (x.rstrip("\n") + "\n" + row + "\n"); p.write_text(x); print("  SOURCE_CANDIDATES.md: TrendForce added")
p = Path("docs/SOURCES.md"); x = p.read_text(); row = "| TrendForce press centre, Semiconductors (trendforce.com/presscenter/news/Semiconductors; feed trendforce.com/feed/Semiconductors.html) | research releases on memory, foundry, servers | third party, claims unverified; date only, no time of day; free |"
if "TrendForce press centre" in x: print("  SOURCES.md: TrendForce already there -- skipped")
else: p.write_text(x.rstrip("\n") + "\n" + row + "\n"); print("  SOURCES.md: TrendForce added")
