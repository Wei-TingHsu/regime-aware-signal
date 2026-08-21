# PROJECT STATE — briefing document

*Upload this file (or the `briefing.md` bundle) at the start of a new conversation to
resume without re-explaining. Last updated: 2026-08-20 (evening SGT). Keep it updated
after each workstream closes.*

> ## STATUS
>
> NYSE-session migration: **COMPLETE**. Forward test: **LIVE** on the new basis.
> GDELT panel: **EXTENDED** 2024 → 2024-2026 (366 → 944 days), both theme variants.
> Two silent-failure bugs found and fixed today (partial-bar signal; hard-coded 2024
> window). Next: the event-engine **drift-existence test** — still unrun.

---

## How this project is worked — read before starting a session

**Session start.** Regenerate the bundle and upload it:
```bash
for f in docs/*.md; do echo "===== $f ====="; cat "$f"; echo; done > ~/Downloads/briefing.md
```
It is a snapshot, not a live link — regenerate every time. The repo is the source of
truth; model memory is not.

**File handoff.** Claude has no access to this machine. The loop is: Claude names the file
it needs → Steven uploads it → Claude returns the **complete patched file** (never a diff)
→ Steven downloads, `cp`s it into place, and commits. Always `ls -lt ~/Downloads | head`
first: a repeat download saves as `name-1.py` and the `cp` then silently installs the
stale version.

**Verify before trusting, always.** Every fix gets a check that would fail if the fix did
not work, and the check is stated **before** it runs. Refactors get a
behaviour-preserving test on known input — the 2024 file reproducing every cell exactly is
what licensed the `regime_event` refactor. Two bugs this week were caught only by such
checks, and one (the hard-coded 2024 window) was invisible except as an exact match to a
result still in view.

**Commit discipline.** One logical change per commit, with the reasoning and the
verification in the message — the commit log is the methodology record, not a changelog.
Never bundle a correctness fix with a documentation fix. Commit and **push** before
stopping; an uncommitted finding is one laptop crash from gone.

**Session end.** Update this document and push it, then regenerate `briefing.md` for next
time. Say *"update PROJECT_STATE before we finish"* at the start of a session so it is a
closing ritual rather than something forgotten mid-flow.

**Daily, regardless of what else is happening:**
```bash
cd ~/Projects/regime-aware-signal && source .venv/bin/activate
python -m src.forward_log
git add docs/forward_scoreboard.md && git commit -m "forward test: daily log $(date +%F)" && git push
```
Skipped days stay skipped. **Never retro-fill.**

**What Claude is asked to do.** Push back rather than agree; name what a test cannot see;
say when a result is exploratory rather than confirmatory; and never present a hypothesis
as a result. Claimed results must come from data actually run.

---

## What this project is

**Regime-Aware Cross-Asset Signal Framework.** Three research problems + a product
vision: engines that (a) read the macro state and issue directional calls, (b) detect
event-triggered rotation cascades, (c) narrate scenarios via an LLM layer. The
47-asset universe is an **MVP baseline and must stay expandable** — never hard-code 47.

**Product vision.** Rotation is **event-initiated**, but the event names the **focus SET,
not the ORDER**. GDELT/text detects the trigger and the set; price statistics determine
sequence and timing **within** episodes.

**Where the three engines stand.**
1. **Macro engine — measured and thin.** Sharpe **0.25–0.51 depending on universe**.
   *Done being measured.* Re-tuning until the number improves is the overfitting failure
   the working principles exist to prevent.
2. **Event engine — its real test has not happened.** Drift-existence is unrun. The data
   for it now exists (944 days, both variants).
3. **Rotation chain — its first test asked the wrong question**, and the current engine
   is structurally unable to detect the kind of chain most likely to exist.

The system thesis is error cancellation across engines with different data, horizons and
failure modes. **That correlation has never been measured**, so "each engine is modest"
and "the system does not work" remain different claims until the ensemble step runs. If
drift-existence is null on an adequately powered sample *and* conditional rotation is
null, the product has no foundation and the correct response is to say so. Three
documented nulls with rigorous method remain a legitimate capstone — a weaker *business*,
not a failed *project*.

**Architecture decision (2026-08-19): CONDITIONAL MERGE of the event and rotation
engines.** Interruptions inside cascades are expected to be common, and detecting them
requires event detection — the same detector that finds a trigger finds a rupture. So the
natural form is one engine: GDELT segments time into episodes (start on trigger, censor on
rupture) and chain logic runs inside them. **Merge only if and when Stage 1
drift-existence is positive.** Consequences to hold in view: merging leaves **two**
engines, reducing the diversification the position-space combiner assumes, and it
concentrates risk since a null on event detection kills both lines at once.

---

## The calendar migration (2026-08-18) — complete

`build_panel` used `pd.bdate_range` (Mon–Fri **including market holidays**). Those rows
carried no asset returns but had macro values forward-filled onto them, entering the PCA
and GMM as near-duplicates — manufactured data.

| 2006+ panel | before | after |
|---|---|---|
| rows | 5,382 | **5,188** |
| rows with zero asset coverage | ~196 | **2** |

Not free: ≤46 rows per series carried genuinely new macro values (Good Fridays, Hurricane
Sandy 2012). Still correct — a macro state with no session cannot be traded. Side effect:
`analog_core._forward` rolls over index rows, so with a session index it is now
session-counting; that horizon bug is resolved with no code change.

**Which results were exposed, and which were immune.** Problem 1 and `chain_rotation`
both `dropna` before computing, so holiday rows were *already* discarded. Their stability
is **not** evidence the migration was inconsequential; it is evidence they were never at
risk. The backtest had no such protection, and it moved. **Ask which results were exposed,
not just which survived.**

### n=4 re-earned — hypothesis NOT falsified, case narrowed

| criterion | old panel | session panel | verdict |
|---|---|---|---|
| seed ARI n=4 | 1.000 (n=5 fragile 0.774) | 1.000 — n=3, n=5 also 1.000 | **leg lost** |
| silhouette | peaks n=4 | n=4 0.4689 vs n=2 0.4678 | **tie** |
| run-length median | 52.5d | **51.0d**, 12 runs (others 3–7d) | **holds decisively** |
| generalization gap | n=4 +4.89 | **n=4 +5.130** (n=3 +0.507) | **against n=4** |

Direct n=2 probe: median run 4.0 vs 51.0; gap −0.080 vs +5.130. Pre-registered rule
required n=2 to win **both**; it won one. **n=4 stands**, on run-length persistence plus
an economic argument (PC1 rates 52.3% + PC2 money/dollar 27.2% = 79.6%; a 2-regime split
collapses two distinct axes into one).

**A registered prior that was wrong:** removing duplicates was predicted to *reduce*
persistence and leave ARI intact. Persistence barely moved; instead the duplicates had
been *destabilising n=5*. **"n=5 fragile at 0.774" was partly an artifact** and is struck.

### PCA on the session panel (5,188 × 8, from 2006-01-03)
PC1 52.3% DGS2 (+0.984) · PC2 27.2% M2SL (+0.813) · PC3 12.8% VIXCLS (+0.964) ·
PC4 5.0% T10Y2Y (weak) · PC5 1.9% DTWEXBGS (weak). Top 3 = 92.3%. No renumbering.

---

## Current status by workstream

### Regime engine — DONE
n=4 pinned in `config.yaml`. Regime structure barely moved across the migration (each
regime −3–4%, macro character unchanged to 2dp). Classifier and verifier agree exactly:
12 runs, median 51.0, mean 432.3. Current regime: **Regime 1** (tight policy, high 10Y,
strong USD).

| regime | days | mean run | VIX | 10Y | USD |
|---|---|---|---|---|---|
| 0 | 1735 | 434 | 22.5 | 2.80% | 92.7 |
| 1 | 984 | 492 | 18.0 | 4.16% | 121.8 |
| 2 | 516 | 258 | 15.4 | 4.69% | 96.0 |
| 3 | 1953 | 488 | 18.5 | 2.02% | 113.7 |

### Problem 1 (safe-haven) — DONE, clean NULL, basis-independent
Liquidity gap **+0.011, p 0.488** (581 stress days / 5,448); macro gap **+0.167,
p 0.0814** (1,084 / 5,186). Robustness cross-check identical to 3dp across all eight
cells; primary non-significant everywhere. Liquidity crisis lift **×2.99**.

*Phrasing correction:* three of four primary raw cells are now mildly negative — noise
around zero. "If anything it co-moves slightly more" is carried by the **cross-check**
block, not the primary one.

**Stress-axis bug (fixed 2026-08-18).** `safe_haven_robustness.py` used hard-coded **PC2**
while `safe_haven_test.py` used the data-driven axis (PC3). The two reported **opposite
signs for the same statistic**: −0.209 vs +0.167, on 1,816 vs 1,084 stress days. The bug
erred in the **flattering** direction. Corrected, they agree to three decimals.
**Lesson: when a hazard is fixed in one script, grep for every other consumer in the same
commit.**

### Problem 1 ENGINE (macro analog) — REVISED DOWN
835 rebalances, 2010-01-04 → 2026-08-11:

| universe | spread/reb | ~/yr | Sharpe | hit | payoff | p |
|---|---|---|---|---|---|---|
| all 47 | +0.292% | ~15.2% | **0.51** | 50.3% | 1.04 | 0.0010 |
| long-history (35, ≥8y) | +0.129% | ~6.7% | **0.25** | 49.7% | 1.01 | 0.0380 |

Was 0.57 / 0.40 with p 0.0010 / 0.0040. **The survivorship-bias block is what degraded.**
The claim "survives dropping recent-inception tickers → not just an AI-boom artifact" is
**retired**. Old figures were flattered by `_forward` compounding across holiday NaNs that
`skipna` dropped. **Lower and correct beats higher and wrong.**

**Ensemble framing:** "a ~0.4 Sharpe ingredient" describes neither block and is retired.
Standalone is **0.25–0.51 depending on universe**, low end being the
survivorship-controlled universe.

### Model grid — RANKING FLIPPED, a prior claim retired

| model | pre-migration | session basis |
|---|---|---|
| model_1_baseline (5d, level) | 0.21 | **0.40** |
| model_2_horizon_trend (10d, trend) | 0.39 | **0.36** |
| model_3_overfit (20d, trend, σ1.0) | 0.50 | **0.44** |

**model_1 now beats model_2.** The claim that model_2's trend-aware amendment "nearly
doubled the baseline Sharpe… hypothesis confirmed" is **overturned and retired**.
Mechanism: the holiday-NaN bug shortened a 5-day horizon by 20% and a 20-day by 5%, so the
shortest horizon was most contaminated and gained most from the fix.

**A confound invalidating the comparison in both directions:** model_1 and model_2 differ
in **horizon AND sim_mode simultaneously**. Neither comparison isolates the trend effect.
The grid contains same-horizon level-vs-trend cells; run those before any claim.

**An unexpected live demonstration.** model_3's pre-registered hypothesis was that its lead
shrinks or inverts *live*. It shrank **in-sample** under a methodology fix unrelated to
model selection (0.50 → 0.44 while model_1 rose) — a cleaner demonstration of in-sample
fragility than the live test will provide, arriving early.

`model_grid.py` was **re-deriving** model_3 as the current grid winner (15d/σ2.0) rather
than reading the frozen 20d/σ1.0. Fixed: all specs now come from `models.yaml`; the
current winner is a labelled diagnostic only; `--out` prevents overwriting the record.
**Pre-registration evidence: `config/models.yaml` first committed ce18d34, 2026-08-17
14:24:09 +0800**, before the valid log began 2026-08-18. Original grid preserved at
`docs/model_grid_results_prereg_2026-08.md`.

### Problem 2 (rotation chain) — NULL confirmed, and the test is known to be too weak

Discovered order ASML→TSM→MU→INTC→NVDA, Spearman **−0.100**, permutation **p=0.605**,
mean sub-period agreement **−0.250**.

| period | order |
|---|---|
| 1999–2005 | MU → INTC → TSM → ASML → NVDA |
| 2005–2012 | INTC → NVDA → TSM → ASML → MU |
| 2012–2019 | ASML → TSM → INTC → NVDA → MU |
| 2019–2026 | ASML → NVDA → MU → TSM → INTC |

**Three problems with the existing test:**
1. **"Anti-stable" is not supported.** −0.250 is a mean of 6 pairwise Spearmans on **n=5
   rankings**; random permutations of 5 items have SD ≈ 0.5, so the statistic's standard
   error is ~0.25 and the observed value is about **one SE from zero**. There is **no
   permutation test on it**. Defensible claim: *"orders are indistinguishable from random
   reshuffling."* **"Anti-stable" is retired.**
2. **The sub-period test has look-ahead.** `residualize()` fits ONE beta over 1999–2026;
   `main()` slices those residuals per sub-period. So 1999–2005 residuals used betas
   estimated through 2026 — in a test about stability over time. **Fix: residualise within
   each sub-period.**
3. **The permutation tests the wrong thing.** It asks whether the discovered order matches
   *the thesis*. A real chain with a different order still returns p≈0.6. Existence is
   tested only by the statistic with no significance test.

**The engine cannot detect the likely form of chain.** `net_lead` averages lags 1..K with
K=10 fixed, unconditionally, assuming one order:
- **Variable speed** — a 2-day cascade contributes at k=1,2 and noise at k=3..10, an 80%
  dilution. Widening K makes this *worse*. Needed: a **per-lag profile**, peak lag reported
  as an episode property.
- **Interruptions** — expected to be the common case. Needs a **rupture/censoring rule**,
  which requires event detection.
- **Variable order** — averaging different per-episode orders yields ~0. Needs a
  **distribution of orders**.

**So the output cannot distinguish "no chain exists" from "chains exist with
episode-varying speed and order."** Earlier framing that the sub-period table was strong
evidence against the phenomenon was **overconfident**.

**Literature check.** Molchanov & Stangl tested cross-sector predictability at lags of
1–24 months — 2,640 t-statistics — finding scant evidence of sector rotation, robust across
groupings and factor models. Jacobsen, Stangl & Visaltanachoti gave perfect foresight of
cycle stages and still got at best 2.3%/yr. **Our null replicates published findings** —
and warns that searching for a better *chain* unconditionally has poor prospects. **The
differentiated angle is the conditioning.**

**Definition of "lead."** *A leads B if, after residualising each name against the
equal-weight mean of the other four, the correlation between A's residual at t and B's
residual at t+k, averaged over k = 1…10 trading days, exceeds the same with roles
reversed.* It measures average statistical precedence in **deviations from the sector**.
**Not** price level, **not** direction, **not** per-episode, **not** causal.

---

## GDELT event layer

### Reproducibility gap CLOSED (2026-08-20)
Nothing in the repo produced `gdelt_2024_clean.csv`; it came from a manual BigQuery console
run exported to `.xlsx` and cleaned by hand, with the query text surviving only in the xlsx
metadata. Now: **`src/gdelt_query.py`** regenerates the SQL from
`config/gdelt_theme_mapping.yaml` with parameterised dates (verified: matches the recovered
query exactly); **`src/gdelt_ingest.py`** scripts xlsx → CSV (verified: reproduces the 2024
file identically) and accepts multiple exports. Console exports live in
`data_provenance/gdelt/` — `raw/` is gitignored as "regenerable", which was **false** for
these, and `*.xlsx` is itself ignored so they needed `git add -f`.

### Narrow vs broad — the definitions
`gdelt_theme_mapping.yaml` documents `market_stress` with **eight** themes; the data
actually used has **six**, omitting `EPU_ECONOMY_HISTORIC` and `EPU_ECONOMY`. The two
differ **~5×** in `stress_count`.

**Narrow is canonical, on definitional grounds decided independently of any p-value:**
broad `stress_count` averages **310,189 against 335,832 total documents** — close to one
hit per document — so `EPU_ECONOMY` tags most economic coverage, and "broad stress" is
closer to *"the economy is in the news"* than to stress.

### The extension: 366 → 944 days

Four year-split BigQuery pulls (the console silently caps a result-pane export at **500
rows** — the 2024 pull at 366 was under it, which is why this never surfaced before).
**2025 has a 17-day GDELT outage, 2025-06-15 → 2025-07-01**, identical in both variants, so
it is upstream of the query. All 11 of those that are trading sessions fall in **regime 1**
— i.e. the outage removes only non-stress days and does not touch the scarce stress-day
count. 2024 had complete coverage; **the samples differ in completeness** and a reader
comparing them should know.

### RESULT — the pre-registered question is answered: NO

**Registered before running:** *does broad-definition share ratio at n=4 survive on the
extended sample?* On 2024 it was p=0.015.

| sample (overlap) | narrow n=4 share | broad n=4 share |
|---|---|---|
| 2024 (252d) | 1.029, p 0.205 | 1.035, **p 0.015** |
| combined (648d) | 1.157, **p 0.038** | 1.080, p 0.098 |
| 2025–26 (396d) | **1.433, p 0.000** | 1.186, **p 0.007** |

**It weakened to p=0.098. Substantially a small-sample artifact.**

**But the definition-dependence REVERSED.** On 2024 broad was stronger; on the extension
narrow is stronger. A definition that were genuinely right should not flip like that —
what flipped is noise in a 252-day window.

**The real structure is temporal, not definitional.** 2025–26 shows significance at n=4
and n=5 under *both* definitions; 2024 shows almost nothing under either.

**Three cautions, or this gets over-read:**
1. **Not pre-registered.** "Narrow n=4 at p=0.000" is **exploratory**. The registered test
   was about broad, and broad failed. Recording this as confirmation would be the
   reverse-engineering the working principles forbid. It must be tested on data it was not
   discovered in before it counts.
2. **n=5 is significant too**, sometimes more so (combined: n=5 p=0.029 vs n=4 p=0.038).
   This does **not** discriminate the regime count.
3. **2025–26 is where the regime model generalizes worst** (+5.130 gap). An alignment
   result concentrated exactly there may reflect regimes being *unstable* there rather
   than *accurate*.

`z_in − z_out` stays null almost everywhere — consistent with its **20-day rolling
baseline** being structurally near-blind to ~400-day regime runs.

### Two silent-failure bugs found 2026-08-20

**(a) Hard-coded 2024 window.** `load_scores_2024()` in `regime_event_alignment.py`
restricted PCA scores to 2024, and all four `regime_event_*` scripts imported it. Passing
an extended panel returned **the 2024 result unchanged** — the "2024–2026" run reproduced
the 2024 numbers to three decimals in every cell. Caught only because the 2025–26 run
crashed (`ValueError: low >= high`, zero overlap) and the 2024 numbers had been kept
alongside for comparison. **Had the crash not happened, a false confirmation of the
pre-registered test would have been recorded.** Replaced with `load_scores_range(start,
end)`; every script derives the window from the GDELT file and **prints the overlap**.
Verified behaviour-preserving: the 2024 file reproduces every cell exactly.

**(b) Live partial bar accepted as signal.** At 21:32 SGT (09:32 ET) the harness took
2026-08-20 as its signal — **two minutes into the session**. 41/47 assets had printed, which
clears the ≥40% coverage guard, because a live bar is not an empty bar and coverage cannot
tell them apart. It also skipped 2026-08-19's completed close entirely. Three invalid rows
were deleted (0 matured, so no cost). Fixed: `market_calendar.last_completed_session()`
checks the actual NYSE closing bell (early closes respected) and `forward_log` excludes any
later bar, saying so.

---

## Forward test — LIVE

Three models frozen in `config/models.yaml` (**ce18d34, 2026-08-17 14:24:09 +0800**).
Wipe #1 (2026-08-17: stale cache + empty bars), wipe #2 (2026-08-18: deliberate, basis
change at 0 matured), plus the 3 partial-bar rows deleted 2026-08-20.

**Current (2026-08-21):** signals 2026-08-18, 08-19 and 08-20 (entries 08-19, 08-20,
08-21). **9 rows, 0 matured, 9 pending, 0 short_window.**

**First regime transition of the live test.** 08-18 and 08-19 signalled in **regime 1**
(tight policy, high 10Y, strong USD); **08-20 signalled in regime 0 — the STRESSED regime**
(VIX 22.5, easy policy, steep curve, weak USD), and the picks shifted accordingly. Watch
whether it persists: regime 0 has a 434-day mean run, so a one-day flip would be unusual,
but the live period is also where the model generalizes worst (+5.130 gap, thread 7).
First maturities: model_1 (H=5) around 2026-08-26; model_3 (H=20) around mid-September.

**Exposure note.** The live models actively trade **recent-inception tickers** (SPCX 43d,
FLY 256d, DRAM 92d) — the exact group whose removal costs 40% of the long-history Sharpe.
Pre-registered behaviour, but if live results come in strong the first follow-up must be
whether that is the newcomers again.

**Window integrity — implemented (7352dd1), still unexercised.** A row scores `matured`
only if every session of its H-day window has a return for every picked asset; otherwise
`short_window` with its realised count, excluded from the headline summary. Entry dates and
picks frozen at log time.

**2026-08-17 vendor gap — CLOSED.** Only Close/Adj Close were NaN. **It healed at ~48
hours**, correcting this document's earlier claim that it had not self-healed.

### Daily command
```bash
cd ~/Projects/regime-aware-signal && source .venv/bin/activate
python -m src.forward_log
```
Once daily after ~05:00 SGT. Then commit `docs/forward_scoreboard.md` — the git timestamp
is what makes entries pre-registered. **Automate via cron if the ritual becomes a burden;
do not stop it.** It is the only evidence not contaminated by in-sample selection, and
`forward_log` is the shared harness the other engines will plug into.

---

## Open threads (ordered)

1. **Event engine Stage 1 — drift-existence test.** GDELT event days; returns at
   1/5/10/20d entered next-open; permutation-tested vs matched non-event days. **The data
   now exists (944 days, both variants).** This is the test that decides whether the event
   engine and the rotation chain have a foundation. Alignment says "regimes and news move
   together"; drift-existence asks "does anything tradeable happen after an event?"

2. **Confirmatory test of the exploratory narrow-n=4 alignment result.** Pre-register it
   properly and test on data it was not discovered in — e.g. extend GDELT back toward the
   ~2015 tagged floor, which also supplies regime variety (2015–16 China, 2018Q4, COVID,
   2022 rate shock). Without that, it stays exploratory.

3. **Fix `chain_rotation.py`** — residualise within sub-periods (removes look-ahead); add a
   permutation null for the sub-period agreement statistic; add an existence test distinct
   from the thesis-match test.

4. **Problem 2 Stage 2** — conditional lead-lag within episodes, built **multi-scale**
   (per-lag profile), **per-episode** (distribution of orders), with a **rupture rule**.
   Blocks on (1).

5. **Same-horizon level-vs-trend comparison** from the existing grid, to isolate the trend
   effect that model_1-vs-model_2 never did.

6. **Ensemble combiner** (position-space, Sharpe-weighted). **The actual open question for
   the product** — engine correlation has never been measured.

7. **The n=4 generalization gap (+5.130) is a live concern**, and now doubly so: it is the
   period where the alignment result appears. **Test:** check which regimes 2025+ rows
   occupy and whether they sit in a low-density corner of the training distribution.

8. **Doc/code accuracy fixes queued:**
   - `regime_classifier.py` console note still claims n=4 stands on "seed stability,
     run-length persistence, and cluster separation" — two of three no longer true.
   - `PIPELINE.md` §4 omits the required `--gdelt` argument on four scripts; §1 has no step
     producing the GDELT panel (now fixable: `gdelt_query` → BigQuery → `gdelt_ingest`).
   - `briefing.md`'s `docs/*.md` glob skips `Regime_Aware_Framework_Methodology_Log.pdf`.

9. **Policy on documented figures** — freeze with an as-of date, or re-run at checkpoints.

10. **Data amendments:** company/entity-level events. `gdelt_theme_mapping.yaml` records
    that GDELT has **no clean semiconductor/defense/space/cyber theme**, that entity
    matching must be **exact** (`LIKE '%INTEL%'` matches "intelligence"), and that SEC EDGAR
    8-K is cleaner for company-specific material events.

11. **Problem 3:** LLM/RAG scenario layer. **12. Streamlit MVP**, then integration.

### Closed 2026-08-18/20
Window integrity (7352dd1) · n=4 pin (5ec014e) · stress-axis port · `_forward` horizon bug
· 08-17 vendor gap · `model_grid` re-deriving model_3 (7c1da76) · GDELT query recovery +
scripted ingest (303bdae) · GDELT extension to 944 days · hard-coded 2024 window ·
partial-bar signal

---

## Working principles

- Every claim about project data must come from data actually run; hypotheses labelled as
  hypotheses with the test proposed.
- Null results are findings. **Check whether the null is definition-dependent** — and
  whether the *dependence itself* is stable across samples. If it reverses, that is noise,
  not a definitional finding.
- **Pre-registration means the question and the success criterion are written down before
  the answer is seen.** A result that emerges instead is **exploratory** and must be tested
  on data it was not discovered in before it counts. Do not relabel the question to match
  whichever arm succeeded.
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
  wrong** — three so far: n=5 fragility (an artifact), the GDELT null holding under a
  broader definition (it did not), and broad-n=4 surviving the extension (it did not).
- **Decide definitions on definitional grounds, before looking at the p-value.**
- **A measured engine is finished being measured.** What strengthens the system is engine
  *independence*, not a better version of a measured component.
- **Know what a test cannot see.** A null from an instrument blind to the phenomenon is not
  evidence of absence.
- **Keep the old numbers beside the new ones.** The hard-coded-2024 bug was invisible
  except as an exact match to a result we still had in view.
- **A silent filter is worse than a crash.** The crash on one arm is what exposed the
  filter on the other.
- **Filename is not provenance.** Verify a data file's variant from its embedded query,
  not its label — that check caught a mislabelled export tonight.
- **Fail loud rather than log something plausible.**
- **Coverage cannot distinguish a live bar from a finished one.** Anything time-sensitive
  must check the clock, not the data.
- Operational rules affecting the forward test are pre-registered while affected rows are
  still pending.
- **Committed is not the same as written**; gitignore rules apply to files you assume are
  safe. Verify with `git ls-files`, not `ls`.
- The **repo is the source of truth**, not model memory.
