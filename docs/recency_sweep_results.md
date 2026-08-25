# Recency kernel sweep -- results

*Run 2026-08-25 09:52:09 +0800. Registered in `docs/prereg_recency_kernel.md` (ladder, primary rung and criterion committed BEFORE this ran; two-engine amendment 2026-08-24).*

Permutations per cell: 1000.

**Every rung is reported. A single winning rung is a grid winner, not a finding.**

**Registered expectation: little or no improvement.** With no decay the weighted mean analog age is already 0.40y and median ESS is 100/100. The lever is sigma, not lambda, and sigma is frozen. A large Sharpe change would be suspect, not success.

## Engine A

`analog_core` -- z-scored PCs, one GMM frozen on all history, genuinely no-decay by default. The frozen-model and live-harness engine.

| rung | universe | n | Sharpe | spread/reb | p |
|---|---|---|---|---|---|
| inf (no decay) (control) | ALL | 826.0 | +0.4034 | +0.2219% | 0.0020 |
| inf (no decay) (control) | LONG-HISTORY | 826.0 | +0.2526 | +0.1250% | 0.0470 |
| 16y | ALL | 826.0 | +0.4043 | +0.2350% | 0.0020 |
| 16y | LONG-HISTORY | 826.0 | +0.2338 | +0.1214% | 0.0480 |
| 8y | ALL | 826.0 | +0.5301 | +0.3126% | 0.0010 |
| 8y | LONG-HISTORY | 826.0 | +0.2495 | +0.1291% | 0.0290 |
| 4y | ALL | 826.0 | +0.4977 | +0.2991% | 0.0010 |
| 4y **<- PRIMARY** | LONG-HISTORY | 826.0 | +0.3205 | +0.1694% | 0.0070 |
| 2y | ALL | 826.0 | +0.5981 | +0.3689% | 0.0010 |
| 2y | LONG-HISTORY | 826.0 | +0.4194 | +0.2279% | 0.0010 |

**VERDICT against the registered criterion: POSITIVE**

primary rung HL=4y beats the no-decay control (+0.3205 vs +0.2526) and the improvement is STRICTLY MONOTONE across 4 adjacent rungs. Criterion MET. [diagnostic only, tolerance-based counts: +/-0.01: 4, +/-0.02: 5 -- these depend on an unregistered tolerance and are NOT the reported figure]

## Engine B

`analog_backtest` -- raw PCs, GMM refit expanding-window every 20 sessions, decayed all along at `recency_decay_lambda=0.0008`/session (HL 3.44y). **The engine behind the reported 0.51 / 0.25.**

| rung | universe | n | Sharpe | spread/reb | p |
|---|---|---|---|---|---|
| incumbent (HL 3.44y, **off-ladder**) | ALL | 836.0 | +0.5200 | +0.2990% | 0.0010 |
| incumbent (HL 3.44y, **off-ladder**) | LONG-HISTORY | 836.0 | +0.2500 | +0.1330% | 0.0370 |
| inf (no decay) (control) | ALL | 836.0 | +0.5300 | +0.2880% | 0.0010 |
| inf (no decay) (control) | LONG-HISTORY | 836.0 | +0.3800 | +0.1890% | 0.0050 |
| 16y | ALL | 836.0 | +0.4700 | +0.2650% | 0.0010 |
| 16y | LONG-HISTORY | 836.0 | +0.2400 | +0.1210% | 0.0539 |
| 8y | ALL | 836.0 | +0.4800 | +0.2750% | 0.0010 |
| 8y | LONG-HISTORY | 836.0 | +0.2900 | +0.1480% | 0.0260 |
| 4y | ALL | 836.0 | +0.5400 | +0.3130% | 0.0010 |
| 4y **<- PRIMARY** | LONG-HISTORY | 836.0 | +0.3200 | +0.1680% | 0.0050 |
| 2y | ALL | 836.0 | +0.4400 | +0.2670% | 0.0010 |
| 2y | LONG-HISTORY | 836.0 | +0.3000 | +0.1600% | 0.0140 |

**VERDICT against the registered criterion: NULL**

primary rung HL=4y Sharpe +0.3200 does not beat the no-decay control +0.3800. The registered criterion requires BOTH conditions; the first fails, so stability is not evaluated.

## Reading

The two engines are different estimators and legitimately report different numbers. Neither is a rung of the other's ladder.

Engine B's `inf` rung is the number that had never been computed: the headline engine with its unregistered decay removed. The gap between it and the incumbent row is what the reported 0.51 / 0.25 owe to a hyperparameter with no recorded provenance.

