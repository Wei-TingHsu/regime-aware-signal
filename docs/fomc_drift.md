# FOMC drift

```
==============================================================================
SCHEDULED MACRO EVENT DRIFT -- FOMC
==============================================================================
dates: 131 from processed/fomc_decisions.csv, 2011-01-26 -> 2026-07-29
assets: SPY, TLT, GLD, UUP | iters 5000 | seed 42

PRE    = open(N)/close(N-1)-1   overnight into the event day
DAY    = close(N)/open(N)-1     session containing the release;
                                daily bars cannot split pre/post release
NEXT_h = close(N+h)/close(N)-1  FIRST FULLY TRADEABLE window  <-- the test

Entry convention changed from t+2 deliberately: the NVDA spillover result
showed events fully reprice before t+2, so every earlier null measured an
empty window. Raw returns, NOT market-adjusted -- a macro event moves the
whole market and adjusting would remove the effect being measured.

fetching adjusted OHLC ...

SPY: 131 events, 2011-01-26 -> 2026-07-29
  mean PRE +0.075%   mean DAY -0.080%
   h    n    Q1 uncond   p(rot)    Q2 signed   p(flip)  p(perm)
   1   131    -0.046%  0.4055     -0.004%   0.9776   0.9578
   2   131    -0.074%  0.2533     +0.054%   0.7445   0.7704
   3   131    +0.063%  0.7347     +0.002%   0.9912   0.9700
   5   131    +0.193%  0.9648     -0.191%   0.4207   0.4733

TLT: 131 events, 2011-01-26 -> 2026-07-29
  mean PRE +0.055%   mean DAY +0.174%
   h    n    Q1 uncond   p(rot)    Q2 signed   p(flip)  p(perm)
   1   131    -0.007%  0.7720     +0.115%   0.3051   0.2931
   2   131    +0.015%  0.8596     -0.047%   0.7670   0.7540
   3   131    -0.067%  0.3979     -0.012%   0.9390   0.9778
   5   131    -0.080%  0.3713     +0.178%   0.3031   0.2713

GLD: 131 events, 2011-01-26 -> 2026-07-29
  mean PRE +0.003%   mean DAY +0.152%
   h    n    Q1 uncond   p(rot)    Q2 signed   p(flip)  p(perm)
   1   131    -0.132%  0.0744     +0.326%   0.0084   0.0038 *
   2   131    -0.232%  0.0280     +0.175%   0.3263   0.2488
   3   131    -0.317%  0.0096     +0.274%   0.2132   0.1520
   5   131    -0.320%  0.0104     +0.387%   0.1028   0.0754

UUP: 131 events, 2011-01-26 -> 2026-07-29
  mean PRE -0.069%   mean DAY -0.030%
   h    n    Q1 uncond   p(rot)    Q2 signed   p(flip)  p(perm)
   1   131    +0.093%  0.0702     -0.023%   0.6469   0.7117
   2   131    +0.130%  0.0968     -0.042%   0.5435   0.5787
   3   131    +0.155%  0.1194     -0.042%   0.6305   0.6857
   5   131    +0.239%  0.0550     -0.032%   0.7485   0.8170

==============================================================================
READING
  Q1 asks whether returns after the event differ from ordinary days.
  Q2 asks whether the event-day move continues (+) or reverses (-),
  entered at the close of the event day -- no look-ahead.
  A single significant horizon is NOT a result; two adjacent are needed.
  PRE and DAY are reported for context. Daily bars cannot separate the
  pre-release part of DAY from the reaction, so DAY is not a trade.
  Multiple testing: 4 assets x 4 horizons x 2
  questions. Read the pattern, not one cell.
==============================================================================
```
