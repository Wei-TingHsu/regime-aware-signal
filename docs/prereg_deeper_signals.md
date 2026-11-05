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
