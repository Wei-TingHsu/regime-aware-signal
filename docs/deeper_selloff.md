# Deeper test selloff — 2026-11-05 18:59

5,522 sessions 2004-11-19 → 2026-11-02; 3,780 cells (one filter at a time, plus eras); cost 10 bp round trip; cells under 30 events are ·.

## D1 long gold after the drawdown — net Sharpe

Best cell `{'thr': -0.06, 'look': 20, 'h': 5, 'delay': 3, 'filter': 'none', 'cost': 0.001}`: net Sharpe +4.23 on n = 34; best-of-search null 95th percentile +4.08; **p_family = 0.045**; survivors 2.

Survivors: {'thr': -0.06, 'look': 20, 'h': 5, 'delay': 3, 'filter': 'none', 'cost': 0.001} +4.23; {'thr': -0.06, 'look': 20, 'h': 5, 'delay': 3, 'filter': 'abundant', 'cost': 0.001} +4.23

## D1 short gold after the drawdown — net Sharpe

Best cell `{'thr': -0.04, 'look': 20, 'h': 5, 'delay': 0, 'filter': 'none', 'cost': 0.001}`: net Sharpe +0.11 on n = 49; best-of-search null 95th percentile +2.51; **p_family = 0.940**; survivors 0.

## The 5 Nov survivor on the path (−6% / look 20 / 15 sessions, long gold, 10 bp cost)

n 34, hit 56%, mean +1.65% per trade, net Sharpe +1.27, worst -9.1%, asymmetry 1.82.

A survivor here is a candidate for the forward log, not a signal: the registered rule is written by dated amendment and judged on data it has never seen.
