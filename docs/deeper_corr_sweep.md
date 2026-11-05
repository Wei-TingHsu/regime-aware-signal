# Sweep — D3 next-period GLD–SPY correlation from realised correlation (+ stress state): out-of-sample skill vs the long-run mean

Best cell: `{'win': 20, 'H': 20, 'state': False}` with statistic +0.26; best-of-grid null over 200 draws: 95th percentile +0.09, **p_family = 0.000**

### state = False

| win \ H | 20 | 40 | 60 |
|---|---|---|---|
| 20 | +0.26** | +0.21** | +0.15** |
| 40 | +0.23** | +0.17** | +0.13** |
| 60 | +0.19** | +0.14** | +0.10** |
| 120 | +0.13** | +0.10** | +0.07 |

### state = True

| win \ H | 20 | 40 | 60 |
|---|---|---|---|
| 20 | +0.23** | +0.18** | +0.10** |
| 40 | +0.19** | +0.14** | +0.07 |
| 60 | +0.14** | +0.10** | +0.03 |
| 120 | +0.07 | +0.06 | +0.01 |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 18 — {'win': 20, 'H': 20, 'state': False} +0.26; {'win': 20, 'H': 20, 'state': True} +0.23; {'win': 20, 'H': 40, 'state': False} +0.21; {'win': 20, 'H': 40, 'state': True} +0.18; {'win': 20, 'H': 60, 'state': False} +0.15; {'win': 20, 'H': 60, 'state': True} +0.10; {'win': 40, 'H': 20, 'state': False} +0.23; {'win': 40, 'H': 20, 'state': True} +0.19; {'win': 40, 'H': 40, 'state': False} +0.17; {'win': 40, 'H': 40, 'state': True} +0.14; {'win': 40, 'H': 60, 'state': False} +0.13; {'win': 60, 'H': 20, 'state': False} +0.19

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
