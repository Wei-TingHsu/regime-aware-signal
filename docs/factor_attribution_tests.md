# Factor attribution — tests for GLD

*2026-10-23 00:30. T-A: betas from the prior 504 sessions, R² on each next 20-session block from 2006 (walk-forward, joint fit). Bar 0.20. T-B: sign of each factor's beta across rolling windows (step 63); stable if the same sign in ≥ 70%.*

**T-A:** median out-of-sample R² **0.177** over 235 blocks → **FAIL**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 235 | 54% | UNSTABLE — not quotable |
| rate-hike speculation (2-yr yield minus fed funds) | 235 | 66% | UNSTABLE — not quotable |
| real 10-yr yield | 235 | 63% | UNSTABLE — not quotable |
| US dollar (broad index) | 235 | 100% | stable |
| oil (WTI spot) | 235 | 90% | stable |
| equity volatility (VIX) | 235 | 59% | UNSTABLE — not quotable |
| macro state, PCA line 1 | 235 | 83% | stable |
| macro state, PCA line 2 | 235 | 88% | stable |

# Factor attribution — tests for GLD

*2026-10-23 00:56. T-A: betas from the prior 504 sessions, R² on each next 20-session block from 2006 (walk-forward, joint fit). Bar 0.20. T-B: sign of each factor's beta across rolling windows (step 63); stable if the same sign in ≥ 70%.*

**T-A:** median out-of-sample R² **0.177** over 235 blocks → **FAIL**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 235 | 54% | UNSTABLE — not quotable |
| rate-hike speculation (2-yr yield minus fed funds) | 235 | 66% | UNSTABLE — not quotable |
| real 10-yr yield | 235 | 63% | UNSTABLE — not quotable |
| US dollar (broad index) | 235 | 100% | stable |
| oil (WTI spot) | 235 | 90% | stable |
| equity volatility (VIX) | 235 | 59% | UNSTABLE — not quotable |
| macro state, PCA line 1 | 235 | 83% | stable |
| macro state, PCA line 2 | 235 | 88% | stable |

# Factor attribution — tests for GLD

*2026-10-23 01:53. T-A registered cell: window 504, block 20, bar 0.20. T-B: sign of each beta across rolling windows (step 63); stable if ≥ 70%.*

**T-A (registered cell):** median out-of-sample R² **0.177** over 235 blocks → **FAIL**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 75 | 52% | UNSTABLE — not quotable |
| rate-hike speculation (2-yr yield minus fed funds) | 75 | 67% | UNSTABLE — not quotable |
| real 10-yr yield | 75 | 68% | UNSTABLE — not quotable |
| US dollar (broad index) | 75 | 100% | stable |
| oil (WTI spot) | 75 | 91% | stable |
| equity volatility (VIX) | 75 | 60% | UNSTABLE — not quotable |
| macro state, PCA line 1 | 75 | 81% | stable |
| macro state, PCA line 2 | 75 | 88% | stable |

## T-A sweep — 30 cells (window × block), SPEC_GRID family 2.10

| window | b1 | b2 | b3 | b5 | b7 | b10 | b15 | b20 | b30 | b45 | b60 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 252 | nan | -0.841 | -0.149 | 0.071 | 0.128 | 0.158 | 0.181 | 0.196 | 0.183 | 0.182 | 0.180 |
| 504 | nan | -0.867 | -0.164 | 0.041 | 0.117 | 0.162 | 0.178 | 0.177 | 0.182 | 0.189 | 0.200 |
| 756 | nan | -0.879 | -0.137 | 0.061 | 0.146 | 0.177 | 0.196 | 0.224 | 0.219 | 0.184 | 0.211 |

Best cell: window 756, block 20, median R² 0.224

Reading: a block of 1 has no R² (one point); short blocks are noisier per block but closer to the founder's 'purest window' idea. The registered verdict is the 504/20 cell; the sweep is the alternatives track and a survivor is promoted to its own forward test, never adopted in place.

# Factor attribution — tests for SPY

*2026-10-23 01:53. T-A registered cell: window 504, block 20, bar 0.10. T-B: sign of each beta across rolling windows (step 63); stable if ≥ 70%.*

**T-A (registered cell):** median out-of-sample R² **0.626** over 235 blocks → **PASS**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 75 | 88% | stable |
| rate-hike speculation (2-yr yield minus fed funds) | 75 | 71% | stable |
| real 10-yr yield | 75 | 95% | stable |
| US dollar (broad index) | 75 | 87% | stable |
| oil (WTI spot) | 75 | 89% | stable |
| equity volatility (VIX) | 75 | 100% | stable |
| macro state, PCA line 1 | 75 | 88% | stable |
| macro state, PCA line 2 | 75 | 80% | stable |

# Factor attribution — tests for TLT

*2026-10-23 01:53. T-A registered cell: window 504, block 20, bar 0.10. T-B: sign of each beta across rolling windows (step 63); stable if ≥ 70%.*

**T-A (registered cell):** median out-of-sample R² **0.841** over 235 blocks → **PASS**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 75 | 55% | UNSTABLE — not quotable |
| rate-hike speculation (2-yr yield minus fed funds) | 75 | 84% | stable |
| real 10-yr yield | 75 | 100% | stable |
| US dollar (broad index) | 75 | 100% | stable |
| oil (WTI spot) | 75 | 68% | UNSTABLE — not quotable |
| equity volatility (VIX) | 75 | 100% | stable |
| macro state, PCA line 1 | 75 | 100% | stable |
| macro state, PCA line 2 | 75 | 100% | stable |

# Factor attribution — tests for SLV

*2026-10-23 01:53. T-A registered cell: window 504, block 20, bar 0.10. T-B: sign of each beta across rolling windows (step 63); stable if ≥ 70%.*

**T-A (registered cell):** median out-of-sample R² **0.190** over 231 blocks → **PASS**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 74 | 66% | UNSTABLE — not quotable |
| rate-hike speculation (2-yr yield minus fed funds) | 74 | 66% | UNSTABLE — not quotable |
| real 10-yr yield | 74 | 61% | UNSTABLE — not quotable |
| US dollar (broad index) | 74 | 100% | stable |
| oil (WTI spot) | 74 | 100% | stable |
| equity volatility (VIX) | 74 | 84% | stable |
| macro state, PCA line 1 | 74 | 72% | stable |
| macro state, PCA line 2 | 74 | 58% | UNSTABLE — not quotable |

# Factor attribution — tests for UUP

*2026-10-23 01:53. T-A registered cell: window 504, block 20, bar 0.10. T-B: sign of each beta across rolling windows (step 63); stable if ≥ 70%.*

**T-A (registered cell):** median out-of-sample R² **0.496** over 221 blocks → **PASS**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 70 | 73% | stable |
| rate-hike speculation (2-yr yield minus fed funds) | 70 | 61% | UNSTABLE — not quotable |
| real 10-yr yield | 70 | 73% | stable |
| US dollar (broad index) | 70 | 100% | stable |
| oil (WTI spot) | 70 | 60% | UNSTABLE — not quotable |
| equity volatility (VIX) | 70 | 91% | stable |
| macro state, PCA line 1 | 70 | 90% | stable |
| macro state, PCA line 2 | 70 | 64% | UNSTABLE — not quotable |

# Factor attribution — tests for USO

*2026-10-23 01:53. T-A registered cell: window 504, block 20, bar 0.10. T-B: sign of each beta across rolling windows (step 63); stable if ≥ 70%.*

**T-A (registered cell):** median out-of-sample R² **0.870** over 232 blocks → **PASS**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 74 | 55% | UNSTABLE — not quotable |
| rate-hike speculation (2-yr yield minus fed funds) | 74 | 61% | UNSTABLE — not quotable |
| real 10-yr yield | 74 | 85% | stable |
| US dollar (broad index) | 74 | 57% | UNSTABLE — not quotable |
| oil (WTI spot) | 74 | 100% | stable |
| equity volatility (VIX) | 74 | 97% | stable |
| macro state, PCA line 1 | 74 | 82% | stable |
| macro state, PCA line 2 | 74 | 80% | stable |

# Factor attribution — tests for NVDA

*2026-10-23 01:53. T-A registered cell: window 504, block 20, bar 0.10. T-B: sign of each beta across rolling windows (step 63); stable if ≥ 70%.*

**T-A (registered cell):** median out-of-sample R² **0.167** over 235 blocks → **PASS**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 75 | 56% | UNSTABLE — not quotable |
| rate-hike speculation (2-yr yield minus fed funds) | 75 | 61% | UNSTABLE — not quotable |
| real 10-yr yield | 75 | 69% | UNSTABLE — not quotable |
| US dollar (broad index) | 75 | 84% | stable |
| oil (WTI spot) | 75 | 72% | stable |
| equity volatility (VIX) | 75 | 100% | stable |
| macro state, PCA line 1 | 75 | 85% | stable |
| macro state, PCA line 2 | 75 | 59% | UNSTABLE — not quotable |

# Factor attribution — tests for META

*2026-10-23 01:53. T-A registered cell: window 504, block 20, bar 0.10. T-B: sign of each beta across rolling windows (step 63); stable if ≥ 70%.*

**T-A (registered cell):** median out-of-sample R² **0.147** over 155 blocks → **PASS**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 50 | 64% | UNSTABLE — not quotable |
| rate-hike speculation (2-yr yield minus fed funds) | 50 | 66% | UNSTABLE — not quotable |
| real 10-yr yield | 50 | 94% | stable |
| US dollar (broad index) | 50 | 62% | UNSTABLE — not quotable |
| oil (WTI spot) | 50 | 78% | stable |
| equity volatility (VIX) | 50 | 100% | stable |
| macro state, PCA line 1 | 50 | 78% | stable |
| macro state, PCA line 2 | 50 | 72% | stable |

# Factor attribution — tests for GLD

*2026-10-23 02:04. T-A registered cell: window 504, block 20, bar 0.20. T-B: sign of each beta across rolling windows (step 63); stable if ≥ 70%.*

**T-A (registered cell):** median out-of-sample R² **0.177** over 235 blocks → **FAIL**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 75 | 52% | UNSTABLE — not quotable |
| rate-hike speculation (2-yr yield minus fed funds) | 75 | 67% | UNSTABLE — not quotable |
| real 10-yr yield | 75 | 68% | UNSTABLE — not quotable |
| US dollar (broad index) | 75 | 100% | stable |
| oil (WTI spot) | 75 | 91% | stable |
| equity volatility (VIX) | 75 | 60% | UNSTABLE — not quotable |
| macro state, PCA line 1 | 75 | 81% | stable |
| macro state, PCA line 2 | 75 | 88% | stable |

## T-A sweep — 30 cells (window × block), SPEC_GRID family 2.10

| window | b1 | b2 | b3 | b5 | b7 | b10 | b15 | b20 | b30 | b45 | b60 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 252 | nan | -0.841 | -0.149 | 0.071 | 0.128 | 0.158 | 0.181 | 0.196 | 0.183 | 0.182 | 0.180 |
| 504 | nan | -0.867 | -0.164 | 0.041 | 0.117 | 0.162 | 0.178 | 0.177 | 0.182 | 0.189 | 0.200 |
| 756 | nan | -0.879 | -0.137 | 0.061 | 0.146 | 0.177 | 0.196 | 0.224 | 0.219 | 0.184 | 0.211 |

Best cell: window 756, block 20, median R² 0.224; best-of-sweep null (50 shifted draws): median best -0.024, p = 0.000 → survives the sweep

Reading: a block of 1 has no R² (one point); short blocks are noisier per block but closer to the founder's 'purest window' idea. The registered verdict is the 504/20 cell; the sweep is the alternatives track and a survivor is promoted to its own forward test, never adopted in place.

# Factor attribution — tests for GLD

*2026-10-27 23:13. T-A registered cell: window 504, block 20, bar 0.20. T-B: sign of each beta across rolling windows (step 63); stable if ≥ 70%.*

**T-A (registered cell):** median out-of-sample R² **0.160** over 236 blocks → **FAIL**

| factor | windows | share with the majority sign | T-B |
|---|---|---|---|
| geopolitical risk (GPR index) | 75 | 51% | UNSTABLE — not quotable |
| rate-hike speculation (2-yr yield minus fed funds) | 75 | 67% | UNSTABLE — not quotable |
| real 10-yr yield | 75 | 65% | UNSTABLE — not quotable |
| US dollar (broad index) | 75 | 100% | stable |
| oil (WTI spot) | 75 | 89% | stable |
| equity volatility (VIX) | 75 | 59% | UNSTABLE — not quotable |
| speculative positioning in gold (CFTC) | 75 | 52% | UNSTABLE — not quotable |
| speculative positioning in silver (CFTC) | 75 | 61% | UNSTABLE — not quotable |
| speculative positioning in oil (CFTC) | 75 | 61% | UNSTABLE — not quotable |
| macro state, PCA line 1 | 75 | 83% | stable |
| macro state, PCA line 2 | 75 | 87% | stable |
