# Forward-test scoreboard (live, out-of-sample)

Pre-registered models frozen in `config/models.yaml` before any live data.
**Regime labels are canonically ordered by ascending mean PC1 from 2026-08-25.** Rows logged before that date carry the old arbitrary GMM component ordering, so the `regime` column is comparable within each era and NOT across the boundary. Historical rows are not retro-relabelled -- the ledger is never rewritten. Picks are unaffected: candidate selection uses label EQUALITY, which is invariant under relabelling.
Signal = last completed US close; **entry = next US session**; exit = H trading days later.
`pending` = horizon has not elapsed yet (expected on recent rows). `short_window` = the horizon elapsed but at least one session was missing data for at least one picked asset; the spread is shown with its realised session count and is EXCLUDED from the summary above.

## Running summary

| model | matured trades | mean spread | hit-rate | NON-OVERLAP trades | NON-OVERLAP mean spread |
|---|---|---|---|---|---|
| model_1_baseline | 6 | +3.231% | 100% | 2 | +3.501% |
| model_2_horizon_trend | 2 | -3.004% | 50% | 1 | +1.376% |
| model_3_overfit | 0 | – | – | 0 | – |

*Naive column counts overlapping daily entries (they share most of their days, so significance would be inflated). The NON-OVERLAP column samples every H-th trade and is the statistically honest one.*

## Full log

| signal date | entry date | model | regime | longs | shorts | H | status | spread |
|---|---|---|---|---|---|---|---|---|
| 2026-09-03 | 2026-09-04 | model_1_baseline | 3 | USO, PLTR, XLE, WCLD, SKYY | XSD, TSLA, SPCX, INTC, FLY | 5 | pending | pending |
| 2026-09-03 | 2026-09-04 | model_2_horizon_trend | 3 | DRAM, SNDK, ARM, MU, CIBR | SLV, REMX, INTC, URNM, URA | 10 | pending | pending |
| 2026-09-03 | 2026-09-04 | model_3_overfit | 3 | SNDK, DRAM, MU, ARM, PLTR | URA, URNM, USO, REMX, FLY | 20 | pending | pending |
| 2026-09-02 | 2026-09-03 | model_1_baseline | 3 | PLTR, MU, URA, ARM, ORCL | LMT, TSLA, INTC, SPCX, FLY | 5 | pending | pending |
| 2026-09-02 | 2026-09-03 | model_2_horizon_trend | 3 | DRAM, SNDK, ARM, MU, PLTR | LMT, URNM, FLY, SLV, USO | 10 | pending | pending |
| 2026-09-02 | 2026-09-03 | model_3_overfit | 3 | SNDK, DRAM, MU, ARM, PLTR | SLV, LMT, USO, SPCX, FLY | 20 | pending | pending |
| 2026-09-01 | 2026-09-02 | model_1_baseline | 3 | PLTR, USO, XLE, WCLD, XLV | TSLA, ARM, SPCX, INTC, FLY | 5 | pending | pending |
| 2026-09-01 | 2026-09-02 | model_2_horizon_trend | 3 | SNDK, DRAM, ARM, MU, HACK | INTC, URA, URNM, FLY, SPCX | 10 | pending | pending |
| 2026-09-01 | 2026-09-02 | model_3_overfit | 3 | SNDK, DRAM, MU, PLTR, ARM | REMX, URA, URNM, FLY, SPCX | 20 | pending | pending |
| 2026-08-31 | 2026-09-01 | model_1_baseline | 3 | USO, PLTR, XLE, WCLD, XLV | TSLA, ARM, SPCX, INTC, FLY | 5 | pending | pending |
| 2026-08-31 | 2026-09-01 | model_2_horizon_trend | 3 | SNDK, ARM, MU, PLTR, HACK | URA, URNM, ORCL, FLY, SPCX | 10 | pending | pending |
| 2026-08-31 | 2026-09-01 | model_3_overfit | 3 | SNDK, MU, PLTR, DRAM, ARM | ORCL, URA, URNM, FLY, SPCX | 20 | pending | pending |
| 2026-08-28 | 2026-08-31 | model_1_baseline | 3 | SNDK, USO, XLE, XLV, SKYY | TSLA, INTC, ARM, SPCX, FLY | 5 | pending | pending |
| 2026-08-28 | 2026-08-31 | model_2_horizon_trend | 3 | SNDK, MU, DRAM, SLV, ASML | JETS, WCLD, TSLA, ORCL, FLY | 10 | pending | pending |
| 2026-08-28 | 2026-08-31 | model_3_overfit | 3 | SNDK, MU, DRAM, ASML, PLTR | URNM, REMX, WCLD, ORCL, FLY | 20 | pending | pending |
| 2026-08-27 | 2026-08-28 | model_1_baseline | 3 | USO, PLTR, XLE, XLV, WCLD | TSLA, ARM, INTC, SPCX, FLY | 5 | pending | pending |
| 2026-08-27 | 2026-08-28 | model_2_horizon_trend | 3 | SNDK, DRAM, MU, ASML, SLV | USO, WCLD, SPCX, TSLA, FLY | 10 | pending | pending |
| 2026-08-27 | 2026-08-28 | model_3_overfit | 3 | SNDK, MU, DRAM, PLTR, ASML | MSFT, WCLD, ORCL, TSLA, FLY | 20 | pending | pending |
| 2026-08-25 | 2026-08-26 | model_1_baseline | 3 | PLTR, MU, USO, ORCL, XLE | LMT, TSLA, INTC, FLY, SPCX | 5 | matured | +2.956% |
| 2026-08-25 | 2026-08-26 | model_2_horizon_trend | 3 | SNDK, DRAM, MU, SLV, INTC | JETS, USO, WCLD, TSLA, FLY | 10 | pending | pending |
| 2026-08-25 | 2026-08-26 | model_3_overfit | 3 | SNDK, MU, INTC, DRAM, PLTR | UUP, MSFT, WCLD, TSLA, FLY | 20 | pending | pending |
| 2026-08-24 | 2026-08-25 | model_1_baseline | 3 | USO, PLTR, XLE, XLV, MU | TSLA, ARM, INTC, SPCX, FLY | 5 | matured | +4.412% |
| 2026-08-24 | 2026-08-25 | model_2_horizon_trend | 3 | SNDK, DRAM, MU, INTC, SLV | WCLD, JETS, MSFT, TSLA, FLY | 10 | pending | pending |
| 2026-08-24 | 2026-08-25 | model_3_overfit | 3 | SNDK, DRAM, MU, PLTR, ASML | ORCL, MSFT, WCLD, TSLA, FLY | 20 | pending | pending |
| 2026-08-21 | 2026-08-24 | model_1_baseline | 0 | MU, PLTR, ORCL, USO, DRAM | SLV, TSLA, INTC, FLY, SPCX | 5 | matured | +3.879% |
| 2026-08-21 | 2026-08-24 | model_2_horizon_trend | 0 | SNDK, MU, DRAM, SLV, TSM | UUP, WCLD, TSLA, SPCX, FLY | 10 | pending | pending |
| 2026-08-21 | 2026-08-24 | model_3_overfit | 0 | SNDK, MU, PLTR, ASML, INTC | MSFT, TLT, WCLD, TSLA, FLY | 20 | pending | pending |
| 2026-08-20 | 2026-08-21 | model_1_baseline | 0 | SNDK, USO, ORCL, PLTR, XLE | ARM, TSLA, INTC, SPCX, FLY | 5 | matured | +2.139% |
| 2026-08-20 | 2026-08-21 | model_2_horizon_trend | 0 | SNDK, MU, PLTR, SLV, TSM | TSLA, MSFT, JETS, WCLD, FLY | 10 | pending | pending |
| 2026-08-20 | 2026-08-21 | model_3_overfit | 0 | SNDK, MU, INTC, PLTR, SLV | TLT, UUP, MSFT, WCLD, FLY | 20 | pending | pending |
| 2026-08-19 | 2026-08-20 | model_1_baseline | 1 | USO, PLTR, XLE, WCLD, SKYY | ARM, INTC, TSLA, SPCX, FLY | 5 | matured | +1.955% |
| 2026-08-19 | 2026-08-20 | model_2_horizon_trend | 1 | SNDK, DRAM, MU, ASML, IAU | NVDA, ORCL, TSLA, FLY, SPCX | 10 | matured | -7.383% |
| 2026-08-19 | 2026-08-20 | model_3_overfit | 1 | SNDK, DRAM, MU, PLTR, ASML | URNM, ORCL, USO, TSLA, FLY | 20 | pending | pending |
| 2026-08-18 | 2026-08-19 | model_1_baseline | 1 | MU, PLTR, ORCL, USO, DRAM | SLV, TSLA, INTC, FLY, SPCX | 5 | matured | +4.045% |
| 2026-08-18 | 2026-08-19 | model_2_horizon_trend | 1 | SNDK, MU, DRAM, TSM, LMT | ORCL, WCLD, TSLA, FLY, SPCX | 10 | matured | +1.376% |
| 2026-08-18 | 2026-08-19 | model_3_overfit | 1 | SNDK, MU, DRAM, PLTR, ASML | URNM, MSFT, WCLD, TSLA, FLY | 20 | pending | pending |
