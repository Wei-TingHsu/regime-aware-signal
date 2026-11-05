# T-L6 — the liquidity–gold link by era and by break (2004-11-24 → 2026-10-28, 1145 weeks)

Weekly GLD log return on weekly Δlog net liquidity (Fed assets − TGA − RRP), contemporaneous. `beta_x_sd` = gold's weekly move, in %, for a one-standard-deviation liquidity week of that era — the 'driver' and the 'habit' read together: a habit that changed shows in `beta`; a driver that started moving shows in `sd_x` and `r2` with `beta` flat.

| era | n weeks | β | t | R² | sd(Δlog NL) % | β × sd (% gold / 1-sd week) |
|---|---|---|---|---|---|---|
| all | 1145 | +0.081 | +1.97 | 0.003 | 1.82 | +0.147 |
| 2004-08 | 215 | +0.046 | +0.54 | 0.001 | 2.61 | +0.120 |
| 2009-14 | 313 | +0.039 | +0.43 | 0.001 | 1.60 | +0.063 |
| 2015-19 | 260 | +0.204 | +2.65 | 0.027 | 1.37 | +0.280 |
| 2020-21 | 105 | -0.015 | -0.14 | 0.000 | 2.18 | -0.032 |
| 2022-26 | 252 | +0.225 | +1.98 | 0.016 | 1.41 | +0.318 |

## Sequential sup-F (Bai 1997), up to 3 breaks, 15% trimming, segments ≥ 104 weeks, block-bootstrap null (500 draws, block 13)

| break | sup-F | p | segment searched | β before | β after |
|---|---|---|---|---|---|
| 2008-09-24 | 8.41 | 0.008 | 2004-11-24 → 2026-10-28 | +0.615 | +0.032 |

Registered watershed dates (±26 weeks): none of 2020-03-15, 2022-02-24, 2022-03-16 is within 26 weeks of a break found

## Sweep — is the recent window different? best W = 312 weeks, z = +1.80; best-of-sweep null q95 +2.87; p_family 0.183

