# Environment-conditional order

```
==============================================================================
ENVIRONMENT-CONDITIONAL ORDER -- does the sequence depend on the regime?
==============================================================================
chain:     TLT, SPY, GLD, UUP, USO
detector:  z<=-2.0 (RISK-OFF only) of SPY vs trailing 60d SD
residual:  none
episodes:  88 (eplen 15) | iters 5000 | seed 42
regimes:   4, canonically ordered calm->stressed by PC3 (|corr| VIX 0.96)
    episodes per regime: R0=2, R1=36, R2=32, R3=18
    THIN GROUPS (<10 episodes): R0 -- these contribute little and their per-regime tables mean nothing.

[A] DOES CONDITIONING ON REGIME RAISE ORDER AGREEMENT?
    pooled  mean pairwise tau = -0.0034
    within-regime  mean tau   = -0.0093
    lift (within - pooled)    = -0.0059
    null (regime labels shuffled across episodes): mean +0.0001, SD 0.0099
    p(lift >= observed) = 0.6883
    Null preserves group SIZES and every episode path; it destroys
    only the correspondence between environment and order. ONE test.

[B] IS THERE A CONSISTENT FIRST MOVER?
    first-mover share (uniform would be 20%):
      TLT     28.4%
      GLD     25.0%
      SPY     23.9%
      UUP     14.8%
      USO      8.0%
    concentration statistic = 0.02831
    null mean 0.01416, SD 0.00668
    p(concentration >= observed) = 0.0320

[C] PER-REGIME ORDERS -- DESCRIPTIVE ONLY, NOT TESTED
    Median half-max response day per asset, by regime. Do NOT report
    these as findings: no significance test is applied, and with a
    handful of episodes per regime the orders are unstable.
      R0 (n=  2): SPY -> TLT -> UUP -> USO -> GLD   median days [2, 4, 5, 6, 10]
      R1 (n= 36): TLT -> SPY -> GLD -> UUP -> USO   median days [3, 3, 3, 4, 4]
      R2 (n= 32): UUP -> GLD -> USO -> TLT -> SPY   median days [3, 4, 4, 5, 5]
      R3 (n= 18): UUP -> TLT -> SPY -> GLD -> USO   median days [3, 3, 3, 4, 5]

==============================================================================
READING
  Conditioning lift [A]: -0.0059, p = 0.6883
  First-mover       [B]: p = 0.0320

  NO conditioning lift. Grouping episodes by macro regime does not
  raise order agreement above shuffled labels. The pooled nulls
  were NOT a dilution artifact: there is no environment-specific
  sequence hiding inside them, at this regime resolution and this
  episode count.
  A consistent first mover EXISTS -- see the shares above. Note
  this is weaker than a full sequence: knowing who moves first
  does not tell you the order of everyone else.
==============================================================================
```
