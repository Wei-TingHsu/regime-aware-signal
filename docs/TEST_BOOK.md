# Test book — every test, how it was done, what it found, and who can use it

*Started 11 Nov 2026 at the founder's request. Purpose: one document a quant specialist can read alone and rebuild any test from — the question,
the data, the method step by step, the pass rule, the result, and how the finding can or cannot be used. `RESULTS_COMPENDIUM.md` stays as the short
summary; this is the long form. Built in parts: Part A (rules and shared method), Part B (the index: every test with its use category), Part C (full
rebuild cards — the N1 family is complete; the other families are added part by part and are marked "card pending" in the index until then).*

---

## Part A — rules and shared method

### A1. The two ways a finding can be used (founder's rule, 11 Nov 2026; standing)

| category | meaning | what it needs to show |
|---|---|---|
| **QUANT** | usable by a rule-based strategy that holds from one session to several weeks | the effect is still there AFTER the information is known at a daily close, over the next 1 … 20+ sessions; passes its registered test after costs |
| **SUBJECTIVE (intraday)** | usable by the founder's own judgement trading inside the day | the effect happens on the SAME day as the information and nothing is left on the following days. Grade **B** = seen at daily closes only (the day's close-to-close move goes with the information; whether it can be captured after the release is not yet tested). Grade **A** = confirmed with intraday prices from the release time to the close |
| **CONTEXT** | not a direction to trade; tells how to size, hedge or explain | a stable fact (for example a hedge ratio, or which regime a relationship holds in) |
| **NEITHER** | no use found | null on the registered test at every span length tried |

Rule of reading: **"nothing is left after day 0" ends a finding as QUANT but not as SUBJECTIVE.** A same-day link is recorded as SUBJECTIVE grade B
and goes on the list for an intraday test. A grade-B finding is a same-day association: the information and the price move happened on the same
day; it does not yet prove that someone who reads the information at its release can still trade the move.

### A2. The other standing rules

- **Registration before running.** Every test is written down first (question, data, statistic, pass rule, Claude's numbered prediction) in a
  `docs/prereg_*.md` file; a wrong prediction is counted. Results are appended as dated rows; nothing is rerun silently.
- **Grid by default (28 Oct).** Every fixed number in a test (threshold, window, horizon, cutoff) is a grid axis from the first run. The best cell
  is judged against the best cell the same grid finds on shuffled data (`p_family`), not on its own p.
- **Sub-period rule (28 Oct).** Every result is also shown by era: 2004–08, 2009–14, 2015–19, 2020–21, 2022–26.
- **Short-window rule (11 Nov).** News arrives every day; the longer the span, the more unrelated news is mixed in. Every news-reaction test runs at
  several span lengths, shortest first (release day, +1, +1…+2, +1…+3, then 5, 10, 20). No conclusion from one span length alone.
- **Sources.** Primary sources only (agency archives, filings, GDELT raw files, the project's corpus). No Wikipedia or similar.
- **Where things run.** Every run happens in the founder's terminal and is committed and pushed, nulls included.

### A3. Shared pass standards

| name | rule |
|---|---|
| H-table standard | a cell passes if n ≥ 30, the gap to the base rate is ≥ 10 percentage points, and the random-date p < 0.05 |
| Family null (`p_family`) | share of shuffled-data runs whose BEST cell is at least as strong as the real best cell; pass below 0.05 (or below 0.05 ÷ number of groups when several groups are tested, e.g. 0.0125 for four) |
| Split rule C | first half and second half must agree in sign (S1) and differ by no more than 3× in size (S2) |
| Net Sharpe | mean ÷ standard deviation of per-trade returns after 10 basis points cost, annualised by the holding span |
| Forward log | a rule that passes in history is logged live with fixed entry and exit before it is called a signal |

### A4. Shared data and code

| item | where | note |
|---|---|---|
| Daily returns (log), ETFs and indices | `processed/asset_returns.parquet` | SPY, TLT, GLD, UUP, USO, SOXX, … ; SOX index is stood in by SOXX; QQQ is not in the panel |
| Macro dials | `processed/macro_panel.parquet` | DGS10, DGS2, T10Y2Y, DFII10, EFFR, M2SL, VIXCLS, DTWEXBGS (FRED) |
| Regime labels | `analog_event.regime_labels_expanding` → confirmed by `exposure_dial.confirmed_labels`; `processed/regime_labels_by_k.parquet` | 8 dials → 3 principal components → mixture of k = 4 states, refit every 20 sessions on past data only, first 504 sessions unlabelled; k = 6 kept as the attribution lens |
| Grid engine | `src/sweep.py` (`grid`, `run`, `write_md`) | `run(cells, stat, data, null_gen, n_null)` returns the surface, best cell, `p_family`, the null's 95th percentile and survivors |
| Document reads | `data_provenance/…` JSON files, one per document per prompt version | write-once caches; a new prompt version gets a new cache and is never pooled with an old one; model `claude-sonnet-5` |
| Environment | Python 3.11 virtual environment in the repo (`source .venv/bin/activate`); run modules as `python -m src.<module> <command>` | LLM reads need `ANTHROPIC_API_KEY`; BLS fetches need `BLS_CONTACT` |

---

## Part B — the index: every test and its use category

"Day 0 checked?" answers the founder's two rules together: was the same-day effect measured separately from the following days? "no" rows form the
**horizon audit list** (TRACK §3.50) — they are rerun at day 0, +1, +1…+2, +1…+3 before their category is final. Detail lives in the named
registration file and result files until the test's rebuild card is written in Part C.

### B1. Gold and the Fed

| id | claim tested | result | category | day 0 checked? | registration · results |
|---|---|---|---|---|---|
| T9b-L1 | gold reacts to the rate SURPRISE on FOMC statement days (2-year yield change that day) | yes: −0.11% per basis point, p 0.039; 131 statement days 2011–26 | **SUBJECTIVE B** | it IS a day-0 test | prereg_surprise · surprise_stageA, chair_power |
| T9b-L3 | same with the published 30-minute surprise series | not shown, p 0.49 | NEITHER | intraday series | prereg_surprise |
| T14-A | the reaction continues from 2 pm to the close | null, low power (daily data) | NEITHER (open: live 2 pm reader logs each meeting → would make T9b grade A) | intraday pending | prereg_event_time · event_time_phaseA |
| T-K1 / K1′ | Fed chairs differ in gold's reaction per basis point / per unit of yield volatility | yes p 0.016 / no p 0.118 | CONTEXT (a new chair inherits the pooled reaction) | day-0 test | prereg_liquidity_and_chair · chair_power |
| T9b-era | the reaction is larger in high-volatility eras | yes: pandemic era 2.7×; p 0.026 | **SUBJECTIVE B** (condition: yields volatile) | day-0 test | prereg_subperiod_audit · era_fomc |
| D4 | Fed-day gold move from the surprise plus the statement's wording | surprise alone, in the high-volatility state: Sharpe 1.34 vs noise 0.89, p_family 0.000; wording adds nothing | **SUBJECTIVE B** | day-0 test | prereg_deeper_signals · deeper_fomc |
| R3 | the Fed-day reaction differs by regime | yes: −0.33 / −0.85 / −0.41 / −0.80 per σ in regimes 0–3; interaction p 0.005 (expanding labels 0.008) | **SUBJECTIVE B** (condition: regimes 1 and 3 react ~2.5× more) | day-0 test | prereg_regime_audit · regime_conditioning, regime_kcompare_expanding |
| T-K3 | the new chair's statement style differs from the last chair's | almost: p 0.042 at 3 statements, 0.061 at 4 | NEITHER (judged again at 5) | n.a. | prereg_liquidity_and_chair · chair_style |
| T-K2σ | how much weight the new chair's own days get | 20%; pooled reaction dominates | CONTEXT | n.a. | prereg_liquidity_and_chair |
| row 14 | FOMC → gold over following sessions (retired cell) | split rule FAIL (halves differ 4.6×) | NEITHER | **no** | PROJECT_MASTER §8 · fomc_drift, fomc_gld_split_cost |
| — | FOMC → gold by regime, forward test | pending since Sep 2026 | — | — | fomc_gld_by_regime, fomc_gld_forward |

### B2. Gold, liquidity, stress and equities

| id | claim tested | result | category | day 0 checked? | registration · results |
|---|---|---|---|---|---|
| P1 | gold stops moving with equities in liquidity stress | null, p 0.44; by era the sign flips, p_family 0.35 | NEITHER | n.a. (correlation over 20 sessions) | prereg_subperiod_audit · era_liquidity_p1 |
| D3 | last month's gold–equity correlation predicts next month's | **yes**: removes 26% of the forecast error, p_family 0.000, tested on the last 40% of the sample | **QUANT — a risk forecast (hedge sizing), not a direction** | n.a. | prereg_deeper_signals · deeper_corr |
| T-L | liquidity (Fed assets − Treasury account − reverse repo) → gold, weekly | faint and unstable: t 1.96; on in 2015–19 and 2022–26 only | NEITHER | weekly data | prereg_liquidity_and_chair · liquidity_link_GLD, era_liquidity_liquidity |
| D2 / D2c | trading gold on weekly / daily liquidity when the link is "on" | null: p_family 0.285 / 0.235 | NEITHER | **no** (daily version) | prereg_deeper_signals · deeper_liquidity, deeper2_daily |
| D2b | the liquidity link by regime | lives in regime 2 (t 3.0) but regimes do not differ, p 0.385 | NEITHER | n.a. | deeper2_regimes |
| T-L5b | gold is sold in the sessions after an equity sell-off | null: 45% vs 45% base; grid best p_family 0.87 (147 cells) | NEITHER | **no** | prereg_liquidity_and_chair · era_liquidity_selloff_sold / _bought |
| D1 | gold is bought after a 6% S&P drawdown | with the event day included p 0.045–0.050; **without it 0.140** → the effect, if any, is on the event day itself | NEITHER as quant; **SUBJECTIVE B candidate** (same-day; weak) | partly — the two runs differ only by the event day | prereg_deeper_signals · deeper_selloff_long / _short |
| D1b | after a sudden one-day sell-off (1.5–4%), gold or the S&P continues or reverses | null ×4, p_family 0.24–0.92 | NEITHER | **no** | prereg_deeper_signals §2b · deeper2_sudden_* |

### B3. Gold and the named factors

| id | claim tested | result | category | day 0 checked? | registration · results |
|---|---|---|---|---|---|
| T-A | standard factors explain gold's daily moves out of sample | partly: median 17.7% of variance explained (bar 20%, FAIL); best window 22% | CONTEXT (attribution: "why it moved") | same-day by construction | prereg_factor_attribution · factor_attribution_tests, era_factors_GLD_full |
| T-B | the factors' signs are stable through time | dollar 100% and oil 90% of windows; rates 63–66%; VIX 59% | CONTEXT (trust the dollar and oil hedge ratios; not the rates one) | same-day | prereg_factor_attribution |
| — | the 2026 gold fall explained by the factors | mostly not: 29% with 2009–21 sensitivities, 11–13% with recent ones | CONTEXT | same-day | factor_attribution_GLD_* |
| D8 | combinations of factors forecast gold | null: p_family 0.120 (299 combinations; 1, 5, 20 days) | NEITHER | n.a. (forecast) | prereg_deeper_signals §2b · deeper2_combo |
| T-H | the unexplained part of a move continues or reverses | null on GLD, SLV, USO, SPY, NVDA (p 0.19–0.82); null in every era (p_family 0.93) | NEITHER | **no** (5–60 sessions) | prereg_factor_attribution · residual_momentum_*, era_resid_GLD |
| T-F′, G, I′, J | window and leg rules explain episodes | yes, as explanation: 53–79% vs 5–11% on shifted factors | CONTEXT | n.a. | prereg_factor_attribution · segmenter_test_GLD |
| A3a / D5 | gold after oil shocks | null: p_family 0.605 (116–152 shocks) | NEITHER | **no** | prereg_blindspot, prereg_deeper_signals · deeper_oil, era_events_oil |
| D5b / D5c | oil → rates → gold chain | link 1 absent; link 3 only in the same window; with tradeable timing null (p_family 0.905) | NEITHER (link 3 is a same-period association) | same-window part seen | deeper2_oilchain, deeper2_oilchain_timed |
| D6 | extreme futures positioning → gold, silver, oil | null: p_family 0.730 | NEITHER | weekly data | deeper_cot |

### B4. The product's own document-driven calls

| id | claim tested | result | category | day 0 checked? | registration · results |
|---|---|---|---|---|---|
| rows 24/27/33 | the report's calls beat drift | no: 59.4% vs 59.1% bar (p 0.0497, inconclusive); at 2 sessions 54.9% vs 57.5% (p 0.40); Sharpe after costs 0.07 | NEITHER | **no** (2 and more sessions) | prereg_report_scoreboard · report_scoreboard_backfill_* |
| A | calls by era / tier / source / asset | none beats its null; best cell p_family 0.957 | NEITHER | **no** | prereg_subperiod_audit · era_scoreboard_* |
| E1–E4 | asymmetry levers | all FAIL vs the incumbent | NEITHER | n.a. | prereg_asymmetry_levers |
| D7 | a learner selects the better calls | null: p_family 0.770 | NEITHER | **no** | deeper_calls |
| — | more documents (political backlog) | neither helps nor hurts: +0.7 points, interval −0.5 … +2.0 | NEITHER (coverage) | n.a. | prereg_political_backfill · source_compare_* |
| H0–H7 | history tables on document classes | 0 of 72 cells pass at 5 and 20 sessions; none by era | NEITHER | **no** | prereg_history_tables · history_H*, era_htables |
| T1 | exposure dial: volatility targeting and regime tilt | vol-targeting helps 1 of 5 assets overall; by era +18.6 points for the S&P in 2004–08; regime tilt adds nothing | CONTEXT (a risk tool for crisis eras) | n.a. | prereg_exposure_dial · exposure_dial_testA, era_t1 |
| — | model 4 long top-5, kernel family, rotation, chain lead–lag, GDELT profile, inverse oil rule | null / FAIL | NEITHER | mixed | prereg_cross_asset_rotation, prereg_sector_rotation, prereg_recency_kernel, prereg_analog_event |
| — | live ledgers: 3 models, 08:30 data-release reader, 2 pm Fed reader | forward, pending | — (the two readers are the route to grade A) | intraday by design | forward_scoreboard |

### B5. Regimes and day-level states

| id | claim tested | result | category | day 0 checked? | registration · results |
|---|---|---|---|---|---|
| R1 | what the four regimes are | 0 low rates / steep curve; 1 stimulus (money growth); 2 inverted curve, strong dollar; 3 high rates. Confirmed runs last 107 / 12 / 10 / 314 sessions | CONTEXT | n.a. | prereg_regime_audit · regime_describe |
| R2 | how late the live label confirms a change | median 6 sessions; live and hindsight labels agree on 60% of days | CONTEXT (a limit: the label is a description of the recent past) | n.a. | regime_lag |
| R5 | each regime has a stable favoured-asset ranking | no: stability +0.25, p 0.193 | NEITHER | n.a. | regime_assets |
| R6b | how many regimes | four (Fed-day job p 0.008); six kept as the attribution lens | CONTEXT (decision 6 Nov) | n.a. | regime_kcompare_expanding |
| Y1–Y4 | named day-types (e.g. 2-year down, 10-year up, gold up) predict the next sessions, cluster before regime changes, or sort the calls | no: p_family 0.100, 0.438; 0 of 7 | NEITHER | **no** (5–20 sessions) | daytype_* |
| F1 | data-formed fast states predict the next 5–20 sessions | no survivor (one cell of five fits at p 0.027) | NEITHER | **no** | faststate_tests, faststate_forward_k* |
| F2 | calm days become rarer in the 60 sessions before a regime change | **yes** at 3 and 5 states: −18 points, p 0.000 | **QUANT candidate — a warning of regime change (risk), not a direction**; lead time (F2b) not yet run | n.a. | faststate_tests |
| F3 | the Fed-day reaction differs by fast state | no, p 0.39–0.84 | NEITHER | — | faststate_tests |
| F4 | assets rank the same way within a fast state | yes at 8 states (same-day description) | CONTEXT | same-day | faststate_tests |

### B6. News-attributed large moves (N1) — full cards in Part C

| id | claim tested | result | category | day 0 checked? |
|---|---|---|---|---|
| N1-S1 | the cause of a ≥ 4% day can be read from GDELT | about half the days show no identifiable cause; GDELT misses company news | NEITHER (instrument limit) | n.a. |
| N1-S3 | prices reverse after a ≥ 4% day | after falls no (57–60% vs 55–59% normal); S&P the session after a ≥ 4% RISE falls 67% vs 45% (n 42, p 0.006), one cell of twelve | **QUANT candidate N1-a** (one-session hold; forward log, not yet a signal) | yes (1, 3, 5 sessions) |
| N1-S4 | a learner on cause, size, trend, VIX beats "buy after a fall" | no | NEITHER | yes |
| N1-v3a grid | an official document that does not support the move raises how OFTEN prices reverse | no, at any cutoff, window, span or document family | NEITHER | spans 1–10 |
| N1-v3c | … raises how BIG the reversal is (measured from the event day) | weak: +0.12, p 0.02, misses the 0.0125 bar | superseded by v3d | — |
| **N1-v3d** | the link is on the document's release day and fades after | **yes after semiconductor falls**: day 0 +0.169 (p 0.004) all documents, +0.382 (p 0.001) Fed documents; days +1…+5 zero (p 0.59); same at spans 1, 2, 3 | **SUBJECTIVE B** — not QUANT | yes — this is the day-0 test |

### B7. Horizon audit results (11 Nov 2026) — these replace the 'day 0 checked? no' entries above

Method and label rule: `docs/prereg_horizon_audit.md`; code `src/horizon_audit.py`; command `python -m src.horizon_audit all`; per-audit tables `docs/horizon_audit_<name>.md`.

| audit (index rows it updates) | day 0 | days +1 … +5 | category after the audit |
|---|---|---|---|
| `fomc` (row 14, T9b) | all statement days → gold, day 0: +76 bp, t +7.6, n 114, hit 80%; family p 0.000 | larger-than-median rate surprise → gold, day +1: +38 bp, t +1.9, n 66, hit 53%; family p 0.403 | **SUBJECTIVE grade B candidate** — Confirms T9b on the audit's own measure: on statement days gold moves 76 bp in the direction the rate surprise predicts, 80% of the time, in every era; nothing reliable is left on the days after (large surprises: +38 bp on day +1, p 0.40). SUBJECTIVE grade B; not QUANT. |
| `calls` (rows 24/27/33, A, D7) | calls on SPY, day 0: +6 bp, t +2.1, n 722, hit 53%; family p 0.245 | all calls, pooled, days +1..+3: +16 bp, t +3.6, n 1646, hit 57%; family p 0.034 | **QUANT candidate** — Label by the registered rule. Read with care: the calls are mostly 'up' calls on assets that drift up; the shift null keeps that drift and the result clears it narrowly (p 0.034, best of 3 span cells × variants). The same calls at 2 sessions did not beat drift in the scoreboard (p 0.40) and earned a Sharpe of 0.07 after costs. Day 0 itself shows nothing (p 0.245): the documents' direction does NOT go with the same-day move. The day −1 check fails for tier 2 (−25 bp, p 0.007): those calls point against the previous day's move, so part of what the call 'predicts' may be a bounce from the day before. Next: a registered, costed rule at 1 / 2 / 3 sessions with the previous day's move controlled. |
| `liquidity` (D2c) | reverse-repo balance change beyond 1.5 sd → gold, day 0: +10 bp, t +1.6, n 273, hit 52%; family p 0.231 | reverse-repo balance change beyond 1.5 sd → gold, day +1: +7 bp, t +1.1, n 273, hit 51%; family p 0.838 | **NEITHER** — Nothing on the day, before or after. |
| `selloff` (D1, T-L5b) | S&P 20-session return crosses -4% → gold, day 0: -27 bp, t -1.2, n 50, hit 50%; family p 0.704 | S&P 10-session return crosses -4% → S&P itself, days +1..+5: +128 bp, t +3.1, n 67, hit 67%; family p 0.160 | **NEITHER** — Gold shows no reliable move on the day a drawdown completes or after. The S&P itself gains 128 bp over the five sessions after a −4% ten-session fall (t 3.1) but that does not clear the family null (p 0.16) and reverses sign in 2022–26. |
| `sudden` (D1b) | S&P falls ≥ 4.0% in one session → gold, day 0: +51 bp, t +1.2, n 43, hit 60%; family p 0.613 | S&P falls ≥ 1.5% in one session → S&P itself, days +1..+3: +35 bp, t +1.9, n 362, hit 59%; family p 0.876 | **NEITHER** — On days the S&P falls ≥ 4% gold is up 51 bp on average but not reliably (t 1.2): gold is not a dependable same-day hedge on crash days. Nothing after. |
| `oil` (A3a, D5) | all oil shocks → gold, day 0: +31 bp, t +3.1, n 202, hit 60%; family p 0.009 | all oil shocks → gold, days +1..+5: +23 bp, t +1.3, n 202, hit 55%; family p 0.808 | **CONTEXT (same-day co-movement)** — Gold rises about 31 bp on the day an oil shock completes — two prices moving together (stronger before 2015); nothing after. CONTEXT. |
| `htables` (H0–H7) | H1 → UUP, day 0: -42 bp, t -8.7, n 115, hit 17%; family p 0.000 | H4dn → USO, day +1: -141 bp, t -3.1, n 30, hit 27%; family p 0.122 | **CONTEXT (same-day co-movement)** — The day-0 passes are market mechanics (on Fed decision days the dollar moves with the 2-year yield, −42 bp on the signed measure, t −8.7). Nothing reliable after (best: oil −141 bp the day after a 2-year yield drop, n 30, family p 0.12). CONTEXT. |
| `states` (F1, Y3) | not measured | fast state k3:1 → SPY, days +1..+5: +31 bp, t +7.9, n 2411, hit 63%; family p 0.002 | **QUANT candidate** — Label by the registered rule. Read with care: the state covers about half of all days (n 2,411) and the S&P's ordinary five-session gain is roughly +20 bp; the excess is about +10 bp per five sessions before costs. The state flips almost daily (median run 1 session), so trading it means paying costs constantly; the costed version of this test at five sessions (F1, net Sharpe) found no survivor at three states (p 0.36). What the audit adds: calm-type days are followed by slightly better S&P returns than other days, in every era — a sizing tilt at most. Next: a registered, costed rule at 1 / 2 / 3 sessions. |
| `resid` (T-H) | not measured | SPY: unexplained move over 20 session(s) beyond 1.5 sd, days +1..+5: -55 bp, t -4.4, n 731, hit 45%; family p 0.106 | **NEITHER** — After a large unexplained 20-session move the S&P gives back about 55 bp over the next five sessions, with the same sign in every era (t −4.4), but the family null is not cleared (p 0.106). Closest miss of the audit; NEITHER as registered. |

After the audit the lists read — **QUANT:** gold–equity correlation persistence (confirmed, a risk forecast); candidates: calm days rarer before regime changes; S&P the session after a ≥ 4% rise; the report's calls over the next 1–3 sessions (narrow, drift-sensitive); calm-type fast state → S&P next sessions (small, cost-sensitive). **SUBJECTIVE grade B:** gold on Fed statement days by the rate surprise (re-confirmed: 76 bp, 80% of days); Fed documents after ≥ 4% semiconductor falls. **Dropped from SUBJECTIVE:** gold on the day an S&P drawdown completes (no day-0 move found). **CONTEXT added:** gold rises with oil on oil-shock days; the dollar moves with the 2-year yield on Fed days. Everything else audited: NEITHER.

---

## Part C — rebuild cards

### C-N1. News-attributed large moves and the documents that follow them

**Question (founder, 6 Nov 2026).** Every sudden fall or rise is the result of news that day. In the next sessions, does an official statistic or
statement give a reason for the price to go back — judged by what the document is made of, not only its headline?

**Registration:** `docs/prereg_news_events.md` (§1–§5; priors #117–#131). **Code:** `src/news_events.py` (stage 1), `src/news_events2.py` (GDELT
cause read, tables, learner), `src/news_events3.py` (official documents: fetch, read, grid, size, joint, decay, decayk).
**Cost:** about US$19 of LLM reads in total.

#### Step 1 — the event days
- Data: `processed/asset_returns.parquet`, columns SOXX (stand-in for the SOX semiconductor index, from 2001) and SPY. QQQ is not in the panel.
- Rule: an event is a session whose close-to-close move is ≥ 4% up or down (log return converted to a simple return).
- Output: `processed/news_events.csv` — 476 sessions (SOX 231 falls and 217 rises; S&P 49 falls and 42 rises).
- Command: `python -m src.news_events events`

#### Step 2 — the cause of each event day, from GDELT (v1 and v2)
- Data: GDELT 1.0 daily event files (`data.gdeltproject.org/events/YYYYMMDD.export.CSV.zip`; monthly files for 2006–13), stored write-once under
  `data_provenance/gdelt_days/raw/`. 246 event days from 2009 have a file; 2022-11-10 is missing at the source.
- Digest v1: the 50 records with the most mentions (actors, event type, tone, source-URL words). Digest v2 adds up to 40 records whose URL words
  contain a market, Fed, earnings, bank, tariff, oil or pandemic term.
- Read: one LLM call per day; fixed instructions; the model must choose one class from {macro release, central bank, earnings/guidance,
  geopolitics, election/regulation, credit/liquidity, health, no identifiable news — positioning}, give a confidence 0–1, one supporting line, and
  the story the market would be trading. It is told to use only the digest. Prompt versions `n1-cause-v1-2026-11-06`, `n1-cause-v2-2026-11-07`;
  caches `data_provenance/news_reads/`.
- Results: "no identifiable news" 68% (v1), 49% (v2). The v2 keyword match is noisy (it matches inside words) and GDELT misses company results;
  on 5 Nov 2026 it found the election/AI-regulation story but not Qualcomm's results. Conclusion: GDELT is a weak same-day source for market causes.
- Commands: `python -m src.news_events fetch`, `digest [--v2]`, `cost [--v2]`; `python -m src.news_events2 read [--v2]`

#### Step 3 — do prices reverse after the event (S3 tables)
- Statistic: reversal rate = share of events where the next h sessions' return (h = 1, 3, 5; starting the session after the event) has the opposite
  sign to the event. Base rate = how often any h sessions have that sign. H-table standard.
- Result: 12 cells (2 indices × 2 directions × 3 spans); one passes — S&P the session after a ≥ 4% rise falls 67% vs 45% (n 42, p 0.006). After
  semiconductor falls the one-session rate is 60% vs 53% (gap 7, below the 10-point bar).
- Command: `python -m src.news_events2 tables [--v2]` → `docs/news_events_tables*.md`

#### Step 4 — a learner (S4)
- Method: walk-forward ridge regression; inputs = cause class, move size and sign, read confidence, release scores, prior 20-session trend, VIX;
  target = the next 1, 3, 5 sessions' return; trade the predicted sign, 10 bp cost; grid over training length {100, 200, 400} and penalty
  {1, 10, 100}; null = targets shuffled, 200 draws; benchmark = "buy the session after a ≥ 4% fall".
- Result: best 2.12 (v1) and 1.42 (v2) at one session against 1.87 for the plain rule; null at 3 and 5 sessions. The learner does not beat the plain rule.
- Command: `python -m src.news_events2 learn [--v2]`

#### Step 5 — the official documents after each event (v3a)
- Documents: BLS Employment Situation, CPI, PPI, JOLTS, Import/Export Prices (archive index pages `bls.gov/bls/news-release/<name>.htm`, about
  2008 onward); FOMC statements (project corpus); speeches by the Fed Chair and Vice Chairs (`federalreserve.gov/json/ne-speeches.json`). Kept if
  released in sessions +1 … +10 after any event. 599 documents. Stored under `data_provenance/releases/`.
- **How a document is read and scored.** The first 15,000 characters of the document go to the model with fixed instructions (`SYS_DOC` in
  `news_events3.py`). The model sees only the document and its date — no prices, and it is not told there was a crash. It returns: headline
  surprise (−1, 0, +1); up to five components that drove it; breadth 0–1; **what the document means for US stocks over the next few sessions,
  from −1 (clearly bad) to +1 (clearly good)**; what it means for interest rates; one quoted sentence as evidence. This is the model's judgement,
  not word counting. One read per document, prompt `n1-doc-v3-2026-11-11`, cache `data_provenance/releases/reads3/`.
- **The score used in the tests.** After a fall: score = the stock number (high = the document does NOT support the fall). After a rise: score =
  minus the stock number (high = the document does NOT support the rise).
- Known weak points: the model cannot see what traders expected before the release; only the first 15,000 characters are read; one read per
  document and no repeat-read check yet; the model knows market history, so hindsight in the score cannot be excluded for famous days.
- Commands: `export BLS_CONTACT=<address>`; `python -m src.news_events3 fetch`, `cost`, `read`

#### Step 6 — does such a document raise how OFTEN prices reverse (v3a grid)
- Statistic: reversal rate of events WITH a document scoring at or above the cutoff in the window, minus the rate WITHOUT, in points; each side n ≥ 20.
- Grid: cutoff 0.1 … 0.7; window +1 … {1, 2, 3, 5, 7, 10}; span 1, 3, 5, 10; document family {all, BLS, labour, prices, Fed}; per index × direction.
- Null: outcomes shuffled among events of the same index and direction, best cell of the grid, 300 draws; bar p_family < 0.0125 (four groups).
- Result: no group passes (SOX fall p 0.44, SOX rise 0.27, S&P fall 0.74; S&P rise not testable).
- Command: `python -m src.news_events3 grid`

#### Step 7 — does it raise how BIG the reversal is (v3a size, v3c joint)
- Statistic: rank correlation between the score and the reversal return (minus the event's sign × the next h sessions' return), among events with a
  document in the window. Rank correlation: rank both columns, measure how far the two rankings agree (+1 identical, 0 unrelated). p from shuffles.
- v3c: one number per group = the mean rank correlation over windows 3, 5, 10 × spans 1, 3, 5, 10; 2,000 shuffles with the same shuffle for every span.
- Result: SOX fall +0.117 (p 0.022), SOX rise +0.121 (p 0.023) — below 0.05, above the 0.0125 bar. Fed documents after SOX falls +0.224 (p 0.001) as a side cut.
- Limit: the return was measured from the event day and the documents came out inside that span, so this is a same-period link, not a forecast.
- Commands: `python -m src.news_events3 size`, `joint`

#### Step 8 — is the link on the release day, and does it fade (v3d; the founder's hypothesis)
- Re-alignment: day 0 = the session the document was released. Pairs = (event, document day) with the document day in sessions +1 … +10 after the
  event. Several documents on one day are averaged.
- Four statistics per index × direction × family: (a) **day 0** — rank correlation between the score and the release-day return; (b) **decay** —
  day 0 minus the mean of days +1 … +k; (c) **drift** — rank correlation with the cumulative return over days +1 … +k (the part someone who reads
  the document at the close of day 0 could still trade); (d) **two days before** — days −2 and −1, which a document cannot cause.
- Null: the documents' stock numbers shuffled across document days, 2,000 draws. Primary cells: SOX fall and SOX rise × all documents and Fed
  documents; bar p < 0.0125. Spans k = 5 (registered) and 1, 2, 3 (short-window rule).
- Results (k = 5; the same picture at k = 1, 2, 3):

| cell | pairs | day 0 | p | day 0 minus later days | p | days +1…+5 | p | two days before |
|---|---|---|---|---|---|---|---|---|
| SOX fall, all documents | 531 | +0.169 | 0.004 | +0.184 | 0.005 | −0.013 | 0.59 | +0.020 |
| SOX fall, Fed documents | 194 | +0.382 | 0.001 | +0.400 | 0.001 | −0.024 | 0.59 | +0.073 |
| SOX rise, all documents | 476 | +0.092 | 0.076 | +0.127 | 0.036 | −0.023 | 0.65 | +0.032 |
| SOX rise, Fed documents | 178 | +0.214 | 0.017 | +0.278 | 0.006 | −0.100 | 0.84 | +0.028 |

- In percent, Fed documents after a semiconductor fall: on the release day the index fell a further 2.93% when the document supported the fall,
  moved −0.30% in the middle group, and rose 0.83% when the document did not support the fall. Over the next five sessions the three groups
  returned +1.51% / +1.18% / +1.10% — no difference.
- **Use.** QUANT: none — nothing is left after the release day. SUBJECTIVE grade B: on the day a Fed statement or Chair / Vice Chair speech comes
  out within ten sessions of a ≥ 4% semiconductor fall, the day's move goes with the document — a further fall when the document supports the fall.
  Not yet shown: that the move can be captured after the release (needs intraday prices; planned as v3e). Cautions: the document and the price may
  both be reacting to the same conditions that day; hindsight in the reader; one read per document.
- Commands: `python -m src.news_events3 decay`, `decayk` → `docs/news_events_v3_decay*.md`

### Cards pending (written part by part from the registration files)

Part 2 — gold and the Fed (B1). Part 3 — liquidity, stress, equities (B2). Part 4 — named factors (B3). Part 5 — the product's calls, history
tables, exposure dial (B4). Part 6 — regimes and day-level states (B5). Each card will carry the same headings as C-N1: question, registration,
code, data, method step by step, pass rule, result, use (QUANT / SUBJECTIVE / CONTEXT / NEITHER), commands.
