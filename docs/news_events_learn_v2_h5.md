# Sweep — N1 learner → 5-session return after the event

Best cell: `{'train': 200, 'ridge': 100.0, 'h': 5}` with statistic +0.09; best-of-grid null over 200 draws: 95th percentile +0.73, **p_family = 0.590**

Plain rule 'long the session after a ≥ 4% fall', 5 sessions: Sharpe +0.73 on n 278.

### h = 5

| train \ ridge | 1.0 | 10.0 | 100.0 |
|---|---|---|---|
| 100 | -0.73 | -0.52 | -0.23 |
| 200 | -0.48 | -0.37 | +0.09 |
| 400 | -0.62 | -0.64 | -0.06 |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 0

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
