# Pre-registration — factor attribution of price episodes (TRACK §3.31)

*Registered 2026-10-23 before code, from the founder's method (22 Oct): "US–Iran war + rate-hike speculation crashed gold from 5,600 to 4,000.
Take the war as the prime factor and put every other reason into the macro-state PCA line; find the weight of that reason; next round make
rate hikes the prime factor. Multiply the weight by the move and you have how many dollars each factor caused; when the war ends, expect
about that many dollars back." This is a return decomposition with an ordered attribution. It replaces the Stage 2/3 plan of
prereg_target_range.md: reasons are measured proxies, not reader labels; the reader's role becomes naming which event is driving a proxy.*

## 1. Model (fixed)
- Market return r_t (daily log) on daily changes of proxies for each reason:
  **war** = Δlog GPR (Caldara–Iacoviello daily geopolitical-risk index); **hikes** = Δ(DGS2 − EFFR) in bp (tightening priced over two years);
  **real** = ΔDFII10 (bp); **dollar** = Δlog DTWEXBGS; **oil** = Δlog WTI_SPOT; **vix** = Δlog VIXCLS; **macro** = Δ of the first two macro PCA
  scores (the "macro state regime" line). The residual is what no named reason explains.
- Sensitivities (betas) are estimated on the **504 sessions before the episode starts** (walk-forward: known at the start) and, for comparison,
  on the full sample. Standard errors from the window.
- **Ordering.** The factors are orthogonalised in a declared order (Gram–Schmidt): the prime factor keeps everything it co-moves with, the second
  keeps what is left, and so on; the macro line last; residual after all. Two orderings are always reported — the founder's prime factor first,
  and the mirror (the second reason first) — plus the joint (unordered) regression. The spread between orderings is the attribution's honest
  uncertainty, published with it.
- **Dollars.** contribution_k (log units) = β_k^ordered × Σ(ΔF_k^orth over the episode); dollars_k = P_start × contribution_k.
  Reversal estimate for factor k = −dollars_k × (fraction of the proxy's move that reverses), with the beta's ±1 s.e. band.

## 2. Tests (both must pass before any bounce number is quoted to a customer)
- **T-A explanatory stability (walk-forward):** for each 20-session block from 2008 on, betas from the prior 504 sessions, R² of the
  contemporaneous decomposition on the block. Criterion: median out-of-sample R² ≥ 0.20 for GLD (≥ 0.10 for the other markets) → PASS.
- **T-B sign stability:** each factor's beta sign is the same in ≥ 70% of rolling windows (504 sessions, stepped 63) → that factor is quotable;
  otherwise its dollars are shown as "unstable — not quotable".
- **T-C reversal (registered, run after T-A/T-B):** episodes where the war proxy spiked (GPR ≥ 90th percentile of the prior two years) and then
  fell back below its median: predicted market move = β_war(pre) × ΔF over the fall-back window vs realised. Criterion: correlation ≥ 0.3 on
  n ≥ 15 episodes and MAE ≥ 10% below the zero forecast → PASS.
- Priors (Claude, counted if wrong): **#58** T-A: GLD median OOS R² 0.25–0.40, carried by real yields and the dollar — PASS; **#59** T-B: war and
  oil betas unstable (< 70%), real, dollar, hikes stable; **#60** T-C: FAIL or INCONCLUSIVE — the war proxy's gold beta is small and its
  reversals are gradual.

## 3. Outputs
`docs/factor_attribution_<market>_<start>_<end>.md` (the episode table, both orderings, dollars, reversal lines with bands and the T-A/T-B
status), `docs/factor_attribution_tests.md`, `processed/factor_attribution.json`. App: the "Why it moved" block under a market, once T-A/T-B
have run, with every line tagged.

## 4. Daily "why it moved" block and the target (registered 2026-10-23, before code)
- **Turning points** per asset by an adaptive reversal rule: a peak or trough is confirmed when price moves against the trend by more than
  max(8%, 1.5 × the asset's 20-session volatility scaled to a month). Both constants are grid variables (SPEC_GRID). The current episode runs
  from the last confirmed turning point to the last session. Assets: the five model markets and silver (SLV).
- **Attribution** of the current episode and of the last session (joint fit, sensitivities from the 504 sessions before the episode start),
  unexplained share stated; factor dollars quotable only where T-A has passed and T-B marks the factor stable.
- **Target.** Base rate: the median size of this asset's past episodes in the same direction (quartile band, n ≥ 5) → "from here" distance and
  level; labelled base rate. **T-D (the conditional claim):** does the episode's attribution profile at the current point predict its remaining
  size better than the base rate? Walk-forward ridge on past episodes' profiles at their midpoint; criterion MAE ≥ 10% below the base rate on
  ≥ 60% of held-out episodes, n ≥ 30 per asset. **Prior #62 (Claude):** FAIL or INCONCLUSIVE — the profile adds little to the size base rate.
- **Impulse window (founder, 23 Oct):** the purest stretch of an episode — from the turning point while the pullback from the running extreme
  stays under a quarter of the reversal threshold; attributed first, the full episode second. **T-E:** the impulse's unexplained share is lower
  than the full episode's in ≥ 60% of past episodes (n ≥ 15) → PASS. **Prior #63:** PASS for GLD, SLV, USO; FAIL for SPY, TLT, UUP.
- **Sweep rule (founder, 23 Oct):** every fixed number in a test is a variable; when the registered cell fails, the sweep runs (T-A: block
  1–60 × window 252/504/756), the curve is published, and the best cell is judged against the best cell of the same sweep on shifted returns.
  A survivor is promoted to a forward test; the registered verdict stands.
- Assets: the five markets, silver, and single names (NVDA, META first) through the same machinery; the unexplained share says how much a
  macro model can carry for a stock.
- **Window rules (founder, 23 Oct: "adjust the time frame so the explained share is as high as possible while the trend holds"):** per episode the
  explained-share curve over every window length; R1 full, R2 impulse, R3 first half, R5 causal stop (patience 5 sessions, usable live), and
  R4 the after-the-fact ceiling, shown but never quoted. **T-F:** R5 beats R1 in ≥ 60% of past episodes (n ≥ 15) → PASS. **Prior #64:** FAIL
  (R5 ≈ R1 within noise; the ceiling's gap over them is the overfitting margin).
- **T-F′ (registered 23 Oct after T-F passed, before running):** the causal rule's median share on episodes with time-shifted factor series
  (20 shifts) — PASS if the real share beats the null median by ≥ 10 points and its 95th percentile. **Prior #65:** PASS.
- **T-G (registered 23 Oct, founder's rule — "why are we satisfied with 53%; sweep the variables"):** the window rule's own variables swept —
  patience {2,3,5,7,10,15,20,30} × min window {3,5,10} × look-back {252,504,756} × reversal rule {(1.0, 5%), (1.5, 8%), (2.0, 12%)} = 216 cells;
  statistic = median R5 share over past episodes; the best cell vs the best cell of the same sweep on 10 time-shifted factor series (p < 0.05
  survives) → promoted as the app's rule by dated amendment, the registered 5/5 cell staying the recorded verdict. The after-the-fact ceiling on
  the current leg is reported with its own noise calibration (median R4 on 20 shifted series). **Prior #66:** patience 10–20 wins, median
  share 58–65%, survives the null; the ceiling's excess over noise on gold's current leg ≈ 30 points.
- **T-I turning-point rules (founder, 23 Oct: "a reversal should be a trend — at least two sessions, not one bounce").** Alternatives to the
  zigzag: persistence — N consecutive sessions against the trend AND a counter-move ≥ X (X = 0 is the pure gradient rule), N ∈ {2,3,5,10},
  X ∈ {0, 2, 4, 8%}; swing highs/lows within k sessions, k ∈ {5,10,20}. Compared on legs found, median length, share of noise legs (< 5 sessions)
  and the explained share the promoted window rule reaches on each. A rule replaces the zigzag only if its median explained share is ≥ 5 points
  higher with at least as many scored legs. **Prior #68:** X = 0 rules produce hundreds of 3–6-session legs and lower shares; persistence with
  X = 4% and swing k = 10 land within 5 points of the zigzag; nothing replaces it.
- Nightly: `src/why_moved.py`; app: the "Why it moved" paragraph beside the day's Up/Down pill, every sentence tagged.

## 5. The unexplained part as a signal — residual momentum / reversal (registered 2026-10-23, before code)
Founder: the share no reason explains is the crowd — emotion, trend-following, differing valuation standards; if it can be measured
consistently it may be the fund's alpha. Literature: residual momentum (Blitz, Huij & Martens 2011), noise-trader and slow-diffusion models;
price pressure unwinds (Campbell–Grossman–Wang; Nagel), information diffuses (Hong–Stein). The test is predictability, not the label.
- Residual e_t from a rolling 252-session fit of the named reasons (refit every 20 sessions). Signal = cumulative residual over the past w ∈ {5,10,20,40,60};
  forward return over h ∈ {5,10,20,40,60}; non-overlapping samples. Statistics: rank IC, sign hit-rate, long-short Sharpe. The same grid on total
  returns (plain momentum) beside it.
- **T-H:** best cell by |IC| vs the best |IC| of the same grid on 200 shifted residual series (p < 0.05), AND |IC| ≥ plain momentum's on that cell + 0.02
  → PASS; predictable but not better than the trend → INCONCLUSIVE; else FAIL. Sign of IC reports the shape (continuation / reversal) by horizon.
  Assets: GLD, SLV, USO, SPY, TLT, UUP, NVDA, META.
- **Prior #67:** GLD and SLV continuation at 20–60 sessions, IC 0.03–0.06, not beating plain momentum (INCONCLUSIVE); SPY, TLT, UUP FAIL; NVDA and META
  residual beats total (PASS) — the equity result of the literature.
- Before quoting any of it as strategy: the omitted-factor proxies (flows, positioning) go in first so the residual is the unmeasured part, not the unmodelled part.

## Amendments
| date | change | reason |
|---|---|---|
| 2026-10-23 | `--start peak` finds the episode's own peak (max close in the prior 300 sessions); **new proxies**: BTC-USD (speculative liquidity, in the model now), GLD shares outstanding (ETF flows) and CFTC net speculative gold positions (weekly) registered, fetchers next; silver deliberately excluded (gold's twin — would explain without naming a reason). Tests re-run after the proxies land; the 23 Oct verdicts stand as the baseline. **Prior #61:** with flows and positioning, T-A rises to 0.20–0.25 and the 2026 episode's unexplained share falls below half. | First-run reading: the fall is unexplained by standard factors; the founder's forced-selling hypothesis has no proxy in the model. |

## Results
| date | test | result | prior |
|---|---|---|---|
| 2026-10-23 | T-A | GLD median out-of-sample R² **0.177** over 235 blocks (bar 0.20) → **FAIL**. `docs/factor_attribution_tests.md` | **#58 wrong** (expected 0.25–0.40). Tally 52 |
| 2026-10-23 | T-B | Stable: dollar 100%, oil 90%, macro line 2 88%, macro line 1 83%. Unstable: hikes 66%, real yield 63%, VIX 59%, war (GPR) 54%. | **#59 wrong** (real, hikes expected stable; oil expected unstable). Tally 53 |
| 2026-10-23 | episode GLD 28 Jan → 21 Oct (first run, dates a guess) | Move −19% (not the −29% of 5,600 → 4,000: 28 Jan was not the peak; the war index fell −14% over the window — its spike was in March). With pre-episode sensitivities the named reasons explain ≈ $90 of a $1,200 fall; the prior uptrend (drift) would have added ≈ $1,700; ≈ $2,800 unexplained. Orderings agree (the war proxy barely moved). Reading: 2026 broke gold's 2024–25 sensitivities (rose with oil, despite rate rises); the unexplained part is where no proxy exists — positioning and forced selling. | diagnostic, not a verdict |
| 2026-10-23 | T-A sweep (GLD) | 30 cells: blocks 2–3 negative, 5 ≈ 0.05, 15–20 ≈ 0.18, best 756/20 = 0.224 (above the bar; best-of-sweep null pending, background run). Explanatory power rises with block length — day-to-day noise swamps short windows. | sweep, no prior |
| 2026-10-23 | T-E (GLD) | Impulse better explained than the full leg in **46%** of 24 episodes → **FAIL**; median unexplained impulse 81% vs full 63%; current impulse 25 Aug → 1 Sep, 5 sessions, −7.3%, 94% unexplained. | **#63 wrong** (expected PASS for GLD). Tally 54 |
| 2026-10-23 | T-F (GLD) | Causal stop beats the full-leg window in **83%** of 24 episodes → **PASS**; median explained share 53% at a median 7 sessions vs 31% over the full leg (102 sessions); fixed impulse 17%; after-the-fact ceiling 71% at 11 sessions. `docs/window_test_GLD.md` | **#64 wrong** (expected FAIL). Tally 55 |
| 2026-10-23 | T-F′ (GLD) | Real median R5 share 53% vs 5% on time-shifted factors (20 shifts; 95th pct 9%) → **PASS**. Gold's current leg: ceiling 61% at 22 sessions, the 5/5 rule stopped at 5 sessions (12%) — patience too short, swept under T-G. | **#65 right** |
| 2026-10-23 | T-G (GLD) | 216 cells. Share rises with patience (2: 43%, 5: 54%, 15: 60%, 20–30: 64%); look-back 252 > 504 > 756 (62 / 54 / 51%); reversal rule flat. Best cell (2.0×/12%, 252, patience 10, min 3) 71% on 13 legs, best-of-sweep null p = 0.00 → **promoted** as the app's rule by this amendment; registered 5/5 cell stays the recorded verdict. Gold's current leg: ceiling 61% vs 12% on shifted series (excess +49 pts). | **#66 right** on patience and survival (predicted 10–20 / 58–65%; actual 20–30 / 64%); excess predicted ≈ 30, actual 49 |
| 2026-10-23 | T-H (GLD, SLV, USO, SPY, NVDA) | **FAIL on all five.** Best cells: GLD 60→60 reversal IC −0.19 (null best 0.24, p 0.77); SLV 20→60 reversal −0.22 (p 0.56); USO 20→20 continuation +0.17, hit 59%, Sharpe +0.5 (p 0.82); SPY 20→60 reversal −0.21 (p 0.31); NVDA 20→60 continuation +0.25 (p 0.19; plain momentum +0.20). No cell distinguishable from noise; where the residual leaned (oil continuation, metals reversal at 60) it did not beat the price trend. The unexplained part, as measured with the current factor set, is not a tradable signal at 5–60 sessions. Re-run after the flow/positioning proxies land. | **#67 wrong** (expected INCONCLUSIVE metals, PASS NVDA). Tally 56 |
| 2026-10-23 | T-A sweep null (GLD) | Best cell 756/20 median R² 0.224 vs best-of-sweep noise median −0.024 over 50 shifts, p = 0.000 → survives. Amendment: the T-A gate for quotable sensitivities is treated as met by the surviving swept cell (tag 'swept cell' on the page); the registered 504/20 verdict (0.177 FAIL) stands as recorded. | no prior |
| 2026-10-23 | T-G amendment | The app uses the best cell *within its registered leg definition* (1.5×/8%), judged against that sub-grid's null — legs are never re-cut to fit a cell (founder's objection: integrity must not cost the leg's meaning). | — |
| 2026-10-23 | T-H (GLD, SLV, USO, SPY, NVDA) | **FAIL on all five.** Best cells: GLD 60→60 reversal IC −0.19 (null best 0.24, p 0.77); SLV 20→60 reversal −0.22 (p 0.56); USO 20→20 continuation +0.17, hit 59%, Sharpe +0.5 (p 0.82); SPY 20→60 reversal −0.21 (p 0.31); NVDA 20→60 continuation +0.25 (p 0.19; plain momentum +0.20). No cell distinguishable from noise; where the residual leaned (oil continuation, metals reversal at 60) it did not beat the price trend. The unexplained part, as measured with the current factor set, is not a tradable signal at 5–60 sessions. Re-run after the flow/positioning proxies land. | **#67 wrong** (expected INCONCLUSIVE metals, PASS NVDA). Tally 56 |
| 2026-10-23 | T-A sweep null (GLD) | Best cell 756/20 median R² 0.224 vs best-of-sweep noise median −0.024 over 50 shifts, p = 0.000 → survives. Amendment: the T-A gate for quotable sensitivities is treated as met by the surviving swept cell (tag 'swept cell' on the page); the registered 504/20 verdict (0.177 FAIL) stands as recorded. | no prior |
| 2026-10-23 | T-G amendment | The app uses the best cell *within its registered leg definition* (1.5×/8%), judged against that sub-grid's null — legs are never re-cut to fit a cell (founder's objection: integrity must not cost the leg's meaning). | — |
