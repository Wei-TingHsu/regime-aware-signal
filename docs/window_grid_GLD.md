# T-G window-rule grid — GLD

*2026-10-23 16:56. 216 cells: reversal rule (mult, floor) × look-back × patience × min window. Statistic: median R5 explained share over past episodes. Best cell judged against the best cell of the same sweep on 10 time-shifted factor series (SPEC_GRID rule 2).*

**Registered cell** (1.5, 8%, 504, patience 5, min 5): median 53%, beats full leg in 83% (n 24).

**Best cell:** mult 2.0, floor 12%, look-back 252, patience 10, min window 3 → median **76%**, beats full leg in 100% (n 13); best-of-sweep null median 17%, **p = 0.00** → survives the sweep

| rank | mult | floor | look-back | patience | min k | median R5 | beats full | n |
|---|---|---|---|---|---|---|---|---|

**Best cell within each leg definition** (the app uses the one for its registered rule — legs are never re-cut to fit a cell):

| leg definition | look-back | patience | min k | median R5 | beats full | n | p (sub-grid null) |
|---|---|---|---|---|---|---|---|
| 1.0× / 5% | 252 | 30 | 3 | 66% | 88% | 52 | 0.00 |
| 1.5× / 8% | 252 | 10 | 3 | 68% | 96% | 24 | 0.00 |
| 2.0× / 12% | 252 | 10 | 3 | 76% | 100% | 13 | 0.00 |

All cells, top 15:

| 1 | 2.0 | 12% | 252 | 10 | 3 | 76% | 100% | 13 |
| 2 | 2.0 | 12% | 252 | 15 | 3 | 76% | 100% | 13 |
| 3 | 2.0 | 12% | 252 | 30 | 3 | 76% | 100% | 13 |
| 4 | 2.0 | 12% | 252 | 20 | 3 | 76% | 100% | 13 |
| 5 | 2.0 | 12% | 252 | 10 | 10 | 71% | 85% | 13 |
| 6 | 2.0 | 12% | 252 | 15 | 5 | 71% | 85% | 13 |
| 7 | 2.0 | 12% | 252 | 15 | 10 | 71% | 92% | 13 |
| 8 | 2.0 | 12% | 252 | 20 | 10 | 71% | 92% | 13 |
| 9 | 2.0 | 12% | 252 | 30 | 5 | 71% | 100% | 13 |
| 10 | 2.0 | 12% | 252 | 30 | 10 | 71% | 100% | 13 |
| 11 | 2.0 | 12% | 252 | 20 | 5 | 71% | 92% | 13 |
| 12 | 2.0 | 12% | 252 | 7 | 3 | 71% | 100% | 13 |
| 13 | 2.0 | 12% | 504 | 15 | 3 | 70% | 92% | 13 |
| 14 | 2.0 | 12% | 504 | 30 | 3 | 70% | 92% | 13 |
| 15 | 2.0 | 12% | 504 | 20 | 3 | 70% | 92% | 13 |

By patience (median over the other variables): 2: 43%, 3: 50%, 5: 54%, 7: 55%, 10: 56%, 15: 60%, 20: 64%, 30: 64%
By look-back: 252: 62%, 504: 54%, 756: 51%
By reversal rule: (1.0, 5%): 57%, (1.5, 8%): 56%, (2.0, 12%): 56%

Reading: the registered 5/5 cell stays the recorded verdict; a surviving best cell is promoted (dated amendment) as the rule the app uses, with its p shown.
