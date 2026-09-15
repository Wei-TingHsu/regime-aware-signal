# Overlay registration — fomc_minutes contrarian (FORWARD-ONLY)

**Registered 2026-09-15, before any second look at the data that produced it.**

hypothesis:  on sessions where `fomc_minutes` is the dominant source for asset a, the report's
             net_view sign is WRONG more often than chance: forward non-overlap hit-rate at h=3
             below the within-asset block-permutation null's 5th percentile (one-sided, 10,000 draws).
origin:      backfill 986e0d65b6df_n2616, 14 Sep 2026: 37.8% on 74 rows. Found by looking; not a finding.
data:        FORWARD ONLY -- processed/report_ledger.csv, write-once reports. The backfill rows that
             produced the observation are excluded by construction; no chronological re-cut of the
             backfill counts as a test.
minimum:     30 non-overlap forward rows (~1 year at 8 minutes releases/yr x 5 assets, once reads resume).
falsifier:   hit-rate at or above the null's 5th percentile after 30 rows -> hypothesis dropped.
             Below it -> registered as an overlay RULE (take the opposite side, size 0.25 x T1 dial),
             never as a change to the reader or its prompt.
code:        src/fomc_minutes_forward.py -- prints "too few to report" until the minimum; writes
             docs/fomc_minutes_forward.md.
blocked by:  nightly reads (paused for credit): no minutes-driven calls are generated until they resume.
