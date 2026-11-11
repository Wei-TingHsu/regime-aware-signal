# Horizon audit — gold (and the S&P) around the day an S&P drawdown is completed (D1, T-L5b)

Event kind: **price move**. Events as in D1: the first session the S&P's rolling return crosses the threshold, one event per 2 × look sessions. Positive = the asset rose.

Returns are signed in the direction the original claim predicts and shown in basis points (100 bp = 1%). p = share of 1,000 time-shifts of the asset's returns with |t| at least as large. Family p = the same for the best cell of the group.

- **Day 0** (the event day): `S&P 20-session return crosses -4% → gold` day 0: mean -27 bp, t -1.17, n 50, hit 50%; family p **0.704** (null 95th percentile of |t| 2.60). By era: 2004-08: -18 bp (n 10); 2009-14: -68 bp (n 15); 2022-26: -58 bp (n 13).
- **After** (days +1 … +5): `S&P 10-session return crosses -4% → S&P itself` days +1..+5: mean +128 bp, t +3.12, n 67, hit 67%; family p **0.160** (null 95th percentile of |t| 3.63). By era: 2004-08: +253 bp (n 15); 2009-14: +148 bp (n 22); 2022-26: -82 bp (n 14).
- **Before** (day −1, a check): `S&P 20-session return crosses -6% → gold` day -1: mean +30 bp, t +1.46, n 34, hit 53%; family p **0.490** (null 95th percentile of |t| 2.74).
- **Label under the two-category rule: NEITHER**

| variant | n | day -1 | day 0 | day +1 | days +1..+2 | days +1..+3 | days +1..+5 |
|---|---|---|---|---|---|---|---|
| S&P 10-session return crosses -4% → gold | 68 | -0 bp (t -0.0, p 0.982) | -7 bp (t -0.4, p 0.730) | +2 bp (t +0.1, p 0.928) | +29 bp (t +1.1, p 0.324) | +30 bp (t +1.0, p 0.345) | +76 bp (t +2.3, p 0.046)** |
| S&P 10-session return crosses -4% → S&P itself | 68 | · | · | +46 bp (t +1.9, p 0.088) | +52 bp (t +1.7, p 0.124) | +57 bp (t +1.6, p 0.201) | +128 bp (t +3.1, p 0.024)** |
| S&P 10-session return crosses -6% → gold | 36 | +8 bp (t +0.4, p 0.730) | -22 bp (t -0.7, p 0.511) | +4 bp (t +0.2, p 0.848) | +48 bp (t +1.2, p 0.232) | +59 bp (t +1.6, p 0.135) | +116 bp (t +2.0, p 0.068) |
| S&P 10-session return crosses -6% → S&P itself | 36 | · | · | +39 bp (t +1.6, p 0.123) | -28 bp (t -0.7, p 0.566) | +53 bp (t +1.1, p 0.366) | +61 bp (t +1.4, p 0.276) |
| S&P 20-session return crosses -4% → gold | 50 | -10 bp (t -0.5, p 0.618) | -27 bp (t -1.2, p 0.267) | -22 bp (t -1.0, p 0.291) | -7 bp (t -0.2, p 0.805) | +6 bp (t +0.2, p 0.860) | +40 bp (t +1.0, p 0.372) |
| S&P 20-session return crosses -4% → S&P itself | 50 | · | · | -2 bp (t -0.1, p 0.927) | -10 bp (t -0.3, p 0.771) | +38 bp (t +1.3, p 0.279) | +55 bp (t +1.4, p 0.265) |
| S&P 20-session return crosses -6% → gold | 34 | +30 bp (t +1.5, p 0.166) | +9 bp (t +0.3, p 0.761) | -11 bp (t -0.4, p 0.678) | +12 bp (t +0.3, p 0.777) | +71 bp (t +1.9, p 0.073) | +142 bp (t +2.2, p 0.047)** |
| S&P 20-session return crosses -6% → S&P itself | 34 | · | · | +24 bp (t +1.0, p 0.364) | +19 bp (t +0.4, p 0.683) | +100 bp (t +2.5, p 0.026)** | +95 bp (t +1.7, p 0.163) |
