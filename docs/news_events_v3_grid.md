# N1 v3 — does a contradicting official document in the window raise the reversal rate?

Statistic: reversal rate of events WITH a contradicting document in the window minus the rate WITHOUT, in percentage points (each side n ≥ 20). 'Contradicting' = max over documents in the window of (−event sign × the document's equity implication) ≥ cutoff. Null: forward outcomes shuffled among the same index-and-direction events, best cell of the whole grid, 300 draws.

## SOX fall

301 valid cells. Best cell `{'index': 'SOX', 'sign': -1, 'family': 'fed', 'cutoff': 0.1, 'window': 7, 'h': 5}`: gap **+22.6 points** (n with 45, without 185); best-of-grid null 95th percentile +32.6; **p_family 0.443**; survivors 0.
Best cell by era (gap, n with/without): 2009–2014: +4 (n 8/17); 2015–2019: +33 (n 5/15); 2020–2021: +2 (n 10/12); 2022–2026: +38 (n 20/45).

## SOX rise

440 valid cells. Best cell `{'index': 'SOX', 'sign': 1, 'family': 'labour', 'cutoff': 0.5, 'window': 7, 'h': 5}`: gap **+27.0 points** (n with 26, without 191); best-of-grid null 95th percentile +32.9; **p_family 0.267**; survivors 0.
Best cell by era (gap, n with/without): 2004–2008: +17 (n 6/16); 2009–2014: +32 (n 9/26); 2022–2026: +45 (n 7/54).

## SPX fall

16 valid cells. Best cell `{'index': 'SPX', 'sign': -1, 'family': 'all', 'cutoff': 0.1, 'window': 7, 'h': 3}`: gap **+4.8 points** (n with 20, without 29); best-of-grid null 95th percentile +33.6; **p_family 0.743**; survivors 0.
Best cell by era (gap, n with/without): 2004–2008: -15 (n 5/11).

## SPX rise

Not testable: no cell reaches 20 events on both sides.

