# T-I turning-point rules — GLD

*2026-10-23 18:14. Window rule used on every segmentation: patience 10, min window 3, look-back 252 (the promoted cell). 'short' = share of legs under 5 sessions (noise legs); 'missed' = legs hiding a counter-move above the zigzag threshold (a reversal the rule did not see — fidelity, added 23 Oct after the consecutive-closes rule missed gold's August peak). Verdict rule: another segmentation replaces the zigzag only if its median explained share is ≥ 5 points higher, with at least as many scored legs, and no more missed reversals.*

**PASS for retrace f=38%, N=3, c=1.0, retrace f=38%, N=5, c=1.0**

**T-J fine scale: PASS — retrace f=38%, N=3, c=0.5** (0 missed, lag 6 sessions, 215 legs, explained 70%); promoted as the fine scale inside the zigzag's legs.

| rule | legs since 2006 | median length | share < 5 sessions | median size | legs scored | median explained share | missed reversals (worst) | confirmation lag (sessions) |
|---|---|---|---|---|---|---|---|---|
| zigzag 1.5× / 8% (registered) | 54 | 66 | 0% | 17.6% | 24 | 68% | 3 (23%) | nan |
| persist-time N=2, X=2% | 496 | 8 | 27% | 4.7% | 171 | 52% | 0 (4%) | nan |
| persist-time N=2, X=4% | 220 | 17 | 10% | 8.1% | 87 | 61% | 0 (4%) | nan |
| persist-time N=2, X=8% | 70 | 45 | 3% | 16.4% | 29 | 54% | 0 (8%) | nan |
| persist-time N=3, X=2% | 448 | 9 | 22% | 5.0% | 165 | 53% | 0 (7%) | nan |
| persist-time N=3, X=4% | 220 | 17 | 10% | 8.0% | 87 | 61% | 0 (6%) | nan |
| persist-time N=3, X=8% | 70 | 45 | 1% | 16.4% | 30 | 58% | 0 (8%) | nan |
| persist-time N=5, X=2% | 346 | 12 | 0% | 5.8% | 164 | 60% | 0 (9%) | nan |
| persist-time N=5, X=4% | 196 | 19 | 0% | 8.5% | 84 | 61% | 0 (9%) | nan |
| persist-time N=5, X=8% | 68 | 47 | 0% | 16.6% | 30 | 58% | 0 (8%) | nan |
| persist-time N=10, X=2% | 236 | 18 | 0% | 7.2% | 104 | 65% | 0 (9%) | nan |
| persist-time N=10, X=4% | 162 | 24 | 0% | 9.8% | 70 | 63% | 0 (9%) | nan |
| persist-time N=10, X=8% | 60 | 56 | 0% | 18.0% | 26 | 54% | 2 (15%) | nan |
| persist-closes N=2, X=0% | 896 | 5 | 49% | 2.8% | 225 | 48% | 0 (8%) | nan |
| persist-closes N=2, X=2% | 442 | 9 | 22% | 5.0% | 159 | 53% | 0 (8%) | nan |
| persist-closes N=2, X=4% | 202 | 18 | 7% | 8.2% | 80 | 61% | 0 (8%) | nan |
| persist-closes N=2, X=8% | 64 | 51 | 2% | 17.1% | 29 | 54% | 0 (8%) | nan |
| persist-closes N=3, X=0% | 352 | 11 | 16% | 5.0% | 140 | 61% | 1 (15%) | nan |
| persist-closes N=3, X=2% | 274 | 15 | 10% | 6.5% | 112 | 66% | 1 (15%) | nan |
| persist-closes N=3, X=4% | 146 | 28 | 5% | 11.2% | 63 | 64% | 1 (15%) | nan |
| persist-closes N=3, X=8% | 60 | 54 | 0% | 17.6% | 28 | 58% | 1 (15%) | nan |
| persist-closes N=5, X=0% | 63 | 52 | 0% | 13.6% | 38 | 68% | 5 (40%) | nan |
| persist-closes N=5, X=2% | 63 | 52 | 0% | 13.6% | 38 | 68% | 5 (40%) | nan |
| persist-closes N=5, X=4% | 55 | 57 | 0% | 14.6% | 34 | 74% | 6 (40%) | nan |
| persist-closes N=5, X=8% | 37 | 97 | 0% | 19.1% | 22 | 74% | 6 (40%) | nan |
| swing k=5 | 554 | 8 | 24% | 4.1% | 210 | 53% | 0 (4%) | nan |
| swing k=10 | 302 | 15 | 6% | 6.1% | 142 | 61% | 1 (15%) | nan |
| swing k=20 | 159 | 28 | 1% | 8.5% | 83 | 65% | 1 (15%) | nan |
| retrace f=25%, N=3, c=0.5 | 376 | 11 | 16% | 5.4% | 155 | 54% | 0 (7%) | 4 |
| retrace f=25%, N=3, c=1.0 | 160 | 28 | 2% | 8.7% | 79 | 64% | 1 (15%) | 10 |
| retrace f=25%, N=5, c=0.5 | 310 | 14 | 0% | 6.0% | 148 | 61% | 0 (8%) | 5 |
| retrace f=25%, N=5, c=1.0 | 148 | 28 | 0% | 9.2% | 70 | 66% | 2 (15%) | 11 |
| retrace f=38%, N=3, c=0.5 | 215 | 13 | 10% | 6.3% | 64 | 70% | 0 (7%) | 6 |
| retrace f=38%, N=3, c=1.0 | 109 | 29 | 1% | 9.3% | 40 | 74% | 1 (15%) | 12 |
| retrace f=38%, N=5, c=0.5 | 193 | 16 | 0% | 6.6% | 65 | 70% | 0 (8%) | 7 |
| retrace f=38%, N=5, c=1.0 | 107 | 29 | 0% | 9.7% | 39 | 76% | 1 (15%) | 12 |
| retrace f=50%, N=3, c=0.5 | 9 | 20 | 0% | 5.1% | 0 | nan% | 0 (2%) | 6 |
| retrace f=50%, N=3, c=1.0 | 9 | 20 | 0% | 5.1% | 0 | nan% | 0 (2%) | 7 |
| retrace f=50%, N=5, c=0.5 | 9 | 20 | 0% | 5.1% | 0 | nan% | 0 (2%) | 6 |
| retrace f=50%, N=5, c=1.0 | 9 | 20 | 0% | 5.1% | 0 | nan% | 0 (2%) | 7 |

Reading: X = 0% is the pure gradient rule — direction flips with N consecutive closes; its legs are counted in days and mostly noise. Adding a minimum counter-move X turns it into a zigzag with a persistence condition; swing k is the local-extremum family. The founder's point stands as a rule in the grid; the data says which scale is useful.
