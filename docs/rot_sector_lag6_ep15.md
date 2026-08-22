# Episode-conditional rotation -- shock arm

```
==============================================================================
EPISODE-CONDITIONAL ROTATION -- Problem 2 Stage 2 (the conditional merge)
==============================================================================
chain:     SOXX, XAR, XLE, XLV, XLP
window:    2011-09-30 -> 2026-08-20 (3743 sessions)
detector:  |z|>=2.0 of SPY vs trailing 60d SD
episode:   15 sessions after trigger (trigger day EXCLUDED; gap conceded)
residual:  explicit factor (SPY)
beta:      trailing 250 sessions frozen at trigger (min 120)
triggers:  225 raw -> 99 after de-clustering (gap 15) -> 97 episodes kept (dropped: {'short_data': 1, 'short_beta': 1, 'nan': 0})
iters 2000 | seed 42 | lags 1..6

[1] POOLED WITHIN-EPISODE LEAD-LAG (k = 1..6)
      pair            max|d|   signed    p      p(Holm)
       SOXX -> XAR   0.1520  +0.1520  0.0045  0.0360 *
       SOXX -> XLE   0.0855  +0.0855  0.2434  0.7301
       SOXX -> XLV   0.0757  +0.0757  0.3893  0.7736
       SOXX -> XLP   0.1273  -0.1273  0.0250  0.1249
        XAR -> XLE   0.2041  +0.2041  0.0010  0.0100 *
        XAR -> XLV   0.1540  -0.1540  0.0035  0.0315 *
        XAR -> XLP   0.1375  -0.1375  0.0120  0.0840
        XLE -> XLV   0.0966  +0.0966  0.1289  0.5157
        XLE -> XLP   0.1373  +0.1373  0.0125  0.0840
        XLV -> XLP   0.0757  +0.0757  0.3868  0.7736
    3 of 10 pairs significant after Holm.
    per-lag pooled profile (d_ij, upper triangle):
      k=1: SOXX->XAR +0.054, SOXX->XLE +0.026, SOXX->XLV -0.000, SOXX->XLP -0.079, XAR->XLE -0.021, XAR->XLV +0.025, XAR->XLP +0.105, XLE->XLV +0.097, XLE->XLP +0.137, XLV->XLP +0.061
      k=2: SOXX->XAR -0.029, SOXX->XLE +0.086, SOXX->XLV -0.061, SOXX->XLP +0.003, XAR->XLE -0.036, XAR->XLV +0.036, XAR->XLP +0.053, XLE->XLV +0.015, XLE->XLP +0.070, XLV->XLP -0.040
      k=3: SOXX->XAR +0.152, SOXX->XLE +0.083, SOXX->XLV -0.014, SOXX->XLP -0.127, XAR->XLE -0.053, XAR->XLV +0.075, XAR->XLP +0.082, XLE->XLV -0.049, XLE->XLP +0.058, XLV->XLP -0.001
      k=4: SOXX->XAR -0.077, SOXX->XLE +0.019, SOXX->XLV +0.023, SOXX->XLP -0.020, XAR->XLE -0.023, XAR->XLV -0.102, XAR->XLP -0.000, XLE->XLV +0.002, XLE->XLP -0.005, XLV->XLP +0.076
      k=5: SOXX->XAR -0.033, SOXX->XLE -0.044, SOXX->XLV -0.059, SOXX->XLP +0.005, XAR->XLE +0.024, XAR->XLV +0.013, XAR->XLP -0.080, XLE->XLV -0.002, XLE->XLP -0.013, XLV->XLP -0.067
      k=6: SOXX->XAR -0.069, SOXX->XLE +0.004, SOXX->XLV +0.076, SOXX->XLP +0.052, XAR->XLE +0.204, XAR->XLV -0.154, XAR->XLP -0.138, XLE->XLV -0.014, XLE->XLP +0.039, XLV->XLP -0.001

[2] ORDER CONCENTRATION across 97 episodes
    mean pairwise Kendall tau-b of per-episode orders = -0.0052
    null: mean -0.0026, SD 0.0027
    p(concentration >= observed) = 0.8406
    High concentration = the same sequence recurs across episodes,
    whatever that sequence is. This is the statistic the unconditional
    test was structurally unable to compute.
    first-mover counts (earliest half-max response per episode):
      XAR    24  (25%)
      SOXX   21  (22%)
      XLV    20  (21%)
      XLE    17  (18%)
      XLP    15  (15%)

==============================================================================
READING
  Within-episode lead-lag [1]: 3/10 pairs after Holm.
  Order concentration     [2]: tau -0.005, p = 0.8406.

  3 pair(s) survive Holm WITHIN this rung, but order
  concentration does not clear its null. Holm was applied within
  the rung, NOT across the {10,15,20} ladder: 30 pair-tests total,
  so ~1.5 false positives are expected at alpha=0.05. Treat a lone
  pair as noise unless it holds with a consistent sign at adjacent
  rungs. NOT a detection.
==============================================================================
```
