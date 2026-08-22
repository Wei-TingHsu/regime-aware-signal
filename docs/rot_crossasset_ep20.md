# Episode-conditional rotation -- shock arm

```
==============================================================================
EPISODE-CONDITIONAL ROTATION -- Problem 2 Stage 2 (the conditional merge)
==============================================================================
chain:     TLT, SPY, GLD, UUP, USO
window:    2007-03-02 -> 2026-08-20 (4899 sessions)
detector:  z<=-2.0 (RISK-OFF only) of SPY vs trailing 60d SD
episode:   20 sessions after trigger (trigger day EXCLUDED; gap conceded)
residual:  NONE -- raw returns (cross-asset: the flow is the signal)
beta:      trailing 250 sessions frozen at trigger (min 120)
triggers:  184 raw -> 83 after de-clustering (gap 20) -> 80 episodes kept (dropped: {'short_data': 0, 'short_beta': 3, 'nan': 0})
iters 2000 | seed 42 | lags 1..3

[1] POOLED WITHIN-EPISODE LEAD-LAG (k = 1..3)
      pair            max|d|   signed    p      p(Holm)
        TLT -> SPY   0.0722  -0.0722  0.1484  0.5937
        TLT -> GLD   0.0707  -0.0707  0.1869  0.5937
        TLT -> UUP   0.0993  -0.0993  0.0250  0.1749
        TLT -> USO   0.0796  -0.0796  0.0970  0.4848
        SPY -> GLD   0.2007  +0.2007  0.0005  0.0050 *
        SPY -> UUP   0.1193  -0.1193  0.0055  0.0495 *
        SPY -> USO   0.0895  -0.0895  0.0490  0.2939
        GLD -> UUP   0.0984  -0.0984  0.0190  0.1519
        GLD -> USO   0.0638  +0.0638  0.2494  0.5937
        UUP -> USO   0.0717  -0.0717  0.1554  0.5937
    2 of 10 pairs significant after Holm.
    per-lag pooled profile (d_ij, upper triangle):
      k=1: TLT->SPY -0.054, TLT->GLD +0.020, TLT->UUP -0.032, TLT->USO -0.078, SPY->GLD +0.201, SPY->UUP -0.119, SPY->USO +0.014, GLD->UUP +0.019, GLD->USO -0.024, UUP->USO +0.050
      k=2: TLT->SPY -0.072, TLT->GLD +0.050, TLT->UUP -0.099, TLT->USO -0.080, SPY->GLD -0.056, SPY->UUP +0.022, SPY->USO +0.082, GLD->UUP -0.000, GLD->USO +0.064, UUP->USO -0.003
      k=3: TLT->SPY +0.028, TLT->GLD -0.071, TLT->UUP +0.046, TLT->USO +0.042, SPY->GLD -0.080, SPY->UUP +0.022, SPY->USO -0.089, GLD->UUP -0.098, GLD->USO +0.021, UUP->USO -0.072

[2] ORDER CONCENTRATION across 80 episodes
    mean pairwise Kendall tau-b of per-episode orders = +0.0049
    null: mean +0.0021, SD 0.0044
    p(concentration >= observed) = 0.2589
    High concentration = the same sequence recurs across episodes,
    whatever that sequence is. This is the statistic the unconditional
    test was structurally unable to compute.
    first-mover counts (earliest half-max response per episode):
      TLT    23  (29%)
      SPY    21  (26%)
      UUP    15  (19%)
      GLD    14  (18%)
      USO     7  (9%)

==============================================================================
READING
  Within-episode lead-lag [1]: 2/10 pairs after Holm.
  Order concentration     [2]: tau +0.005, p = 0.2589.

  2 pair(s) survive Holm WITHIN this rung, but order
  concentration does not clear its null. Holm was applied within
  the rung, NOT across the {10,15,20} ladder: 30 pair-tests total,
  so ~1.5 false positives are expected at alpha=0.05. Treat a lone
  pair as noise unless it holds with a consistent sign at adjacent
  rungs. NOT a detection.
==============================================================================
```
