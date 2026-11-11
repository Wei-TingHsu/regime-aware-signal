# Results compendium — every tested claim, as recorded (6 Nov 2026)

*How to read it. "p" is one cell's tail probability — the chance a world with no relationship produces a result at least this strong. "p_family" is
the same question asked of the best cell in a whole search. Below 0.05 the result is unlikely to be luck; above, the data cannot tell it from luck.
Tags: **quant signal** = clears its registered null and the split rule, is non-overlapping and costed, and (for a live rule) its forward log —
none has reached this yet; **discretionary input** = a robust fact or conditional table that changes how a trader sizes, hedges or filters without
being a rule; **neither** = null, instrument check, or explanation only. Sources: PROJECT_MASTER §8 rows 1–52 and every prereg's results table.*

## 1. Gold and the Fed

| claim | result | statistics | conditions / time frame | tag |
|---|---|---|---|---|
| Gold reacts to the rate *surprise* on statement days, not the decision (T9b L1) | yes | −0.11% per bp of 2-yr change on the day; p 0.039 (gold); Treasuries no | 131 statement days 2011–26; daily proxy for the surprise | discretionary input (same-day; 2 pm reader supplies it live) |
| Same with the published 30-min surprise (T9b L3) | not shown | p 0.49 gold, 0.57 Treasuries | Bauer–Swanson series | neither |
| Reaction extends from 2 pm to the close (T14 A) | null | low power | daily data; live reader now logs 1:55→2:15 and the close | neither (open; answered one meeting at a time) |
| Chairs differ per bp (T-K1) / per unit of yield volatility (T-K1′) | yes / **no** | p 0.016 / p 0.118 | Bernanke 25, Yellen 32, Powell 71 statements | discretionary input: a new chair inherits the pooled reaction |
| Eras differ per unit of volatility (T9b by era) | yes | pandemic era 2.7× (19 statements); p 0.026 per σ | 2011–15 / 15–19 / 20–21 / 22–26 | discretionary input: high-vol periods carry the effect |
| Fed-day gold from surprise + statement wording (D4) | surprise alone, high-vol state | Sharpe 1.34 vs noise 0.89, p_family 0.000; wording adds nothing | 132 statements, leave-one-out | discretionary input (statement-day only) |
| Warsh's style distinguishable from Powell's (T-K3) | almost | n 3 p 0.042; n 4 p 0.061; on inflation emphasis and lower hedging; rubric detects past transitions (p 0.011, 0.005) | 4 statements | neither (yet); judged again at n 5 |
| Chair posterior (T-K2σ) | pooled dominates | weight on Warsh's own days 20%; −0.50% ± 0.16 per σ | page quantity | discretionary input |
| FOMC→GLD retired cell (row 14) | split FAIL | halves differ 4.62× | 2011–26 | neither |
| FOMC→GLD by regime | forward test pending | — | since Sep 2026 | — |

## 2. Gold and liquidity, stress, equities

| claim | result | statistics | conditions / time frame | tag |
|---|---|---|---|---|
| Gold decouples from equities in liquidity stress (P1) | null | gap +0.017, p 0.44 | 2004–26, GMM stress state, 20-session correlation | neither |
| Same by era | sign flips, not provable | 2009–14 −0.34; 2022–26 +0.21; p_family 0.35 | five eras | neither (shape noted) |
| **Last month's gold–equity correlation predicts next month's (D3)** | **yes** | 26% of forecast error removed; p_family 0.000; stress state adds nothing | 20-session windows, last 40% of sample out of sample | **discretionary input — hedge sizing** |
| Liquidity (Fed assets − TGA − RRP) → gold, weekly (T-L) | faint, unstable | β +0.08, t 1.96; sign stable in 73% of windows; break Sept 2008 p 0.002, none after | weekly 2004–26 | neither |
| Link by era | on/off | 2015–19 t 2.7, 2022–26 t 2.0; others ≈ 0; recent window p_family 0.18 | five eras | neither |
| Link in stress weeks | null | t −0.6 (calm weeks t 3.7) | T-L4 | neither |
| Link by engine regime (D2b) | lives in regime 2 | β +0.26, t 3.0, R² 4%; regimes differ p 0.385 | weekly, engine labels | neither (descriptive) |
| Trading gold on weekly liquidity, only when the link is 'on' (D2) | null | 0.93 vs 1.66, p_family 0.285 | 52–156-week windows | neither |
| Trading daily liquidity (D2c) | null | 2.48 vs 3.87, p_family 0.235; daily driver is RRP only | since Sep 2013 | neither |
| Gold sold after an equity sell-off (T-L5b, grids) | null | −8%/20: 45% vs 45% base; grid best p_family 0.87 | 22 years, 147 cells | neither |
| Gold bought after a 6% drawdown (D1, two runs) | null once the event day is excluded | 0.050 / 0.045 with the event day; **0.140 without**; no survivor | 1,620 cells with filters | neither; forward rules D1-5nov / -b logged as experiments |
| Sudden one-day sell-off, gold or S&P continue/reverse (D1b) | null ×4 | p_family 0.235–0.915 | 1.5–4% one-day falls, 2004–26 | neither |

## 3. Gold and the named factors

| claim | result | statistics | conditions / time frame | tag |
|---|---|---|---|---|
| Standard factors explain gold out of sample (T-A) | partly | median OOS R² 0.177 (bar 0.20, FAIL); best window 0.224 survives its null | walk-forward 504/20 from 2008; 13 proxies | discretionary input (attribution) |
| Factor signs stable through time (T-B) | dollar, oil yes; rates no | dollar 100%, oil 90%, macro lines 83–87%; hikes 66%, real yields 63%, VIX 59%, war 54%; positioning 52–61% | 75 two-year windows | discretionary input: trust dollar/oil betas as hedge ratios |
| Factors by era (B4) | 2015–19 best explained | R² 0.33 / 0.26 / 0.22; T-A era sweep p_family 0.000 | panel from 2014 (late proxy) | neither |
| The 2026 gold fall explained by factors | mostly not | old (2009–21) betas 29%, recent 11%, pre-episode 2% | peak → 21 Oct 2026 | discretionary input: the fall was outside the named reasons |
| Factor combinations forecast gold (D8) | null | best 0.85 vs 0.97, p_family 0.120 | 299 combinations, walk-forward ridge, 1/5/20 days | neither |
| Residual momentum / reversal (T-H) | null ×5 | GLD p 0.77, SLV 0.56, USO 0.82, SPY 0.31, NVDA 0.19 | 5–60 sessions, 200 shifts | neither |
| Window / leg rules explain episodes (T-F′, T-G, T-I′, T-J) | yes (explanation) | 53% vs 5%; 71%; 74% vs 11%; 79% | shifted-factor nulls | neither for trading; the "why it moved" block |
| Gold after oil shocks (A3a, D5) | null | p_family 0.605; +1.0% at 60 sessions inside noise | 116–152 shocks | neither |
| Oil → rates → gold chain (D5b) | link 1 absent; link 3 same-window | rates after shocks t −0.7…+1.0; gold where real yields fell p_family 0.005 (not tradeable: same window) | D5c registered | neither (pending D5c) |
| Positioning extremes (D6) | null | 0.90 vs 1.81, p_family 0.730 | GLD/SLV/USO, 1990s–2026 weekly COT | neither |

## 4. The product's own calls

| claim | result | statistics | conditions / time frame | tag |
|---|---|---|---|---|
| Report calls beat drift (rows 24/27/33) | no | 59.4% vs q95 59.1% (p 0.0497, INCONCLUSIVE); 58.2% vs 58.8% (p 0.088); h 2: 54.9% vs 57.5% (p 0.40); Sharpe after costs 0.07 | backfill 2008–26, non-overlapping | neither |
| By era / tier / source / asset (A) | none beats its null | best cell 63.4% vs q95 75.0%, p_family 0.957; split rule PASS | five eras | neither |
| E4 asymmetry lever | no | 1.128 vs 1.008; hit below null | — | neither |
| Learner selects better calls (D7) | null | 0.28 vs 1.63, p_family 0.770 | ridge, walk-forward | neither |
| More documents help (political backlog) | neither help nor hurt | +0.7 pts, CI [−0.5, +2.0]; same sign 100%; coverage 38 → 61% | 2,946 documents | neither (coverage) |
| Truncated 6-K filings | at chance | 190 calls at 50.5% | 165 documents | neither |
| Reader separates sources (gate) | yes | spread 0.326, CI [0.308, 0.344] | 5,746 documents | instrument |
| Model 4 long top-5; kernel family; rotation; chain lead–lag; GDELT; inverse oil rule; H0–H7 tables; vol targeting | null / FAIL | p 0.035→0.10 split 9×; p 0.114; NULL; NULL; NO; 47% held out; 0 of 72 cells; 1 of 5 assets | various | neither |
| Model ledger (3 models), 08:30 reader, 2 pm reader | forward, pending | — | since Aug–Oct 2026 | — |

## 5. What holds, and who could use it

Three relationships clear their bars; none is alpha on its own.

1. **Gold's same-day reaction to Fed-rate surprises, strongest when yields are volatile.** Quant: a 2 pm event sleeve sized by surprise ÷ yield volatility, held to the close. Institutional desk: cut gold into high-vol meetings rather than guess the decision. Hedge fund: gold vs 2-year futures around meetings — the ratio of reactions is stable across chairs. Market maker: skew gold inventory and widen quotes into 2 pm in high-vol regimes. Discretionary: a filter — a hawkish surprise means don't buy gold that afternoon.
2. **Gold–equity correlation persists month to month.** Quant: feed the forecast into the optimiser's covariance. Institutional: size the gold hedge monthly; when forecast correlation is high, buy protection elsewhere. Hedge fund: trade the correlation where instruments exist; time gold shorts as cheap insurance. Market maker: a better covariance for multi-asset inventory and gold–equity structures. Discretionary: a monthly line — "gold is behaving like a risk asset / like a hedge".
3. **Dollar and oil carry stable gold sensitivities; rates do not.** Quant: a dollar- and oil-hedged gold position isolates the unexplained part. Institutional: attribution of a client's gold P&L into dollar, oil and gold-itself — a product in itself. Hedge fund: long gold / long dollar to hold gold's own move without the currency. Market maker: live hedge ratios off dollar and oil moves. Discretionary: a move the dollar and oil don't explain points to positioning or geopolitics — the "why it moved" block says which question to ask.

Everything else tested — liquidity drains, oil shocks, chair personality, residual momentum, sudden sell-offs, positioning extremes, factor combinations, document-driven calls — is null on the data we have, and is recorded here so it is not searched twice.

## 6. Added 6 Nov afternoon

- Factor eras on the full 2006–26 span (Bitcoin dropped): the factors explain 18% of gold's daily moves overall, 32% in 2006–08 and 2015–19, 18% in 2009–14; the 2026 fall is explained 29% by 2009–21 sensitivities and 13% by 2022→ ones — **discretionary input (attribution)**, unchanged.
- Residual momentum by era: null in every era (p_family 0.93) — **neither**; closed.
- The oil → rates → gold chain with tradeable timing (D5c): null (p_family 0.905) — **neither**; closed.
- T1 by era: vol-targeting adds +18.6 pts CER for the S&P in 2004–08 and +6.6 for Treasuries in 2022–26, costs 1–3 pts in calm bull eras; regime tilt adds nothing — **discretionary input (risk tool)**. H-tables by era: no era cell passes — **neither**.

**Regime count (decided 2026-11-06):** fixed k = 4 for the product's labels; a second fixed six-state fit (`k6`, `processed/regime_labels_by_k.parquet`) as the attribution lens only. Neither is a predictor; both are conditioning variables for the relationships above.

### N1 — news-attributed ≥ 4% days (SOXX, SPY; 2009 → 2026; recorded 2026-11-11)
- **Cause of a ≥ 4% day, read from GDELT:** about half of event days show no identifiable same-day news in GDELT even with a finance filter; earnings, central bank, macro and election/regulation classes share the rest. Instrument-limited (GDELT misses company news); not a tradeable fact. — *neither*
- **Reversal after a ≥ 4% day:** after falls, the next five sessions are up 57–60% of the time, which is only 2–4 points above how often any five sessions are up — no signal. After a ≥ 4% *rise* the S&P falls the next session 67% vs 45% base (n 42, p 0.006) — one cell of twelve, on the forward log as candidate N1-a. — *discretionary at most, after the forward test*
- **A contradicting bureau release in the next five sessions:** does not lift the reversal rate past the standard. — *neither*
- **Learner on cause class, move size, trend, VIX, release scores:** does not beat "buy the session after a ≥ 4% fall". — *neither*

### Standing rule — short windows first

**Short-window rule (founder, 11 Nov 2026; standing).** News arrives every day. The longer the span of sessions a test measures, the more unrelated news is mixed into it, which adds noise and can hide or fake an effect. So: (1) every test of a reaction to news is run at several span lengths, the shortest first (the release day itself, then +1, +1…+2, +1…+3, and only then 5, 10, 20); (2) no conclusion — pass or null — is written from one span length alone; (3) where a long span fails, the short spans are run before the idea is called null; (4) this applies back to earlier tests whose verdict rests on a single span of five sessions or more (horizon audit, TRACK §3.49). It sits beside the grid-by-default rule (28 Oct) and the sub-period rule; the search over span lengths is judged against the best the same search finds on shuffled data.
