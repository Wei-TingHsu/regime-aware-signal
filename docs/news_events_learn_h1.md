# Sweep — N1 learner → 1-session return after the event

Best cell: `{'train': 200, 'ridge': 100.0, 'h': 1}` with statistic +2.12; best-of-grid null over 200 draws: 95th percentile +1.52, **p_family = 0.005**

Plain rule 'long the session after a ≥ 4% fall', 1 sessions: Sharpe +1.87 on n 278.

### h = 1

| train \ ridge | 1.0 | 10.0 | 100.0 |
|---|---|---|---|
| 100 | +1.30 | +0.49 | +0.58 |
| 200 | +1.16 | +1.00 | +2.12** |
| 400 | +1.37 | +0.83 | +1.81** |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 2 — {'train': 200, 'ridge': 100.0, 'h': 1} +2.12; {'train': 400, 'ridge': 100.0, 'h': 1} +1.81

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
