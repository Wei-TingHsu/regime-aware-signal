# Episode-conditional rotation -- shock arm

```
==============================================================================
EPISODE-CONDITIONAL ROTATION -- Problem 2 Stage 2 (the conditional merge)
==============================================================================
chain:     SOXX, XAR, XLE, XLV, XLP
window:    2011-09-30 -> 2026-08-20 (3743 sessions)
detector:  |z|>=2.0 of SPY vs trailing 60d SD
episode:   10 sessions after trigger (trigger day EXCLUDED; gap conceded)
residual:  explicit factor (SPY)
beta:      trailing 250 sessions frozen at trigger (min 120)
triggers:  225 raw -> 108 after de-clustering (gap 10) -> 107 episodes kept (dropped: {'short_data': 0, 'short_beta': 1, 'nan': 0})
iters 2000 | seed 42 | lags 1..3

[1] POOLED WITHIN-EPISODE LEAD-LAG (k = 1..3)
      pair            max|d|   signed    p      p(Holm)
       SOXX -> XAR   0.2011  +0.2011  0.0020  0.0200 *
       SOXX -> XLE   0.1184  +0.1184  0.0420  0.2939
       SOXX -> XLV   0.0479  -0.0479  0.6837  1.0000
       SOXX -> XLP   0.0896  -0.0896  0.1924  1.0000
        XAR -> XLE   0.0688  +0.0688  0.3978  1.0000
        XAR -> XLV   0.0625  +0.0625  0.4788  1.0000
        XAR -> XLP   0.0595  +0.0595  0.5287  1.0000
        XLE -> XLV   0.1574  +0.1574  0.0070  0.0630
        XLE -> XLP   0.1326  +0.1326  0.0175  0.1399
        XLV -> XLP   0.0387  -0.0387  0.8261  1.0000
    1 of 10 pairs significant after Holm.
    per-lag pooled profile (d_ij, upper triangle):
      k=1: SOXX->XAR +0.011, SOXX->XLE +0.060, SOXX->XLV -0.028, SOXX->XLP -0.028, XAR->XLE -0.036, XAR->XLV +0.030, XAR->XLP +0.060, XLE->XLV +0.157, XLE->XLP +0.133, XLV->XLP -0.004
      k=2: SOXX->XAR +0.006, SOXX->XLE +0.118, SOXX->XLV -0.027, SOXX->XLP -0.015, XAR->XLE +0.069, XAR->XLV +0.062, XAR->XLP +0.054, XLE->XLV +0.044, XLE->XLP +0.131, XLV->XLP -0.039
      k=3: SOXX->XAR +0.201, SOXX->XLE +0.039, SOXX->XLV -0.048, SOXX->XLP -0.090, XAR->XLE -0.010, XAR->XLV +0.033, XAR->XLP +0.030, XLE->XLV -0.064, XLE->XLP -0.005, XLV->XLP -0.029

[2] ORDER CONCENTRATION across 107 episodes
    mean pairwise Kendall tau-b of per-episode orders = +0.0010
    null: mean +0.0020, SD 0.0032
    p(concentration >= observed) = 0.5952
    High concentration = the same sequence recurs across episodes,
    whatever that sequence is. This is the statistic the unconditional
    test was structurally unable to compute.
    first-mover counts (earliest half-max response per episode):
      SOXX   35  (33%)
      XAR    23  (21%)
      XLV    20  (19%)
      XLE    19  (18%)
      XLP    10  (9%)

==============================================================================
READING
  Within-episode lead-lag [1]: 1/10 pairs after Holm.
  Order concentration     [2]: tau +0.001, p = 0.5952.

  1 pair(s) survive Holm WITHIN this rung, but order
  concentration does not clear its null. Holm was applied within
  the rung, NOT across the {10,15,20} ladder: 30 pair-tests total,
  so ~1.5 false positives are expected at alpha=0.05. Treat a lone
  pair as noise unless it holds with a consistent sign at adjacent
  rungs. NOT a detection.
==============================================================================
```
