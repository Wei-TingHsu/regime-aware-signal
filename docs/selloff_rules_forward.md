# Sell-off rules SS-2a, SS-2b, SS-2c: the forward record

Registered in TRACK 3.110 (24 Nov 2026) before any case. Every sell-off of 5% or more of the list from 24 Nov 2026 is tested against the rules as frozen in `docs/selloff_rules.json`. A match is sold at the next open and closed at the rule's exit; cost: the founder's fees, 2 basis points of spread per order, 4.8% a year on the short position; account US$70,000. Each day counts once per rule. **Verdict per rule at 30 separate days.** The two bp columns are the registered measure (the stock sold short with the whole account). **'The founder's way' (decided 25 Nov 2026, TRACK 3.121) is how a match is really traded: the inverse fund bought with cash where one exists, otherwise the stock sold short with US$35,000; its result is in US dollars after cost.** The history numbers are flattered (the rules were chosen on those years); this record is the first clean evidence.

| rule | trade that passed the test | history 2018-2026, per day with a trade | days so far with a known result | average so far, the stock alone | against the S&P 500 | waiting for their sessions |
|---|---|---|---|---|---|---|
| SS-2a | sell the stock; exit +2 | +166 bp (91 days) | 0 of 30 |  |  | 3 |
| SS-2b | sell the stock; exit +2 | +102 bp (142 days) | 0 of 30 |  |  | 0 |
| SS-2c | sell the stock and buy the S&P 500 fund; exit +3 | +82 bp (194 days) | 0 of 30 |  |  | 0 |

| sell-off day | rule | stock | move that day % | sold at the open of | closed at the close of | the stock alone, bp after cost | against the S&P 500, bp after cost | the founder's way | its result, US$ |
|---|---|---|---|---|---|---|---|---|---|
| 2026-11-25 | SS-2a | ORCL | -5.1 |  |  |  |  | buy the inverse fund ORCS (1x) with US$35,000; no short sale, nothing borrowed (reduced: the account already holds US$35,000 of its US$70,000) |  |
| 2026-11-25 | SS-2a | SNDK | -5.6 |  |  |  |  | NO TRADE: a position in SNDK is still open |  |
| 2026-11-24 | SS-2a | SNDK | -11.1 |  |  |  |  | sell SNDK short with US$35,000 (it has no inverse fund) |  |

## When signals overlap: the four ways side by side (founder, 26 Nov 2026)

**A** = one position per stock; **B** = limits on the whole account; **C** = one position per stock AND limits on the whole account; **D** = no rule: every signal at full size. Limits of B and C: at most US$35,000 sold short in all, at most US$70,000 in all positions together; a signal that would get under US$5,000 is not traded. Sizes are the money in the fund or the short sale; results in US dollars after cost. **The page shows way C.**

| sell-off day | rule | stock | size A | size B | size C | size D | result A | result B | result C | result D |
|---|---|---|---|---|---|---|---|---|---|---|
| 2026-11-25 | SS-2a | ORCL | 70,000 | 35,000 | 35,000 | 70,000 |  |  |  |  |
| 2026-11-25 | SS-2a | SNDK | no trade | no trade | no trade | 35,000 |  |  |  |  |
| 2026-11-24 | SS-2a | SNDK | 35,000 | 35,000 | 35,000 | 35,000 |  |  |  |  |
