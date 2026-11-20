# SR-2: public calls by well-known investors -- how the security moved

827 calls extracted, 733 priced (35 securities without prices on Yahoo). Return = the security's daily move minus the S&P 500's (a call on an index itself: the raw move), in the direction of the call, in bp (1 bp = 0.01%). Day 0 = the first session whose close comes after the first headline. Each of +1 to +7 is that one session alone. p = how often the same securities on other dates did as well (200 sets). A group counts at p < 0.0063; it needs 30 calls.

| group | calls | day 0 | +1 | +2 | +3 | +4 | +5 | +6 | +7 | day 0 to +7 |
|---|---|---|---|---|---|---|---|---|---|---|
| Bill Ackman | 88 | **+234 bp, 55%, p 0.000** | **+86 bp, 50%, p 0.000** | +42 bp, 48%, p 0.035 | +17 bp, 44%, p 0.260 | +22 bp, 55%, p 0.155 | +27 bp, 52%, p 0.175 | +22 bp, 52%, p 0.145 | -13 bp, 51%, p 0.690 | **+437 bp, 57%, p 0.000** |
| Carl Icahn | 65 | +69 bp, 57%, p 0.040 | +41 bp, 46%, p 0.070 | +6 bp, 51%, p 0.505 | -3 bp, 54%, p 0.530 | -3 bp, 52%, p 0.505 | +50 bp, 57%, p 0.075 | -14 bp, 52%, p 0.670 | +28 bp, 55%, p 0.240 | +174 bp, 57%, p 0.055 |
| Cathie Wood | 201 | -11 bp, 53%, p 0.655 | +55 bp, 53%, p 0.040 | -24 bp, 50%, p 0.865 | +73 bp, 54%, p 0.010 | -24 bp, 51%, p 0.840 | -34 bp, 50%, p 0.910 | -1 bp, 50%, p 0.615 | +5 bp, 49%, p 0.450 | +39 bp, 46%, p 0.285 |
| George Soros | 37 | +90 bp, 65%, p 0.035 | +44 bp, 54%, p 0.195 | -21 bp, 41%, p 0.655 | -51 bp, 35%, p 0.905 | +6 bp, 43%, p 0.445 | -18 bp, 62%, p 0.700 | -11 bp, 54%, p 0.635 | -63 bp, 43%, p 0.935 | -25 bp, 49%, p 0.650 |
| Michael Burry | 116 | +17 bp, 53%, p 0.220 | +49 bp, 55%, p 0.010 | +26 bp, 48%, p 0.120 | -44 bp, 40%, p 0.920 | -41 bp, 44%, p 0.865 | +14 bp, 50%, p 0.225 | -97 bp, 40%, p 1.000 | -29 bp, 50%, p 0.795 | -105 bp, 50%, p 0.820 |
| Ray Dalio | 40 | +88 bp, 65%, p 0.015 | +22 bp, 55%, p 0.260 | +24 bp, 52%, p 0.275 | -26 bp, 50%, p 0.805 | -25 bp, 50%, p 0.770 | -26 bp, 57%, p 0.820 | +76 bp, 50%, p 0.015 | +12 bp, 32%, p 0.400 | +145 bp, 50%, p 0.080 |
| Warren Buffett | 186 | **+86 bp, 54%, p 0.000** | **+53 bp, 59%, p 0.000** | -8 bp, 48%, p 0.720 | -20 bp, 50%, p 0.885 | -9 bp, 54%, p 0.655 | +24 bp, 52%, p 0.115 | -5 bp, 47%, p 0.635 | -30 bp, 45%, p 0.960 | +90 bp, 56%, p 0.040 |
| ALL INVESTORS | 733 | **+65 bp, 55%, p 0.005** | **+54 bp, 54%, p 0.000** | +1 bp, 49%, p 0.460 | +6 bp, 48%, p 0.330 | -14 bp, 51%, p 0.845 | +4 bp, 52%, p 0.340 | -12 bp, 48%, p 0.850 | -13 bp, 48%, p 0.890 | +91 bp, 52%, p 0.025 |
| negative calls only | 273 | +35 bp, 54%, p 0.010 | -17 bp, 54%, p 0.805 | +0 bp, 48%, p 0.390 | -38 bp, 47%, p 0.985 | +1 bp, 53%, p 0.440 | +8 bp, 48%, p 0.225 | -55 bp, 46%, p 0.985 | -20 bp, 51%, p 0.825 | -85 bp, 49%, p 0.875 |
| positive calls only | 460 | **+83 bp, 56%, p 0.000** | **+96 bp, 54%, p 0.000** | +2 bp, 49%, p 0.535 | +32 bp, 49%, p 0.020 | -23 bp, 50%, p 0.960 | +2 bp, 55%, p 0.515 | +13 bp, 50%, p 0.250 | -8 bp, 46%, p 0.755 | **+196 bp, 54%, p 0.000** |
| reported as that day's news | 586 | **+84 bp, 57%, p 0.000** | **+66 bp, 55%, p 0.000** | -2 bp, 48%, p 0.540 | +12 bp, 49%, p 0.205 | -8 bp, 50%, p 0.755 | -1 bp, 52%, p 0.475 | +0 bp, 48%, p 0.475 | +5 bp, 49%, p 0.305 | **+157 bp, 53%, p 0.005** |
| single calls | 721 | **+66 bp, 55%, p 0.000** | **+54 bp, 54%, p 0.000** | +2 bp, 49%, p 0.425 | +7 bp, 49%, p 0.290 | -13 bp, 51%, p 0.850 | +3 bp, 52%, p 0.370 | -12 bp, 48%, p 0.845 | -11 bp, 48%, p 0.845 | +96 bp, 52%, p 0.010 |
| CLUSTERS: a second investor, same direction, within two weeks | 12 (under 30: not judged) |  |  |  |  |  |  |  |  |  |

Each cell: average move in the direction of the call, share of calls where the move went the call's way, and p. Bold = passes the bar.

Most-called securities: TSLA 63, AAPL 30, NVDA 30, GOOGL 24, OXY 21, SPY 20, COIN 20, AMZN 18, PLTR 18, BABA 15, GME 13, META 13, GLD 12, HOOD 11, BYDDY 10.
