# fomc_minutes contrarian -- forward-only test

*Registered docs/overlays/fomc_minutes_contrarian.md. Forward ledger only; the backfill rows that produced the 37.8% observation are excluded by construction. Minimum 30 non-overlap rows. Criterion: hit-rate below the within-asset null's 5th percentile.*

- matured forward calls with `fomc_minutes` dominant at h=3: **0** (non-overlap **0**)
- verdict: **too few to report (0 of 30 non-overlap rows)**

No figure is printed below the minimum. Rows accumulate only while nightly reads are running (paused for credit as of 15 Sep 2026).
