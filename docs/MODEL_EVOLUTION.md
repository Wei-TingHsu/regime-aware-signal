# How the models evolved

*A record for readers outside the project — investors, a supervisor, a
prospective client — of every model this project has run, what each one was
for, what it found, and what is registered next. Written 2026-09-08. Every
number below traces to a file in this repository; the file is named.*

The short version: **four models and a three-kernel family have been
specified. Three models run forward; Model 4 and the kernel family were run on
8 September and neither produced a finding.** Two headline claims were made
early and both were retired by the project's own tests. What survives is
narrower than the first draft promised and every step of the narrowing is
recorded here.

---

## The rule that governs everything below

A model in this project is a **single written specification, frozen before it
sees live data**. The three running models were committed to `config/models.yaml`
on 17 August 2026 and have not changed. Their forward ledger appends one row per
completed US session and is never rewritten. A model that is adjusted after
seeing its own forward results is not out-of-sample, and the whole value of the
ledger is that none of these has been.

New models run **beside** the old ones, never instead of them.

---

## Model 1 — baseline · running since 19 Aug 2026

| | |
|---|---|
| **Specification** | 5-session horizon, long 5 / short 5, 100 nearest same-regime days, kernel width 1.5, recency half-life 3.4 years |
| **Selection** | Specified in advance |
| **What it tests** | Whether ranking assets by what happened after macro-similar past days produces a spread |
| **Backtest** | Sharpe **0.51** on 47 assets, 837 weekly rebalances 2010–2026 |
| **Under correct inference** | Block-permutation **p = 0.045** (8 exceedances of 200) — survives, marginally |
| **On the survivorship-controlled 35** | Sharpe 0.25, **p = 0.184** — **retired** as a claim |
| **Costs** | Break-even 60.6 bps/side; realistic execution takes ~0.08 of Sharpe |
| **What went wrong** | The short leg returned **+0.169%/week** — the five worst-ranked names went *up*. The spread is a strong long leg fighting a bad short. |

*Source: `backtest_evidence.py` → `docs/backtest_evidence.md`, 28 Aug 2026.*

## Model 2 — horizon-trend · running since 19 Aug 2026

| | |
|---|---|
| **Specification** | 10-session horizon, trend-mode similarity, kernel width 1.5 |
| **Selection** | Specified in advance |
| **What it tests** | Whether matching on the *direction* of macro movement beats matching on its *level* |
| **What was found** | Its apparent advantage over Model 1 **was a look-ahead** in feature scaling. On a live-basis standardisation, level beats trend by 0.12 Sharpe. |
| **Status** | Runs forward as registered. The trend advantage is not claimed. |

*Source: `CURRENT_STATE_2026-08-23.md` §15.3; `_z()` look-ahead measured at +0.261 Sharpe (p 0.057) for the trend model.*

## Model 3 — deliberate overfit · running since 19 Aug 2026

| | |
|---|---|
| **Specification** | 20-session horizon, trend mode, kernel width 1.0 |
| **Selection** | **Best in-sample of 48 configurations — grid-selected** |
| **What it tests** | Whether the best cell in a grid holds up live. It is a labelled control, not a candidate. |
| **What was found** | Its in-sample p-value is not evidence after selection. The family-level test on 28 Aug showed the best of 54 grid configurations reaches Sharpe **0.73**, while the best of 54 *nulls* averages **0.56** and reaches 0.77 at the 95th percentile. **Family p = 0.090.** Searching a grid of pure noise produces a Sharpe of 0.56. |
| **Status** | Runs forward as registered. Exists to show what grid selection does. |

*Source: `backtest_evidence.py` §5.*

---

## What the three models established together

**One thing survives.** The model specified in advance, on the full universe,
at p = 0.045. That is a real but weak effect — or no effect at all. On this
evidence the two cannot be separated, and no document in this project claims
otherwise.

**Three things were retired.** The survivorship-controlled result. The trend
model's advantage. The grid-selected best.

**One mechanism was diagnosed.** The kernel's recency decay does not
*tie-break* between similar past days — it *reselects*: with and without decay,
the top-100 sets overlap only 76–85% against a 90% threshold, and every
selected day gets nearly equal weight. It was initially inferred that the engine therefore reduces to *"the 100
most recent same-regime days, averaged equally."* **The kernel family test on
8 September showed that inference was wrong**: equal-weighting every
same-regime day gives Sharpe 0.04, so the kernel's weighting is doing the
work. Recency reselects rather than tie-breaks — that finding stands — but the
selection it performs is not nothing. The word "analog" still overpromises; the
mechanism is more than regime averaging.

*Source: `CURRENT_STATE` §15.3, rung-level selection diagnostic.*

---

## Model 4 — long top-5 against the universe · RUN 8 Sep 2026 · FAIL

**The hypothesis.** Selection skill exists on the long side and is masked by a
short leg that captures beta. Remove the short leg without removing market
neutrality: hold the top 5, benchmark against the equal-weight universe. Both
legs carry beta; the difference isolates whether ranking adds anything over
holding everything.

**Everything else identical to Model 1.** Same score, same horizon, same
kernel. Only the benchmark changes. If anything else changed, a result could
not be attributed.

**Must clear the bar Model 1 could not.** Positive at block-permutation
p < 0.05 on *both* universes — including the survivorship-controlled 35 where
Model 1 failed — and stable across a chronological split at ≤ 3×. Meeting the
full-universe criterion alone is what the incumbent already does and is not a
pass.

**Registered falsification.** If top-5 minus universe is indistinguishable
from zero, there is no selection skill in the ranking. Model 1's +0.295% was
the long leg riding beta while the shorts lost, and the plan's language about
ranking is retired.

**Designed from the backtest record only.** The forward ledger held two
non-overlapping trades at the time of writing and contributed nothing.

**Result — FAIL, and the shape of the failure is the finding.**

| | ALL 47 | LONG-HISTORY 35 |
|---|---|---|
| spread, top-5 − universe | +0.206%/wk, Sharpe 0.54 | +0.099%/wk, Sharpe 0.32 |
| block-permutation p | **0.035** — passes | 0.0995 — fails |
| chronological split | +0.041% → +0.370%, **9.08×** — fails | +0.041% → +0.158%, 3.87× — fails |

Ranking beats holding everything on the full universe at p 0.035, so some
selection skill exists. **But it lives almost entirely after 2018** — the
early half is +0.041%/week, effectively zero — and it does not clear
significance on the survivorship-controlled universe. Whatever skill the
ranking has is recent and concentrated in recently listed names: the top 5 in
the forward ledger is the same handful of AI-semiconductor names almost every
day. Selection "skill" in 2019–2026 is picking momentum names in a momentum
market.

The falsification fired in a specific way: not "no skill exists" but "skill
exists, is not stable, and is not survivorship-robust." Removing the short leg
does not rescue the strategy. The plan's language on ranking is retired
accordingly.

*Source: `model4_long_vs_universe.py` → `docs/model4_long_vs_universe.md`.*

---

## A hypothesis found by looking — FOMC → GLD by regime · 8 Sep 2026

Not a model and not a test. The retired FOMC→GLD cell (split FAIL 4.62×) was
broken down by regime, descriptively:

| regime | n | h=3 after FOMC |
|---|---|---|
| steep curve, low rates | 50 | −0.37% |
| low long rates, low real rates | 30 | −0.51% |
| **flat curve, strong dollar** | 30 | **+0.42%** |
| rapid money growth, high policy rate | 21 | −1.14% |

The time split failed because its late half pooled the third regime's +0.4%
with the fourth's −1.1% and they cancelled. The effect did not fade with time;
it reverses under one specific condition.

**This is a hypothesis, not a finding.** One regime of four flipping sign is
what a four-way split of noise produces, and every one of the 131 events was
used to find it. It is registered for *forward* testing only — the next FOMC
meetings that land in a flat-curve, strong-dollar regime — and a verdict is
roughly two years away. It is recorded here because a registered directional
prediction per regime is the right thing to have on file, whichever way it
goes.

*Source: `fomc_gld_by_regime.py` → `docs/fomc_gld_by_regime.md`.*

## The kernel family — RUN 8 Sep 2026 · NULL, with one prediction reversed

Three alternative kernels, registered as **one family** so that no single one
can be quoted on its own p-value. The reported result is the best-of-three
against the best-of-three-nulls, per the standing protocol (business plan
§3.4.1).

| kernel | what it tests | prior expectation |
|---|---|---|
| **Regime-only, equal weight** | The floor: every same-regime day, weighted equally, no similarity, no recency. | *Registered prior:* should match Model 1 closely. **Result: Sharpe 0.04 — the floor is zero.** The prior was wrong (logged as #28). Regime membership alone has no ranking power; the kernel is where the spread comes from. |
| **Similarity-only, tight σ** | The ceiling. Drop recency, shrink the kernel so only genuinely close days score. Makes "analog" true. | The no-decay control already ran and was indistinguishable from the incumbent (p 0.485). Expect a null; be pleased if not. |
| **Mahalanobis distance** | Whether similarity is being measured wrong. Euclidean distance lets the first principal component dominate; Mahalanobis normalises by variance. | Untested. The one of the three that could genuinely differ. |

**Why a family and not three models.** Run three and report the best, and the
selection problem that produced Model 3's false 0.73 is reintroduced at small
scale. The family-level test is the correction, and it is committed here before
any of the three runs.

**Result.**

| kernel | ALL Sharpe | p | split | LONG-HIST Sharpe | p |
|---|---|---|---|---|---|
| Model 1 (incumbent) | +0.54 | 0.030 | **3.88×** | +0.26 | 0.164 |
| K0 regime-only | **+0.04** | 0.418 | 1.35× | −0.02 | 0.503 |
| K1 similarity σ=0.75 | +0.44 | 0.065 | **33.3×** | +0.25 | 0.164 |
| K2 Mahalanobis | +0.52 | 0.0498 | 2.94× | +0.35 | 0.110 |

**Family p = 0.114. Null.** Best-of-three was Mahalanobis at 0.52; the
best-of-three null averages 0.23 and reaches 0.61 at its 95th percentile. No
kernel is adopted.

Three things the run established beyond the null:

- **The floor is zero.** Regime-only weighting has no ranking power. Whatever
  Model 1 does, it does through the similarity-and-recency kernel, not through
  regime membership. This reverses the registered prior and a sentence earlier
  in this document.
- **Model 1 fails the chronological split** at 3.88× — a check never run on it
  before. It survives the dependence-corrected null (p 0.045) and fails the
  split. Both facts now stand in the record.
- **Mahalanobis is the only kernel that holds across time** (2.94×). Its own
  p sits at the 0.05 boundary and it fails on the survivorship-controlled
  universe. Not a finding — but the one variant that does not collapse when
  the sample is cut in half, which similarity-only does at 33×.

The paired K0-versus-Model-1 comparison shows a Sharpe gap of 0.49 at p 0.124:
the gap is large, the paired test is underpowered because the two kernels
select almost entirely different baskets, and both facts are reported.

*Source: `kernel_family.py` → `docs/kernel_family.md`.*

---

## What is not claimed

- **No live performance figure.** The forward ledger holds fewer than ten
  non-overlapping trades. Model 1 shows 100% hit-rate on six *overlapping*
  trades — that is beta through a rally, counted six times, and it means
  nothing. The honest column has n = 2.
- **No capacity figure.** Dollar-volume history is not in the repository.
- **No claim that any model is tradeable as a product.** The business plan
  sells a regime label, a document reading, an explicit precision and a rule
  for silence. It does not sell any of the models above as a return stream.

---

## Reading this as an investor

Four models in and the project has retired more than it has kept. That is the
record working as designed. A vendor who reports Sharpe 0.9 from a grid search
cannot become this vendor without admitting the 0.9 was the best of many, and
they kept no record. This one kept the record, and every retirement in it has a
date, a criterion and a file.
