# Input latency audit

*2026-11-26 15:12. Last completed NYSE session: 2026-11-25. Lag = sessions the series is behind it at run time. Flag rule (TRACK 3.27): ≥ 2 sessions behind on ≥ 20% of the last 20 runs → STALE. Runs on record: 20.*

| file | series | last date this run | lag now | runs seen | share ≥ 2 behind | flag |
|---|---|---|---|---|---|---|
| asset_returns.parquet | SPY | 2026-11-24 | 1 | 20 | 5% |  |
| asset_returns.parquet | TLT | 2026-11-24 | 1 | 20 | 5% |  |
| asset_returns.parquet | GLD | 2026-11-24 | 1 | 20 | 10% |  |
| asset_returns.parquet | UUP | 2026-11-24 | 1 | 20 | 5% |  |
| asset_returns.parquet | USO | 2026-11-24 | 1 | 20 | 5% |  |
| wti_cont.parquet | WTI_SPOT | 2026-11-20 | 3 | 20 | 30% | STALE |
| wti_cont.parquet | WTI_FUT | 2026-11-25 | 0 | 20 | 0% |  |
| wti_cont.parquet | USO | 2026-11-24 | 1 | 20 | 10% |  |
| raw/yfinance | GLD | 2026-11-24 | 1 | 20 | 15% |  |
| raw/yfinance | SPY | 2026-11-24 | 1 | 20 | 10% |  |
| raw/yfinance | TLT | 2026-11-24 | 1 | 20 | 10% |  |
| raw/yfinance | USO | 2026-11-24 | 1 | 20 | 10% |  |
| raw/yfinance | UUP | 2026-11-24 | 1 | 20 | 10% |  |
| raw/fred | DFII10 | 2026-11-23 | 2 | 20 | 25% | STALE |
| raw/fred | DGS10 | 2026-11-23 | 2 | 20 | 25% | STALE |
| raw/fred | DGS2 | 2026-11-23 | 2 | 20 | 25% | STALE |
| raw/fred | DTWEXBGS | 2026-11-20 | 3 | 20 | 80% | STALE |
| raw/fred | EFFR | 2026-11-23 | 2 | 20 | 25% | STALE |
| raw/fred | M2SL | 2026-10-01 | 39 | 20 | 100% | STALE |
| raw/fred | SOFR | 2026-07-02 | 104 | 20 | 100% | STALE |
| raw/fred | T10Y2Y | 2026-11-24 | 1 | 20 | 5% |  |
| raw/fred | VIXCLS | 2026-11-23 | 2 | 20 | 20% | STALE |
| yahoo-live | SPY |  |  | 20 | 0% |  |
| yahoo-live | GLD |  |  | 20 | 0% |  |
| yahoo-live | USO |  |  | 20 | 0% |  |
| yahoo-live | TLT |  |  | 20 | 0% |  |
| yahoo-live | UUP |  |  | 20 | 0% |  |
| yahoo-live | ^TNX |  |  | 20 | 0% |  |
| yahoo-live | DX-Y.NYB |  |  | 20 | 0% |  |
| yahoo-live | CL=F |  |  | 20 | 0% |  |
| yahoo-live | SI=F |  |  | 20 | 0% |  |

Reading: raw/fred and raw/yfinance are what the nightly --force refresh actually received (no forward-fill). A lag of 1 on FRED series is their publication schedule, declared where it matters (the oil leg's provisional flag). A lag of 1 on the price panel at the nightly run time means the download missed the latest close — the fault seen on 16 and 21 Oct 2026. Backtests are unaffected by latency only where the backfill used the same as-of alignment; that is checked per flagged series.
