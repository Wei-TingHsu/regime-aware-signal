# Selling points for customers (kept for the deck)

Founder's instruction (15 Nov 2026): record each advantage the tests show, so it can be used later for the deck and for advertising.
Rule for this file: every point has (1) the sentence for the customer, (2) the evidence with its source, (3) the limit that must be said with it.
Past results are not a promise of future results; none of this is investment advice.

## SP-1. Faster than a person at reading company results (recorded 15 Nov 2026)

**For the customer:** "When a company on the list publishes its results, the engine reads the release and gives a scored view within seconds. A person
has to find the release, read it and judge it."

**Evidence** (`docs/ai_chain_test.md`, family F2; 12 US companies, May 2018 to Nov 2026; 756 results releases scored by Claude from the text alone):
trading the company's own stock in the direction of the own-stock score, held 60 minutes, before cost:

| entered after the SEC time stamp | average gain | right on | trades |
|---|---|---|---|
| 1 minute | +0.649% | 58% | 365 |
| 5 minutes | +0.408% | 54% | 366 |
| 15 minutes | +0.250% | 56% | 365 |

- The earlier the entry, the larger the gain: speed is worth money, which is the customer's problem the product solves.
- The backtest entered LATE: the SEC time stamp is usually some minutes after the news wire. A user who receives the score at wire time is earlier
  than this backtest.

**Limits to say with it:** the result is a near miss of the strict bar set in advance (chance of luck about 1 in 100; the bar was about 1 in 140), so
it is a candidate under forward test, not a confirmed signal. Gains are before trading cost, and after-hours trading costs more. Trading machines
react faster than any reader, human or AI: the claim is "faster than a person", never "first in the market".

## SP-2. Central-bank statements scored the minute they appear (recorded 15 Nov 2026)

**For the customer:** "The engine scores each Fed statement at release and says which way it leans for stocks."

**Evidence** (`docs/prereg_intraday_v3e.md`, E1(c); June 2010 to Nov 2026): entering the Nasdaq-100 future 1 minute after the statement in the
direction of the score and holding 60 minutes gave +0.300% on average, right on 74% of 101 statement days; the checks passed (nothing before the
release, four periods, without the ten largest days).

**Limits:** about eight statements a year; a candidate under forward test (first live statement: 9 Dec 2026).

## SP-3. Primary sources only, every item with its source and time (recorded 15 Nov 2026)

**For the customer:** "Every item comes from the company's own filing or the official body's own document, with its time. No rumours, no
anonymous posts."

**Evidence:** project rule; 756 results releases and 1,854 event filings were collected from the companies' own SEC filings.

**Limit:** news that first appears in the media is not covered until the company or the official body publishes it.

## SP-4. The numbers behind the view, not only a score (recorded 15 Nov 2026)

**For the customer:** "For each results release the engine shows the figures it read: revenue, profit, cash flow, free cash flow, cash, debt, the
new guidance, and how the results compare with the company's own earlier guidance."

**Evidence** (`docs/ai_chain_scores_summary.md`): revenue found in 99% of releases, free cash flow in 78%, next guidance in 67%.

**Limit:** "expectation" means the company's own earlier guidance; analyst forecasts are not included.

## SP-5. An honest track record (recorded 15 Nov 2026)

**For the customer:** "Every test is written down before it is run, and every result is published, including the ones that found nothing."

**Evidence:** the public repository: `docs/TEST_BOOK.md` lists every test with its result; `docs/prereg_*.md` hold the rules fixed before each run.
Example: the reader's "who gains, who loses" directions for competitors and suppliers did NOT pay (families F3, F5), and that is on record.

**Limit:** an honest record includes failures; the deck should present it as a reason to trust the passes.
