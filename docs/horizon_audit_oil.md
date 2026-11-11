# Horizon audit — gold around an oil shock (A3a, D5)

Event kind: **price move**. Shock dates from processed/oil_shocks.csv (the session the five-session oil rise crosses the threshold). Positive = gold rose.

Returns are signed in the direction the original claim predicts and shown in basis points (100 bp = 1%). p = share of 1,000 time-shifts of the asset's returns with |t| at least as large. Family p = the same for the best cell of the group.

- **Day 0** (the event day): `all oil shocks → gold` day 0: mean +31 bp, t +3.06, n 202, hit 60%; family p **0.009** (null 95th percentile of |t| 2.51). By era: 2004-08: +62 bp (n 44); 2009-14: +50 bp (n 42); 2015-19: +8 bp (n 45); 2020-21: +9 bp (n 21); 2022-26: +15 bp (n 50).
- **After** (days +1 … +5): `all oil shocks → gold` days +1..+5: mean +23 bp, t +1.28, n 202, hit 55%; family p **0.808** (null 95th percentile of |t| 3.24). By era: 2004-08: +43 bp (n 44); 2009-14: +19 bp (n 42); 2015-19: +2 bp (n 45); 2020-21: -7 bp (n 21); 2022-26: +40 bp (n 50).
- **Before** (day −1, a check): `oil +5–8% in five sessions → gold` day -1: mean +22 bp, t +2.63, n 120, hit 53%; family p **0.041** (null 95th percentile of |t| 2.55).
- **Label under the two-category rule: CONTEXT (same-day co-movement)**

| variant | n | day -1 | day 0 | day +1 | days +1..+2 | days +1..+3 | days +1..+5 |
|---|---|---|---|---|---|---|---|
| all oil shocks → gold | 202 | +19 bp (t +2.6, p 0.025)** | +31 bp (t +3.1, p 0.005)** | -6 bp (t -0.6, p 0.584) | -1 bp (t -0.1, p 0.946) | -3 bp (t -0.2, p 0.899) | +23 bp (t +1.3, p 0.424) |
| oil +5–8% in five sessions → gold | 120 | +22 bp (t +2.6, p 0.015)** | +19 bp (t +1.7, p 0.128) | -4 bp (t -0.3, p 0.749) | +10 bp (t +0.7, p 0.500) | -14 bp (t -0.8, p 0.507) | +17 bp (t +0.8, p 0.584) |
| oil +8–12% → gold | 69 | +10 bp (t +0.7, p 0.508) | +55 bp (t +2.9, p 0.004)** | -7 bp (t -0.3, p 0.730) | -6 bp (t -0.2, p 0.861) | +32 bp (t +1.2, p 0.272) | +38 bp (t +1.2, p 0.321) |
