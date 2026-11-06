# T-H by era — residual momentum / reversal, GLD (2004-11-19 → 2026-11-05; 8 factors)

Signal: the residual of a rolling 252-session factor fit (refit every 20 sessions) summed over the past w sessions. Target: the next h sessions, non-overlapping. Positive IC = continuation, negative = reversal; the search is over |IC| with era as an axis.

Best `{'w': 20, 'h': 40, 'era': '2009-14'}` |IC| 0.257 vs best-of-sweep null q95 0.504; **p_family 0.930**; survivors 0.

## Signed rank IC (pooled)

| w \ h | 5 | 10 | 20 | 40 | 60 |
|---|---|---|---|---|---|
| 5 | -0.004 | +0.049 | -0.049 | -0.141 | -0.077 |
| 10 | -0.008 | -0.052 | -0.029 | -0.082 | -0.112 |
| 20 | -0.041 | -0.052 | -0.055 | -0.142 | -0.098 |
| 40 | -0.033 | -0.029 | -0.060 | +0.032 | +0.000 |
| 60 | -0.041 | -0.042 | -0.059 | -0.078 | +0.009 |

Per-era signed values are in the JSON; the pooled T-H verdict of 23 Oct (FAIL ×5) stands unless a survivor appears above.
