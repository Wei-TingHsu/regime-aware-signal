# ET-1: company announcements by type -- does Claude's score tell where the company's own stock goes next?

Registered in TRACK 3.89 before running. Events of the twelve US filers from May 2018, material 0.2 or more, routine filings left out. Trade = sign(score) x the stock's return after the SEC stamp, in bp, before cost. Signals: `own_stock` (Claude's reading for the share) and `neg_uncertainty` (sell when the event raises uncertainty), each kept only for events of material 0.2+, 0.3+ or 0.5+. Windows: 1 or 5 minutes after the stamp held 15, 30 or 60 minutes or to the next 09:35; or entered at the next regular session and held 30 or 60 minutes, to 16:00, or to the 16:00 after. Each type is one family: p = how often shuffled scores produce a best cell as strong as the real best cell (2,000 shuffles). 5 families are tested, so a family counts at p < 0.0100. **A type becomes a candidate only if** p is below that bar AND the best cell's average is above 30 bp (the measured cost of a round trip) AND at least three of its four time periods are positive. This is a second look at data already tested once in pooled form (F4), so a candidate is confirmed only by the forward record.

## financing or capital return (111 events)

**Best cell:** neg_uncertainty | material 0.2+; next regular session, hold 30 min: +19.1 bp before cost (-10.9 after 30 bp), t +1.63, right on 63% of 109. **Family p = 0.8805** (bar 0.0100) -> **does not pass**.
Four periods in time order (average bp; events): [(4.8, 28), (13.6, 27), (52.6, 27), (5.9, 27)]. Without the ten largest moves: 29.0 bp. The 30 minutes before the stamp: {'n': 87, 'mean': 3.4, 't': 0.5}.

| signal | 1 min after the stamp, hold 15 min | 1 min after the stamp, hold 30 min | 1 min after the stamp, hold 60 min | 5 min after the stamp, hold 30 min | 5 min after the stamp, hold 60 min | 5 min after the stamp, to the next 09:35 | next regular session, hold 30 min | next regular session, hold 60 min | next regular session, to the next 16:00 | next regular session, to the 16:00 after that |
|---|---|---|---|---|---|---|---|---|---|---|
| own_stock | material 0.2+ | +17 bp, 49%, n 65 | +9 bp, 51%, n 67 | +10 bp, 46%, n 59 | -1 bp, 47%, n 62 | -9 bp, 42%, n 59 | +1 bp, 49%, n 67 | +12 bp, 56%, n 88 | +16 bp, 55%, n 88 | +15 bp, 51%, n 88 | +7 bp, 52%, n 88 |
| own_stock | material 0.3+ | +15 bp, 46%, n 46 | +9 bp, 46%, n 48 | +17 bp, 49%, n 43 | -0 bp, 52%, n 46 | +2 bp, 44%, n 43 | +18 bp, 53%, n 49 | +19 bp, 60%, n 57 | +24 bp, 56%, n 57 | +41 bp, 56%, n 57 | -12 bp, 53%, n 57 |
| own_stock | material 0.5+ | n 13 | n 13 | n 12 | n 13 | n 11 | n 13 | n 14 | n 14 | n 14 | n 14 |
| neg_uncertainty | material 0.2+ | +13 bp, 50%, n 80 | +9 bp, 46%, n 82 | +14 bp, 53%, n 74 | +2 bp, 51%, n 79 | +0 bp, 53%, n 74 | -10 bp, 46%, n 85 | +19 bp, 63%, n 109 | +12 bp, 59%, n 109 | +31 bp, 57%, n 109 | +35 bp, 55%, n 109 |
| neg_uncertainty | material 0.3+ | +12 bp, 44%, n 50 | +9 bp, 41%, n 54 | +23 bp, 53%, n 47 | +2 bp, 53%, n 51 | +12 bp, 55%, n 47 | +2 bp, 47%, n 55 | +21 bp, 62%, n 64 | +16 bp, 56%, n 64 | +36 bp, 58%, n 64 | -14 bp, 47%, n 64 |
| neg_uncertainty | material 0.5+ | n 13 | n 13 | n 12 | n 13 | n 11 | n 13 | n 14 | n 14 | n 14 | n 14 |

## acquisition or disposal (54 events)

**Best cell:** neg_uncertainty | material 0.2+; 5 min after the stamp, to the next 09:35: -56.7 bp before cost (-86.7 after 30 bp), t -2.82, right on 31% of 42. **Family p = 0.0795** (bar 0.0100) -> **does not pass**.
Four periods in time order (average bp; events): [(-61.6, 11), (-86.0, 11), (-76.0, 10), (0.4, 10)]. Without the ten largest moves: -23.2 bp. The 30 minutes before the stamp: {'n': 39, 'mean': 17.7, 't': 0.91}.

| signal | 1 min after the stamp, hold 15 min | 1 min after the stamp, hold 30 min | 1 min after the stamp, hold 60 min | 5 min after the stamp, hold 30 min | 5 min after the stamp, hold 60 min | 5 min after the stamp, to the next 09:35 | next regular session, hold 30 min | next regular session, hold 60 min | next regular session, to the next 16:00 | next regular session, to the 16:00 after that |
|---|---|---|---|---|---|---|---|---|---|---|
| own_stock | material 0.2+ | +6 bp, 33%, n 36 | +13 bp, 56%, n 39 | +2 bp, 46%, n 37 | +1 bp, 54%, n 39 | -1 bp, 57%, n 37 | -5 bp, 48%, n 42 | +1 bp, 54%, n 54 | -14 bp, 48%, n 54 | -32 bp, 46%, n 54 | -18 bp, 54%, n 54 |
| own_stock | material 0.3+ | +8 bp, 36%, n 33 | +11 bp, 56%, n 36 | -0 bp, 44%, n 34 | -2 bp, 49%, n 35 | -4 bp, 56%, n 34 | -16 bp, 42%, n 38 | +2 bp, 53%, n 49 | -6 bp, 53%, n 49 | -29 bp, 45%, n 49 | -11 bp, 55%, n 49 |
| own_stock | material 0.5+ | n 16 | n 19 | n 18 | n 18 | n 19 | n 20 | n 26 | n 26 | n 26 | n 26 |
| neg_uncertainty | material 0.2+ | -4 bp, 47%, n 36 | -14 bp, 33%, n 39 | -22 bp, 41%, n 37 | -11 bp, 28%, n 39 | -21 bp, 43%, n 37 | -57 bp, 31%, n 42 | -6 bp, 37%, n 54 | -12 bp, 48%, n 54 | -43 bp, 44%, n 54 | -73 bp, 44%, n 54 |
| neg_uncertainty | material 0.3+ | -6 bp, 42%, n 33 | -12 bp, 33%, n 36 | -21 bp, 41%, n 34 | -10 bp, 29%, n 35 | -20 bp, 44%, n 34 | -58 bp, 32%, n 38 | -4 bp, 39%, n 49 | -16 bp, 45%, n 49 | -40 bp, 47%, n 49 | -71 bp, 45%, n 49 |
| neg_uncertainty | material 0.5+ | n 16 | n 19 | n 18 | n 18 | n 19 | n 20 | n 26 | n 26 | n 26 | n 26 |

## leadership change (37 events)

**Best cell:** neg_uncertainty | material 0.2+; next regular session, hold 30 min: +38.0 bp before cost (+8.0 after 30 bp), t +1.92, right on 60% of 35. **Family p = 0.2620** (bar 0.0100) -> **does not pass**.
Four periods in time order (average bp; events): [(44.6, 9), (-35.7, 9), (38.4, 9), (112.9, 8)]. Without the ten largest moves: None bp. The 30 minutes before the stamp: {'n': 31, 'mean': 15.6, 't': 1.16}.

| signal | 1 min after the stamp, hold 15 min | 1 min after the stamp, hold 30 min | 1 min after the stamp, hold 60 min | 5 min after the stamp, hold 30 min | 5 min after the stamp, hold 60 min | 5 min after the stamp, to the next 09:35 | next regular session, hold 30 min | next regular session, hold 60 min | next regular session, to the next 16:00 | next regular session, to the 16:00 after that |
|---|---|---|---|---|---|---|---|---|---|---|
| own_stock | material 0.2+ | n 25 | n 26 | n 23 | n 24 | n 23 | n 25 | +22 bp, 60%, n 30 | +23 bp, 58%, n 31 | -19 bp, 52%, n 31 | +61 bp, 60%, n 30 |
| own_stock | material 0.3+ | n 17 | n 18 | n 15 | n 16 | n 16 | n 18 | n 20 | n 20 | n 20 | n 20 |
| own_stock | material 0.5+ | n 4 | n 5 | n 4 | n 4 | n 4 | n 5 | n 5 | n 5 | n 5 | n 5 |
| neg_uncertainty | material 0.2+ | n 28 | -5 bp, 42%, n 31 | n 27 | n 28 | n 26 | n 29 | +38 bp, 60%, n 35 | +40 bp, 53%, n 36 | -8 bp, 44%, n 36 | +9 bp, 46%, n 35 |
| neg_uncertainty | material 0.3+ | n 18 | n 19 | n 16 | n 17 | n 17 | n 19 | n 21 | n 21 | n 21 | n 21 |
| neg_uncertainty | material 0.5+ | n 4 | n 5 | n 4 | n 4 | n 4 | n 5 | n 5 | n 5 | n 5 | n 5 |

## GROUP business news (contract or partnership; product or technology; guidance update; capital expenditure) (34 events)

**Best cell:** own_stock | material 0.2+; 1 min after the stamp, hold 15 min: +78.5 bp before cost (+48.5 after 30 bp), t +2.14, right on 71% of 31. **Family p = 0.4215** (bar 0.0100) -> **does not pass**.
Four periods in time order (average bp; events): [(114.8, 8), (78.6, 8), (8.0, 8), (117.3, 7)]. Without the ten largest moves: None bp. The 30 minutes before the stamp: {'n': 27, 'mean': None, 't': None}.

| signal | 1 min after the stamp, hold 15 min | 1 min after the stamp, hold 30 min | 1 min after the stamp, hold 60 min | 5 min after the stamp, hold 30 min | 5 min after the stamp, hold 60 min | 5 min after the stamp, to the next 09:35 | next regular session, hold 30 min | next regular session, hold 60 min | next regular session, to the next 16:00 | next regular session, to the 16:00 after that |
|---|---|---|---|---|---|---|---|---|---|---|
| own_stock | material 0.2+ | +78 bp, 71%, n 31 | +85 bp, 65%, n 31 | n 29 | +11 bp, 57%, n 30 | +15 bp, 52%, n 31 | +67 bp, 58%, n 31 | +19 bp, 47%, n 32 | +29 bp, 56%, n 32 | +29 bp, 56%, n 32 | +8 bp, 53%, n 32 |
| own_stock | material 0.3+ | n 28 | n 28 | n 26 | n 27 | n 28 | n 28 | n 29 | n 29 | n 29 | n 29 |
| own_stock | material 0.5+ | n 21 | n 21 | n 20 | n 21 | n 21 | n 21 | n 22 | n 22 | n 22 | n 22 |
| neg_uncertainty | material 0.2+ | +32 bp, 52%, n 33 | +35 bp, 55%, n 33 | +40 bp, 61%, n 31 | +27 bp, 44%, n 32 | +15 bp, 45%, n 33 | +56 bp, 48%, n 33 | +24 bp, 47%, n 34 | +13 bp, 38%, n 34 | +21 bp, 44%, n 34 | +2 bp, 47%, n 34 |
| neg_uncertainty | material 0.3+ | +28 bp, 53%, n 30 | +27 bp, 57%, n 30 | n 28 | n 29 | +17 bp, 47%, n 30 | +65 bp, 47%, n 30 | +30 bp, 52%, n 31 | +19 bp, 42%, n 31 | +44 bp, 48%, n 31 | +10 bp, 48%, n 31 |
| neg_uncertainty | material 0.5+ | n 21 | n 21 | n 20 | n 21 | n 21 | n 21 | n 22 | n 22 | n 22 | n 22 |

## GROUP trouble (legal or regulatory; cyber incident; accounting; restructuring; leadership change) (72 events)

**Best cell:** own_stock | material 0.2+; 1 min after the stamp, hold 15 min: +44.5 bp before cost (+14.5 after 30 bp), t +2.93, right on 56% of 48. **Family p = 0.0155** (bar 0.0100) -> **does not pass**.
Four periods in time order (average bp; events): [(5.7, 12), (83.0, 12), (52.0, 12), (37.1, 12)]. Without the ten largest moves: 5.7 bp. The 30 minutes before the stamp: {'n': 57, 'mean': 27.4, 't': 2.64}.

| signal | 1 min after the stamp, hold 15 min | 1 min after the stamp, hold 30 min | 1 min after the stamp, hold 60 min | 5 min after the stamp, hold 30 min | 5 min after the stamp, hold 60 min | 5 min after the stamp, to the next 09:35 | next regular session, hold 30 min | next regular session, hold 60 min | next regular session, to the next 16:00 | next regular session, to the 16:00 after that |
|---|---|---|---|---|---|---|---|---|---|---|
| own_stock | material 0.2+ | +44 bp, 56%, n 48 | +41 bp, 51%, n 51 | +36 bp, 58%, n 48 | +14 bp, 54%, n 50 | +12 bp, 55%, n 47 | +24 bp, 51%, n 53 | +20 bp, 60%, n 65 | +20 bp, 58%, n 66 | +12 bp, 50%, n 66 | +72 bp, 54%, n 65 |
| own_stock | material 0.3+ | +48 bp, 54%, n 37 | +44 bp, 45%, n 40 | +39 bp, 58%, n 36 | +11 bp, 54%, n 39 | +7 bp, 56%, n 36 | +23 bp, 50%, n 42 | +31 bp, 65%, n 49 | +30 bp, 59%, n 49 | +11 bp, 49%, n 49 | +72 bp, 53%, n 49 |
| own_stock | material 0.5+ | n 15 | n 17 | n 16 | n 16 | n 16 | n 17 | n 19 | n 19 | n 19 | n 19 |
| neg_uncertainty | material 0.2+ | +22 bp, 51%, n 51 | +22 bp, 50%, n 56 | +23 bp, 54%, n 52 | +12 bp, 56%, n 54 | +12 bp, 52%, n 50 | +44 bp, 56%, n 57 | +15 bp, 53%, n 70 | +18 bp, 51%, n 71 | +3 bp, 45%, n 71 | +22 bp, 49%, n 70 |
| neg_uncertainty | material 0.3+ | +24 bp, 53%, n 38 | +24 bp, 49%, n 41 | +19 bp, 51%, n 37 | +11 bp, 57%, n 40 | +7 bp, 49%, n 37 | +50 bp, 56%, n 43 | +10 bp, 56%, n 50 | +10 bp, 50%, n 50 | -19 bp, 44%, n 50 | +26 bp, 52%, n 50 |
| neg_uncertainty | material 0.5+ | n 15 | n 17 | n 16 | n 16 | n 16 | n 17 | n 19 | n 19 | n 19 | n 19 |

## Not tested (under 30 events)

legal or regulatory (25), contract or partnership (16), guidance update (16), restructuring (8), other (5), product or technology (2), accounting (1), cyber incident (1)

