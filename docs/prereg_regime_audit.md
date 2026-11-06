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

## 4. Results

| date | part | result | prior |
|---|---|---|---|
