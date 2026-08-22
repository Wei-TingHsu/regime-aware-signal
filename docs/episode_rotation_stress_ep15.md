# Episode-conditional rotation -- stress arm

```
==============================================================================
EPISODE-CONDITIONAL ROTATION -- Problem 2 Stage 2 (the conditional merge)
==============================================================================
chain:     NVDA, TSM, ASML, MU, INTC
window:    1999-01-25 -> 2026-08-20 (6936 sessions)
detector:  narrow stress-share z>=1.5 vs trailing 20-session baseline excl. t (processed/gdelt_2024_2026_narrow.csv)
episode:   15 sessions after trigger (trigger day EXCLUDED; gap conceded)
beta:      trailing 250 sessions frozen at trigger (min 120)
triggers:  65 raw -> 26 after de-clustering (gap 15) -> 26 episodes kept (dropped: {'short_data': 0, 'short_beta': 0, 'nan': 0})
iters 2000 | seed 42 | lags 1..3

[1] POOLED WITHIN-EPISODE LEAD-LAG (k = 1..3)
      pair            max|d|   signed    p      p(Holm)
       NVDA -> TSM   0.1406  +0.1406  0.2499  1.0000
       NVDA -> ASML  0.0580  +0.0580  0.8421  1.0000
       NVDA -> MU    0.0598  +0.0598  0.8231  1.0000
       NVDA -> INTC  0.1891  -0.1891  0.0275  0.2749
        TSM -> ASML  0.1828  -0.1828  0.0480  0.4318
        TSM -> MU    0.0669  -0.0669  0.7731  1.0000
        TSM -> INTC  0.1175  +0.1175  0.3893  1.0000
       ASML -> MU    0.0710  -0.0710  0.6957  1.0000
       ASML -> INTC  0.1278  +0.1278  0.2539  1.0000
         MU -> INTC  0.0689  -0.0689  0.7381  1.0000
    0 of 10 pairs significant after Holm.
    per-lag pooled profile (d_ij, upper triangle):
      k=1: NVDA->TSM +0.141, NVDA->ASML +0.058, NVDA->MU +0.060, NVDA->INTC -0.189, TSM->ASML +0.039, TSM->MU +0.035, TSM->INTC +0.065, ASML->MU +0.008, ASML->INTC +0.128, MU->INTC +0.034
      k=2: NVDA->TSM -0.016, NVDA->ASML -0.005, NVDA->MU -0.038, NVDA->INTC -0.041, TSM->ASML -0.183, TSM->MU -0.014, TSM->INTC +0.096, ASML->MU -0.023, ASML->INTC -0.071, MU->INTC +0.008
      k=3: NVDA->TSM +0.013, NVDA->ASML -0.055, NVDA->MU +0.016, NVDA->INTC -0.027, TSM->ASML -0.078, TSM->MU -0.067, TSM->INTC +0.118, ASML->MU -0.071, ASML->INTC -0.079, MU->INTC -0.069

[2] ORDER CONCENTRATION across 26 episodes
    mean pairwise Kendall tau-b of per-episode orders = -0.0149
    null: mean +0.0085, SD 0.0135
    p(concentration >= observed) = 0.9685
    High concentration = the same sequence recurs across episodes,
    whatever that sequence is. This is the statistic the unconditional
    test was structurally unable to compute.
    first-mover counts (earliest half-max response per episode):
      ASML    7  (27%)
      TSM     7  (27%)
      NVDA    6  (23%)
      INTC    4  (15%)
      MU      2  (8%)

==============================================================================
READING
  Within-episode lead-lag [1]: 0/10 pairs after Holm.
  Order concentration     [2]: tau -0.015, p = 0.9685.

  No episode-local structure under this detector. Scope: this arm's
  trigger and this chain. If the POWERED (shock) arm is null, the
  episode-local hypothesis loses its main support; a stress-arm
  null alone is underpowered and inconclusive by itself.
==============================================================================
```
