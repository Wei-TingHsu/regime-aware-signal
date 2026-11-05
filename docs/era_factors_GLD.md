# Factor sensitivities by era — GLD (2014-09-18 → 2026-10-30, 12 reasons)

Joint OLS per era (no ordering: the question is whether the sensitivities moved, not how to split shared variance). `r2` is in-sample within the era.

| era | n | R² | war | hikes | real | dollar | oil | vix | btc | cot_gold | cot_silver | cot_oil | macro1 | macro2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | 3046 | 0.213 | +0.0008 | -0.0001 | -0.0002 | -0.9528 | +0.0083 | -0.0028 | +0.0152 | +0.0087 | +0.0026 | +0.0119 | -0.0255 | +0.0223 |
| 2015-19 | 1256 | 0.329 | +0.0000 | -0.0002 | +0.0004 | -0.8873 | +0.0090 | -0.0057 | +0.0080 | +0.0129 | -0.0074 | +0.0133 | -0.0748 | +0.0638 |
| 2020-21 | 505 | 0.255 | +0.0007 | +0.0001 | -0.0006 | -1.1078 | -0.0040 | +0.0093 | +0.0126 | +0.0126 | +0.0061 | -0.1286 | +0.0237 | +0.0427 |
| 2022-26 | 1212 | 0.217 | +0.0021 | -0.0001 | -0.0001 | -0.8504 | +0.0423 | -0.0228 | +0.0227 | +0.0234 | +0.0039 | +0.0492 | -0.0426 | -0.0188 |

Sign agreement with the pooled beta (✓ same sign):

| era | war | hikes | real | dollar | oil | vix | btc | cot_gold | cot_silver | cot_oil | macro1 | macro2 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2015-19 | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ | ✓ | ✓ | ✓ |
| 2020-21 | ✓ | ✗ | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | ✓ | ✗ | ✗ | ✓ |
| 2022-26 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✗ |

## T-A by era × window (median out-of-sample R², blocks of 20 sessions)

Best `{'W': 1008, 'era': '2015-19'}` = 0.437; best-of-sweep null (factors time-shifted together) q95 -0.007; p_family 0.000. Surface in `era_factors_GLD_sweep.md`.

## The current episode re-attributed: 2026-01-29 → 2026-10-30, move -33.2% (log)

| betas from | window | explained (log %) | explained share | largest contributions |
|---|---|---|---|---|
| pre-episode 504 | 2024-01-25 → 2026-01-28 | -0.67 | +0.02 | oil +5.86, dollar -5.29, macro1 -5.01 |
| 2009-21 | 2014-09-18 → 2021-12-31 | -9.63 | +0.29 | dollar -3.64, macro1 -2.45, hikes -1.44 |
| 2022-start | 2022-01-03 → 2026-01-28 | -3.67 | +0.11 | macro1 -4.14, oil +4.02, dollar -2.57 |
| all | 2014-09-18 → 2026-10-30 | -8.24 | +0.25 | dollar -3.37, macro1 -2.73, real -1.22 |

If the 2022→ betas explain much more of the episode than the 2009–21 betas, the sensitivities changed (a habit); if neither explains it, the move sits outside the named reasons in every era (T-A's reading of 23 Oct).
