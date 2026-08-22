# Universe-wide directed-pair scan

```
==============================================================================
UNIVERSE-WIDE DIRECTED-PAIR SCAN -- maximum-statistic null
==============================================================================
assets:    34
window:    2015-07-08 -> 2026-07-17 (2772 sessions)
residual:  market (factor SPY, removed from the universe)
pairs:     561 x 5 lags = 2805 directed tests
iters 1000 | seed 42

EXPLORATORY BY CONSTRUCTION: run after five pre-registered nulls, on
the same data. A surviving pair is a CANDIDATE for out-of-sample
confirmation, not a finding.

[1] THE COST OF SEARCHING
    observed maximum |d| across the universe = 0.1572
    null distribution of the MAXIMUM: mean 0.2321, SD 0.1853, 95th pct 0.6278
    pairs significant at NAIVE p<0.05 (no correction): 148 of 561
    pairs significant after UNIVERSE-WIDE correction:  0 of 561
    expected naive false positives under the null: ~28
    The gap between those counts is what the search manufactures.

[2] TOP 20 PAIRS BY |d|
      leader -> follower      d       lag   p(naive)  p(universe)
        MLPA -> TLT    0.1572   k=1   0.0010    0.4845
        AMLP -> TLT    0.1511   k=1   0.0010    0.4995
         XSD -> ITA    0.1460   k=3   0.0010    0.5115
         USO -> VOO    0.1455   k=3   0.0020    0.5125
         ITA -> VOO    0.1440   k=3   0.0010    0.5205
        SOXX -> ITA    0.1402   k=3   0.0030    0.5395
         SMH -> ITA    0.1394   k=3   0.0070    0.5415
        ASML -> ITA    0.1369   k=3   0.0010    0.5495
         LMT -> VOO    0.1262   k=5   0.0060    0.6164
         XLV -> CIBR   0.1208   k=1   0.0030    0.6533
         XLP -> VOO    0.1203   k=5   0.0060    0.6573
         SMH -> XAR    0.1190   k=3   0.0010    0.6653
         XLP -> USO    0.1149   k=4   0.0010    0.7043
        SOXX -> XAR    0.1132   k=3   0.0010    0.7233
         UUP -> MLPA   0.1115   k=1   0.0010    0.7483
         VOO -> ASML   0.1104   k=2   0.0040    0.7562
         XAR -> VOO    0.1102   k=3   0.0060    0.7582
         XSD -> XAR    0.1100   k=3   0.0010    0.7612
        AMLP -> LMT    0.1079   k=3   0.0030    0.7922
         UUP -> TLT    0.1053   k=1   0.0060    0.8312

==============================================================================
READING
  NO directed pair in the universe survives correction for having
  searched it. 148 pairs clear a naive threshold -- against
  ~28 expected by chance alone -- and none clears the
  maximum-statistic null. This is the broad sweep the
  pre-registered tests could not provide: the nulls were not an
  artifact of testing the wrong baskets.

  Scope: unconditional, full-sample, linear lead-lag at lags 1..5.
  It cannot see nonlinear relationships, episode-local structure that
  averages to zero unconditionally, or lags beyond the window.
==============================================================================
```
