# Pre-registration — target-range engine (TRACK §3.29, T2 + T13)

*Registered 2026-10-22 before code, at the founder's direction: attribution, magnitude and a point target are to be designed and tested, not
discussed. What A3b tested and failed was **direction** (sign hit-rate at 20 sessions from three shock-week features, as few as 8 comparable
cases). This engine answers a different question — **how far, how likely** — which depends on volatility and regime, both of which persist.*

## Output (fixed form)
For a market, today's price P, a horizon h and a target T: the median h-session path end (P × e^median), the inter-quartile band, and
**the probability that the price touches T within h sessions** under today's condition, with the independent-case count, against the
unconditional probability. The point target is the median; the probability is the claim. Reasons (Stage 2/3) may shift the probability only
through cells that have passed their own test.

## Stage 1 — statistics (built 22 Oct)
- Markets SPY, TLT, GLD, UUP, USO, WTI_SPOT; horizons 20, 60, 120 sessions; targets ±2.5, 5, 10, 15, 20%.
- For every session i: max and min cumulative log return over sessions i+1 … i+h. Reach-up(X) = share of sessions whose max ≥ log(1+X);
  reach-down likewise. Conditioned on the regime label at i (expanding labels, as the app); "all" row unconditional. Independent cases = n ÷ h.
- **Test (walk-forward calibration):** for each year y = 2012 … last complete year, probabilities are estimated from sessions whose window
  ends before 1 Jan y, applied to non-overlapping starts in y (step h), scored by Brier against the unconditional probabilities estimated the
  same way. Primary cells: h = 60, X = 5% and 10%, up and down, each market. Criterion: Brier skill ≥ 0.05 and positive in ≥ 60% of years →
  PASS; skill ≤ 0 → FAIL; else INCONCLUSIVE. 10% of cells may pass by chance at this count (48 cells); a PASS is reported with that sentence.
- **Prior #55 (Claude):** skill between 0 and 0.03 on most cells — the regime adds little beyond what the unconditional base rate already
  carries; INCONCLUSIVE overall, no market with a majority of PASS cells.

## Stage 2 — reasons (registered, built after Stage 1 is recorded)
- Episodes: peak-to-trough and trough-to-peak swings ≥ 10% per market, 1995 →.
- The reader labels the documents dated inside each episode (FOMC, 8-K, political; prints from 2026) with the reasons present, v1 vocabulary
  open-ended on the first pass over 20 episodes, then **frozen** before the full pass (the prompt-review rule of prereg_prints).
- Measured: each reason's frequency in rises vs falls (lift) with a label-permutation null; nothing enters Stage 3 without lift p < 0.05/k
  for k reasons.
- **Prior #56:** fewer than three reasons clear the bar; the same reasons appear in both rises and falls.

## Stage 3 — weights (registered, built after Stage 2)
- Walk-forward regularised quantile model: inputs = reason indicators that cleared Stage 2 + regime + trailing 60-session volatility;
  output = the 25/50/75 quantiles of the h-session path end and the reach probabilities. Scored on held-out years by pinball loss and Brier
  against Stage 1. Criterion: ≥ 5% improvement on both, in ≥ 60% of years. Weights are published with the cell count that earned them.
- **Prior #57:** volatility carries the improvement; reasons add < 1%; FAIL on the reasons' marginal contribution.

## Amendments
| date | change | reason |
|---|---|---|

## Results
| date | stage | result | prior |
|---|---|---|---|
| 2026-10-22 | Stage 1 | Walk-forward calibration, h = 60, ±5/±10%, 2012–2025, 24 cells: **15 FAIL, 9 INCONCLUSIVE, 0 PASS.** Regime-conditional reach probabilities were *less* accurate than unconditional ones on most cells (SPY −0.13 skill at 10%, UUP −0.49 at 10% down); gold up-cells +0.04 but better in only 43–50% of years. Cause identified, not fixed here: the training rule accepted a regime with ≥ 100 overlapping sessions (< 2 independent 60-session cases). Until a cell passes, `ask` leads with the unconditional probability and marks the regime figure uncalibrated. The sample-size rule (independent cases, not sessions) goes to the specification grid (SPEC_GRID §2.9). `docs/target_range_calibration.md` | **#55 wrong** (negative, not ~0). Tally 51 |
