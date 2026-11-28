# Test MW-2: can a Treasury auction result be traded, and what does a late source cost?

Fixed in TRACK 3.146 before running. 790 auction closings of notes and bonds since 2018-05-01. All results are averages per trade in basis points (1 bp = 0.01%), BEFORE cost. A minus sign means the opposite trade would have won. 'Entry' = minutes after the auction closed at which the trade starts: a late source can only use the later entries. 'Ordinary' = what the same trade gives on days without an auction (signal A) or with the demand signs shuffled (signal B). 'Chance' is for that one cell alone; the verdict is for the whole grid of a signal (5,000 draws).
Cost, as an assumption: one price step is roughly 0.4 bp for S&P 500 futures, 0.2 bp for Nasdaq-100 futures, 0.3 bp for gold futures, 1.4 bp for 10-year Treasury note futures. A trade pays about one step in and one out, so an average smaller than two steps is not tradable.

## Signal A, the first move (go the way the 10-year note future went in the first 5 minutes)

**Whole grid (240 cells): the strongest cell would be matched by luck in 10.3% of draws -> not more than luck.**

### S&P 500 futures, all auctions: average bp by entry minute (down) and holding time (across)

| entry, minutes after the close | 15 minutes | 30 minutes | 60 minutes | until 15:59 |
|---|---|---|---|---|
| 5 | +1.0 (chance 0.632) | +2.2 (chance 0.144) | +3.1 (chance 0.083) | +5.5 (chance 0.062) |
| 10 | +1.0 (chance 0.703) | +2.4 (chance 0.169) | +2.7 (chance 0.135) | +5.4 (chance 0.083) |
| 15 | +0.7 (chance 0.738) | +2.4 (chance 0.086) | +2.2 (chance 0.129) | +5.0 (chance 0.103) |
| 30 | +1.7 (chance 0.003) | +2.3 (chance 0.005) | +1.8 (chance 0.052) | +4.3 (chance 0.078) |
| 60 | -0.8 (chance 0.782) | -0.5 (chance 0.827) | +0.0 (chance 0.307) | +2.1 (chance 0.391) |

### Nasdaq-100 futures, all auctions: average bp by entry minute (down) and holding time (across)

| entry, minutes after the close | 15 minutes | 30 minutes | 60 minutes | until 15:59 |
|---|---|---|---|---|
| 5 | +0.9 (chance 0.711) | +2.6 (chance 0.318) | +3.7 (chance 0.131) | +5.8 (chance 0.087) |
| 10 | +0.9 (chance 0.376) | +2.7 (chance 0.304) | +3.0 (chance 0.199) | +5.5 (chance 0.111) |
| 15 | +0.6 (chance 0.384) | +2.5 (chance 0.165) | +2.4 (chance 0.189) | +5.1 (chance 0.134) |
| 30 | +1.9 (chance 0.002) | +2.6 (chance 0.008) | +2.1 (chance 0.038) | +4.4 (chance 0.073) |
| 60 | -0.8 (chance 0.895) | -0.5 (chance 0.716) | -0.2 (chance 0.390) | +1.8 (chance 0.401) |

### gold futures, all auctions: average bp by entry minute (down) and holding time (across)

| entry, minutes after the close | 15 minutes | 30 minutes | 60 minutes | until 15:59 |
|---|---|---|---|---|
| 5 | -0.4 (chance 0.064) | -0.2 (chance 0.186) | +0.3 (chance 0.635) | +0.2 (chance 0.518) |
| 10 | -0.2 (chance 0.003) | +0.1 (chance 0.497) | +0.5 (chance 0.503) | +0.1 (chance 0.753) |
| 15 | -0.2 (chance 0.042) | +0.2 (chance 0.753) | +0.9 (chance 0.697) | +0.2 (chance 0.535) |
| 30 | +0.3 (chance 0.120) | +0.2 (chance 0.479) | +0.6 (chance 0.276) | +0.4 (chance 0.177) |
| 60 | +0.9 (chance 0.115) | +0.5 (chance 0.372) | +0.4 (chance 0.296) | +0.3 (chance 0.226) |

### 10-year Treasury note futures, all auctions: average bp by entry minute (down) and holding time (across)

| entry, minutes after the close | 15 minutes | 30 minutes | 60 minutes | until 15:59 |
|---|---|---|---|---|
| 5 | -0.1 (chance 0.220) | -0.2 (chance 0.678) | -0.3 (chance 0.758) | -0.5 (chance 0.459) |
| 10 | -0.0 (chance 0.944) | -0.2 (chance 0.436) | -0.3 (chance 0.389) | -0.5 (chance 0.787) |
| 15 | +0.0 (chance 0.770) | -0.2 (chance 0.600) | -0.3 (chance 0.375) | -0.4 (chance 0.668) |
| 30 | -0.2 (chance 0.323) | -0.1 (chance 0.413) | -0.4 (chance 0.270) | -0.4 (chance 0.709) |
| 60 | -0.2 (chance 0.461) | -0.2 (chance 0.482) | +0.0 (chance 0.475) | -0.3 (chance 0.376) |

### The 15 strongest cells of this signal (any future, any situation)

| future | situation | entry | hold | auctions | average bp | ordinary bp | right, % | chance (this cell alone) |
|---|---|---|---|---|---|---|---|---|
| S&P 500 futures | long terms (10 to 30 years) | 30 | 15 minutes | 315 | +2.6 | -0.1 | 56% | 0.0012 |
| Nasdaq-100 futures | long terms (10 to 30 years) | 30 | 15 minutes | 315 | +2.9 | -0.4 | 57% | 0.0014 |
| S&P 500 futures | long terms (10 to 30 years) | 5 | 60 minutes | 315 | +6.7 | +0.9 | 57% | 0.0022 |
| Nasdaq-100 futures | all auctions | 30 | 15 minutes | 683 | +1.9 | -0.2 | 53% | 0.0024 |
| S&P 500 futures | long terms (10 to 30 years) | 30 | 30 minutes | 315 | +3.5 | -0.2 | 56% | 0.0028 |
| S&P 500 futures | long terms (10 to 30 years) | 5 | 30 minutes | 315 | +4.8 | +1.2 | 56% | 0.0038 |
| S&P 500 futures | all auctions | 30 | 15 minutes | 683 | +1.7 | +0.0 | 53% | 0.0034 |
| gold futures | all auctions | 10 | 15 minutes | 683 | -0.2 | +1.0 | 49% | 0.0032 |
| S&P 500 futures | long terms (10 to 30 years) | 15 | 30 minutes | 315 | +4.5 | +1.0 | 58% | 0.0044 |
| S&P 500 futures | all auctions | 30 | 30 minutes | 683 | +2.3 | -0.0 | 53% | 0.0054 |
| S&P 500 futures | long terms (10 to 30 years) | 10 | 60 minutes | 315 | +6.0 | +0.8 | 56% | 0.0064 |
| S&P 500 futures | long terms (10 to 30 years) | 30 | 60 minutes | 315 | +4.1 | -1.0 | 56% | 0.0056 |
| Nasdaq-100 futures | long terms (10 to 30 years) | 30 | 30 minutes | 315 | +3.8 | -0.5 | 53% | 0.0066 |
| Nasdaq-100 futures | all auctions | 30 | 30 minutes | 683 | +2.6 | -0.2 | 53% | 0.0078 |
| Nasdaq-100 futures | long terms (10 to 30 years) | 30 | 60 minutes | 315 | +4.4 | -1.5 | 53% | 0.0092 |

## Signal B, demand (buy when bid-to-cover is above the average of the last six auctions of that term, sell when below)

**Whole grid (336 cells): the strongest cell would be matched by luck in 0.0% of draws -> MORE THAN LUCK.**

### S&P 500 futures, all auctions: average bp by entry minute (down) and holding time (across)

| entry, minutes after the close | 15 minutes | 30 minutes | 60 minutes | until 15:59 |
|---|---|---|---|---|
| 1 | +1.4 (chance 0.010) | +2.0 (chance 0.053) | +3.7 (chance 0.008) | +3.3 (chance 0.210) |
| 3 | +1.1 (chance 0.090) | +1.9 (chance 0.071) | +3.1 (chance 0.025) | +3.0 (chance 0.264) |
| 5 | +1.0 (chance 0.209) | +2.3 (chance 0.038) | +2.7 (chance 0.046) | +2.7 (chance 0.312) |
| 10 | +1.0 (chance 0.328) | +2.6 (chance 0.010) | +3.0 (chance 0.029) | +2.4 (chance 0.365) |
| 15 | +0.4 (chance 0.664) | +2.0 (chance 0.059) | +2.4 (chance 0.077) | +1.9 (chance 0.461) |
| 30 | +1.6 (chance 0.006) | +1.7 (chance 0.030) | +1.9 (chance 0.079) | +1.5 (chance 0.525) |
| 60 | +0.3 (chance 0.600) | +0.2 (chance 0.765) | -0.1 (chance 0.921) | -0.2 (chance 0.869) |

### Nasdaq-100 futures, all auctions: average bp by entry minute (down) and holding time (across)

| entry, minutes after the close | 15 minutes | 30 minutes | 60 minutes | until 15:59 |
|---|---|---|---|---|
| 1 | +1.6 (chance 0.019) | +2.2 (chance 0.078) | +4.6 (chance 0.007) | +4.2 (chance 0.167) |
| 3 | +1.2 (chance 0.124) | +2.2 (chance 0.080) | +4.0 (chance 0.020) | +3.8 (chance 0.212) |
| 5 | +1.0 (chance 0.272) | +2.6 (chance 0.043) | +3.5 (chance 0.034) | +3.5 (chance 0.259) |
| 10 | +0.9 (chance 0.451) | +3.2 (chance 0.008) | +3.6 (chance 0.033) | +3.2 (chance 0.296) |
| 15 | +0.3 (chance 0.774) | +2.5 (chance 0.040) | +2.9 (chance 0.084) | +2.6 (chance 0.384) |
| 30 | +2.2 (chance 0.001) | +2.4 (chance 0.015) | +2.2 (chance 0.106) | +2.3 (chance 0.389) |
| 60 | +0.1 (chance 0.859) | -0.2 (chance 0.870) | -0.5 (chance 0.693) | -0.1 (chance 0.928) |

### gold futures, all auctions: average bp by entry minute (down) and holding time (across)

| entry, minutes after the close | 15 minutes | 30 minutes | 60 minutes | until 15:59 |
|---|---|---|---|---|
| 1 | +0.7 (chance 0.058) | -0.0 (chance 0.963) | -0.2 (chance 0.849) | +0.3 (chance 0.770) |
| 3 | -0.3 (chance 0.502) | -0.7 (chance 0.251) | -0.9 (chance 0.237) | -0.4 (chance 0.745) |
| 5 | -0.9 (chance 0.035) | -1.0 (chance 0.125) | -1.1 (chance 0.136) | -0.7 (chance 0.570) |
| 10 | -0.6 (chance 0.143) | -0.8 (chance 0.214) | -0.9 (chance 0.187) | -0.9 (chance 0.488) |
| 15 | -0.6 (chance 0.146) | -0.6 (chance 0.322) | -0.6 (chance 0.468) | -0.5 (chance 0.674) |
| 30 | +0.0 (chance 0.911) | -0.3 (chance 0.511) | -0.2 (chance 0.763) | +0.1 (chance 0.928) |
| 60 | +0.4 (chance 0.276) | +0.2 (chance 0.827) | +0.1 (chance 0.892) | +0.4 (chance 0.631) |

### 10-year Treasury note futures, all auctions: average bp by entry minute (down) and holding time (across)

| entry, minutes after the close | 15 minutes | 30 minutes | 60 minutes | until 15:59 |
|---|---|---|---|---|
| 1 | +1.5 (chance 0.000) | +1.3 (chance 0.000) | +1.3 (chance 0.000) | +1.7 (chance 0.000) |
| 3 | +0.1 (chance 0.359) | -0.2 (chance 0.500) | -0.2 (chance 0.590) | +0.2 (chance 0.631) |
| 5 | -0.1 (chance 0.514) | -0.3 (chance 0.131) | -0.3 (chance 0.368) | +0.0 (chance 0.923) |
| 10 | -0.2 (chance 0.162) | -0.4 (chance 0.040) | -0.4 (chance 0.131) | -0.1 (chance 0.886) |
| 15 | -0.3 (chance 0.098) | -0.3 (chance 0.110) | -0.4 (chance 0.148) | +0.1 (chance 0.854) |
| 30 | -0.1 (chance 0.716) | +0.1 (chance 0.706) | -0.1 (chance 0.669) | +0.3 (chance 0.414) |
| 60 | -0.2 (chance 0.125) | -0.2 (chance 0.312) | -0.0 (chance 0.830) | +0.3 (chance 0.449) |

### The 15 strongest cells of this signal (any future, any situation)

| future | situation | entry | hold | auctions | average bp | ordinary bp | right, % | chance (this cell alone) |
|---|---|---|---|---|---|---|---|---|
| 10-year Treasury note futures | all auctions | 1 | 15 minutes | 746 | +1.5 | -0.0 | 53% | 0.0002 |
| 10-year Treasury note futures | all auctions | 1 | 30 minutes | 745 | +1.3 | -0.0 | 54% | 0.0002 |
| 10-year Treasury note futures | short terms (2 to 7 years) | 1 | 15 minutes | 413 | +1.4 | -0.0 | 54% | 0.0002 |
| 10-year Treasury note futures | long terms (10 to 30 years) | 1 | 15 minutes | 333 | +1.7 | -0.0 | 53% | 0.0002 |
| 10-year Treasury note futures | all auctions | 1 | 60 minutes | 745 | +1.3 | -0.0 | 53% | 0.0002 |
| 10-year Treasury note futures | short terms (2 to 7 years) | 1 | 30 minutes | 412 | +1.3 | -0.0 | 53% | 0.0002 |
| 10-year Treasury note futures | all auctions | 1 | until 15:59 | 741 | +1.7 | -0.0 | 52% | 0.0002 |
| 10-year Treasury note futures | short terms (2 to 7 years) | 1 | 60 minutes | 412 | +1.2 | -0.0 | 53% | 0.0016 |
| Nasdaq-100 futures | all auctions | 30 | 15 minutes | 746 | +2.2 | +0.0 | 54% | 0.0014 |
| 10-year Treasury note futures | long terms (10 to 30 years) | 1 | 30 minutes | 333 | +1.3 | -0.0 | 56% | 0.0038 |
| Nasdaq-100 futures | short terms (2 to 7 years) | 30 | 15 minutes | 413 | +2.4 | -0.0 | 53% | 0.0052 |
| 10-year Treasury note futures | long terms (10 to 30 years) | 1 | 60 minutes | 333 | +1.4 | -0.0 | 54% | 0.0064 |
| S&P 500 futures | all auctions | 30 | 15 minutes | 746 | +1.6 | +0.0 | 51% | 0.0058 |
| gold futures | short terms (2 to 7 years) | 5 | 15 minutes | 411 | -1.4 | -0.0 | 48% | 0.0064 |
| Nasdaq-100 futures | all auctions | 1 | 60 minutes | 746 | +4.6 | +0.0 | 51% | 0.0070 |

What this cannot say: the true surprise of an auction is its yield against the yield traded just before it closed, which is not in the public list; signal A uses the market's own first move instead, and signal B uses bid-to-cover. Prices are 1-minute closes of the most-traded contract; a real order pays the step assumed above and can slip in the first minute. Every cell is in `docs/mw_direction.csv`.
Sources: US Treasury, Fiscal Data (auction list, public); Databento GLBX.MDP3 1-minute futures prices (licensed, not uploaded).
