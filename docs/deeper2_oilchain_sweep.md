# Sweep — D5b gold after an oil shock, conditioned on whether rates/real yields rose afterwards — net Sharpe (sign +1 long gold)

Best cell: `{'h': 'f20', 'series': 'DFII10', 'rate_h': 20, 'rates': 'down', 'sign': 1}` with statistic +2.04; best-of-grid null over 200 draws: 95th percentile +1.58, **p_family = 0.005**

### series = DFII10, rate_h = 5, sign = -1

| rates \ h | f10 | f20 | f40 | f5 | f60 |
|---|---|---|---|---|---|
| any | -0.25 | -0.54 | -0.47 | -0.94 | -0.55 |
| down | -1.14 | -1.09 | -0.89 | -2.48 | -0.79 |
| up | +0.82 | +0.07 | -0.01 | +0.93 | -0.27 |

### series = DFII10, rate_h = 5, sign = 1

| rates \ h | f10 | f20 | f40 | f5 | f60 |
|---|---|---|---|---|---|
| any | -0.04 | +0.39 | +0.40 | +0.37 | +0.50 |
| down | +0.84 | +0.94 | +0.81 | +1.91** | +0.74 |
| up | -1.13 | -0.22 | -0.06 | -1.54 | +0.22 |

### series = DFII10, rate_h = 10, sign = -1

| rates \ h | f10 | f20 | f40 | f5 | f60 |
|---|---|---|---|---|---|
| any | -0.25 | -0.54 | -0.47 | -0.94 | -0.55 |
| down | -2.00 | -1.75 | -1.36 | -2.40 | -1.05 |
| up | +1.30 | +0.43 | +0.30 | +0.27 | -0.07 |

### series = DFII10, rate_h = 10, sign = 1

| rates \ h | f10 | f20 | f40 | f5 | f60 |
|---|---|---|---|---|---|
| any | -0.04 | +0.39 | +0.40 | +0.37 | +0.50 |
| down | +1.68** | +1.58 | +1.28 | +1.78** | +1.00 |
| up | -1.60 | -0.58 | -0.38 | -0.82 | +0.01 |

### series = DFII10, rate_h = 20, sign = -1

| rates \ h | f10 | f20 | f40 | f5 | f60 |
|---|---|---|---|---|---|
| any | -0.25 | -0.54 | -0.47 | -0.94 | -0.55 |
| down | -1.49 | -2.21 | -1.45 | -1.63 | -1.15 |
| up | +1.47 | +0.96 | +0.46 | -0.11 | +0.08 |

### series = DFII10, rate_h = 20, sign = 1

| rates \ h | f10 | f20 | f40 | f5 | f60 |
|---|---|---|---|---|---|
| any | -0.04 | +0.39 | +0.40 | +0.37 | +0.50 |
| down | +1.22 | +2.04** | +1.37 | +1.10 | +1.10 |
| up | -1.84 | -1.12 | -0.54 | -0.52 | -0.13 |

### series = DGS2, rate_h = 5, sign = -1

| rates \ h | f10 | f20 | f40 | f5 | f60 |
|---|---|---|---|---|---|
| any | -0.25 | -0.54 | -0.47 | -0.94 | -0.55 |
| down | -0.74 | -0.87 | -0.74 | -1.71 | -0.79 |
| up | +0.30 | -0.14 | -0.11 | -0.05 | -0.24 |

### series = DGS2, rate_h = 5, sign = 1

| rates \ h | f10 | f20 | f40 | f5 | f60 |
|---|---|---|---|---|---|
| any | -0.04 | +0.39 | +0.40 | +0.37 | +0.50 |
| down | +0.43 | +0.72 | +0.67 | +1.11 | +0.74 |
| up | -0.59 | -0.00 | +0.03 | -0.50 | +0.18 |

### series = DGS2, rate_h = 10, sign = -1

| rates \ h | f10 | f20 | f40 | f5 | f60 |
|---|---|---|---|---|---|
| any | -0.25 | -0.54 | -0.47 | -0.94 | -0.55 |
| down | -0.98 | -1.31 | -0.77 | -1.50 | -0.94 |
| up | +0.42 | +0.09 | -0.14 | -0.40 | -0.14 |

### series = DGS2, rate_h = 10, sign = 1

| rates \ h | f10 | f20 | f40 | f5 | f60 |
|---|---|---|---|---|---|
| any | -0.04 | +0.39 | +0.40 | +0.37 | +0.50 |
| down | +0.68 | +1.14 | +0.70 | +0.93 | +0.89 |
| up | -0.71 | -0.23 | +0.06 | -0.18 | +0.08 |

### series = DGS2, rate_h = 20, sign = -1

| rates \ h | f10 | f20 | f40 | f5 | f60 |
|---|---|---|---|---|---|
| any | -0.25 | -0.54 | -0.47 | -0.94 | -0.55 |
| down | -0.85 | -1.50 | -1.08 | -1.40 | -1.15 |
| up | +0.45 | +0.25 | +0.18 | -0.46 | +0.04 |

### series = DGS2, rate_h = 20, sign = 1

| rates \ h | f10 | f20 | f40 | f5 | f60 |
|---|---|---|---|---|---|
| any | -0.04 | +0.39 | +0.40 | +0.37 | +0.50 |
| down | +0.59 | +1.34 | +1.01 | +0.87 | +1.10 |
| up | -0.80 | -0.40 | -0.27 | -0.16 | -0.09 |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 4 — {'h': 'f5', 'series': 'DFII10', 'rate_h': 5, 'rates': 'down', 'sign': 1} +1.91; {'h': 'f5', 'series': 'DFII10', 'rate_h': 10, 'rates': 'down', 'sign': 1} +1.78; {'h': 'f10', 'series': 'DFII10', 'rate_h': 10, 'rates': 'down', 'sign': 1} +1.68; {'h': 'f20', 'series': 'DFII10', 'rate_h': 20, 'rates': 'down', 'sign': 1} +2.04

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
