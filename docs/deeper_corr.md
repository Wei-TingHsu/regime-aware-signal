# Deeper test corr — 2026-11-05 19:01

5,522 sessions; skill = 1 − (model squared error / baseline squared error) on the last 40% of the sample; a sizing input for the equity hedge, not a direction call.

## D3 next-period GLD–SPY correlation from realised correlation (+ stress state): out-of-sample skill vs the long-run mean

Best cell `{'win': 20, 'H': 20, 'state': False}`: net Sharpe +0.26 on n = 2194; best-of-search null 95th percentile +0.09; **p_family = 0.000**; survivors 18.

Survivors: {'win': 20, 'H': 20, 'state': False} +0.26; {'win': 20, 'H': 20, 'state': True} +0.23; {'win': 20, 'H': 40, 'state': False} +0.21; {'win': 20, 'H': 40, 'state': True} +0.18; {'win': 20, 'H': 60, 'state': False} +0.15; {'win': 20, 'H': 60, 'state': True} +0.10; {'win': 40, 'H': 20, 'state': False} +0.23; {'win': 40, 'H': 20, 'state': True} +0.19; {'win': 40, 'H': 40, 'state': False} +0.17; {'win': 40, 'H': 40, 'state': True} +0.14


A survivor here is a candidate for the forward log, not a signal: the registered rule is written by dated amendment and judged on data it has never seen.
