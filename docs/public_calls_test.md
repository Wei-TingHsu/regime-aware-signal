# SR-2: public calls by well-known investors -- how the security moved

1134 calls extracted, 957 priced (37 securities without prices on Yahoo). Return = the security's daily move minus the S&P 500's (a call on an index itself: the raw move), in the direction of the call, in bp (1 bp = 0.01%). Day 0 = the first session whose close comes after the first headline. Each of +1 to +7 is that one session alone. p = how often the same securities on other dates did as well (200 sets). A group counts at p < 0.0063; it needs 30 calls.

| group | calls | day 0 | +1 | +2 | +3 | +4 | +5 | +6 | +7 | day 0 to +7 |
|---|---|---|---|---|---|---|---|---|---|---|
| Bill Ackman | 104 | **+233 bp, 59%, p 0.000** | +60 bp, 49%, p 0.015 | **+50 bp, 49%, p 0.005** | +24 bp, 46%, p 0.130 | +9 bp, 53%, p 0.335 | +14 bp, 52%, p 0.290 | +38 bp, 55%, p 0.070 | +15 bp, 52%, p 0.230 | **+443 bp, 58%, p 0.000** |
| Carl Icahn | 65 | +69 bp, 57%, p 0.020 | +41 bp, 46%, p 0.065 | +6 bp, 51%, p 0.455 | -3 bp, 54%, p 0.570 | -3 bp, 52%, p 0.570 | +50 bp, 57%, p 0.050 | -14 bp, 52%, p 0.675 | +28 bp, 55%, p 0.230 | +174 bp, 57%, p 0.060 |
| Cathie Wood | 309 | -5 bp, 51%, p 0.560 | +56 bp, 53%, p 0.010 | -30 bp, 48%, p 0.880 | **+53 bp, 56%, p 0.005** | -17 bp, 51%, p 0.810 | -18 bp, 51%, p 0.805 | +0 bp, 52%, p 0.505 | -2 bp, 48%, p 0.680 | +37 bp, 48%, p 0.355 |
| George Soros | 37 | +90 bp, 65%, p 0.025 | +44 bp, 54%, p 0.180 | -21 bp, 41%, p 0.670 | -51 bp, 35%, p 0.840 | +6 bp, 43%, p 0.495 | -18 bp, 62%, p 0.710 | -11 bp, 54%, p 0.595 | -63 bp, 43%, p 0.920 | -25 bp, 49%, p 0.695 |
| Michael Burry | 174 | +29 bp, 51%, p 0.080 | +44 bp, 57%, p 0.025 | +14 bp, 52%, p 0.170 | +19 bp, 48%, p 0.125 | -22 bp, 44%, p 0.820 | -18 bp, 48%, p 0.730 | -50 bp, 46%, p 0.990 | -19 bp, 49%, p 0.760 | -1 bp, 54%, p 0.300 |
| Ray Dalio | 40 | +88 bp, 65%, p 0.010 | +22 bp, 55%, p 0.310 | +24 bp, 52%, p 0.325 | -26 bp, 50%, p 0.845 | -25 bp, 50%, p 0.800 | -26 bp, 57%, p 0.735 | +76 bp, 50%, p 0.050 | +12 bp, 32%, p 0.365 | +145 bp, 50%, p 0.135 |
| Warren Buffett | 228 | **+79 bp, 55%, p 0.005** | **+52 bp, 59%, p 0.000** | -8 bp, 48%, p 0.710 | -8 bp, 50%, p 0.720 | -13 bp, 52%, p 0.805 | +15 bp, 53%, p 0.175 | +3 bp, 48%, p 0.445 | -23 bp, 46%, p 0.960 | +97 bp, 56%, p 0.025 |
| ALL INVESTORS | 957 | **+60 bp, 54%, p 0.000** | **+50 bp, 55%, p 0.005** | -3 bp, 49%, p 0.605 | +18 bp, 51%, p 0.070 | -13 bp, 50%, p 0.905 | -2 bp, 52%, p 0.615 | -2 bp, 50%, p 0.595 | -8 bp, 48%, p 0.715 | +100 bp, 53%, p 0.015 |
| negative calls only | 367 | **+45 bp, 54%, p 0.000** | -8 bp, 54%, p 0.585 | -6 bp, 50%, p 0.555 | -18 bp, 50%, p 0.815 | -3 bp, 51%, p 0.415 | -1 bp, 49%, p 0.380 | -29 bp, 50%, p 0.945 | -24 bp, 49%, p 0.855 | -46 bp, 51%, p 0.475 |
| positive calls only | 590 | **+69 bp, 54%, p 0.000** | **+87 bp, 55%, p 0.005** | -1 bp, 48%, p 0.635 | **+40 bp, 52%, p 0.005** | -18 bp, 49%, p 0.980 | -3 bp, 54%, p 0.680 | +14 bp, 51%, p 0.225 | +2 bp, 47%, p 0.525 | **+190 bp, 54%, p 0.000** |
| reported as that day's news | 784 | **+74 bp, 55%, p 0.000** | **+64 bp, 55%, p 0.000** | -9 bp, 48%, p 0.820 | +24 bp, 52%, p 0.040 | -9 bp, 50%, p 0.805 | -7 bp, 51%, p 0.655 | +8 bp, 50%, p 0.255 | +6 bp, 48%, p 0.290 | **+151 bp, 54%, p 0.000** |
| single calls | 923 | **+59 bp, 54%, p 0.005** | **+52 bp, 55%, p 0.000** | -2 bp, 49%, p 0.600 | +21 bp, 51%, p 0.020 | -11 bp, 50%, p 0.855 | -7 bp, 52%, p 0.765 | -3 bp, 50%, p 0.575 | -7 bp, 48%, p 0.755 | +101 bp, 53%, p 0.015 |
| CLUSTERS: a second investor, same direction, within two weeks | 34 | +85 bp, 53%, p 0.020 | +16 bp, 50%, p 0.305 | -24 bp, 50%, p 0.725 | -77 bp, 44%, p 0.950 | -45 bp, 44%, p 0.830 | +119 bp, 56%, p 0.010 | +17 bp, 50%, p 0.360 | -31 bp, 44%, p 0.800 | +61 bp, 44%, p 0.310 |

Each cell: average move in the direction of the call, share of calls where the move went the call's way, and p. Bold = passes the bar.

Most-called securities: TSLA 73, NVDA 38, AAPL 35, GOOGL 31, AMZN 26, PLTR 26, SPY 25, OXY 22, COIN 22, BABA 18, META 17, HOOD 16, GLD 13, GME 13, BYDDY 12.
