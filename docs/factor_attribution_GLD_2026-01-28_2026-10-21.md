# Factor attribution — GLD, 2026-01-28 → 2026-10-21

*2026-10-23 00:30. Actual move -19.2% (5,600 → 4,524 at the quoted start price); 177 sessions. Sensitivities from the 504 sessions before the episode (walk-forward). Dollars = start price × each factor's share of the log move. Two orderings + the joint fit; the spread between them is the attribution's uncertainty. prereg_factor_attribution §1.*

## Prime factor geopolitical risk (GPR index): war → hikes → real → dollar → oil → vix → macro1 → macro2

| factor | sensitivity (β, per unit of the orthogonalised proxy) | ±1 s.e. | proxy move over the episode | share of the move | dollars | if it fully reverses |
|---|---|---|---|---|---|---|
| geopolitical risk (GPR index) | -0.0002929 | 0.0014 | -0.136 (orth. -0.136) | -0% | +0 | -0 (±1) |
| rate-hike speculation (2-yr yield minus fed funds) | -0.0002189 | 7.1e-05 | +103 (orth. +103) | +11% | -126 | +126 (±41) |
| real 10-yr yield | -0.0002693 | 0.00014 | +101 (orth. +58.5) | +7% | -88 | +88 (±46) |
| US dollar (broad index) | -1.415 | 0.17 | +0.0347 (orth. +0.0159) | +11% | -126 | +126 (±15) |
| oil (WTI spot) | +0.1026 | 0.025 | +0.439 (orth. +0.387) | -19% | +222 | -222 (±55) |
| equity volatility (VIX) | +0.0006464 | 0.0056 | -0.0969 (orth. -0.0888) | +0% | -0 | +0 (±3) |
| macro state, PCA line 1 | -0.04082 | 0.019 | +1.36 (orth. +0.16) | +3% | -37 | +37 (±17) |
| macro state, PCA line 2 | +0.04658 | 0.038 | -0.447 (orth. +0.253) | -6% | +66 | -66 (±53) |
| drift (the window's ordinary daily return × 177 sessions) | | | | -142% | +1,699 | — |
| **unexplained residual** | | | | +235% | -2,806 | — |

## Prime factor rate-hike speculation (2-yr yield minus fed funds): hikes → war → real → dollar → oil → vix → macro1 → macro2

| factor | sensitivity (β, per unit of the orthogonalised proxy) | ±1 s.e. | proxy move over the episode | share of the move | dollars | if it fully reverses |
|---|---|---|---|---|---|---|
| rate-hike speculation (2-yr yield minus fed funds) | -0.0002191 | 7.1e-05 | +103 (orth. +103) | +11% | -126 | +126 (±41) |
| geopolitical risk (GPR index) | -0.0001995 | 0.0014 | -0.136 (orth. -0.244) | -0% | +0 | -0 (±2) |
| real 10-yr yield | -0.0002693 | 0.00014 | +101 (orth. +58.5) | +7% | -88 | +88 (±46) |
| US dollar (broad index) | -1.415 | 0.17 | +0.0347 (orth. +0.0159) | +11% | -126 | +126 (±15) |
| oil (WTI spot) | +0.1026 | 0.025 | +0.439 (orth. +0.387) | -19% | +222 | -222 (±55) |
| equity volatility (VIX) | +0.0006464 | 0.0056 | -0.0969 (orth. -0.0888) | +0% | -0 | +0 (±3) |
| macro state, PCA line 1 | -0.04082 | 0.019 | +1.36 (orth. +0.16) | +3% | -37 | +37 (±17) |
| macro state, PCA line 2 | +0.04658 | 0.038 | -0.447 (orth. +0.253) | -6% | +66 | -66 (±53) |
| drift (the window's ordinary daily return × 177 sessions) | | | | -142% | +1,699 | — |
| **unexplained residual** | | | | +235% | -2,806 | — |

## Joint fit (no ordering — shared co-movement split by least squares)

| factor | β | proxy move | share | dollars |
|---|---|---|---|---|
| geopolitical risk (GPR index) | +0.0001542 | -0.136 | +0% | -0 |
| rate-hike speculation (2-yr yield minus fed funds) | +6.575e-05 | +103 | -3% | +38 |
| real 10-yr yield | +0.0005883 | +101 | -28% | +333 |
| US dollar (broad index) | -1.47 | +0.0347 | +24% | -286 |
| oil (WTI spot) | +0.124 | +0.439 | -26% | +305 |
| equity volatility (VIX) | -0.008257 | -0.0969 | -0% | +4 |
| macro state, PCA line 1 | -0.04812 | +1.36 | +31% | -367 |
| macro state, PCA line 2 | +0.04658 | -0.447 | +10% | -117 |
| **residual** | | | +93% | -1,106 |

## Status of the two tests that gate any bounce number (prereg §2)
- T-A explanatory stability: FAIL (median out-of-sample R² 0.18)
- T-B sign stability: geopolitical risk (GPR index) 54% UNSTABLE — not quotable, rate-hike speculation (2-yr yield minus fed funds) 66% UNSTABLE — not quotable, real 10-yr yield 63% UNSTABLE — not quotable, US dollar (broad index) 100% stable, oil (WTI spot) 90% stable, equity volatility (VIX) 59% UNSTABLE — not quotable, macro state, PCA line 1 83% stable, macro state, PCA line 2 88% stable

Reading: 'if it fully reverses' is the dollars that factor's proxy returning to its episode-start level would imply at the same sensitivity — a conditional statement, not a forecast of the reversal itself; it is quotable only for factors T-B marks stable and only after T-A passes.
