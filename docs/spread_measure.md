# The real spread at the times the sell-off rules trade

Registered in TRACK 3.112. Nasdaq's best bid and ask (Databento, XNAS.ITCH) for each stock and its inverse fund on the entry and exit sessions of 351 sessions since Aug 2022. **Cost of one order = half the gap between ask and bid, in basis points of the price.** Nasdaq's own book only: the best price across all exchanges is equal or better, so these numbers are an upper limit. The tests so far ASSUMED 2 basis points per order for shares and 10 for funds.

| what is traded | moment | middle value, bp per order | average | 9 in 10 are under | measured | no valid quote |
|---|---|---|---|---|---|---|
| stock | entry, 1 minute after the open | 3.6 | 4.9 | 9.9 | 343 | 0 |
| stock | entry, 5 minutes after the open | 2.4 | 3.2 | 6.3 | 343 | 0 |
| stock | exit, 5 minutes before the close | 1.1 | 1.4 | 2.8 | 343 | 0 |
| stock | exit, 1 minute before the close | 0.6 | 0.7 | 1.4 | 343 | 0 |
| 1x fund | entry, 1 minute after the open | 7.8 | 12.9 | 24.7 | 329 | 0 |
| 1x fund | entry, 5 minutes after the open | 7.0 | 10.4 | 22.6 | 329 | 0 |
| 1x fund | exit, 5 minutes before the close | 6.5 | 11.2 | 21.8 | 333 | 0 |
| 1x fund | exit, 1 minute before the close | 5.2 | 6.9 | 12.1 | 333 | 0 |
| 2x fund | entry, 1 minute after the open | 11.4 | 14.7 | 23.7 | 172 | 0 |
| 2x fund | entry, 5 minutes after the open | 10.2 | 14.4 | 24.6 | 172 | 0 |
| 2x fund | exit, 5 minutes before the close | 8.2 | 11.1 | 21.6 | 172 | 0 |
| 2x fund | exit, 1 minute before the close | 6.6 | 9.6 | 21.4 | 172 | 0 |

## The cheapest way for the same exposure, with the measured spreads

Entry one minute after the open, exit one minute before the close two sessions later; middle values. Fees about 1 basis point (1.5 for the cheaper-priced 1x funds); a short sale also carries about 2.6 basis points for two nights (the 4.8% a year stand-in). A 2x fund needs half the money, so its spread counts half.

| way | spread, in and out | total cost, bp of the exposure | with the assumed spreads it was |
|---|---|---|---|
| sell the stock short | 4.2 | 7.8 | 13.1 |
| buy the 1x inverse fund | 13.0 | 14.5 | 28.2 |
| buy the 2x inverse fund with half the money | 9.0 | 10.0 | 18.7 |

By fund (middle value at the entry, 1 minute after the open; number measured): AAPD 5 (5), AMDD 10 (32), AMZD 6 (11), AVS 7 (21), CSCS 41 (4), GGLS 6 (10), METD 11 (13), MSFD 8 (6), MUD 8 (40), NFXS 14 (9), NVD 15 (25), NVDD 7 (25), NVDQ 13 (25), NVDS 7 (37), ORCS 34 (23), PLTD 7 (36), QCMD 49 (15), TSDD 12 (43), TSLS 5 (68), TSLZ 12 (42), TSMZ 13 (11).
