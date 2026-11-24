# The addition and subtraction pool: the plan as the founder stated it

Recorded 24 Nov 2026 from the founder's messages of 24 Nov (15:34 and 16:34 Taipei). **Part 1 is the founder's plan, point by point, in the exact words shown to him in the chat. It is not to be reworded from memory.** Part 2 is Claude's proposal for how to do it and is NOT yet confirmed by the founder. Nothing here has been built or tested.

## Part 1. The founder's points

**A. What we look for**

1. A fast trend: the price of a stock moves clearly up or down over a stretch that a person sees at once on the daily chart. The founder's examples: NVIDIA down from 6 Oct to 20 Nov 2026; AMD up from 4 Apr to 11 May 2026.
2. No length is fixed. "2 to 6 weeks" was an estimate by eye, not a rule ("2 weeks" meant 14 sessions). A trend of 13 sessions, or of any other length, must not be missed because of a number. Finding a rule that sees what the eye sees (the "raw-eye-measured length") is Claude's job, not the founder's.
3. Inside a trend there are crests and temporary troughs. AMD: start near US$190, a crest on 24 Apr, about a week of slight slide, then up to the crest of 11 May.

**B. News**

4. The founder's assumption: a turn that lasts about a week is caused by released news. Profit-taking turns the price for 1 to 3 days at most; large institutions reducing a position take months, which is not a temporary turn.
5. Addition and subtraction: good news adds to a pool, bad news subtracts from it. A temporary trough inside an uptrend means bad news was subtracted; later good news adds again and the trend goes on.
6. News is recorded in the pool immediately when it is released. It does not wait for the chart to confirm a crest or a trough. Example: the news that NVIDIA brings Jensen Huang back as CEO goes into the addition pool at once, although the daily chart shows no crest yet and that day closed below its open.
7. Linked news is compared. The return of the CEO is compared with the price fall on the day of his dismissal: how much of that fall was recovered, or more than recovered. In theory, undoing a news item should bring the same amount back.
8. Known difficulties, to be solved and not hidden: (a) two linked items can be weeks apart; (b) other news on the same day makes one item's share of the move hard to separate; (c) some news cannot be valued through a company valuation at all -- a CEO's reputation is an intangible asset.
9. "News" is every informative source, and the list is open: the company's own news, other companies' news that reaches it through the supply chain, industry research, government policy, the Fed, talks by CEOs such as fireside chats, and more. Some sources cost money. The set of sources that feeds the pool will change over time, and the pool must be built so that it can change.
10. The time of publication is the most important data in this research. A lag between a news item and the price move can put a support or resistance level in the wrong place. News released at the weekend (big announcements, war, government) shows in the price on Monday all at once.

**C. Support levels and the product**

11. The crest that ends an uptrend becomes a support level for months; a temporary trough inside the trend also supports a later sell-off. The founder's reason: the level holds while the story behind it is intact.
12. The product names the most important news story behind each support level, says that a price near the level is a short-term buying price while that story is intact, and warns when a news item breaks the story.

**D. The page (later)**

13. On the "Look up an Asset" tab, the stocks that have a pool appear at the top as rounded buttons that enlarge under the mouse, by ticker (AMZN, NVDA ...), as a quick entry. Any other asset traded on a US exchange is still reached through the search bar and has no pool.
14. The pools show only inside a stock's page, never on the empty search page. There are two separate pools. ADDITION: all information gathered up to the stock's historical highest price. SUBTRACTION: information deducted since that highest price. On a day of a new historical high the subtraction pool is empty. Bad news after the high becomes the first line of the subtraction pool; if the same information line stands in the addition pool it is taken away from there; if it does not, nothing is taken away.

**E. Valuation and the order of work**

15. The fact base: yes. Assumptions come only from the company's own reports and from Fed statements: debt due dates from the filings, future orders from management guidance. The discount rate is deduced backward from the stock price and the Treasury yield, and that same rule is used afterwards.
16. Order: this plan is recorded now. Reading by Claude waits until there is Anthropic credit. Work that needs no Anthropic credit continues on the track first; Databento credit may be used. The addition and subtraction pool is the last item on the track's waiting list.

## Part 2. Claude's proposal for the method (not yet confirmed by the founder)

The founder's new points collide with Claude's first proposal of 24 Nov (15:34) in five places. The first proposal is withdrawn where it collides.

| Collision | First proposal (withdrawn) | New proposal |
|---|---|---|
| Length (point 2) | join swings into trends of about 2 to 6 weeks | **No length is chosen.** For every stretch from 5 to 60 sessions compute one number: the move over the stretch divided by (the stock's usual daily move x the square root of the number of sessions). That number says how unusual the move is for its length, so a 9-session move and a 40-session move are judged on the same scale. A stretch is a trend when the number is above one cut; overlapping stretches are merged. The single cut is set by the founder marking chart pictures as "my eye sees a trend / does not", not by a number he has to name. |
| Chart first or news first (point 6) | find trends on the chart, then look for news inside them | **The pool is driven by the news clock.** An item enters the pool when it is released, with a first measure of its effect. The chart is read afterwards and labels the item (inside an uptrend, at a crest, ...). A label can come days later; the entry does not wait for it. |
| Valuing news (points 7, 8c) | every item goes through the fact base and the valuation model | **Three measures side by side, none alone.** (1) Market-measured: the stock's move minus its sector's move, from the first minute the item could be traded to the end of a short window. Works for intangibles. (2) Value-based: the change in value per share from the fact base and the valuation model, only for items that carry numbers (a price forecast, an order, a debt). (3) Linked pair: for an item that undoes an earlier one, the share of the earlier move that came back. |
| Several items on one day (point 8b) | not handled | Use the minute each item was published and minute prices (Databento) to give each item the move that followed it. Where two items cannot be separated in time, the day's move is recorded once, shared between them, and marked "not separable". |
| Weekend news (point 10) | not handled | Each item carries two times: when it was published and the first time it could be traded. A weekend item's first tradable time is Monday's open; the Monday opening move is shared between the weekend's items and marked as such. |

**What still has to be tested, not assumed** (unchanged from 24 Nov, kept because the founder's points do not remove them): (1) hindsight -- trends and levels are found with the prices known on each day only, and every level is counted, including those that broke; (2) the assumption of point 4 is checked against ordinary days: turn days must show clearly more, or bigger, news; (3) the page states a tested frequency ("levels of this kind held N times out of M while their story was intact"), not "no worries"; (4) levels that broke with no news are counted and shown.

**Three consequences of point 14 the founder should know.** (a) The addition pool reaches back to the start of our news archive, not to the start of the stock: older information is not in it. (b) For a stock that has been below its historical high for years, the subtraction pool covers years. (c) "The same information line" needs a rule for when two items are the same story; Claude proposes the linked-pair mark of the table above.

**Which stocks have a pool.** No set of 19 exists in the project. The sets are: 13 AI-chain stocks whose news the listener scores (AMD, NVDA, MU, INTC, AVGO, SNDK, ORCL, TSM, CRWD, GOOG, META, AMZN, MSFT); 20 companies whose annual reports were read into profiles (those 13 plus AAPL, CSCO, EMR, GE, IBM, QCOM, TXN); 104 stocks of the sell-off study (prices and reported figures, no news scoring). Claude proposes the 20 as the pool's stocks, to be confirmed.

**Checked on 24 Nov.** The founder's NVIDIA example is real news: public radio reports of 17 Nov 2026 say the board did not intend to reinstate Jensen Huang; an SEC 8-K of NVIDIA dated 22 Nov 2026 carries a press release dated 23 Nov, which Claude has not read. The price dates and levels of the two chart examples are NOT yet checked against prices.
