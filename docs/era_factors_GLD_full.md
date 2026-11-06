# Factor sensitivities by era — GLD (2004-11-19 → 2026-11-05, 8 reasons; dropped ['btc', 'dollar', 'macro1', 'macro2'])

Joint OLS per era (no ordering: the question is whether the sensitivities moved, not how to split shared variance). `r2` is in-sample within the era.

| era | n | R² | war | hikes | real | oil | vix | cot_gold | cot_silver | cot_oil |
|---|---|---|---|---|---|---|---|---|---|---|
| all | 5515 | 0.093 | +0.0002 | -0.0001 | -0.0005 | +0.0537 | -0.0105 | -0.0066 | +0.0081 | +0.0377 |
| 2004-08 | 1036 | 0.177 | -0.0002 | -0.0002 | -0.0000 | +0.2020 | -0.0190 | -0.0293 | +0.0163 | +0.1889 |
| 2009-14 | 1503 | 0.137 | -0.0004 | -0.0002 | -0.0006 | +0.1418 | -0.0098 | -0.0532 | +0.0543 | +0.0259 |
| 2015-19 | 1256 | 0.200 | -0.0000 | -0.0002 | -0.0008 | +0.0179 | +0.0057 | +0.0098 | -0.0072 | -0.0010 |
| 2020-21 | 505 | 0.183 | +0.0006 | -0.0000 | -0.0009 | +0.0013 | -0.0128 | +0.0255 | +0.0023 | -0.1472 |
| 2022-26 | 1215 | 0.122 | +0.0022 | -0.0002 | -0.0004 | +0.0359 | -0.0208 | +0.0178 | -0.0021 | -0.0018 |

Sign agreement with the pooled beta (✓ same sign):

| era | war | hikes | real | oil | vix | cot_gold | cot_silver | cot_oil |
|---|---|---|---|---|---|---|---|---|
| all | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2004-08 | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2009-14 | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2015-19 | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ |
| 2020-21 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| 2022-26 | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✗ | ✗ |

## T-A by era × window (median out-of-sample R², blocks of 20 sessions)

Best `{'W': 504, 'era': '2015-19'}` = 0.183; best-of-sweep null (factors time-shifted together) q95 -0.014; p_family 0.000. Surface in `era_factors_GLD_full_sweep.md`.

## The current episode re-attributed: 2026-01-29 → 2026-11-05, move -31.4% (log)

| betas from | window | explained (log %) | explained share | largest contributions |
|---|---|---|---|---|
| pre-episode 504 | 2024-01-25 → 2026-01-28 | +1.33 | -0.04 | oil +4.68, hikes -1.86, real -1.50 |
| 2009-21 | 2009-01-02 → 2021-12-31 | -5.18 | +0.16 | real -5.04, hikes -1.38, oil +1.37 |
| 2022-start | 2022-01-03 → 2026-01-28 | -0.86 | +0.03 | oil +3.83, real -3.29, hikes -1.35 |
| all | 2004-11-19 → 2026-11-05 | -2.71 | +0.09 | real -3.72, oil +2.31, hikes -1.14 |

If the 2022→ betas explain much more of the episode than the 2009–21 betas, the sensitivities changed (a habit); if neither explains it, the move sits outside the named reasons in every era (T-A's reading of 23 Oct).
