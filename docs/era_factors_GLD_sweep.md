# Sweep — T-A by era × window — median out-of-sample R² (GLD)

Best cell: `{'W': 1008, 'era': '2015-19'}` with statistic 0.437; best-of-grid null over 100 draws: 95th percentile -0.007, **p_family = 0.000**

| era \ W | 252 | 504 | 756 | 1008 |
|---|---|---|---|---|
| 2015-19 | 0.337** | 0.374** | 0.341** | 0.437** |
| 2020-21 | 0.170** | 0.204** | 0.177** | 0.190** |
| 2022-26 | 0.188** | 0.151** | 0.181** | 0.138** |
| all | 0.242** | 0.187** | 0.212** | 0.191** |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 16 — {'W': 252, 'era': 'all'} 0.242; {'W': 252, 'era': '2015-19'} 0.337; {'W': 252, 'era': '2020-21'} 0.170; {'W': 252, 'era': '2022-26'} 0.188; {'W': 504, 'era': 'all'} 0.187; {'W': 504, 'era': '2015-19'} 0.374; {'W': 504, 'era': '2020-21'} 0.204; {'W': 504, 'era': '2022-26'} 0.151; {'W': 756, 'era': 'all'} 0.212; {'W': 756, 'era': '2015-19'} 0.341; {'W': 756, 'era': '2020-21'} 0.177; {'W': 756, 'era': '2022-26'} 0.181

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
