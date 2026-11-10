# Sweep — N1 learner → 3-session return after the event

Best cell: `{'train': 400, 'ridge': 100.0, 'h': 3}` with statistic -0.38; best-of-grid null over 200 draws: 95th percentile +0.77, **p_family = 0.920**

Plain rule 'long the session after a ≥ 4% fall', 3 sessions: Sharpe +0.63 on n 278.

### h = 3

| train \ ridge | 1.0 | 10.0 | 100.0 |
|---|---|---|---|
| 100 | -0.72 | -0.93 | -0.38 |
| 200 | -0.50 | -0.54 | -0.67 |
| 400 | -0.46 | -0.61 | -0.38 |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 0

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
