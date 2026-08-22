# Drift-existence results (prereg 8273be4)

```
==============================================================================
DRIFT-EXISTENCE -- Event engine Stage 1, per prereg 8273be4
==============================================================================
gdelt window: 2024-01-01 -> 2026-08-18 | usable sessions: 659
B = 5000 | seed 42

REGISTERED SCOPE: macro narrative-density drift, NOT the PEAD analog.
A positive result does not discharge the entity-detection precondition;
a null does not close out firm-level drift.
PRE-DECLARED: a null at H=10 or H=20 is INCONCLUSIVE, not evidence of
absence (MDE ~1.6% / ~2.3% at ~25-35 episodes, above expected effects).

==============================================================================
ladder   z >= 1.0   ->  70 de-clustered episodes

  asset: SPY
    estimand  H   n   stat        p(matched)  p(rotation)  pool
    E1       1   70   +0.043%     0.8020      0.7638    16
    E1       5   69   +0.369%     0.0002      0.8762    11
    E1      10   69   +0.633%     0.0002      0.4743     7
    E1      20   68   +1.454%       n/a       nan     0
    E2       1   70   -0.213%     0.0642      0.0902    16
    E2       5   69   -0.442%     0.0008      0.0594    11
    E2      10   69   +0.017%     0.0002      0.9688     7
    E2      20   68   +0.152%       n/a       nan     0

  asset: DEF(TLT+GLD)-SPY
    estimand  H   n   stat        p(matched)  p(rotation)  pool
    E1       1   70   +0.147%     0.3191      0.1998    11
    E1       5   69   +0.113%     0.0022      0.1890    10
    E1      10   69   -0.034%     0.0002      0.4501    21
    E1      20   68   -0.503%       n/a       nan     0
    E2       1   70   +0.107%     0.8518      0.4185    11
    E2       5   69   +0.172%     0.0908      0.7694    10
    E2      10   69   +0.161%     0.0840      0.9114    21
    E2      20   68   +0.691%       n/a       nan     0

==============================================================================
PRIMARY  z >= 1.5   ->  37 de-clustered episodes

  asset: SPY
    estimand  H   n   stat        p(matched)  p(rotation)  pool
    E1       1   37   +0.103%     0.9990      0.8766    24
    E1       5   37   +0.268%     0.6249      0.6653    12
    E1      10   37   +0.462%     0.0002      0.4143    10
    E1      20   36   +1.564%       n/a       nan     0
    E2       1   37   -0.287%     0.0272      0.1308    24
    E2       5   37   -0.388%     0.0226      0.2675    12
    E2      10   37   +0.357%     0.5149      0.4437    10
    E2      20   36   +0.582%       n/a       nan     0

  asset: DEF(TLT+GLD)-SPY
    estimand  H   n   stat        p(matched)  p(rotation)  pool
    E1       1   37   +0.006%     0.7141      0.8506    22
    E1       5   37   +0.447%     0.0008      0.0842    13
    E1      10   37   +0.596%     0.0002      0.0540     8
    E1      20   36   +0.059%       n/a       nan     0
    E2       1   37   +0.224%     0.1830      0.2080    22
    E2       5   37   -0.250%     0.3987      0.3495    13
    E2      10   37   -0.762%     0.0326      0.0876     8
    E2      20   36   -0.476%       n/a       nan     0

==============================================================================
ladder   z >= 2.0   ->  14 de-clustered episodes

  asset: SPY
    estimand  H   n   stat        p(matched)  p(rotation)  pool
    E1       1   14   +0.373%     0.3483      0.2174    36
    E1       5   14   -0.260%     0.0758      0.1808    30
    E1      10   14   +0.143%     0.0710      0.3275    16
    E1      20   14   +1.641%     0.2168      0.8992    11
    E2       1   14   -0.614%     0.0036      0.0338    36  *
    E2       5   14   -0.903%     0.0340      0.0998    30
    E2      10   14   -0.351%     0.2112      0.6511    16
    E2      20   14   +0.402%     0.8336      0.7391    11

  asset: DEF(TLT+GLD)-SPY
    estimand  H   n   stat        p(matched)  p(rotation)  pool
    E1       1   14   -0.197%     0.5265      0.5781    26
    E1       5   14   +0.742%     0.0204      0.1368    23
    E1      10   14   +1.206%     0.0002      0.1188    27
    E1      20   14   -0.074%     0.1378      0.7544    18
    E2       1   14   +0.843%     0.0010      0.0094    26  *
    E2       5   14   -0.117%     0.6703      0.7311    23
    E2      10   14   -0.728%     0.2705      0.3169    27
    E2      20   14   +0.171%     0.7095      0.9130    18

==============================================================================
ladder   z >= 2.5   ->  7 de-clustered episodes

  asset: SPY
    estimand  H   n   stat        p(matched)  p(rotation)  pool
    E1       1    7   +1.049%     0.0156      0.0200    34  *
    E1       5    7   +0.609%     0.7307      0.7894    37
    E1      10    7   +1.912%     0.4037      0.2617    25
    E1      20    7   +2.622%     0.9718      0.4145    19
    E2       1    7   -1.079%     0.0004      0.0136    34  *
    E2       5    7   -0.636%     0.2164      0.3685    37
    E2      10    7   +0.260%     0.7165      0.7898    25
    E2      20    7   -0.181%     0.5695      0.8786    19

  asset: DEF(TLT+GLD)-SPY
    estimand  H   n   stat        p(matched)  p(rotation)  pool
    E1       1    7   -0.737%     0.0512      0.0962    22
    E1       5    7   +0.520%     0.1982      0.4947    22
    E1      10    7   +0.142%     0.1614      0.7305    22
    E1      20    7   +0.433%     0.1482      0.6137    21
    E2       1    7   +2.653%     0.0002      0.0002    22  *
    E2       5    7   +2.413%     0.0018      0.0210    22  *
    E2      10    7   +2.255%     0.1898      0.0934    22
    E2      20    7   +2.794%     0.0022      0.1910    21

==============================================================================
VERDICT against the registered criterion (§6)
  Requires p<0.05 under BOTH nulls, at TWO ADJACENT horizons, with
  consistent sign across ALL FOUR ladder rungs.
  SPY                  E1: NOT MET (0 horizon(s) clear both nulls, not adjacent)
  SPY                  E2: NOT MET (0 horizon(s) clear both nulls, not adjacent)
  DEF(TLT+GLD)-SPY     E1: NOT MET (0 horizon(s) clear both nulls, not adjacent)
  DEF(TLT+GLD)-SPY     E2: NOT MET (0 horizon(s) clear both nulls, not adjacent)

  OVERALL: NULL. No cell meets the registered criterion.
  H=10 and H=20 cells are pre-declared INCONCLUSIVE regardless of outcome.
  AMENDMENT 1 applied: control buffer H+2 rather than a flat 20 -- the
  registered buffer was infeasible on a 659-session panel (empty pools).
  Recorded before any result was read. All other parameters unchanged.
==============================================================================
```
