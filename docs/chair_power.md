# T-K — the few-shot chair problem (GLD on the 2-yr surprise, statement days)

*2026-10-27 23:47. 131 statement days 2011-01-26 → 2026-09-16; s = ΔDGS2 bp on the day, s/σ = the same in units of the yield's trailing two-year daily volatility; y = GLD log return on the day (%). prereg_liquidity_and_chair §3.*

**Pooled:** β = -0.1138% per bp (se 0.0141); in volatility units β = -0.443% per σ (se 0.054); residual σ = 1.07% a day; sd of the surprise 6.7 bp.

| chair | statements | mean surprise (bp) | sd (bp) | yield vol (bp/day) | mean GLD day (%) | β (% per bp) | se (own) | β (% per σ) | se |
|---|---|---|---|---|---|---|---|---|---|
| Bernanke | 25 | -0.4 | 2.6 | 2.9 | +0.12 | -0.3317 | 0.0995 | -0.796 | 0.236 |
| Yellen | 32 | -0.5 | 5.7 | 2.8 | +0.13 | -0.1444 | 0.0226 | -0.354 | 0.058 |
| Powell | 71 | -1.6 | 7.8 | 5.1 | +0.21 | -0.0964 | 0.0170 | -0.447 | 0.084 |
| Warsh | 3 | +6.0 | 9.5 | 5.3 | -0.82 | -0.1423 | 0.0315 | -0.757 | 0.183 |

**T-K0 power:** meetings needed to detect a chair-specific difference at α 5%, power 80% — delta = beta/2: **62**; delta = beta/1: **16**. A tenure is 8 meetings a year; a four-year term 32.

**T-K1 chairs differ (per bp)?** F = 4.43 among Bernanke, Yellen, Powell; permutation p = **0.016** → **PASS — chairs differ per bp**; between-chair τ = 0.1091% per bp; TLT cross-check F = 0.36, p = 0.634.

**T-K1′ chairs differ (per σ of the yield)?** F = 2.10; permutation p = **0.118** → **FAIL — no chair difference once the surprise is in volatility units**.

**T-K2 Warsh so far (3 statements):** own slope -0.1423% per bp; standard error from the pooled residual σ 0.0795 (the own 1-dof se was 0.0315); weight the data earns against the pooled prior **65%** (it would have been 92% on the own se); posterior **-0.1324% ± 0.0643** per bp. His statement days averaged -0.82% on gold; the pooled slope times his average surprise gives -0.68% — most of it: gold fell on his days because the statements surprised hawkish, not because gold reacts to him differently.

**T-K3 (not run):** smallest attainable exact-permutation p for n statements against the previous chair's last 8 — n = 3: 0.0061, n = 4: 0.0020, n = 5: 0.0008, n = 6: 0.0003, n = 8: 0.0001.
