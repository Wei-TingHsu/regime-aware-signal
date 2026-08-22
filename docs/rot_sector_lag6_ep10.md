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
iters 2000 | seed 42 | lags 1..6

[1] POOLED WITHIN-EPISODE LEAD-LAG (k = 1..6)
      pair            max|d|   signed    p      p(Holm)
       SOXX -> XAR   0.2011  +0.2011  0.0100  0.1000
       SOXX -> XLE   0.1184  +0.1184  0.1919  0.9595
       SOXX -> XLV   0.1369  -0.1369  0.0990  0.6927
       SOXX -> XLP   0.0896  -0.0896  0.4928  1.0000
        XAR -> XLE   0.1663  +0.1663  0.0285  0.2564
        XAR -> XLV   0.0817  -0.0817  0.5897  1.0000
        XAR -> XLP   0.0595  +0.0595  0.8591  1.0000
        XLE -> XLV   0.1574  +0.1574  0.0460  0.3678
        XLE -> XLP   0.1326  +0.1326  0.1044  0.6927
        XLV -> XLP   0.1207  +0.1207  0.1989  0.9595
    0 of 10 pairs significant after Holm.
    per-lag pooled profile (d_ij, upper triangle):
      k=1: SOXX->XAR +0.011, SOXX->XLE +0.060, SOXX->XLV -0.028, SOXX->XLP -0.028, XAR->XLE -0.036, XAR->XLV +0.030, XAR->XLP +0.060, XLE->XLV +0.157, XLE->XLP +0.133, XLV->XLP -0.004
      k=2: SOXX->XAR +0.006, SOXX->XLE +0.118, SOXX->XLV -0.027, SOXX->XLP -0.015, XAR->XLE +0.069, XAR->XLV +0.062, XAR->XLP +0.054, XLE->XLV +0.044, XLE->XLP +0.131, XLV->XLP -0.039
      k=3: SOXX->XAR +0.201, SOXX->XLE +0.039, SOXX->XLV -0.048, SOXX->XLP -0.090, XAR->XLE -0.010, XAR->XLV +0.033, XAR->XLP +0.030, XLE->XLV -0.064, XLE->XLP -0.005, XLV->XLP -0.029
      k=4: SOXX->XAR -0.045, SOXX->XLE -0.046, SOXX->XLV +0.067, SOXX->XLP -0.021, XAR->XLE +0.011, XAR->XLV -0.076, XAR->XLP -0.052, XLE->XLV -0.100, XLE->XLP -0.109, XLV->XLP +0.121
      k=5: SOXX->XAR +0.091, SOXX->XLE +0.049, SOXX->XLV -0.137, SOXX->XLP -0.034, XAR->XLE +0.083, XAR->XLV +0.057, XAR->XLP -0.042, XLE->XLV -0.013, XLE->XLP -0.047, XLV->XLP -0.061
      k=6: SOXX->XAR -0.054, SOXX->XLE +0.058, SOXX->XLV +0.060, SOXX->XLP -0.048, XAR->XLE +0.166, XAR->XLV -0.082, XAR->XLP -0.002, XLE->XLV -0.080, XLE->XLP +0.047, XLV->XLP +0.030

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
  Within-episode lead-lag [1]: 0/10 pairs after Holm.
  Order concentration     [2]: tau +0.001, p = 0.5952.

  No episode-local structure under this detector. Scope: this arm's
  trigger and this chain. If the POWERED (shock) arm is null, the
  episode-local hypothesis loses its main support; a stress-arm
  null alone is underpowered and inconclusive by itself.
==============================================================================
```
