> **SUPERSEDED 2026-09-13.** This file is a dated snapshot and is no longer maintained. For current status read `docs/TRACK.md`; for model results read `docs/MODEL_EVOLUTION.md`. Statements here about schedules, what is built, or what is pending may be wrong.

# EXECUTION PLAN — Problem 3, steps 1–7 (agreed 2026-08-23)

*Append to `docs/CURRENT_STATE_2026-08-23.md`. This is the whole plan through to
a working product: engines finished, report written, demo built. Every
pre-registration decision that must be made before a number is looked at is
marked **REGISTER FIRST**.*

*Standing rule: nothing here is more important than the report due 2026-08-24.*

---

## STEP 0 — Two things before anything else (30 minutes total)

| # | action | why |
|---|---|---|
| 0a | Log Amendment 1 in `prereg_drift_existence.md` §9 | An empty amendment table beside a documented amendment is the one place a reader can pull at the discipline the report rests on |
| 0b | Adopt the phrasing *"registered in a script docstring committed before the run (commit X)"* for FOMC→GLD, PEAD, spillover | They have no standalone prereg. Weaker than `8273be4`, stronger than exploratory. Do NOT back-fill documents — the commits verifiably predate the runs, and a registration written today would be worse |

---

## STEP 1 — Macro analog engine

**What it does.** Finds past days resembling today, weighted by similarity **and
recency**, and averages what each asset did next.

**What to run, in order:**

1. **λ ladder, ∞ first.** No-decay must reproduce the frozen number
   **bit-for-bit** before any decayed rung is trusted — otherwise a later change
   cannot be attributed to λ rather than a bug. Then 16, 8, 4, 2. **All five
   reported, no cherry-picking.** Primary is HL=4y on presidential-term grounds;
   registered in `prereg_recency_kernel.md`.
2. **`_z()` expanding-window rerun.** `analog_core._z()` standardises PC features
   using full-panel moments, so distances at 2010 use moments through 2026. Same
   class as the frozen regime model but never declared. Recompute with
   expanding-window moments and **report both Sharpes side by side.**
3. **Same-horizon level-vs-trend cells** from the existing grid — isolates the
   trend effect that model_1-vs-model_2 never did (they differ in two things at
   once).
4. **Write down the ESS characterisation** as a stated limitation, not a
   footnote.

**Ordering:** items 2–4 are independent of the corpus and can run **in parallel
with** step 2's reading, which is API-bound. Do not serialise them behind it.

> **REGISTER FIRST — already done.** Ladder {2,4,8,16,∞}, exponential, HL=4y
> primary, success requires the long-history universe at the primary rung AND
> stability across three adjacent rungs. **A single winning rung is a grid
> winner, not a finding.**

**Registered expectation: little or no improvement.** With NO decay the weighted
mean analog age is already **0.40 years** and median ESS is **100/100** — the
engine averages the recent same-regime past with near-uniform weights rather than
locating distinctive analogs. **The lever is σ, not λ**, and σ is frozen for the
live test. **A large Sharpe change would be suspect, not success.**

---

## STEP 2 — Read the news

**What it does.** Turns every document into the same numbers — direction per
asset class, magnitude, specificity, novelty, confidence. **Never touches
prices.**

**Order matters, and it removes a dilemma:**

1. **Full political pull first.** `--types "executive order" --limit 400`. You
   have 60 of ~870; reading 60 now means re-reading later. One command.
2. **Pilot read: `--limit 20` per source**, five sources, ~100 documents. Cheap.
3. **Check the gate on the pilot** (below).
4. **Only then the full ~800-document pass.**

This is why the plan's "re-read or declare" dilemma never arises: the gate is
checked on 100 documents, not 492.

**`--with-prev`:** **ON** for `fomc_minutes` — read as deltas, like statements.
**OFF** for `earnings_8k` — the folder mixes issuers, so the "previous document"
would belong to a different company. **OFF** for `political` — consecutive
executive orders are unrelated.

---

## GATE — does `specificity` discriminate?

**Test:** mean `specificity` by source on the pilot. Expected ordering:

| high | low |
|---|---|
| executive orders (decided policy) | bank research (opinion) |
| 8-K Item 2.02 (reported results) | transcripts (forward-looking talk) |
| FOMC statements (decided) | |

> **REGISTER FIRST:** the gate passes if the **spread between the highest and
> lowest source mean exceeds 0.25**, and decided-policy sources rank above
> opinion sources. Write this number down before looking.

**If it fails:** fix the prompt and re-read the pilot — ~100 documents, not 492.
Proceeding with a non-discriminating `specificity` means step 5 has nothing to
weigh with, and no downstream statistic can rescue it.

---

## STEP 3 — Analog-conditioned event effect **← the product**

**What it does.** Takes today's document; finds past days that carried a similar
*kind* of document **and** were macro-similar to today, weighted by similarity
and recency; measures what each asset actually did.

Write `src/analog_event.py`. **Needs the full corpus** — "similar kind of
document" is meaningless with one source in it.

> **REGISTER FIRST — five decisions, all before any number is seen:**
>
> **(a) Document similarity.** Cosine distance on the five `direction` fields
> plus `magnitude`. Explicitly EXCLUDE `novelty` and `confidence` — they describe
> the *reading*, not the *content*. Include `specificity` only if the gate passed.
>
> **(b) Its own σ and λ**, declared separately from the frozen live models. σ
> governs macro-state matching; a second σ governs document matching. Both need
> stated values with reasoning, not tuned ones.
>
> **(c) Success criterion.** *The conditioned effect must beat the unconditional
> fallback (step 4) on the same events, at two adjacent horizons, in the
> registered direction.* Step 4 IS the baseline — that is why it is built first.
> Without this, you read a number and decide afterwards whether you like it.
>
> **(d) Null.** Shuffle the macro-analog weights across events, preserving group
> sizes and every path, destroying only the correspondence between macro state
> and outcome. `conditional_order.py` already implements exactly this and
> transfers directly.
>
> **(e) Power / MDE.** 131 FOMC events across analog neighbourhoods gives perhaps
> **20–30 effective per neighbourhood** — the wall every test in this project has
> hit. **Compute the MDE before the run.** If the detectable effect exceeds what
> is plausible, say so in advance and report a null as inconclusive rather than
> as absence.

---

## STEP 4 — Unconditional fallback

**Build this BEFORE step 3.** It is the baseline step 3's criterion is defined
against.

Same call with macro weights off. Output labelled **weaker evidence**.

> **REGISTER FIRST:** the cut-off. **Fewer than 10 macro-matched precedents →
> fall back and label it.** Below that the conditioned estimate is noise wearing
> a precedent's clothes. `pair_confirm.py` and `episode_rotation.py` both use
> this threshold; keep it consistent.

Already existing as tier-4 results: **FOMC→GLD −0.3%** (registered in a
docstring; **not yet a finding** — no temporal split, no cost test).

---

## STEP 5 — Weigh competing sources

**What it does.** FOMC statement, earnings release and tariff order land the same
day and disagree → one net view per asset.

> **REGISTER FIRST:** the combination rule, written before it runs.
>
> Recommended: `weight = magnitude × specificity × novelty × confidence`, then
> `net_direction[asset] = Σ(weight × direction[asset]) / Σ(weight)`.
>
> Straight product means **any near-zero field kills the document** — which is
> the intended behaviour for a low-specificity threat. If you want specificity to
> dominate rather than merely veto, use `specificity^2`. **Pick one, write it
> down, do not tune it against outcomes.**
>
> The honest alternative: **estimate the weights from history** — which source
> historically dominated when they disagreed. That is the better answer and it
> needs the full corpus plus enough same-day collisions. Count them first; if
> there are fewer than ~50, use the fixed rule and say why.

---

## STEP 6 — Decision report

**The customer-facing artifact — the business plan's actual deliverable.**

**Format:** one Markdown file per day at `outputs/reports/YYYYMMDD.md`, plus the
same content as JSON for the app. Both from one function so they cannot diverge.

**Must contain:**
- current macro state, regime, and **posterior confidence** (a below-60% posterior
  is a warning, not a footnote);
- each document read today: source, direction, magnitude, specificity, evidence
  quotes;
- the **net view per asset** with the dominant source named;
- **whether it came from a macro-matched precedent or the fallback**, and how many
  precedents backed it;
- what the system **cannot** see — the coverage gaps in §8;
- **no performance number that has not matured.**

Then rebuild `app.py` around this. The old version was never saved and its
evidence tab predates the rotation closure, the PEAD result and the spillover
finding — **rebuild, do not recover.**

---

## STEP 7 — Daily operation

**Missing from every earlier plan.** Steps 1–6 build a historical engine; nothing
schedules it. This is the gap between a study and a product.

- `cron` or `launchd` at 07:45 SGT: `forward_log`, then fetch new documents, read
  them, emit the day's report.
- **Fail loud, never silently.** Same discipline as `forward_log`: a missed day is
  an honest gap, never retro-filled.
- Live sources: FOMC, EDGAR, Federal Register — all automated. Transcripts and
  bank research are manual, which is deferred decision #1 and must be resolved
  before launch.

---

## ANSWERS TO THE OPEN QUESTIONS

| question | answer |
|---|---|
| Which λ rung first? | **∞ (no decay)** — confirm bit-for-bit reproduction of the frozen number, so any later change is provably λ |
| `_z()` and level-vs-trend before or after corpus work? | **In parallel.** Corpus reading is API-bound; these are CPU-bound and independent |
| Political pull before reading? | **Before.** 60 of 870 means re-reading later; the full pull is one command |
| `--with-prev`? | **ON** for minutes; **OFF** for 8-K and political |
| Fix prompt or declare if the gate fails? | **Neither** — pilot on 20/source first, so a failed gate costs ~100 documents, not 492 |
| How is "similar kind" defined? | Cosine on `direction` + `magnitude`; exclude `novelty`/`confidence`; `specificity` only if the gate passed |
| Fallback cut-off? | **<10 matched precedents** |
| How do the four fields combine? | Product, or `specificity^2` if it should dominate. **Register before running** |

---

## THINGS THAT WILL BREAK THIS IF FORGOTTEN

1. **Power.** 20–30 effective events per neighbourhood is the same wall as
   everywhere else. MDE before the run, not an explanation after.
2. **The gate is a real gate.** If `specificity` does not discriminate, step 5 is
   impossible and no statistic downstream fixes it.
3. **Step 4 before step 3.** The baseline defines the criterion.
4. **σ, not λ.** ESS 100/100 and mean analog age 0.40y say the engine is not doing
   what "analog" implies. Say it in the report.
5. **Register before running.** Every result in this project that survived
   scrutiny had its criterion written first; every one that collapsed was found
   by a test registered in advance.


---

## SESSION CLOSE 2026-08-25 — STEP 1 DONE, STEPS 3–6 REGISTERED AND BUILT BLIND

*Detail lives in `docs/CURRENT_STATE_2026-08-23.md` §15. This records only what
changes in this file, including where the plan was wrong.*

**STEP 0 — CLOSED.** 0a was already done when this plan was written. 0b's
phrasing stands: FOMC→GLD, PEAD and spillover are registered in **script
docstrings committed before their runs** (`8640d2d` / `8be9fcd` / `78419d0`).
No prereg was back-filled.

**STEP 1 — CLOSED, SEVEN ITEMS** (the plan listed four; three were added as
earlier items surfaced them):

| item | verdict |
|---|---|
| λ ladder, **both engines** | A POSITIVE, B NULL → **reframed exploratory** |
| rung-level selection diagnostic *(added)* | **RESELECTION on both engines** |
| fine λ scan *(added)* | surface **jagged**; dip **unexplained** |
| adjacent-rung count | **4**, strictly monotone |
| `_z()` expanding-window rerun | small for level, **large for trend** |
| same-horizon level-vs-trend | **the trend advantage IS the look-ahead** |
| Engine B no-decay vs incumbent *(added)* | **not distinguishable**, p 0.485 |

**Where this plan was wrong.** Its *"the lever is σ, not λ"* was scoped to the
macro panel and stated as general. And **λ already existed**: `config.yaml`
carries `analog.recency_decay_lambda: 0.0008` (HL 3.44y) and `analog_backtest.py`
applies it, so the reported 0.51 / 0.25 always carried decay. The plan and the
prereg it cited both said the opposite.

**STEP 2 AND THE GATE — CLOSED.** The pilot-then-gate sequencing worked exactly
as designed: a 20-document pilot caught that the entire 307-document
`earnings_8k` corpus was **SEC cover pages**, before anything was spent on the
full read. **GATE: PASS**, n=60×4, spread 0.363, CI [0.279, 0.453]. Two
amendments, both declared, in `prereg_analog_event.md` §11. **Re-run
`gate_check` once the corpus completes** — `political_other` was n=60 of 816.

**STEPS 3–6 — REGISTERED (74b88dc), 3+4 BUILT BLIND, 6/6 TESTS PASS.**

**Where this plan was wrong.** Step 4's hard *"<10 precedents → fall back"*
cutoff is **replaced** by a precision-weighted blend `w = ESS/(ESS+k)`, because
nothing real changes between 9 and 10 precedents. **k is estimated, never
chosen.** The floor survives only as an **abstention** rule at ESS < 8. Steps 3
and 4 are therefore one estimator, `src/analog_event.py`.

**WHAT IS LEFT** — authoritative list is `CURRENT_STATE` §15.11. The report does
not exist and the deadline has passed.

**"THINGS THAT WILL BREAK THIS" all held.** Power was binding everywhere. The
gate was a real gate and caught a dead corpus. Step 4 was built before step 3.
σ-not-λ was right in direction, wrong in scope. And every result that survived
had its criterion written first — while **nine claims were retired**, each by a
test registered before it ran.
