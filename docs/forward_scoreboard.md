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
| 2026-08-18 | 2026-08-19 | model_1_baseline | 1 | MU, PLTR, ORCL, USO, DRAM | SLV, TSLA, INTC, FLY, SPCX | 5 | pending | pending |
| 2026-08-18 | 2026-08-19 | model_2_horizon_trend | 1 | SNDK, MU, DRAM, TSM, LMT | ORCL, WCLD, TSLA, FLY, SPCX | 10 | pending | pending |
| 2026-08-18 | 2026-08-19 | model_3_overfit | 1 | SNDK, MU, DRAM, PLTR, ASML | URNM, MSFT, WCLD, TSLA, FLY | 20 | pending | pending |
