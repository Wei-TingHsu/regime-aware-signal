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

  peer     component      n    stat      p(flip)  p(perm)
  TSM        GAP                96   +0.194%  0.1738   0.1786
  TSM      INTRA                96   +0.594%  0.0006   0.0002 *
  TSM       NEXT                96   +0.069%  0.6875   0.4541
  ASML       GAP                96   +0.373%  0.0042   0.0048 *
  ASML     INTRA                96   +0.538%  0.0004   0.0010 *
  ASML      NEXT                96   +0.096%  0.6369   0.5969
  MU         GAP                96   +0.598%  0.0002   0.0002 *
  MU       INTRA                96   +0.527%  0.0202   0.0116 *
  MU        NEXT                96   +0.136%  0.6161   0.6149
  INTC       GAP                96   +0.036%  0.7277   0.8074
  INTC     INTRA                96   +0.184%  0.1830   0.0928
  INTC      NEXT                96   +0.057%  0.7481   0.7357
  SOXX       GAP                96   +0.416%  0.0002   0.0002 *
  SOXX     INTRA                96   +0.598%  0.0002   0.0002 *
  SOXX      NEXT                96   +0.184%  0.1970   0.1724
  SMH        GAP                96   +0.486%  0.0002   0.0002 *
  SMH      INTRA                96   +0.455%  0.0016   0.0008 *
  SMH       NEXT                96   +0.150%  0.2669   0.2278
  XSD        GAP                81   +0.411%  0.0002   0.0002 *
  XSD      INTRA                81   +0.339%  0.0458   0.0252 *
  XSD       NEXT                81   +0.061%  0.7007   0.7483
  NVDA       GAP  (announcer)   96   +4.788%  0.0002   0.0002 *
  NVDA     INTRA  (announcer)   96   +2.319%  0.0002   0.0002 *
  NVDA      NEXT  (announcer)   96   +0.180%  0.6621   0.5023

==============================================================================
READING
  peers with significant GAP:   5/7
  peers with significant INTRA: 6/7   <-- the capturable one
  peers with significant NEXT:  0/7

  RESIDUAL AFTER THE OPEN. Some spillover is still available to a
  trader entering at the bell. Before this means anything: (a) it is
  an UPPER BOUND -- a real fill is not the printed open; (b) it needs
  the transaction-cost test the rotation pairs got; (c) it needs a
  temporal split, which is what killed SPY->GLD and SOXX->XAR.

  Multiple testing: 21 peer-component cells, ~1.1
  false positives expected at alpha=0.05. Read the pattern, not one cell.
  Announcer's own rows are the coherence check: if the announcer shows
  no GAP, the timing inference failed and nothing else is meaningful.
==============================================================================
```
