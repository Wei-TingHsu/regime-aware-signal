# FOMC → GLD — temporal split and cost test

*Run 2026-08-26 18:23:23 +0800.*

*Pre-registered in this script's docstring, committed before the run. The original result stays at its own tier — docstring `8640d2d` — and this document does not upgrade it.*

131 events, 2011-01-26 → 2026-07-29. Split at the chronological median, 2019-03-20.

| h | arm | n | mean NEXT_h | p(rotation) |
|---|---|---|---|---|
| 1 | pooled | 131 | -0.132% | 0.0925 |
| 1 | EARLY | 65 | -0.427% | 0.0039 |
| 1 | LATE | 66 | +0.159% | 0.4175 |
| 2 | pooled | 131 | -0.232% | 0.0288 |
| 2 | EARLY | 65 | -0.383% | 0.0234 |
| 2 | LATE | 66 | -0.083% | 0.3880 |
| 3 | pooled | 131 | -0.317% | 0.0142 |
| 3 | EARLY | 65 | -0.380% | 0.0511 |
| 3 | LATE | 66 | -0.254% | 0.1187 |
| 5 | pooled | 131 | -0.320% | 0.0132 |
| 5 | EARLY | 65 | -0.690% | 0.0088 |
| 5 | LATE | 66 | +0.045% | 0.5560 |

- **S1** sign agreement: **PASS**
- **S2** magnitude ratio ≤ 3.0×: **FAIL**
- **S3** pooled p < 0.05 under the rotation null: **PASS**
- **C1** net > 0 at 10 bps: **PASS**

| h | gross (bps) | net @2bp | net @5bp | net @10bp | net @20bp | break-even |
|---|---|---|---|---|---|---|
| 2 | 23.2 | +21.2 | +18.2 | +13.2 | +3.2 | 23.2 |
| 3 | 31.7 | +29.7 | +26.7 | +21.7 | +11.7 | 31.7 |

## Verdict

NOT A FINDING. Split failed: reported as a subsample artifact, same treatment as SPY->GLD and SOXX->XAR. It does not become the Tier-1 exemplar and the demo abstains.

**Multiplicity, recorded before this run.** `macro_event_test.py` evaluates 4 assets × 4 horizons × 2 questions = 32 cells; ~1.6 false positives are expected at α = 0.05 and exactly one cell survived. NEXT_2, NEXT_3 and NEXT_5 overlap by construction and are not three independent confirmations. On the original evidence alone this cell is indistinguishable from chance — which is why the result was withheld pending this split.

**Power, computed before this run.** ~85 events per half; GLD daily σ ≈ 1.0% gives se ≈ 0.19% at h=3 against a 0.30% effect, t ≈ 1.6. A real effect of this size would fail a both-halves-significant criterion more often than it passed, so the registered criterion is sign agreement and magnitude stability. Per-half p-values are reported and are not part of the criterion.

