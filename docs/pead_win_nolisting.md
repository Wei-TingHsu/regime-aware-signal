# PEAD results

```
==============================================================================
PEAD -- post-earnings announcement drift (firm-level event test)
==============================================================================
universe: TSLA, NVDA, MSFT
market proxy: SPY | beta: trailing 250 frozen at t
iters 5000 | seed 42

Announcement response measured over {t, t+1} COMBINED (yfinance does
not flag BMO/AMC). Drift measured from t+2 -- the entire announcement
window is DISCARDED, so drift cannot be contaminated by it.

fetching earnings dates:
    TSLA    65 dates  2010-11-09 -> 2026-10-21
    NVDA    97 dates  2002-05-22 -> 2026-08-26
    MSFT   100 dates  2002-01-17 -> 2026-10-28

usable events: 256  (dropped 6 for short beta window, missing sessions, or zero announcement return)
span: 2002-01-17 -> 2026-07-29
mean |announcement AR| = 5.94%

  H    n    PEAD stat   p(sign-flip)  p(rotation)   hit
   1  256    +0.454%    0.0104        0.0100     56%  *
   5  256    +0.525%    0.0994        0.0868     55%
  10  256    +0.312%    0.5091        0.5261     50%
  20  255    +0.941%    0.1344        0.1140     55%

==============================================================================
VERDICT against the registered criterion
  NOT MET (1 horizon(s) clear both nulls with the
  registered sign; not adjacent).
  Scope: pooled across firms, return-based surprise proxy, drift
  measured from t+2. A null here does NOT rule out PEAD measured
  with analyst-estimate SUE, at intraday resolution, or on the
  announcement window itself -- none of which this test examines.
==============================================================================
```
