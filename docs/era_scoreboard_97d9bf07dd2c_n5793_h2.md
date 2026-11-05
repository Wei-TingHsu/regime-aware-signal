# The report's calls by era — `97d9bf07dd2c_n5793`, horizon 2, ret_primary

1,646 calls 2009-02-11 → 2026-10-22; pooled hit-rate 55.3%, asymmetry 1.001, mean signed +0.110%, PF 1.24. Null: call signs permuted in blocks of 2 within asset, 500 draws; a group 'beats null' when its hit-rate exceeds the null's 95th percentile. Rows with n < 30 are UNDERPOWERED, not verdicts.

## By era (registered boundaries)

| group | n | first | last | hit-rate | null q95 | p | asymmetry | mean signed | PF | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 2009-14 | 263 | 2009-02-11 | 2014-12-24 | 57.0% | 58.6% | 0.144 | 0.829 | +0.044% | 1.10 | inside null |
| 2015-19 | 421 | 2015-01-07 | 2019-12-23 | 54.6% | 57.2% | 0.426 | 1.033 | +0.087% | 1.24 | inside null |
| 2020-21 | 263 | 2020-01-02 | 2021-12-27 | 58.6% | 60.1% | 0.150 | 0.764 | +0.039% | 1.08 | inside null |
| 2022-26 | 699 | 2022-01-03 | 2026-10-22 | 53.8% | 56.4% | 0.490 | 1.147 | +0.175% | 1.33 | inside null |

## Split rule C at the median date (2021-03-13)

First half: n 823, hit 57.0%, mean signed +0.095%; second half: n 823, hit 53.6%, mean signed +0.124%. S1 sign agreement: PASS; S2 magnitude (ratio 1.30 ≤ 3): PASS.

## By tier (row 25)

| group | n | first | last | hit-rate | null q95 | p | asymmetry | mean signed | PF | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| 3.0 | 1404 | 2009-02-11 | 2026-10-22 | 56.7% | 56.4% | 0.026 | 0.973 | +0.121% | 1.27 | beats null |
| 2.0 | 223 | 2012-03-13 | 2026-10-15 | 47.1% | 58.7% | 0.992 | 1.199 | +0.036% | 1.07 | inside null |
| 1.0 | 19 | 2012-06-19 | 2017-01-05 | 47.4% | 63.2% | 0.626 | 1.286 | +0.158% | 1.16 | UNDERPOWERED (n < 30) |

## By dominant source (row 26)

| group | n | first | last | hit-rate | null q95 | p | asymmetry | mean signed | PF | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| political_order | 302 | 2011-03-02 | 2026-10-21 | 55.0% | 57.3% | 0.294 | 0.998 | +0.109% | 1.22 | inside null |
| fomc_statement | 289 | 2011-01-26 | 2026-09-16 | 53.6% | 57.1% | 0.440 | 1.048 | +0.108% | 1.21 | inside null |
| fomc_minutes | 296 | 2011-02-16 | 2026-08-19 | 52.7% | 56.4% | 0.422 | 0.910 | +0.006% | 1.01 | inside null |
| political_other | 189 | 2012-03-14 | 2026-10-14 | 59.3% | 59.8% | 0.110 | 0.984 | +0.239% | 1.43 | inside null |
| earnings_8k | 570 | 2009-02-11 | 2026-10-22 | 56.3% | 58.8% | 0.436 | 1.019 | +0.122% | 1.31 | inside null |

## By asset

| group | n | first | last | hit-rate | null q95 | p | asymmetry | mean signed | PF | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| GLD | 209 | 2011-03-02 | 2026-10-21 | 51.2% | 57.9% | 0.668 | 1.079 | +0.074% | 1.13 | inside null |
| SPY | 722 | 2009-03-17 | 2026-10-22 | 57.1% | 59.4% | 0.484 | 0.949 | +0.104% | 1.26 | inside null |
| TLT | 316 | 2009-02-11 | 2026-10-21 | 53.8% | 57.6% | 0.466 | 1.047 | +0.088% | 1.22 | inside null |
| USO | 189 | 2011-05-25 | 2026-10-21 | 57.7% | 57.7% | 0.056 | 0.922 | +0.252% | 1.26 | inside null |
| UUP | 210 | 2010-10-13 | 2026-10-15 | 53.3% | 54.8% | 0.134 | 1.190 | +0.068% | 1.36 | inside null |

## Sweep — era × source × asset (hit-rate, cells with n ≥ 30)

Best cell `{'era': '2020-21', 'source': 'earnings_8k', 'asset': 'all'}`: hit-rate 63.4% on n = 101; best-of-sweep null 95th percentile 75.0%; **p_family = 0.957**; survivors 0.
A survivor here is a candidate for a forward test, not a finding: the whole surface is in the JSON beside this file.

