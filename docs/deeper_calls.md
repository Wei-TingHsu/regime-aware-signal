# Deeper test calls — 2026-11-05 19:01

1,646 calls (h 2) from report_backfill_97d9bf07dd2c_n5793.csv; features ['ess', 'w', 'n_docs', 'agreement', 'net_view', 'tier', 'regime', 'dominant_source', 'asset']; target = the call's own signed 2-session return; learner refit every 250 calls on the trailing window; `q` keeps the top share by predicted return (0 = all with positive prediction). Baseline: every call, net Sharpe +0.07.

## D7 keep only the calls a walk-forward ridge expects to pay — net Sharpe of the kept calls

Best cell `{'train': 1000, 'ridge': 10.0, 'q': 0.0}`: net Sharpe +0.28 on n = 612; best-of-search null 95th percentile +1.63; **p_family = 0.770**; survivors 0.


A survivor here is a candidate for the forward log, not a signal: the registered rule is written by dated amendment and judged on data it has never seen.
