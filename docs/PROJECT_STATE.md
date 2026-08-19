# PROJECT STATE — briefing document

*Upload this file (or the `briefing.md` bundle) at the start of a new conversation to
resume without re-explaining. Last updated: 2026-08-20 (early hours SGT). Keep it
updated after each workstream closes.*

> ## STATUS
>
> The NYSE-session migration cascade is **COMPLETE** — every downstream script has
> been re-run. The forward test is live on the new basis.
>
> Active workstream: **GDELT event layer.** The BigQuery query was lost and has been
> recovered; the ingest is now scripted. Two findings are open and are the reason the
> 2025–2026 extension is the next step.

---

## What this project is

**Regime-Aware Cross-Asset Signal Framework.** Three research problems + a product
vision: engines that (a) read the macro state and issue directional calls, (b) detect
event-triggered rotation cascades, (c) narrate scenarios via an LLM layer. The
47-asset universe is an **MVP baseline and must stay expandable** — never hard-code 47.

**Product vision.** Rotation is **event-initiated**, but the event names the **focus
SET, not the ORDER**. GDELT/text detects the trigger and the set; price statistics
determine sequence and timing **within** event episodes.

**Where the three engines stand.**
1. **Macro engine — measured and thin.** Sharpe **0.25–0.51 depending on universe**.
   *Done being measured.* Re-tuning it until the number improves is the overfitting
   failure the working principles exist to prevent.
2. **Event engine — its real test has not happened.** Drift-existence is unrun.
3. **Rotation chain — its first test asked the wrong question**, and the current engine
   is structurally unable to detect the kind of chain most likely to exist (below).

The system thesis is error cancellation across engines with different data, horizons and
failure modes. **That correlation has never been measured**, so "each engine is modest"
and "the system does not work" remain different claims until the ensemble step runs.
Equally: if drift-existence is null on an adequately powered sample *and* conditional
rotation is null, the product has no foundation and the correct response is to say so.
Three documented nulls with rigorous method remain a legitimate capstone — a weaker
*business*, not a failed *project*.

### Architecture decision (2026-08-19): CONDITIONAL MERGE of the event and rotation engines

Interruptions inside cascades are expected to be common, and detecting them requires
event detection — the same detector that identifies a trigger identifies a rupture. So
the natural form is **one engine**: GDELT segments time into episodes (start on trigger,
censor on rupture) and the chain logic runs inside them.

**Merge only if and when Stage 1 drift-existence is positive.** A merged engine built on
an undetected trigger has nothing to condition on. Two consequences to hold in view:
merging leaves **two** engines, not three, reducing the diversification the
position-space combiner assumes; and it concentrates risk, since a null on event
detection would kill both lines at once.

---

## The calendar migration (2026-08-18) — complete

`build_panel` used `pd.bdate_range` (Mon–Fri **including market holidays**). Those rows
carried no asset returns but had macro values forward-filled onto them, entering the PCA
and GMM as near-duplicates — manufactured data, against the rule *extend by removing
redundancy, never by imputation*.

| 2006+ panel | before | after |
|---|---|---|
| rows | 5,382 | **5,188** |
| rows with zero asset coverage | ~196 | **2** |

Not free: ≤46 rows per series carried genuinely new macro values (Good Fridays, Hurricane
Sandy 2012). Still correct — a macro state with no session cannot be traded.
Side effect: `analog_core._forward` rolls over index rows, so with a session index it is
now session-counting; that horizon bug is resolved with no code change.

**Which results were exposed, and which were immune — the key structural lesson.**
Problem 1 and `chain_rotation` both `dropna` before computing, so all-NaN holiday rows
were *already* discarded. Their stability is **not** evidence the migration was
inconsequential; it is evidence they were never at risk. The backtest had no such
protection, and it moved. **Ask which results were exposed, not just which survived.**

### n=4 re-earned — hypothesis NOT falsified, case narrowed

| criterion | old panel | session panel | verdict |
|---|---|---|---|
| seed ARI n=4 | 1.000 (n=5 fragile 0.774) | 1.000 — n=3, n=5 also 1.000 | **leg lost** |
| silhouette | peaks n=4 | n=4 0.4689 vs n=2 0.4678 | **tie** |
| run-length median | 52.5d | **51.0d**, 12 runs (others 3–7d) | **holds decisively** |
| generalization gap | n=4 +4.89 | **n=4 +5.130** (n=3 +0.507) | **against n=4** |

Direct n=2 probe (a blind spot in `verify_regimes`, closed): median run 4.0 vs 51.0; gap
−0.080 vs +5.130. Pre-registered rule required n=2 to win **both**. It won one. **n=4
stands**, on run-length persistence plus an economic argument (PC1 rates 52.3% + PC2
money/dollar 27.2% = 79.6%; a 2-regime split collapses two distinct axes into one).

**A registered prior that was wrong:** removing duplicates was predicted to *reduce*
persistence and leave ARI intact. Persistence barely moved; instead the duplicates had
been *destabilising n=5*. **"n=5 fragile at 0.774" was partly an artifact** and is struck.

### PCA on the session panel (5,188 × 8, from 2006-01-03)
PC1 52.3% DGS2 (+0.984) · PC2 27.2% M2SL (+0.813) · PC3 12.8% VIXCLS (+0.964) ·
PC4 5.0% T10Y2Y (+0.402, weak) · PC5 1.9% DTWEXBGS (+0.245, weak). Top 3 = 92.3%.
**No renumbering this refit** — stress axis stays PC3.

---

## Current status by workstream

### Regime engine — DONE
n=4 pinned in `config.yaml`; every consumer reads it. Regime structure barely moved
(each regime −3–4%, macro character unchanged to 2dp). Classifier and verifier agree
exactly: 12 runs, median 51.0, mean 432.3. Current regime as of 2026-08-18: **Regime 1**
(tight policy, high 10Y, strong USD).

| regime | days | mean run | VIX | 10Y | USD |
|---|---|---|---|---|---|
| 0 | 1735 | 434 | 22.5 | 2.80% | 92.7 |
| 1 | 984 | 492 | 18.0 | 4.16% | 121.8 |
| 2 | 516 | 258 | 15.4 | 4.69% | 96.0 |
| 3 | 1953 | 488 | 18.5 | 2.02% | 113.7 |

### Problem 1 (safe-haven) — DONE, clean NULL, basis-independent
Liquidity gap **+0.011, p 0.488** (581 stress days / 5,448); macro gap **+0.167,
p 0.0814** (1,084 / 5,186). Robustness cross-check identical to 3dp across all eight
cells; primary non-significant everywhere (p 0.415–0.537). Liquidity classifier crisis
lift **×2.99**.

*Phrasing correction:* three of four primary raw cells are now mildly negative — noise
around zero. "If anything it co-moves slightly more" is now carried by the **cross-check**
block, not the primary one.

**Stress-axis bug (fixed 2026-08-18).** `safe_haven_robustness.py` selected its stress
regime by hard-coded **PC2** while `safe_haven_test.py` used the data-driven axis (PC3).
The two reported **opposite signs for the same statistic**: −0.209 vs +0.167, on 1,816 vs
1,084 stress days. The bug erred in the **flattering** direction. Corrected, they agree to
three decimals and the documented null is corroborated rather than contradicted.
**Lesson: when a hazard is fixed in one script, grep for every other consumer in the same
commit.**

### Problem 1 ENGINE (macro analog) — REVISED DOWN
835 rebalances, 2010-01-04 → 2026-08-11:

| universe | spread/reb | ~/yr | Sharpe | hit | payoff | p |
|---|---|---|---|---|---|---|
| all 47 | +0.292% | ~15.2% | **0.51** | 50.3% | 1.04 | 0.0010 |
| long-history (35, ≥8y) | +0.129% | ~6.7% | **0.25** | 49.7% | 1.01 | 0.0380 |

Was 0.57 / 0.40 with p 0.0010 / 0.0040. **The survivorship-bias block is what degraded**
— it exists to answer "is this just recent AI-boom tickers?", and the honest answer is now
that the edge weakens substantially without them and clears 5% only just. The claim
"survives dropping recent-inception tickers → not just an AI-boom artifact" is **retired**.

Old figures were flattered by `_forward` compounding across holiday NaNs that `skipna`
dropped — a "5-day" return was sometimes 4 sessions of movement, understating volatility.
**Lower and correct beats higher and wrong.**

**Ensemble framing:** "a ~0.4 Sharpe ingredient" describes neither block and is retired.
Standalone is **0.25–0.51 depending on universe**, low end being the
survivorship-controlled universe. The ingredient is **thinner than previously recorded**,
which makes the ensemble case more load-bearing, not less.

### Model grid — RANKING FLIPPED, a prior claim retired

Re-run on the session basis, all three scored at their **frozen** specs:

| model | pre-migration | session basis |
|---|---|---|
| model_1_baseline (5d, level) | 0.21 | **0.40** |
| model_2_horizon_trend (10d, trend) | 0.39 | **0.36** |
| model_3_overfit (20d, trend, σ1.0) | 0.50 | **0.44** |

**model_1 now beats model_2.** The documented claim — *"model_2 is the principled
amendment… nearly doubled the baseline Sharpe and became significant. Hypothesis
confirmed"* — is **overturned** and retired.

Mechanism: the old bug dropped holiday NaNs from forward windows, so a 5-day horizon was
sometimes short by 20%, a 10-day by 10%, a 20-day by 5%. **The shortest horizon was most
contaminated and gained most from the fix.** That is what one would predict, not a
coincidence.

**A confound that invalidated the comparison in both directions:** model_1 and model_2
differ in **horizon AND sim_mode simultaneously** (5d/level vs 10d/trend). Neither the old
nor the new comparison isolates the trend effect. The grid contains same-horizon
level-vs-trend cells; that specific comparison must be run before any claim about
trend-aware similarity.

**An unexpected live demonstration.** `model_3_overfit`'s pre-registered hypothesis was
that its in-sample lead shrinks or inverts *live*. It has now shrunk **in-sample**, on a
corrected basis (0.50 → 0.44 while model_1 rose 0.21 → 0.40) — the cherry-picked winner
degraded under a methodology fix unrelated to model selection. A cleaner demonstration of
in-sample fragility than the live test will provide, and it arrived early.

**`model_grid.py` was re-deriving `model_3_overfit`** as whatever currently won the grid
(15d/σ2.0 on this basis) rather than reading the frozen 20d/σ1.0 from `models.yaml` — so
the written record contradicted both the frozen spec and the live harness. Fixed: all
three specs now come from `models.yaml`, parsed identically to `forward_log.load_models`;
the current winner is reported as a labelled diagnostic only; `--out` prevents re-runs
overwriting the record.

**Pre-registration evidence:** `config/models.yaml` first committed in **ce18d34,
2026-08-17 14:24:09 +0800** — before the valid forward log began 2026-08-18. Original grid
preserved at `docs/model_grid_results_prereg_2026-08.md`; session re-run at
`docs/model_grid_results_session_basis.md`.

### Problem 2 (rotation chain) — NULL confirmed, and the test is now known to be too weak

Re-run unchanged on the session basis (immune via `dropna`): discovered order
ASML→TSM→MU→INTC→NVDA, Spearman **−0.100**, permutation **p=0.605**, mean sub-period
agreement **−0.250**.

| period | order |
|---|---|
| 1999–2005 | MU → INTC → TSM → ASML → NVDA |
| 2005–2012 | INTC → NVDA → TSM → ASML → MU |
| 2012–2019 | ASML → TSM → INTC → NVDA → MU |
| 2019–2026 | ASML → NVDA → MU → TSM → INTC |

**Three problems with the existing test, all found 2026-08-20:**

1. **"Anti-stable" is not supported.** −0.250 is the mean of 6 pairwise Spearmans on
   **n=5 rankings**; random permutations of 5 items have SD ≈ 0.5, so the statistic's
   standard error is ~0.25 and the observed value sits about **one SE from zero**. There
   is **no permutation test on it anywhere in the script**. The defensible claim is
   *"orders across sub-periods are indistinguishable from random reshuffling"* — not
   systematic reversal. **Correcting this; "anti-stable" is retired.**
2. **The sub-period test has look-ahead.** `residualize()` fits ONE OLS beta over the
   full 1999–2026 sample; `main()` then slices those residuals per sub-period. So
   1999–2005 residuals were built with betas estimated through 2026 — in a test whose
   entire purpose is asking whether structure is stable *over time*. ASML's beta to the
   complex pre- and post-EUV is certainly not constant. **Fix: residualise within each
   sub-period.**
3. **The permutation tests the wrong thing.** `[2]` asks whether the discovered order
   matches *the thesis* beyond chance. A perfectly real chain with a different order
   still returns p≈0.6. Existence is tested only by `[3]`, which is the statistic with no
   significance test. **The null currently rests on the weaker leg.**

**The engine cannot detect the kind of chain most likely to exist.** `net_lead` averages
correlation across lags 1..K with K=10 fixed, unconditionally, assuming one order:
- **Variable speed** — a 2-day cascade contributes at k=1,2 and noise at k=3..10, an 80%
  dilution. Widening K makes this *worse*, not better. Needed: a **per-lag profile**, with
  peak lag reported as an episode property rather than assumed.
- **Interruptions** — expected to be the common case. A cascade that stalls two weeks
  mid-episode has real propagation averaged with dead time. Needs a **rupture/censoring
  rule**, which requires event detection.
- **Variable order** — averaging different per-episode orders yields ~0. Needs a
  **distribution of orders**, not one averaged order. And "predict the next link" then
  requires knowing which order *this* episode follows — a harder, possibly underpowered
  problem.

**Therefore the current output cannot distinguish "no chain exists" from "chains exist
with episode-varying speed and order."** Both produce this result. Earlier framing that
the sub-period table was strong evidence against the phenomenon was **overconfident**.

**Literature check (2026-08-19).** Molchanov & Stangl relaxed any assumed sequence,
ignored cycle stages, and tested cross-sector predictability at lags of 1–24 months —
2,640 t-statistics — finding scant evidence of sector rotation; robust across groupings
and factor models. Jacobsen, Stangl & Visaltanachoti gave an investor *perfect foresight*
of cycle stages and still got at best 2.3%/yr, dissipating in realistic settings.
**Our null replicates published findings** — a stronger position than a lone null, and a
warning that searching for a better *chain* unconditionally has poor prospects. **The
differentiated angle is the conditioning, which nobody in that literature applied.**

**Definition of "lead" for the write-up.** *A leads B if, after residualising each name
against the equal-weight mean of the other four (removing shared semiconductor beta), the
correlation between A's residual at t and B's residual at t+k, averaged over k = 1…10
trading days, exceeds the same quantity with roles reversed; net-lead sums that asymmetry
across all partners.* It measures average statistical precedence in **deviations from the
sector**, across the whole sample. It is **not** price level, **not** direction (a led
decline scores identically to a led rally), **not** per-episode, and **not** causal.

---

## GDELT event layer — query recovered, two open findings

### Reproducibility gap CLOSED
Nothing in the repo produced `processed/gdelt_2024_clean.csv`; it came from a manual
BigQuery console run exported to `.xlsx` and cleaned by hand. The query text survived only
inside the xlsx export metadata. Now:
- **`src/gdelt_query.py`** regenerates the SQL from `config/gdelt_theme_mapping.yaml` with
  parameterised dates. **Verified: generated SQL matches the recovered query exactly.**
- **`src/gdelt_ingest.py`** scripts xlsx → CSV. **Verified: reproduces
  `gdelt_2024_clean.csv` identically.**
- Exports copied to `data_provenance/gdelt/`. `raw/` is gitignored as "regenerable",
  which was true for FRED and yfinance and **false** for these — without the query they
  could not be regenerated at all. (`*.xlsx` is itself gitignored; they required
  `git add -f`.)
- Source: `gdelt-bq.gdeltv2.gkg_partitioned`, V2Themes exploded via UNNEST/SPLIT with the
  character offset stripped, grouped daily.

### FINDING 1 — config and data disagree on what "stress" means
`gdelt_theme_mapping.yaml` documents `market_stress` with **eight** themes. The data
actually used has **six**, omitting `EPU_ECONOMY_HISTORIC` and `EPU_ECONOMY` — confirmed
by exact match against `raw/UNNEST EPU_ECO one-year.xlsx`. The two differ **~5.5×** in
`stress_count` (mean 63,712 narrow vs 310,189 broad). **Every alignment result to date
used the narrow definition while the config described the broad one.** Intent
undocumented; the narrow export is timestamped later (6:21 PM vs 6:07 PM), consistent with
a deliberate refinement, but that is inference, not a record.

### FINDING 2 — the alignment result is DEFINITION-DEPENDENT

Narrow (as used): n=4 **p=0.261**, 0/7 windows; n=5 marginal 0.079.
Broad (same 2024 data, wider stress themes):

| n | share ratio | p | z_in − z_out | p |
|---|---|---|---|---|
| 3 | 1.026 | **0.046** | +0.011 | 0.428 |
| 4 | **1.035** | **0.015** | −0.029 | 0.581 |
| 5 | 1.024 | 0.089 | +0.061 | 0.218 |

Window sweep on z-diff: still **0/7 at every n**.

**Prediction stated before running was that the null would hold. It held for the z-score
measure and broke for share ratio.** Recorded as another wrong prior.

*Why the two measures disagree, mechanically:* `z_in − z_out` uses a **20-day rolling**
baseline while regime runs average ~400 days, so inside a long stress regime the baseline
drifts up to meet the level and the z-score reads ≈0. The de-baselining that removes news
volume also removes the regime-length signal — it is structurally near-blind to persistent
regimes. `share ratio` compares against the global mean and survives that; the
circular-rotation permutation preserves autocorrelation, so p=0.015 is not a clustering
artifact. **This argues share ratio is the more appropriate statistic, not that broad is
the right definition.**

*Three cautions:* (a) the direction now favours **n=4** (strongest at p=0.015, with n=5
weakest) — partially restoring a third leg, but one that appears under only one theme
definition, so **conditional, not corroborated**; (b) **multiple comparisons** — six tests
in that table, twenty-one more in the sweep; (c) broad `stress_count` averages **310,189
against 335,832 total documents** — nearly one hit per document, so `EPU_ECONOMY` appears
to tag most economic coverage and the "broad stress measure" may be closer to *"the
economy is in the news"* than to stress. That is a substantive argument for narrow,
independent of any p-value.

**The choice of canonical definition must be made on definitional grounds and stated
before looking again.** Choosing broad *because* it produced significance is exactly the
failure this project's discipline exists to prevent. Current read: narrow is more
defensible on the 310k/336k grounds.

**PRE-REGISTERED TEST for the extension:** *under the extended 2025–2026 sample, does
broad-definition share ratio at n=4 remain significant?* If yes, it is real; if it
evaporates, it was a 2024 small-sample artifact. 2024 alone gives 252 overlap days and
~30 stress days — far too few to adjudicate.

---

## Forward test — LIVE on the session basis

Three models frozen in `config/models.yaml` (**ce18d34, 2026-08-17 14:24:09 +0800**),
before any live data. Wipe #1 (2026-08-17: stale cache + empty bars) and wipe #2
(2026-08-18: deliberate, at 0 matured rows, because the ledger held picks computed on the
`bdate_range` basis while the scores parquet had moved to sessions).

**Live rows:** signal **2026-08-18** (45/47 coverage), entry **2026-08-19**, all three in
regime 1. 3 rows, 0 matured, 3 pending, 0 short_window.

**Exposure note.** Model 1 shorts SPCX (43 days of history); model 2 shorts SPCX and FLY
(256); all three go long DRAM (92). The live models actively trade **recent-inception
tickers — the exact group whose removal costs 40% of the long-history Sharpe**.
Pre-registered behaviour, not a bug, but if live results come in strong the first
follow-up must be whether that is the newcomers again.

**Window integrity — implemented (7352dd1), still unexercised.** A row scores `matured`
only if every session of its H-day window has a return for every picked asset; otherwise
`short_window` with its realised session count, excluded from the headline summary.
Entry dates and picks frozen at log time, never reassigned. Fixed alongside: horizons
counted index rows not sessions; `skipna=True` silently shortening windows; maturation
firing past usable data; `entry_date` re-derived each run; `--dry-run` writing on skip
days.

**2026-08-17 vendor gap — CLOSED.** Only Close/Adj Close were NaN (OHLV present).
**It healed at ~48 hours**, correcting this document's earlier claim that it had not
self-healed. Correct statement: *Yahoo can leave a Close missing for up to two days; the
panel heals retroactively via `--force`, but a forward-test entry for a skipped day stays
skipped.* No permanent panel gap.

### Daily command
```bash
cd ~/Projects/regime-aware-signal && source .venv/bin/activate
python -m src.forward_log
```
Once daily after ~05:00 SGT. Skips if no new US close. Then commit
`docs/forward_scoreboard.md` — the git timestamp is what makes entries pre-registered.
**Automate via cron if the ritual becomes a burden; do not stop it.** It is the only
evidence in the project not contaminated by in-sample selection, and `forward_log` is the
shared harness the other engines will plug into.

---

## Open threads (ordered)

1. **GDELT extension 2025 → 2026.** `python -m src.gdelt_query --start 2025-01-01 --end
   2026-08-19 --variant narrow` (and `--variant broad`), run in BigQuery, export, ingest.
   Answers the pre-registered test above and feeds the live forward test.
   **Then extend back toward the ~2015 tagged floor** — the forward window is essentially
   one macro regime (Regime 1), so a positive drift result there alone could not be
   distinguished from a regime-conditional one. This project has already been bitten by
   exactly that (alignment significant on 2018+, null on 2006+). 2015–16 China, 2018Q4,
   COVID and the 2022 rate shock supply the regime variety. **Watch the control group:**
   if event density is very high, matched non-event days become scarce and the test loses
   power from the other direction.

2. **Fix `chain_rotation.py`** — residualise within sub-periods (removes look-ahead); add
   a permutation null for the sub-period agreement statistic; add an existence test
   distinct from the thesis-match test.

3. **Event engine Stage 1 — drift-existence test.** GDELT event days; returns at
   1/5/10/20d entered next-open; permutation-tested vs matched non-event days.

4. **Problem 2 Stage 2** — conditional lead-lag within episodes, built **multi-scale**
   (per-lag profile), **per-episode** (distribution of orders), with a **rupture rule**.
   Blocks on (3).

5. **Same-horizon level-vs-trend comparison** from the existing grid, to isolate the trend
   effect that model_1-vs-model_2 never did.

6. **Ensemble combiner** (position-space, Sharpe-weighted). **The actual open question for
   the product** — engine correlation has never been measured.

7. **The n=4 generalization gap (+5.130) is a live concern.** The regime model transfers
   poorly to 2025–26 — the exact period the forward test runs in. **Test:** check which
   regimes 2025+ rows occupy and whether they sit in a low-density corner of the training
   distribution.

8. **Doc/code accuracy fixes queued:**
   - `regime_classifier.py` console note still claims n=4 stands on "seed stability,
     run-length persistence, and cluster separation" — two of three no longer true.
   - `regime_event_alignment_normalized.py` prints a VERDICT the next script's permutation
     test contradicts; written before the permutation existed.
   - `chain_rotation.py` READING says "even if the full-sample order matches the thesis" —
     it does not (Spearman −0.100).
   - `PIPELINE.md` §4 omits the required `--gdelt` argument on four scripts.
   - `PIPELINE.md` §1 has no step producing the GDELT panel — now fixable by documenting
     `gdelt_query` → BigQuery → `gdelt_ingest`.
   - `briefing.md`'s `docs/*.md` glob silently skips
     `docs/Regime_Aware_Framework_Methodology_Log.pdf`.

9. **Policy on documented figures.** Numbers drift as the panel grows. Freeze with an
   as-of date, or re-run at fixed checkpoints.

10. **Data amendments:** company/entity-level events. Note `gdelt_theme_mapping.yaml`
    already records that GDELT has **no clean semiconductor/defense/space/cyber theme**,
    that entity matching must be **exact** (`LIKE '%INTEL%'` matches "intelligence" and
    floods the signal), and that SEC EDGAR 8-K is the cleaner source for company-specific
    material events.

11. **Problem 3:** LLM/RAG scenario layer. **12. Streamlit MVP**, then integration.

### Closed 2026-08-18/20
- Window integrity (7352dd1) · n=4 pin (5ec014e) · stress-axis port · `_forward` horizon
  bug (resolved by the migration) · 08-17 vendor gap · `model_grid` re-deriving model_3
  (7c1da76) · GDELT query recovery + scripted ingest (303bdae)

---

## Working principles

- Every claim about project data must come from data actually run; hypotheses labelled as
  hypotheses with the test proposed.
- Null results are findings. **Check whether the null is definition-dependent** before
  calling it clean.
- Permutation tests over raw p-values; check robustness across specifications.
- Judge signals by **risk-adjusted return**, never hit-rate alone.
- Few, principled hypotheses beat large grids — and a grid's winner is labelled a
  cherry-pick and forward-tested.
- Extend data by **removing redundancy, never by imputation** — including redundancy
  entering through the *index*.
- Identify axes by **economic meaning, never by index** — and when that hazard is fixed in
  one script, **grep for every other consumer in the same commit**.
- **Re-validate rather than assume** when the substrate changes — and **ask which results
  were exposed**, since one that survives may never have been at risk.
- **Correct the record**, including corrections to this document's own earlier statements.
- **Verify before asserting in a commit message.**
- **State the prediction before running the check**, and **record priors that turn out
  wrong** — two so far: n=5 fragility (an artifact) and the GDELT null holding under a
  broader definition (it did not).
- **Register falsification conditions before re-validating.**
- **Decide definitions on definitional grounds, before looking at the p-value they
  produce.**
- **A measured engine is finished being measured.** What strengthens the system is engine
  *independence*, not a better version of a measured component.
- **Know what a test cannot see.** A null from an instrument blind to the phenomenon is
  not evidence of absence.
- **Take the correct long-term fix over the contained one** when they conflict.
- **Fail loud rather than log something plausible.**
- Operational rules affecting the forward test are pre-registered while affected rows are
  still pending.
- **Committed is not the same as written**, and gitignore rules apply to files you assume
  are safe. Verify with `git ls-files`, not `ls`.
- The **repo is the source of truth**, not model memory.
