# Forward-test scoreboard (live, out-of-sample)

Pre-registered models frozen in `config/models.yaml` before any live data.
**Regime labels are canonically ordered by ascending mean PC1 from 2026-08-25.** Rows logged before that date carry the old arbitrary GMM component ordering, so the `regime` column is comparable within each era and NOT across the boundary. Historical rows are not retro-relabelled -- the ledger is never rewritten. Picks are unaffected: candidate selection uses label EQUALITY, which is invariant under relabelling.
Signal = last completed US close; **entry = next US session**; exit = H trading days later.
`pending` = horizon has not elapsed yet (expected on recent rows). `short_window` = the horizon elapsed but at least one session was missing data for at least one picked asset; the spread is shown with its realised session count and is EXCLUDED from the summary above.

## Running summary

| model | matured trades | mean spread | hit-rate | NON-OVERLAP trades | NON-OVERLAP mean spread |
|---|---|---|---|---|---|
| model_1_baseline | 28 | +1.906% | 68% | 6 | +2.041% |
| model_2_horizon_trend | 23 | +4.985% | 83% | 3 | +5.690% |
| model_3_overfit | 13 | +11.072% | 100% | 1 | +3.487% |

*Naive column counts overlapping daily entries (they share most of their days, so significance would be inflated). The NON-OVERLAP column samples every H-th trade and is the statistically honest one.*

## Full log

| signal date | entry date | model | regime | longs | shorts | H | status | spread |
|---|---|---|---|---|---|---|---|---|
| 2026-10-06 | 2026-10-07 | model_1_baseline | 3 | PLTR, SPCX, MSFT, FLY, NVDA | SLV, TLT, UFO, JETS, REMX | 5 | pending | pending |
| 2026-10-06 | 2026-10-07 | model_2_horizon_trend | 3 | DRAM, SNDK, MU, ARM, FLY | SLV, XLP, TSLA, REMX, SPCX | 10 | pending | pending |
| 2026-10-06 | 2026-10-07 | model_3_overfit | 3 | DRAM, SNDK, MU, PLTR, NVDA | UFO, TSLA, JETS, REMX, FLY | 20 | pending | pending |
| 2026-10-05 | 2026-10-06 | model_1_baseline | 3 | PLTR, SPCX, MSFT, FLY, NVDA | ARM, TLT, UFO, JETS, REMX | 5 | pending | pending |
| 2026-10-05 | 2026-10-06 | model_2_horizon_trend | 3 | DRAM, MU, SNDK, ARM, FLY | USO, XLP, TSLA, REMX, SPCX | 10 | pending | pending |
| 2026-10-05 | 2026-10-06 | model_3_overfit | 3 | DRAM, SNDK, MU, PLTR, NVDA | XLP, UFO, JETS, REMX, FLY | 20 | pending | pending |
| 2026-10-02 | 2026-10-05 | model_1_baseline | 3 | PLTR, MSFT, SPCX, NVDA, TSM | ARM, TLT, UFO, JETS, REMX | 5 | pending | pending |
| 2026-10-02 | 2026-10-05 | model_2_horizon_trend | 3 | ARM, PLTR, MU, DRAM, NVDA | XLP, USO, SPCX, REMX, TSLA | 10 | pending | pending |
| 2026-10-02 | 2026-10-05 | model_3_overfit | 3 | SNDK, DRAM, SPCX, PLTR, MU | USO, JETS, UFO, REMX, FLY | 20 | pending | pending |
| 2026-10-01 | 2026-10-02 | model_1_baseline | 3 | PLTR, FLY, MSFT, SPCX, MU | TLT, DRAM, SNDK, TSLA, REMX | 5 | pending | pending |
| 2026-10-01 | 2026-10-02 | model_2_horizon_trend | 3 | DRAM, PLTR, ARM, MU, NVDA | XLP, SLV, SPCX, USO, REMX | 10 | pending | pending |
| 2026-10-01 | 2026-10-02 | model_3_overfit | 3 | DRAM, SNDK, PLTR, MU, NVDA | LMT, UFO, REMX, USO, FLY | 20 | pending | pending |
| 2026-09-30 | 2026-10-01 | model_1_baseline | 3 | PLTR, FLY, MSFT, MU, SPCX | XLP, TLT, TSLA, JETS, REMX | 5 | pending | pending |
| 2026-09-30 | 2026-10-01 | model_2_horizon_trend | 3 | DRAM, ARM, NVDA, PLTR, MU | XLE, LMT, USO, REMX, SPCX | 10 | pending | pending |
| 2026-09-30 | 2026-10-01 | model_3_overfit | 3 | DRAM, SNDK, PLTR, NVDA, MU | REMX, XLV, LMT, USO, FLY | 20 | pending | pending |
| 2026-09-29 | 2026-09-30 | model_1_baseline | 3 | PLTR, SPCX, FLY, MSFT, ORCL | XLP, UFO, TLT, JETS, REMX | 5 | pending | pending |
| 2026-09-29 | 2026-09-30 | model_2_horizon_trend | 3 | DRAM, ARM, FLY, NVDA, SNDK | SLV, LMT, XLE, REMX, USO | 10 | pending | pending |
| 2026-09-29 | 2026-09-30 | model_3_overfit | 3 | SNDK, NVDA, PLTR, ARM, TSLA | XLE, REMX, LMT, USO, FLY | 20 | pending | pending |
| 2026-09-28 | 2026-09-29 | model_1_baseline | 3 | PLTR, SPCX, FLY, MSFT, SNDK | XLP, UUP, TLT, JETS, REMX | 5 | matured | +4.095% |
| 2026-09-28 | 2026-09-29 | model_2_horizon_trend | 3 | DRAM, FLY, ARM, NVDA, PLTR | LMT, ASML, XLE, REMX, USO | 10 | pending | pending |
| 2026-09-28 | 2026-09-29 | model_3_overfit | 3 | SNDK, NVDA, PLTR, ARM, TSLA | XLE, REMX, LMT, FLY, USO | 20 | pending | pending |
| 2026-09-25 | 2026-09-28 | model_1_baseline | 3 | PLTR, SPCX, SNDK, USO, TSM | ITA, FLY, UFO, JETS, REMX | 5 | matured | +6.009% |
| 2026-09-25 | 2026-09-28 | model_2_horizon_trend | 3 | DRAM, ARM, SNDK, NVDA, PLTR | ASML, USO, URNM, REMX, FLY | 10 | pending | pending |
| 2026-09-25 | 2026-09-28 | model_3_overfit | 3 | DRAM, SNDK, NVDA, PLTR, TSLA | LMT, UFO, REMX, USO, FLY | 20 | pending | pending |
| 2026-09-24 | 2026-09-25 | model_1_baseline | 3 | PLTR, SPCX, MSFT, SNDK, ORCL | TLT, ARM, UFO, JETS, REMX | 5 | matured | +3.831% |
| 2026-09-24 | 2026-09-25 | model_2_horizon_trend | 3 | FLY, ARM, NVDA, TSLA, PLTR | LMT, AMLP, XLE, USO, REMX | 10 | pending | pending |
| 2026-09-24 | 2026-09-25 | model_3_overfit | 3 | SNDK, NVDA, PLTR, TSLA, ARM | URNM, XLE, LMT, REMX, USO | 20 | pending | pending |
| 2026-09-23 | 2026-09-24 | model_1_baseline | 3 | PLTR, SPCX, SNDK, TSM, USO | FLY, ARM, UFO, REMX, JETS | 5 | matured | +3.428% |
| 2026-09-23 | 2026-09-24 | model_2_horizon_trend | 3 | FLY, NVDA, ARM, PLTR, TSLA | AMLP, ASML, XLE, REMX, USO | 10 | pending | pending |
| 2026-09-23 | 2026-09-24 | model_3_overfit | 3 | SNDK, NVDA, PLTR, ORCL, TSLA | LMT, URNM, XLE, REMX, USO | 20 | pending | pending |
| 2026-09-22 | 2026-09-23 | model_1_baseline | 3 | SPCX, PLTR, USO, SNDK, SLV | REMX, INTC, UFO, JETS, FLY | 5 | matured | -1.596% |
| 2026-09-22 | 2026-09-23 | model_2_horizon_trend | 3 | DRAM, NVDA, TSLA, ARM, PLTR | LMT, XLE, FLY, USO, REMX | 10 | pending | pending |
| 2026-09-22 | 2026-09-23 | model_3_overfit | 3 | SNDK, NVDA, PLTR, TSLA, ARM | XLE, LMT, USO, REMX, FLY | 20 | pending | pending |
| 2026-09-21 | 2026-09-22 | model_1_baseline | 3 | PLTR, SPCX, SNDK, USO, NVDA | UFO, REMX, ARM, JETS, FLY | 5 | matured | +3.514% |
| 2026-09-21 | 2026-09-22 | model_2_horizon_trend | 3 | FLY, NVDA, TSLA, ARM, PLTR | AMLP, XLE, REMX, ASML, USO | 10 | matured | -0.410% |
| 2026-09-21 | 2026-09-22 | model_3_overfit | 3 | SNDK, NVDA, PLTR, TSLA, ORCL | LMT, URNM, ASML, REMX, USO | 20 | pending | pending |
| 2026-09-18 | 2026-09-21 | model_1_baseline | 3 | PLTR, USO, WCLD, SKYY, MSFT | UFO, ARM, JETS, INTC, FLY | 5 | matured | +3.163% |
| 2026-09-18 | 2026-09-21 | model_2_horizon_trend | 3 | DRAM, SNDK, NVDA, ARM, PLTR | XLE, LMT, REMX, ASML, USO | 10 | matured | +1.052% |
| 2026-09-18 | 2026-09-21 | model_3_overfit | 3 | SNDK, NVDA, PLTR, TSLA, MU | ASML, REMX, LMT, USO, FLY | 20 | pending | pending |
| 2026-09-17 | 2026-09-18 | model_1_baseline | 3 | PLTR, MU, URA, ORCL, FLY | USO, XLP, REMX, UUP, TSLA | 5 | matured | +4.743% |
| 2026-09-17 | 2026-09-18 | model_2_horizon_trend | 3 | NVDA, PLTR, ARM, MU, SNDK | USO, LMT, SLV, REMX, ASML | 10 | matured | +7.589% |
| 2026-09-17 | 2026-09-18 | model_3_overfit | 3 | SNDK, PLTR, NVDA, MU, TSLA | REMX, ASML, LMT, USO, FLY | 20 | pending | pending |
| 2026-09-16 | 2026-09-17 | model_1_baseline | 3 | MU, PLTR, ORCL, DRAM, MSFT | REMX, XLP, SPCX, UUP, TSLA | 5 | matured | +4.368% |
| 2026-09-16 | 2026-09-17 | model_2_horizon_trend | 3 | DRAM, PLTR, NVDA, MU, ARM | XLP, LMT, ASML, REMX, USO | 10 | matured | +10.221% |
| 2026-09-16 | 2026-09-17 | model_3_overfit | 3 | DRAM, SNDK, PLTR, MU, NVDA | XLV, REMX, LMT, USO, FLY | 20 | pending | pending |
| 2026-09-15 | 2026-09-16 | model_1_baseline | 3 | MU, PLTR, ORCL, DRAM, URA | XLP, SPCX, UUP, FLY, TSLA | 5 | matured | +5.393% |
| 2026-09-15 | 2026-09-16 | model_2_horizon_trend | 3 | DRAM, PLTR, NVDA, ARM, MU | SNDK, ASML, REMX, SLV, FLY | 10 | matured | +4.791% |
| 2026-09-15 | 2026-09-16 | model_3_overfit | 3 | DRAM, SNDK, PLTR, MU, NVDA | UFO, LMT, REMX, USO, FLY | 20 | pending | pending |
| 2026-09-14 | 2026-09-15 | model_1_baseline | 3 | PLTR, USO, URA, ORCL, MU | JETS, SPCX, LMT, INTC, FLY | 5 | matured | -4.991% |
| 2026-09-14 | 2026-09-15 | model_2_horizon_trend | 3 | DRAM, PLTR, NVDA, MU, ARM | ASML, INTC, REMX, SLV, FLY | 10 | matured | +5.035% |
| 2026-09-14 | 2026-09-15 | model_3_overfit | 3 | DRAM, SNDK, PLTR, MU, NVDA | LMT, UFO, USO, REMX, FLY | 20 | pending | pending |
| 2026-09-11 | 2026-09-14 | model_1_baseline | 3 | MU, ARM, URA, DRAM, PLTR | SPCX, XLP, FLY, UUP, TSLA | 5 | matured | +10.719% |
| 2026-09-11 | 2026-09-14 | model_2_horizon_trend | 3 | NVDA, PLTR, ARM, MU, SNDK | XLP, LMT, USO, REMX, ASML | 10 | matured | +11.576% |
| 2026-09-11 | 2026-09-14 | model_3_overfit | 3 | SNDK, PLTR, NVDA, MU, TSLA | REMX, ASML, LMT, USO, FLY | 20 | pending | pending |
| 2026-09-10 | 2026-09-11 | model_1_baseline | 3 | MU, ORCL, PLTR, USO, URA | LMT, TSLA, INTC, SPCX, FLY | 5 | matured | -0.671% |
| 2026-09-10 | 2026-09-11 | model_2_horizon_trend | 3 | DRAM, PLTR, ARM, MU, NVDA | URNM, REMX, SLV, INTC, USO | 10 | matured | +8.780% |
| 2026-09-10 | 2026-09-11 | model_3_overfit | 3 | DRAM, SNDK, MU, PLTR, ARM | LMT, REMX, UFO, USO, FLY | 20 | pending | pending |
| 2026-09-09 | 2026-09-10 | model_1_baseline | 3 | USO, PLTR, ORCL, XLE, MU | LMT, TSLA, SPCX, INTC, FLY | 5 | matured | -3.320% |
| 2026-09-09 | 2026-09-10 | model_2_horizon_trend | 3 | DRAM, ARM, MU, SNDK, PLTR | INTC, URA, URNM, REMX, USO | 10 | matured | +10.932% |
| 2026-09-09 | 2026-09-10 | model_3_overfit | 3 | SNDK, DRAM, MU, ARM, PLTR | LMT, UFO, REMX, USO, FLY | 20 | pending | pending |
| 2026-09-08 | 2026-09-09 | model_1_baseline | 3 | USO, XLE, PLTR, WCLD, XLV | DRAM, SPCX, ARM, INTC, FLY | 5 | matured | +7.888% |
| 2026-09-08 | 2026-09-09 | model_2_horizon_trend | 3 | SNDK, DRAM, ARM, MU, PLTR | LMT, URA, INTC, URNM, TSLA | 10 | matured | +9.233% |
| 2026-09-08 | 2026-09-09 | model_3_overfit | 3 | SNDK, DRAM, MU, PLTR, ARM | REMX, URA, URNM, USO, FLY | 20 | pending | pending |
| 2026-09-04 | 2026-09-08 | model_1_baseline | 3 | USO, XLE, WCLD, PLTR, XLV | XSD, SPCX, ARM, INTC, FLY | 5 | matured | +10.851% |
| 2026-09-04 | 2026-09-08 | model_2_horizon_trend | 3 | SNDK, ARM, MU, DRAM, PLTR | ORCL, URA, URNM, FLY, SPCX | 10 | matured | +15.247% |
| 2026-09-04 | 2026-09-08 | model_3_overfit | 3 | SNDK, MU, ARM, DRAM, PLTR | REMX, URNM, URA, FLY, SPCX | 20 | matured | +10.460% |
| 2026-09-03 | 2026-09-04 | model_1_baseline | 3 | USO, PLTR, XLE, WCLD, SKYY | XSD, TSLA, SPCX, INTC, FLY | 5 | matured | +3.078% |
| 2026-09-03 | 2026-09-04 | model_2_horizon_trend | 3 | DRAM, SNDK, ARM, MU, CIBR | SLV, REMX, INTC, URNM, URA | 10 | matured | +7.636% |
| 2026-09-03 | 2026-09-04 | model_3_overfit | 3 | SNDK, DRAM, MU, ARM, PLTR | URA, URNM, USO, REMX, FLY | 20 | matured | +14.046% |
| 2026-09-02 | 2026-09-03 | model_1_baseline | 3 | PLTR, MU, URA, ARM, ORCL | LMT, TSLA, INTC, SPCX, FLY | 5 | matured | -2.659% |
| 2026-09-02 | 2026-09-03 | model_2_horizon_trend | 3 | DRAM, SNDK, ARM, MU, PLTR | LMT, URNM, FLY, SLV, USO | 10 | matured | +8.105% |
| 2026-09-02 | 2026-09-03 | model_3_overfit | 3 | SNDK, DRAM, MU, ARM, PLTR | SLV, LMT, USO, SPCX, FLY | 20 | matured | +10.491% |
| 2026-09-01 | 2026-09-02 | model_1_baseline | 3 | PLTR, USO, XLE, WCLD, XLV | TSLA, ARM, SPCX, INTC, FLY | 5 | matured | -4.820% |
| 2026-09-01 | 2026-09-02 | model_2_horizon_trend | 3 | SNDK, DRAM, ARM, MU, HACK | INTC, URA, URNM, FLY, SPCX | 10 | matured | +1.499% |
| 2026-09-01 | 2026-09-02 | model_3_overfit | 3 | SNDK, DRAM, MU, PLTR, ARM | REMX, URA, URNM, FLY, SPCX | 20 | matured | +19.992% |
| 2026-08-31 | 2026-09-01 | model_1_baseline | 3 | USO, PLTR, XLE, WCLD, XLV | TSLA, ARM, SPCX, INTC, FLY | 5 | matured | -10.336% |
| 2026-08-31 | 2026-09-01 | model_2_horizon_trend | 3 | SNDK, ARM, MU, PLTR, HACK | URA, URNM, ORCL, FLY, SPCX | 10 | matured | +2.628% |
| 2026-08-31 | 2026-09-01 | model_3_overfit | 3 | SNDK, MU, PLTR, DRAM, ARM | ORCL, URA, URNM, FLY, SPCX | 20 | matured | +13.372% |
| 2026-08-28 | 2026-08-31 | model_1_baseline | 3 | SNDK, USO, XLE, XLV, SKYY | TSLA, INTC, ARM, SPCX, FLY | 5 | matured | -4.678% |
| 2026-08-28 | 2026-08-31 | model_2_horizon_trend | 3 | SNDK, MU, DRAM, SLV, ASML | JETS, WCLD, TSLA, ORCL, FLY | 10 | matured | -0.296% |
| 2026-08-28 | 2026-08-31 | model_3_overfit | 3 | SNDK, MU, DRAM, ASML, PLTR | URNM, REMX, WCLD, ORCL, FLY | 20 | matured | +14.840% |
| 2026-08-27 | 2026-08-28 | model_1_baseline | 3 | USO, PLTR, XLE, XLV, WCLD | TSLA, ARM, INTC, SPCX, FLY | 5 | matured | -4.022% |
| 2026-08-27 | 2026-08-28 | model_2_horizon_trend | 3 | SNDK, DRAM, MU, ASML, SLV | USO, WCLD, SPCX, TSLA, FLY | 10 | matured | -7.299% |
| 2026-08-27 | 2026-08-28 | model_3_overfit | 3 | SNDK, MU, DRAM, PLTR, ASML | MSFT, WCLD, ORCL, TSLA, FLY | 20 | matured | +8.447% |
| 2026-08-25 | 2026-08-26 | model_1_baseline | 3 | PLTR, MU, USO, ORCL, XLE | LMT, TSLA, INTC, FLY, SPCX | 5 | matured | +2.956% |
| 2026-08-25 | 2026-08-26 | model_2_horizon_trend | 3 | SNDK, DRAM, MU, SLV, INTC | JETS, USO, WCLD, TSLA, FLY | 10 | matured | +2.619% |
| 2026-08-25 | 2026-08-26 | model_3_overfit | 3 | SNDK, MU, INTC, DRAM, PLTR | UUP, MSFT, WCLD, TSLA, FLY | 20 | matured | +13.706% |
| 2026-08-24 | 2026-08-25 | model_1_baseline | 3 | USO, PLTR, XLE, XLV, MU | TSLA, ARM, INTC, SPCX, FLY | 5 | matured | +4.412% |
| 2026-08-24 | 2026-08-25 | model_2_horizon_trend | 3 | SNDK, DRAM, MU, INTC, SLV | WCLD, JETS, MSFT, TSLA, FLY | 10 | matured | +12.618% |
| 2026-08-24 | 2026-08-25 | model_3_overfit | 3 | SNDK, DRAM, MU, PLTR, ASML | ORCL, MSFT, WCLD, TSLA, FLY | 20 | matured | +8.686% |
| 2026-08-21 | 2026-08-24 | model_1_baseline | 0 | MU, PLTR, ORCL, USO, DRAM | SLV, TSLA, INTC, FLY, SPCX | 5 | matured | +3.879% |
| 2026-08-21 | 2026-08-24 | model_2_horizon_trend | 0 | SNDK, MU, DRAM, SLV, TSM | UUP, WCLD, TSLA, SPCX, FLY | 10 | matured | +4.982% |
| 2026-08-21 | 2026-08-24 | model_3_overfit | 0 | SNDK, MU, PLTR, ASML, INTC | MSFT, TLT, WCLD, TSLA, FLY | 20 | matured | +15.254% |
| 2026-08-20 | 2026-08-21 | model_1_baseline | 0 | SNDK, USO, ORCL, PLTR, XLE | ARM, TSLA, INTC, SPCX, FLY | 5 | matured | +2.139% |
| 2026-08-20 | 2026-08-21 | model_2_horizon_trend | 0 | SNDK, MU, PLTR, SLV, TSM | TSLA, MSFT, JETS, WCLD, FLY | 10 | matured | +4.119% |
| 2026-08-20 | 2026-08-21 | model_3_overfit | 0 | SNDK, MU, INTC, PLTR, SLV | TLT, UUP, MSFT, WCLD, FLY | 20 | matured | +8.953% |
| 2026-08-19 | 2026-08-20 | model_1_baseline | 1 | USO, PLTR, XLE, WCLD, SKYY | ARM, INTC, TSLA, SPCX, FLY | 5 | matured | +1.955% |
| 2026-08-19 | 2026-08-20 | model_2_horizon_trend | 1 | SNDK, DRAM, MU, ASML, IAU | NVDA, ORCL, TSLA, FLY, SPCX | 10 | matured | -7.383% |
| 2026-08-19 | 2026-08-20 | model_3_overfit | 1 | SNDK, DRAM, MU, PLTR, ASML | URNM, ORCL, USO, TSLA, FLY | 20 | matured | +2.205% |
| 2026-08-18 | 2026-08-19 | model_1_baseline | 1 | MU, PLTR, ORCL, USO, DRAM | SLV, TSLA, INTC, FLY, SPCX | 5 | matured | +4.045% |
| 2026-08-18 | 2026-08-19 | model_2_horizon_trend | 1 | SNDK, MU, DRAM, TSM, LMT | ORCL, WCLD, TSLA, FLY, SPCX | 10 | matured | +1.376% |
| 2026-08-18 | 2026-08-19 | model_3_overfit | 1 | SNDK, MU, DRAM, PLTR, ASML | URNM, MSFT, WCLD, TSLA, FLY | 20 | matured | +3.487% |
