# Horizon audit — the history tables' events — Fed decision days (H1), dollar jumps and drops (H3), 2-year yield shocks (H4), regime changes (H5) — on five markets

Event kind: **price move**. Events rebuilt by the history-table code itself. H1 is signed by the 2-year yield's move that day (yield up predicts the market down); the others are unsigned (positive = the market rose). H1 is an information event; it is grouped here with the price-move tables, so read its rows with the `fomc` audit.

Returns are signed in the direction the original claim predicts and shown in basis points (100 bp = 1%). p = share of 1,000 time-shifts of the asset's returns with |t| at least as large. Family p = the same for the best cell of the group.

- **Day 0** (the event day): `H1 → UUP` day 0: mean -42 bp, t -8.68, n 115, hit 17%; family p **0.000** (null 95th percentile of |t| 2.90). By era: 2009-14: -38 bp (n 27); 2015-19: -42 bp (n 37); 2020-21: -49 bp (n 13); 2022-26: -44 bp (n 38).
- **After** (days +1 … +5): `H4dn → USO` day +1: mean -141 bp, t -3.14, n 30, hit 27%; family p **0.122** (null 95th percentile of |t| 3.43). By era: 2004-08: -175 bp (n 12); 2022-26: -153 bp (n 12).
- **Before** (day −1, a check): `H4up → TLT` day -1: mean -46 bp, t -2.80, n 37, hit 27%; family p **0.087** (null 95th percentile of |t| 3.00).
- **Label under the two-category rule: CONTEXT (same-day co-movement)**

| variant | n | day -1 | day 0 | day +1 | days +1..+2 | days +1..+3 | days +1..+5 |
|---|---|---|---|---|---|---|---|
| H1 → SPY | 115 | +1 bp (t +0.0, p 0.970) | +14 bp (t +0.9, p 0.351) | +16 bp (t +1.0, p 0.317) | +17 bp (t +1.0, p 0.345) | +27 bp (t +1.2, p 0.243) | +15 bp (t +0.6, p 0.529) |
| H1 → TLT | 115 | +6 bp (t +0.7, p 0.487) | +48 bp (t +4.8, p 0.000)** | +1 bp (t +0.1, p 0.938) | +3 bp (t +0.2, p 0.890) | +3 bp (t +0.2, p 0.860) | +25 bp (t +1.3, p 0.183) |
| H1 → GLD | 115 | +4 bp (t +0.5, p 0.659) | +74 bp (t +7.4, p 0.000)** | +26 bp (t +1.9, p 0.046)** | +31 bp (t +1.6, p 0.119) | +34 bp (t +1.4, p 0.150) | +44 bp (t +1.7, p 0.086) |
| H1 → UUP | 115 | +10 bp (t +2.1, p 0.031)** | -42 bp (t -8.7, p 0.000)** | -3 bp (t -0.5, p 0.595) | -3 bp (t -0.4, p 0.697) | -6 bp (t -0.7, p 0.515) | -8 bp (t -0.7, p 0.445) |
| H1 → USO | 115 | -26 bp (t -1.2, p 0.264) | +7 bp (t +0.3, p 0.759) | +8 bp (t +0.4, p 0.724) | -5 bp (t -0.1, p 0.878) | -5 bp (t -0.1, p 0.910) | -55 bp (t -1.0, p 0.351) |
| H4up → SPY | 56 | +28 bp (t +1.7, p 0.114) | +0 bp (t +0.0, p 0.986) | -4 bp (t -0.3, p 0.767) | +16 bp (t +0.9, p 0.410) | +13 bp (t +0.5, p 0.648) | -11 bp (t -0.3, p 0.817) |
| H4up → TLT | 37 | -46 bp (t -2.8, p 0.007)** | -84 bp (t -5.9, p 0.000)** | +11 bp (t +0.7, p 0.507) | -12 bp (t -0.6, p 0.585) | -34 bp (t -1.5, p 0.146) | -25 bp (t -1.0, p 0.348) |
| H4dn → SPY | 60 | +2 bp (t +0.1, p 0.933) | -95 bp (t -3.7, p 0.000)** | -13 bp (t -0.5, p 0.618) | +1 bp (t +0.0, p 0.987) | +5 bp (t +0.2, p 0.909) | +48 bp (t +1.3, p 0.326) |
| H4dn → TLT | 38 | +28 bp (t +2.2, p 0.038)** | +105 bp (t +5.7, p 0.000)** | +8 bp (t +0.6, p 0.567) | -41 bp (t -2.0, p 0.050) | -9 bp (t -0.3, p 0.753) | -32 bp (t -1.0, p 0.310) |
| H4dn → GLD | 31 | +18 bp (t +0.9, p 0.402) | +90 bp (t +2.8, p 0.008)** | -37 bp (t -1.7, p 0.096) | -26 bp (t -0.5, p 0.610) | +13 bp (t +0.3, p 0.788) | +100 bp (t +1.7, p 0.114) |
| H4dn → UUP | 30 | -11 bp (t -0.9, p 0.363) | -35 bp (t -2.6, p 0.003)** | +10 bp (t +1.0, p 0.330) | +16 bp (t +1.1, p 0.293) | +9 bp (t +0.6, p 0.561) | +9 bp (t +0.4, p 0.712) |
| H4dn → USO | 30 | -35 bp (t -0.7, p 0.524) | -19 bp (t -0.3, p 0.770) | -141 bp (t -3.1, p 0.002)** | -204 bp (t -2.7, p 0.004)** | -137 bp (t -1.6, p 0.115) | -107 bp (t -0.9, p 0.373) |
