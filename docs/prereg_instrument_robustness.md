# Pre-registration — instrument robustness (TRACK §3.10)

*Registered 2026-09-29, before any code. Question: does replacing the five model ETFs with
the instruments the app displays change any verdict? "Probably not" is a prior; this is the
test.*

## 1. What is compared

| model asset (unchanged) | alternative instrument | how its daily log return is built |
|---|---|---|
| SPY | S&P 500 index, `^GSPC` | log(C_t / C_{t−1}) on the NYSE session calendar |
| GLD | gold futures, front month, `GC=F` | same; sessions on which NYSE is closed are dropped |
| USO | WTI crude futures, front month, `CL=F` | same |
| UUP | DXY dollar index, `DX-Y.NYB` | same |
| TLT | 10-year Treasury **price proxy** from the yield `^TNX` | r_t = −D·(y_t − y_{t−1})/100 + (y_{t−1}/100)/252, with **D = 8.0 fixed here** (a constant-maturity 10-year modified duration; not fitted) |

The alternative panel is a copy of `processed/asset_returns.parquet` with those five
**columns replaced under their original names**, so that nothing downstream (the reader
schema's axis map, the estimator, the report emitter) changes. All 42 other columns are
untouched. The macro panel, the regime labels and the document reads are identical in both runs.

## 2. What is run on both panels

1. The report backfill (`src/report_backfill.py`) on the current corpus, scored by
   `src/report_scoreboard.py` at the registered 10,000 permutations, with the alternative
   run written to its own folder `outputs/reports_backfill/<hash>_altinstr/` — never merged
   with the baseline `48a6c4e879a1_n2617`.
2. Problem 1 (the safe-haven test) on the alternative panel, if its script accepts a panel
   path; otherwise deferred and recorded as such.

The forward ledger, `models.yaml` and the frozen models are not touched.

## 3. Criteria — fixed before the run

| # | criterion | threshold |
|---|---|---|
| C1 | primary-cell verdict (h*=3, close-to-close, non-overlap) | identical word (FAIL / INCONCLUSIVE / PASS) |
| C2 | sign agreement of the report's `net_view` × realised outcome across (date, asset) rows present in both runs | ≥ 90% of rows agree on hit/miss |
| C3 | non-overlap hit-rate | within 2.0 points |
| C4 | asymmetry | within 0.15 |

**All four → CONSISTENT.** The app may say: *"Modelled on SPY, TLT, GLD, UUP and USO; shown
as the S&P 500, the 10-year yield, gold futures, DXY and WTI. Verdicts are unchanged on the
alternative panel."*

**Any one fails → DIFFERENT**, and the difference is attributed before anything else is done:

- per asset, which instrument pair drives the disagreement (rows where hit/miss flips);
- per mechanism, whether flips concentrate on FOMC statement days (settlement timing: GLD 4 pm
  vs `GC=F` 1:30 pm ET, `CL=F` 2:30 pm, against a 2 pm announcement), on futures-roll weeks
  (USO), or on the Treasury pair (maturity and the proxy's fixed D).

The app then shows whichever the record supports, and says why.

## 4. Priors, stated

- C1 holds (the FAIL is not a knife-edge on the new corpus: hit 58.2% vs 58.8%).
- C2 holds for SPY/^GSPC and UUP/DXY at > 97%; lower for GLD and USO; lowest for TLT/proxy.
- If anything fails it will be C3 or C4 through the Treasury proxy, because a 10-year
  constant-maturity proxy and a 20+-year ETF are different instruments — and that is expected,
  not a defect.

## 5. What this does not decide

Whether the model *should* run on the alternative instruments. That would be a change to the
registered estimator and its universe, requiring its own registration; this test only decides
what the app may claim.

## 6. Amendments

| date | change | reason |
|---|---|---|
| — | — | — |
