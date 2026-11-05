# Deeper test fomc — 2026-11-05 19:01

132 statements; targets: statement day, next day, next two days; features: the 2-yr surprise per σ, the T-K3 rubric (hawk/dove, inflation emphasis, hedging), or both; state = the yield's trailing volatility above/below its median. The statement-day target is tradeable only from 2 pm (the live reader); the others from the close.

## D4 Fed-day gold from the surprise and the statement's rubric — leave-one-out, per-meeting Sharpe

Best cell `{'target': 'gld', 'features': 'surprise', 'state': 'highvol'}`: net Sharpe +1.34 on n = 66; best-of-search null 95th percentile +0.89; **p_family = 0.000**; survivors 6.

Survivors: {'target': 'gld', 'features': 'surprise', 'state': 'all'} +1.29; {'target': 'gld', 'features': 'surprise', 'state': 'highvol'} +1.34; {'target': 'gld', 'features': 'surprise', 'state': 'lowvol'} +1.34; {'target': 'gld', 'features': 'both', 'state': 'all'} +1.02; {'target': 'gld', 'features': 'both', 'state': 'highvol'} +1.28; {'target': 'gld', 'features': 'both', 'state': 'lowvol'} +1.13


A survivor here is a candidate for the forward log, not a signal: the registered rule is written by dated amendment and judged on data it has never seen.
