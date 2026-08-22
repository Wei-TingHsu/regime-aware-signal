# PEAD results

```
==============================================================================
PEAD -- post-earnings announcement drift (firm-level event test)
==============================================================================
universe: NVDA, MSFT, ASML, LMT
market proxy: SPY | beta: trailing 250 frozen at t
iters 5000 | seed 42

Announcement response measured over {t, t+1} COMBINED (yfinance does
not flag BMO/AMC). Drift measured from t+2 -- the entire announcement
window is DISCARDED, so drift cannot be contaminated by it.

fetching earnings dates:
    NVDA    97 dates  2002-05-22 -> 2026-08-26
    MSFT   100 dates  2002-01-17 -> 2026-10-28
    ASML   100 dates  2001-01-18 -> 2026-10-14
    LMT    100 dates  2002-01-25 -> 2026-10-20

usable events: 393  (dropped 4 for short beta window, missing sessions, or zero announcement return)
span: 2001-01-18 -> 2026-07-29
mean |announcement AR| = 4.84%

  H    n    PEAD stat   p(sign-flip)  p(rotation)   hit
   1  393    +0.180%    0.0898        0.0930     53%
   5  393    +0.186%    0.3613        0.3309     56%
  10  393    -0.109%    0.7199        0.6809     53%
  20  391    +0.331%    0.4155        0.3929     53%

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
