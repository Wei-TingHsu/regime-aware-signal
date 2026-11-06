# Pre-registration — the deeper tests: from measured patterns to candidate signals (TRACK §3.40)

*Registered 2026-11-05, before any run. Origin: the founder, 5 Nov — "could the test continue by going a bit deeper so that a pattern could
be discovered, then be regarded as a weak trading signal for alpha?" — applied to every past test that showed any conditional structure.*

## 1. What "a weak signal" has to clear, in order

1. **Path, not hit-rate.** Every cell is scored on the whole trade after costs: net Sharpe = (mean forward return − round-trip cost) ÷ its
   standard deviation, annualised by horizon; hit-rate, mean, worst trade and asymmetry carried beside. Cost 10 bp round trip (an axis in D1).
2. **The family null.** The best cell is judged against the best cell the same search finds on time-shifted (or permuted) data: `p_family`
   (`src/sweep.py`). A cell above the null's 95th percentile is a *survivor*. Cells with fewer than 30 trades are never judged.
3. **The forward log.** A survivor is written here by dated amendment as a rule in words, and `src/deeper.py forward` logs every live trigger to
   `processed/forward_signals.csv` from that day. Only a forward log that itself clears the H-table standard (n ≥ 30, hit ≥ base + 10 points,
   p < 0.05) makes a signal; the backtest alone never does.
4. **The learner comes last.** Where a grid has survivors, a walk-forward learner (ridge or boosted trees over the same axes as features) is
   registered as a further amendment, judged against the same null, to find combinations the grid missed. Never instead of the grid.

## 2. The seven tests (`src/deeper.py`)

| id | pattern it extends | grid (every value a cell) | statistic | null |
|---|---|---|---|---|
| **D1** | gold after an S&P drawdown (5 Nov survivor: −6% / 20 / 15) | threshold −4…−10% × look-back 10/20/40 × horizon 5–30 × entry delay 0/1/3 × one filter at a time (gold's own drawdown down/up, dollar up/down, 2-yr rates down/up, liquidity stress/abundant, era) × both directions | net Sharpe per trade set | GLD time-shifted ≥ 250 sessions |
| **D2** | the liquidity–gold link, on in 2015–19 and 2022–26, off otherwise | trailing window 52–156 weeks × 'on' bar (t 1.0–2.5) × mode on/off/always; position = sign of this week's Δlog net liquidity, held Thursday→Wednesday | annualised net Sharpe | liquidity series time-shifted ≥ 52 weeks |
| **D3** | P1's sign flip (safe haven ↔ dash for cash) | realised-correlation window 20–120 × forecast horizon 20/40/60 × with/without the stress state | out-of-sample skill vs the long-run mean (1 − model error ÷ baseline error), last 40% of the sample | future correlations time-shifted |
| **D4** | Fed-day reaction (T9b, the pandemic era, T-K3's rubric) | target statement day / next day / two days × features surprise per σ / rubric (hawk-dove, inflation emphasis, hedging) / both × volatility state all/high/low | leave-one-out, trade the predicted sign; per-meeting Sharpe | targets permuted across meetings |
| **D5** | gold after oil shocks (A3a +1.0% at 60, never judged) | horizon f5–f90 × pool × shock size 5–8 / 8–12 / >12% × regime or era × direction | net Sharpe | forward paths detached from the shock's attributes |
| **D6** | COT positioning as a state (27 Oct candidate) | asset GLD/SLV/USO × z-window 52–156 weeks × bar 1.0–2.0 × horizon 5–40 × fade/follow | net Sharpe | returns time-shifted |
| **D7** | the report's calls, selected by a learner | training window 500–2000 calls × ridge 1–100 × keep top 0/50/75% by predicted return; features tier, specificity weight, ESS, agreement, regime, source, asset | net Sharpe of the kept calls vs all calls | the calls' outcomes permuted |

Registered but not yet coded (next adapters): **D8** earnings-day chain spillover (leader's filing day → followers' 5–20 sessions); **D9** vol-targeting
by era and asset (a risk input, not alpha).


## 2b. The founder's redesigns (5 Nov evening; `src/deeper2.py`)

| id | the founder's reasoning | grid | statistic / null |
|---|---|---|---|
| **D1b sudden sell-off** | "6% in 20 sessions is not a sudden sell-off": the S&P down x% in ONE session and gold down y% the same session; what each does over the next 1–10 sessions | x ∈ {1.5, 2, 2.5, 3, 4}%, y ∈ {0 (no gold condition), 0.5, 1, 1.5, 2}%, h ∈ {1, 2, 3, 5, 10}, era; four readings: gold continues / reverses, S&P continues / reverses | net Sharpe from the next session's open-equivalent (event day excluded); the traded asset time-shifted |
| **D2b the link by regime** | the liquidity link is on in some years and off in others: which engine regime is it on in, so that when the regime returns the link is expected | β, t, R² per engine regime (weekly); regime × liquidity interaction, block-permutation p | p < 0.05 → the standing expectation "same regime, same link" is registered and logged forward |
| **D2c daily liquidity** | the weekly rule arrives too late; trade daily | driver: the overnight reverse-repo balance (daily, same evening) and the Wednesday balance-sheet change spread over the week (flagged as an approximation); z-bar {0.5, 1, 1.5} × h {1, 2, 5, 10} × direction × regime | net Sharpe; GLD time-shifted |
| **D8 factor combinations as an index** | not all factors explain the move: which combination explains and predicts best, as an index | every subset of up to 3 factors (+ all) × trailing 1/5/20-session changes → gold's next 1/5/20 sessions; walk-forward ridge refit every 250 sessions; train 1000/2000; ridge 10/100 | net Sharpe of trading the predicted sign; gold time-shifted (fewer null draws: the grid is large) |
| **D5b the oil → rates → gold chain** | oil up → inflation expectations → hawkish policy → higher real rates → gold down | link 1: 2-yr and 10-yr real yield change 5/10/20 sessions after each shock (mean, share up, t); link 3: gold after shocks split by whether rates rose | net Sharpe; forward paths detached from shock attributes |

**Priors (Claude, before the runs; counted if wrong).** **#100 D1b:** at 2–3% one-day S&P falls (n ≈ 150–300) the S&P shows no continuation or reversal beyond the null; gold shows a one-session reversal up after same-day falls ≥ 1% at p_family 0.05–0.20 — not a survivor; no era cell reaches 30 at x ≥ 3%. **#101 D2b:** the link differs by regime at p < 0.05, strongest in the regime that covers 2015–19 and 2022–26 (the engine's 'calm, tightening' state), β ≈ +0.2. **#102 D2c:** the RRP driver alone is null (p_family > 0.3); the interpolated series looks better only because it leaks the week's information. **#103 D8:** the best combination includes the dollar and real yields; next-1-session Sharpe 0.3–0.6 against a null q95 near 0.8 → p_family > 0.1 — the factors explain gold's move the same day, they do not forecast tomorrow's. **#104 D5b:** link 1 holds weakly (2-yr up after shocks in 55–60% of cases, t 1–2); link 3: gold after shocks where rates rose is lower than where they did not, but inside the null (p_family > 0.1) — the chain is real in sign and too slow and too diluted to trade from the shock.

**Second forward rule (5 Nov):** **D1-5nov-b** — buy GLD 3 sessions after SPY's 20-session return crosses −6%, hold 5 sessions (the D1 grid's best cell, first run). Logged beside D1-5nov; the forward log decides between them.

## 3. Priors (Claude, before any run; counted if wrong)

- **#93 D1:** the long side keeps a survivor near −6% / 20 / 10–20 sessions with 1–3 survivors in all, p_family 0.02–0.10 (i.e. marginal); the "gold already
  down" filter helps, the dollar and rates filters do not; no era cell reaches 30 events; the short side has none. Net Sharpe of the registered cell 0.4–0.8 on ~35 trades.
- **#94 D2:** the "on" rule beats "always" in-sample but p_family > 0.10; the trailing t-statistic is too slow to switch on before the link fades.
- **#95 D3:** realised correlation alone has skill 0.05–0.15 (persistence); the stress state adds under 0.02; p_family < 0.05 for the persistence cell — a usable sizing input, not alpha.
- **#96 D4:** statement-day target with the surprise is the only cell to clear the null (it is the T9b effect, tradeable only from 2 pm); the rubric adds nothing; next-day and two-day targets inside the null.
- **#97 D5:** no survivor; the best cell is a small-n era or regime cell.
- **#98 D6:** fading extremes at the 2.0 bar, 20–40 sessions, best; p_family 0.05–0.20; no survivor at n ≥ 30 after the cooling.
- **#99 D7:** no learner cell beats "all calls" by more than noise; p_family > 0.3.

## 4. Registered forward rules

| date | rule (in words) | source | status |
|---|---|---|---|
| 2026-11-05 | **D1-5nov:** buy GLD at the close of the first session on which SPY's trailing 20-session return crosses below −6%; hold 15 sessions; one entry per 40 sessions; cost 10 bp | sell-off grid survivor, 5 Nov (+17.9 pts vs q95 +17.6, p_family 0.050) | logging from 5 Nov via `deeper forward`; judged at n ≥ 30 |

## 5. Results

| date | test | result | prior |
|---|---|---|---|
| 2026-11-06 | D1 re-run (v2: windows start the session after the event) | long: best −6% / 20 / hold 5 / enter +1, Sharpe 3.46 vs q95 4.23, **p_family 0.140, no survivor**; short: −0.18 vs 2.39, p 0.97. The 5 Nov 0.045 / 0.050 readings included the sell-off day's gold return. Rules D1-5nov and D1-5nov-b stay in the forward log as registered experiments (both triggered 5 Nov). | **#93 wrong** |
| 2026-11-06 | D6 positioning (flows.parquet) | fade/follow z-extremes, GLD/SLV/USO: best USO 0.90 vs q95 1.81, p_family 0.730 → **null** | **#98** right on no survivor, wrong on p (said 0.05–0.20) |
| 2026-11-06 | D1b sudden one-day sell-off | gold continues 3.71 vs 4.96 (p 0.235); gold reverses 2.54 vs 6.58 (0.915); S&P continues 2.50 vs 4.66 (0.395); S&P reverses 4.17 vs 7.44 (0.540) → **null, all four** | **#100** right on no survivor, wrong on the gold-reversal clause |
| 2026-11-06 | D2b the link by engine regime | regime 2: β +0.26, t 2.98, R² 0.043 (200 weeks); regime −1 +0.29 (t 1.5); 0: +0.01; 1: +0.11; 3: +0.13; interaction p **0.385** → the regimes are not distinguishable from one slope; the link lives in regime 2 descriptively only | **#101 wrong** |
| 2026-11-06 | D2c daily liquidity | best: the interpolated weekly series (leaks the week), 2.48 vs 3.87, p_family 0.235 → **null**; the RRP-only driver weaker still | **#102 right** |
| 2026-11-06 | D8 factor combinations → next 1/5/20 sessions | 299 combinations; best cot_oil + macro2, h 20, Sharpe 0.85 vs q95 0.97, **p_family 0.120 → null**: today's factor moves explain today's gold, not tomorrow's | **#103** right on p, wrong on which factors |
| 2026-11-06 | D5b oil → rates → gold | link 1: 2-yr and 10-yr real yields do not reliably rise after oil shocks (t −0.7 … +1.0). Link 3: gold after shocks where DFII10 fell over the next 20 sessions, long f20 Sharpe 2.04 vs q95 1.58, **p_family 0.005** — **not tradeable as found**: the condition uses the same 20 sessions as the return (the standing real-yield→gold relation inside shock windows). Cells conditioning on the first 5–10 sessions did not win. **D5c registered:** condition on the real-yield move over sessions 1–5 after the shock, gold over sessions 6–20; prior **#105**: inside the null (p_family > 0.1). | **#104** right on link 1, wrong on link 3 |
| 2026-11-05 17:5x | D1 gold after a drawdown (first run) | long: best −6% / 20 / hold 5 / enter +3, no filter, Sharpe 4.23 vs q95 4.08, **p_family 0.045**, 2 survivors; short: 0.11 vs 2.51, p 0.94, none. **Superseded:** the forward windows of this run included the event session (fixed in deeper.py v2); the re-run's row replaces it. | #93 half right (threshold, survivor count, short side); wrong on horizon (5 not 10–20) and the gold-down filter |
| 2026-11-05 17:5x | D2 liquidity on/off meta-signal | 'on' rule Sharpe 0.93 vs q95 1.66, p_family 0.285 → **null**: the trailing t-statistic switches on too late | #94 right |
| 2026-11-05 17:5x | D3 correlation regime | last 20 sessions' GLD–SPY correlation predicts the next 20: skill 0.26 (26% of the forecast error removed vs the long-run mean) vs q95 0.09, **p_family 0.000**; the stress state adds nothing | #95 right on structure, wrong on size (said 0.05–0.15) |
| 2026-11-05 17:5x | D4 Fed-day drift | statement-day gold from the surprise alone, in high-volatility states: per-meeting Sharpe 1.34 vs q95 0.89, **p_family 0.000**; the rubric adds nothing; next-day and two-day targets inside the null. Tradeable only from 2 pm. | #96 right |
| 2026-11-05 17:5x | D5 gold after oil shocks | best cell a regime sub-cell, 2.15 vs q95 3.34, p_family 0.605 → **null** | #97 right |
| 2026-11-05 17:5x | D6 positioning | not run: the positioning series is `processed/flows.parquet` / `flows_levels.parquet`; deeper.py v2 finds it | — |
| 2026-11-05 17:5x | D7 calls learner | all calls net Sharpe 0.07 (n 1,646); best learner cell 0.28 vs q95 1.63, p_family 0.770 → **null** | #99 right |
