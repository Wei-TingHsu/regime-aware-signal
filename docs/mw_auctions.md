# Test MW-1, first kind: Treasury auction results

Registered in TRACK 3.125 and 3.143 before running. 790 auction closings of Treasury notes and bonds since 2018-05-01 (the US Treasury's own list). For each: the size of the move (up or down) of each future over the H minutes from the auction's closing minute, against the size of its move over the same clock minutes on the 20 sessions before that had no auction closing then. 'Times' = the average size after an auction divided by the average ordinary size. 'Place' = where the auction day stands among those sessions on average (0.5 = like any other day, 1 = always the largest). 'Chance' = how often 20,000 draws of ordinary days give a place at least as high. **PASSES** = chance under 0.0031 (0.05 / 16 tests).

| future | minutes after the close of the auction | auctions | average move after an auction, basis points | on ordinary days at that minute | times | place | chance | verdict |
|---|---|---|---|---|---|---|---|---|
| S&P 500 futures | 5 | 783 | 6.5 | 5.2 | 1.25 | 0.535 | 0.0009 | **PASSES** |
| S&P 500 futures | 15 | 783 | 9.8 | 8.7 | 1.12 | 0.515 | 0.0753 | no |
| S&P 500 futures | 30 | 783 | 14.6 | 12.1 | 1.21 | 0.544 | 0.0001 | **PASSES** |
| S&P 500 futures | 60 | 783 | 19.9 | 17.6 | 1.13 | 0.507 | 0.2682 | no |
| Nasdaq-100 futures | 5 | 783 | 8.5 | 6.7 | 1.27 | 0.534 | 0.0011 | **PASSES** |
| Nasdaq-100 futures | 15 | 783 | 12.8 | 11.4 | 1.13 | 0.509 | 0.1952 | no |
| Nasdaq-100 futures | 30 | 783 | 18.9 | 15.9 | 1.19 | 0.532 | 0.0013 | **PASSES** |
| Nasdaq-100 futures | 60 | 783 | 26.1 | 22.6 | 1.16 | 0.525 | 0.0119 | no |
| gold futures | 5 | 782 | 4.9 | 4.0 | 1.23 | 0.567 | 0.0000 | **PASSES** |
| gold futures | 15 | 781 | 7.2 | 6.5 | 1.11 | 0.547 | 0.0000 | **PASSES** |
| gold futures | 30 | 780 | 10.6 | 9.4 | 1.13 | 0.532 | 0.0014 | **PASSES** |
| gold futures | 60 | 779 | 13.6 | 12.6 | 1.09 | 0.519 | 0.0369 | no |
| 10-year Treasury note futures | 5 | 783 | 4.1 | 1.5 | 2.79 | 0.746 | 0.0000 | **PASSES** |
| 10-year Treasury note futures | 15 | 783 | 4.8 | 2.3 | 2.06 | 0.697 | 0.0000 | **PASSES** |
| 10-year Treasury note futures | 30 | 782 | 5.5 | 3.1 | 1.78 | 0.664 | 0.0000 | **PASSES** |
| 10-year Treasury note futures | 60 | 782 | 6.4 | 4.5 | 1.41 | 0.605 | 0.0000 | **PASSES** |

What a pass means and does not mean: an auction result moves that market more than an ordinary minute does -- it says the kind of headline matters, not which way the market goes. Direction needs the result compared with what the market expected (the yield traded just before the auction), which is not in this list.
Sources: US Treasury (auction list, public); Databento GLBX.MDP3 1-minute futures prices (licensed, not uploaded).
