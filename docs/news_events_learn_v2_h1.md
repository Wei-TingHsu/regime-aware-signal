# Sweep — N1 learner → 1-session return after the event

Best cell: `{'train': 200, 'ridge': 100.0, 'h': 1}` with statistic +1.42; best-of-grid null over 200 draws: 95th percentile +1.53, **p_family = 0.075**

Plain rule 'long the session after a ≥ 4% fall', 1 sessions: Sharpe +1.87 on n 278.

### h = 1

| train \ ridge | 1.0 | 10.0 | 100.0 |
|---|---|---|---|
| 100 | +0.01 | +0.46 | +0.40 |
| 200 | +0.25 | +0.81 | +1.42 |
| 400 | -0.12 | +0.75 | +0.58 |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 0

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
