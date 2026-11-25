"""record_25nov_fund_way_result_and_decision.py -- TRACK 3.121: the result of measurement FD-1 (priors #221-#223 scored); the founder's final way to trade a match;
the Yahoo fault of the daily check and its fix; the first match of the forward record. Adds the NYSE calendar to docs/SOURCES.md. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.121 FD-1: result; the founder's way to trade a match; the Yahoo fault of the daily check; the first match (25 Nov 23:30)
**FD-1, result (`docs/selloff_fund_way.md`).** The three rules redone by buying the inverse fund with cash, nothing borrowed; a rule passes with 20+ separate days, a gain on average and a chance under 0.0167.
| rule | past trades | a fund existed | separate days | the fund way, average a day | 95 in 100 range | chance | the stock way, same days | verdict |
|---|---|---|---|---|---|---|---|---|
| SS-2a | 185 | 23 | 23 (from Aug 2022) | +US$267 (+38 bp) | -1,015 to +1,528 | 0.33 | +US$372 (+53 bp) | does not pass |
| SS-2b | 372 | 6 | 5 | -US$386 (-55 bp) | -2,575 to +2,533 | 0.65 | -US$320 (-46 bp) | too few days to judge |
| SS-2c | 380 | 60 | 57 (from Aug 2022) | +US$195 (+28 bp) | -148 to +550 | 0.13 | +US$499 (+71 bp) | does not pass |
**Reading.** (1) Most past trades cannot be done with a fund at all: 162 of 185 (SS-2a), 366 of 372 (SS-2b), 320 of 380 (SS-2c). (2) Where a fund existed, the fund way earned less than the stock way under all three rules (SS-2c: half the size by design, plus the fund's wider spread). (3) No rule is shown to make money the fund way: the averages are positive for SS-2a and SS-2c but could be chance. This is NOT a failure of the rules themselves -- their registered test is the forward record (30 days each) -- it says the fund way is unproven and the history too short.
**Priors.** #221 (under 40 days with a fund for each rule): MIXED -- right for SS-2a (23) and SS-2b (5), wrong for SS-2c (57). #222 (no rule passes the fund way): RIGHT. #223 (the fund way earns less than the stock way on the same days, all three): RIGHT.
**Founder, 25 Nov 22:29 and 22:59, word for word:** 'And i forgot a few stocks dont have short funds, hence we use shorting' ... 'short with 35000.'
**The founder's way to trade a match (final, replaces the decision in 3.120).** Where the stock has an inverse fund: buy it with the account's own cash (US$70,000 with a 1x fund; where the rule also buys the S&P 500 fund, US$35,000 each). Where it has none: sell the stock short with US$35,000, half the account (and buy US$35,000 of the S&P 500 fund where the rule says so). Why US$35,000: Claude showed that the one past trade with a margin call (Morgan Stanley, 17 Sep 2008, +56.7%) was in a stock without a fund; with half the account sold short the cushion falls under a 50% limit only if the stock about doubles. The gain per trade is halved too.
**In the code (`src/selloff_live.py`).** The registered measure of the forward record is unchanged (the stock sold short with the whole account, in basis points). Added beside it: 'the founder's way' for every match and its result in US dollars after cost, with the spreads measured in 3.114. The Severe Sell-off block now names the trade the founder's way.

**The fault in the daily check of 25 Nov, 09:34 and 09:46 New York.** The founder: 'alot of the results shown below are delisted and failed download, what the hell is this'. Cause: the block ran `selloff_real fetch` (174 securities, one request each) and straight after it the daily check (121 securities at once); Yahoo refuses requests that come too fast, and its software words every refusal as 'possibly delisted'. Nothing is delisted. First run: prices for 46 of 121 securities; second run: 111 of 121, missing COST, DUK, MDLZ, MS, PFE, PG, TGT, TSLA, VZ, SMH. **Claude's mistake:** the code went on with old prices for the missing names without saying that the check could be wrong, and the block put the two downloads back to back.
**Fix.** Refused names are asked again one by one after 20, 40 and 60 seconds; Yahoo's wording is replaced by a plain message; if names are still missing, the run prints a warning and the forward record and the block carry it.
**The first match of the forward record: SS-2a, SanDisk (SNDK), closed -11.1% on 24 Nov 2026.** Entry: the open of Wed 25 Nov; exit: the close of the second session after the sell-off = Fri 27 Nov (Thu 26 Nov is Thanksgiving; on 27 Nov the market closes at 13:00 New York). The founder's way: SNDK has no inverse fund -> short with US$35,000. **Caveat, recorded before the result is known:** the match appeared in the run with 10 names without fresh prices (among them the semiconductor fund SMH) and did not appear in the first run (46 of 121). It stands in the record only if a run with all prices confirms it; if a full run does not show it, that is recorded here as a false match caused by the fault.
**Second fault found while checking this (Claude's):** the code did not know market holidays and would have shown the exit as Thu 26 Nov. Fixed with the NYSE Group calendar for 2026-2027 (holidays, and the three days closing at 13:00); the results themselves were never affected (they use the sessions in the price data).
"""
if "### 3.121 FD-1: result" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.121 added")
else: print("  TRACK.md: 3.121 already there -- skipped")
p = Path("docs/SOURCES.md"); x = p.read_text(); key = "Holiday and Early Closings Calendar"
row = "| NYSE Group, 'NYSE Group Announces 2026, 2027 and 2028 Holiday and Early Closings Calendar' (Intercontinental Exchange press release, ir.theice.com) | market holidays and 13:00 closes in the daily check of the sell-off rules (TRACK 3.121) | primary; read 25 Nov 2026 |"
if key in x: print("  SOURCES.md: NYSE calendar already there -- skipped")
else: p.write_text(x.rstrip("\n") + "\n" + row + "\n"); print("  SOURCES.md: NYSE calendar added")
