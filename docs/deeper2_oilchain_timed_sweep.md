# Sweep — D5c gold from session 6 (or 11) after an oil shock, conditioned on the rate move over the first 5 sessions — net Sharpe

Best cell: `{'series': 'DGS2', 'rates': 'down', 'window': 'gold_10_20', 'sign': 1}` with statistic +0.78; best-of-grid null over 200 draws: 95th percentile +1.43, **p_family = 0.905**

### series = DFII10, sign = -1

| rates \ window | gold_10_20 | gold_10_40 | gold_5_20 | gold_5_40 |
|---|---|---|---|---|
| any | -0.90 | -0.59 | -0.46 | -0.43 |
| down | -1.04 | -0.86 | -0.60 | -0.67 |
| up | -0.74 | -0.30 | -0.29 | -0.17 |

### series = DFII10, sign = 1

| rates \ window | gold_10_20 | gold_10_40 | gold_5_20 | gold_5_40 |
|---|---|---|---|---|
| any | +0.62 | +0.49 | +0.27 | +0.35 |
| down | +0.76 | +0.76 | +0.42 | +0.59 |
| up | +0.46 | +0.21 | +0.11 | +0.09 |

### series = DGS2, sign = -1

| rates \ window | gold_10_20 | gold_10_40 | gold_5_20 | gold_5_40 |
|---|---|---|---|---|
| any | -0.90 | -0.59 | -0.46 | -0.43 |
| down | -1.05 | -0.84 | -0.59 | -0.64 |
| up | -0.70 | -0.28 | -0.28 | -0.16 |

### series = DGS2, sign = 1

| rates \ window | gold_10_20 | gold_10_40 | gold_5_20 | gold_5_40 |
|---|---|---|---|---|
| any | +0.62 | +0.49 | +0.27 | +0.35 |
| down | +0.78 | +0.74 | +0.41 | +0.56 |
| up | +0.43 | +0.19 | +0.08 | +0.07 |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 0

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
