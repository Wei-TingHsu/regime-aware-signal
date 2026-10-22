# T-F window rules — GLD

*2026-10-23 02:04. 24 past episodes. Explained share = 1 − |residual| / |move|, reasons only (drift excluded), pre-episode sensitivities. R4 is chosen after seeing every window — an in-sample ceiling, shown so the gap to the usable rules is visible.*

**R5 (causal stop) beats R1 (full episode) in 83% of episodes → PASS**

| rule | median explained share | median window (sessions) |
|---|---|---|
| R1 full episode | 31% | 102 |
| R2 impulse (quarter-threshold) | 17% | 8 |
| R3 first half | 25% | 50 |
| R5 causal stop (patience 5) | 53% | 7 |
| R4 ceiling — after the fact, not a result | 71% | 11 |
