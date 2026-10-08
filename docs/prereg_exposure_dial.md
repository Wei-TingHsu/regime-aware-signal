# Pre-registration — T1, the exposure dial (roadmap tree 1; TRACK §3)

*Registered 2026-10-07, before any code. The first of the thirteen routes. Everything that
could be tuned is fixed here; nothing in this file is chosen by looking at returns.*

## 1. The claim

A long-only position-size rule that (a) scales exposure to a volatility target and (b) tilts it
by the regime engine's label improves the certainty-equivalent return of holding each core
market, net of costs, out of sample — and does so without the features that make published
volatility-managed strategies disappoint when traded (Cederburg, O'Doherty, Wang and Yan 2020):
no fitted scaling constant, no leverage, and no reaction to unconfirmed regime changes.

The product output is one number per market per day — *how much of a full position to hold*,
between 0 and 100% — displayed beside the existing 3-day line. The 3-day line is untouched.

## 2. Data

- **Universe A (Test A):** the five model ETFs — SPY, TLT, GLD, UUP, USO — daily log returns
  from `processed/asset_returns.parquet`, 2006 onward (each from its own inception).
- **Universe B (Test B):** the registered thirty-ETF extension (U-ETF30, roadmap Appendix B),
  as one book. Run only after Test A has a verdict, whatever it is.
- **Regime labels and posteriors:** the expanding-window labels (`regime_labels_expanding`),
  frozen pipeline, no refit. A day's label uses nothing after its own date.
- **Risk-free rate:** EFFR from the macro panel, for excess returns.
- **Cost table, fixed:** one-way cost 3 bp of traded value for SPY, TLT, GLD; 5 bp for UUP, USO
  (round-trip double). Reported at **1× and 3×** this table. Execution lag: a weight decided at
  close *t* is held from close *t+1* (one session late — the product's own rule).

## 3. The rules, fixed

| element | rule | why it is fixed this way |
|---|---|---|
| volatility forecast `σ̂_t` | exponentially weighted daily variance of the asset's own returns, decay 0.94 (RiskMetrics), annualised; uses returns through *t* only | a published constant, not fitted; the same for every asset and era |
| target `σ*` | **10% annualised** for every asset | one number, chosen before any result; a sweep is forbidden |
| raw dial | `w_t = min(1, σ* / σ̂_t)` | long-only, capped at 100%: the dial de-risks, it never levers — the Cederburg critique is about leverage and about a scaling constant fitted to the sample; both are removed by construction |
| regime tilt (variant 3) | `w_t = min(1, σ* · m_r / σ̂_t)` where `m_r` = (median σ̂ across all regimes) / (median σ̂ within regime *r*), computed on an **expanding** window through *t−1* | the tilt is a ratio of *volatilities*, never of returns, so it cannot be fitted to profitability; it says "in this regime, the forecast tends to run high or low — correct for it" |
| posterior tilt (variant 4) | as variant 3, with `m_r` replaced by the posterior-weighted average of the `m_r` across regimes | tests whether the model's own uncertainty helps |
| hysteresis `δ` | a regime change is **acted on only after the label has been the same for 3 consecutive sessions**, and `w_t` changes only if `|w_t − w_{t−1}| > 0.05` | prevents the dial from trading on flicker; both numbers fixed, not swept |
| rebalance | daily evaluation, trade only when the hysteresis condition fires | — |

Four variants, nested, so each addition is tested against the one before it:

1. **constant 100%** (buy and hold) — the baseline the plan is honest about
2. **vol-targeted** — rules above without the tilt
3. **vol-targeted + regime tilt by label**
4. **vol-targeted + regime tilt by posterior**

## 4. Objective and inference

**Primary metric:** certainty-equivalent excess return, `CER = μ − (γ/2)·σ²`, annualised, with
**γ = 3** fixed; net of costs at 1×. Secondary, reported not tested: Sharpe, maximum drawdown,
annual turnover, and the same at 3× costs and gross.

**Comparisons, each paired on the same days:**

- (i) variant 2 vs 1 — does vol targeting help?
- (ii) variant 3 vs 2 — does the regime tilt add anything beyond vol targeting?
- (iii) variant 4 vs 3 — does the posterior add anything beyond the label?

**Inference.** For (i): stationary block bootstrap (mean block 20 sessions) of the *paired* daily
return difference, 10,000 resamples, 95% interval on the CER difference. For (ii) and (iii), a
second null that targets the regime specifically: the label sequence is **circularly shifted**
by a random offset (preserving run lengths and regime shares), the tilt recomputed, and the CER
difference re-measured, 10,000 times; the p-value is the share of shifted sequences doing at
least as well. A tilt that only works with the *true* labels has information in it; one that
works with shifted labels is just a different vol target.

**Chronological split, fixed:** 2006–2016 and 2017–2026, reported separately; the stability ratio
(second-half effect / first-half effect) must lie in [0.5, 2.0] for a PASS.

## 5. Criteria, fixed

Per asset, per comparison:

- **PASS** — CER difference > 0 net at 1× costs, bootstrap interval excludes zero, stability
  ratio in [0.5, 2.0], and (for ii, iii) the label-shift p < 0.05.
- **INCONCLUSIVE** — positive point estimate, one of the three conditions missed.
- **FAIL** — otherwise.

**Tree-level verdict for Test A:** comparison (i) must PASS on at least three of five assets for
vol targeting to enter the product; comparison (ii) must PASS on at least three of five for the
regime tilt to enter. Each enters only on its own PASS. If (i) passes and (ii) fails, the product
ships a plain vol-targeted dial and says the regime adds nothing to it — recorded as such.

## 6. Priors, stated

- (i) PASS on SPY and USO (the high-vol assets, where de-risking in stress matters most);
  INCONCLUSIVE on GLD and UUP; FAIL or INCONCLUSIVE on TLT. Vol targeting improves drawdown far
  more than it improves CER — that is the literature's finding and this project's expectation.
- (ii) INCONCLUSIVE or FAIL on all five. The regime engine's labels carry essentially no ranking
  power (kernel family, §18 of the record); the prior is that they carry little sizing power
  either. A PASS here would be the first positive use of the labels and would deserve suspicion
  before celebration.
- (iii) FAIL: the posterior is ~1 most days (the app shows 100% confidence routinely), so the
  variant collapses to the label.

## 7. Acceptance tests, before any real data

Registered here; the dial is built against these and no real figure is computed until all pass.

| test | what it checks |
|---|---|
| constant-vol series | on a synthetic series with constant volatility equal to the target, the dial sits at 100% and variants 1–2 have identical returns |
| planted regime vol | on a synthetic series whose volatility doubles in a planted "regime," the tilt reduces exposure there and comparison (ii) PASSES against the shift null |
| shifted labels | on the same series, with labels circularly shifted, comparison (ii) FAILS |
| no look-ahead | `σ̂_t` and `m_r` at *t* are unchanged when all data after *t* is deleted |
| cost accounting | a hand-computed two-trade path reproduces the net return to the basis point |
| hysteresis | a label that flips every session produces zero regime-driven trades |

## 8. What the app may show

A PASS on (i) permits a line per market: *"Exposure: 62% of a full position (volatility-targeted)."*
A PASS on (ii) permits *"… regime-tilted."* Anything short of PASS permits nothing beyond what
the record already says. The dial is never shown as a forecast of direction.

## 9. Test B (registered, run after A)

The thirty-ETF book: risk parity (inverse-vol weights) → vol-targeted risk parity → the same
regime tilts → a model-predictive-control allocator with the trading penalty **equal to the cost
table** (not fitted). Same objective, inference, split, criteria and cost multipliers. Its own
verdict; it does not rescue or revise Test A.

## 10. Amendments

| date | change | reason |
|---|---|---|
| — | — | — |
| 2026-10-07 | Acceptance tests 1 and 2 re-specified after first-run failure (vol equal to target → half the target; fixed regime blocks → irregular lengths); originals preserved in the self-test report | The tests were wrong, not the dial |
| 2026-10-07 | Regime multipliers refreshed every 21 sessions from data through t−1 | §3 fixed 'expanding through t−1' without a cadence; monthly makes the 10,000-shift null computable |
| 2026-10-08 | Variant 4 not run: the frozen pipeline exposes regime labels, not posteriors | Reported, not substituted |
| 2026-10-08 | Test A run. **NO on both** — vol targeting PASS 1/5 (USO), regime tilt 0/5. Prior (i) half wrong (#37); prior (ii) held. CURRENT_STATE §18.14. Criterion not changed to drawdown after the fact; a drawdown claim is a new registration for Test B | Result |
| 2026-10-08 | **Drawdown claim registered for Test B and, retrospectively labelled, for Test A.** Claim: the vol-targeted dial (variant 2) reduces maximum drawdown versus buy-and-hold by ≥ 30% on ≥ 4 of 5 core assets, net at 1×. Null: 10,000 stationary-bootstrap resamples of the paired daily returns, 95% interval on the drawdown ratio. **Prior is contaminated**: it is stated after Test A measured exactly this (SPY −0.83→−0.29, TLT −0.80→−0.57, GLD −0.61→−0.48, UUP −0.26→−0.25, USO −4.08→−1.01). Test A's figures may be cited by T15 as *measured*; the claim becomes *tested* only on Test B's 30-ETF universe, where no figure has been seen | Founder's request; makes the T15 block's figures citable with their status stated |
