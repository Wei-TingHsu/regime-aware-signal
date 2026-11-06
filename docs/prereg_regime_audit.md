# Pre-registration — the regime audit and the day-type layer (TRACK §3.41)

*Registered 2026-11-06, before any run. Origin: the founder, 6 Nov — "is the engine with only four regimes capable of detecting those
situations in advance? if long yields rise while short yields fall and gold rises on the same day, does the engine detect it? does the
engine update itself to five regimes when required?"*

## 1. What the engine is (stated so the audit measures the right thing)

Eight FRED series — DGS10, DGS2, T10Y2Y, DFII10, EFFR, M2SL, VIXCLS, DTWEXBGS — standardised, three principal components, a four-state Gaussian
mixture refit on an expanding window every 20 sessions; the label switches when the posterior exceeds 0.8 for three sessions. It classifies
**levels** (where the dials sit), not **moves** (what changed today); it persists ~52 sessions; k = 4 was chosen on stability and persistence,
not on prediction. The product uses the label as a *filter* for the precedent pool, not as a forecast.

## 2. The audit (`src/regime_describe.py`)

| part | question | statistic | prior (Claude, counted if wrong) |
|---|---|---|---|
| **R1 describe** | what are the four regimes? | per regime: sessions, mean standardised level of each of the eight dials, annualised return and volatility of SPY, TLT, GLD, UUP, USO inside it | **#107a:** they read as roughly low-rates/calm, low-rates/stressed, rising-rates/strong-dollar, high-rates/inverted-curve |
| **R2 lag** | how late does the live labeller confirm a change? | for every change in the hindsight (full-sample) labels, sessions until the expanding labeller agrees; median, 75th percentile; share of hindsight changes never confirmed | **#107b:** median 15–30 sessions on runs of ~52 — a rear-view mirror by construction |
| **R3 conditioning** | do the labels sharpen the confirmed relationships? | by regime: the Fed-day reaction (β per σ, t), the factor model's in-sample R², the report's call hit-rate vs its block-permutation null; regime × relationship interaction with label permutation (blocks of 20 sessions) | **#107c:** no relationship differs by regime at p < 0.05 |
| **R4 k by time** | was four ever not the best count? | at each year-end from 2010, refit k = 3…8 on data to date; seed stability (adjusted Rand across 5 seeds), median run length, silhouette; the winning k per year | **#107d:** four wins or ties in every year; six or more never wins on stability |

Amendment rule: a switch of k is a founder decision taken on R4's table, never automatic — it relabels history and the precedent pools are keyed
by label.

## 3. The day-type layer (`src/daytype.py`) — the founder's example made testable

Each session is typed by the signs of five same-day moves: the 2-year yield, the 10-year yield, gold, the S&P, the dollar → 32 patterns
(2-yr down + 10-yr up = *bear steepening with a front-end rally*, the founder's case). Moves inside ±0.25 of the series' trailing 60-session
standard deviation count as flat (so small noise days do not type).

| test | question | statistic / null | prior |
|---|---|---|---|
| **Y1 counts** | how often does each pattern occur; the founder's pattern (2y ↓, 10y ↑, gold ↑) in particular | counts, by era | **#108a:** the founder's pattern 100–250 sessions since 2006, more frequent in 2022–26 |
| **Y2 turning points** | do day-types cluster in the 60 sessions before a regime change? | each pattern's frequency in pre-change windows vs elsewhere; null = the change dates shifted at random (500 draws); family null over the 32 patterns | **#108b:** no pattern's excess survives the family null |
| **Y3 forward** | does a day-type predict the next 5 / 10 / 20 sessions? | for each pattern with ≥ 30 occurrences and each asset (SPY, TLT, GLD, UUP, USO; a high-leverage equity proxy if one exists in the panel), net Sharpe of the forward path; best-of-search null over patterns × horizons × assets (asset returns time-shifted) | **#108c:** no survivor; the founder's pattern inside the null for gold and the S&P |
| **Y4 as a conditioner** | does the day-type add to the regime label? | the precedent engine's hit-rate on days of each type vs its null (from the backfill CSV: `regime`, `date`) | **#108d:** no type beats its null |

A survivor in Y3 is logged forward as a rule in words (prereg_deeper_signals §4); a PASS in Y2 is the amendment case for a *fast layer beside the
slow one* — never a fifth cluster.


## 3b. Fast-state discovery and the honest k comparison (founder, 6 Nov evening: "a full discovery, not one pattern")

**R6b** (`src/regime_k.py compare`): k = 3…6 through the engine's own `regime_labels_expanding` (refit every 20 sessions, first 504 unlabelled,
canonical PC1 order, confirmed labels) — the same three jobs as R6, without the full-sample look-ahead. The count is chosen on this table by dated
amendment. **R2** (`regime_k lag`): one full-sample mixture (hindsight) vs the live expanding labels, matched by canonical label.

**Fast states** (`src/faststate.py`): the slow regimes classify LEVELS; the fast states classify the day's MOVES — standardised daily changes of the
eight dials and the five assets (13 inputs, trailing-504 standardisation) → PCA(3) → mixture k ∈ {3, 4, 5, 6, 8}, expanding refit, canonical order.
Tests per k: **F1** forward 5/10/20-session returns per state × asset × direction, best-of-search null (returns time-shifted); **F2** state frequency in
the 60 sessions before a slow-regime change vs elsewhere, change dates shifted at random; **F3** Fed-day reaction by fast state (interaction p);
**F4** the environment → favoured-asset map's stability (first vs second half of each state's days) against block-permuted labels.

**Priors (Claude, counted if wrong).** **#111 R6b:** on expanding labels k = 6 loses its full-sample lead — Fed-day p 0.02–0.10 for k = 5 and 6, no k
reaches asset-map stability p < 0.05; k = 4 is still last on the factor spread. **#112 R2:** median lag 20–40 sessions; live and hindsight labels agree on
70–85% of sessions. **#113 F1:** no survivor at any k — a day's move pattern does not forecast the next 5–20 sessions. **#114 F2:** no fast state is
over-represented before slow-regime changes beyond the null. **#115 F3:** the Fed-day interaction by fast state is inside the null at every k (the fast
state on the statement day is mostly the statement's own move). **#116 F4:** stability below +0.3 at every k, p > 0.1. In words: fast states will read as
"risk-on day / risk-off day / rates-up day / flat day" and will describe the day well and the next days not at all.

## 4. Results

| date | part | result | prior |
|---|---|---|---|
| 2026-11-06 | F2b registered (before running) | lead time of the abnormal-day signal: for each live slow-regime change, the share of calm-type days in rolling 20-session windows from −120 to +20 sessions; the first window in which the share falls below its unconditional 10th percentile = the lead. Prior **#122:** median lead 10–30 sessions before the live label change (which itself confirms ~6 sessions after hindsight), so the signal arrives inside the season's last month, not before it; the event-rate rise is driven by the big-move days that cause the level shift. | — |
| 2026-11-06 | R6b k by usefulness (expanding refit, confirmed) | k=3: run 53, Fed p 0.938, R² spread 0.05, map +0.50 (p 0.14); **k=4: run 44, Fed p 0.008, spread 0.12, map +0.30 (p 0.20)**; k=5: run 43, p 0.442, spread 0.26, map −0.14; k=6: run 26, p 0.014, spread 0.25, map −0.15. Four wins the Fed-day job, six the factor spread, three the map; no map stability reaches p < 0.05. **Decision: keep k = 4**; a six-state fit may serve as an attribution lens. docs/regime_kcompare_expanding.md | **#111** half right (six lost its lead; four is not last on spread) |
| 2026-11-06 | R2 lag | live vs hindsight agree on 60% of sessions; 11 hindsight changes, 41 live; matched changes confirm a median 6 sessions late, 64% never match within the window — the two fits see different regimes, so the lag is weakly measured. | **#112** wrong on agreement (said 70–85%) |
| 2026-11-06 | Fast states F1–F4 (k 3/4/5/6/8, 13 move inputs, expanding) | median run 1 session at every k (day-types). F1 forward: no survivor except k=6 state 0 → SPY 5 sessions (1.46 vs 1.41, p 0.027 — one of five k's, not a survivor). F3 Fed-day by fast state: p 0.39–0.84, null. F4 within-state asset ranking stable at k=8 (+0.55, p 0.000) — contemporaneous, descriptive. **F2: the calm day-type is under-represented in the 60 sessions before a slow-regime change** (k=3 −17.8 pts, p 0.000; k=5 −18.1, p 0.000; k=4 −13.3, p 0.023) — runs of abnormal days precede label changes; lead time to be measured (F2b). docs/faststate_*.md | #113 right (no survivor), #114 **wrong** (a state is under-represented beyond the null), #115 right, #116 wrong at k=8 |
| 2026-11-06 | R5 asset map (k = 4, confirmed) | ranking stability first vs second half **+0.25**, null q95 +0.42, p 0.193 → the favoured-asset map does not reliably repeat within a regime; a description, not yet an input. docs/regime_assets.md | **#109 right** (said +0.3…+0.5, p 0.05–0.20) |
| 2026-11-06 | R6 k by usefulness (full-sample refits, confirmed) | k=3: run 32, Fed-day p 0.114, R² spread 0.11, map stability +0.50 (p 0.067); **k=4: run 254, p 0.098, spread 0.05, stability +0.40 (p 0.073)**; k=5: run 112, p 0.026, spread 0.07, stability +0.28 (p 0.173); **k=6: run 60, p 0.006, spread 0.20, stability +0.35 (p 0.087)**. Four wins on none of the three jobs; six wins two. Caveat: full-sample fits carry look-ahead; the decision waits for the same table on expanding labels (R6b, registered here). docs/regime_kcompare.md | **#110 wrong** (k=5 does not beat 4 on the map; k=3 does not lose everything) |
| 2026-11-06 | R1/R3 re-run on CONFIRMED labels | median runs 107 / 12 / 10 / 314 sessions — regimes 0 and 3 are seasons, 1 and 2 episodes. **Fed-day β per σ by regime −0.33 / −0.85 / −0.41 / −0.80, interaction p 0.005**: gold's reaction to a rate surprise is ~2.5× larger in the stimulus (1) and high-rates (3) regimes — the first regime-conditioned result to clear its bar; the page's Fed-day line should quote the regime's β. Factor R² 0.18 / 0.25 / 0.31 / 0.18, p 0.060 (borderline). Calls p 0.882 (no). **R5 and R6 registered** (this row, before running): R5 = per-regime asset Sharpe table with first-half/second-half ranking stability vs block-permuted labels (prior **#109**: stability +0.3 to +0.5, p 0.05–0.20 — the map is half a story); R6 = k 3…6 refit on the same panel, compared on Fed-day interaction p, factor-R² spread and asset-map stability (prior **#110**: k = 5 beats 4 on the asset map and ties on Fed days; k = 3 loses on everything; no k reaches stability p < 0.05). | **#107c re-judged: wrong** (two relationships differ on confirmed labels) |
| 2026-11-06 | R1 describe (raw expanding labels) | 0 (45%): low rates, steep curve, weak dollar; 1 (21%): low rates, M2 growth +0.8 sd; 2 (20%): 2-yr +0.6, curve −1.0 (inverted), dollar +0.8, M2 −0.8; 3 (13%): 10-yr +1.2, 2-yr +1.2, real +1.1, EFFR +1.2, dollar +1.2. Median raw run 13 / 2 / 3 / 2 sessions — the raw label flickers; the ~52-session persistence on record is the confirmed label's. Re-run on confirmed labels follows. docs/regime_describe.md | #107a roughly right (easy-money / stimulus / tightening-inverted / high-rates) |
| 2026-11-06 | R2 lag | not measured: the engine exposes no full-sample label function under the names tried; 91 live changes. | #107b not judged |
| 2026-11-06 | R3 conditioning | Fed-day β per σ by regime −0.40 / −0.55 / −0.36 / −0.80, interaction p **0.242** (no); factor R² for gold 0.18 / 0.27 / **0.33** / 0.17, spread vs block-permuted labels p **0.023** (yes — the factors explain gold best in the tightening regime); call hit-rate 56.7 / 54.8 / 55.5 / 54.3%, p 0.882 (no). docs/regime_conditioning.md | **#107c wrong** (one relationship differs) |
| 2026-11-06 | R4 k by time | four wins only in 2017; three or five win 13 of 17 years; five every year since 2021; every winner since 2014 has a median run of 2–8 sessions. docs/regime_kbytime.md | **#107d wrong** |
| 2026-11-06 | Y1–Y4 day-types | founder's pattern 67 sessions (flat threshold 0.25 sd); Y2 no clustering before regime changes (best `00000` −1.9 pts, p_family 0.438); Y3 no survivor (best all-flat day → SPY +5.28 vs q95 6.17, p_family 0.100); Y4 0 of 7 types beat their null. docs/daytype_*.md | #108a wrong (count), #108b–d right |
