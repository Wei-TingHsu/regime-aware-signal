# Episode-conditional rotation -- shock arm

```
==============================================================================
EPISODE-CONDITIONAL ROTATION -- Problem 2 Stage 2 (the conditional merge)
==============================================================================
chain:     TLT, SPY, GLD, UUP, USO
window:    2007-03-02 -> 2026-08-20 (4899 sessions)
detector:  z<=-2.0 (RISK-OFF only) of SPY vs trailing 60d SD
episode:   15 sessions after trigger (trigger day EXCLUDED; gap conceded)
residual:  NONE -- raw returns (cross-asset: the flow is the signal)
beta:      trailing 250 sessions frozen at trigger (min 120)
triggers:  184 raw -> 91 after de-clustering (gap 15) -> 88 episodes kept (dropped: {'short_data': 0, 'short_beta': 3, 'nan': 0})
iters 2000 | seed 42 | lags 1..3

[1] POOLED WITHIN-EPISODE LEAD-LAG (k = 1..3)
      pair            max|d|   signed    p      p(Holm)
        TLT -> SPY   0.0481  +0.0481  0.5762  1.0000
        TLT -> GLD   0.1278  +0.1278  0.0140  0.0840
        TLT -> UUP   0.1568  -0.1568  0.0030  0.0270 *
        TLT -> USO   0.0471  -0.0471  0.5867  1.0000
        SPY -> GLD   0.1701  +0.1701  0.0010  0.0100 *
        SPY -> UUP   0.1568  -0.1568  0.0030  0.0270 *
        SPY -> USO   0.1209  -0.1209  0.0205  0.1024
        GLD -> UUP   0.1245  -0.1245  0.0105  0.0735
        GLD -> USO   0.0586  -0.0586  0.3848  1.0000
        UUP -> USO   0.0634  +0.0634  0.3178  1.0000
    3 of 10 pairs significant after Holm.
    per-lag pooled profile (d_ij, upper triangle):
      k=1: TLT->SPY -0.020, TLT->GLD +0.053, TLT->UUP -0.019, TLT->USO -0.047, SPY->GLD +0.170, SPY->UUP -0.157, SPY->USO -0.023, GLD->UUP -0.021, GLD->USO -0.034, UUP->USO +0.063
      k=2: TLT->SPY -0.013, TLT->GLD +0.128, TLT->UUP -0.157, TLT->USO +0.000, SPY->GLD -0.097, SPY->UUP +0.129, SPY->USO +0.005, GLD->UUP -0.011, GLD->USO +0.051, UUP->USO -0.001
      k=3: TLT->SPY +0.048, TLT->GLD -0.052, TLT->UUP -0.041, TLT->USO +0.042, SPY->GLD -0.097, SPY->UUP -0.001, SPY->USO -0.121, GLD->UUP -0.125, GLD->USO -0.059, UUP->USO -0.015

[2] ORDER CONCENTRATION across 88 episodes
    mean pairwise Kendall tau-b of per-episode orders = -0.0034
    null: mean -0.0060, SD 0.0023
    p(concentration >= observed) = 0.1239
    High concentration = the same sequence recurs across episodes,
    whatever that sequence is. This is the statistic the unconditional
    test was structurally unable to compute.
    first-mover counts (earliest half-max response per episode):
      TLT    25  (28%)
      GLD    22  (25%)
      SPY    21  (24%)
      UUP    13  (15%)
      USO     7  (8%)

==============================================================================
READING
  Within-episode lead-lag [1]: 3/10 pairs after Holm.
  Order concentration     [2]: tau -0.003, p = 0.1239.

  3 pair(s) survive Holm WITHIN this rung, but order
  concentration does not clear its null. Holm was applied within
  the rung, NOT across the {10,15,20} ladder: 30 pair-tests total,
  so ~1.5 false positives are expected at alpha=0.05. Treat a lone
  pair as noise unless it holds with a consistent sign at adjacent
  rungs. NOT a detection.
==============================================================================
```
