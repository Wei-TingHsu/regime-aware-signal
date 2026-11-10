# Pre-registration — N1: news-attributed large moves and the releases that follow them (TRACK §3.42)

*Registered 2026-11-06, before any run. Origin: the founder, 6 Nov evening — after the 5 Nov sell-off (S&P −4.4%, Nasdaq-100 −6.4%, SOX −12.3%) and
the 6 Nov payrolls beat (+165,000): "every plummet or sudden rise is the result of news released that day; see whether, in the next 1–5 sessions, a
bureau statistic shows a reason supporting the reverse — and read the constitution of the statistic, not just whether there is a turning point."*

## 1. Sources (standing rule, 6 Nov: no tertiary sources — Wikipedia and the like are never used)

- **Price events:** SOX (Philadelphia Semiconductor index), QQQ, S&P 500, close to close, from the price panel; event = |move| ≥ 4%; both signs; from
  1995 (SOX) / 1999 (QQQ).
- **Same-day news:** GDELT (the project's `gdelt_ingest` — themes, actors, tone, source URLs for the day), the project's own corpus on that day (FOMC
  statements and minutes, 8-K/6-K filings and exhibits, Federal Register documents), and the primary releases of the day (BLS, BEA, Census, Fed,
  Treasury). Text is the primary document where it exists; otherwise GDELT's structured fields.
- **Releases in the window:** the Employment Situation (industry tables B-1), CPI (components), PPI, retail sales, GDP, FOMC — the release text and tables
  from the issuing agency's archive. **AI-related occupations** (computer and information research scientists, data scientists, software developers,
  operations research analysts, information security analysts) come from the annual OEWS, not the monthly report; they enter as a yearly series, lagged.

## 2. Steps

| step | what | schema / statistic |
|---|---|---|
| **S1 cause** (LLM) | each event day's news read under one fixed schema | cause class ∈ {macro release, central bank, earnings / guidance, geopolitics, election / regulation, credit / liquidity, health, **no identifiable news — positioning**}; confidence 0–1; one-line reason; the class "no identifiable news" is the test of the founder's "meme" claim |
| **S2 composition** (LLM) | every scheduled release in sessions +1 … +5 after the event, read for what drove it | surprise sign; the components that drove it (industries for payrolls; core vs energy / shelter for CPI); **contradiction score** −1…+1: does the composition contradict (+) or confirm (−) the event's cause story |
| **S3 tables** | reversal rate (sign of the 1 / 3 / 5-session return opposite to the event) by index × direction × cause class; with vs without a contradicting release in the window | H-table standard per cell (n ≥ 30, gap ≥ 10 points vs the base rate, random-date null); family null across classes |
| **S4 learner** | walk-forward ridge and gradient-boosted trees: cause class, move size, prior 20-session trend, VIX level, release-in-window, surprise sign, contradiction score → the 1–5-session return after the event and after the release | net Sharpe vs the best-of-search null (outcomes permuted) and vs the plain rule "buy the session after a ≥ 4% fall" |
| **S5 annual** | OEWS AI-occupation employment, year on year, against SOX's annual return and the year's count of ≥ 4% days | descriptive; n ≈ 12 years |

Cost: a few hundred event-day reads and ~200 release reads, measured on disk before the run (`news_events cost`); cap US$25.

## 3. Priors (Claude, before any run; counted if wrong)

- **#117** the LLM assigns "no identifiable news — positioning" to 20–35% of ≥ 4% days, and the share is higher after 2017 than before.
- **#118** the 5-session reversal rate after a ≥ 4% fall is above 50% for all three indices (mean reversion after crashes), and below 50% after a ≥ 4% rise.
- **#119** a contradicting release inside the window does not raise the reversal rate beyond the family null — the reversal happens with or without the statistic.
- **#120** the learner does not beat "buy the session after a −4% day" out of sample.
- **#121** the 5 Nov 2026 event reads as a mix of positioning and election / regulation at confidence under 0.7; the 6 Nov payrolls composition (business services, health care; information flat) scores near zero on contradiction of an AI-demand story.

## 4. Results

| date | step | result | prior |
|---|---|---|---|
| 2026-11-06 | S0 events + fetch + digest + cost | 539 index-events on 476 sessions (SOXX stand-in for SOX; QQQ not in panel; SPY for S&P); 40 digests on disk; cost ≈ US$0.29 / 40 digests | — |
| 2026-11-07 | S1 cause read, **v1** digest (top-50 by mentions), prompt n1-cause-v1 | 246 event days read (2009 → 2026; 181 GDELT files, 3.2 GB; 2022-11-10 missing from GDELT, 404). Classes: no_identifiable_news_positioning 168, geopolitics 18, health 16, credit_liquidity 13, election_regulation 10, earnings_guidance 10, central_bank 9, macro_release 2. Mean confidence 0.54. Share "no identifiable news — positioning" **68%** (before 2017 77%, from 2017 66%). | **#117 wrong (counted)** — predicted 20–35%. Caveat recorded with it: the v1 digest ranks GDELT records by mentions, which on any day is wars, elections and diplomacy; market, earnings and Fed records barely surface, so part of the 68% is the instrument not seeing finance rather than the market moving on nothing. The v2 digest below tests how much. |
| 2026-11-07 | S2a release fetch | 0 BLS releases fetched — every archive request failed silently (v1 fetcher swallowed the error; BLS refuses scripted clients without a contact address in the User-Agent). 38 FOMC-statement pairs found in the +1…+5 window from the corpus. S2b/S3 contradiction split not yet run. | — |
| 2026-11-07 | **Amendment — v2 digest and prompt version registered before running** | `news_events digest --v2` adds to each day a FINANCE / MACRO / EARNINGS section: the GDELT records whose source slug carries a market, Fed, yield, earnings, chip, bank, tariff, oil or pandemic term (fixed keyword list in `src/news_events.py`), ranked by mentions, up to 40. Same classification prompt under version **n1-cause-v2-2026-11-07**, own cache; v1 reads stay on disk and in this table. Prior **#123:** the v2 share of "no identifiable news" falls to 35–50% — still above #117's band — with the gain going mostly to earnings/guidance and central-bank; the before/after-2017 ordering is unchanged. S3 tables and S4 learner run on v2; v1 tables kept for comparison. | — |
| 2026-11-11 | S1 cause read, **v2** digest (finance section), prompt n1-cause-v2 | 245 event days. Classes: no_identifiable_news_positioning 119, geopolitics 26, earnings_guidance 26, election_regulation 22, health 18, credit_liquidity 13, central_bank 11, macro_release 10. Share "no identifiable news — positioning" **49%** (before 2017 70% n 57, from 2017 42% n 188; the pre-2013 archives carry no source URL so those days have no finance section — the before/after split is confounded by the instrument, not evidence). Mean confidence 0.54. One read failed (2022-10-07, `.failed.txt`). | **#123 right** (35–50%). **Instrument finding, recorded:** the finance section is a substring match on URL slugs ("stock" catches Stockton; 4,680 matches on 5 Nov 2026, ranked by mentions, mostly politics); on 5 Nov it surfaced the Democrats-AI-giants story and the oil slump but not Qualcomm. GDELT is a weak same-day source for market causes even filtered; the 49% is an upper bound on "positioning". A v3, if run, reads the day's own corpus (8-Ks, FOMC, Federal Register) instead of GDELT. |
| 2026-11-11 | S2b release composition | 192 release reads (empsit 81, cpi 73, fomc 38); contradiction score mean +0.15, share > +0.3: 28%, share < −0.3: 12%. 6 Nov payrolls read: surprise +1, breadth 0.65, contradiction +0.00; drivers [{"component": "professional and business services", "contribution": "large", "direction": "+"}, {"component": "health care", "contribution": "moderate", "direction": "+"}, {"component": "transportation and warehousing", "contribution": "moderate", "direction": "+"}, {"component": "manufacturing (incl. computer/electronic products)", "contribution": "small", "direction": "+"}, {"component": "prior months' revisions (Aug/Sept +84,000 combined)", "contribution": "moderate", "direction": "+"}]. | **#121** right: 5 Nov read as election_regulation / geopolitics at confidence 0.55. |
| 2026-11-11 | S3 tables, v1 and v2 (identical ALL rows; the cause classes change only the sub-rows) | 12 index × direction × horizon cells, H-table standard. **One PASS:** S&P the session after a ≥ 4% *rise* — reversal 67% vs base 45%, n 42, p 0.006. SOX after a fall: 60% vs 53% at one session (p 0.029) but gap 7 < 10 → FAIL. All 3- and 5-session cells FAIL. Release split: SOX fall h1 with contradicting release: n 30, reversal 57% vs base 53%, gap +4, p 0.710 → FAIL<br>SOX fall h1 without: n 201, reversal 60% vs base 53%, gap +7, p 0.033 → FAIL<br>SOX fall h3 with contradicting release: n 30, reversal 50% vs base 54%, gap -4, p 0.710 → FAIL<br>SOX fall h3 without: n 201, reversal 58% vs base 54%, gap +3, p 0.338 → FAIL<br>SOX fall h5 with contradicting release: n 30, reversal 50% vs base 55%, gap -5, p 0.573 → FAIL<br>SOX fall h5 without: n 200, reversal 58% vs base 55%, gap +3, p 0.388 → FAIL<br>SOX rise h1 without: n 199, reversal 51% vs base 47%, gap +4, p 0.276 → FAIL<br>SOX rise h3 without: n 199, reversal 45% vs base 46%, gap -0, p 0.939 → FAIL<br>SOX rise h5 without: n 199, reversal 49% vs base 45%, gap +5, p 0.193 → FAIL<br>SPX fall h1 without: n 43, reversal 63% vs base 54%, gap +8, p 0.280 → FAIL<br>SPX fall h3 without: n 43, reversal 58% vs base 58%, gap +0, p 1.000 → FAIL<br>SPX fall h5 without: n 42, reversal 62% vs base 59%, gap +3, p 0.729 → FAIL<br>SPX rise h1 without: n 40, reversal 68% vs base 45%, gap +22, p 0.008 → PASS<br>SPX rise h3 without: n 40, reversal 57% vs base 42%, gap +16, p 0.045 → PASS<br>SPX rise h5 without: n 40, reversal 52% vs base 41%, gap +11, p 0.149 → FAIL. | **#118** half: after falls both indices reverse > 50% at five sessions (SOX 57%, SPX 60%) as predicted, but after rises SPX is 55%, not below 50% — **counted wrong**. **#119** right: a contradicting release in the window does not lift the reversal rate past the standard. The PASS cell is one of twelve: **forward-log candidate N1-a** — "short SPY at the close of a session that rose ≥ 4%, one session" — logged, not promoted. |
| 2026-11-11 | S4 learner, v2 features | h = 1: best {'train': 200, 'ridge': 100.0, 'h': 1} Sharpe +1.42 vs null q95 +1.53, p_family 0.075; plain "buy the session after a ≥ 4% fall" +1.87 (n 278, from the run log). h = 3 and 5: null. v1 features did better at h = 1 (+2.12, p 0.005) and still lost to the plain rule — more cause detail added noise. | **#120 right.** Compendium tag: **neither** quant nor discretionary. |
| 2026-11-11 | Cost | ≈ US$10.3 of the US$25 cap (cause reads 0.31 + 1.58 + 2.73; release reads 5.72). | — |

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
