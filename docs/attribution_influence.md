# T16 B4 — influence weights per source class × regime

*Run 2026-10-09 16:39. Registered in `docs/prereg_prints_and_attribution.md` B4. An event = one document with a non-zero reading on one asset; its move = the bin it landed in (overnight for prints/8-Ks/orders, intraday for FOMC). Hit share vs a within-class permutation null (10,000 draws); weight > 0 only at p < 0.05 with ≥ 30 events. **Displayed only; not used in the 3-day line.***

| asset | source | regime | events | hit share | null mean | p | slope (bp per unit reading) | weight |
|---|---|---|---|---|---|---|---|---|
| GLD | data_print:cpi | 0 | 101 | 41% | 51% | 0.990 | -20.3 | none |
| GLD | data_print:cpi | 1 | 47 | 62% | 52% | 0.143 | +7.2 | none |
| GLD | data_print:cpi | 2 | 47 | 57% | 49% | 0.191 | +28.9 | none |
| GLD | data_print:cpi | 3 | 27 | 59% | 46% | 0.145 | +83.8 | too few |
| GLD | data_print:cpi_core | 0 | 101 | 58% | 52% | 0.116 | +18.5 | none |
| GLD | data_print:cpi_core | 1 | 47 | 57% | 57% | 0.568 | +8.1 | none |
| GLD | data_print:cpi_core | 2 | 47 | 53% | 45% | 0.204 | -0.5 | none |
| GLD | data_print:cpi_core | 3 | 27 | 52% | 47% | 0.440 | +55.3 | too few |
| GLD | data_print:empsit | 0 | 100 | 65% | 49% | 0.001 | +65.6 | **earned** |
| GLD | data_print:empsit | 1 | 48 | 56% | 48% | 0.161 | +47.4 | none |
| GLD | data_print:empsit | 2 | 44 | 70% | 50% | 0.007 | +83.6 | **earned** |
| GLD | data_print:empsit | 3 | 28 | 75% | 52% | 0.015 | +111.9 | too few |
| GLD | data_print:pce | 0 | 103 | 48% | 50% | 0.720 | -12.2 | none |
| GLD | data_print:pce | 1 | 47 | 62% | 53% | 0.155 | +17.6 | none |
| GLD | data_print:pce | 2 | 42 | 43% | 46% | 0.819 | +3.4 | none |
| GLD | data_print:pce | 3 | 30 | 43% | 37% | 0.284 | +37.2 | none |
| GLD | data_print:unrate | 0 | 100 | 46% | 49% | 0.769 | -22.5 | none |
| GLD | data_print:unrate | 1 | 48 | 42% | 49% | 0.890 | -21.5 | none |
| GLD | data_print:unrate | 2 | 44 | 61% | 52% | 0.164 | +43.7 | none |
| GLD | data_print:unrate | 3 | 27 | 56% | 56% | 0.685 | -50.3 | too few |
| GLD | earnings_8k | 0 | 4 | 50% | 34% | 0.690 | +nan | too few |
| GLD | earnings_8k | 1 | 1 | 100% | 100% | 1.000 | +nan | too few |
| GLD | earnings_8k | 2 | 6 | 17% | 38% | 1.000 | -569.1 | too few |
| GLD | earnings_8k | 3 | 11 | 55% | 55% | 0.775 | +61.0 | too few |
| GLD | fomc_minutes | 0 | 38 | 47% | 51% | 0.762 | +27.9 | none |
| GLD | fomc_minutes | 1 | 21 | 62% | 50% | 0.265 | +19.5 | too few |
| GLD | fomc_minutes | 2 | 23 | 43% | 50% | 0.860 | +61.5 | too few |
| GLD | fomc_minutes | 3 | 18 | 56% | 60% | 0.845 | +26.4 | too few |
| GLD | fomc_statement | 0 | 38 | 42% | 50% | 0.904 | +130.6 | none |
| GLD | fomc_statement | 1 | 27 | 52% | 51% | 0.630 | +31.4 | too few |
| GLD | fomc_statement | 2 | 26 | 58% | 55% | 0.520 | +135.7 | too few |
| GLD | fomc_statement | 3 | 15 | 53% | 49% | 0.575 | +73.5 | too few |
| GLD | political_order | 0 | 14 | 43% | 38% | 0.695 | -7.9 | too few |
| GLD | political_order | 1 | 13 | 38% | 47% | 1.000 | +99.5 | too few |
| GLD | political_order | 2 | 9 | 67% | 67% | 1.000 | -1311.9 | too few |
| GLD | political_order | 3 | 40 | 32% | 50% | 0.998 | -69.6 | none |
| SPY | data_print:claims | 0 | 384 | 58% | 50% | 0.002 | +19.8 | **earned** |
| SPY | data_print:claims | 1 | 2414 | 49% | 50% | 0.893 | -2.1 | none |
| SPY | data_print:claims | 2 | 191 | 53% | 49% | 0.191 | +1.3 | none |
| SPY | data_print:claims | 3 | 128 | 55% | 50% | 0.096 | +3.3 | none |
| SPY | data_print:empsit | 0 | 100 | 62% | 49% | 0.004 | +48.5 | **earned** |
| SPY | data_print:empsit | 1 | 48 | 62% | 49% | 0.041 | +53.7 | **earned** |
| SPY | data_print:empsit | 2 | 44 | 50% | 50% | 0.621 | -12.6 | none |
| SPY | data_print:empsit | 3 | 28 | 36% | 48% | 0.970 | -5.2 | too few |
| SPY | data_print:gdp | 0 | 36 | 67% | 52% | 0.018 | +52.2 | **earned** |
| SPY | data_print:gdp | 1 | 14 | 64% | 50% | 0.250 | -13.8 | too few |
| SPY | data_print:gdp | 2 | 15 | 67% | 57% | 0.330 | +44.2 | too few |
| SPY | data_print:gdp | 3 | 10 | 50% | 50% | 1.000 | -11.9 | too few |
| SPY | data_print:retail | 0 | 100 | 61% | 51% | 0.031 | +50.8 | **earned** |
| SPY | data_print:retail | 1 | 50 | 54% | 50% | 0.340 | +21.3 | none |
| SPY | data_print:retail | 2 | 46 | 48% | 50% | 0.721 | -1.7 | none |
| SPY | data_print:retail | 3 | 28 | 61% | 51% | 0.250 | +18.0 | too few |
| SPY | data_print:unrate | 0 | 100 | 51% | 48% | 0.297 | +8.2 | none |
| SPY | data_print:unrate | 1 | 48 | 52% | 51% | 0.536 | +24.8 | none |
| SPY | data_print:unrate | 2 | 44 | 50% | 49% | 0.554 | -17.4 | none |
| SPY | data_print:unrate | 3 | 27 | 59% | 44% | 0.095 | +9.7 | too few |
| SPY | earnings_8k | 0 | 117 | 50% | 51% | 0.809 | -2.5 | none |
| SPY | earnings_8k | 1 | 77 | 52% | 54% | 0.925 | -14.6 | none |
| SPY | earnings_8k | 2 | 156 | 51% | 49% | 0.370 | -0.5 | none |
| SPY | earnings_8k | 3 | 112 | 51% | 53% | 0.839 | -7.0 | none |
| SPY | fomc_minutes | 0 | 38 | 53% | 54% | 0.706 | -13.5 | none |
| SPY | fomc_minutes | 1 | 25 | 56% | 61% | 0.930 | -79.6 | too few |
| SPY | fomc_minutes | 2 | 27 | 41% | 50% | 0.890 | -24.7 | too few |
| SPY | fomc_minutes | 3 | 19 | 68% | 50% | 0.140 | -347.7 | too few |
| SPY | fomc_statement | 0 | 49 | 45% | 50% | 0.854 | +49.8 | none |
| SPY | fomc_statement | 1 | 30 | 40% | 39% | 0.654 | -24.6 | none |
| SPY | fomc_statement | 2 | 29 | 52% | 53% | 0.715 | -60.8 | too few |
| SPY | fomc_statement | 3 | 17 | 59% | 46% | 0.275 | +229.0 | too few |
| SPY | political_order | 0 | 34 | 53% | 51% | 0.541 | -8.9 | none |
| SPY | political_order | 1 | 58 | 41% | 47% | 0.845 | +130.6 | none |
| SPY | political_order | 2 | 27 | 59% | 50% | 0.315 | +65.2 | too few |
| SPY | political_order | 3 | 114 | 54% | 55% | 0.732 | +9.1 | none |
| SPY | political_other | 0 | 5 | 40% | 40% | 1.000 | -27.1 | too few |
| TLT | data_print:claims | 0 | 384 | 59% | 50% | 0.000 | +14.7 | **earned** |
| TLT | data_print:claims | 1 | 2414 | 51% | 50% | 0.014 | +2.2 | **earned** |
| TLT | data_print:claims | 2 | 191 | 59% | 50% | 0.007 | +34.0 | **earned** |
| TLT | data_print:claims | 3 | 128 | 50% | 50% | 0.571 | +7.3 | none |
| TLT | data_print:cpi | 0 | 101 | 43% | 49% | 0.929 | -6.4 | none |
| TLT | data_print:cpi | 1 | 47 | 66% | 52% | 0.040 | +53.2 | **earned** |
| TLT | data_print:cpi | 2 | 47 | 55% | 49% | 0.242 | +38.0 | none |
| TLT | data_print:cpi | 3 | 27 | 56% | 44% | 0.145 | +44.7 | too few |
| TLT | data_print:cpi_core | 0 | 101 | 50% | 49% | 0.542 | +4.6 | none |
| TLT | data_print:cpi_core | 1 | 47 | 66% | 55% | 0.084 | +34.2 | none |
| TLT | data_print:cpi_core | 2 | 47 | 55% | 51% | 0.323 | -3.8 | none |
| TLT | data_print:cpi_core | 3 | 27 | 56% | 44% | 0.125 | +46.0 | too few |
| TLT | data_print:empsit | 0 | 100 | 65% | 50% | 0.001 | +70.2 | **earned** |
| TLT | data_print:empsit | 1 | 48 | 54% | 50% | 0.366 | +24.6 | none |
| TLT | data_print:empsit | 2 | 44 | 61% | 50% | 0.100 | +39.4 | none |
| TLT | data_print:empsit | 3 | 28 | 57% | 49% | 0.320 | +48.7 | too few |
| TLT | data_print:gdp | 0 | 36 | 56% | 52% | 0.444 | +7.1 | none |
| TLT | data_print:gdp | 1 | 14 | 57% | 49% | 0.480 | +36.2 | too few |
| TLT | data_print:gdp | 2 | 15 | 53% | 48% | 0.525 | -13.7 | too few |
| TLT | data_print:gdp | 3 | 10 | 50% | 50% | 1.000 | +3.5 | too few |
| TLT | data_print:pce | 0 | 103 | 53% | 49% | 0.243 | +3.2 | none |
| TLT | data_print:pce | 1 | 47 | 47% | 49% | 0.729 | -17.4 | none |
| TLT | data_print:pce | 2 | 42 | 52% | 51% | 0.568 | +8.9 | none |
| TLT | data_print:pce | 3 | 30 | 40% | 45% | 0.929 | -13.8 | none |
| TLT | data_print:ppi | 0 | 92 | 60% | 56% | 0.241 | +8.8 | none |
| TLT | data_print:ppi | 1 | 40 | 52% | 49% | 0.467 | +35.1 | none |
| TLT | data_print:ppi | 2 | 41 | 68% | 51% | 0.023 | +64.7 | **earned** |
| TLT | data_print:ppi | 3 | 28 | 57% | 46% | 0.120 | +19.4 | too few |
| TLT | data_print:retail | 0 | 100 | 58% | 50% | 0.070 | +20.3 | none |
| TLT | data_print:retail | 1 | 50 | 66% | 49% | 0.014 | +51.6 | **earned** |
| TLT | data_print:retail | 2 | 46 | 52% | 49% | 0.460 | +34.8 | none |
| TLT | data_print:retail | 3 | 28 | 68% | 50% | 0.055 | +57.7 | too few |
| TLT | data_print:unrate | 0 | 100 | 50% | 49% | 0.463 | -7.7 | none |
| TLT | data_print:unrate | 1 | 48 | 44% | 50% | 0.878 | +7.3 | none |
| TLT | data_print:unrate | 2 | 44 | 48% | 46% | 0.522 | +12.0 | none |
| TLT | data_print:unrate | 3 | 27 | 70% | 48% | 0.015 | +58.0 | too few |
| TLT | earnings_8k | 0 | 17 | 41% | 52% | 0.910 | -102.9 | too few |
| TLT | earnings_8k | 1 | 5 | 80% | 46% | 0.250 | +113.7 | too few |
| TLT | earnings_8k | 2 | 26 | 50% | 50% | 0.665 | -71.7 | too few |
| TLT | earnings_8k | 3 | 27 | 48% | 46% | 0.515 | +30.9 | too few |
| TLT | fomc_minutes | 0 | 47 | 43% | 50% | 0.934 | -45.4 | none |
| TLT | fomc_minutes | 1 | 28 | 57% | 50% | 0.335 | +60.6 | too few |
| TLT | fomc_minutes | 2 | 28 | 46% | 47% | 0.700 | +32.9 | too few |
| TLT | fomc_minutes | 3 | 19 | 53% | 46% | 0.470 | +6.2 | too few |
| TLT | fomc_statement | 0 | 50 | 50% | 51% | 0.677 | +16.2 | none |
| TLT | fomc_statement | 1 | 29 | 48% | 50% | 0.650 | +113.9 | too few |
| TLT | fomc_statement | 2 | 27 | 63% | 61% | 0.605 | +86.7 | too few |
| TLT | fomc_statement | 3 | 18 | 50% | 44% | 0.385 | +68.9 | too few |
| TLT | political_order | 0 | 8 | 38% | 38% | 1.000 | -659.1 | too few |
| TLT | political_order | 1 | 12 | 33% | 42% | 1.000 | -241.1 | too few |
| TLT | political_order | 2 | 9 | 33% | 33% | 1.000 | -659.7 | too few |
| TLT | political_order | 3 | 26 | 31% | 26% | 0.460 | +56.0 | too few |
| USO | earnings_8k | 0 | 5 | 80% | 80% | 1.000 | +463.9 | too few |
| USO | earnings_8k | 1 | 2 | 100% | 100% | 1.000 | +nan | too few |
| USO | earnings_8k | 2 | 4 | 75% | 75% | 1.000 | +nan | too few |
| USO | earnings_8k | 3 | 1 | 0% | 0% | 1.000 | +nan | too few |
| USO | fomc_minutes | 0 | 25 | 40% | 50% | 0.910 | -350.4 | too few |
| USO | fomc_minutes | 1 | 17 | 59% | 56% | 0.630 | +309.5 | too few |
| USO | fomc_minutes | 2 | 18 | 39% | 52% | 0.985 | -319.9 | too few |
| USO | fomc_minutes | 3 | 10 | 70% | 49% | 0.245 | -57.6 | too few |
| USO | fomc_statement | 0 | 24 | 54% | 53% | 0.655 | +172.2 | too few |
| USO | fomc_statement | 1 | 13 | 62% | 47% | 0.200 | +362.0 | too few |
| USO | fomc_statement | 2 | 18 | 44% | 51% | 0.850 | +295.0 | too few |
| USO | fomc_statement | 3 | 7 | 57% | 40% | 0.440 | +704.1 | too few |
| USO | political_order | 0 | 22 | 50% | 53% | 0.845 | -38.5 | too few |
| USO | political_order | 1 | 18 | 44% | 47% | 0.800 | +334.6 | too few |
| USO | political_order | 2 | 11 | 36% | 41% | 0.910 | +67.6 | too few |
| USO | political_order | 3 | 49 | 55% | 55% | 0.652 | -69.4 | none |
| UUP | data_print:claims | 0 | 384 | 45% | 48% | 0.925 | -4.4 | none |
| UUP | data_print:claims | 1 | 2414 | 49% | 50% | 0.794 | -0.2 | none |
| UUP | data_print:claims | 2 | 191 | 53% | 47% | 0.035 | +9.8 | **earned** |
| UUP | data_print:claims | 3 | 128 | 50% | 48% | 0.363 | +6.7 | none |
| UUP | data_print:cpi | 0 | 101 | 42% | 45% | 0.795 | -6.5 | none |
| UUP | data_print:cpi | 1 | 47 | 51% | 48% | 0.365 | +3.0 | none |
| UUP | data_print:cpi | 2 | 47 | 62% | 48% | 0.032 | +21.2 | **earned** |
| UUP | data_print:cpi | 3 | 27 | 48% | 38% | 0.135 | +38.6 | too few |
| UUP | data_print:cpi_core | 0 | 101 | 50% | 42% | 0.024 | +22.4 | **earned** |
| UUP | data_print:cpi_core | 1 | 47 | 60% | 51% | 0.124 | +15.9 | none |
| UUP | data_print:cpi_core | 2 | 47 | 51% | 46% | 0.296 | +3.8 | none |
| UUP | data_print:cpi_core | 3 | 27 | 48% | 39% | 0.185 | +38.6 | too few |
| UUP | data_print:empsit | 0 | 100 | 59% | 47% | 0.009 | +35.1 | **earned** |
| UUP | data_print:empsit | 1 | 48 | 54% | 48% | 0.234 | +8.5 | none |
| UUP | data_print:empsit | 2 | 44 | 75% | 49% | 0.000 | +50.1 | **earned** |
| UUP | data_print:empsit | 3 | 28 | 71% | 49% | 0.030 | +42.7 | too few |
| UUP | data_print:gdp | 0 | 36 | 56% | 56% | 0.719 | +18.1 | none |
| UUP | data_print:gdp | 1 | 14 | 79% | 50% | 0.060 | +30.5 | too few |
| UUP | data_print:gdp | 2 | 15 | 87% | 52% | 0.010 | +39.8 | too few |
| UUP | data_print:gdp | 3 | 10 | 50% | 50% | 1.000 | -0.2 | too few |
| UUP | data_print:pce | 0 | 103 | 44% | 47% | 0.819 | -7.7 | none |
| UUP | data_print:pce | 1 | 47 | 62% | 49% | 0.037 | +16.9 | **earned** |
| UUP | data_print:pce | 2 | 42 | 50% | 45% | 0.246 | +1.4 | none |
| UUP | data_print:pce | 3 | 30 | 50% | 47% | 0.545 | +11.1 | none |
| UUP | data_print:ppi | 0 | 92 | 41% | 44% | 0.800 | +2.1 | none |
| UUP | data_print:ppi | 1 | 40 | 48% | 48% | 0.599 | +21.2 | none |
| UUP | data_print:ppi | 2 | 41 | 71% | 47% | 0.002 | +25.9 | **earned** |
| UUP | data_print:ppi | 3 | 28 | 57% | 45% | 0.120 | +5.6 | too few |
| UUP | data_print:unrate | 0 | 100 | 50% | 47% | 0.292 | +5.0 | none |
| UUP | data_print:unrate | 1 | 48 | 44% | 49% | 0.829 | -12.0 | none |
| UUP | data_print:unrate | 2 | 44 | 52% | 47% | 0.246 | +18.2 | none |
| UUP | data_print:unrate | 3 | 27 | 67% | 50% | 0.075 | +25.2 | too few |
| UUP | earnings_8k | 0 | 3 | 67% | 45% | 0.680 | +nan | too few |
| UUP | earnings_8k | 1 | 1 | 100% | 100% | 1.000 | +nan | too few |
| UUP | earnings_8k | 2 | 11 | 64% | 53% | 0.360 | +37.5 | too few |
| UUP | earnings_8k | 3 | 26 | 77% | 67% | 0.085 | +99.4 | too few |
| UUP | fomc_minutes | 0 | 40 | 60% | 51% | 0.211 | +0.5 | none |
| UUP | fomc_minutes | 1 | 26 | 54% | 46% | 0.210 | +5.6 | too few |
| UUP | fomc_minutes | 2 | 24 | 42% | 48% | 0.805 | +5.9 | too few |
| UUP | fomc_minutes | 3 | 19 | 37% | 49% | 0.945 | -30.5 | too few |
| UUP | fomc_statement | 0 | 48 | 54% | 48% | 0.239 | +39.9 | none |
| UUP | fomc_statement | 1 | 29 | 52% | 48% | 0.420 | +24.1 | too few |
| UUP | fomc_statement | 2 | 26 | 50% | 52% | 0.715 | -2.9 | too few |
| UUP | fomc_statement | 3 | 16 | 56% | 46% | 0.410 | +58.7 | too few |
| UUP | political_order | 0 | 6 | 67% | 67% | 1.000 | -396.5 | too few |
| UUP | political_order | 1 | 7 | 57% | 52% | 0.725 | -9.8 | too few |
| UUP | political_order | 2 | 1 | 0% | 0% | 1.000 | +nan | too few |
| UUP | political_order | 3 | 36 | 64% | 62% | 0.552 | -13.0 | none |
