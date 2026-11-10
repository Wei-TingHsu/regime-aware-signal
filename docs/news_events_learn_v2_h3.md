# Sweep — N1 learner → 3-session return after the event

Best cell: `{'train': 100, 'ridge': 100.0, 'h': 3}` with statistic -0.56; best-of-grid null over 200 draws: 95th percentile +0.90, **p_family = 0.975**

Plain rule 'long the session after a ≥ 4% fall', 3 sessions: Sharpe +0.63 on n 278.

### h = 3

| train \ ridge | 1.0 | 10.0 | 100.0 |
|---|---|---|---|
| 100 | -0.62 | -1.16 | -0.56 |
| 200 | -0.95 | -0.99 | -0.88 |
| 400 | -1.12 | -1.17 | -0.72 |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 0

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
