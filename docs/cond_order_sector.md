# Environment-conditional order

```
==============================================================================
ENVIRONMENT-CONDITIONAL ORDER -- does the sequence depend on the regime?
==============================================================================
chain:     SOXX, XAR, XLE, XLV, XLP
detector:  |z|>=2.0 of SPY vs trailing 60d SD
residual:  market
episodes:  97 (eplen 15) | iters 5000 | seed 42
regimes:   4, canonically ordered calm->stressed by PC3 (|corr| VIX 0.96)
    episodes per regime: R1=49, R2=21, R3=27

[A] DOES CONDITIONING ON REGIME RAISE ORDER AGREEMENT?
    pooled  mean pairwise tau = -0.0052
    within-regime  mean tau   = -0.0015
    lift (within - pooled)    = +0.0037
    null (regime labels shuffled across episodes): mean -0.0001, SD 0.0079
    p(lift >= observed) = 0.2717
    Null preserves group SIZES and every episode path; it destroys
    only the correspondence between environment and order. ONE test.

[B] IS THERE A CONSISTENT FIRST MOVER?
    first-mover share (uniform would be 20%):
      XAR     24.7%
      SOXX    21.6%
      XLV     20.6%
      XLE     17.5%
      XLP     15.5%
    concentration statistic = 0.00523
    null mean 0.00917, SD 0.00538
    p(concentration >= observed) = 0.7437

[C] PER-REGIME ORDERS -- DESCRIPTIVE ONLY, NOT TESTED
    Median half-max response day per asset, by regime. Do NOT report
    these as findings: no significance test is applied, and with a
    handful of episodes per regime the orders are unstable.
      R1 (n= 49): XLP -> SOXX -> XAR -> XLE -> XLV   median days [3, 4, 4, 4, 5]
      R2 (n= 21): XLE -> XAR -> XLV -> SOXX -> XLP   median days [3, 4, 4, 6, 6]
      R3 (n= 27): XAR -> XLV -> SOXX -> XLE -> XLP   median days [3, 4, 5, 6, 7]

==============================================================================
READING
  Conditioning lift [A]: +0.0037, p = 0.2717
  First-mover       [B]: p = 0.7437

  NO conditioning lift. Grouping episodes by macro regime does not
  raise order agreement above shuffled labels. The pooled nulls
  were NOT a dilution artifact: there is no environment-specific
  sequence hiding inside them, at this regime resolution and this
  episode count.
  No consistent first mover. The observed shares are within what
  the shuffle null produces.
==============================================================================
```
