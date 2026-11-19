# C: measured trading cost of the results rule, Interactive Brokers

Trade: own stock, enter 1 min after the SEC stamp, hold 60 min; 359 past trades with Nasdaq quotes at both ends. Cost of one round trip = half the bid-ask spread going in + half going out + IBKR Pro Fixed commission (USD 0.005 per share, at least USD 1, at most 1%, both orders) + SEC fee on the sale, for a trade of US$10,000. In bp (1 bp = 0.01%).

| | median | average | three in four trades below | nine in ten below |
|---|---|---|---|---|
| spread when entering | 22.3 | 32.7 | 38.6 | 69.4 |
| spread when leaving | 14.3 | 21.1 | 24.5 | 48.5 |
| spread cost of the round trip | 19.1 | 26.9 | 31.7 | 51.5 |
| commission and fee | 2.2 | 2.3 | 2.2 | 2.2 |
| TOTAL cost | 21.3 | 29.2 | 34.2 | 54.1 |

| rule | trades | before cost | cost (average) | after cost | t after cost | right on, after cost |
|---|---|---|---|---|---|---|
| every score, one unit | 359 | +64.8 bp | 29.2 bp | +35.5 bp | +1.93 | 54% |
| only scores of 0.8 or more | 132 | +132.8 bp | 29.0 bp | +103.8 bp | +3.13 | 60% |

Limits: these are Nasdaq's own best bid and ask; IBKR routes to the best of all exchanges, so the true spread is at most this. A quote shows the price for a small size; a large order moves the price further. Outside regular hours IBKR accepts limit orders only, so an order may not fill.
