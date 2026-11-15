# Live news log (forward record)

Each row: a results release, a material company filing or a Fed statement seen live by `src/news_listener.py`, scored by the same readers as the backtest. Three clocks: published (as the source states), seen (this machine), scored. Prices are joined later.

| seen (New York) | seen (Singapore) | who | kind | first source | published → seen | seen → scored | score | title |
|---|---|---|---|---|---|---|---|---|
| 2026-11-15 08:16:04 | 2026-11-15 21:16:04 | AMD | results (DRILL) | AMD investor page | 1008065 s | 18 s | own stock 0.8, market 0.6, AI demand 0.9, vs prior guidance 0.6, new guidance 0.8, free cash flow 0.3 / revenue $13,377M (GAAP, up 45% YoY, up 16% QoQ); free cash flow None; guidance Q4 2026 revenue ~$17B +/-3% (~66% YoY growth, ~ | AMD Reports Third Quarter 2026 Financial Results |
