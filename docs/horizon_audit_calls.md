# Horizon audit — the report's document-driven calls: the report day itself and the days after (rows 24/27/33, A, D7)

Event kind: **information**. 1,646 calls from report_backfill_97d9bf07dd2c_n5793.csv; sign = the call's direction; day 0 = the report date (the day the documents came out). Assets not in the price panel and skipped: none.

Returns are signed in the direction the original claim predicts and shown in basis points (100 bp = 1%). p = share of 1,000 time-shifts of the asset's returns with |t| at least as large. Family p = the same for the best cell of the group.

- **Day 0** (the event day): `calls on SPY` day 0: mean +6 bp, t +2.06, n 722, hit 53%; family p **0.245** (null 95th percentile of |t| 2.79). By era: 2009-14: +8 bp (n 107); 2015-19: +7 bp (n 195); 2020-21: +15 bp (n 132); 2022-26: +1 bp (n 288).
- **After** (days +1 … +5): `all calls, pooled` days +1..+3: mean +16 bp, t +3.56, n 1646, hit 57%; family p **0.034** (null 95th percentile of |t| 3.43). By era: 2009-14: +15 bp (n 263); 2015-19: +19 bp (n 421); 2020-21: +18 bp (n 263); 2022-26: +15 bp (n 699).
- **Before** (day −1, a check): `tier 2.0` day -1: mean -25 bp, t -3.30, n 223, hit 42%; family p **0.007** (null 95th percentile of |t| 2.72).
- **Label under the two-category rule: QUANT candidate**

| variant | n | day -1 | day 0 | day +1 | days +1..+2 | days +1..+3 | days +1..+5 |
|---|---|---|---|---|---|---|---|
| all calls, pooled | 1646 | +2 bp (t +0.8, p 0.401) | +2 bp (t +0.6, p 0.547) | +1 bp (t +0.3, p 0.767) | +11 bp (t +2.9, p 0.008)** | +16 bp (t +3.6, p 0.004)** | +15 bp (t +2.6, p 0.044)** |
| calls on GLD | 209 | -7 bp (t -0.9, p 0.401) | -4 bp (t -0.5, p 0.680) | +1 bp (t +0.2, p 0.846) | +7 bp (t +0.6, p 0.553) | +13 bp (t +0.9, p 0.430) | +17 bp (t +1.1, p 0.311) |
| calls on SPY | 722 | +9 bp (t +2.9, p 0.004)** | +6 bp (t +2.1, p 0.050) | +4 bp (t +1.4, p 0.187) | +10 bp (t +2.2, p 0.060) | +17 bp (t +2.9, p 0.022)** | +7 bp (t +1.0, p 0.500) |
| calls on TLT | 316 | -1 bp (t -0.3, p 0.760) | -8 bp (t -1.7, p 0.086) | +4 bp (t +0.8, p 0.455) | +9 bp (t +1.3, p 0.200) | +10 bp (t +1.2, p 0.266) | +11 bp (t +1.1, p 0.335) |
| calls on USO | 189 | -3 bp (t -0.2, p 0.832) | +3 bp (t +0.2, p 0.840) | -16 bp (t -1.1, p 0.281) | +25 bp (t +1.2, p 0.238) | +43 bp (t +1.7, p 0.110) | +68 bp (t +2.0, p 0.053) |
| calls on UUP | 210 | -1 bp (t -0.5, p 0.660) | +5 bp (t +1.6, p 0.107) | -1 bp (t -0.3, p 0.756) | +7 bp (t +1.7, p 0.102) | +5 bp (t +1.2, p 0.282) | -4 bp (t -0.8, p 0.486) |
| tier 2.0 | 223 | -25 bp (t -3.3, p 0.000)** | -10 bp (t -1.2, p 0.243) | -3 bp (t -0.4, p 0.622) | +4 bp (t +0.3, p 0.744) | +6 bp (t +0.4, p 0.677) | -9 bp (t -0.6, p 0.611) |
| tier 3.0 | 1404 | +6 bp (t +2.4, p 0.025)** | +4 bp (t +1.4, p 0.149) | +2 bp (t +0.7, p 0.493) | +12 bp (t +3.0, p 0.007)** | +17 bp (t +3.5, p 0.002)** | +17 bp (t +2.8, p 0.047)** |
