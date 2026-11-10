"""register_11nov_n1v3.py -- registers N1 v3 BEFORE any v3 run, and puts the agenda on TRACK. Idempotent.    python scripts_applied/register_11nov_n1v3.py"""
from pathlib import Path
REG = """
## 5. N1 v3 — the founder's two explanations for the null, registered 2026-11-11 01:40 before any run

Origin (founder, 11 Nov): the contradicting releases we read did not explain the rebound, so either **(1) we missed the information source that is the
real reason**, or **(2) the document read was aimed wrong and the critical information was not captured**. Recorded beside them, Claude's third reading:
after a ≥ 4% fall the five-session rebound rate (57–60%) is only 2–4 points above how often any five sessions rise, so there may be no rebound to explain.

| step | what changes vs v1/v2 | fixed numbers now grid axes |
|---|---|---|
| **v3a documents** (explanation 1) | BLS: jobs, CPI, **PPI, JOLTS, import/export prices**; FOMC statements; **speeches by the Fed Chair and Vice Chairs**; every event day back to the BLS archive, not only the GDELT era; fetched from the agencies' own archives (index pages, write-once) | window +1 … **1, 2, 3, 5, 7, 10** sessions; document family all / BLS / labour / prices / Fed |
| **v3a read** (explanation 2) | each document read **once, on its own**, prompt `n1-doc-v3-2026-11-11`, own cache: surprise sign, drivers, breadth, **implication for equities −1…+1**, implication for rates. No GDELT story is needed, so a wrong story cannot spoil the score. Contradiction = −(event sign) × (equity implication): a fall then a supportive document, or a rise then a negative one | cutoff **0.1 … 0.7** in steps of 0.1 |
| **v3a grid** | statistic = reversal rate WITH a contradicting document minus WITHOUT, points, each side n ≥ 20; per index × direction; horizons 1, 3, 5, 10 | judged against the best cell of the same grid on outcomes shuffled within index-and-direction (300 draws); four groups, so a group counts only at **p_family < 0.0125**; best cell reported by era |
| **v3a size** | does the SIZE of the reversal (not only its sign) rise with the contradiction score: rank correlation, 1,000 shuffles; mean score in the largest quarter of reversals vs the rest | windows 3, 5, 10 × horizons 1, 3, 5, 10 (48 cells; ~2.4 below 0.05 by chance) |
| **v3b corpus survey** (no LLM) | how many event days have a same-day document in the project's own corpus (8-K, 6-K, FOMC, Federal Register), by source — decides whether a corpus-based CAUSE read replaces GDELT | — |
| not in v3a (listed, not fetched) | retail sales (Census), GDP (BEA), other issuers' earnings in the window (needs v3b), QQQ events (QQQ not in the panel), 2001–2012 GDELT archives | — |

Code check before delivery (not a result): on five synthetic noise datasets the grid returned p_family < 0.05 in 2 of 16 groups — as chance allows — which is why the bar is 0.0125 per group.
Cost: one read per document, text capped at 15,000 characters; measured on disk by `news_events3 cost` before reading; `--max-usd 12`; N1 total stays under the US$25 cap (US$10.3 spent).

Priors (Claude, before any run; counted if wrong):
- **#124** no index × direction group reaches p_family < 0.0125 in the v3 grid — a contradicting official document in the window does not raise the reversal rate, at any cutoff, window, horizon or family.
- **#125** in the size test at most 5 of 48 cells show p < 0.05, and they do not share a sign pattern.
- **#126** fewer than 40% of event days have a same-day document in the project's own corpus; from 2020 the share is above 50%.
- **#127** the documents' mean equity implication is positive after falls and after rises alike (official text leans reassuring), within 0.1 of each other.

### v3 results

| date | step | result | prior |
|---|---|---|---|
"""
TRACK = """
### 3.46 Agenda from 11 Nov 01:40 — N1 v3 registered; the signal-creation redirect put to the founder

| # | step | why it matters to the business | founder decides |
|---|---|---|---|
| 1 | **N1 v3a** — wider official documents (PPI, JOLTS, import prices, Chair / Vice Chair speeches), window to 10 sessions, one story-free read per document, cutoff × window × horizon × family grid, reversal SIZE test (`src/news_events3.py`; prereg_news_events §5; priors #124–#127) | tests the founder's two explanations for the N1 null directly; if a document family passes, it is a "what to watch after a crash" product line | nothing — registered, running tonight |
| 2 | **N1 v3b** — corpus survey: event days with a same-day 8-K / FOMC / Federal Register document | decides whether the cause read moves from GDELT to primary filings | after the survey: register the corpus cause read or not |
| 3 | **N1-a forward log** — short SPY at the close of a ≥ 4% up session, one session (the single PASS cell, n 42) | the only candidate trade rule N1 produced; needs live evidence before any claim | whether to wire it into `deeper forward` |
| 4 | **QQQ into the price panel** | N1 has no Nasdaq-100 events without it | yes / no |
| 5 | **S1 — risk signals from the survivors**: sell the forecast of correlation, volatility and regime change (gold–equity correlation persistence, skill 0.26; abnormal-day runs before regime changes, p 0.000) as a hedge-ratio / exposure signal rather than a direction call | the relationships that survived are about risk, which institutions buy and which is far more predictable than direction | whether to register S1 |
| 6 | **S2 — cross-sectional filing signal**: each issuer's 8-K read scored, then that stock's return relative to its sector over the next 1–20 sessions; thousands of stock-events instead of 40 macro events | the LLM document layer is the project's own data; one stock at a time is where a text edge is most plausible and where the statistics have power | whether to register S2 (needs single-stock prices) |
| 7 | **S3 — conditional event trades**: the Fed-day reaction that differs by regime (p 0.005), traded only in the regime and volatility state where it is strong, entry after the announcement | turns the strongest surviving relationship into a rule with an entry and exit | whether to register S3 |
| 8 | Carried: F2b lead time of the abnormal-day signal; Group C returns-only tests; R7 every event class by regime; regime × fast-state hierarchy | completes the regime audit | order |
| 9 | Buyer conversation (TRACK §3.7 customer interviews) | tells which of 5–7 a buyer would pay for before weeks are spent on the wrong one | when, and with whom |
"""
p = Path("docs/prereg_news_events.md"); s = p.read_text()
if "## 5. N1 v3" in s: print("  prereg_news_events: v3 already registered -- skipped")
else: p.write_text(s.rstrip("\n") + "\n" + REG); print("  prereg_news_events: §5 N1 v3 registered (priors #124-#127)")
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.46 Agenda from 11 Nov" in s: print("  TRACK: 3.46 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.46 agenda appended")
