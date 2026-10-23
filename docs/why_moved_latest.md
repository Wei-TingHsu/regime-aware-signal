# Why it moved — 2026-10-23 16:56

*Turning points: reversal > max(8%, 1.5 × 20-session volatility scaled to a month). Attribution: joint fit, sensitivities from the two years before the episode. Target: base rate of this asset's past episodes in the same direction (median size; quartiles), UNTESTED as a conditional claim (prereg_factor_attribution §4, prior #62).*

## US equities (SPY)

- Current episode: **up since 2026-03-30** (trough confirmed; 143 sessions), move so far +21.5%; extreme so far +23.9% on 2026-10-06; reversal threshold now 8.0%.
- Typical rise of this kind for US equities: +24.2% from the start (middle half of past episodes +16.1% to +48.9%), median 130 sessions, n 30 — this one is at 90% of the typical size; the typical level is +2.3% from here (band -4.5% to +22.6%). Base rate, UNTESTED as a conditional target.
- **The impulse** (purest stretch, 2026-03-30 → 2026-05-26, 39 sessions, +18.8%): equity volatility (VIX) +26%, macro state, PCA line 1 +11%, real 10-yr yield -4%; unexplained +47%.
- Window where the reasons explain most, chosen after the fact (a ceiling, not a result): first 3 sessions to 2026-04-02, +3.8%, explained 75%. Causal rule (stop after 5 sessions without improvement): first 8 sessions, +7.5%, explained 71% — T-F not run. Noise calibration of the ceiling: a time-shifted series reaches 8% by the same after-the-fact choice, so the ceiling's excess over noise is +68% points.
- Episode attribution (joint fit): macro state, PCA line 1 +40%, real 10-yr yield -38%, equity volatility (VIX) +24%, macro state, PCA line 2 +4%; prior-trend drift +53%; **unexplained +15%**. Stable sensitivities: geopolitical risk (GPR index), rate-hike speculation (2-yr yield minus fed funds), real 10-yr yield, US dollar (broad index), oil (WTI spot), equity volatility (VIX), macro state, PCA line 1, macro state, PCA line 2.
- Last session 2026-10-22: -1.2%; reasons macro state, PCA line 1 +0.04%, macro state, PCA line 2 -0.00%, geopolitical risk (GPR index) +0.00%; unexplained -1.29%.

## long Treasuries (TLT)

- Current episode: **down since 2026-02-27** (peak confirmed; 164 sessions), move so far -7.2%; extreme so far -12.5% on 2026-10-05; reversal threshold now 8.0%.
- Typical fall of this kind for long Treasuries: -11.8% from the start (middle half of past episodes -10.4% to -17.1%), median 82 sessions, n 25 — this one is at 60% of the typical size; the typical level is -5.0% from here (band -3.4% to -10.7%). Base rate, UNTESTED as a conditional target.
- **The impulse** (purest stretch, 2026-02-27 → 2026-03-27, 20 sessions, -5.4%): macro state, PCA line 2 +123%, real 10-yr yield -74%, US dollar (broad index) +60%; unexplained -28%.
- Window where the reasons explain most, chosen after the fact (a ceiling, not a result): first 111 sessions to 2026-08-07, -6.8%, explained 100%. Causal rule (stop after 5 sessions without improvement): first 13 sessions, -3.9%, explained 100% — T-F not run. Noise calibration of the ceiling: a time-shifted series reaches 15% by the same after-the-fact choice, so the ceiling's excess over noise is +85% points.
- Episode attribution (joint fit): macro state, PCA line 2 +185%, real 10-yr yield -138%, macro state, PCA line 1 +52%, US dollar (broad index) +51%; prior-trend drift -1%; **unexplained -79%**. Stable sensitivities: rate-hike speculation (2-yr yield minus fed funds), real 10-yr yield, US dollar (broad index), equity volatility (VIX), macro state, PCA line 1, macro state, PCA line 2.
- Last session 2026-10-22: +1.9%; reasons macro state, PCA line 2 +0.08%, macro state, PCA line 1 -0.01%, geopolitical risk (GPR index) -0.00%; unexplained +1.78%.

## gold (GLD)

- Current episode: **down since 2026-08-25** (peak confirmed; 41 sessions), move so far -13.8%; extreme so far -13.8% on 2026-10-22; reversal threshold now 9.4%.
- Typical fall of this kind for gold: -14.0% from the start (middle half of past episodes -12.1% to -17.3%), median 57 sessions, n 27 — this one is at 98% of the typical size; the typical level is -0.3% from here (band +2.0% to -4.0%). Base rate, UNTESTED as a conditional target.
- **The impulse** (purest stretch, 2026-08-25 → 2026-09-01, 5 sessions, -7.3%): real 10-yr yield -20%, macro state, PCA line 1 +19%, US dollar (broad index) +10%; unexplained +94%.
- Window where the reasons explain most, chosen after the fact (a ceiling, not a result): first 22 sessions to 2026-09-25, -8.1%, explained 61%. Causal rule (stop after 5 sessions without improvement): first 5 sessions, -7.3%, explained 12% — T-F PASS. Noise calibration of the ceiling: a time-shifted series reaches 12% by the same after-the-fact choice, so the ceiling's excess over noise is +49% points. Best swept rule (same leg definition; look-back 252, patience 10, min 3; sub-grid p 0.00): first 3 sessions, explained 47%: macro state, PCA line 1 +30%, real 10-yr yield -28%, US dollar (broad index) +20%.
- Episode attribution (joint fit): US dollar (broad index) +38%, real 10-yr yield -38%, macro state, PCA line 1 +37%, oil (WTI spot) -14%; prior-trend drift -27%; **unexplained +91%**. Stable sensitivities: US dollar (broad index), oil (WTI spot), macro state, PCA line 1, macro state, PCA line 2.
- Last session 2026-10-22: -2.6%; reasons speculative liquidity (Bitcoin) -0.26%, macro state, PCA line 1 -0.03%, macro state, PCA line 2 +0.02%; unexplained -2.46%.

## silver (SLV)

- Current episode: **down since 2026-08-27** (peak confirmed; 39 sessions), move so far -21.4%; extreme so far -21.4% on 2026-10-22; reversal threshold now 17.6%.
- Typical fall of this kind for silver: -17.6% from the start (middle half of past episodes -13.9% to -23.9%), median 41 sessions, n 47 — this one is at 124% of the typical size; it is already beyond the typical size — larger than 62% of past episodes of this kind; the base rate gives no further level. Base rate, UNTESTED as a conditional target.
- **The impulse** (purest stretch, 2026-08-27 → 2026-09-01, 3 sessions, -7.7%): real 10-yr yield -17%, macro state, PCA line 1 +13%, US dollar (broad index) +12%; unexplained +88%.
- Window where the reasons explain most, chosen after the fact (a ceiling, not a result): first 20 sessions to 2026-09-25, -7.4%, explained 77%. Causal rule (stop after 5 sessions without improvement): first 20 sessions, -7.4%, explained 77% — T-F not run. Noise calibration of the ceiling: a time-shifted series reaches 19% by the same after-the-fact choice, so the ceiling's excess over noise is +58% points.
- Episode attribution (joint fit): US dollar (broad index) +39%, real 10-yr yield -24%, macro state, PCA line 1 +19%, oil (WTI spot) -11%; prior-trend drift -20%; **unexplained +88%**. Stable sensitivities: US dollar (broad index), oil (WTI spot), equity volatility (VIX), macro state, PCA line 1.
- Last session 2026-10-22: -5.6%; reasons speculative liquidity (Bitcoin) -0.55%, macro state, PCA line 1 -0.03%, macro state, PCA line 2 +0.02%; unexplained -5.29%.

## the dollar (UUP)

- Current episode: **up since 2025-07-02** (trough confirmed; 329 sessions), move so far +11.3%; extreme so far +12.2% on 2026-10-12; reversal threshold now 8.0%.
- Typical rise of this kind for the dollar: +21.8% from the start (middle half of past episodes +11.6% to +25.2%), median 215 sessions, n 9 — this one is at 54% of the typical size; the typical level is +9.4% from here (band +0.3% to +12.5%). Base rate, UNTESTED as a conditional target.
- **The impulse** (purest stretch, 2025-07-02 → 2025-07-31, 20 sessions, +3.9%): US dollar (broad index) +50%, macro state, PCA line 1 +13%, macro state, PCA line 2 -4%; unexplained +31%.
- Window where the reasons explain most, chosen after the fact (a ceiling, not a result): first 16 sessions to 2025-07-25, +1.3%, explained 73%. Causal rule (stop after 5 sessions without improvement): first 9 sessions, +1.8%, explained 63% — T-F not run. Noise calibration of the ceiling: a time-shifted series reaches 14% by the same after-the-fact choice, so the ceiling's excess over noise is +59% points.
- Episode attribution (joint fit): macro state, PCA line 1 +29%, real 10-yr yield -23%, US dollar (broad index) +16%, macro state, PCA line 2 +5%; prior-trend drift +50%; **unexplained +24%**. Stable sensitivities: geopolitical risk (GPR index), real 10-yr yield, US dollar (broad index), equity volatility (VIX), macro state, PCA line 1.
- Last session 2026-10-22: -0.1%; reasons macro state, PCA line 1 +0.01%, macro state, PCA line 2 -0.01%, speculative liquidity (Bitcoin) -0.00%; unexplained -0.09%.

## oil (USO)

- Current episode: **up since 2026-07-01** (trough confirmed; 79 sessions), move so far +57.4%; extreme so far +57.4% on 2026-10-22; reversal threshold now 13.8%.
- Typical rise of this kind for oil: +23.9% from the start (middle half of past episodes +18.2% to +41.5%), median 56 sessions, n 44 — this one is at 212% of the typical size; it is already beyond the typical size — larger than 86% of past episodes of this kind; the base rate gives no further level. Base rate, UNTESTED as a conditional target.
- **The impulse** (purest stretch, 2026-07-01 → 2026-07-23, 15 sessions, +35.1%): oil (WTI spot) +75%, real 10-yr yield -7%, macro state, PCA line 2 +7%; unexplained +19%.
- Window where the reasons explain most, chosen after the fact (a ceiling, not a result): first 26 sessions to 2026-08-07, +14.2%, explained 82%. Causal rule (stop after 5 sessions without improvement): first 7 sessions, +14.1%, explained 78% — T-F not run. Noise calibration of the ceiling: a time-shifted series reaches 24% by the same after-the-fact choice, so the ceiling's excess over noise is +58% points.
- Episode attribution (joint fit): oil (WTI spot) +75%, real 10-yr yield -14%, macro state, PCA line 2 +11%, macro state, PCA line 1 +4%; prior-trend drift +15%; **unexplained +8%**. Stable sensitivities: real 10-yr yield, oil (WTI spot), equity volatility (VIX), macro state, PCA line 1, macro state, PCA line 2.
- Last session 2026-10-22: +1.7%; reasons macro state, PCA line 2 -0.08%, speculative liquidity (Bitcoin) +0.08%, macro state, PCA line 1 +0.04%; unexplained +1.54%.

## Nvidia (NVDA)

- Current episode: **down since 2026-10-06** (peak confirmed; 12 sessions), move so far -11.3%; extreme so far -11.3% on 2026-10-22; reversal threshold now 12.5%.
- Typical fall of this kind for Nvidia: -26.7% from the start (middle half of past episodes -17.4% to -41.7%), median 36 sessions, n 57 — this one is at 39% of the typical size; the typical level is -17.4% from here (band -6.9% to -34.2%). Base rate, UNTESTED as a conditional target.
- **The impulse** (purest stretch, 2026-10-06 → 2026-10-16, 8 sessions, -10.5%): equity volatility (VIX) +39%, real 10-yr yield -19%, macro state, PCA line 1 +18%; unexplained +63%.
- Window where the reasons explain most, chosen after the fact (a ceiling, not a result): first 8 sessions to 2026-10-16, -10.5%, explained 46%. Causal rule (stop after 5 sessions without improvement): first 8 sessions, -10.5%, explained 46% — T-F not run. Noise calibration of the ceiling: a time-shifted series reaches 9% by the same after-the-fact choice, so the ceiling's excess over noise is +36% points.
- Episode attribution (joint fit): real 10-yr yield -16%, equity volatility (VIX) +13%, macro state, PCA line 2 +7%, macro state, PCA line 1 +4%; prior-trend drift -12%; **unexplained +103%**. Stable sensitivities: US dollar (broad index), oil (WTI spot), equity volatility (VIX), macro state, PCA line 1.
- Last session 2026-10-22: -4.4%; reasons macro state, PCA line 1 +0.06%, macro state, PCA line 2 -0.02%, geopolitical risk (GPR index) +0.00%; unexplained -4.63%.

## Meta (META)

- Current episode: **up since 2026-07-30** (trough confirmed; 58 sessions), move so far +20.1%; extreme so far +44.4% on 2026-09-24; reversal threshold now 19.8%.
- Typical rise of this kind for Meta: +37.7% from the start (middle half of past episodes +27.2% to +62.5%), median 77 sessions, n 26 — this one is at 57% of the typical size; the typical level is +14.7% from here (band +6.0% to +35.4%). Base rate, UNTESTED as a conditional target.
- **The impulse** (purest stretch, 2026-07-30 → 2026-08-11, 8 sessions, +11.1%): equity volatility (VIX) +9%, US dollar (broad index) +2%, real 10-yr yield -2%; unexplained +85%.
- Window where the reasons explain most, chosen after the fact (a ceiling, not a result): first 14 sessions to 2026-08-19, +1.3%, explained 86%. Causal rule (stop after 5 sessions without improvement): first 5 sessions, +9.4%, explained 22% — T-F not run. Noise calibration of the ceiling: a time-shifted series reaches 28% by the same after-the-fact choice, so the ceiling's excess over noise is +58% points.
- Episode attribution (joint fit): macro state, PCA line 1 +46%, real 10-yr yield -19%, oil (WTI spot) -12%, US dollar (broad index) -4%; prior-trend drift +24%; **unexplained +65%**. Stable sensitivities: real 10-yr yield, oil (WTI spot), equity volatility (VIX), macro state, PCA line 1, macro state, PCA line 2.
- Last session 2026-10-22: -6.9%; reasons macro state, PCA line 1 +0.47%, equity volatility (VIX) +0.21%, rate-hike speculation (2-yr yield minus fed funds) -0.14%; unexplained -7.70%.

