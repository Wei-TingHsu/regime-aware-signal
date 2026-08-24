# Rung-level selection diagnostic — results

*Run 2026-08-24 20:44:22 +0800. Registered in `docs/prereg_rung_diagnostic.md`, written before any quantity below was computed.*

Registered threshold: median top-k overlap vs the no-decay control **≥ 0.90** at HL=4y = tie-breaking; below = reselection.

**No forward return enters any quantity here.** These are properties of the weighting and selection alone.

## Engine A

| rung | wtd mean analog age (y) | median ESS (of 100) | top-k overlap vs ∞ |
|---|---|---|---|
| inf (no decay) | 0.444 [0.25, 1.15] | 100.0 [99.4, 100.0] | 1.000 (control) |
| 16y | 0.304 [0.23, 0.73] | 100.0 [99.1, 100.0] | 0.900 [0.700, 0.990] |
| 8y | 0.269 [0.23, 0.56] | 99.9 [98.9, 100.0] | 0.830 [0.560, 0.980] |
| 4y **← PRIMARY** | 0.246 [0.22, 0.39] | 99.8 [98.4, 99.9] | 0.765 [0.450, 0.960] |
| 2y | 0.228 [0.22, 0.31] | 99.6 [97.1, 99.8] | 0.710 [0.370, 0.940] |

**VERDICT: RESELECTION**

median top-k overlap at HL=4y is 0.765, BELOW the registered 0.90. Lambda is choosing WHICH analogs enter the average, not merely how they are weighted. The ladder does not measure 'does gentle recency decay improve analog quality'; it measures 'does restricting to recent history improve returns'. The report must say the latter.

*Bracketed figures are the 10th and 90th percentiles across rebalances.*

## Engine B

| rung | wtd mean analog age (y) | median ESS (of 100) | top-k overlap vs ∞ |
|---|---|---|---|
| inf (no decay) | 0.371 [0.24, 1.20] | 99.9 [97.4, 100.0] | 1.000 (control) |
| 16y | 0.298 [0.23, 0.91] | 99.9 [96.7, 100.0] | 0.950 [0.820, 0.990] |
| 8y | 0.268 [0.22, 0.76] | 99.8 [96.1, 100.0] | 0.910 [0.720, 0.985] |
| 4y **← PRIMARY** | 0.246 [0.22, 0.56] | 99.7 [94.6, 99.9] | 0.850 [0.600, 0.970] |
| 2y | 0.228 [0.21, 0.38] | 99.4 [90.9, 99.8] | 0.800 [0.500, 0.950] |

**VERDICT: RESELECTION**

median top-k overlap at HL=4y is 0.850, BELOW the registered 0.90. Lambda is choosing WHICH analogs enter the average, not merely how they are weighted. The ladder does not measure 'does gentle recency decay improve analog quality'; it measures 'does restricting to recent history improve returns'. The report must say the latter.

*Bracketed figures are the 10th and 90th percentiles across rebalances.*

## Reading

If overlap is low on both engines, the A/B Sharpe disagreement is not a disagreement about recency — both ladders are measuring a recency filter, and Engine A's POSITIVE verdict is a recency-filter result, not an analog result.

If overlap changes sharply between HL=2y and HL=4y on Engine B, the incumbent's interior Sharpe dip (0.25 at HL 3.438y, below both neighbours at 0.30 and 0.32) is attributable to discrete top-k membership changes. If overlap is flat across that interval, the dip is unexplained and is reported as unexplained.

