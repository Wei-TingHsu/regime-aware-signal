# SPEC_GRID — the alternatives track (registered 2026-10-22, runs after the main list)

*Founder's instruction: every variable a main-track test fixed is to be swept, every value, so no possibility is missed by convention
("59 sessions, 58, 57 … not just 30, 15, 5"). This file sits beside `TRACK.md`: TRACK holds the registered tests and their verdicts;
SPEC_GRID holds, for each of them, the full set of alternatives, how many cells that is, and the one rule that keeps a sweep honest.*

## 0. Rules of the track

1. **Everything runs, everything is shown.** Each family's cells are run in full and published as a specification curve (cells sorted by
   their statistic, with the null band). No cell is hidden, dropped or re-run alone.
2. **The best cell is judged against the best cell of a shuffled sweep.** For each family the same sweep is run on resampled data
   (random event dates / permuted labels / block-shuffled returns, as the family's own test does), N_NULL times, and the *maximum* statistic
   across all cells is recorded each time. The observed best cell's p-value is its rank in that distribution (White's reality check;
   Hansen's SPA form when some cells are dominated). A 50,000-cell sweep therefore does not manufacture a winner: the bar rises with the
   number of cells tried.
3. **A survivor is promoted, not adopted.** A cell that beats the sweep-wide null is registered on TRACK as its own forward test, with a
   prior, and only enters the engine after that test — the A3b/E-lever/H-table verdicts already on record never change.
4. **Variables are registered before the sweep runs.** Ranges below are fixed when the family is first run; widening a range afterwards is a
   dated amendment and re-runs the whole family's null.
5. **Compute is budgeted per family** (N_NULL = 2,000 for the sweep, 10,000 for finalists; vectorised over horizons; nulls shared across
   cells that have the same event count), run order §5. Results: `docs/spec_grid/<family>.md`, `processed/spec_grid/<family>.json`;
   runner `src/spec_grid.py` (to build).

## 1. Variable inventory (global)

| variable | main-track value | sweep |
|---|---|---|
| horizon h | 2 (referee), 5/20 (H), 20/60/90 (A3), 60 (target) | **1, 2, 3 … 120** sessions, every value |
| event threshold | oil +8%/5 s; dollar ±2%/5 s; 2-yr ±25 bp/5 s; VIX +30% | oil 3–15% step 1; dollar 0.5–4% step 0.25; rates 5–60 bp step 5; VIX 10–80% step 5; window 1–10 sessions |
| event collapse (GAP) | 20 sessions | 0, 5, 10 … 60 |
| sample start | 1995 (A3, H), 2011 (H1), 2012 (calibration) | 1990, 1995, 2000, 2006, 2010, 2015 |
| regime definition | 4-state GMM on 8 FRED series, expanding | k = 2 … 6; every subset of the 8 series (255); price-based regimes (T12: trend × vol × curve) |
| sample-size floor | 30 events; 100 sessions; ESS ≥ 8 | **independent cases** 5 … 40; ESS 4 … 20; sessions floor replaced by cases |
| frequency gap floor / p | 10 pts, p < 0.05/6 | reported, not swept: the sweep-wide null replaces per-cell thresholds |
| conditioning features | shock-week legs (3) | legs + trailing 20/60/120-session vol, 60/120-session trend, 2s10s, real 10-yr, M2 growth, breakevens, credit spread — every subset up to size 4 (with ridge for larger) |
| kernel | Gaussian, 10-yr half-life, 0.5 regime-mismatch weight | half-life 2 … 20; mismatch 0 … 1; bandwidth 0.5 … 2 |
| targets ±X | 2.5, 5, 10, 15, 20% | 1 … 30% step 1 |
| scoring | sign hit-rate; Brier; median path | sign hit-rate, Brier, log-loss, pinball (25/50/75), MAE of median, coverage of the IQR |
| markets | SPY, TLT, GLD, UUP, USO, WTI_SPOT | + silver (SI=F), gold spot (LBMA), copper (HG=F), Brent (BZ=F), DXY (DX-Y.NYB, 1971→), HYG, TIP, EEM, BTC-USD (2014→) |
| document variables | direction floor; tiers; 5 sources; prompt v1 | floor 0.02 … 0.30; tier ≥ 1/2/3; each source in/out (2^5); prompt versions as a dated dimension |

## 2. Per-test grids (side by side with TRACK)

| § | main-track test (TRACK) | fixed there | sweep cells (approx.) | statistic / null |
|---|---|---|---|---|
| 2.1 | Report referee (prereg_report_scoreboard) | h = 2; floor; 5 sources; tiers | h 1–20 × floor 15 × source subsets 32 × tier 3 ≈ 29k | hit-rate & asymmetry / block permutation; max over cells |
| 2.2 | F1–F5 hit-rate gates (3.26-era prereg, to write) | 5 gates | the gates are cells of 2.1 — not a separate family | — |
| 2.3 | E1–E5 asymmetry levers (3.16) | lever parameters | τ² 0 … 1; confidence weights; expected-move sizing 0.5 … 2 × ≈ 2k | asymmetry / permutation |
| 2.4 | T1 exposure dial (Test A) | vol target; regime tilt | vol targets 5 … 20%; look-backs 10 … 120; tilt 0 … 1 ≈ 3k | drawdown & Sharpe / block bootstrap |
| 2.5 | Chain rule W2-seq (A2) | 3 legs' thresholds and windows | oil 3–15% × dollar 0–3% × rates 0–30 bp × windows 1–10 ≈ 40k | firings' gold f60 sign share / random-date; **n too small — measured only until ≥ 10 firings** |
| 2.6 | A3 oil-shock path table & A3b estimate | +8%/5 s; H 5–90; kernel | thresholds 13 × windows 10 × h 120 × kernels 30 ≈ 470k (vectorised) | sign hit-rate and pinball / random-date, max over cells |
| 2.7 | A3d tail classifier | 5 features; q90 | feature subsets 31 × tail quantile 80–95 ≈ 500 | AUC / permutation |
| 2.8 | H1–H7 history tables (3.25) | thresholds; h 5/20; GAP 20 | thresholds × windows × h 120 × GAP 7 × 7 tables × markets ≈ 60k | sign share vs base / random-date, max over cells |
| 2.9 | Target range Stage 1 (3.29) | h 60; ±5/10%; regime; 100-session floor | h 1–120 × X 1–30% × regime defs 6 × floors 8 ≈ 170k | Brier skill / block-shuffled labels, max over cells |
| 2.10 | Target range Stage 2–3 | reason vocabulary; model | vocabulary v1/v2; ridge λ; quantile set | pinball & Brier / permuted reasons |
| 2.11 | 08:30 event-time reader (3.19) | 5–120-min windows | windows 1 … 240 min × releases 7 | reaction sign vs reader / permutation |
| 2.12 | T14 phase A/B (same-day extension) | h; event set | h 1–20; event subsets | as registered |
| 2.13 | Instrument robustness (prereg_instrument_robustness) | 5 substitutes | all 47 panel instruments as substitutes | verdict stability |
| 2.14 | §3.24 implied vs realised vol | 20-session realised | realised 5 … 120; VIX/GVZ/OVX/TYVIX; shock sets of 2.6 | gap vs non-shock / permutation |

## 3. Data sources to add (free first; paid only where a free one fails)

| source | cost | what it unlocks | feeds |
|---|---|---|---|
| Stooq daily CSV | free | latest-session fallback (built 22 Oct); second price source for 2.13 | nightly |
| SEC EDGAR full-text search (efts) | free | 8-K/6-K for **every** filer by phrase ("capital expenditures", "guidance"), not a ticker list | corpus; Stage 2 reasons |
| 6-K exhibit parser (TSM, ASML) | free, build | results text for foreign issuers (two TSM filings rejected as cover-only) | corpus |
| Fed speeches & testimony RSS; FOMC SEP/dot plots | free | rhetoric before decisions (the low-specificity end the register says is missing) | T10, Stage 2 |
| CFTC Commitments of Traders (weekly) | free | positioning in gold, silver, oil, 10-yr, dollar — the "forced selling" channel | blind-spot, 2.9 features |
| EIA weekly petroleum status; Baker Hughes rigs | free | oil supply/inventory legs | 2.5, 2.6 |
| TreasuryDirect auction results | free | tail/bid-cover shocks for TLT | H-tables (new H8) |
| Polymarket / Kalshi APIs | free | market-implied odds of events (hike, shutdown, conflict) — a surprise measure that exists before the print | T10, 2.11 |
| GDELT 2.0 | free | event counts and tone as a trigger (not text) | §3.4 |
| CBOE/FRED implied vols (VIXCLS, GVZCLS, OVXCLS, VXTYN) | free | §3.24; vol features for 2.9 | 2.14 |
| FRED daily: T5YIE/T10YIE breakevens, BAMLH0A0HYM2 credit, DTWEXBGS→DX-Y.NYB swap | free | features in §1; the long dollar series H3 needs | 2.8, 2.9 |
| Yahoo: SI=F, HG=F, BZ=F, ^MOVE, TIP, HYG, EEM, BTC-USD, EURUSD=X, USDJPY=X | free | new markets and legs (§1) | all |
| LBMA gold/silver fixes (via FRED or LBMA site) | free | pre-2004 metals history for H4up and the regime tables | 2.8, 2.9 |
| Atlanta Fed GDPNow, Cleveland Fed inflation nowcast, UMich sentiment | free | nowcast surprises | T10 |
| ACLED (research licence) | free w/ registration | conflict events for the geopolitical leg | 2.5 |
| Earnings-call transcripts | paid (Seeking Alpha / FactSet) or limited free (Finnhub) | the "capex cut" wording the 8-K deck may omit | Stage 2, §3.2 |
| ISM PMI, Conference Board | paid; headlines free | activity surprises | T10 |

Nothing above enters a test without the §0 rules; each is a dated corpus or population amendment.

## 4. Earnings pool (amended 22 Oct)

23 issuers by the market they inform (prereg_report_scoreboard amendment). Backfill of the 14 new issuers: `fetch_sources edgar --tickers
META,GOOGL,AMZN,AAPL,AVGO,AMD,JPM,GS,XOM,CVX,NEM,FCX,WMT,CAT --limit 40 --sleep 0.5` (SEC, free, ~10 min) then a dedicated
`doc_read --source earnings_8k --unread-only --limit 600` (~US$40). The EDGAR full-text route (§3) replaces the ticker list once built.

## 5. Run order and budget

1. Build `src/spec_grid.py` with the shared null engine (random-date / permutation / block-shuffle, max-statistic across cells).
2. Families in order of what the main track is waiting on: 2.9 (sample-size rule, the Stage 1 cause) → 2.8 → 2.6 → 2.1 (+ F gates as cells) → 2.3 → 2.4 → 2.14 → 2.7 → 2.11 → 2.5 (measured only) → 2.13.
3. Each family: one night of compute on the Mac at N_NULL 2,000; finalists re-run at 10,000; the md published with the curve, the null band,
   the best cell's p, and the sentence "k of N cells would beat 5% by chance".
4. Promotion: a survivor gets a TRACK § with a prior and a forward log before any engine change.

## 6. The multiplicity rule in one paragraph

If you try N specifications and pick the best, its apparent p-value is meaningless: with N = 1,000 independent cells, the best one shows
p < 0.001 under pure noise. The fix is to ask "how good does the best of 1,000 *noise* cells look?" — run the identical 1,000-cell sweep on
shuffled data many times, record the best statistic each time, and compare. That distribution is the only fair bar for a cell found by
searching. It is why the main track pre-registers a single cell, and why this track can search freely without lying to itself.
