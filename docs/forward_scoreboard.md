# Forward-test scoreboard (live, out-of-sample)

Pre-registered models frozen in `config/models.yaml` before any live data.
Signal = last completed US close; **entry = next US session**; exit = H trading days later.
`pending` = horizon has not elapsed yet (expected on recent rows). `short_window` = the horizon elapsed but at least one session was missing data for at least one picked asset; the spread is shown with its realised session count and is EXCLUDED from the summary above.

## Running summary

| model | matured trades | mean spread | hit-rate | NON-OVERLAP trades | NON-OVERLAP mean spread |
|---|---|---|---|---|---|
| model_1_baseline | 0 | – | – | 0 | – |
| model_2_horizon_trend | 0 | – | – | 0 | – |
| model_3_overfit | 0 | – | – | 0 | – |

*Naive column counts overlapping daily entries (they share most of their days, so significance would be inflated). The NON-OVERLAP column samples every H-th trade and is the statistically honest one.*

## Full log

| signal date | entry date | model | regime | longs | shorts | H | status | spread |
|---|---|---|---|---|---|---|---|---|
| 2026-08-21 |  | model_1_baseline | 0 | MU, PLTR, ORCL, USO, DRAM | SLV, TSLA, INTC, FLY, SPCX | 5 | pending | pending |
| 2026-08-21 |  | model_2_horizon_trend | 0 | SNDK, MU, DRAM, SLV, TSM | UUP, WCLD, TSLA, SPCX, FLY | 10 | pending | pending |
| 2026-08-21 |  | model_3_overfit | 0 | SNDK, MU, PLTR, ASML, INTC | MSFT, TLT, WCLD, TSLA, FLY | 20 | pending | pending |
| 2026-08-20 | 2026-08-21 | model_1_baseline | 0 | SNDK, USO, ORCL, PLTR, XLE | ARM, TSLA, INTC, SPCX, FLY | 5 | pending | pending |
| 2026-08-20 | 2026-08-21 | model_2_horizon_trend | 0 | SNDK, MU, PLTR, SLV, TSM | TSLA, MSFT, JETS, WCLD, FLY | 10 | pending | pending |
| 2026-08-20 | 2026-08-21 | model_3_overfit | 0 | SNDK, MU, INTC, PLTR, SLV | TLT, UUP, MSFT, WCLD, FLY | 20 | pending | pending |
| 2026-08-19 | 2026-08-20 | model_1_baseline | 1 | USO, PLTR, XLE, WCLD, SKYY | ARM, INTC, TSLA, SPCX, FLY | 5 | pending | pending |
| 2026-08-19 | 2026-08-20 | model_2_horizon_trend | 1 | SNDK, DRAM, MU, ASML, IAU | NVDA, ORCL, TSLA, FLY, SPCX | 10 | pending | pending |
| 2026-08-19 | 2026-08-20 | model_3_overfit | 1 | SNDK, DRAM, MU, PLTR, ASML | URNM, ORCL, USO, TSLA, FLY | 20 | pending | pending |
| 2026-08-18 | 2026-08-19 | model_1_baseline | 1 | MU, PLTR, ORCL, USO, DRAM | SLV, TSLA, INTC, FLY, SPCX | 5 | pending | pending |
| 2026-08-18 | 2026-08-19 | model_2_horizon_trend | 1 | SNDK, MU, DRAM, TSM, LMT | ORCL, WCLD, TSLA, FLY, SPCX | 10 | pending | pending |
| 2026-08-18 | 2026-08-19 | model_3_overfit | 1 | SNDK, MU, DRAM, PLTR, ASML | URNM, MSFT, WCLD, TSLA, FLY | 20 | pending | pending |
