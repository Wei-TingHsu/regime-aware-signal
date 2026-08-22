# Episode-conditional rotation -- shock arm

```
==============================================================================
EPISODE-CONDITIONAL ROTATION -- Problem 2 Stage 2 (the conditional merge)
==============================================================================
chain:     NVDA, TSM, ASML, MU, INTC
window:    1999-01-25 -> 2026-08-20 (6936 sessions)
detector:  |z|>=2.0 of eq-weight chain vs trailing 60d SD
episode:   20 sessions after trigger (trigger day EXCLUDED; gap conceded)
beta:      trailing 250 sessions frozen at trigger (min 120)
triggers:  417 raw -> 173 after de-clustering (gap 20) -> 171 episodes kept (dropped: {'short_data': 1, 'short_beta': 1, 'nan': 0})
iters 2000 | seed 42 | lags 1..3

[1] POOLED WITHIN-EPISODE LEAD-LAG (k = 1..3)
      pair            max|d|   signed    p      p(Holm)
       NVDA -> TSM   0.0175  +0.0175  0.8581  1.0000
       NVDA -> ASML  0.0413  +0.0413  0.2829  1.0000
       NVDA -> MU    0.0148  -0.0148  0.9225  1.0000
       NVDA -> INTC  0.0351  -0.0351  0.4063  1.0000
        TSM -> ASML  0.0944  -0.0944  0.0020  0.0200 *
        TSM -> MU    0.0297  +0.0297  0.5892  1.0000
        TSM -> INTC  0.0257  +0.0257  0.6667  1.0000
       ASML -> MU    0.0479  -0.0479  0.1784  1.0000
       ASML -> INTC  0.0390  +0.0390  0.3293  1.0000
         MU -> INTC  0.0386  +0.0386  0.3573  1.0000
    1 of 10 pairs significant after Holm.
    per-lag pooled profile (d_ij, upper triangle):
      k=1: NVDA->TSM +0.018, NVDA->ASML -0.041, NVDA->MU +0.003, NVDA->INTC -0.035, TSM->ASML +0.022, TSM->MU +0.027, TSM->INTC +0.026, ASML->MU -0.034, ASML->INTC -0.030, MU->INTC +0.008
      k=2: NVDA->TSM -0.006, NVDA->ASML +0.041, NVDA->MU -0.012, NVDA->INTC +0.014, TSM->ASML -0.039, TSM->MU +0.030, TSM->INTC -0.005, ASML->MU -0.004, ASML->INTC +0.017, MU->INTC +0.039
      k=3: NVDA->TSM -0.017, NVDA->ASML +0.029, NVDA->MU -0.015, NVDA->INTC +0.005, TSM->ASML -0.094, TSM->MU -0.026, TSM->INTC +0.010, ASML->MU -0.048, ASML->INTC +0.039, MU->INTC -0.036

[2] ORDER CONCENTRATION across 171 episodes
    mean pairwise Kendall tau-b of per-episode orders = -0.0021
    null: mean -0.0028, SD 0.0012
    p(concentration >= observed) = 0.2674
    High concentration = the same sequence recurs across episodes,
    whatever that sequence is. This is the statistic the unconditional
    test was structurally unable to compute.
    first-mover counts (earliest half-max response per episode):
      NVDA   44  (26%)
      ASML   42  (25%)
      TSM    34  (20%)
      MU     27  (16%)
      INTC   24  (14%)

==============================================================================
READING
  Within-episode lead-lag [1]: 1/10 pairs after Holm.
  Order concentration     [2]: tau -0.002, p = 0.2674.

  EPISODE-LOCAL STRUCTURE DETECTED. Next: (a) confirm on the other
  trigger arm; (b) per-episode order table as the Stage 2 output;
  (c) only then, position sizing on the detected sequence.
==============================================================================
```
