# Pre-registration: the AI-chain news test (company results and other company events)

Registered 15 Nov 2026, before any price was joined to a score. Code: `src/ai_earnings.py` (collection and scoring), `src/ai_chain_test.py` (the test).

## 1. The question (founder, 12-15 Nov)

The Fed-statement test (v3e E1c) found that the score Claude gives a statement tells the direction of the Nasdaq-100 future over the next hour. The founder
asked for the same test on company news for his AI-chain list, because "these companies' financial reports can alter the whole market's basic logic":
**AMD, NVDA, MU, INTC, AVGO, SNDK, SKHY, ORCL, TSM, CRWD, GOOG, META, AMZN, MSFT** (Anthropic and OpenAI to be added once listed).

Two kinds of news, both scored (founder, 15 Nov):
- **Type 1, results releases.** Scored by comparing what is reported with the company's previous guidance, and by the new guidance.
- **Type 2, other company events** (for example a chief executive's sudden resignation, an acquisition, a financing). Scored against the latest type 1
  report: what the event changes for future free cash flow, the balance sheet and the guidance, how much UNCERTAINTY it adds (investors dislike
  uncertainty), and which competitors, suppliers and customers are affected.

## 2. Data

| item | what | count |
|---|---|---|
| Type 1 texts | 8-K Item 2.02 releases (US filers) and TSMC's quarterly-results 6-Ks, June 2010 to Nov 2026 | 756 collected, 754 scored |
| Type 2 texts | 8-K filings under event items (1.01, 1.02, 1.05, 2.01, 2.03, 2.05, 2.06, 4.02, 5.02, 7.01, 8.01 and similar), the foreign filers' other 6-Ks, TSMC monthly revenue | 1,854 collected, 1,854 scored |
| Clock | the SEC acceptance stamp, converted from UTC to New York time | |
| Type 1 reader | `ai-earn-v3-2026-11-15`: facts (revenue, profit, cash flow, capital spending, free cash flow, cash, debt, next guidance) and six scores from -1 to +1: results against prior guidance, guidance change, free-cash-flow trend, own stock, market, AI demand; plus the other companies affected | |
| Type 2 reader | `ai-event-v2-2026-11-15`: event type, material 0 to 1, free-cash-flow outlook, uncertainty, own stock, market; plus the other companies affected | |
| Prices | Nasdaq-100 and S&P 500 futures, 1-minute, 08:00-16:59 New York, from June 2010; each stock's 1-minute bars 04:00-20:00 (Nasdaq exchange trades), from May 2018 | |

Each results release was read in date order within its company, with the guidance taken from the previous release. Each event was read with the facts
of the company's latest results before it. The readers saw texts only. Cost of the reads: US$0.34 (first sample, reader v1, not used), US$0.54 (trial,
readers v2 / v1, not used), US$40.44 (the scores used here).

What was looked at before this registration: the spread of the scores, the event counts and the time of day of the stamps
(`docs/ai_chain_scores_summary.md`), no prices. Type 1: 626 of 754 stamped 16:00-16:59. Type 2: 469 events with material 0.3 or more (265 from 2018).
Materiality cut-offs 0.2 / 0.3 / 0.5 are all tested (grid rule), not chosen.

## 3. The seven families

Trade = sign(score) x return after the stamp. A score of 0 = no position. Price at minute m = last trade before m, at most 5 minutes old. Returns in
basis points before cost. A cell needs 30 observations.

| family | news | price | signals | windows |
|---|---|---|---|---|
| F1 | results stamped 16:00-16:40, US filers; one observation per day (average score of that afternoon's releases; entry counted from the last stamp) | Nasdaq-100 future, from 2010 | the six type 1 scores | enter 1 / 5 / 15 min after the stamp; hold 15 min, 30 min, to 16:59, to the next 09:35, to the next 16:00 |
| F2 | results, US filers | the company's own stock, from May 2018 | the six type 1 scores | enter 1 / 5 / 15 min after; hold 15, 30, 60 min, to the next 09:35, to the next 16:00 |
| F3 | results, US filers | the other listed companies the reader named as affected | the reader's direction for that company; and "copy the reporter's own sign" | as F2 |
| F4 | events, US filers, material 0.2+ / 0.3+ / 0.5+ | own stock, from May 2018 | own stock, free-cash-flow outlook, minus uncertainty (each at the three cut-offs) | 5 min after the stamp: hold 30, 60 min, to the next 09:35; or enter at the next regular session: hold 30, 60 min, to 16:00, to the 16:00 after |
| F5 | events, material 0.3+ | the other listed companies named as affected | direction; copy the reporter | as F4 |
| F6 | events, US filers, material 0.3+ / 0.5+ | Nasdaq-100 future, from 2010 | market score, own-stock score | 5 min after: hold 30, 60 min; next regular session: hold 30, 60 min, to 16:00 |
| F7 | foreign filers (TSMC; SK Hynix when its prices are on disk): results, monthly revenue, material events | own stock, from May 2018 | own stock | next regular session: hold 30, 60 min, to 16:00, to the 16:00 after |

"Next regular session" = 5 minutes after the stamp if it falls 09:30-15:49, otherwise 09:35 on the next trading day. F7 uses only this entry because a
foreign filer's SEC stamp can be hours after the release in Asia.

**Family p.** The largest |t| over all signals and windows of a family, against the same quantity when the scores are shuffled across observations
2,000 times (seed 20261115). F3 and F5 have several companies per event, so the unit is the event: each window's average return is removed first, and
the null flips each event's whole set of signs at random.

## 4. Verdict rule (fixed before running)

- A family **passes** when family p < 0.0071 (0.05 / 7) AND the best cell's mean is positive (prices follow the score) AND above the cost: 2 bp for the
  future (as in v3e); 10 bp for a stock, an assumption because stocks trade wider outside regular hours.
- Use category by the founder's rule: a best cell held minutes (or to 16:59) = **SUBJECTIVE grade A candidate**; a best cell held to the next open or
  close = **QUANT candidate**. Either one then needs its own registered rule and a forward log before it is called a signal.
- A family with p below the bar but prices moving AGAINST the score is recorded and is not a pass.
- Checks printed for every best cell, whatever the verdict: net of cost; four periods; without the ten largest moves; large scores against small
  scores; the 30 minutes before the stamp (should show nothing); in F2, a price-only rule at the same cell (follow the stock's move so far) and the
  score rule split by whether the move so far agrees with the score.
- Everything is recorded, including families that do not pass.

Code check before delivery, on made-up prices with a drift planted in one family only: that family passed (p 0.000), the other six did not
(p 0.27 to 0.87).

## 5. Priors (Claude, before any run; counted if wrong)

- **#145** F1 (results -> Nasdaq future): does not pass.
- **#146** F2 (results -> own stock): does not pass at 0.0071, but the own-stock score's mean is positive in more than half of its fifteen windows.
- **#147** F3 (results -> affected companies): does not pass, and "copy the reporter" does at least as well as the reader's direction in more than half
  of the windows.
- **#148** F4 (events -> own stock): does not pass.
- **#149** F5 (events -> affected companies): does not pass.
- **#150** F6 (events -> Nasdaq future): does not pass.
- **#151** F7 (foreign filers): does not pass.
- **#152** F2: at the score rule's best cell, the price-only rule (follow the move so far) has the higher mean.

## 6. Limits stated

- **"Expectation" is the company's own earlier guidance.** Analyst forecasts are not in the filings and are not used.
- **Only the companies' own SEC filings are read.** News first published elsewhere (media reports, rumours) is not in the test; an 8-K can also follow
  the first public word of an event. The stamp is when the filing became public, which can be minutes after the press release reached the wires, so
  the entry here is, if anything, late.
- **Prices move within seconds of a results release.** The test asks only what happens AFTER the entry point; the jump before it is not earned.
- Stock prices are Nasdaq-exchange trades only and are thin outside regular hours: observations without a trade in the last 5 minutes drop out.
  Unadjusted prices: a move above 50% between two points is treated as a share split and dropped.
- Several companies often report on the same afternoon. F1 handles this by one observation per day; F2 treats each company as its own observation,
  although same-day stocks share the market's move.
- Scores of exactly +1 or -1 are common in type 1 (own stock: 32% at 0.9 or beyond); the test uses the sign, so this loses no observations.
- Intel's cash-flow tables are often outside the collected text; SK Hynix's results could not be separated from its other filings and sit in type 2.
- SK Hynix has no minute prices on disk yet; its events enter F7 once they are downloaded.
- The reader is one model (`claude-sonnet-5`) run once per text; its consistency on repeat reads has not been measured.
- Seven families, 311 cells: the family p and the 0.0071 bar are what protect against a lucky cell.

## 7. Results

| date | what | result |
|---|---|---|
