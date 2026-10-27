# Factor attribution — GLD, 2026-01-29 → 2026-10-22

*2026-10-27 23:13. Actual move -25.4% (5,600 → 4,178 at the quoted start price); 185 sessions. Sensitivities from the 504 sessions before the episode (walk-forward). Dollars = start price × each factor's share of the log move. Two orderings + the joint fit; the spread between them is the attribution's uncertainty. prereg_factor_attribution §1.*

Proxies unavailable on disk: btc, gldflow.

## Prime factor geopolitical risk (GPR index): war → hikes → real → dollar → oil → vix → cot_gold → cot_silver → cot_oil → macro1 → macro2

| factor | sensitivity (β, per unit of the orthogonalised proxy) | ±1 s.e. | proxy move over the episode | share of the move | dollars | if it fully reverses |
|---|---|---|---|---|---|---|
| geopolitical risk (GPR index) | -0.0005962 | 0.0014 | +0.617 (orth. +0.617) | +0% | -2 | +2 (±5) |
| rate-hike speculation (2-yr yield minus fed funds) | -0.0002126 | 7.1e-05 | +85 (orth. +84.7) | +6% | -101 | +101 (±34) |
| real 10-yr yield | -0.0002724 | 0.00014 | +74 (orth. +38.6) | +4% | -59 | +59 (±31) |
| US dollar (broad index) | -1.436 | 0.17 | +0.0322 (orth. +0.017) | +8% | -137 | +137 (±16) |
| oil (WTI spot) | +0.1057 | 0.025 | +0.542 (orth. +0.495) | -18% | +293 | -293 (±71) |
| equity volatility (VIX) | +0.001185 | 0.0057 | +0.152 (orth. +0.222) | -0% | +1 | -1 (±7) |
| speculative positioning in gold (CFTC) | +0.01934 | 0.04 | +0.00735 (orth. +0.00267) | -0% | +0 | -0 (±1) |
| speculative positioning in silver (CFTC) | +0.007818 | 0.036 | +0.00707 (orth. +0.0214) | -0% | +1 | -1 (±4) |
| speculative positioning in oil (CFTC) | +0.1294 | 0.088 | +0.0294 (orth. +0.0295) | -1% | +21 | -21 (±15) |
| macro state, PCA line 1 | -0.0385 | 0.019 | +1.11 (orth. +0.171) | +2% | -37 | +37 (±18) |
| macro state, PCA line 2 | +0.04233 | 0.038 | -0.23 (orth. +0.285) | -4% | +67 | -67 (±61) |
| drift (the window's ordinary daily return × 185 sessions) | | | | -116% | +1,903 | — |
| **unexplained residual** | | | | +219% | -3,592 | — |

## Prime factor rate-hike speculation (2-yr yield minus fed funds): hikes → war → real → dollar → oil → vix → cot_gold → cot_silver → cot_oil → macro1 → macro2

| factor | sensitivity (β, per unit of the orthogonalised proxy) | ±1 s.e. | proxy move over the episode | share of the move | dollars | if it fully reverses |
|---|---|---|---|---|---|---|
| rate-hike speculation (2-yr yield minus fed funds) | -0.0002131 | 7.1e-05 | +85 (orth. +85) | +6% | -101 | +101 (±34) |
| geopolitical risk (GPR index) | -0.00051 | 0.0014 | +0.617 (orth. +0.533) | +0% | -2 | +2 (±4) |
| real 10-yr yield | -0.0002724 | 0.00014 | +74 (orth. +38.6) | +4% | -59 | +59 (±31) |
| US dollar (broad index) | -1.436 | 0.17 | +0.0322 (orth. +0.017) | +8% | -137 | +137 (±16) |
| oil (WTI spot) | +0.1057 | 0.025 | +0.542 (orth. +0.495) | -18% | +293 | -293 (±71) |
| equity volatility (VIX) | +0.001185 | 0.0057 | +0.152 (orth. +0.222) | -0% | +1 | -1 (±7) |
| speculative positioning in gold (CFTC) | +0.01934 | 0.04 | +0.00735 (orth. +0.00267) | -0% | +0 | -0 (±1) |
| speculative positioning in silver (CFTC) | +0.007818 | 0.036 | +0.00707 (orth. +0.0214) | -0% | +1 | -1 (±4) |
| speculative positioning in oil (CFTC) | +0.1294 | 0.088 | +0.0294 (orth. +0.0295) | -1% | +21 | -21 (±15) |
| macro state, PCA line 1 | -0.0385 | 0.019 | +1.11 (orth. +0.171) | +2% | -37 | +37 (±18) |
| macro state, PCA line 2 | +0.04233 | 0.038 | -0.23 (orth. +0.285) | -4% | +67 | -67 (±61) |
| drift (the window's ordinary daily return × 185 sessions) | | | | -116% | +1,903 | — |
| **unexplained residual** | | | | +219% | -3,592 | — |

## Joint fit (no ordering — shared co-movement split by least squares)

| factor | β | proxy move | share | dollars |
|---|---|---|---|---|
| geopolitical risk (GPR index) | -0.0002338 | +0.617 | +0% | -1 |
| rate-hike speculation (2-yr yield minus fed funds) | +6.015e-05 | +85 | -2% | +29 |
| real 10-yr yield | +0.0005576 | +74 | -14% | +231 |
| US dollar (broad index) | -1.501 | +0.0322 | +16% | -270 |
| oil (WTI spot) | +0.1249 | +0.542 | -23% | +379 |
| equity volatility (VIX) | -0.006866 | +0.152 | +0% | -6 |
| speculative positioning in gold (CFTC) | +0.01923 | +0.00735 | -0% | +1 |
| speculative positioning in silver (CFTC) | +0.006096 | +0.00707 | -0% | +0 |
| speculative positioning in oil (CFTC) | +0.122 | +0.0294 | -1% | +20 |
| macro state, PCA line 1 | -0.04514 | +1.11 | +17% | -279 |
| macro state, PCA line 2 | +0.04233 | -0.23 | +3% | -55 |
| **residual** | | | +103% | -1,689 |

## Status of the two tests that gate any bounce number (prereg §2)
- T-A explanatory stability: FAIL (median out-of-sample R² 0.16)
- T-B sign stability: geopolitical risk (GPR index) 51% UNSTABLE — not quotable, rate-hike speculation (2-yr yield minus fed funds) 67% UNSTABLE — not quotable, real 10-yr yield 65% UNSTABLE — not quotable, US dollar (broad index) 100% stable, oil (WTI spot) 89% stable, equity volatility (VIX) 59% UNSTABLE — not quotable, speculative positioning in gold (CFTC) 52% UNSTABLE — not quotable, speculative positioning in silver (CFTC) 61% UNSTABLE — not quotable, speculative positioning in oil (CFTC) 61% UNSTABLE — not quotable, macro state, PCA line 1 83% stable, macro state, PCA line 2 87% stable

Reading: 'if it fully reverses' is the dollars that factor's proxy returning to its episode-start level would imply at the same sensitivity — a conditional statement, not a forecast of the reversal itself; it is quotable only for factors T-B marks stable and only after T-A passes.
