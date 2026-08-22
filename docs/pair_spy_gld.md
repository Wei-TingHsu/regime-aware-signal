# Pair confirmation: SPY -> GLD lag 1

```
==============================================================================
PAIR CONFIRMATION -- SPY -> GLD at lag 1
==============================================================================
chain:     TLT, SPY, GLD, UUP, USO
detector:  z<=-2.0 (RISK-OFF only) of SPY vs trailing 60d SD
residual:  none
episodes:  88 (eplen 15) | iters 2000 | seed 42

The pair is PRE-SPECIFIED, so each test below is a SINGLE test -- no
Holm correction over 10 pairs. But the pair was CHOSEN after seeing the
full sample, so this measures STABILITY, not replication.

[1] FULL SAMPLE:  d = +0.1701   p = 0.0010   (88 episodes)

[2] TEMPORAL SPLIT (episodes are in date order)
    FIRST half   2007-10-19 .. 2017-05-17  n= 44   d = +0.2938   p = 0.0005 *
    SECOND half  2017-08-10 .. 2026-06-05  n= 44   d = +0.0525   p = 0.3573
    sign agreement: YES | magnitude ratio 5.60 (1.0 = identical)
    Same sign but magnitudes differ by >3x -- concentrated in one period.

[3] ECONOMIC SIGNIFICANCE
    Rule: on each episode day t, take sign(SPY) and hold GLD
    for 1 session(s). Block bootstrap resamples whole episodes.
    mean payoff   = +9.32 bps per trade (95% CI +0.11 .. +19.66)
    hit rate      = 52.2%   trades = 1232 across 88 episodes
    bootstrap p   = 0.0238
    round-trip cost assumption 4.0 bps -> NET +5.32 bps per trade
    Net positive at the point estimate, but the 95% CI lower
    bound does not clear costs. Not established.

==============================================================================
READING
  Stability [2]: FAIL (sign agrees, ratio 5.60)
  Economics [3]: net +5.32 bps vs 4.0 bps cost

  Not time-stable. The ladder consistency seen at discovery came
  from overlapping episodes, not from a persistent effect.
==============================================================================
```
