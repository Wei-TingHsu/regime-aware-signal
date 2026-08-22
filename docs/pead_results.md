# PEAD results

```
==============================================================================
PEAD -- post-earnings announcement drift (firm-level event test)
==============================================================================
universe: NVDA, TSM, ASML, MU, INTC, MSFT, ORCL, PLTR, TSLA, ARM, LMT, SNDK
market proxy: SPY | beta: trailing 250 frozen at t
iters 5000 | seed 42

Announcement response measured over {t, t+1} COMBINED (yfinance does
not flag BMO/AMC). Drift measured from t+2 -- the entire announcement
window is DISCARDED, so drift cannot be contaminated by it.

fetching earnings dates:
    NVDA    97 dates  2002-05-22 -> 2026-08-26
    TSM     99 dates  2000-04-25 -> 2026-10-15
    ASML   100 dates  2001-01-18 -> 2026-10-14
    MU     100 dates  2001-12-18 -> 2026-09-23
    INTC    99 dates  2002-04-16 -> 2026-10-22
    MSFT   100 dates  2002-01-17 -> 2026-10-28
    ORCL    98 dates  2002-06-18 -> 2026-09-10
    PLTR    25 dates  2020-11-12 -> 2026-11-02
    TSLA    65 dates  2010-11-09 -> 2026-10-21
    ARM     13 dates  2023-11-09 -> 2026-11-04
    LMT    100 dates  2002-01-25 -> 2026-10-20
    SNDK     7 dates  2025-05-07 -> 2026-11-06

usable events: 876  (dropped 27 for short beta window, missing sessions, or zero announcement return)
span: 2000-04-25 -> 2026-08-05
mean |announcement AR| = 5.37%

  H    n    PEAD stat   p(sign-flip)  p(rotation)   hit
   1  876    +0.239%    0.0032        0.0040     53%  *
   5  876    +0.226%    0.1522        0.1414     55%
  10  876    +0.223%    0.3129        0.3537     52%
  20  870    +0.500%    0.1152        0.1178     52%

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
