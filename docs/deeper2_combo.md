# Deeper test combo — 2026-11-05 20:54

Features: each factor's trailing 1-, 5- and 20-session change; target: gold's return over the NEXT h sessions; ridge refit every 250 sessions on the trailing window; null: gold time-shifted (the factors keep their own structure). 3,588 cells, 50 null draws (fewer than usual: the grid is large).

## D8 factor combinations → gold's next 1/5/20 sessions (walk-forward ridge, sign traded) — net Sharpe

Best cell `{'combo': ('cot_oil', 'macro2'), 'h': 20, 'train': 1000, 'ridge': 100.0}`: statistic +0.86 on n = 1987; null 95th percentile +0.98; **p_family = 0.120**; survivors 0.

## The twelve strongest combinations

| combination | h | train | ridge | net Sharpe | n |
|---|---|---|---|---|---|
| dollar+cot_oil+macro2 | 20 | 1000 | 100.0 | +0.86 | 1987 |
| cot_oil+macro2 | 20 | 1000 | 100.0 | +0.86 | 1987 |
| dollar | 20 | 1000 | 100.0 | +0.86 | 1987 |
| macro2 | 20 | 1000 | 100.0 | +0.85 | 1987 |
| dollar+macro2 | 20 | 1000 | 100.0 | +0.85 | 1987 |
| cot_oil | 20 | 1000 | 100.0 | +0.85 | 1987 |
| dollar+cot_oil | 20 | 1000 | 100.0 | +0.85 | 1987 |
| dollar | 20 | 1000 | 10.0 | +0.85 | 1987 |
| dollar+oil+cot_oil | 20 | 1000 | 100.0 | +0.85 | 1987 |
| oil | 20 | 1000 | 100.0 | +0.84 | 1987 |
| oil+cot_oil | 20 | 1000 | 100.0 | +0.84 | 1987 |
| dollar+oil | 20 | 1000 | 100.0 | +0.84 | 1987 |
