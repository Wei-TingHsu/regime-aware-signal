# Step 3 — robustness re-test of the passing cells

*Run 2026-08-26 19:33:03 +0800.*

*The estimator is unchanged and frozen at `9062391`. What is re-tested is the NULL: `unblind_step3.py` permuted outcomes freely on a pool whose outcomes overlap 61–87% at h=20, which makes the null too narrow and every p-value too small. Wrong prior #25.*

**Confirmed: 1 of 7.**

| cell | n | n non-ov | N2 p(mse) | N2 p(hit) | N1 p(mse) | N1 p(hit) | EARLY | LATE | ratio | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| fomc_minutes/USO/h5 | 69 | 69 | 0.0024 | 0.0138 | 0.0022 | 0.0122 | +1.78e-04 | +4.07e-04 | 2.28× | **CONFIRMED** |
| political_order/GLD/h20 | 76 | 41 | 0.0039 | 0.0129 | 0.0018 | 0.0149 | -1.19e-05 | +1.77e-04 | 14.86× | ok |
| political_order/SPY/h20 | 232 | 97 | 0.0166 | 0.2244 | 0.3400 | 0.9042 | +2.88e-04 | +2.04e-03 | 7.08× | ok |
| political_order/SPY/h3 | 233 | 166 | 0.0001 | 0.0337 | 0.1333 | 0.8793 | +2.18e-05 | +1.01e-04 | 4.62× | ok |
| political_order/SPY/h5 | 233 | 149 | 0.0002 | 0.0611 | 0.0358 | 0.9885 | +2.26e-05 | +3.27e-05 | 1.44× | ok |
| earnings_8k/SPY/h20 | 459 | 171 | 0.0232 | 0.1177 | 0.9681 | 0.7280 | +7.44e-05 | +3.05e-04 | 4.10× | ok |
| earnings_8k/SPY/h5 | 462 | 317 | 0.1022 | 0.0769 | 0.4118 | 0.8313 | -3.17e-06 | +4.00e-05 | 12.64× | ok |
