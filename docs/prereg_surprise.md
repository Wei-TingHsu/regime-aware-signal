# Pre-registration — surprise conditioning for scheduled events (T9b, TRACK §3.9)

*Registered 2026-09-29, before any code. Origin: the founder's observation that a "hold" when a
hike was priced is a dovish surprise — the text reads neutral, the market moves — and that the
reader cannot see expectations.*

## 1. The claim

For a scheduled event, the market reacts to the **surprise** (decision minus what was priced),
not to the decision. The reader scores the document's content; a surprise measure must be
added beside it, computed only from information available **before** the session's close.

## 2. Stage A — does the surprise explain the reaction? (this registration runs it)

**Events.** The 131 FOMC statements in the corpus (2011–2026). Minutes are excluded from
stage A: they have no decision to be surprised by.

**Level-1 surprise measure, fixed.** `s_t` = change in the 2-year Treasury yield on the
statement day, DGS2(t) − DGS2(t−1), in basis points. Buckets: **hawkish surprise** if
s_t > +2 bp; **dovish surprise** if s_t < −2 bp; **neutral** otherwise. Both thresholds are set
here and are not swept.

**Run-up, fixed.** `u_t` = the asset's own 5-session log return ending at t−1, standardised
within asset over the sample.

**Stance.** The reader's `stance` field for the statement (hawkish / dovish / neutral → +1 / −1 / 0);
if the read carries no stance, the sign of `direction.duration` reversed (a hawkish read is
negative for bond prices).

**Outcome.** The asset's 3-session forward log return from the close of t (the estimator's
registered horizon and estimand).

**Model.** Per asset, OLS: `y_t = a + b1·stance_t + b2·bucket_t + b3·u_t + e_t`, with `bucket`
coded −1/0/+1. Inference by permutation: `bucket` is shuffled across statements 10,000 times;
the two-sided p is the share of permuted |b2| ≥ observed |b2|. Meetings are ~6 weeks apart, so
3-session outcomes do not overlap and no block structure is needed.

**Criterion, fixed.**

- **PASS**: b2 significant at p < 0.05 with the *expected sign* on **both** TLT (negative:
  hawkish surprise → bond prices fall) and GLD (negative).
- **INCONCLUSIVE**: one of the two.
- **FAIL**: neither.

SPY, UUP and USO are reported with expected signs (SPY −, UUP +, USO −) but do not enter the
criterion. The stance × bucket interaction and the 3 × 3 table of mean outcomes by (stance,
bucket) are reported descriptively, never tested.

**Prior, stated.** PASS on TLT is likely (the 2-year change on the day *is* the bond market's
own reaction, so this is close to tautological for Treasuries and the test is weak there);
GLD is the informative one. Level 1 is a proxy; if it passes only on TLT, the result says
"the proxy measures the bond market, not the surprise", and level 2/3 (the published
Swanson / Bauer–Swanson series) is the next registration.

## 3. Stage B — conditioning the precedent pool (registered, not run)

If stage A is PASS or INCONCLUSIVE-on-GLD: the precedent pool for FOMC-statement days adds the
surprise bucket as a third conditioning key beside regime and document class. Test: the report
backfill re-run with the conditioned pool, scored by the same scorer; criterion = the registered
source-expansion rule (§8 of `prereg_report_scoreboard.md`) applied to FOMC-day rows — pooled
hit-rate on those rows must not fall by more than 2 points and the lower bound must exceed −5,
with the expected direction being an *improvement*. A change to the estimator; it runs beside
the incumbent, never instead of it, and the forward test is untouched.

## 4. Other event classes — registered as later stages, each its own file

| class | expectation source | status |
|---|---|---|
| earnings releases | analyst consensus (yfinance `earnings_dates`, recent years; paid for depth) | stage C |
| scheduled macro releases (NFP, CPI, PPI, GDP) | consensus paid; run-up proxy free; calendar from T8 | stage D |
| executive orders / proclamations | no consensus; prediction-market odds where a contract exists; run-up | stage E |
| corporate cooperation / partnerships / M&A | not yet a source — 8-K Items 1.01 / 2.01 / 7.01 / 8.01 + EX-99 via EDGAR, entering through T13's provisional pool | stage F |
| foreign central banks | run-up; same-day 2-year change in that currency | stage G |

Rule for all: the surprise uses only data available before the session's close — never the
reaction it is meant to explain.

## 5. Amendments

| date | change | reason |
|---|---|---|
| — | — | — |
