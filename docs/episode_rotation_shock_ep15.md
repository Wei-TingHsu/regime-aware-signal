# Episode-conditional rotation -- shock arm

```
==============================================================================
EPISODE-CONDITIONAL ROTATION -- Problem 2 Stage 2 (the conditional merge)
==============================================================================
chain:     NVDA, TSM, ASML, MU, INTC
window:    1999-01-25 -> 2026-08-20 (6936 sessions)
detector:  |z|>=2.0 of eq-weight chain vs trailing 60d SD
episode:   15 sessions after trigger (trigger day EXCLUDED; gap conceded)
beta:      trailing 250 sessions frozen at trigger (min 120)
triggers:  417 raw -> 204 after de-clustering (gap 15) -> 203 episodes kept (dropped: {'short_data': 0, 'short_beta': 1, 'nan': 0})
iters 2000 | seed 42 | lags 1..3

[1] POOLED WITHIN-EPISODE LEAD-LAG (k = 1..3)
      pair            max|d|   signed    p      p(Holm)
       NVDA -> TSM   0.0057  -0.0057  0.9965  1.0000
       NVDA -> ASML  0.0507  -0.0507  0.1684  1.0000
       NVDA -> MU    0.0209  -0.0209  0.8051  1.0000
       NVDA -> INTC  0.0429  -0.0429  0.2874  1.0000
        TSM -> ASML  0.0509  -0.0509  0.1979  1.0000
        TSM -> MU    0.0474  -0.0474  0.2544  1.0000
        TSM -> INTC  0.0324  -0.0324  0.5587  1.0000
       ASML -> MU    0.0276  -0.0276  0.6977  1.0000
       ASML -> INTC  0.0456  +0.0456  0.2714  1.0000
         MU -> INTC  0.0579  -0.0579  0.1199  1.0000
    0 of 10 pairs significant after Holm.
    per-lag pooled profile (d_ij, upper triangle):
      k=1: NVDA->TSM -0.005, NVDA->ASML -0.051, NVDA->MU +0.018, NVDA->INTC -0.043, TSM->ASML +0.026, TSM->MU +0.019, TSM->INTC +0.018, ASML->MU -0.028, ASML->INTC -0.031, MU->INTC +0.001
      k=2: NVDA->TSM -0.006, NVDA->ASML +0.029, NVDA->MU +0.011, NVDA->INTC +0.021, TSM->ASML -0.027, TSM->MU +0.046, TSM->INTC -0.032, ASML->MU +0.015, ASML->INTC +0.008, MU->INTC +0.047
      k=3: NVDA->TSM +0.003, NVDA->ASML +0.029, NVDA->MU -0.021, NVDA->INTC +0.035, TSM->ASML -0.051, TSM->MU -0.047, TSM->INTC +0.011, ASML->MU -0.011, ASML->INTC +0.046, MU->INTC -0.058

[2] ORDER CONCENTRATION across 203 episodes
    mean pairwise Kendall tau-b of per-episode orders = +0.0040
    null: mean +0.0026, SD 0.0020
    p(concentration >= observed) = 0.2294
    High concentration = the same sequence recurs across episodes,
    whatever that sequence is. This is the statistic the unconditional
    test was structurally unable to compute.
    first-mover counts (earliest half-max response per episode):
      TSM    54  (27%)
      NVDA   42  (21%)
      MU     39  (19%)
      ASML   39  (19%)
      INTC   29  (14%)

==============================================================================
READING
  Within-episode lead-lag [1]: 0/10 pairs after Holm.
  Order concentration     [2]: tau +0.004, p = 0.2294.

  No episode-local structure under this detector. Scope: this arm's
  trigger and this chain. If the POWERED (shock) arm is null, the
  episode-local hypothesis loses its main support; a stress-arm
  null alone is underpowered and inconclusive by itself.
==============================================================================
```
