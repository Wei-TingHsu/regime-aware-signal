# Sweep — T-A by era × window — median out-of-sample R² (GLD)

Best cell: `{'W': 504, 'era': '2015-19'}` with statistic 0.339; best-of-grid null over 100 draws: 95th percentile -0.020, **p_family = 0.000**

| era \ W | 252 | 504 | 756 | 1008 |
|---|---|---|---|---|
| 2004-08 | 0.312** | 0.293** | · | · |
| 2009-14 | 0.063** | 0.114** | 0.134** | 0.143** |
| 2015-19 | 0.284** | 0.339** | 0.324** | 0.287** |
| 2020-21 | 0.157** | 0.138** | 0.281** | 0.196** |
| 2022-26 | 0.172** | 0.116** | 0.180** | 0.129** |
| all | 0.177** | 0.158** | 0.215** | 0.177** |

Bold-marked (**) cells clear the best-of-sweep null's 95th percentile. Per-cell n and local p in the JSON.

Survivors (statistic above the null's 95th percentile): 22 — {'W': 252, 'era': 'all'} 0.177; {'W': 252, 'era': '2004-08'} 0.312; {'W': 252, 'era': '2009-14'} 0.063; {'W': 252, 'era': '2015-19'} 0.284; {'W': 252, 'era': '2020-21'} 0.157; {'W': 252, 'era': '2022-26'} 0.172; {'W': 504, 'era': 'all'} 0.158; {'W': 504, 'era': '2004-08'} 0.293; {'W': 504, 'era': '2009-14'} 0.114; {'W': 504, 'era': '2015-19'} 0.339; {'W': 504, 'era': '2020-21'} 0.138; {'W': 504, 'era': '2022-26'} 0.116

The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated amendment, never by this table.
