# PEAD results

```
==============================================================================
PEAD -- post-earnings announcement drift (firm-level event test)
==============================================================================
universe: ASML, LMT, TSM, ORCL, INTC, MU
market proxy: SPY | beta: trailing 250 frozen at t
iters 5000 | seed 42

Announcement response measured over {t, t+1} COMBINED (yfinance does
not flag BMO/AMC). Drift measured from t+2 -- the entire announcement
window is DISCARDED, so drift cannot be contaminated by it.

fetching earnings dates:
    ASML   100 dates  2001-01-18 -> 2026-10-14
    LMT    100 dates  2002-01-25 -> 2026-10-20
    TSM     99 dates  2000-04-25 -> 2026-10-15
    ORCL    98 dates  2002-06-18 -> 2026-09-10
    INTC    99 dates  2002-04-16 -> 2026-10-22
    MU     100 dates  2001-12-18 -> 2026-09-23

usable events: 590  (dropped 6 for short beta window, missing sessions, or zero announcement return)
span: 2000-04-25 -> 2026-07-23
mean |announcement AR| = 4.77%

  H    n    PEAD stat   p(sign-flip)  p(rotation)   hit
   1  590    +0.096%    0.2428        0.2406     51%
   5  590    +0.098%    0.5797        0.5915     55%
  10  590    +0.120%    0.6185        0.6627     52%
  20  588    +0.183%    0.5931        0.5865     50%

==============================================================================
VERDICT against the registered criterion
  NOT MET (0 horizon(s) clear both nulls with the
  registered sign; not adjacent).
  Scope: pooled across firms, return-based surprise proxy, drift
  measured from t+2. A null here does NOT rule out PEAD measured
  with analyst-estimate SUE, at intraday resolution, or on the
  announcement window itself -- none of which this test examines.
==============================================================================
```
