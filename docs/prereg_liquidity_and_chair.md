# Pre-registration — the liquidity–gold link through time (T-L) and the few-shot chair problem (T-K)

*Registered 2026-10-27 (night, SGT), before any code. Origin: the founder's question of 27 Oct — "we tested whether gold gets sold off when liquidity
drains; was it tested as time-dependent — not there before, there now? I want the logic to hold for all situations — such as a new Fed chair, who will
not announce often enough in his life for a large n; the machine must learn his pattern from a few actions."*

## 1. What is on record (read before registering; nothing re-run)

- **P1, 11 Aug (safe-haven inversion).** Claim: gold decouples from equities under liquidity stress. Liquidity state = 2-component GMM on correlation
  breadth and realised volatility of a basket excluding gold and equities (`src/liquidity_classifier.py`); outcome = 20-session rolling GLD–SPY
  correlation. **NULL, robust:** stress-minus-abundant gap +0.017 (p 0.44); macro-regime gap +0.16, wrong direction. The journal's "if anything gold
  co-moves slightly more in stress — consistent with dash-for-cash selling" is the *sign of a gap that is not distinguishable from zero*, not a finding.
  So "gold is sold when liquidity drains" has never been a registered, passed result here. **The test was pooled over the whole span: one gap, no
  sub-periods, no rolling windows, no change-point. It did not ask whether the relationship changed through time.**
- **T-B, 23 Oct (factor attribution sign stability).** The only time-dependence check on record: 75 walk-forward two-year windows. The rate-based
  proxies flip sign across windows — hike speculation 67%, real 10-yr yield 65% (unstable); dollar 100%, oil 89%, macro lines 83–87% (stable);
  positioning 52–61% (unstable, 27 Oct). Whatever "liquidity" means through yields, gold's response to it is not constant.
- **T9b, 29 Sep (surprise conditioning).** FOMC statement days 2011–2026 (131): gold's reaction to the 2-yr-yield surprise — level 1 INCONCLUSIVE
  (b −0.0054 per bucket, p 0.039), level 3 with the Bauer–Swanson intraday surprises FAIL (b −0.0005/bp, p 0.49). FOMC-by-regime split retired
  (forking paths). No test has ever split FOMC reactions by chair.
- **Not on record:** a direct liquidity quantity (the Fed's balance sheet net of the Treasury's account and reverse repo), a stability test on it, and
  a change-point test on anything.

## 2. T-L — is the liquidity–gold link constant through time?

**Data (free, FRED, as-of Wednesday).** Net liquidity `NL = WALCL/1000 − WTREGEN − RRPONTSYD` (US$ bn: Fed total assets − Treasury General Account −
overnight reverse repo; RRP is daily and is taken as of the Wednesday). `x_t` = weekly Δlog NL. `y_t` = GLD's weekly log return, Thursday-to-Wednesday
(sum of daily log returns from `processed/asset_returns.parquet`). Sample: from GLD's start (Nov 2004) to the latest Wednesday. Contemporaneous.
**This is a description of co-movement, not a trading signal:** the balance sheet is published Thursday for Wednesday.

| test | statistic | criterion |
|---|---|---|
| **T-L1 stability** | β of `y` on `x` in 104-week windows stepped 13 weeks; share of windows with the majority sign | stable if ≥ 80% (the T-B bar) |
| **T-L2 change-point** | Quandt–Andrews sup-F for one break in (α, β) with 15% trimming; null = constant-β model with a circular block bootstrap of its residuals (block 13 weeks, 500 draws) | break if p < 0.05; the break date and β before/after are reported |
| **T-L3 recent-only** | β of the last 104 weeks against the earlier windows' βs | flagged "recent is different" if outside the earlier windows' 5–95% range (descriptive) |
| **T-L4 conditional** | β in the P1 stress weeks vs abundant weeks (`processed/liquidity_states.parquet`, weekly majority) | reported; no criterion (two cells) |
| sub-periods | β, t and n for 2004–08, 2009–14, 2015–19, 2020–21, 2022–26 | reported |
| **T-L5a after an equity sell-off** (the founder's sentence, 27 Oct, added before the first valid run) | β in weeks where SPY's trailing 20-session return at the week's start is ≤ −8%, vs all other weeks; difference in units of its standard error | reported; the registered verdict sits in T-L5b |
| **T-L5b gold after the sell-off** | events = the first session on which SPY's 20-session log return crosses below −8% (one event per 40 sessions); gold's forward 5-, 10-, 20-session return; share negative vs the base rate (all sessions); random-date null, 1,000 draws of as many random start dates. Thresholds −5% and −10% run beside as the sweep (standing rule, 23 Oct) | registered cell −8% / 20 sessions: PASS if n ≥ 30, gap ≥ 10 points and p < 0.05 (the H-table standard); INCONCLUSIVE if n < 30; else FAIL |

**Prior #76 (Claude, before running).** Pooled β > 0 (more liquidity, higher gold) but small, t < 3. T-L1 share 60–75% → **UNSTABLE**. T-L2 p > 0.05 —
no single break survives the bootstrap; weekly noise swamps it. T-L3: the last window inside the range. In words: the link never held reliably and has
not newly appeared; what looks like "gold sold when liquidity drains" in 2026 is one episode, not a law. The founder's reading (a logic that was absent
before and present now) is the alternative; T-L2 and T-L3 are the tests that would support it.

**Prior #80 (Claude, T-L5, before running).** At −8% there are fewer than 30 non-overlapping events since 2004 → INCONCLUSIVE; at −5% (n ≥ 30) the share of
negative 20-session gold returns is within 10 points of the base rate → FAIL. 2008 and March 2020 are the two famous dash-for-cash cases; across all
sell-offs gold's forward return after an equity drawdown is not distinguishable from any other time. T-L5a: β after a sell-off not distinguishable from β in other weeks (|t| < 2).

## 3. T-K — the few-shot chair problem

**The point, stated before any number.** A chair's *actions* (what the statement says, how it changed, whether the press conference softened it) are
measured without noise: one statement gives one exact vector of features. The *market's response* to those actions is measured with noise of about
1% a day on gold against a surprise of a few basis points. Few-shot learning is possible for the first and not for the second: no tenure is long
enough to estimate a chair-specific market coefficient at daily resolution. T-K0 puts a number on that; T-K1 asks whether chairs have ever differed;
T-K2 is the quantity the page should show for the current chair; T-K3 is the few-shot style test on his statements' content.

**Units.** FOMC statement days from `processed/fomc_decisions.csv` up to today (corpus text on disk for 131 statements through 29 Jul 2026; the
16 Sep statement is not yet fetched — a feed gap to close). Chairs by date: Bernanke (to 31 Jan 2014), Yellen (3 Feb 2014 – 3 Feb 2018), Powell
(5 Feb 2018 – 15 May 2026), Warsh (sworn in 22 May 2026; statements 17 Jun, 29 Jul, 16 Sep; the fourth is 28 Oct, 2 pm ET = 29 Oct 02:00 SGT).
Surprise `s` = DGS2(t) − DGS2(t−1) in bp on the statement day (the registered level-1 proxy of T9b). Reaction `y` = GLD's log return on the day.

| test | statistic | criterion / prior |
|---|---|---|
| **T-K0 power (a calculation, not a test)** | pooled β of `y` on `s`, residual σ, var(s); meetings needed to detect a chair-specific difference δ at α 5% and power 80%: n = (2.80 σ)² / (δ² var s), for δ = β/2 and δ = β | **Prior #77:** n > 100 for δ = β/2 — beyond any tenure (8 meetings a year) |
| **T-K1 do chairs differ at all?** | chair × surprise interaction F-test on GLD (Bernanke, Yellen, Powell; ≥ 20 statements each), p from 2,000 permutations of the chair labels; TLT as the cross-check | PASS if p < 0.05 on GLD. **Prior #78: FAIL** (p > 0.2); between-chair variance τ² ≈ 0 |
| **T-K1′ chairs differ in volatility units?** (added 27 Oct after T-K1, before running) | the same interaction test with the surprise divided by the 2-yr yield's trailing two-year daily volatility (bp per day), so a 2 bp move at the zero bound and a 10 bp move in 2023 are compared on the same scale | PASS if p < 0.05 on GLD. **Prior #81: FAIL (p > 0.05)** — the per-bp difference found in T-K1 is the yield era's scale, not the chair: per bp Bernanke −0.33, Yellen −0.14, Powell −0.10, but times each era's surprise sd (2.6, 5.7, 7.8 bp) the three come to about −0.8% per sd |
| **T-K2 the current chair's posterior** | empirical Bayes: τ² from the chairs with n ≥ 20 (method of moments); for the current chair, w = τ² / (τ² + se²), posterior mean = β_pool + w (β̂_chair − β_pool), sd = (1/τ² + 1/se²)^−½ | reported with the shrinkage weight; refreshed after each statement. No criterion — it is what the page shows instead of a per-chair estimate. **Amendment 27 Oct (after seeing the v1 run, before the v2 run):** for a chair with few statements the own residual has 1 degree of freedom and is not an estimate (Warsh's 3 points gave se 0.03 and a 92% weight); the se used in the weight is the pooled residual σ divided by √Σ(s − s̄)² over his statements. Both weights are reported |
| **T-K3 few-shot style (next script, after T-K0/T-K1)** | the LLM reads every statement (and press-conference transcript where on disk) on a fixed rubric: hawkish–dovish score, guidance strength, balance-sheet language, inflation-vs-labour emphasis, hedging density, dissents, length change, novelty vs the previous statement. Energy distance between the current chair's n statements and the previous chair's last 8; exact permutation over all C(n+8, n) arrangements | PASS if p < 0.05 ("his style is distinguishable"). Smallest attainable p: n = 3 → 1/165, n = 4 → 1/495. **Prior #79:** with n = 4 the overall distance does not separate (p > 0.05); balance-sheet language is the single dimension most likely to |

**Standing rule proposed by this registration.** "Learn fast from few" = a strong prior from the pooled history (T-K2) plus content features measured
without market noise (T-K3); never a per-chair market coefficient from n < 30. The page may say "Warsh so far: n statements; style distance from
Powell p = …; gold's reaction assumed at the pooled value until the data can say otherwise (after ~N meetings)".

## 4. Amendments

| date | change | reason |
|---|---|---|
| 2026-10-27 | Units error in the first T-L run: WTREGEN is in millions on FRED (taken as billions), net liquidity negative, every week dropped; `to_bn` guard (median > 50,000 → millions). First module kept in scripts_applied/superseded/ | a data error, not a prior; counted in the text, not the tally |
| 2026-10-27 | T-L5a/b added; T-K1′ added; T-K2 se from the pooled σ (texts above) | the founder's exact sentence; the chair–era confound seen in T-K1; a 1-dof se is not an estimate |

| 2026-10-27 (23:50) | **Data error in T-L5b, after the first valid run:** the price panel starts in 1995 and GLD in Nov 2004; equity sell-offs before GLD existed (21 of 64 at −5%, 10 of 30 at −8%, 7 of 23 at −10%) were counted as zero gold returns, and the random-date null drew from the same dates. The medians printing as exactly 0.00% exposed it. Events and the null's date pool are restricted to GLD's history; the rows written to the register are replaced by the re-run; **#80 re-judged clause by clause** (−8% INCONCLUSIVE with n < 30; −5% within 10 points; T-L5a |t| < 2). The first T-L5b numbers are void and not quoted. | a data error, not a prior; counted in the text |
| 2026-10-27 (23:50) | **T-K2 in volatility units (T-K2σ).** T-K1′ found no chair difference once the surprise is in units of the yield's own volatility, so that is the scale on which chairs are exchangeable; the between-chair variance per bp (τ 0.109% per bp) was the yield era's scale and must not lend a few-statement chair a 65% weight. The page's chair posterior is computed per σ (τ_σ from Bernanke/Yellen/Powell, the chair's se from the pooled residual σ) and translated to per bp at today's yield volatility. Expectation, not a prior: the weight on Warsh's own three statements falls well below the 65% found per bp. | consistency between T-K1′ and the quantity shown |
| 2026-10-27 (23:57) | **Record note.** Commit 6b1e44a carries the message of this fix, but the fix had not run: the script was not yet on disk, so the v2 modules re-ran unchanged, the contaminated T-L5b rows stayed, and two result lines were duplicated in CURRENT_STATE (removed here as exact repeats). History is not rewritten; the next commit applies the fix and says so. | an honest ledger |
| 2026-10-28 | **Correction to section 3 'Units':** the 16 Sep 2026 statement IS on disk (`data_provenance/docs/fomc_statement/20260916.txt`, 131 words in the 2026 format) and IS read under v1 (132 texts, 132 reads); CURRENT_STATE 18.8 recorded that re-read on 24 Sep. The 27 Oct sentence 'not yet fetched — a feed gap to close' and TRACK 3.35's 'not in the corpus' were wrong: written from the T-K0 sample count, not from a listing. Wrong-prior candidate, founder to decide (#10's rule: a negative claim about the repo needs a grep). T-K3 therefore runs on all three Warsh statements today and on four after 28 Oct. | found by `ls` on 28 Oct, before any T-K3 read |
| 2026-10-28 | **T-K3 implemented** in `src/chair_style.py`, before any read: every statement on disk read on the registered rubric (hawkish–dovish, guidance strength, balance-sheet language, inflation-vs-labour emphasis, hedging density, dissents, novelty vs the previous statement; length change computed from the texts), with its own cache folder `data_provenance/doc_reads_style/` and prompt version `style-v1-2026-10-28` — never pooled with v1; features z-scored on all statements; energy distance; exact permutation over all C(n+8, n) arrangements; per-dimension distances reported descriptively (eight dimensions, no single one is a finding). **Acceptance check, registered before the first run:** the same test on Yellen's last 8 vs Powell's first 8 and Bernanke's last 8 vs Yellen's first 8 (C(16,8) = 12,870 arrangements each). If neither transition separates at p < 0.05 the rubric has no discriminating power and a Warsh null is UNINFORMATIVE, not FAIL. It shows the rubric can see a change at a transition, not that the change was the person — T-K1's era confound applies. Synthetic selftest (planted 3.5-sd shift on one of eight dimensions at n = 4 vs 8 detected in ≥ 90%; no shift rejected in 2–8%) must PASS before the read. Reading order: n = 3 today (reported, not judged), n = 4 after the 28 Oct statement (prior #79 judged there, as written). Cost measured on disk before the read (`chair_style cost`). **Prior #82 (Claude):** Yellen→Powell separates at p < 0.05, on hedging density and balance-sheet language; Bernanke→Yellen does not (p > 0.05). | the next script after T-K0–K2; the instrument-first rule (every null from an instrument shown to catch a known effect) |

## 5. Results

| date | test | result | prior |
|---|---|---|---|
| 2026-10-27 | T-K0 power | 131 statement days 2011-01-26 → 2026-09-16; pooled β −0.1138% per bp (se 0.0141), residual σ 1.07% a day, surprise sd 6.7 bp. Meetings needed at α 5%, power 80%: **62** for a chair whose reaction is half the pooled one, **16** for a reaction that has vanished. A four-year term is 32 meetings. docs/chair_power.md | **#77 wrong** (I said > 100; the same-day reaction is twice what I assumed and the noise smaller) — the conclusion survives in a weaker form: a halving is not detectable within one term |
| 2026-10-27 | T-K1 chairs differ (per bp) | Bernanke −0.332 (25), Yellen −0.144 (32), Powell −0.096 (71) % per bp; interaction F 4.43, permutation p **0.016 → PASS**; between-chair τ 0.109% per bp. TLT cross-check F 0.36, p 0.61 — the bond market's reaction does not differ by chair. **Caveat:** each chair sits in one yield era (Bernanke's surprises sd 2.6 bp at the zero bound), so chair and era are confounded → T-K1′ | **#78 wrong** (I said FAIL) |
| 2026-10-27 | T-K2 Warsh (3 statements, v1) | own slope −0.142% per bp; the own 1-dof se (0.03) gave a 92% weight — not an estimate (amendment above). His three statement days: mean surprise +6.0 bp (hawkish), mean GLD day −0.82%; the pooled slope times +6.0 bp is −0.68%, i.e. most of the fall is the hawkish surprise, not a different reaction to him | no prior; the page quotes the pooled-σ posterior from the v2 run |
| 2026-10-27 | T-L (GLD) | 1144 weeks 2004-11-24 → 2026-10-21: pooled β +0.080 (t +1.96); T-L1 73% of windows share the majority sign (+) → UNSTABLE; T-L2 sup-F 8.41 at 2008-09-24, p 0.002 → BREAK (β +0.615 → +0.031; the link was stronger before the break, when net liquidity barely moved week to week — sd 1.27% → 1.92% after — the opposite of 'absent before, present now'); T-L3 last two years β +0.194 vs the earlier range -0.235..+0.355 → nothing new; T-L4 stress weeks β -0.053 (t -0.64, n 117) vs abundant +0.200 (t +3.66, n 1014); T-L5a β after a sell-off +0.021 (n 38 weeks) vs other weeks +0.107, difference t -0.52; T-L5b (−8%, 20 sessions, events within GLD's history): 20 events, 45% negative vs base 45% (gap +0 pts, p 0.572) → INCONCLUSIVE (n < 30); at −5%: 43 events, 33% vs 45% (gap -12, p 0.972) → FAIL. docs/liquidity_link_GLD.md | **#76 wrong** (no_break did not hold); **#80 wrong** (-5% within 10 points of base did not hold) |
| 2026-10-27 | T-K1′ and T-K2 (pooled σ, volatility units) | T-K1′: interaction F 2.10, permutation p 0.118 → FAIL — no chair difference once the surprise is in volatility units; β per σ of the yield — Bernanke -0.80, Yellen -0.35, Powell -0.45% (per bp they were -0.332, -0.144, -0.096). T-K2 per bp with the pooled-σ se: Warsh weight on own data 65% (was 92%), posterior -0.1324% ± 0.0643 per bp. T-K2σ in volatility units, the scale on which chairs are exchangeable: weight on own data 15%, posterior -0.491% ± 0.166 per σ (≈ -0.0931% per bp at today's 5.3 bp/day) — the page quotes this one. docs/chair_power.md | **#81 right** |
| 2026-10-28 | T-K3 chair style (rubric, exact permutation) | T-K3 (Warsh n = 3 vs Powell's last 8, exact permutation over 165 arrangements, floor 0.0061): energy 3.39, p 0.0424 → PASS — his statements are distinguishable from the previous chair's on the rubric; strongest dimension inflation_vs_labour (p 0.018; balance_sheet ranked 6 of 8). Acceptance on past transitions: Bernanke->Yellen p 0.011; Yellen->Powell p 0.005 → INSTRUMENT OK (at least one past transition separates). docs/chair_style.md | #79 not yet judged (n = 3 read; judged at n = 4 as registered); **#82 wrong** |
