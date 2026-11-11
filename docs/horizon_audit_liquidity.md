# Horizon audit — gold around a large daily change in the Fed's reverse-repo balance (D2c)

Event kind: **information**. Sign: liquidity ADDED (money leaving the facility) predicts gold UP. The balance is published the same evening, so day 0 is the day of the change, known after the close.

Returns are signed in the direction the original claim predicts and shown in basis points (100 bp = 1%). p = share of 1,000 time-shifts of the asset's returns with |t| at least as large. Family p = the same for the best cell of the group.

- **Day 0** (the event day): `reverse-repo balance change beyond 1.5 sd → gold` day 0: mean +10 bp, t +1.60, n 273, hit 52%; family p **0.231** (null 95th percentile of |t| 2.35). By era: 2009-14: +11 bp (n 17); 2015-19: -0 bp (n 107); 2020-21: +42 bp (n 55); 2022-26: +2 bp (n 94).
- **After** (days +1 … +5): `reverse-repo balance change beyond 1.5 sd → gold` day +1: mean +7 bp, t +1.10, n 273, hit 51%; family p **0.838** (null 95th percentile of |t| 2.52). By era: 2009-14: +31 bp (n 17); 2015-19: +5 bp (n 107); 2020-21: +9 bp (n 55); 2022-26: +4 bp (n 94).
- **Before** (day −1, a check): `reverse-repo balance change beyond 0.5 sd → gold` day -1: mean +4 bp, t +1.22, n 1100, hit 53%; family p **0.446** (null 95th percentile of |t| 2.30).
- **Label under the two-category rule: NEITHER**

| variant | n | day -1 | day 0 | day +1 | days +1..+2 | days +1..+3 | days +1..+5 |
|---|---|---|---|---|---|---|---|
| reverse-repo balance change beyond 0.5 sd → gold | 1100 | +4 bp (t +1.2, p 0.226) | +2 bp (t +0.8, p 0.432) | -0 bp (t -0.1, p 0.916) | -1 bp (t -0.2, p 0.846) | +1 bp (t +0.2, p 0.791) | +2 bp (t +0.4, p 0.684) |
| reverse-repo balance change beyond 1.0 sd → gold | 529 | +2 bp (t +0.5, p 0.570) | +5 bp (t +1.0, p 0.306) | +2 bp (t +0.5, p 0.641) | -0 bp (t -0.0, p 0.977) | -0 bp (t -0.0, p 0.974) | -1 bp (t -0.1, p 0.934) |
| reverse-repo balance change beyond 1.5 sd → gold | 273 | +5 bp (t +0.9, p 0.379) | +10 bp (t +1.6, p 0.101) | +7 bp (t +1.1, p 0.271) | +3 bp (t +0.4, p 0.687) | +6 bp (t +0.5, p 0.544) | -7 bp (t -0.5, p 0.540) |
