# Scaling check — the declared `_z()` full-panel look-ahead, measured

*Run 2026-08-25 02:13:00 +0800. PROJECT_STATE open thread 12.*

`analog_core._z()` standardises PC features using **whole-panel** moments, so a distance computed at 2010 uses units set by data through 2026. Declared but never quantified — *"expected to be small is not measured."* Both bases below are identical in every respect except the standardisation window. min_periods = 252, registered.

| model | universe | full-panel Sharpe | expanding Sharpe | diff | paired mean spread diff | sign-flip p |
|---|---|---|---|---|---|---|
| model_1_baseline | ALL | +0.4034 | +0.3834 | +0.0200 | +0.0122% | 0.8950 |
| model_1_baseline | LONG-HISTORY | +0.2526 | +0.2406 | +0.0120 | +0.0063% | 0.9404 |
| model_2_horizon_trend | ALL | +0.3598 | +0.2538 | +0.1060 | +0.1033% | 0.4621 |
| model_2_horizon_trend | LONG-HISTORY | +0.4131 | +0.1522 | +0.2610 | +0.2453% | 0.0572 |
| model_3_overfit | ALL | +0.4434 | +0.4035 | +0.0399 | +0.0341% | 0.9260 |
| model_3_overfit | LONG-HISTORY | +0.4947 | +0.3568 | +0.1379 | +0.1969% | 0.4999 |

## Candidate pool

Expanding scaling makes the first 252 rows NaN, so they leave the candidate pool through the existing NaN guard. A Sharpe difference driven by a smaller pool is a different finding from one driven by the scaling itself, so the counts are reported.

| model | full median pool | expanding median pool | shrinkage |
|---|---|---|---|
| model_1_baseline | 852 | 852 | 0.0% |
| model_2_horizon_trend | 844 | 844 | 0.0% |
| model_3_overfit | 831 | 831 | 0.0% |

## Reading

A small, non-significant difference means the declared look-ahead is small **on this panel** — what thread 12 expected but had never measured. It does **not** retract the declaration: the phrase "no look-ahead" stays wrong, and is now wrong by a measured amount.

A large or significant difference means every recorded figure on the `analog_core` basis carries it, and both numbers must appear side by side wherever those figures appear.

