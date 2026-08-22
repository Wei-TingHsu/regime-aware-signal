# PEAD results

```
==============================================================================
PEAD -- post-earnings announcement drift (firm-level event test)
==============================================================================
universe: TSM, ORCL, INTC, MU
market proxy: SPY | beta: trailing 250 frozen at t
iters 5000 | seed 42

Announcement response measured over {t, t+1} COMBINED (yfinance does
not flag BMO/AMC). Drift measured from t+2 -- the entire announcement
window is DISCARDED, so drift cannot be contaminated by it.

fetching earnings dates:
    TSM     99 dates  2000-04-25 -> 2026-10-15
    ORCL    98 dates  2002-06-18 -> 2026-09-10
    INTC    99 dates  2002-04-16 -> 2026-10-22
    MU     100 dates  2001-12-18 -> 2026-09-23

usable events: 392  (dropped 4 for short beta window, missing sessions, or zero announcement return)
span: 2000-04-25 -> 2026-07-23
mean |announcement AR| = 5.14%

  H    n    PEAD stat   p(sign-flip)  p(rotation)   hit
   1  392    +0.041%    0.7041        0.6895     50%
   5  392    +0.056%    0.8056        0.8082     53%
  10  392    -0.029%    0.9336        0.9424     49%
  20  391    -0.048%    0.9218        0.9232     49%

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
