# Sweep — P1 by era x correlation window x state lag (|stress − abundant| gap)

Best cell: `{'era': '2009-14', 'win': 10, 'lag': 0}` with statistic 0.344; best-of-grid null over 200 draws: 95th percentile 0.510, **p_family = 0.350**

### lag = 0

| era \ win | 10 | 20 | 40 | 60 |
|---|---|---|---|---|
| 2004-08 | 0.067 | 0.035 | 0.096 | 0.220 |
| 2009-14 | 0.344 | 0.337 | 0.340 | 0.321 |
| 2015-19 | 0.041 | 0.103 | 0.019 | 0.026 |
| 2020-21 | 0.077 | 0.041 | 0.032 | 0.003 |
| 2022-26 | 0.109 | 0.207 | 0.167 | 0.107 |
| all | 0.010 | 0.007 | 0.004 | 0.013 |

### lag = 5

| era \ win | 10 | 20 | 40 | 60 |
|---|---|---|---|---|
| 2004-08 | 0.123 | 0.073 | 0.065 | 0.195 |
| 2009-14 | 0.327 | 0.332 | 0.337 | 0.321 |
| 2015-19 | 0.061 | 0.053 | 0.032 | 0.031 |
| 2020-21 | 0.046 | 0.046 | 0.024 | 0.001 |
| 2022-26 | 0.042 | 0.144 | 0.171 | 0.119 |
| all | 0.007 | 0.002 | 0.001 | 0.004 |

### lag = 10

| era \ win | 10 | 20 | 40 | 60 |
|---|---|---|---|---|
| 2004-08 | 0.181 | 0.117 | 0.029 | 0.166 |
| 2009-14 | 0.266 | 0.295 | 0.316 | 0.312 |
| 2015-19 | 0.109 | 0.023 | 0.040 | 0.037 |
| 2020-21 | 0.007 | 0.045 | 0.004 | 0.000 |
| 2022-26 | 0.009 | 0.089 | 0.165 | 0.125 |
| all | 0.005 | 0.012 | 0.007 | 0.008 |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 0

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
