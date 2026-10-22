# Factor attribution — GLD, 2026-01-29 → 2026-10-21

*2026-10-23 00:56. Actual move -22.2% (5,600 → 4,355 at the quoted start price); 176 sessions. Sensitivities from the 504 sessions before the episode (walk-forward). Dollars = start price × each factor's share of the log move. Two orderings + the joint fit; the spread between them is the attribution's uncertainty. prereg_factor_attribution §1.*

Proxies unavailable on disk: btc (run fetch-gpr for the war factor).

## Prime factor geopolitical risk (GPR index): war → hikes → real → dollar → oil → vix → macro1 → macro2

| factor | sensitivity (β, per unit of the orthogonalised proxy) | ±1 s.e. | proxy move over the episode | share of the move | dollars | if it fully reverses |
|---|---|---|---|---|---|---|
| geopolitical risk (GPR index) | -0.0005962 | 0.0014 | +0.294 (orth. +0.294) | +0% | -1 | +1 (±2) |
| rate-hike speculation (2-yr yield minus fed funds) | -0.0002126 | 7.1e-05 | +100 (orth. +99.9) | +8% | -119 | +119 (±40) |
| real 10-yr yield | -0.0002724 | 0.00014 | +101 (orth. +59.6) | +6% | -91 | +91 (±47) |
| US dollar (broad index) | -1.436 | 0.17 | +0.0342 (orth. +0.0154) | +9% | -124 | +124 (±15) |
| oil (WTI spot) | +0.1057 | 0.025 | +0.428 (orth. +0.377) | -16% | +223 | -223 (±54) |
| equity volatility (VIX) | +0.001185 | 0.0057 | -0.0969 (orth. -0.105) | +0% | -1 | +1 (±3) |
| macro state, PCA line 1 | -0.03918 | 0.019 | +1.34 (orth. +0.153) | +2% | -34 | +34 (±16) |
| macro state, PCA line 2 | +0.04165 | 0.038 | -0.444 (orth. +0.261) | -4% | +61 | -61 (±56) |
| drift (the window's ordinary daily return × 176 sessions) | | | | -128% | +1,797 | — |
| **unexplained residual** | | | | +222% | -3,120 | — |

## Prime factor rate-hike speculation (2-yr yield minus fed funds): hikes → war → real → dollar → oil → vix → macro1 → macro2

| factor | sensitivity (β, per unit of the orthogonalised proxy) | ±1 s.e. | proxy move over the episode | share of the move | dollars | if it fully reverses |
|---|---|---|---|---|---|---|
| rate-hike speculation (2-yr yield minus fed funds) | -0.0002131 | 7.1e-05 | +100 (orth. +100) | +8% | -119 | +119 (±40) |
| geopolitical risk (GPR index) | -0.00051 | 0.0014 | +0.294 (orth. +0.194) | +0% | -1 | +1 (±2) |
| real 10-yr yield | -0.0002724 | 0.00014 | +101 (orth. +59.6) | +6% | -91 | +91 (±47) |
| US dollar (broad index) | -1.436 | 0.17 | +0.0342 (orth. +0.0154) | +9% | -124 | +124 (±15) |
| oil (WTI spot) | +0.1057 | 0.025 | +0.428 (orth. +0.377) | -16% | +223 | -223 (±54) |
| equity volatility (VIX) | +0.001185 | 0.0057 | -0.0969 (orth. -0.105) | +0% | -1 | +1 (±3) |
| macro state, PCA line 1 | -0.03918 | 0.019 | +1.34 (orth. +0.153) | +2% | -34 | +34 (±16) |
| macro state, PCA line 2 | +0.04165 | 0.038 | -0.444 (orth. +0.261) | -4% | +61 | -61 (±56) |
| drift (the window's ordinary daily return × 176 sessions) | | | | -128% | +1,797 | — |
| **unexplained residual** | | | | +222% | -3,120 | — |

## Joint fit (no ordering — shared co-movement split by least squares)

| factor | β | proxy move | share | dollars |
|---|---|---|---|---|
| geopolitical risk (GPR index) | -0.0001844 | +0.294 | +0% | -0 |
| rate-hike speculation (2-yr yield minus fed funds) | +7.211e-05 | +100 | -3% | +40 |
| real 10-yr yield | +0.0005277 | +101 | -21% | +298 |
| US dollar (broad index) | -1.476 | +0.0342 | +20% | -283 |
| oil (WTI spot) | +0.1259 | +0.428 | -21% | +302 |
| equity volatility (VIX) | -0.007568 | -0.0969 | -0% | +4 |
| macro state, PCA line 1 | -0.0457 | +1.34 | +24% | -343 |
| macro state, PCA line 2 | +0.04165 | -0.444 | +7% | -104 |
| **residual** | | | +94% | -1,323 |

## Status of the two tests that gate any bounce number (prereg §2)
- T-A explanatory stability: FAIL (median out-of-sample R² 0.18)
- T-B sign stability: geopolitical risk (GPR index) 54% UNSTABLE — not quotable, rate-hike speculation (2-yr yield minus fed funds) 66% UNSTABLE — not quotable, real 10-yr yield 63% UNSTABLE — not quotable, US dollar (broad index) 100% stable, oil (WTI spot) 90% stable, equity volatility (VIX) 59% UNSTABLE — not quotable, macro state, PCA line 1 83% stable, macro state, PCA line 2 88% stable

Reading: 'if it fully reverses' is the dollars that factor's proxy returning to its episode-start level would imply at the same sensitivity — a conditional statement, not a forecast of the reversal itself; it is quotable only for factors T-B marks stable and only after T-A passes.
