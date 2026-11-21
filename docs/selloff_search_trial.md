# Sell-off study, stage D: the machine search for patterns

Registered in TRACK 3.98 before running. Patterns are FOUND on sell-offs of 2005-2017 and CONFIRMED on 2018-2026 (not used for finding). A pattern = one, two or three conditions together, from one table or a pair of tables. FOUND: inside the pattern the outcome's frequency differs from its frequency over all sell-offs by z of 3.5 or more, on 60 or more day-equivalents (each day counts once however many securities fell). CONFIRMED: in 2018-2026 the difference has the same sign and at least half the size, on 30 or more day-equivalents. **The test:** the whole search is repeated 3 times on scrambled data (the outcomes slid along the calendar by a random amount). 'p' = the share of scrambled repeats that gave at least as many CONFIRMED patterns as the real data. A group of sell-offs counts at p < 0.0125 (0.05 / 4 groups). Only then are its patterns candidates, and only those seen in 24 or more separate months of 2005-2017 and 12 or more of 2018-2026 with a difference of 10 points or more in 2018-2026.

## stocks, one day -5% or worse

3733 sell-offs to find on, 3279 to confirm on. Searched 3 of 3 families: 339,680 pattern-outcome pairs. FOUND in 2005-2017: 434 (scrambled data, middle: 18.0). **CONFIRMED in 2018-2026: 83; scrambled data gave 0 in the middle, 0 in its top 5%, at most 0. p = 0.250 -> no more than luck gives.**

| family (tables) | items | pairs tried | found | found, scrambled | confirmed | confirmed, scrambled (middle; top 5%) | p |
|---|---|---|---|---|---|---|---|
| T1 | 41 | 32,980 | 28 | 4 | 16 | 0; 0 | 0.250 |
| T2 | 52 | 53,760 | 1 | 0 | 0 | 0; 0 | 1.000 |
| T1 + T2 | 93 | 252,940 | 405 | 13 | 67 | 0; 0 | 0.250 |

### The confirmed patterns with the largest difference in 2018-2026 (overlapping ones removed) -- shown for the record; this group did NOT beat scrambled data, so read them as luck

| when ALL of these hold | then | 2005-2017: how often (all sell-offs) | days; months; sell-offs | 2018-2026: how often (all sell-offs) | days; months; sell-offs | average price move after, 2018-2026 | candidate |
|---|---|---|---|---|---|---|---|
| distance below the one-year high %: high (over -24.6) AND machine group 3 of 5 in 'the fall and the market' (marked by high volume against normal and low size in units of its own usual move) AND move against sector fund pct: low (under -4.82) | the price is higher after 1 session | 36% (49%) | 174; 111; 231 | 42% (51%) | 168; 89; 247 | +1: -39 bp, +2: -32 bp, +3: -44 bp, +5: -45 bp, +7: -32 bp, +10: -40 bp | no |
| run-up over the 60 sessions before %: high (over 1.77) AND machine group 3 of 5 in 'the fall and the market' (marked by high volume against normal and low size in units of its own usual move) | it beats the S&P 500 over 2 sessions | 35% (49%) | 161; 103; 212 | 38% (48%) | 144; 90; 220 | +1: -62 bp, +2: -66 bp, +3: -82 bp, +5: -53 bp, +7: -73 bp, +10: -64 bp | no |
| run-up over the 60 sessions before %: high (over 1.77) AND machine group 3 of 5 in 'the fall and the market' (marked by high volume against normal and low size in units of its own usual move) AND worst peer had any filing: no | the price is higher after 2 sessions | 36% (51%) | 134; 99; 175 | 39% (49%) | 125; 89; 186 | +1: -55 bp, +2: -54 bp, +3: -65 bp, +5: -44 bp, +7: -57 bp, +10: -50 bp | no |
| distance below the one-year high %: high (over -24.6) AND machine group 3 of 5 in 'the fall and the market' (marked by high volume against normal and low size in units of its own usual move) AND fell more than every peer: yes | the price is higher after 2 sessions | 37% (51%) | 187; 114; 246 | 40% (49%) | 173; 92; 250 | +1: -45 bp, +2: -44 bp, +3: -55 bp, +5: -60 bp, +7: -50 bp, +10: -50 bp | no |
| S&P 500 against its 200-day average %: high (over -3.11) AND own results filing: yes AND move against sector fund pct: low (under -4.82) | it beats the S&P 500 over 2 sessions | 36% (49%) | 191; 103; 249 | 41% (48%) | 247; 89; 405 | +1: -28 bp, +2: -36 bp, +3: -53 bp, +5: -16 bp, +7: +17 bp, +10: +19 bp | no |
| machine group 3 of 5 in 'the fall and the market' (marked by high volume against normal and low size in units of its own usual move) AND move against sector fund pct: low (under -4.82) | the price is higher after 2 sessions | 40% (51%) | 251; 127; 357 | 42% (49%) | 255; 102; 408 | +1: -34 bp, +2: -34 bp, +3: -51 bp, +5: -27 bp, +7: -15 bp, +10: -8 bp | no |
| last day's move %: low (under -7.56) AND machine group 3 of 5 in 'the fall and the market' (marked by high volume against normal and low size in units of its own usual move) AND own filings in the last 30 days: middle (1 to 2) | it beats its sector fund over 2 sessions | 32% (49%) | 136; 99; 191 | 39% (48%) | 121; 84; 221 | +1: -46 bp, +2: -60 bp, +3: -89 bp, +5: -58 bp, +7: -77 bp, +10: -76 bp | no |
| gap at the open %: low (under -2.94) AND in ai chain: yes AND machine group 3 of 5 in 'who fell and who set it off' (marked by low share of peers down 3pct and high peers average move pct) | it beats the S&P 500 over 2 sessions | 27% (49%) | 64; 66; 91 | 36% (48%) | 61; 62; 94 | +1: -95 bp, +2: -168 bp, +3: -189 bp, +5: -77 bp, +7: -27 bp, +10: +29 bp | no |
| machine group 3 of 5 in 'the fall and the market' (marked by high volume against normal and low size in units of its own usual move) | it beats the S&P 500 over 2 sessions | 39% (49%) | 295; 134; 421 | 42% (48%) | 273; 103; 442 | +1: -34 bp, +2: -33 bp, +3: -52 bp, +5: -32 bp, +7: -19 bp, +10: -8 bp | no |

