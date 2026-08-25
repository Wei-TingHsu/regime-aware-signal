# Engine B — no decay vs the incumbent lambda, paired test

*Run 2026-08-25 10:10:40 +0800. Registered in `docs/prereg_rung_diagnostic.md` §3, before implementation.*

Sign-flip permutation on the paired per-rebalance differences, 10,000 draws, real at **p < 0.05 two-sided**. Above that the difference is reported as *not distinguishable at this sample size* — **not** as evidence the two are equal.

| universe | n paired | no-decay Sharpe | incumbent Sharpe | mean spread diff | sign-flip p | verdict |
|---|---|---|---|---|---|---|
| ALL | 836 | +0.5251 | +0.5165 | -0.0105% | 0.8960 | not distinguishable |
| LONG-HISTORY | 836 | +0.3837 | +0.2528 | +0.0579% | 0.4848 | not distinguishable |

## Reading

`docs/fine_lambda_sweep_results.md` found the Sharpe surface is **jagged** in λ — 0.30 / 0.25 / 0.22 / 0.29 across steps of 1e-4. A null here means the 0.38-vs-0.25 gap is not separable from that roughness, which is a statement about the surface rather than about λ.

