# Sweep — D7 keep only the calls a walk-forward ridge expects to pay — net Sharpe of the kept calls

Best cell: `{'train': 1000, 'ridge': 10.0, 'q': 0.0}` with statistic +0.28; best-of-grid null over 200 draws: 95th percentile +1.63, **p_family = 0.770**

### q = 0.0

| train \ ridge | 1.0 | 10.0 | 100.0 |
|---|---|---|---|
| 500 | -0.57 | -0.65 | -0.27 |
| 1000 | +0.16 | +0.28 | +0.11 |
| 2000 | +0.21 | +0.11 | +0.01 |

### q = 0.5

| train \ ridge | 1.0 | 10.0 | 100.0 |
|---|---|---|---|
| 500 | -0.47 | -0.51 | -0.36 |
| 1000 | +0.07 | -0.08 | -0.14 |
| 2000 | +0.18 | +0.04 | -0.10 |

### q = 0.75

| train \ ridge | 1.0 | 10.0 | 100.0 |
|---|---|---|---|
| 500 | -0.67 | -0.70 | -0.38 |
| 1000 | +0.02 | +0.15 | +0.23 |
| 2000 | +0.27 | +0.09 | +0.16 |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 0

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
