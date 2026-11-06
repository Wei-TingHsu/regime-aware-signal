# Deeper test selloff — 2026-11-06 12:33

5,524 sessions 2004-11-19 → 2026-11-05; 3,780 cells (one filter at a time, plus eras); cost 10 bp round trip; cells under 30 events are ·.

## D1 long gold after the drawdown — net Sharpe

Best cell `{'thr': -0.06, 'look': 20, 'h': 5, 'delay': 1, 'filter': 'none', 'cost': 0.001}`: net Sharpe +3.46 on n = 34; best-of-search null 95th percentile +4.23; **p_family = 0.140**; survivors 0.

## D1 short gold after the drawdown — net Sharpe

Best cell `{'thr': -0.04, 'look': 10, 'h': 15, 'delay': 1, 'filter': 'gold_up', 'cost': 0.001}`: net Sharpe -0.18 on n = 32; best-of-search null 95th percentile +2.39; **p_family = 0.970**; survivors 0.

## The 5 Nov survivor on the path (−6% / look 20 / 15 sessions, long gold, 10 bp cost)

n 34, hit 74%, mean +1.94% per trade, net Sharpe +1.55, worst -11.0%, asymmetry 0.93.

A survivor here is a candidate for the forward log, not a signal: the registered rule is written by dated amendment and judged on data it has never seen.
