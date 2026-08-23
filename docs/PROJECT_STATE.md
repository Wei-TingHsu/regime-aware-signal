# PROJECT STATE — briefing document

*Upload this file (or the `briefing.md` bundle) at the start of a new conversation to
resume without re-explaining. Last updated: 2026-08-23 (00:15 SGT). Keep it updated
after each workstream closes.*

> ## STATUS
>
> **Report due to Dr. Lee 2026-08-24.** Nothing in the forward test matures before then
> (model_1 matures ~08-26), so the live test contributes its *design and timestamps* to
> the report, not numbers — which is the correct contribution at this stage.
>
> **ROTATION IS CLOSED AT EVERY LEVEL REACHABLE WITH THIS DATA (2026-08-22).**
> Seven hypotheses, four instruments, all null: the semiconductor chain
> (unconditional, shock-conditional, news-conditional), cross-asset
> flight-to-quality, sector business-cycle, environment-conditional order, and a
> universe-wide 561-pair scan. The two pairs that survived discovery failed a
> temporal split and a transaction-cost test. **No tradeable rotation signal
> exists in this universe.**
> Stage 1 drift-existence is **PRE-REGISTERED (8273be4, 2026-08-21 13:18:53 +0800) and
> UNRUN** — deliberately, so the registration stays valid for a deeper panel.
>
> Two live-edge defects found today: **per-series macro staleness** (bounded — 2 affected
> rows, no reported result exposed) and **GMM label permutation across refits** (the
> ledger's `regime` column is not comparable across rows; picks are unaffected).

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
2. **Event engine — PRE-REGISTERED, UNRUN, and deliberately so.** Drift-existence is
   specified in `docs/prereg_drift_existence.md` (8273be4, 2026-08-21 13:18:53 +0800),
   re-scoped to a *macro narrative-density* test because the 944-day panel has no
   per-asset event density. Held until the GDELT extension supplies adequate power, so the
   registration stays valid for the deeper panel.
3. **Rotation — CLOSED AT EVERY LEVEL (2026-08-21/22).** The unconditional null was
   extended by an episode-conditional engine (`src/episode_rotation.py`), two new
   pre-registered hypotheses on different asset classes, an environment-conditional
   test, and a universe-wide scan. All null. The scoping caveat that previously
   protected the hypothesis — "this instrument cannot see episode-local chains" — has
   itself been tested and removed: the instrument was built, verified to recover a
   planted lead at d=+0.50 on the real panel, and still found nothing.

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

**A declared look-ahead in the feature scaling (found 2026-08-21, NOT a bug).**
`analog_core._z()` standardises the PC features using `nanmean`/`nanstd` over the **entire
panel**, and `feature_matrix` applies it before any `pos` slicing — so analog distances at
2010 are measured in units set by moments estimated through 2026. This is the same class
as the frozen regime model, which the docstring declares intentional and which Stage 2
validated; but that declaration did **not** extend to the feature scaling, and the phrase
"expanding-window walk-forward, no look-ahead" was therefore too strong. **Corrected here
rather than defended.** Magnitude is expected to be small — PC moments over 5,188 days are
stable — but *expected to be small* is not measured. **Test when time allows:** recompute
the backtest with expanding-window moments and report both numbers side by side.

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

### Problem 2 (rotation chain) — CLOSED, unconditional NULL under three tests

*Run 2026-08-21, seed 42, 2,000 rotations, 1999-01-25 → 2026-08-20 (6,936 days).
All three defects listed in the previous version of this section are now fixed;
`docs/chain_rotation_results.md` holds the full output.*

| arm | statistic | p | reading |
|---|---|---|---|
| **Existence** (order-agnostic) | net_lead dispersion 0.0067 | **0.8371** | no ordering structure |
| **Pairwise** | 10 directed pairs, Holm-corrected | **0/10 significant** | no single pair survives |
| **Thesis-match** | Spearman −0.100 | **0.5947** | discovered order ≠ thesis |
| **Sub-period stability** | agreement −0.217 | **0.2659** | indistinguishable from reshuffling |

### Problem 2 Stage 2 — the conditional merge, BUILT and NULL (2026-08-21/22)

`src/episode_rotation.py` implements the conditional merge decided 2026-08-19: an event
detector segments time into **episodes**, chain logic runs **inside** them. The event
names the WHEN and the SET; price statistics determine the sequence. Detector-agnostic —
`--trigger file --dates <csv>` is the slot FOMC decisions, FOMC minutes, chain earnings
and SEC 8-K plug into with **no engine changes**.

**Design:** episode = eplen sessions AFTER the trigger (trigger day excluded — the gap is
conceded, and including the day that defines a shock trigger would be circular);
de-clustering gap = eplen so episodes never overlap; betas fit on the trailing 250
sessions ending the day before the trigger and frozen through the episode. Statistic [1]
pooled within-episode lead-lag at short lags (a 15-day episode cannot support K=10 — this
is the multi-scale fix); statistic [2] **order concentration**, mean pairwise Kendall τ-b
of per-episode half-max response orders — the *distribution of orders* the old engine
could not compute. Null for both: independent per-name episode shuffle.

**Detection capability demonstrated, not assumed.** `--inject` plants a known lead in the
REAL episodes. On the semiconductor basket a strength-0.3 lead moved NVDA→TSM from
d=−0.006 (p=0.997) to **d=+0.502 (p=0.0005, Holm 0.005)**. Every null below comes from an
instrument proven to recover planted structure on this data.

| arm | trigger | episodes | [2] τ | p |
|---|---|---|---|---|
| **Shock** (powered) | \|z\|≥2 eq-weight chain | 203 / 243 / 171 | +0.004 / +0.001 / −0.002 | 0.229 / 0.886 / 0.267 |
| **Stress** (GDELT merge) | narrow share z≥1.5 | 26 | −0.015 | 0.969 |

eplen ladder {10, 15, 20}, all rungs reported. **The GDELT→episode plumbing ran end to
end** (65 triggers → 26 episodes, inside the 25–35 preregistered range) — the merge
architecture works; there is nothing for it to find.

### Cross-asset and sector rotation — PRE-REGISTERED, both NULL (2026-08-22)

Registered `b4a942a` **before execution**. Two hypotheses with independent mechanisms, not
retries of the closed chain. Injection audits passed on both baskets first (TLT→SPY
d=+0.269 p=0.0005; SOXX→XLE d=+0.369 p=0.0005).

| hypothesis | registered order | design | [2] τ / p at ep 10/15/20 |
|---|---|---|---|
| **Cross-asset** | TLT→UUP→GLD→SPY→USO | no residualization (the raw flow IS the signal); **risk-off only** (flight-to-quality is directional) | +0.005/0.311 · −0.003/0.124 · +0.005/0.259 |
| **Sector** | SOXX→XAR→XLE→XLV→XLP | SPY-factor residual (sectors share market beta); bidirectional (capex lead is symmetric) | +0.001/0.595 · −0.005/0.841 · −0.005/0.559 |

Each trigger justified by **its own mechanism**, not by consistency across hypotheses.
Neither clears the registered criterion at any rung. Sector prereg recorded the base rate
against it up front (Molchanov & Stangl, 2,640 t-statistics, scant evidence; Jacobsen et
al., ~2.3%/yr with perfect foresight) — **a null replicates published findings.**

Panel limit recorded honestly: **no financials, industrials, discretionary, utilities or
materials ETFs exist in the universe**, so a full business-cycle rotation test is not
constructible on this data.

### The two surviving pairs — BOTH FAILED confirmation (2026-08-22)

Statistic [1] produced two pairs stable in sign and magnitude across the eplen ladder.
`src/pair_confirm.py` tested them on the two questions discovery cannot answer. **Both
failed**, for different reasons.

| pair | full sample | first half | second half | verdict |
|---|---|---|---|---|
| **SPY→GLD** k=1 | d=+0.170, p=0.001 | 2007–2017: **+0.294**, p=0.0005 | 2017–2026: **+0.053**, p=0.357 | magnitude collapses **5.6×**; crisis-specific |
| **SOXX→XAR** k=3 | d=+0.152, p=0.001 | 2012–2019: **−0.035**, p=0.578 | 2019–2026: **+0.228**, p=0.001 | **sign FLIPS**; entirely one period |

**Economic test** (sign of leader → hold follower, block bootstrap by episode, 4bps
round-trip):

- SPY→GLD: +9.32 bps/trade, **95% CI +0.11 … +19.66**, net +5.32 — the CI lower bound
  does not clear costs, and the estimate is inflated by the dead first half.
- SOXX→XAR: +3.69 bps, CI −2.48 … +10.33, **net −0.31 bps**, hit rate 49.2%. Not tradeable.

**Read the SPY→GLD sign.** Positive d on a risk-off trigger means equities fall and gold
follows *the next day, in the same direction*. That is **not** flight-to-quality — it is
liquidation (the "dash for cash" mechanism), the rival hypothesis that was NOT registered.
A pre-registered hypothesis producing evidence for its rival is a stronger result than
confirmation would have been.

**The methodological lesson, worth more than the pairs.** Ladder consistency across
eplen {10,15,20} looked like robustness. It was not: the rungs draw 108/97/77 episodes
from the *same* 225 triggers, so they re-measure one sample three times. **Overlapping-
sample robustness checks can pass while an effect is entirely period-specific. A temporal
split catches what a parameter ladder cannot.**

### Environment-conditional order — NULL (2026-08-22)

Hypothesis: sequences are not universal but **environment-specific** — bonds lead in one
macro regime, equities in another — so pooling across regimes dilutes real order to ~0.
This is the one test the project is uniquely equipped to run, because it has a regime
classifier.

Designed as **ONE test, not twelve**: testing each regime separately and reporting the
significant one is a fishing licence. The hypothesis predicts that grouping episodes by
regime raises **within-group** order agreement above **pooled** agreement. Null shuffles
regime labels across episodes, preserving group sizes and every episode path.

Regimes are **canonically ordered** calm→stressed by the stress axis (PC3, |corr| VIX
0.96), so labels are comparable by construction.

| basket | pooled τ | within-regime τ | lift | p |
|---|---|---|---|---|
| Cross-asset | −0.0034 | −0.0093 | **−0.0059** | 0.688 |
| Sector | −0.0052 | −0.0015 | **+0.0037** | 0.272 |

Cross-asset conditioning made agreement **worse** than pooling. **The pooled nulls were
not a dilution artifact.** Verified on synthetic data first: four planted per-regime
orders give a lift of +0.977 (p=0.002); order independent of regime gives +0.005.

**One positive, and it is narrow.** Cross-asset first-mover concentration: **TLT first in
28.4%** of episodes against 20% uniform, **p=0.032** — the significance test first-mover
counts never had. Sector was null (p=0.744), so it is not a generic property of the
statistic. But: (a) a first mover is **not a sequence** — knowing bonds move first says
nothing about the order of what follows, and [2] says what follows does not repeat;
(b) across two baskets × two statistics that is four tests, and one at p=0.032 is roughly
what chance produces. **Requires confirmation before it is a finding.**

### Universe-wide scan — the answer to "did we only test what we imagined"

`src/universe_scan.py`. Pre-registration is lossy: it can only test what someone thought
to write down. Testing every 5-asset basket is arithmetically hopeless — C(47,5) =
1,533,939, of which ~77,000 would look significant on pure noise. The honest construction
changes the unit to **ordered pairs** and corrects for the search itself: compute every
pair at every lag, take the **maximum** |d|, and build the null distribution *of that
maximum* by independent circular rotation (White reality check / Westfall-Young).

Window 2015-07-08 → 2026-07-17, 2,772 sessions, 35 of 47 assets with ≥2,500 sessions.

| variant | pairs | naive p<0.05 | expected by chance | universe-corrected |
|---|---|---|---|---|
| SPY-residualized | 561 | **148** | ~28 | **0** |
| raw | 595 | **154** | ~30 | **0** |

**The informative number is 148 vs 28.** Real dependence exists in the universe, and
roughly 120 apparent findings are manufactured by the search. That is the empirical
demonstration, on this data, of why exhaustive search without correction is worthless.

**HONEST CAVEAT — the corrected test is underpowered and its null is inflated.** Observed
maximum |d| = 0.157 against a null maximum averaging 0.232 and a 95th percentile of
**0.628** (0.893 unresidualized). For Gaussian series of this length the null maximum
should be ≈0.11. Diagnosed: **MLPA (18.8σ) and AMLP (17.4σ)** have extreme single-day
moves and appear in 7 of the top 20 pairs — they drive both the observed maximum and the
null's tail. A normal-scores transform was attempted and **did not demonstrably fix it**
on fat-tailed synthetic data, so it is not claimed as a fix. **"0 survive" is therefore
conservative but weak**: the test likely could not have detected a real effect either.
Remedy (winsorize or exclude the offending assets) is post-submission. The 148-vs-28
contrast is unaffected by this defect.

Full-sample discovered order **ASML→TSM→MU→INTC→NVDA**, net_lead spanning +0.0082 to
−0.0069. Adjacent names are separated by as little as **0.0007** (MU −0.0033 vs INTC
−0.0040): these are near-ties, not a ranking.

**The existence test is the one that was missing**, and it is the one that closes the
question. The old permutation asked only whether the discovered order matched the
supply-chain thesis — a real chain running in a *different* order also returns p≈0.6
there, so it could never have detected existence. The new arm tests the dispersion of the
net_lead vector against an independent circular-rotation null and is agnostic to which
order appears. Note the direction: p=0.8371 puts the observed dispersion in the **lower**
tail — the real data is *less* ordered than randomly-rotated data typically is. The
opposite of a chain, though not significantly so.

**"Anti-stable" is RETIRED** — the claim now has the test it never had. Null mean −0.007,
SD 0.200, observed −0.217, p=0.2659. About one SD from a null centred at zero. The
defensible claim is *"sub-period orders are indistinguishable from random reshuffling."*

#### The sub-period table is a noise realisation, not a finding

| period | CORRECTED (betas fit within period) | OLD (look-ahead) |
|---|---|---|
| 1999–2005 | MU → TSM → INTC → ASML → NVDA | MU → INTC → TSM → ASML → NVDA |
| 2005–2012 | NVDA → INTC → TSM → ASML → MU | INTC → NVDA → TSM → ASML → MU |
| 2012–2019 | TSM → ASML → NVDA → INTC → MU | ASML → TSM → INTC → NVDA → MU |
| 2019–2026 | ASML → NVDA → MU → TSM → INTC | ASML → NVDA → MU → TSM → INTC |

**8 of 20 name-slots moved** when the look-ahead was removed — every one an *adjacent*
swap, which is what near-tied net_lead scores produce. Yet the agreement statistic moved
only −0.250 → −0.217.

**That combination is the actual finding.** Reshuffling 40% of the positions barely moved
the number *because both versions are draws from the same null*. The earlier presentation
of these four orders as substantive evidence is **retired**: they are one realisation, and
a defensible change to the beta-estimation window reshuffles nearly half of them.

#### Per-lag profile — dilution hypothesis NOT supported

The previous version of this section asserted that averaging k=1..10 dilutes a fast
cascade by ~80%. **The profile does not show that.** Peak |d_ij| lags are scattered —
5, 6, 6, 1, 2, 10, 10, 8, 10, 4 — with three sitting at the k=10 boundary, which is where
`argmax` lands on a flat profile. Per-lag values reach ±0.06 while the k-average is
~0.008, so the averaging is diluting **sign-flipping noise**, not a signal. This
*strengthens* the null rather than qualifying it.

**Still unaddressed by this test**, and the reason the null is scoped rather than
absolute:
- **Interruptions** — need a rupture/censoring rule, which requires event detection.
- **Variable order across episodes** — averaging different per-episode orders yields ~0.
  Needs a *distribution* of orders, not a single one.

**So the null is scoped: no unconditional, single-order, full-period chain exists in these
five names.** It does not distinguish that from "chains exist with episode-varying order."
The instrument is blind to the episode-local form by construction.

**Invariance check passed.** Sections [1] and [2] were untouched by the look-ahead fix —
the full-sample beta was always correct for the full-sample test — and Spearman reproduced
at **−0.100 exactly**. The permutation p read 0.5947 against 0.605 recorded; the Monte
Carlo SE at 2,000 iterations is ~0.011 and the window is longer than when 0.605 was
recorded, so every rotation draw differs. Within noise; to be confirmed at higher iters.

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

**NO regime transition has occurred — CORRECTION (2026-08-21).** This document previously
recorded 08-20 as *"the first regime transition of the live test… regime 0 — the STRESSED
regime… and the picks shifted accordingly."* **That entry was wrong on every clause** and
is retired.

*What actually happened: a label permutation across GMM refits.* `analog_core.frozen_labels`
refits the GMM on every call, and `forward_log.refresh_data` reruns `pca_macro` first.
PCA component **signs are arbitrary across refits**; a sign flip mirrors the input, which
is an isometry — the partition is identical but the component *indices* are free to
permute. `random_state` is pinned, which makes the fit deterministic given identical input,
but it cannot pin index order across a *changed* input.

*Diagnosis by pool size.* Re-running the classifier today labels **08-19 as regime 0** —
a past, fixed date whose ledger row says regime 1 — while handing it an analog pool of
**979**. Regime 1 holds 984 days; regime 0 holds 1,735. The cluster now called 0 is the
cluster that was called 1. Not a close call.

*What follows:*
- **The macro state did not move.** 08-19 PC1..3 = [3.0668, 0.3524, 0.1245], 08-20 =
  [3.0505, 0.3397, 0.1272]. A ~0.02 move on PC1 cannot reassign anything.
- **The picks cannot have shifted because of the regime.** Analog selection is
  `labels[:pos] == r_now` plus Euclidean distance — both invariant under a label
  permutation *and* under a PC sign flip. "The picks shifted accordingly" asserted a
  causal link that does not exist and is **retired**.
- **The `regime` column in `forward_ledger.csv` is not comparable across rows** and is
  currently an annotation only. The regime table above is likewise labelled by whichever
  run produced it.
- **Seed stability never tested this.** The n=4 validation is ARI = 1.000, and ARI is
  **label-invariant by construction** — mathematically incapable of detecting an ID
  permutation. The strongest validation the regime engine has could not see this failure.

*Fix (queued, thread 3):* fit once, persist the fitted parameters, order components by
their coordinate on the data-driven stress axis — the principle `src/stress_axis.py`
already applies one level down — and make consumers **read** `regime_labels.parquet`
instead of refitting.

**Per-series macro staleness at the live edge (2026-08-21) — bounded.** 08-20 and 08-21
carry a fresh `T10Y2Y` (0.50) beside a stale `DGS10`/`DGS2` (4.65/4.19), so the curve
identity `DGS10 − DGS2 = T10Y2Y` fails on exactly those two rows. Full-panel audit:
**3 violations in 7,962 rows** — those two plus 1995-11-29, which sits outside the
2006-01-03 PCA panel and has never entered a result. **No reported number is exposed.**
`DTWEXBGS` frozen at 118.9028 to 4dp across six sessions and `VIXCLS` at 14.89 across
three indicate the staleness is broader than the two flagged series. Note this survives
`download_data --force`, so the divergence is either upstream at FRED or in a per-series
cache path that `--force` does not reach. *Guard queued (thread 4).*

*This is the macro-side twin of the partial-bar bug.* There, coverage could not distinguish
a live bar from a finished one. Here, **value-equality cannot distinguish "no change" from
"no data."*

**Maturity dates.** model_1 (H=5) matures ~2026-08-26; model_3 (H=20) ~mid-September.
**Nothing matures before the 08-24 report deadline** — every row will read `pending`. The
forward test's contribution to the report is its pre-registration timestamps, its harness
design, and the two silent-failure bugs it caught, not any number.

**Live-period location — first concrete evidence for thread 7.** PC1 ≈ **3.05** on the
current bars, roughly three standard deviations out on the rates axis. That is a genuinely
low-density corner of the training distribution, which is what the +5.130 generalization
gap predicts and which had until now only been inferred from a summary statistic.

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

1. **Event engine Stage 1 — drift-existence test. PRE-REGISTERED, UNRUN.**
   `docs/prereg_drift_existence.md`, committed **8273be4, 2026-08-21 13:18:53 +0800**,
   before any drift-test code exists. **RE-SCOPED**: the 944-day panel carries a *global*
   stress-density series with no per-asset event density, so the entity-level spec in
   `architecture_decisions.md` §3 was not runnable. The registered question is now *does a
   spike in economy-wide narrative-stress density predict market-level drift?*

   **The earlier description of this as "the test that decides whether the event engine
   and the rotation chain have a foundation" is RETIRED as overstated in both
   directions.** A positive result does **not** discharge the entity-detection
   precondition on the conditional merge; a null does **not** close out firm-level drift,
   because the instrument is blind to it. Entity-level detection is thread 11.

   **Deliberately unrun.** At ~25–35 de-clustered episodes the MDE is ~1.6% at H=10 and
   ~2.3% at H=20 — above plausible PEAD-scale effects — so running it now would spend the
   registration on an underpowered version of a question worth asking on a deeper panel.
   Sequence: **extend GDELT first (thread 2), then run.**

2. **GDELT extension to the ~2015 tagged floor.** Serves three purposes at once: powers
   thread 1 to ~100+ episodes; supplies the out-of-sample basis for the exploratory
   narrow-n=4 alignment result; adds regime variety (2015–16 China, 2018Q4, COVID, 2022
   rate shock). Tooling exists (`gdelt_query` → BigQuery → `gdelt_ingest`, 303bdae), so
   the marginal cost is an afternoon of year-split pulls.

   **Precondition before trusting any share or z-score across the join:** plot `total_docs`
   across 2015–2026 and check for level shifts. GDELT's source set grew over the period; a
   structural break in the *denominator* would contaminate the share measure and a z-score
   computed through it would manufacture spikes at the seam. Check before it becomes a
   finding.

3. **Canonical regime labels.** Fit once, persist the fitted parameters, order components
   by their coordinate on the data-driven stress axis, make consumers read
   `regime_labels.parquet` rather than refit. Makes the ledger's `regime` column
   comparable **by construction** instead of by luck. Five hard-coded `n_components=4`
   literals should be replaced with config reads in the same commit.

4. **`forward_log` macro guard.** Refuse to log when the signal-date macro row duplicates
   its predecessor across all eight series, or when |DGS10 − DGS2 − T10Y2Y| > 0.005.
   Direct analogue of the partial-bar fix. Fail loud.

5. **Problem 2 Stage 2** — conditional lead-lag within episodes, built **multi-scale**
   (per-lag profile), **per-episode** (distribution of orders), with a **rupture rule**.
   Blocks on (1). *The unconditional arm is now closed as a null, so this is the only
   remaining route by which a rotation chain could exist.*

6. **Universe-wide directed-pair scan (exploratory by construction).** Instead of choosing
   another 5-name chain by hand — data-mining, and C(47,5) = 1,533,939 subsets makes
   per-subset testing meaningless — compute the full **47 × 46 = 2,162** ordered-pair
   lead-lag matrix in one pass and test the **maximum statistic across the whole matrix**
   against the rotation null. That single distribution accounts for the search itself and
   is far less conservative than Bonferroni because the pairs are heavily correlated
   (White reality-check construction). Chains would then be *built* from surviving pairs
   rather than assumed. `cross_corr_by_lag` already vectorises this. Must be labelled
   **exploratory** — it would be run after seeing the 5-name null — and a universe-wide
   null is the expected outcome, replicating Molchanov & Stangl at larger scale.

7. **Max-over-lag existence test** on the existing 5 names: `max_k |d_ij(k)|` against the
   same rotation null. Immune to k-averaging dilution by construction, so a second null
   would close the "the engine cannot detect the likely form of chain" objection on
   evidence rather than argument. Exploratory. ~30 minutes.

8. **Same-horizon level-vs-trend comparison** from the existing grid, to isolate the trend
   effect that model_1-vs-model_2 never did.

9. **Ensemble combiner** (position-space, Sharpe-weighted). **The actual open question for
   the product** — engine correlation has never been measured.

10. **The n=4 generalization gap (+5.130) is a live concern**, and now doubly so: it is the
   period where the alignment result appears. **PARTIALLY ANSWERED 2026-08-21:** live bars
   sit at PC1 ≈ 3.05, ~3 SD out on the rates axis — a low-density corner, as predicted.
   Remaining: quantify the training-density at that coordinate rather than eyeballing it,
   and check which regimes 2025+ rows occupy.

11. **Entity-level event detection** — the precondition for the conditional merge, carved
    out of thread 1 where it was previously implicit. `gdelt_theme_mapping.yaml` records
    that GDELT has **no clean semiconductor/defense/space/cyber theme**, that entity
    matching must be **exact** (`LIKE '%INTEL%'` matches "intelligence"), and that SEC
    EDGAR 8-K is cleaner for company-specific material events. **The merge decision cannot
    be made without this**, whichever way thread 1 resolves.

12. **Expanding-window feature scaling** — measure the magnitude of the declared `_z()`
    full-sample look-ahead in `analog_core`, and report both numbers side by side.

13. **Doc/code accuracy fixes queued:**
   - `regime_classifier.py` console note still claims n=4 stands on "seed stability,
     run-length persistence, and cluster separation" — two of three no longer true.
   - `PIPELINE.md` §4 omits the required `--gdelt` argument on four scripts; §1 has no step
     producing the GDELT panel (now fixable: `gdelt_query` → BigQuery → `gdelt_ingest`).
   - `briefing.md`'s `docs/*.md` glob skips `Regime_Aware_Framework_Methodology_Log.pdf`.
   - `chain_rotation.py` docstring's dilution claim is now contradicted by its own §5
     output; the file says "if a cascade completes fast" conditionally, but PROJECT_STATE
     previously asserted it. Corrected above.

14. **Policy on documented figures** — freeze with an as-of date, or re-run at checkpoints.

15. **Problem 3:** LLM/RAG scenario layer. **16. Streamlit MVP**, then integration.

### Closed 2026-08-18/21
Window integrity (7352dd1) · n=4 pin (5ec014e) · stress-axis port · `_forward` horizon bug
· 08-17 vendor gap · `model_grid` re-deriving model_3 (7c1da76) · GDELT query recovery +
scripted ingest (303bdae) · GDELT extension to 944 days · hard-coded 2024 window ·
partial-bar signal · **Problem 2 unconditional null closed under three tests** ·
**`chain_rotation` sub-period look-ahead removed** · **Stage 1 pre-registered (8273be4)** ·
**08-19/08-20 regime flip diagnosed as label permutation** · **curve-identity audit:
staleness bounded to 2 live-edge rows, no result exposed**

### Closed 2026-08-22
**Problem 2 Stage 2 conditional merge BUILT and null** (shock + GDELT arms, injection
audit passed) · **cross-asset rotation pre-registered and null** · **sector rotation
pre-registered and null** · **both surviving pairs failed temporal split and cost test**
· **environment-conditional order null** · **universe-wide 561-pair scan, 0 survive
correction** · three silent-failure bugs fixed: O(E²) Kendall loop (~1hr → ~1s at E=203,
verified against scipy to 1e-12), **YYYYMMDD integers parsed as nanoseconds since epoch**
(every GDELT date became 1970, zero triggers, no error raised), reading rule firing
"structure detected" on a single Holm hit within one ladder rung

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
- **A robustness ladder built on OVERLAPPING samples is not robustness.** eplen
  {10,15,20} drew 108/97/77 episodes from the same 225 triggers and re-measured one
  sample three times; both pairs that passed it failed a temporal split. **Split by time,
  not just by parameter.**
- **Demonstrate detection capability before reporting a null.** `--inject` plants a known
  lead in the real episodes; a null from an instrument that cannot recover it is
  meaningless. Synthetic verification is not sufficient — it must run on the actual data,
  and the synthetic must match the data's distribution (Gaussian verification missed the
  fat-tail problem in the universe scan entirely).
- **When a hypothesis has a natural rival, register which one you believe.** SPY→GLD came
  back with the sign of the *unregistered* rival (liquidation, not flight-to-quality).
  Evidence for a rival mechanism is stronger than confirmation of your own.
- **Test the conditioning hypothesis as ONE statistic, not per-group.** "Does grouping by
  regime raise agreement above shuffled labels" is one test; "is regime k significant" ×
  4 regimes is a fishing licence.
- **When the search space is large, permute the search, not the candidate.** A
  maximum-statistic null over the whole matrix accounts for having looked at all of it,
  and is far less conservative than Bonferroni because the candidates are correlated.
- **A statistically detectable effect that does not clear the spread is not a product.**
  Measure bps against a cost assumption with a block bootstrap, not correlation alone.
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
  wrong** — **five so far**: n=5 fragility (an artifact); the GDELT null holding under a
  broader definition (it did not); broad-n=4 surviving the extension (it did not); the
  chain agreement statistic moving substantially under the look-ahead fix (it moved 0.033);
  and the per-lag profile peaking at 1–2 days to show cascade dilution (peaks are
  scattered, three at the k=10 boundary).
- **The first three wrong priors shared a pattern**: results were more *basis-carried* and
  less *phenomenon-carried* than expected. The fourth was that correction **over-applied**.
  The refinement: *the presentation layer can be basis-sensitive while the test statistic
  is not.* 8 of 20 chain order-slots moved and the agreement barely shifted — precisely
  because both versions were draws from the same null.
- **A statistic robust to a basis change is not thereby evidence of signal.** If it sits at
  its null, robustness only says the null is stable.
- **Test existence separately from thesis-match.** A test asking "does the discovered order
  match my hypothesis?" returns a large p for a real effect running in a different order,
  and can never detect existence. This is what the rotation chain lacked for months.
- **A null needs its estimand stated, not just its p-value.** "No unconditional,
  single-order, full-period chain in these five names" is a claim; "no chain" is not
  something this instrument can say.
- **Label-invariant validation cannot detect label instability.** ARI = 1.000 was the
  regime engine's strongest evidence and was mathematically incapable of seeing the ID
  permutation that broke the ledger column.
- **Value-equality cannot distinguish "no change" from "no data."** The macro twin of
  "coverage cannot distinguish a live bar from a finished one." Check the as-of date, not
  the values — and check derived identities (a curve that must equal a difference) as a
  cheap cross-series staleness detector.
- **When a search space is large, permute the search, not the candidate.** C(47,5) subsets
  makes per-candidate testing meaningless; a maximum-statistic null over the whole matrix
  is the honest construction.
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

## GAP FOUND 2026-08-23 — the recency kernel was designed and never built

The 2026-08-18 design session LOCKED a two-axis weighting:
w_t = exp(-lambda*(T-t)) * exp(-||z_t - z_now||^2 / 2 sigma^2), described as
"similarity-dominant (tight sigma so only true analogs get weight; gentle
recency decay breaks ties among them) -- an explicit, documented choice."

`analog_core._kw()` implements ONLY the similarity kernel. There is no lambda
and no time term anywhere in the codebase; a 2008 analog and a 2024 analog at
equal macro distance receive equal weight. Not in config.yaml, not in
models.yaml, not in any open thread. It fell through the gap between design
and build and went unnoticed for five days.

NOT to be implemented under deadline. lambda is a free hyperparameter, and
adding a tunable knob after observing Sharpe 0.25 is exactly how backtests get
flattered. Disciplined version, post-submission: pre-register lambda on
economic grounds (a stated half-life, not a searched one), declare a
sensitivity ladder, report every rung.

## EVENT SOURCE REGISTRY (created 2026-08-23)

Recorded because no single place listed what still needs testing. `--trigger file`
in episode_rotation and the spillover/PEAD harnesses take any date list, so each
row below is a CSV away from being runnable.

| # | event class | status | source | cost |
|---|---|---|---|---|
| 1 | Macro narrative-stress density (GDELT) | TESTED — null, prereg 8273be4 | BigQuery GDELT, 944d | done |
| 2 | Firm earnings — own-firm drift (PEAD) | TESTED — criterion not met; H=1 confined to TSLA/NVDA/MSFT | yfinance | done |
| 3 | Firm earnings — cross-firm spillover | REGISTERED, unrun | yfinance + adjusted OHLC | done |
| 4 | FOMC decisions (2pm day-2 statement) | UNTESTED | federalreserve.gov calendars | ~1h transcription |
| 5 | FOMC minutes (3 weeks after decision) | UNTESTED | same | ~1h |
| 6 | SEC 8-K filings (Item 2.02 etc.) | UNTESTED — the clean firm-level source (thread 11) | EDGAR full-text API | ~half day |
| 7 | CEO fireside chats / conference appearances | UNTESTED — no structured source | transcript scraping | weeks |
| 8 | Institutional research reports | UNTESTED — no free structured source | — | weeks, may be infeasible |
| 9 | Senate/Congressional announcements, policy events | UNTESTED — no date list | Congress.gov / Federal Register | ~half day |
| 10 | Central bank materials beyond FOMC | UNTESTED — intended as the Problem 3 RAG corpus (2026-08-18 session) | central bank sites | tied to Problem 3 |
| 11 | Guidance revisions, product launches, analyst days | UNTESTED, never previously recorded | — | unscoped |

**Structural limitation applying to rows 4-11 under the current entry convention:**
drift is measured from t+2, so the announcement session and the following session
are DISCARDED. For a 2pm FOMC statement that removes the entire announcement
response and the pre-FOMC drift anomaly (Lucca & Moench). Any null on these
sources is a null about POST-announcement drift only. The spillover harness
(row 3) is the first to decompose GAP vs INTRA and can see inside that window.

## DECISIONS DEFERRED — revisit before any product launch (recorded 2026-08-23)

**1. Manual-collection sources cannot scale to a daily automated product.**
`transcript` (CEO fireside chats, conference appearances) and `bank_research`
(published summaries of investment-bank views) have NO free structured feed.
Manual collection is fine for building the HISTORICAL corpus that step 3 needs,
and that corpus is genuinely necessary. But a live daily product cannot depend
on a human saving files. Three options, none chosen:
  (a) buy a data vendor feed (transcript providers, news APIs) -- a purchasing
      decision, not an engineering one;
  (b) accept a declared coverage gap and state it to the customer;
  (c) drop those two sources from the live product and keep them for research.
DECIDE BEFORE LAUNCH, not before submission.

**2. The political source is biased toward DECIDED policy.**
Federal Register presidential documents (executive orders, proclamations,
memoranda) are free, full-text and backtestable to 1994 -- and they are all
high-`specificity` by construction. Statements, posts and rhetoric -- the
low-specificity end, which is precisely where a market-moving threat-to-act
lives -- are NOT covered. The X API is ~$200/mo and its HISTORICAL archive is
the expensive part; without history a source can never enter step 3, which
conditions on macro-similar precedent. Truth Social has no public API at all.
CONSEQUENCE: an absence of low-specificity political events in any result is a
COVERAGE GAP, not evidence that rhetoric does not move markets.

**3. Foreign private issuers file 6-K, not 8-K.**
TSM (Taiwan) and ASML (Netherlands) returned zero 8-Ks -- correctly, since the
form does not apply to them. 6-K carries no item codes, so the Item 2.02 filter
that isolates earnings releases for domestic filers has no equivalent. Foreign
issuers therefore arrive with LOWER PRECISION than domestic ones, and any
cross-firm comparison must account for that asymmetry rather than treating the
two document sets as equivalent.

## OPEN THREAD 17 — political source, BUILT BUT NOT YET WORKING (2026-08-23)

Status: `src/fetch_sources.py political` exists; first run returned HTTP 400 on
every document type. Cause: server-side filtering on
`conditions[presidential_document_type][]` with GUESSED enum values. Rewritten
to query only `conditions[type][]=PRESDOCU`, paginate, filter client-side, and
print the API's own error body plus the type labels actually returned.

**NOT DONE UNTIL `data_provenance/docs/political/` is non-empty.** Recorded as a
numbered thread rather than an intention because the recency kernel (λ) was
"locked" on 2026-08-18 and sat unbuilt for five days without anything in the
repo flagging it. A thread that only exists in conversation does not exist.

Remaining coverage gap after this works: LOW-SPECIFICITY political
communication -- statements, posts, rhetoric. Federal Register carries decided
policy only. X archive is the paid tier and Truth Social has no API, so this
gap is a purchasing decision, not an engineering one. See "Decisions deferred".
