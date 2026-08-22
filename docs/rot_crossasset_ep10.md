# Episode-conditional rotation -- shock arm

```
==============================================================================
EPISODE-CONDITIONAL ROTATION -- Problem 2 Stage 2 (the conditional merge)
==============================================================================
chain:     TLT, SPY, GLD, UUP, USO
window:    2007-03-02 -> 2026-08-20 (4899 sessions)
detector:  z<=-2.0 (RISK-OFF only) of SPY vs trailing 60d SD
episode:   10 sessions after trigger (trigger day EXCLUDED; gap conceded)
residual:  NONE -- raw returns (cross-asset: the flow is the signal)
beta:      trailing 250 sessions frozen at trigger (min 120)
triggers:  184 raw -> 112 after de-clustering (gap 10) -> 108 episodes kept (dropped: {'short_data': 0, 'short_beta': 4, 'nan': 0})
iters 2000 | seed 42 | lags 1..3

[1] POOLED WITHIN-EPISODE LEAD-LAG (k = 1..3)
      pair            max|d|   signed    p      p(Holm)
        TLT -> SPY   0.1134  -0.1134  0.0655  0.3538
        TLT -> GLD   0.1143  +0.1143  0.0690  0.3538
        TLT -> UUP   0.1269  -0.1269  0.0300  0.2099
        TLT -> USO   0.1121  +0.1121  0.0590  0.3538
        SPY -> GLD   0.1874  +0.1874  0.0025  0.0250 *
        SPY -> UUP   0.0738  -0.0738  0.3078  0.6157
        SPY -> USO   0.1264  +0.1264  0.0245  0.1959
        GLD -> UUP   0.0603  -0.0603  0.5092  0.6157
        GLD -> USO   0.1078  +0.1078  0.0900  0.3538
        UUP -> USO   0.1738  -0.1738  0.0025  0.0250 *
    2 of 10 pairs significant after Holm.
    per-lag pooled profile (d_ij, upper triangle):
      k=1: TLT->SPY -0.039, TLT->GLD +0.063, TLT->UUP -0.123, TLT->USO -0.064, SPY->GLD +0.187, SPY->UUP -0.074, SPY->USO +0.032, GLD->UUP -0.015, GLD->USO +0.013, UUP->USO +0.037
      k=2: TLT->SPY -0.113, TLT->GLD +0.114, TLT->UUP -0.127, TLT->USO -0.053, SPY->GLD -0.094, SPY->UUP +0.028, SPY->USO +0.126, GLD->UUP -0.027, GLD->USO +0.108, UUP->USO +0.009
      k=3: TLT->SPY +0.063, TLT->GLD -0.083, TLT->UUP +0.049, TLT->USO +0.112, SPY->GLD -0.027, SPY->UUP +0.034, SPY->USO -0.063, GLD->UUP -0.060, GLD->USO +0.056, UUP->USO -0.174

[2] ORDER CONCENTRATION across 108 episodes
    mean pairwise Kendall tau-b of per-episode orders = +0.0049
    null: mean +0.0034, SD 0.0035
    p(concentration >= observed) = 0.3108
    High concentration = the same sequence recurs across episodes,
    whatever that sequence is. This is the statistic the unconditional
    test was structurally unable to compute.
    first-mover counts (earliest half-max response per episode):
      TLT    46  (43%)
      SPY    21  (19%)
      GLD    19  (18%)
      UUP    14  (13%)
      USO     8  (7%)

==============================================================================
READING
  Within-episode lead-lag [1]: 2/10 pairs after Holm.
  Order concentration     [2]: tau +0.005, p = 0.3108.

  2 pair(s) survive Holm WITHIN this rung, but order
  concentration does not clear its null. Holm was applied within
  the rung, NOT across the {10,15,20} ladder: 30 pair-tests total,
  so ~1.5 false positives are expected at alpha=0.05. Treat a lone
  pair as noise unless it holds with a consistent sign at adjacent
  rungs. NOT a detection.
==============================================================================
```
