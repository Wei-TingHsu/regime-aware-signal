# R6b — the regime count on usefulness, with the engine's own expanding refit (no look-ahead)

Each k through `regime_labels_expanding` (refit every 20 sessions, first 504 unlabelled, components ordered by mean PC1), then confirmed as the product applies labels. Jobs: (a) Fed-day — lower p = the labels condition gold's reaction to a rate surprise; (b) factor R² spread — wider = the labels separate 'gold is a macro asset' from 'it is not'; (c) favoured-asset map — ranking stability between each regime's first and second half, with its block-permutation p.

| k | median run | runs | Fed-day interaction p | factor R² by regime | spread | asset-map stability | p |
|---|---|---|---|---|---|---|---|
| 3 | 53 | 32 | 0.938 | 0: 0.16, 1: 0.22 | 0.055 | +0.50 | 0.140 |
| 4 | 44 | 42 | 0.008 | 0: 0.18, 1: 0.25, 2: 0.31, 3: 0.18 | 0.125 | +0.30 | 0.200 |
| 5 | 43 | 40 | 0.442 | 0: 0.20, 1: 0.28, 2: 0.23, 3: 0.43, 4: 0.18 | 0.256 | -0.14 | 0.873 |
| 6 | 26 | 61 | 0.014 | 0: 0.20, 1: 0.25, 2: 0.22, 3: 0.31, 4: 0.44, 5: 0.19 | 0.254 | -0.15 | 0.860 |

The count is chosen on this table by dated amendment (prereg_regime_audit §2); a switch relabels history and the precedent pools are rebuilt.
