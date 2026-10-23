# T-I turning-point rules — GLD

*2026-10-23 17:25. Window rule used on every segmentation: patience 10, min window 3, look-back 252 (the promoted cell). 'short' = share of legs under 5 sessions (noise legs). Verdict rule: another segmentation replaces the zigzag only if its median explained share is ≥ 5 points higher with at least as many scored legs.*

**PASS for persist N=5, X=4%**

| rule | legs since 2006 | median length (sessions) | share < 5 sessions | median size | legs scored | median explained share |
|---|---|---|---|---|---|---|
| zigzag 1.5× / 8% (registered) | 54 | 66 | 0% | 17.6% | 24.0 | 68% |
| persist N=2, X=0% | 896 | 5 | 49% | 2.8% | 225.0 | 48% |
| persist N=2, X=2% | 442 | 9 | 22% | 5.0% | 159.0 | 53% |
| persist N=2, X=4% | 202 | 18 | 7% | 8.2% | 80.0 | 61% |
| persist N=2, X=8% | 64 | 51 | 2% | 17.1% | 29.0 | 54% |
| persist N=3, X=0% | 352 | 11 | 16% | 5.0% | 140.0 | 61% |
| persist N=3, X=2% | 274 | 15 | 10% | 6.5% | 112.0 | 66% |
| persist N=3, X=4% | 146 | 28 | 5% | 11.2% | 63.0 | 64% |
| persist N=3, X=8% | 60 | 54 | 0% | 17.6% | 28.0 | 58% |
| persist N=5, X=0% | 63 | 52 | 0% | 13.6% | 38.0 | 68% |
| persist N=5, X=2% | 63 | 52 | 0% | 13.6% | 38.0 | 68% |
| persist N=5, X=4% | 55 | 57 | 0% | 14.6% | 34.0 | 74% |
| persist N=5, X=8% | 37 | 97 | 0% | 19.1% | 22.0 | 74% |
| persist N=10, X=0% | 0 | nan | nan% | nan% | nan | nan% |
| persist N=10, X=2% | 0 | nan | nan% | nan% | nan | nan% |
| persist N=10, X=4% | 0 | nan | nan% | nan% | nan | nan% |
| persist N=10, X=8% | 0 | nan | nan% | nan% | nan | nan% |
| swing k=5 | 554 | 8 | 24% | 4.1% | 210.0 | 53% |
| swing k=10 | 302 | 15 | 6% | 6.1% | 142.0 | 61% |
| swing k=20 | 159 | 28 | 1% | 8.5% | 83.0 | 65% |

Reading: X = 0% is the pure gradient rule — direction flips with N consecutive closes; its legs are counted in days and mostly noise. Adding a minimum counter-move X turns it into a zigzag with a persistence condition; swing k is the local-extremum family. The founder's point stands as a rule in the grid; the data says which scale is useful.
