# Episode-conditional rotation -- shock arm

```
==============================================================================
EPISODE-CONDITIONAL ROTATION -- Problem 2 Stage 2 (the conditional merge)
==============================================================================
chain:     SOXX, XAR, XLE, XLV, XLP
window:    2011-09-30 -> 2026-08-20 (3743 sessions)
detector:  |z|>=2.0 of SPY vs trailing 60d SD
episode:   20 sessions after trigger (trigger day EXCLUDED; gap conceded)
residual:  explicit factor (SPY)
beta:      trailing 250 sessions frozen at trigger (min 120)
triggers:  225 raw -> 79 after de-clustering (gap 20) -> 77 episodes kept (dropped: {'short_data': 1, 'short_beta': 1, 'nan': 0})
iters 2000 | seed 42 | lags 1..6

[1] POOLED WITHIN-EPISODE LEAD-LAG (k = 1..6)
      pair            max|d|   signed    p      p(Holm)
       SOXX -> XAR   0.1497  +0.1497  0.0015  0.0150 *
       SOXX -> XLE   0.0544  +0.0544  0.6597  1.0000
       SOXX -> XLV   0.0826  -0.0826  0.2084  0.8336
       SOXX -> XLP   0.1063  -0.1063  0.0495  0.3958
        XAR -> XLE   0.0586  +0.0586  0.5537  1.0000
        XAR -> XLV   0.0876  +0.0876  0.1369  0.6847
        XAR -> XLP   0.0693  +0.0693  0.3783  1.0000
        XLE -> XLV   0.1013  +0.1013  0.0660  0.3958
        XLE -> XLP   0.1116  +0.1116  0.0360  0.3238
        XLV -> XLP   0.1070  +0.1070  0.0550  0.3958
    1 of 10 pairs significant after Holm.
    per-lag pooled profile (d_ij, upper triangle):
      k=1: SOXX->XAR +0.066, SOXX->XLE +0.053, SOXX->XLV -0.006, SOXX->XLP -0.048, XAR->XLE +0.006, XAR->XLV -0.002, XAR->XLP +0.069, XLE->XLV +0.101, XLE->XLP +0.112, XLV->XLP +0.066
      k=2: SOXX->XAR -0.032, SOXX->XLE +0.054, SOXX->XLV -0.030, SOXX->XLP -0.021, XAR->XLE +0.001, XAR->XLV +0.017, XAR->XLP +0.028, XLE->XLV -0.021, XLE->XLP +0.085, XLV->XLP -0.072
      k=3: SOXX->XAR +0.150, SOXX->XLE +0.036, SOXX->XLV -0.055, SOXX->XLP -0.106, XAR->XLE -0.028, XAR->XLV +0.067, XAR->XLP +0.035, XLE->XLV -0.017, XLE->XLP +0.020, XLV->XLP -0.010
      k=4: SOXX->XAR -0.041, SOXX->XLE +0.037, SOXX->XLV +0.073, SOXX->XLP -0.006, XAR->XLE +0.018, XAR->XLV -0.079, XAR->XLP -0.064, XLE->XLV -0.007, XLE->XLP -0.084, XLV->XLP +0.107
      k=5: SOXX->XAR +0.000, SOXX->XLE -0.018, SOXX->XLV -0.083, SOXX->XLP -0.027, XAR->XLE +0.026, XAR->XLV +0.088, XAR->XLP -0.040, XLE->XLV +0.002, XLE->XLP -0.072, XLV->XLP -0.064
      k=6: SOXX->XAR +0.018, SOXX->XLE +0.039, SOXX->XLV +0.061, SOXX->XLP -0.024, XAR->XLE +0.059, XAR->XLV -0.067, XAR->XLP -0.013, XLE->XLV -0.041, XLE->XLP +0.006, XLV->XLP +0.026

[2] ORDER CONCENTRATION across 77 episodes
    mean pairwise Kendall tau-b of per-episode orders = -0.0051
    null: mean -0.0043, SD 0.0035
    p(concentration >= observed) = 0.5592
    High concentration = the same sequence recurs across episodes,
    whatever that sequence is. This is the statistic the unconditional
    test was structurally unable to compute.
    first-mover counts (earliest half-max response per episode):
      XAR    21  (27%)
      SOXX   20  (26%)
      XLV    13  (17%)
      XLP    12  (16%)
      XLE    11  (14%)

==============================================================================
READING
  Within-episode lead-lag [1]: 1/10 pairs after Holm.
  Order concentration     [2]: tau -0.005, p = 0.5592.

  1 pair(s) survive Holm WITHIN this rung, but order
  concentration does not clear its null. Holm was applied within
  the rung, NOT across the {10,15,20} ladder: 30 pair-tests total,
  so ~1.5 false positives are expected at alpha=0.05. Treat a lone
  pair as noise unless it holds with a consistent sign at adjacent
  rungs. NOT a detection.
==============================================================================
```
