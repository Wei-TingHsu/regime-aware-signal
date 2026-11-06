# Fast states — do they carry information?

## k = 3

F1 forward: best `{'state': np.int64(2), 'asset': 'GLD', 'h': 20, 'sign': 1}` Sharpe +0.92 vs q95 +1.21, p_family 0.360, survivors 0.
F2 before slow-regime changes: state 1 excess -17.8 pts vs q95 14.0, p 0.000.
F3 Fed-day reaction by fast state: interaction p 0.732.
F4 favoured-asset map: stability +0.03, p 0.660.

## k = 4

F1 forward: best `{'state': np.int64(0), 'asset': 'SPY', 'h': 20, 'sign': 1}` Sharpe +1.04 vs q95 +1.24, p_family 0.273, survivors 0.
F2 before slow-regime changes: state 1 excess -13.3 pts vs q95 10.5, p 0.023.
F3 Fed-day reaction by fast state: interaction p 0.840.
F4 favoured-asset map: stability +0.30, p 0.207.

## k = 5

F1 forward: best `{'state': np.int64(4), 'asset': 'SPY', 'h': 10, 'sign': 1}` Sharpe +1.21 vs q95 +1.41, p_family 0.140, survivors 0.
F2 before slow-regime changes: state 2 excess -18.1 pts vs q95 9.7, p 0.000.
F3 Fed-day reaction by fast state: interaction p 0.576.
F4 favoured-asset map: stability +0.28, p 0.140.

## k = 6

F1 forward: best `{'state': np.int64(0), 'asset': 'SPY', 'h': 5, 'sign': 1}` Sharpe +1.46 vs q95 +1.41, p_family 0.027, survivors 1.
F2 before slow-regime changes: state 3 excess -9.4 pts vs q95 12.6, p 0.183.
F3 Fed-day reaction by fast state: interaction p 0.526.
F4 favoured-asset map: stability +0.30, p 0.160.

## k = 8

F1 forward: best `{'state': np.int64(1), 'asset': 'SPY', 'h': 10, 'sign': 1}` Sharpe +1.27 vs q95 +1.83, p_family 0.387, survivors 0.
F2 before slow-regime changes: state 3 excess -7.8 pts vs q95 6.7, p 0.030.
F3 Fed-day reaction by fast state: interaction p 0.390.
F4 favoured-asset map: stability +0.55, p 0.000.

