# S: position size from the score, shape learned by least squares

Trade: results release -> own stock, enter 1 min after the SEC stamp, hold 60 min; 365 releases, May 2018 to Nov 2026; returns in bp before cost. r = the stock's return, s = the own-stock score.

## Fitted on all releases (in sample: this describes the past, it is not a test)

| shape | equation | fitted | sum of squared errors, share of the total | per unit of position | t |
|---|---|---|---|---|---|
| M0 sign (every score the same size) | r = b * sign(s) | b = +64.9 bp | 0.9670 | +64.9 bp | +3.53 |
| M1 linear (size = score) | r = b * s | b = +121.3 bp | 0.9448 | +93.5 bp | +4.28 |
| M2 power (size = |score|^g) | r = b * sign(s) * |s|^g | b = +135.7 bp, g = 1.65 | 0.9425 | +104.7 bp | +4.25 |
| M3 step (trade only |score| >= h) | r = b * sign(s) * [|s| >= h] | b = +143.7 bp, h = 0.7 | 0.9277 | +143.7 bp | +4.74 |

## Out of sample (2020-2026; parameters fitted only on earlier releases)

| shape | per unit of position | t | releases traded | parameter fitted each year |
|---|---|---|---|---|
| M0 sign (every score the same size) | +77.5 bp | +3.76 | 302 of 302 | 2020: b +4; 2021: b +27; 2022: b +22; 2023: b +45; 2024: b +44; 2025: b +72; 2026: b +71 |
| M1 linear (size = score) | +98.4 bp | +4.00 | 302 of 302 | 2020: b +92; 2021: b +86; 2022: b +58; 2023: b +76; 2024: b +82; 2025: b +134; 2026: b +130 |
| M2 power (size = |score|^g) | +105.6 bp | +3.78 | 302 of 302 | 2020: g 2.95; 2021: g 2.50; 2022: g 1.55; 2023: g 1.05; 2024: g 1.45; 2025: g 1.80; 2026: g 1.45 |
| M3 step (trade only |score| >= h) | +141.5 bp | +4.16 | 140 of 302 | 2020: h 0.80; 2021: h 0.70; 2022: h 0.70; 2023: h 0.70; 2024: h 0.70; 2025: h 0.70; 2026: h 0.70 |

Per unit of position = total gain divided by total position size, so shapes that trade fewer or smaller positions are compared fairly. The out-of-sample table is the one to believe: the shape's parameter was chosen without seeing that year's releases.
