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
