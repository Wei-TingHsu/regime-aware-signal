# Sweep — D2 gold on weekly liquidity change, traded only when the trailing link is 'on' — annualised net Sharpe

Best cell: `{'W': 78, 'bar': 2.5, 'mode': 'on'}` with statistic +0.93; best-of-grid null over 200 draws: 95th percentile +1.66, **p_family = 0.285**

### mode = always

| W \ bar | 1.0 | 1.5 | 2.0 | 2.5 |
|---|---|---|---|---|
| 52 | -0.03 | -0.03 | -0.03 | -0.03 |
| 78 | -0.03 | -0.03 | -0.03 | -0.03 |
| 104 | -0.03 | -0.03 | -0.03 | -0.03 |
| 156 | -0.03 | -0.03 | -0.03 | -0.03 |

### mode = off

| W \ bar | 1.0 | 1.5 | 2.0 | 2.5 |
|---|---|---|---|---|
| 52 | +0.01 | -0.01 | +0.01 | +0.02 |
| 78 | +0.03 | +0.09 | -0.11 | -0.14 |
| 104 | +0.09 | +0.04 | -0.07 | -0.13 |
| 156 | +0.08 | +0.05 | -0.21 | -0.06 |

### mode = on

| W \ bar | 1.0 | 1.5 | 2.0 | 2.5 |
|---|---|---|---|---|
| 52 | -0.03 | +0.00 | -0.11 | -0.65 |
| 78 | -0.27 | -0.55 | +0.06 | +0.93 |
| 104 | -0.35 | -0.41 | -0.17 | +0.22 |
| 156 | -0.34 | -0.35 | +0.29 | -0.73 |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 0

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
