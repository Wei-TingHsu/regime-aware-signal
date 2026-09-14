# Report scoreboard — acceptance tests (prereg §12)

*Run 2026-09-14 13:00 +0800. Synthetic ledgers only; no real report used. Fast settings: 300 permutation draws per test, 200 replications for T2.*

| test | result | detail |
|---|---|---|
| T1 planted-perfect | PASS | hit 1.000, no_misses=True, p 0.0000 (300 draws) |
| T2 planted-shuffled | PASS | rejection rate 0.040 over 200 reps (300 draws each) |
| T3 min-count | PASS | 29 -> too few to report (29 non-overlap rows; minimum 30); 30 -> n=30, hit printed |
| T4 non-overlap sampler | PASS | selected 7 rows; positions [1, 4, 7, 10, 13, 16, 19] |
| T5 exclusions | PASS | coverage {'call': 36, 'abstain': 1, 'divergence': 1, 'zero_direction': 1, 'no_document': 1}; naive rows 36 of 40; zero-return row scored as miss |
| T6 two entries | PASS | rp-rt = 0.010338089, expected 0.010338089 |
| T7 block null does something | PASS | null sd block=0.0199 vs free=0.0147 |

**ALL SEVEN PASS**
