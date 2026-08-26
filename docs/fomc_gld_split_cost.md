# FOMC → GLD — temporal split and cost test

*Run 2026-08-26 15:03:59 +0800.*

*Pre-registered in this script's docstring, committed before the run. The original result stays at its own tier — docstring `8640d2d` — and this document does not upgrade it.*

131 events, 2011-01-26 → 2026-07-29. Split at the chronological median, 2019-03-20.

| h | arm | n | stat | p(flip) | p(perm) |
|---|---|---|---|---|---|
| 1 | pooled | 131 | +0.326% | 0.0088 | 0.0059 |
| 1 | EARLY | 65 | +0.411% | 0.0249 | 0.0151 |
| 1 | LATE | 66 | +0.242% | 0.1498 | 0.1982 |
| 2 | pooled | 131 | +0.175% | 0.3232 | 0.2469 |
| 2 | EARLY | 65 | +0.589% | 0.0051 | 0.0029 |
| 2 | LATE | 66 | -0.232% | 0.4096 | 0.4432 |
| 3 | pooled | 131 | +0.274% | 0.2047 | 0.1372 |
| 3 | EARLY | 65 | +0.758% | 0.0013 | 0.0003 |
| 3 | LATE | 66 | -0.203% | 0.5773 | 0.6736 |
| 5 | pooled | 131 | +0.387% | 0.1044 | 0.0778 |
| 5 | EARLY | 65 | +0.771% | 0.0101 | 0.0053 |
| 5 | LATE | 66 | +0.009% | 0.9810 | 0.9987 |

- **S1** sign agreement: **FAIL**
- **S2** magnitude ratio ≤ 3.0×: **FAIL**
- **S3** pooled p < 0.05 under both nulls: **FAIL**
- **C1** net > 0 at 10 bps: **PASS**

| h | gross (bps) | net @2bp | net @5bp | net @10bp | net @20bp | break-even |
|---|---|---|---|---|---|---|
| 2 | 17.5 | +15.5 | +12.5 | +7.5 | -2.5 | 17.5 |
| 3 | 27.4 | +25.4 | +22.4 | +17.4 | +7.4 | 27.4 |

## Verdict

NOT A FINDING. Split failed: reported as a subsample artifact, same treatment as SPY->GLD and SOXX->XAR. It does not become the Tier-1 exemplar and the demo abstains.

**Multiplicity, recorded before this run.** `macro_event_test.py` evaluates 4 assets × 4 horizons × 2 questions = 32 cells; ~1.6 false positives are expected at α = 0.05 and exactly one cell survived. NEXT_2, NEXT_3 and NEXT_5 overlap by construction and are not three independent confirmations. On the original evidence alone this cell is indistinguishable from chance — which is why the result was withheld pending this split.

**Power, computed before this run.** ~85 events per half; GLD daily σ ≈ 1.0% gives se ≈ 0.19% at h=3 against a 0.30% effect, t ≈ 1.6. A real effect of this size would fail a both-halves-significant criterion more often than it passed, so the registered criterion is sign agreement and magnitude stability. Per-half p-values are reported and are not part of the criterion.

