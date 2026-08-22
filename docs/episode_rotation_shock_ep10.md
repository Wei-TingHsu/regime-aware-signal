# Episode-conditional rotation -- shock arm

```
==============================================================================
EPISODE-CONDITIONAL ROTATION -- Problem 2 Stage 2 (the conditional merge)
==============================================================================
chain:     NVDA, TSM, ASML, MU, INTC
window:    1999-01-25 -> 2026-08-20 (6936 sessions)
detector:  |z|>=2.0 of eq-weight chain vs trailing 60d SD
episode:   10 sessions after trigger (trigger day EXCLUDED; gap conceded)
beta:      trailing 250 sessions frozen at trigger (min 120)
triggers:  417 raw -> 244 after de-clustering (gap 10) -> 243 episodes kept (dropped: {'short_data': 0, 'short_beta': 1, 'nan': 0})
iters 2000 | seed 42 | lags 1..3

[1] POOLED WITHIN-EPISODE LEAD-LAG (k = 1..3)
      pair            max|d|   signed    p      p(Holm)
       NVDA -> TSM   0.0392  -0.0392  0.5112  1.0000
       NVDA -> ASML  0.0908  +0.0908  0.0235  0.2349
       NVDA -> MU    0.0233  +0.0233  0.8271  1.0000
       NVDA -> INTC  0.0190  +0.0190  0.8986  1.0000
        TSM -> ASML  0.0854  -0.0854  0.0305  0.2744
        TSM -> MU    0.0481  -0.0481  0.3563  1.0000
        TSM -> INTC  0.0245  -0.0245  0.8176  1.0000
       ASML -> MU    0.0592  -0.0592  0.1919  1.0000
       ASML -> INTC  0.0534  +0.0534  0.2609  1.0000
         MU -> INTC  0.0357  +0.0357  0.6092  1.0000
    0 of 10 pairs significant after Holm.
    per-lag pooled profile (d_ij, upper triangle):
      k=1: NVDA->TSM -0.031, NVDA->ASML -0.056, NVDA->MU +0.023, NVDA->INTC -0.016, TSM->ASML +0.053, TSM->MU +0.013, TSM->INTC -0.004, ASML->MU -0.059, ASML->INTC +0.025, MU->INTC -0.028
      k=2: NVDA->TSM -0.018, NVDA->ASML +0.091, NVDA->MU -0.023, NVDA->INTC +0.018, TSM->ASML -0.008, TSM->MU +0.005, TSM->INTC -0.025, ASML->MU +0.006, ASML->INTC +0.053, MU->INTC +0.036
      k=3: NVDA->TSM -0.039, NVDA->ASML +0.076, NVDA->MU -0.019, NVDA->INTC +0.019, TSM->ASML -0.085, TSM->MU -0.048, TSM->INTC -0.008, ASML->MU +0.030, ASML->INTC +0.052, MU->INTC -0.006

[2] ORDER CONCENTRATION across 243 episodes
    mean pairwise Kendall tau-b of per-episode orders = +0.0011
    null: mean +0.0031, SD 0.0017
    p(concentration >= observed) = 0.8856
    High concentration = the same sequence recurs across episodes,
    whatever that sequence is. This is the statistic the unconditional
    test was structurally unable to compute.
    first-mover counts (earliest half-max response per episode):
      NVDA   65  (27%)
      TSM    64  (26%)
      ASML   48  (20%)
      MU     42  (17%)
      INTC   24  (10%)

==============================================================================
READING
  Within-episode lead-lag [1]: 0/10 pairs after Holm.
  Order concentration     [2]: tau +0.001, p = 0.8856.

  No episode-local structure under this detector. Scope: this arm's
  trigger and this chain. If the POWERED (shock) arm is null, the
  episode-local hypothesis loses its main support; a stress-arm
  null alone is underpowered and inconclusive by itself.
==============================================================================
```
