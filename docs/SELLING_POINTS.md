# Selling points for customers (kept for the deck) — version 2, 15 Nov 2026

Founder's instruction (15 Nov 2026): record each advantage the tests show, written as full reasoning a person can follow, so it can be lifted into the
deck and the advertising later. Each point has: **the customer's problem → what the engine does → the proof → why that matters to the customer**, then
the evidence source and the limits that must be said with it. Past results are not a promise of future results; none of this is investment advice.

---

## SP-1. We read the results release faster than a person can

**The customer's problem.** When a company publishes its results, a person must first find the release, then read ten or more pages of figures, then
judge whether it is good or bad against what the company had promised. By the time that is done, the price has moved.

**What the engine does.** It takes the release the moment it is public, compares the reported figures with the company's own earlier guidance, reads
the new guidance, and gives one scored view in seconds: good or bad for the stock, and by how much.

**The proof, in the words to use.**
> "We can beat a person, who must find the release, read it and judge it. And speed is worth money: in our test of 756 results releases, a trader who
> followed the engine's score and entered 1 minute after the release earned +0.65% on average in the next hour. Entering 5 minutes after earned
> +0.41%. Entering 15 minutes after earned +0.25%. Every minute of delay gave away part of the move.
> The test was even unfair to us: it used the regulator's time stamp, which is usually a few minutes later than the news wire. So the test entered
> late and still showed the gain. A user who gets the score at wire time is earlier than our test, and should see at least that much of the move."

**Why that matters to the customer.** The customer does not need to know where the release appears or how to read it. The engine removes the three
slow steps (find, read, judge) and leaves only the decision.

**Evidence.** `docs/ai_chain_test.md`, family F2: 12 US companies on the AI-chain list, May 2018 to Nov 2026, the company's own stock, trade in the
direction of the own-stock score, held 60 minutes, before cost: +64.9 bp (n 365, right on 58%), +40.8 bp (n 366, 54%), +25.0 bp (n 365, 56%).
The stock had already moved +55.0 bp with the score before the regulator's stamp, which is the sign that the stamp is late.

**Limits that must be said with it.** (1) This is a candidate under forward test, not a confirmed signal: the chance that luck explains it is about 1
in 100, and the bar set in advance was about 1 in 140. (2) Gains are before trading cost, and trading after hours costs more. (3) "At least that
much at wire time" is an expectation; the live forward test measures it. (4) Trading machines are faster than any reader: the claim is "faster than a
person", never "first in the market".

---

## SP-2. We score the central bank's statement the minute it appears

**The customer's problem.** A Fed statement is short, but its meaning is in small changes of wording. Most people wait for a commentator to explain
it, and the market does not wait.

**What the engine does.** It reads the statement at release and says which way it leans for stocks.

**The proof, in the words to use.**
> "On Fed statement days since 2010, buying or selling the Nasdaq-100 future 1 minute after the statement, in the direction of the engine's score, and
> holding for one hour, earned +0.30% on average and was right on 74% of 101 days. The link was not there before the release, it held in each of four
> periods, and it held without the ten largest days. So the score is reading the statement, not the price."

**Why that matters to the customer.** About eight times a year the whole market turns on one page of text. The customer has a view of that page in
the first minute.

**Evidence.** `docs/prereg_intraday_v3e.md`, E1(c): +30.0 bp, t +4.54, 74% of 101 days with a non-zero score; S&P 500 future +27.4 bp.

**Limits.** About eight statements a year; a candidate under forward test (first live statement: 9 Dec 2026); before cost (about 0.02% for the future).

---

## SP-3. Only the original document, with its source and its time

**The customer's problem.** News apps mix facts, opinion and rumour, and the reader cannot tell which is which or when each first appeared.

**What the engine does.** It reads only what the company or the official body itself published, and shows the source and the time on every item.

**The words to use.**
> "Every item in the product comes from the company's own filing or the official body's own document, with its time. No rumours, no anonymous posts.
> If we say a company raised its guidance, you can open the page where the company said it."

**Why that matters to the customer.** An institution has to be able to defend why it acted. A dated primary source can be defended; a rumour cannot.

**Evidence.** Project rule; 756 results releases and 1,854 event filings were collected from the companies' own filings with the regulator.

**Limits.** News that first appears in the media is not covered until the company or the official body publishes it.

---

## SP-4. The figures behind the view, not only a score

**The customer's problem.** A bare "buy" or "sell" cannot be checked. A professional wants to see what the view rests on.

**What the engine does.** For each results release it lays out the figures it read: revenue, profit, operating cash flow, capital spending, free cash
flow, cash, debt, the new guidance, and how the results compare with what the company itself had guided.

**The words to use.**
> "You do not get a black box. You get the score and, next to it, the numbers the score was built on: free cash flow, the balance sheet, the guidance,
> and whether the company beat its own promise. For events that are not results, such as a change of chief executive, the engine judges the event
> against the latest results: what it does to future cash flow and how much uncertainty it adds."

**Why that matters to the customer.** The customer can agree or disagree with the reasoning in one glance, which is faster than reading the release.

**Evidence.** `docs/ai_chain_scores_summary.md`: revenue found in 99% of releases, free cash flow in 78%, next guidance in 67%.

**Limits.** "Expectation" means the company's own earlier guidance; analyst forecasts are not included. Scores of other events (not results) showed
no tradable link in our test; they are an explanation, not a signal.

---

## SP-5. A track record that shows its failures

**The customer's problem.** Every signal seller shows a rising line. The buyer cannot tell a real effect from the luckiest of many attempts.

**What we do.** Every test is written down before it is run, with the pass rule fixed in advance, and every result is published, including the ones
that found nothing.

**The words to use.**
> "We tried 311 combinations in our company-news test and we tell you so. We set the bar before we looked, and we published what failed: for
> example, the engine's guesses about which competitors gain when a company stumbles did not pay, and that is in our public record. When we say a
> result passed, you can check that the rule was written before the result."

**Why that matters to the customer.** A buyer at a financial institution is paid to distrust backtests. A record that includes its failures is the
one kind of record that buyer can trust.

**Evidence.** The public repository: `docs/TEST_BOOK.md` (every test and its result), `docs/prereg_*.md` (rules fixed before each run).

**Limits.** An honest record contains more failures than passes; the deck should present that as the reason to believe the passes.
