# Forward-test scoreboard (live, out-of-sample)

Pre-registered models frozen in `config/models.yaml` before any live data.
Signal = last completed US close; **entry = next US session**; exit = H trading days later.
`pending` = horizon has not elapsed yet (expected on recent rows).

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
| 2026-08-14 | 2026-08-17 | model_1_baseline | 1 | USO, ORCL, PLTR, XLE, SKYY | TSLA, INTC, DRAM, SPCX, FLY | 5 | pending | pending |
| 2026-08-14 | 2026-08-17 | model_2_horizon_trend | 1 | SNDK, PLTR, MU, INTC, ASML | TSLA, ORCL, ARM, URNM, FLY | 10 | pending | pending |
| 2026-08-14 | 2026-08-17 | model_3_overfit | 1 | SNDK, MU, INTC, LMT, IAU | WCLD, ORCL, USO, ARM, FLY | 20 | pending | pending |
