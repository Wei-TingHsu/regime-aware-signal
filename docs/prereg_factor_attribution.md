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

## Amendments
| date | change | reason |
|---|---|---|

## Results
| date | test | result | prior |
|---|---|---|---|
