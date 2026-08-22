# Pair confirmation: SOXX -> XAR lag 3

```
==============================================================================
PAIR CONFIRMATION -- SOXX -> XAR at lag 3
==============================================================================
chain:     SOXX, XAR, XLE, XLV, XLP
detector:  |z|>=2.0 of SPY vs trailing 60d SD
residual:  market (factor SPY)
episodes:  97 (eplen 15) | iters 2000 | seed 42

The pair is PRE-SPECIFIED, so each test below is a SINGLE test -- no
Holm correction over 10 pairs. But the pair was CHOSEN after seeing the
full sample, so this measures STABILITY, not replication.

[1] FULL SAMPLE:  d = +0.1520   p = 0.0010   (97 episodes)

[2] TEMPORAL SPLIT (episodes are in date order)
    FIRST half   2012-04-10 .. 2019-06-04  n= 48   d = -0.0352   p = 0.5782
    SECOND half  2019-08-05 .. 2026-06-05  n= 49   d = +0.2283   p = 0.0010 *
    sign agreement: NO | magnitude ratio 0.15 (1.0 = identical)
    SIGN FLIPS ACROSS HALVES -- the effect is not stable in time.

[3] ECONOMIC SIGNIFICANCE
    Rule: on each episode day t, take sign(SOXX) and hold XAR
    for 3 session(s). Block bootstrap resamples whole episodes.
    mean payoff   = +3.69 bps per trade (95% CI -2.48 .. +10.33)
    hit rate      = 49.2%   trades = 1164 across 97 episodes
    bootstrap p   = 0.1296
    round-trip cost assumption 4.0 bps -> NET -0.31 bps per trade
    NET NEGATIVE. Statistically detectable, not economically
    tradeable at this cost assumption. A signal that does not
    clear the spread is not a product.

==============================================================================
READING
  Stability [2]: FAIL (sign FLIPS, ratio 0.15)
  Economics [3]: net -0.31 bps vs 4.0 bps cost

  Not time-stable. The ladder consistency seen at discovery came
  from overlapping episodes, not from a persistent effect.
==============================================================================
```
