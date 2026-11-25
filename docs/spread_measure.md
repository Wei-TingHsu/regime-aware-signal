# The real spread at the times the sell-off rules trade

Registered in TRACK 3.112. Nasdaq's best bid and ask (Databento, XNAS.ITCH) for each stock and its inverse fund on the entry and exit sessions of 134 sessions since Aug 2022. **Cost of one order = half the gap between ask and bid, in basis points of the price.** Nasdaq's own book only: the best price across all exchanges is equal or better, so these numbers are an upper limit. The tests so far ASSUMED 2 basis points per order for shares and 10 for funds.

| what is traded | moment | middle value, bp per order | average | 9 in 10 are under | measured | no valid quote |
|---|---|---|---|---|---|---|
| stock | entry, 1 minute after the open | 2.1 | 2.6 | 4.6 | 92 | 0 |
| stock | entry, 5 minutes after the open | 1.4 | 1.7 | 3.1 | 92 | 0 |
| stock | exit, 5 minutes before the close | 0.7 | 0.8 | 1.4 | 92 | 0 |
| stock | exit, 1 minute before the close | 0.5 | 0.6 | 1.0 | 92 | 0 |
| 1x fund | entry, 1 minute after the open | 5.6 | 7.2 | 11.8 | 79 | 0 |
| 1x fund | entry, 5 minutes after the open | 5.1 | 6.4 | 11.8 | 79 | 0 |
| 1x fund | exit, 5 minutes before the close | 4.4 | 6.0 | 12.0 | 79 | 0 |
| 1x fund | exit, 1 minute before the close | 3.5 | 4.2 | 6.8 | 79 | 0 |
| 2x fund | entry, 1 minute after the open | 13.3 | 18.0 | 27.2 | 85 | 0 |
| 2x fund | entry, 5 minutes after the open | 11.9 | 17.5 | 25.5 | 85 | 0 |
| 2x fund | exit, 5 minutes before the close | 8.7 | 11.6 | 23.1 | 83 | 0 |
| 2x fund | exit, 1 minute before the close | 7.0 | 10.4 | 22.8 | 83 | 0 |

## The cheapest way for the same exposure, with the measured spreads

Entry one minute after the open, exit one minute before the close two sessions later; middle values. Fees about 1 basis point (1.5 for the cheaper-priced 1x funds); a short sale also carries about 2.6 basis points for two nights (the 4.8% a year stand-in). A 2x fund needs half the money, so its spread counts half.

| way | spread, in and out | total cost, bp of the exposure | with the assumed spreads it was |
|---|---|---|---|
| sell the stock short | 2.6 | 6.2 | 13.1 |
| buy the 1x inverse fund | 9.1 | 10.6 | 28.2 |
| buy the 2x inverse fund with half the money | 10.2 | 11.2 | 18.7 |

By fund (middle value at the entry, 1 minute after the open; number measured): AAPD 13 (1), AMZD 6 (7), AVS 16 (1), GGLS 5 (5), METD 11 (2), MSFD 7 (4), MUD 17 (2), NVD 19 (14), NVDD 7 (13), NVDQ 13 (13), NVDS 7 (25), PLTD 12 (1), TSDD 18 (17), TSLS 5 (42), TSLZ 13 (16), TSMZ 12 (1).
