# Fine lambda sweep — the interior dip

*Run 2026-08-24 21:23:03 +0800.*

> **EXPLORATORY, POST-HOC, NO REGISTERED CRITERION.** Run after seeing the ladder, chosen to bracket one anomalous point. It cannot produce a finding and nothing in it may be promoted to a model, a rung, or a claim. The registered ladder's verdict (`docs/recency_sweep_results.md`) stands regardless of what is here.

## The anomaly

Engine B, long-history, 836 rebalances: HL 4y → 0.3200, incumbent λ=0.0008 (HL 3.438y) → 0.2500, HL 2y → 0.3000. The incumbent sits **below both neighbours**. `docs/prereg_rung_diagnostic.md` §3.3 registered the discriminating check: Engine B top-k overlap runs 0.950 / 0.910 / 0.850 / 0.800 — smooth, no break between 4y and 2y — so the dip is **unexplained**, not attributable to selection discreteness.

| λ /session | HL (y) | ALL Sharpe | ALL p | long-history Sharpe | long-history p |
|---|---|---|---|---|---|
| 0.000400 | 6.876 | +0.4300 | 0.0010 | +0.2400 | 0.0519 |
| 0.000500 | 5.501 | +0.5000 | 0.0010 | +0.2800 | 0.0230 |
| 0.000600 | 4.584 | +0.5200 | 0.0010 | +0.2900 | 0.0140 |
| 0.000700 | 3.929 | +0.5300 | 0.0010 | +0.3000 | 0.0120 |
| 0.000800 **← incumbent** | 3.438 | +0.5200 | 0.0010 | +0.2500 | 0.0370 |
| 0.000900 | 3.056 | +0.4500 | 0.0020 | +0.2200 | 0.0470 |
| 0.001000 | 2.751 | +0.5000 | 0.0010 | +0.2900 | 0.0180 |
| 0.001100 | 2.501 | +0.4700 | 0.0020 | +0.2900 | 0.0120 |
| 0.001200 | 2.292 | +0.4800 | 0.0010 | +0.2700 | 0.0240 |
| 0.001300 | 2.116 | +0.4200 | 0.0010 | +0.2800 | 0.0260 |
| 0.001400 | 1.965 | +0.4200 | 0.0010 | +0.2600 | 0.0300 |

## Description

Long-history Sharpe ranges +0.2200 to +0.3000 across this λ interval (spread 0.0800). Largest step between adjacent λ values: 0.0700.

Interior local minima at λ = 0.000900, 0.001200.

**Reading.** A Sharpe surface that moves materially between adjacent λ values differing by 1e-4 is a surface on which any single-λ result is fragile. That fragility is a property of `topk=100` selecting after weighting, and it applies to every rung of the registered ladder as much as to the incumbent.

