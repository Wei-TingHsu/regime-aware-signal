# Earnings spillover -- NVDA

```
==============================================================================
EARNINGS SPILLOVER -- NVDA announces; do its links move, and is any of
it capturable AFTER the open?
==============================================================================
announcer: NVDA | peers: TSM, ASML, MU, INTC, SOXX, SMH, XSD | market: SPY
iters 5000 | seed 42

GAP   = open(N)/close(N-1)-1   priced before anyone can act
INTRA = close(N)/open(N)-1     available AFTER the open  <-- the question
NEXT  = close(N+1)/close(N)-1  next-session drift
All market-adjusted by SPY over the SAME window.

fetching adjusted OHLC ...
NVDA: 97 earnings dates 2002-05-22 -> 2026-08-26

usable events: 96   timing split: 14 before-open, 82 after-close
mean |NVDA surprise| = 7.13%

  signal used per component:
    GAP        <- SIG_FULL   descriptive co-movement, never a trade
    INTRA_LA   <- SIG_FULL   LOOK-AHEAD, shown only for comparison
    INTRA      <- SIG_GAP    TRADEABLE: signal known at the open
    NEXT       <- SIG_FULL   tradeable: signal known at close(N)

  peer     component      n    stat      p(flip)  p(perm)
  TSM          GAP                96   +0.194%  0.1738   0.1786
  TSM     INTRA_LA                96   +0.594%  0.0006   0.0002 *
  TSM        INTRA                96   +0.235%  0.1850   0.1548
  TSM         NEXT                96   +0.069%  0.7119   0.4559
  ASML         GAP                96   +0.373%  0.0046   0.0026 *
  ASML    INTRA_LA                96   +0.538%  0.0006   0.0004 *
  ASML       INTRA                96   +0.032%  0.8600   0.7970
  ASML        NEXT                96   +0.096%  0.6501   0.5797
  MU           GAP                96   +0.598%  0.0002   0.0002 *
  MU      INTRA_LA                96   +0.527%  0.0218   0.0154 *
  MU         INTRA                96   -0.210%  0.3609   0.4837
  MU          NEXT                96   +0.136%  0.6137   0.6075
  INTC         GAP                96   +0.036%  0.7231   0.8124
  INTC    INTRA_LA                96   +0.184%  0.1786   0.0988
  INTC       INTRA                96   -0.133%  0.3401   0.6329
  INTC        NEXT                96   +0.057%  0.7500   0.7576
  SOXX         GAP                96   +0.416%  0.0002   0.0002 *
  SOXX    INTRA_LA                96   +0.598%  0.0002   0.0004 *
  SOXX       INTRA                96   -0.089%  0.5891   0.7353
  SOXX        NEXT                96   +0.184%  0.2048   0.1770
  SMH          GAP                96   +0.486%  0.0002   0.0002 *
  SMH     INTRA_LA                96   +0.455%  0.0020   0.0012 *
  SMH        INTRA                96   -0.142%  0.3547   0.4117
  SMH         NEXT                96   +0.150%  0.2725   0.2396
  XSD          GAP                81   +0.411%  0.0002   0.0002 *
  XSD     INTRA_LA                81   +0.339%  0.0436   0.0260 *
  XSD        INTRA                81   -0.230%  0.1868   0.3367
  XSD         NEXT                81   +0.061%  0.7165   0.7489
  NVDA         GAP  (announcer)   96   +4.788%  0.0002   0.0002 *
  NVDA    INTRA_LA  (announcer)   96   +2.319%  0.0002   0.0002 *
  NVDA       INTRA  (announcer)   96   +0.012%  0.9756   0.8734
  NVDA        NEXT  (announcer)   96   +0.180%  0.6643   0.5159

==============================================================================
READING
  peers with significant GAP:   5/7
  peers with significant INTRA_LA: 6/7  (look-ahead, NOT a result)
  peers with significant INTRA: 0/7   <-- the capturable one
  peers with significant NEXT:  0/7

  PROPAGATION IS INSTANT. The links reprice in the overnight gap and
  nothing survives the open. This is efficient pricing MEASURED, not
  assumed -- and it explains why every t+2 test was null: by then it
  was already over. No tradeable spillover.

  Multiple testing: 28 peer-component cells, ~1.4
  false positives expected at alpha=0.05. Read the pattern, not one cell.
  Announcer's own rows are the coherence check: if the announcer shows
  no GAP, the timing inference failed and nothing else is meaningful.
==============================================================================
```
