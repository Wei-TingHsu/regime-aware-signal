# Input latency audit

*2026-10-27 15:02. Last completed NYSE session: 2026-10-26. Lag = sessions the series is behind it at run time. Flag rule (TRACK 3.27): ≥ 2 sessions behind on ≥ 20% of the last 20 runs → STALE. Runs on record: 5.*

| file | series | last date this run | lag now | runs seen | share ≥ 2 behind | flag |
|---|---|---|---|---|---|---|
| asset_returns.parquet | SPY | 2026-10-26 | 0 | 5 | 0% |  |
| asset_returns.parquet | TLT | 2026-10-26 | 0 | 5 | 0% |  |
| asset_returns.parquet | GLD | 2026-10-26 | 0 | 5 | 0% |  |
| asset_returns.parquet | UUP | 2026-10-26 | 0 | 5 | 0% |  |
| asset_returns.parquet | USO | 2026-10-26 | 0 | 5 | 0% |  |
| macro_panel.parquet | DGS10 | 2026-10-22 | 0 | 1 | 0% |  |
| macro_panel.parquet | DFII10 | 2026-10-22 | 0 | 1 | 0% |  |
| macro_panel.parquet | T10Y2Y | 2026-10-22 | 0 | 1 | 0% |  |
| macro_panel.parquet | DGS2 | 2026-10-22 | 0 | 1 | 0% |  |
| macro_panel.parquet | M2SL | 2026-10-22 | 0 | 1 | 0% |  |
| macro_panel.parquet | EFFR | 2026-10-22 | 0 | 1 | 0% |  |
| macro_panel.parquet | VIXCLS | 2026-10-22 | 0 | 1 | 0% |  |
| macro_panel.parquet | DTWEXBGS | 2026-10-22 | 0 | 1 | 0% |  |
| wti_cont.parquet | WTI_SPOT | 2026-10-23 | 1 | 5 | 40% | STALE |
| wti_cont.parquet | WTI_FUT | 2026-10-27 | 0 | 5 | 40% | STALE |
| wti_cont.parquet | USO | 2026-10-26 | 0 | 5 | 40% | STALE |
| yahoo-live | SPY | 2026-10-26 | 0 | 5 | 0% |  |
| yahoo-live | GLD | 2026-10-26 | 0 | 5 | 0% |  |
| yahoo-live | USO | 2026-10-26 | 0 | 5 | 0% |  |
| yahoo-live | TLT | 2026-10-26 | 0 | 5 | 0% |  |
| yahoo-live | UUP | 2026-10-26 | 0 | 5 | 0% |  |
| yahoo-live | ^TNX | 2026-10-26 | 0 | 5 | 0% |  |
| yahoo-live | DX-Y.NYB | 2026-10-27 | 0 | 5 | 0% |  |
| yahoo-live | CL=F | 2026-10-27 | 0 | 5 | 0% |  |
| yahoo-live | SI=F | 2026-10-27 | 0 | 5 | 0% |  |
| raw/yfinance | GLD | 2026-10-26 | 0 | 4 | 0% |  |
| raw/yfinance | SPY | 2026-10-26 | 0 | 4 | 0% |  |
| raw/yfinance | TLT | 2026-10-26 | 0 | 4 | 0% |  |
| raw/yfinance | USO | 2026-10-26 | 0 | 4 | 0% |  |
| raw/yfinance | UUP | 2026-10-26 | 0 | 4 | 0% |  |
| raw/fred | DFII10 | 2026-10-23 | 1 | 4 | 0% |  |
| raw/fred | DGS10 | 2026-10-23 | 1 | 4 | 0% |  |
| raw/fred | DGS2 | 2026-10-23 | 1 | 4 | 0% |  |
| raw/fred | DTWEXBGS | 2026-10-23 | 1 | 4 | 75% |  |
| raw/fred | EFFR | 2026-10-23 | 1 | 4 | 0% |  |
| raw/fred | M2SL | 2026-08-01 | 60 | 4 | 100% |  |
| raw/fred | SOFR | 2026-07-02 | 82 | 4 | 100% |  |
| raw/fred | T10Y2Y | 2026-10-26 | 0 | 4 | 0% |  |
| raw/fred | VIXCLS | 2026-10-23 | 1 | 4 | 0% |  |

Reading: raw/fred and raw/yfinance are what the nightly --force refresh actually received (no forward-fill). A lag of 1 on FRED series is their publication schedule, declared where it matters (the oil leg's provisional flag). A lag of 1 on the price panel at the nightly run time means the download missed the latest close — the fault seen on 16 and 21 Oct 2026. Backtests are unaffected by latency only where the backfill used the same as-of alignment; that is checked per flagged series.
