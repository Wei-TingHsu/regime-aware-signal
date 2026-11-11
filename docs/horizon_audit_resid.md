# Horizon audit — after a large unexplained move, does the asset continue (+) or reverse (−) over the next 1–5 sessions (T-H)

Event kind: **price move**. Sign: the direction of the unexplained move, so a positive mean = continuation and a negative mean = reversal. Day 0 is the move itself and is not measured.

Returns are signed in the direction the original claim predicts and shown in basis points (100 bp = 1%). p = share of 1,000 time-shifts of the asset's returns with |t| at least as large. Family p = the same for the best cell of the group.

- **Day 0** (the event day): not measured. By era: -.
- **After** (days +1 … +5): `SPY: unexplained move over 20 session(s) beyond 1.5 sd` days +1..+5: mean -55 bp, t -4.37, n 731, hit 45%; family p **0.106** (null 95th percentile of |t| 4.87). By era: 2004-08: -47 bp (n 74); 2009-14: -86 bp (n 184); 2015-19: -32 bp (n 202); 2020-21: -97 bp (n 53); 2022-26: -45 bp (n 218).
- **Before** (day −1, a check): not measured.
- **Label under the two-category rule: NEITHER**

| variant | n | day -1 | day 0 | day +1 | days +1..+2 | days +1..+3 | days +1..+5 |
|---|---|---|---|---|---|---|---|
| GLD: unexplained move over 1 session(s) beyond 1.5 sd | 292 | · | · | -9 bp (t -1.2, p 0.275) | -9 bp (t -0.8, p 0.435) | -13 bp (t -1.0, p 0.342) | -8 bp (t -0.5, p 0.626) |
| GLD: unexplained move over 5 session(s) beyond 1.5 sd | 360 | · | · | +1 bp (t +0.1, p 0.909) | -5 bp (t -0.5, p 0.677) | -14 bp (t -1.1, p 0.423) | -29 bp (t -1.9, p 0.201) |
| GLD: unexplained move over 20 session(s) beyond 1.5 sd | 398 | · | · | -10 bp (t -1.6, p 0.087) | -17 bp (t -1.8, p 0.135) | -23 bp (t -2.1, p 0.143) | -37 bp (t -2.8, p 0.103) |
| SLV: unexplained move over 1 session(s) beyond 1.5 sd | 300 | · | · | -1 bp (t -0.0, p 0.957) | +1 bp (t +0.1, p 0.946) | -25 bp (t -0.9, p 0.382) | -35 bp (t -1.0, p 0.322) |
| SLV: unexplained move over 5 session(s) beyond 1.5 sd | 372 | · | · | -3 bp (t -0.2, p 0.857) | -6 bp (t -0.3, p 0.839) | -30 bp (t -1.1, p 0.460) | -69 bp (t -2.1, p 0.209) |
| SLV: unexplained move over 20 session(s) beyond 1.5 sd | 403 | · | · | +1 bp (t +0.1, p 0.937) | -7 bp (t -0.3, p 0.799) | -7 bp (t -0.3, p 0.842) | -2 bp (t -0.1, p 0.971) |
| USO: unexplained move over 1 session(s) beyond 1.5 sd | 184 | · | · | -8 bp (t -0.2, p 0.797) | +13 bp (t +0.3, p 0.766) | -22 bp (t -0.4, p 0.647) | +53 bp (t +0.8, p 0.309) |
| USO: unexplained move over 5 session(s) beyond 1.5 sd | 283 | · | · | +21 bp (t +0.9, p 0.337) | +20 bp (t +0.6, p 0.597) | +25 bp (t +0.6, p 0.615) | +114 bp (t +1.9, p 0.133) |
| USO: unexplained move over 20 session(s) beyond 1.5 sd | 337 | · | · | +9 bp (t +0.4, p 0.667) | +18 bp (t +0.6, p 0.614) | +31 bp (t +0.9, p 0.543) | +93 bp (t +1.9, p 0.290) |
| SPY: unexplained move over 1 session(s) beyond 1.5 sd | 492 | · | · | -8 bp (t -0.9, p 0.383) | -21 bp (t -1.7, p 0.085) | -30 bp (t -2.1, p 0.032)** | -34 bp (t -1.9, p 0.051) |
| SPY: unexplained move over 5 session(s) beyond 1.5 sd | 575 | · | · | -18 bp (t -2.0, p 0.034)** | -28 bp (t -2.6, p 0.041)** | -32 bp (t -2.4, p 0.096) | -52 bp (t -3.1, p 0.062) |
| SPY: unexplained move over 20 session(s) beyond 1.5 sd | 731 | · | · | -11 bp (t -1.5, p 0.130) | -23 bp (t -2.4, p 0.078) | -31 bp (t -2.7, p 0.105) | -55 bp (t -4.4, p 0.036)** |
| NVDA: unexplained move over 1 session(s) beyond 1.5 sd | 471 | · | · | -10 bp (t -0.6, p 0.559) | +12 bp (t +0.5, p 0.581) | -6 bp (t -0.2, p 0.831) | -0 bp (t -0.0, p 1.000) |
| NVDA: unexplained move over 5 session(s) beyond 1.5 sd | 565 | · | · | -39 bp (t -2.6, p 0.007)** | -51 bp (t -2.7, p 0.023)** | -64 bp (t -2.8, p 0.040)** | -113 bp (t -3.7, p 0.012)** |
| NVDA: unexplained move over 20 session(s) beyond 1.5 sd | 657 | · | · | +1 bp (t +0.1, p 0.940) | +16 bp (t +0.8, p 0.580) | +17 bp (t +0.7, p 0.669) | +19 bp (t +0.6, p 0.763) |
