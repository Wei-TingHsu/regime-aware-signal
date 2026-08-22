# Universe-wide directed-pair scan

```
==============================================================================
UNIVERSE-WIDE DIRECTED-PAIR SCAN -- maximum-statistic null
==============================================================================
assets:    35
window:    2015-07-08 -> 2026-07-17 (2772 sessions)
residual:  none
pairs:     595 x 5 lags = 2975 directed tests
iters 1000 | seed 42

EXPLORATORY BY CONSTRUCTION: run after five pre-registered nulls, on
the same data. A surviving pair is a CANDIDATE for out-of-sample
confirmation, not a finding.

[1] THE COST OF SEARCHING
    observed maximum |d| across the universe = 0.1563
    null distribution of the MAXIMUM: mean 0.4901, SD 0.2578, 95th pct 0.8926
    pairs significant at NAIVE p<0.05 (no correction): 154 of 595
    pairs significant after UNIVERSE-WIDE correction:  0 of 595
    expected naive false positives under the null: ~30
    The gap between those counts is what the search manufactures.

[2] TOP 20 PAIRS BY |d|
      leader -> follower      d       lag   p(naive)  p(universe)
        MLPA -> TLT    0.1563   k=1   0.0040    0.8262
         XLP -> USO    0.1531   k=4   0.0020    0.8342
        AMLP -> TLT    0.1509   k=1   0.0020    0.8392
         USO -> LMT    0.1382   k=3   0.0040    0.8661
        MLPA -> LMT    0.1373   k=3   0.0020    0.8681
        AMLP -> LMT    0.1331   k=3   0.0060    0.8771
         XLV -> USO    0.1323   k=4   0.0030    0.8821
         UUP -> MLPA   0.1284   k=1   0.0040    0.8931
        JETS -> XLP    0.1213   k=2   0.0050    0.9131
         VOO -> AMLP   0.1199   k=1   0.0040    0.9171
         SPY -> AMLP   0.1184   k=1   0.0060    0.9201
         USO -> ITA    0.1170   k=3   0.0050    0.9281
        MSFT -> AMLP   0.1169   k=1   0.0050    0.9281
         UUP -> AMLP   0.1165   k=1   0.0010    0.9311
         VOO -> MLPA   0.1148   k=1   0.0030    0.9361
         SPY -> MLPA   0.1142   k=1   0.0050    0.9361
        ORCL -> MLPA   0.1141   k=4   0.0070    0.9361
        ASML -> XLP    0.1117   k=3   0.0040    0.9461
        ASML -> VOO    0.1117   k=1   0.0050    0.9461
         ITA -> XLP    0.1102   k=3   0.0110    0.9500

==============================================================================
READING
  NO directed pair in the universe survives correction for having
  searched it. 154 pairs clear a naive threshold -- against
  ~30 expected by chance alone -- and none clears the
  maximum-statistic null. This is the broad sweep the
  pre-registered tests could not provide: the nulls were not an
  artifact of testing the wrong baskets.

  Scope: unconditional, full-sample, linear lead-lag at lags 1..5.
  It cannot see nonlinear relationships, episode-local structure that
  averages to zero unconditionally, or lags beyond the window.
==============================================================================
```
