# Trend check — level vs trend at fixed horizon

*Run 2026-08-25 02:17:36 +0800. PROJECT_STATE open thread 8.*

`model_1_baseline` (horizon 5, level) and `model_2_horizon_trend` (horizon 10, trend) differ in **two** things, so that comparison supports neither the original claim that trend helps nor its later retirement. Every cell below fixes horizon, kernel and sigma and varies **only** `sim_mode`.

Every cell is also run on both scaling bases, because `docs/scaling_check_results.md` found the declared `_z()` look-ahead is small for the level model and large for both trend models — so "does trend beat level" cannot be answered on the full-panel basis alone.

> **No multiplicity correction is applied and none is claimed.** These are 16 cells × 2 bases; at α = 0.05 roughly 1.6 clear by chance. Individual cells are estimates; the claim is the pattern.

| basis | sigma | horizon | universe | level | trend | trend−level | paired mean spread diff | sign-flip p |
|---|---|---|---|---|---|---|---|---|
| full | 1.0 | 5 | ALL | +0.4346 | +0.1092 | -0.3254 | -0.1815% | 0.1736 |
| full | 1.0 | 5 | LONG-HISTORY | +0.2493 | +0.0213 | -0.2280 | -0.1147% | 0.3607 |
| full | 1.0 | 10 | ALL | +0.1308 | +0.3441 | +0.2133 | +0.2270% | 0.3675 |
| full | 1.0 | 10 | LONG-HISTORY | +0.0708 | +0.4219 | +0.3511 | +0.3457% | 0.1694 |
| full | 1.0 | 15 | ALL | +0.3025 | +0.4896 | +0.1872 | +0.3352% | 0.3411 |
| full | 1.0 | 15 | LONG-HISTORY | +0.1587 | +0.4075 | +0.2487 | +0.3830% | 0.3127 |
| full | 1.0 | 20 | ALL | +0.3359 | +0.4434 | +0.1075 | +0.1871% | 0.7141 |
| full | 1.0 | 20 | LONG-HISTORY | +0.3460 | +0.4947 | +0.1487 | +0.2355% | 0.5571 |
| full | 1.5 | 5 | ALL | +0.4034 | +0.0625 | -0.3409 | -0.1889% | 0.1348 |
| full | 1.5 | 5 | LONG-HISTORY | +0.2526 | -0.0470 | -0.2997 | -0.1470% | 0.2100 |
| full | 1.5 | 10 | ALL | +0.1787 | +0.3598 | +0.1811 | +0.1956% | 0.4257 |
| full | 1.5 | 10 | LONG-HISTORY | +0.1413 | +0.4131 | +0.2719 | +0.2549% | 0.2839 |
| full | 1.5 | 15 | ALL | +0.3305 | +0.4934 | +0.1630 | +0.2910% | 0.4479 |
| full | 1.5 | 15 | LONG-HISTORY | +0.2196 | +0.4925 | +0.2729 | +0.4439% | 0.2432 |
| full | 1.5 | 20 | ALL | +0.3433 | +0.3446 | +0.0013 | -0.0806% | 0.8736 |
| full | 1.5 | 20 | LONG-HISTORY | +0.3101 | +0.4543 | +0.1442 | +0.2373% | 0.5461 |
| expanding | 1.0 | 5 | ALL | +0.4060 | -0.1666 | -0.5726 | -0.3141% | 0.0214 |
| expanding | 1.0 | 5 | LONG-HISTORY | +0.1775 | -0.3420 | -0.5195 | -0.2508% | 0.0520 |
| expanding | 1.0 | 10 | ALL | +0.1142 | +0.1224 | +0.0082 | +0.0013% | 0.9978 |
| expanding | 1.0 | 10 | LONG-HISTORY | -0.0091 | +0.0869 | +0.0960 | +0.0955% | 0.6893 |
| expanding | 1.0 | 15 | ALL | +0.5715 | +0.3159 | -0.2556 | -0.4208% | 0.2200 |
| expanding | 1.0 | 15 | LONG-HISTORY | +0.3519 | +0.2680 | -0.0839 | -0.1374% | 0.7041 |
| expanding | 1.0 | 20 | ALL | +0.4134 | +0.4035 | -0.0099 | -0.0750% | 0.8770 |
| expanding | 1.0 | 20 | LONG-HISTORY | +0.2940 | +0.3568 | +0.0628 | +0.1160% | 0.7938 |
| expanding | 1.5 | 5 | ALL | +0.3834 | -0.0467 | -0.4301 | -0.2351% | 0.0728 |
| expanding | 1.5 | 5 | LONG-HISTORY | +0.2406 | -0.2530 | -0.4936 | -0.2376% | 0.0458 |
| expanding | 1.5 | 10 | ALL | +0.1722 | +0.2538 | +0.0816 | +0.0792% | 0.7451 |
| expanding | 1.5 | 10 | LONG-HISTORY | +0.0442 | +0.1522 | +0.1080 | +0.1002% | 0.6597 |
| expanding | 1.5 | 15 | ALL | +0.5898 | +0.3234 | -0.2663 | -0.4342% | 0.2412 |
| expanding | 1.5 | 15 | LONG-HISTORY | +0.3941 | +0.2969 | -0.0973 | -0.1577% | 0.6577 |
| expanding | 1.5 | 20 | ALL | +0.4583 | +0.3393 | -0.1190 | -0.3380% | 0.4719 |
| expanding | 1.5 | 20 | LONG-HISTORY | +0.3169 | +0.2738 | -0.0431 | -0.1201% | 0.7794 |

## Pattern

| basis | universe | mean trend−level | trend ahead in |
|---|---|---|---|
| full | ALL | +0.0234 | 6/8 cells |
| full | LONG-HISTORY | +0.1137 | 6/8 cells |
| expanding | ALL | -0.1955 | 2/8 cells |
| expanding | LONG-HISTORY | -0.1213 | 3/8 cells |

Long-history: trend advantage **+0.1137** on the full basis, **-0.1213** with the look-ahead removed.

