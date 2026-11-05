# Sweep — D4 Fed-day gold from the surprise and the statement's rubric — leave-one-out, per-meeting Sharpe

Best cell: `{'target': 'gld', 'features': 'surprise', 'state': 'highvol'}` with statistic +1.34; best-of-grid null over 200 draws: 95th percentile +0.89, **p_family = 0.000**

### state = all

| target \ features | both | rubric | surprise |
|---|---|---|---|
| gld | +1.02** | -0.39 | +1.29** |
| gld_2 | +0.31 | +0.31 | +0.39 |
| gld_next | +0.29 | +0.20 | +0.40 |

### state = highvol

| target \ features | both | rubric | surprise |
|---|---|---|---|
| gld | +1.28** | -0.17 | +1.34** |
| gld_2 | +0.43 | +0.43 | +0.23 |
| gld_next | -0.10 | -0.30 | +0.31 |

### state = lowvol

| target \ features | both | rubric | surprise |
|---|---|---|---|
| gld | +1.13** | -0.52 | +1.34** |
| gld_2 | +0.48 | +0.01 | +0.56 |
| gld_next | +0.21 | +0.31 | +0.32 |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 6 — {'target': 'gld', 'features': 'surprise', 'state': 'all'} +1.29; {'target': 'gld', 'features': 'surprise', 'state': 'highvol'} +1.34; {'target': 'gld', 'features': 'surprise', 'state': 'lowvol'} +1.34; {'target': 'gld', 'features': 'both', 'state': 'all'} +1.02; {'target': 'gld', 'features': 'both', 'state': 'highvol'} +1.28; {'target': 'gld', 'features': 'both', 'state': 'lowvol'} +1.13

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
