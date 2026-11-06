# Factor sensitivities by era — GLD (2006-01-04 → 2026-11-05, 11 reasons; dropped ['btc'])

Joint OLS per era (no ordering: the question is whether the sensitivities moved, not how to split shared variance). `r2` is in-sample within the era.

| era | n | R² | war | hikes | real | dollar | oil | vix | cot_gold | cot_silver | cot_oil | macro1 | macro2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 5233 | 0.176 | +0.0002 | -0.0001 | -0.0000 | -1.1323 | +0.0376 | -0.0040 | -0.0012 | +0.0054 | +0.0582 | -0.0145 | +0.0281 |
| 2004-08 | 754 | 0.324 | -0.0009 | -0.0002 | +0.0007 | -1.5123 | +0.1913 | -0.0334 | -0.0182 | -0.0194 | +0.2883 | -0.0421 | +0.0189 |
| 2009-14 | 1503 | 0.183 | -0.0002 | +0.0002 | +0.0000 | -0.7298 | +0.1047 | -0.0213 | -0.0496 | +0.0499 | +0.0268 | -0.0820 | +0.0312 |
| 2015-19 | 1256 | 0.327 | +0.0000 | -0.0002 | +0.0004 | -0.8858 | +0.0087 | -0.0059 | +0.0131 | -0.0068 | +0.0139 | -0.0746 | +0.0634 |
| 2020-21 | 505 | 0.253 | +0.0006 | +0.0001 | -0.0006 | -1.1665 | -0.0037 | +0.0089 | +0.0123 | +0.0062 | -0.1342 | +0.0268 | +0.0456 |
| 2022-26 | 1215 | 0.213 | +0.0020 | -0.0001 | -0.0002 | -0.8647 | +0.0399 | -0.0260 | +0.0251 | +0.0022 | +0.0472 | -0.0425 | -0.0208 |

Sign agreement with the pooled beta (✓ same sign):

| era | war | hikes | real | dollar | oil | vix | cot_gold | cot_silver | cot_oil | macro1 | macro2 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| all | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2004-08 | ✗ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| 2009-14 | ✗ | ✗ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2015-19 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ |
| 2020-21 | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ | ✓ |
| 2022-26 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✗ |

## T-A by era × window (median out-of-sample R², blocks of 20 sessions)

Best `{'W': 504, 'era': '2015-19'}` = 0.339; best-of-sweep null (factors time-shifted together) q95 -0.020; p_family 0.000. Surface in `era_factors_GLD_full_sweep.md`.

## The current episode re-attributed: 2026-01-29 → 2026-11-05, move -31.4% (log)

| betas from | window | explained (log %) | explained share | largest contributions |
|---|---|---|---|---|
| pre-episode 504 | 2024-01-25 → 2026-01-28 | -1.12 | +0.04 | oil +5.38, dollar -5.31, macro1 -4.88 |
| 2009-21 | 2009-01-02 → 2021-12-31 | -9.16 | +0.29 | dollar -3.33, macro1 -3.10, real -1.64 |
| 2022-start | 2022-01-03 → 2026-01-28 | -4.20 | +0.13 | macro1 -4.21, oil +3.70, dollar -2.58 |
| all | 2006-01-04 → 2026-11-05 | -6.21 | +0.20 | dollar -4.00, oil +1.62, macro1 -1.57 |

If the 2022→ betas explain much more of the episode than the 2009–21 betas, the sensitivities changed (a habit); if neither explains it, the move sits outside the named reasons in every era (T-A's reading of 23 Oct).
