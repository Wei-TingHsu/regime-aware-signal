# Horizon audit — gold and the S&P around a sudden one-day S&P fall (D1b)

Event kind: **price move**. Positive = the asset rose.

Returns are signed in the direction the original claim predicts and shown in basis points (100 bp = 1%). p = share of 1,000 time-shifts of the asset's returns with |t| at least as large. Family p = the same for the best cell of the group.

- **Day 0** (the event day): `S&P falls ≥ 4.0% in one session → gold` day 0: mean +51 bp, t +1.16, n 43, hit 60%; family p **0.613** (null 95th percentile of |t| 2.67). By era: 2004-08: +62 bp (n 16); 2009-14: +189 bp (n 10).
- **After** (days +1 … +5): `S&P falls ≥ 1.5% in one session → S&P itself` days +1..+3: mean +35 bp, t +1.92, n 362, hit 59%; family p **0.876** (null 95th percentile of |t| 4.41). By era: 2004-08: +35 bp (n 71); 2009-14: +30 bp (n 108); 2015-19: +57 bp (n 57); 2020-21: +3 bp (n 42); 2022-26: +45 bp (n 84).
- **Before** (day −1, a check): `S&P falls ≥ 2.0% in one session → gold` day -1: mean +25 bp, t +2.48, n 214, hit 56%; family p **0.062** (null 95th percentile of |t| 2.57).
- **Label under the two-category rule: NEITHER**

| variant | n | day -1 | day 0 | day +1 | days +1..+2 | days +1..+3 | days +1..+5 |
|---|---|---|---|---|---|---|---|
| S&P falls ≥ 1.5% in one session → gold | 362 | +17 bp (t +2.4, p 0.030)** | -8 bp (t -0.8, p 0.475) | +3 bp (t +0.4, p 0.704) | +6 bp (t +0.5, p 0.719) | +12 bp (t +0.8, p 0.610) | +26 bp (t +1.4, p 0.504) |
| S&P falls ≥ 1.5% in one session → S&P itself | 362 | · | · | +20 bp (t +1.6, p 0.206) | +28 bp (t +1.9, p 0.225) | +35 bp (t +1.9, p 0.311) | +42 bp (t +1.9, p 0.469) |
| S&P falls ≥ 2.0% in one session → gold | 214 | +25 bp (t +2.5, p 0.021)** | -8 bp (t -0.5, p 0.630) | -10 bp (t -0.9, p 0.435) | +2 bp (t +0.1, p 0.929) | +10 bp (t +0.5, p 0.741) | +17 bp (t +0.6, p 0.732) |
| S&P falls ≥ 2.0% in one session → S&P itself | 214 | · | · | +30 bp (t +1.6, p 0.185) | +32 bp (t +1.4, p 0.333) | +41 bp (t +1.4, p 0.380) | +52 bp (t +1.6, p 0.452) |
| S&P falls ≥ 3.0% in one session → gold | 88 | +15 bp (t +0.9, p 0.409) | -3 bp (t -0.1, p 0.908) | -26 bp (t -1.1, p 0.310) | +3 bp (t +0.1, p 0.942) | +6 bp (t +0.1, p 0.912) | -1 bp (t -0.0, p 0.995) |
| S&P falls ≥ 3.0% in one session → S&P itself | 88 | · | · | +28 bp (t +0.8, p 0.453) | +29 bp (t +0.7, p 0.551) | +1 bp (t +0.0, p 0.991) | +40 bp (t +0.6, p 0.724) |
| S&P falls ≥ 4.0% in one session → gold | 43 | +10 bp (t +0.3, p 0.757) | +51 bp (t +1.2, p 0.264) | -33 bp (t -0.8, p 0.438) | +45 bp (t +0.7, p 0.520) | +48 bp (t +0.7, p 0.593) | +65 bp (t +0.7, p 0.633) |
| S&P falls ≥ 4.0% in one session → S&P itself | 43 | · | · | +53 bp (t +0.9, p 0.407) | +69 bp (t +1.0, p 0.404) | +48 bp (t +0.5, p 0.705) | +103 bp (t +1.0, p 0.507) |
