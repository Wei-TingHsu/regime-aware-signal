# Rotation chain -- Stage 1 results

```
==============================================================================
ROTATION-CHAIN TRACKER -- Stage 1 (does a stable lead-lag order exist?)
==============================================================================
chain:   NVDA, TSM, ASML, MU, INTC
window:  1999-01-25 -> 2026-08-20 (6936 days)
lags:    k = 1..10 trading days | iters 2000 | seed 42

[1] DISCOVERED ORDER (residualized, full sample)
    net-lead score (higher = leads the others more):
      ASML  +0.0082
      TSM   +0.0060
      MU    -0.0033
      INTC  -0.0040
      NVDA  -0.0069
    discovered:  ASML -> TSM -> MU -> INTC -> NVDA
    thesis:      NVDA -> TSM -> ASML -> MU -> INTC
    rank agreement (Spearman) = -0.100   (+1 = identical order)

[2] THESIS-MATCH permutation (2000 rotations): p(match >= observed) = 0.5947
    Tests ONLY whether the discovered order matches the supply-chain
    thesis. A real chain running in a DIFFERENT order also returns a
    large p here. Existence is tested in [3], not here.

[3] EXISTENCE test -- is there ANY ordering structure?
    dispersion of net_lead (SD across the 5 names) = 0.0067
    permutation p (dispersion >= observed)         = 0.8371
    Null: each residual series independently circular-rotated, which
    destroys cross-series timing but preserves each series' own
    autocorrelation. This test is agnostic to WHICH order appears.

    pairwise directional statistic d_ij (positive = i leads j):
      pair            d_ij      p      p(Holm)
       NVDA -> TSM   -0.0087  0.0770  0.6927
       NVDA -> ASML  -0.0071  0.1529  0.7646
       NVDA -> MU    +0.0004  0.9365  1.0000
       NVDA -> INTC  +0.0086  0.1004  0.7031
        TSM -> ASML  -0.0079  0.0805  0.6927
        TSM -> MU    -0.0025  0.6102  1.0000
        TSM -> INTC  +0.0077  0.1174  0.7046
       ASML -> MU    +0.0026  0.6227  1.0000
       ASML -> INTC  -0.0094  0.0645  0.6447
         MU -> INTC  -0.0029  0.5507  1.0000
    0 of 10 pairs significant after Holm correction.

[4] STABILITY across 4 sub-periods
    CORRECTED -- betas fit within each sub-period:
      1999-01-25..2005-12-13:  MU -> TSM -> INTC -> ASML -> NVDA
      2005-12-14..2012-11-02:  NVDA -> INTC -> TSM -> ASML -> MU
      2012-11-05..2019-09-25:  TSM -> ASML -> NVDA -> INTC -> MU
      2019-09-26..2026-08-20:  ASML -> NVDA -> MU -> TSM -> INTC
    OLD (look-ahead) -- betas fit through 2026, kept for comparison:
      1999-01-25..2005-12-13:  MU -> INTC -> TSM -> ASML -> NVDA
      2005-12-14..2012-11-02:  INTC -> NVDA -> TSM -> ASML -> MU
      2012-11-05..2019-09-25:  ASML -> TSM -> INTC -> NVDA -> MU
      2019-09-26..2026-08-20:  ASML -> NVDA -> MU -> TSM -> INTC
    name-slots changed by removing the look-ahead: 8 / 20
    mean pairwise agreement  CORRECTED = -0.217   (old, look-ahead = -0.250)
    permutation null: mean -0.007, SD 0.200
    p(|agreement| >= observed) = 0.2659
    This is the test the statistic never had. Without it, a value near
    zero cannot be called 'anti-stable' -- with 5-item rankings the
    sampling SD alone is of the same size as the observed value.

[5] PER-LAG PROFILE (diagnostic, not a test)
    d_ij by lag k -- if a cascade completes fast, lags beyond its length
    contribute noise and DILUTE the k=1..K average that [1] reports.
      pair            k=1   k=2   k=3   k=4   k=5   k=6   k=7   k=8   k=9   k=10
       NVDA -> TSM    +0.009 -0.024 -0.022 -0.011 -0.061 -0.006 -0.004 -0.002 -0.019 +0.053
       NVDA -> ASML   -0.031 +0.021 -0.015 +0.008 +0.009 -0.040 -0.033 +0.017 +0.014 -0.023
       NVDA -> MU     +0.011 -0.006 +0.006 -0.012 +0.010 +0.032 +0.004 -0.013 -0.010 -0.017
       NVDA -> INTC   -0.032 +0.019 +0.017 +0.003 +0.030 +0.012 +0.027 +0.002 +0.009 -0.002
        TSM -> ASML   +0.008 -0.064 -0.032 -0.013 -0.014 +0.024 +0.004 +0.018 -0.015 +0.005
        TSM -> MU     +0.023 +0.041 -0.028 -0.026 -0.015 -0.012 -0.018 -0.036 -0.000 +0.046
        TSM -> INTC   +0.014 -0.018 -0.008 +0.046 -0.028 -0.006 -0.000 +0.000 +0.028 +0.048
       ASML -> MU     -0.024 -0.003 -0.014 +0.013 +0.022 +0.011 -0.021 +0.037 -0.014 +0.018
       ASML -> INTC   -0.006 -0.032 -0.000 +0.004 -0.027 -0.026 +0.030 +0.019 -0.011 -0.045
         MU -> INTC   +0.000 +0.030 -0.020 -0.053 +0.006 +0.043 -0.041 -0.008 -0.000 +0.014
    peak |d_ij| lag per pair: NVDA->TSM:5d, NVDA->ASML:6d, NVDA->MU:6d, NVDA->INTC:1d, TSM->ASML:2d, TSM->MU:10d, TSM->INTC:10d, ASML->MU:8d, ASML->INTC:10d, MU->INTC:4d

==============================================================================
READING
  Existence  [3]: p = 0.8371, 0/10 pairs after Holm.
  Thesis     [2]: p = 0.5947 (agreement -0.100).
  Stability  [4]: agreement -0.217, p = 0.2659.

  NO ordering structure detectable in this estimand. Note what that
  does and does not mean: this test measures UNCONDITIONAL, single-
  order, full-period lead-lag. If rotation is episode-local with
  per-episode order and speed, averaging across episodes yields ~0
  whether or not chains exist. A null here is consistent with both
  'no chain' and 'chains that this instrument cannot see'.

  Sub-period orders are INDISTINGUISHABLE FROM RANDOM RESHUFFLING.
  That is the defensible claim. 'Anti-stable' is NOT supported and
  is not claimed.

  Literature context: Molchanov & Stangl tested cross-sector
  predictability across 2,640 t-statistics and found scant evidence of
  sector rotation; Jacobsen, Stangl & Visaltanachoti granted perfect
  foresight of cycle stages and still got at best ~2.3%/yr. An
  unconditional null here REPLICATES published findings. The
  differentiated angle is the conditioning, not a better unconditional
  chain search.
==============================================================================
```
