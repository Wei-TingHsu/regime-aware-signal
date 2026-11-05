# Pre-registration — the sub-period audit and the grid-by-default rule (TRACK §3.37)

*Registered 2026-10-28 (afternoon, SGT), before any re-run. Origin: the founder, 28 Oct — "if we only looked at the entire history the
overall result might be balanced out and we could not see a shift in trend through some sub-periods; I want all of them re-tested, not
five" — and, the same hour, "every variable should change and be tested to see which condition shows the strongest pattern; we are
prioritising finding the relationship, by simple statistics or machine learning."*

## 1. Two standing rules, stated once

**Grid by default.** Every fixed number in a test is a grid variable from now on, not only when the registered cell fails (the 23 Oct rule
ran the sweep after a failure). The whole surface is published. The strongest cell is judged against the strongest cell the same search finds
on data with no relationship — the best-of-sweep null (`src/sweep.py`: the statistic of every cell on 100–300 draws of time-shifted or
block-permuted data; `p_family` = share of draws whose best cell is at least as strong as the real best cell; a *survivor* is a cell above the
null's 95th percentile). This is the only number that means anything for a searched cell: on noise, a 147-cell grid of sell-off tests
produces best gaps of ±15–20 points. The registered cell's verdict stands as recorded; a survivor is promoted to a forward test by dated
amendment. Machine-learning forms enter the same way: a walk-forward learner with the grid variables as features, scored out of sample, against
the same best-of-grid null on shifted data — registered per family after the grid run, never instead of it.

**Era as an axis, not a loophole.** Rule C (both halves same sign; neither half > 3× the other) stays the guard against one-era findings.
A *transition* is claimed only when (i) a registered break test clears p < 0.05 with the null the test names, (ii) the post-break value sits
outside the pre-break windows' 5–95% range, and (iii) the two sides fail rule C's S1 or S2 across the break. Where "era" enters a grid, the family
null covers the era choice too, so "the era in which it works" is searched and judged in one pass. Any one-era PASS needs a forward test before
it is a verdict. Eras are fixed here and never moved: **2004–08, 2009–14, 2015–19, 2020–21, 2022–26** (the pre-2004 span is reported where a series
reaches it), plus the median-date split and rolling windows. Minimum cell sizes: 30 events, 250 sessions, 100 weeks — smaller cells are printed
as "·" and never judged.

## 2. Every registered test, classified (PROJECT_MASTER §8 rows 1–52 and the un-numbered families)

**Already era-aware (no re-run needed; listed so the audit is complete):** 13 Step-3 cells (7 → 1 under the split), 14 FOMC→GLD (split FAIL 4.62×),
16/17 Model 1 (3.88×), 20 Model 4 (9.08×), 21 kernel family, 44 A3 inverse rule (held-out = chronological), 47 T-A/T-B (walk-forward windows),
51 T-L1–L3 (rolling, one break, recent window), 52 T-K (eras = chairs).

**Not applicable (no time axis, or forward-only with no history yet):** 7 `_z()` look-ahead, 10 Step-3 acceptance, 11 specificity gate, 12 read
audits, 22 FOMC→GLD by regime (forward), 23 scoreboard acceptance, 38 event calendar, 39 A4 reader consistency, 41 08:30 reader (30-row floor
≈ Jan 2027), the model ledger (since 19 Aug), the 2 pm reader. Reader drift over document years (11, 12, 39) is an optional descriptive check.

**Group A — the backfill CSVs, one module (`src/era_scoreboard.py`), $0, this week:**

| row | claim | re-run |
|---|---|---|
| 24 / 27 / 33 | the report's calls beat drift | hit-rate, asymmetry, mean signed, PF per era; block-permutation null per era; rule C; sweep era × source × asset |
| 25 | the tiers grade confidence | tier table per era (same module, `tier` column) |
| 26 | `fomc_minutes`-driven calls wrong more often | dominant-source table per era |
| 34–37 | E1–E4 levers | the same module on each `report_backfill_*_E*.csv` |
| 15 | reader–history agreement predicts better | `agreement` column by era (follow-up flag) |
| 6 / 8 / 28 / 40 | design variants and instruments | the same module on `_altinstr`, `_wtifut`, `_wtispot` |

**Group B — series on disk, per-test adapters on the engine, $0:**

| item | row | claim | module | status |
|---|---|---|---|---|
| B1 | 51 | T-L6: liquidity–gold by era; sequential sup-F up to 3 breaks; the three registered watershed dates; recent-window sweep | `era_liquidity liquidity` | written |
| B2 | 1 | P1 safe-haven inversion by era, rolling 2-year windows, sweep era × window × lag | `era_liquidity p1` | written |
| B3 | 51 | T-L5b as a grid: threshold −4…−10% × horizon 5/7/10/13/15/20/30 × look-back 10/20/40 × era, both directions | `era_liquidity selloff` | written |
| B4 | 47 | factor betas and R² per era, sign vs pooled; T-A by era × window (sweep); the 2026 episode re-attributed with pre-episode, 2009–21 and 2022→ betas | `era_factors` | written |
| B5 | 29 / 30 | T9b by era in bp and per σ; era × surprise interaction | `era_fomc` | written |
| B6 | 32 | T1 vol-targeting / regime-tilt CER by era | `exposure_dial` adapter | next |
| B7 | 42 / 43 | A3a paths after oil shocks by era and pool | `era_events oil` | written (measured only) |
| B8 | 48 | T-H residual momentum: w × h × era, family null | adapter on `era_factors.fit` | next |
| B9 | 46 | target-range reach probabilities by era | adapter | next |
| B10 | 45 | H0–H7 tables by era | adapter | next (measured only) |
| B11 | 27 Oct flows run | COT positioning level as a state, by era | adapter | next |
| B12 | 31 | T14 phase A by era | adapter | next (measured only; n small) |
| B13 | T-L5b, H-tables | the sell-off and event tables by era | B3 / B10 | — |

**Group C — returns only, through the backtest engine, $0:** 3 P2 chain lead–lag, 4 rotation order, 9 λ removal, 18 the 54 grid configurations,
19 costs by era (spreads moved), 49/50 the leg rules' explained share by era (descriptive), 16/17 Model 1 on five eras beyond the median split.

**Group D — the reader by document year, $0, optional:** 11, 12, 39 — specificity and direction by year of the document, a drift check on the
instrument, not a market claim.

Order of work: A (one run per CSV), then B1–B5 and B7 (written), then B6/B8–B12 (adapters), then C, then D. Each run writes `docs/era_*.md` and
`.json`; the results rows below are filled from those files, never from a terminal.

## 3. Priors (Claude, before any run; counted if wrong)

- **#85 Group A, `97d9bf07dd2c_n5793` at h = 2:** no era beats its own null; rule C: S1 PASS, S2 FAIL (the pooled mean signed return is near zero,
  so one half exceeds 3× the other); the sweep's best cell has p_family > 0.05; `earnings_8k` is the strongest source in every era with n ≥ 30.
- **#86 B1 (T-L6):** no break after September 2008 clears p < 0.05; the 2022–26 slope sits inside the earlier range; liquidity's weekly volatility in
  2022–26 is ≥ 1.5× its 2009–19 level and R² rises while the slope does not — the driver moved, the habit did not; no watershed date within 26 weeks of a break.
- **#87 B2 (P1):** every era's gap within ±0.05; the safe-haven sign (negative gap) appears in no era beyond its null; sweep p_family > 0.05.
- **#88 B3 (T-L5b grid):** "gold sold" best cell p_family > 0.05; "gold bought" best cell (the 27 Oct −5% / 20-session reading) does not clear the
  best-of-sweep 95th percentile — p_family > 0.05, no survivor.
- **#89 B4:** T-A by era: 2009–14 and 2022–26 the highest median out-of-sample R² (0.20–0.25), 2015–19 the lowest; the sweep survives (p_family < 0.05,
  as T-A's did); the 2026 episode's explained share < 0.3 under the 2022→ betas and < 0.2 under 2009–21 — outside the named reasons in every era;
  dollar and oil keep the pooled sign in every era, real yield and hikes flip in at least two.
- **#90 B5:** per σ no era difference (p > 0.05); per bp a difference (p < 0.05) carried by 2022–26's larger surprises — T-K1 → T-K1′ again.
- **#91 B7:** gold's median 60-session path after an oil shock positive in every era except 2015–19; every era under 30 shocks → measured only.
- **#92 silver (`prereg_silver_stocks.md` v2):** across the whole grid, "stocks lead price" has no survivor; "price leads stocks" has at least one.

## 4. Results

| date | item | result | prior |
|---|---|---|---|
| 2026-11-05 | A — calls by era (`97d9bf07dd2c_n5793`, h 2) | 2009–14 hit 57.0% (n 263, null q95 58.6%), 2015–19 54.6% (421; 57.2%), 2020–21 58.6% (263; 60.1%), 2022–26 53.8% (699; 56.4%): no era beats its null. Rule C: S1 PASS, S2 PASS (ratio 1.30). Sweep era × source × asset: best 2020–21 × earnings_8k 63.4% vs best-of-sweep q95 75.0%, p_family 0.957. docs/era_scoreboard_97d9bf07dd2c_n5793_h2.md | **#85** right on 'no era beats its null' and on the sweep; wrong on S2 (predicted FAIL) — counted if the founder agrees |
| 2026-11-05 | B1 — T-L6 liquidity–gold by era | β by era: 2004–08 +0.05 (t 0.5), 2009–14 +0.04 (0.4), 2015–19 +0.20 (2.7, R² 0.027), 2020–21 −0.01 (−0.1), 2022–26 +0.23 (2.0, R² 0.016). Sequential sup-F: one break, 2008-09-24 (p 0.008, β 0.62 → 0.03), none after; no registered watershed within 26 weeks. Recent-window sweep: best W 312, z +1.80 vs q95 +2.87, p_family 0.183. Liquidity's weekly volatility: 2022–26 1.41% vs 2015–19 1.37%, 2009–14 1.60%, 2004–08 2.61%. Reading: the link is present in 2015–19 and 2022–26 and absent in 2009–14 and 2020–21 — on-and-off, not 'absent then present'; no break survives. docs/era_liquidity_liquidity.md | **#86** right on no break and on 2022–26 inside the range; wrong on the volatility clause (predicted ≥ 1.5× 2009–19; measured ≈ 1×) — counted if the founder agrees |
| 2026-11-05 | B2 — P1 by era | Stress-minus-abundant gap in 20-session GLD–SPY correlation: 2004–08 +0.04, 2009–14 **−0.34**, 2015–19 −0.10, 2020–21 +0.04, 2022–26 **+0.21**; pooled +0.007. Sweep era × window × lag: best 2009–14 \|gap\| 0.344 vs q95 0.510, p_family 0.350 — the state labels are so persistent that block-permuted labels produce gaps this large by chance. Reading: the sign flips from safe-haven (2009–14) to dash-for-cash (2022–26), the shape the founder asked about, but the instrument cannot tell it from chance with this few independent stress episodes. docs/era_liquidity_p1.md | **#87** right on 'no era beyond its null' and the sweep; wrong on 'every gap within ±0.05' — counted if the founder agrees |
| 2026-11-05 | B3 — T-L5b grid (147 cells × eras, both directions) | 'Gold sold after a sell-off': best cell −4% / 10 sessions / look 10 / all, gap +4.8 pts (n 67) vs q95 +20.9, p_family 0.865, no survivor. 'Gold bought after a sell-off': best cell **−6% / 15 sessions / look 20 / all, gap +17.9 pts (n 34) vs q95 +17.6, p_family 0.050, one survivor** — by 0.3 points, at the bar. Every era-specific cell under 30 events ('·'). docs/era_liquidity_selloff_sold.md, _bought.md | **#88** right on 'sold'; wrong on 'bought' (predicted no survivor) — counted if the founder agrees. Under the standing rule the survivor is a candidate for a forward test by dated amendment, not a finding |
| 2026-11-05 | B4 — factor sensitivities by era (GLD) | The factor panel starts in 2014 (a late-starting proxy truncates it: 3,046 sessions), so only 2015–19, 2020–21, 2022–26 are measured: in-sample R² 0.33, 0.26, 0.22. T-A by era × window: best W 1008 × 2015–19 median OOS R² 0.437 vs q95 −0.007, p_family 0.000 (survives). The 2026 fall re-attributed: pre-episode 504 sessions explain 2%, **2009–21 betas 29%**, 2022→ betas 11%, all 25% — the old sensitivities explain more of the fall than the recent ones; none explains most of it. docs/era_factors_GLD.md | **#89** right on the sweep surviving and on '< 0.3 under 2022→'; wrong on the era ranking (2015–19 is the highest, not the lowest) and on '< 0.2 under 2009–21' — counted if the founder agrees. Follow-up: re-run with the late-starting proxy dropped so 2004–14 enter |
| 2026-11-05 | B5 — T9b by era | β per σ: zero bound (39) −0.40 (t −4.4), normalisation (34) −0.39 (−4.7), **pandemic (19) −1.12 (−4.2)**, hiking (40) −0.42 (−4.4). Era × surprise interaction: per bp F 5.10, p 0.005; **per σ F 3.06, p 0.026 — the eras differ even in volatility units**, carried by 2020–21: gold reacted about 2.7× more per unit of surprise in the pandemic era, on 19 statements. By chair (T-K1′) this was invisible because the era sits inside Powell's tenure. A closed era cannot be forward-tested; it is recorded as measured. docs/era_fomc.md | **#90 wrong** (predicted no difference per σ) — counted if the founder agrees |
| 2026-11-05 | B7 — oil shocks by era | Measured only (every era under 30 shocks in p8; p5 reaches 31–37): GLD's 20-session median after a shock positive in every era but 2015–19 (p5: +2.2%, +1.1%, −0.3%, +0.3%, +0.4%). docs/era_events_oil.md | **#91** judged by the founder from the f60 column of the table |
| 2026-11-05 | T-K3 at n = 4 (28 Oct statement in) | Warsh's 4 vs Powell's last 8: energy 2.41, exact p **0.061** (30 of 495 arrangements) → does not separate at 0.05; at n = 3 it had (0.042). Dimensions: inflation-vs-labour 0.010, hedging density 0.038, balance sheet 0.275. Acceptance unchanged (both past transitions separate). Chair posterior refreshed: weight on his own 4 days 20% per σ, posterior −0.50% ± 0.16 per σ; his days averaged −0.53% on gold against −0.43% implied by his +3.8 bp hawkish surprises. The 2 pm reader fired live for the first time (02:00:37 SGT, reaction file 02:20). docs/chair_style.md, chair_power.md | **#79** right on the verdict (no separation at n = 4), wrong on the dimension (balance sheet named; inflation emphasis measured) — counted if the founder agrees |
