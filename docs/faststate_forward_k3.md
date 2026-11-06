# Sweep — F1 fast state (k=3) → next sessions, net Sharpe

Best cell: `{'state': np.int64(2), 'asset': 'GLD', 'h': 20, 'sign': 1}` with statistic +0.92; best-of-grid null over 150 draws: 95th percentile +1.21, **p_family = 0.360**

### asset = GLD, sign = -1

| state \ h | 5 | 10 | 20 |
|---|---|---|---|
| 0 | -0.65 | -0.50 | -0.48 |
| 1 | -0.72 | -0.60 | -0.45 |
| 2 | -0.99 | -0.84 | -1.07 |

### asset = GLD, sign = 1

| state \ h | 5 | 10 | 20 |
|---|---|---|---|
| 0 | +0.04 | +0.18 | +0.31 |
| 1 | +0.07 | +0.28 | +0.29 |
| 2 | +0.47 | +0.55 | +0.92 |

### asset = SPY, sign = -1

| state \ h | 5 | 10 | 20 |
|---|---|---|---|
| 0 | -1.18 | -1.09 | -0.99 |
| 1 | -1.52 | -1.24 | -1.06 |
| 2 | -0.32 | -0.55 | -0.72 |

### asset = SPY, sign = 1

| state \ h | 5 | 10 | 20 |
|---|---|---|---|
| 0 | +0.53 | +0.75 | +0.82 |
| 1 | +0.79 | +0.86 | +0.87 |
| 2 | -0.12 | +0.33 | +0.60 |

### asset = TLT, sign = -1

| state \ h | 5 | 10 | 20 |
|---|---|---|---|
| 0 | -0.72 | -0.48 | -0.32 |
| 1 | -0.33 | -0.19 | -0.11 |
| 2 | -0.87 | -0.79 | -0.69 |

### asset = TLT, sign = 1

| state \ h | 5 | 10 | 20 |
|---|---|---|---|
| 0 | -0.01 | +0.09 | +0.13 |
| 1 | -0.44 | -0.20 | -0.08 |
| 2 | +0.24 | +0.45 | +0.52 |

### asset = USO, sign = -1

| state \ h | 5 | 10 | 20 |
|---|---|---|---|
| 0 | +0.17 | +0.17 | +0.12 |
| 1 | -0.41 | -0.24 | -0.14 |
| 2 | +0.70 | +0.62 | +0.54 |

### asset = USO, sign = 1

| state \ h | 5 | 10 | 20 |
|---|---|---|---|
| 0 | -0.47 | -0.31 | -0.19 |
| 1 | +0.11 | +0.10 | +0.07 |
| 2 | -0.88 | -0.72 | -0.58 |

### asset = UUP, sign = -1

| state \ h | 5 | 10 | 20 |
|---|---|---|---|
| 0 | -0.66 | -0.41 | -0.17 |
| 1 | -1.24 | -0.76 | -0.58 |
| 2 | -1.08 | -1.05 | -1.05 |

### asset = UUP, sign = 1

| state \ h | 5 | 10 | 20 |
|---|---|---|---|
| 0 | -0.69 | -0.26 | -0.17 |
| 1 | -0.30 | -0.02 | +0.19 |
| 2 | -0.10 | +0.41 | +0.70 |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 0

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
