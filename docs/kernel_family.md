# Kernel family — result

*Run 2026-09-08 17:28 +0800. 200 permutations. Expectation written first: three nulls.*

| kernel | ALL Sharpe | ALL p | LONG-HIST Sharpe | LONG-HIST p | split |
|---|---|---|---|---|---|
| model_1 (incumbent) | +0.54 | 0.0299 | +0.26 | 0.1642 | 3.88× |
| K0 regime-only | +0.04 | 0.4179 | -0.02 | 0.5025 | 1.35× |
| K1 similarity-only sigma=0.75 | +0.44 | 0.0647 | +0.25 | 0.1642 | 33.32× |
| K2 mahalanobis | +0.52 | 0.0498 | +0.35 | 0.1095 | 2.94× |

**Family test:** best of K0/K1/K2 = K2 mahalanobis at +0.52; best-of-3 null mean +0.23, 95th pct +0.61; **family p = 0.1144**. F1 False · F2 False · F3 True → **null**.

**K0 vs incumbent, paired:** Sharpe diff +0.49, paired p 0.1244 → the kernel does something.

