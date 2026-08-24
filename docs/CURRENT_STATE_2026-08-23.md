# CURRENT STATE — 2026-08-23 (AUTHORITATIVE)

*This document supersedes any conflicting statement elsewhere in `docs/`. Where
`PROJECT_STATE.md` and this file disagree, THIS FILE IS CORRECT — the stale
passages are listed in §9 with the reason.*

*A new session can work from this file plus `PROJECT_STATE.md` alone.*

---

## 1. THE ONLY THING WITH A DEADLINE

**Report due to Dr. Lee 2026-08-24. It does not exist yet.**

No forward-test row matures before submission (model_1 ~08-26, model_3
mid-September), so the live test contributes its **design and timestamps**, not
numbers. Everything in §6 survives to next week. Nothing there improves
tomorrow's submission.

---

## 2. ENGINE STATUS — FINAL

| engine | verdict |
|---|---|
| Macro analog (P1) | **Measured.** Sharpe 0.25–0.51, permutation p 0.001 / 0.038 |
| Safe-haven inversion (P1) | **Clean null**, survived panel extension, stress-axis fix, calendar migration |
| Rotation (P2) | **Closed.** 7 hypotheses, 4 instruments, all null |
| Drift-existence (GDELT macro) | **RUN, null** at the registered criterion (prereg 8273be4) |
| PEAD (firm-level) | Criterion not met; H=1 positive but survivorship-contaminated |
| FOMC → GLD | **−0.3% at h=2,3,5**, p 0.028 / 0.0096 / 0.0104 — the only cell to meet its registered criterion |
| Cross-firm spillover | Propagation **instant**: 5/7 GAP, 0/7 INTRA, 0/7 NEXT |
| Forward test | 12 rows through signal 08-21, **0 matured** |

### 2.1 The mechanism that unifies every null

`spillover_test.py` showed NVDA's earnings reprice TSM / ASML / MU / SOXX / SMH /
XSD **entirely in the overnight gap** — nothing survives the open, nothing the
next session. **Every earlier test entered at t+2, after the event had fully
propagated.** Those were not four independent nulls; they were one mechanism
observed four times.

That is why `macro_event_test.py` moved the entry convention to
close-of-event-day, and it is the only reason FOMC→GLD appeared at all.

### 2.2 The look-ahead catch — belongs in the report

Spillover v1 used the announcer's **close** to predict peers' **open-to-close on
the same session**. Result: **6/7 peers significant.** With the tradeable signal
(the announcer's gap, known at the open): **0/7**, four flipping sign. The
announcer's own INTRA went **+2.319% (p=0.0002) → +0.012% (p=0.976)**.

`INTRA_LA` is retained in the output, labelled, as a measured demonstration of
what look-ahead is worth on real data. **This is the strongest methodological
demonstration in the project** — stronger than the universe scan's 148-vs-28,
because it is a self-caught error rather than an argument.

### 2.3 Detail that must not be lost

- **PEAD**: the H=1 effect lives in **TSLA/NVDA/MSFT** (+0.454%, p≈0.01, n=256).
  The four mature laggards are flat (+0.041%, p=0.70). Growth-megacap
  under-reaction and hindsight selection are **indistinguishable on this
  universe**.
- **FOMC→GLD is NOT YET A FINDING.** It meets its criterion but has not had the
  temporal split or the cost test — the two checks that killed both rotation
  pairs. −0.3% clears a 4bps hurdle comfortably, so unlike those pairs it might
  survive. Untested.
- **Universe-wide scan**: 148 pairs clear a naive threshold vs ~28 expected by
  chance; **0 survive** maximum-statistic correction. Caveat recorded: the
  corrected null is inflated by MLPA (18.8σ) and AMLP (17.4σ), so "0 survive" is
  conservative but underpowered. **The usable number is 148-vs-28**, which
  demonstrates empirically why exhaustive search without correction is worthless.
- **Wrong-prior tally: ten.** Several are Claude's. Pattern across the first
  three: results are more *basis-carried* and less *phenomenon-carried* than
  expected. The fourth showed that correction can be over-applied.
  **Tenth (2026-08-24):** "no λ existed anywhere in the codebase, not in
  config.yaml" — asserted in `prereg_recency_kernel.md` §1 and in PROJECT_STATE's
  gap note, **false**; λ was in `config.yaml` and applied in
  `analog_backtest.py`, the engine behind the headline numbers. The lesson is
  narrower than the earlier basis-carried pattern and worth stating separately:
  **a negative claim about a codebase requires a grep, not a reading of the file
  you happen to have open.**
  *(Note: PROJECT_STATE's working-principles list still says "five so far" — it
  stopped being updated at five while this count went to ten. Reconcile.)*

---

## 3. PROBLEM 3 — the LLM layer, the actual product

Steven's design, restated and confirmed 2026-08-23:

1. Match today's macro state to historical analogs, weighted by similarity **and
   recency**.
2. Read today's news **content**, not just its timestamp.
3. **Ask what this kind of news did to each asset IN THE MACRO-SIMILAR PAST**,
   weighted by similarity and recency. ← the core; **never attempted**
4. No macro-matched precedent → fall back to the unconditional effect, labelled
   as weaker evidence.
5. Weigh competing sources landing the same day into a net view per asset.
6. Emit a decision report: which force dominates, direction, horizon, evidence,
   and whether it came from a matched precedent or the weaker fallback.

**Built:** steps 1 and 2. **Not built:** steps 3–6, which are the product.

---

## 4. CORPUS — 623 documents, none of which existed on the morning of 08-23

| source | docs | state |
|---|---|---|
| `fomc_statement` | 131 | fetched, **all read**, reader validated |
| `fomc_minutes` | 125 | fetched, **not yet read** |
| `earnings_8k` | 307 | fetched (8-K domestic + 6-K foreign), **not yet read** |
| `political` | 60 | fetched, **not yet read** — full pull pending |
| `bank_research` | 0 | manual drop |
| `transcript` | 0 | manual drop |

Drop folder: `data_provenance/docs/<source_type>/YYYYMMDD[_id].txt`. Anything in
that layout is readable — fetched by a script or saved by hand. **Files are dated
by when the document became PUBLIC**, not when the event occurred (FOMC minutes
are released ~3 weeks after the meeting; dating them by meeting date would build
look-ahead into a filename).

**Reader validated** against known policy: 2015-12 **+0.6** (first hike),
2020-03 **−0.95** (emergency cuts), 2022-03 **+0.6**, 2022-06 **+0.7**. Range
−0.95..+0.70; |shift|>0.3 on 28 of 131.

### 4.1 Common schema — why it exists

`doc_read.py` emits ONE schema across all sources: direction per asset class
(equity, duration, gold, dollar, oil), magnitude, horizon_days, **specificity**,
novelty, confidence, evidence. Source-specific prompts, comparable output.

**Step 5 is impossible without this.** A hawkish FOMC statement, an NVDA earnings
beat and a tariff order must produce commensurable numbers or there is nothing to
weigh. `specificity` is what separates a signed executive order from a threat to
act — it is the field that makes political sources usable at all.

**The model never predicts returns.** It classifies content; what a given
direction did is answered by data in step 3. This is also the main defence
against outcome leakage on documents the model has seen before.

---

## 5. THREAD 17 — CLOSED (was mislabelled as blocked)

The Federal Register political source **works**. Final run: **60 documents
fetched, 0 unfetchable.**

Two sequential faults, both mine, both now fixed:
1. Server-side filtering on guessed enum values → HTTP 400.
2. The rewrite dropped the `fields[]` parameters, so the API returned summary
   records with **no `raw_text_url`** — 4,652 documents found, all "unfetchable"
   because no text link had been requested.

The invalid field was `presidential_document_type`; the API named it in its own
error body once `get()` was changed to surface the response instead of a bare
HTTP code.

**Real type labels, now visible:**

| type | count |
|---|---|
| proclamation | 2,440 |
| **executive order** | **870** |
| notice | 518 |
| memorandum | 509 |
| determination | 244 |
| other | 59 |
| presidential order | 12 |

**Remaining action:** full pull with `--types "executive order" --limit 400`,
then commit. Not blocked.

**General lesson, worth keeping:** when an API returns records you cannot use,
the problem is almost always *which fields you requested*, not access. Reporting
"the API is inaccessible" when it had returned 4,652 rows was a misdiagnosis.

---

## 6. NEXT ACTIONS, in order — none required for the report

1. **Write the report.** Nothing competes with this.
2. Full `political` pull; commit; close Thread 17 in PROJECT_STATE.
3. `python -m src.doc_read --all` — read minutes + 8-K + political through the
   common schema. **Check `specificity` SEPARATES sources**: decided policy and
   reported earnings high, rhetoric and opinion low. If it does not discriminate,
   step 5 has nothing to weigh with and the prompt needs fixing first.
4. **λ sweep** on the registered ladder {2, 4, 8, 16, ∞}, all rungs reported.
5. **Build step 3** — the analog-conditioned event effect. Nothing else is the
   product.

**Standing:** `python -m src.forward_log` daily, never retro-filled. Currently
clean — last signal 08-21 (Friday); 08-22 was a Saturday.

---

## 7. THE λ CHARACTERISATION — limits what the sweep can show

The mechanism is built (`analog_core._kw(dist, spec, age_years)`, opt-in via
`half_life_years`; `None` reproduces prior weights bit-identically, so the frozen
live models are untouched). Pre-registered: exponential, HL = 4 years, ladder
{2,4,8,16,∞}. **The sweep has NOT been run.**

> **SCOPE CORRECTION 2026-08-24.** The table below characterises
> **`analog_core`** only. `analog_backtest.py` — the engine behind the reported
> 0.51 / 0.25 — has decayed all along at `recency_decay_lambda = 0.0008`/session
> (HL ≈ 3.44y). Its "no decay" behaviour has never been measured; that is the
> ∞ rung of Engine B and it is the point of running the sweep. The claim in §9
> that the kernel was merely "BUILT, sweep unrun" understates this: the sweep is
> also a **correction to the record**, not only an extension of it.

**Measured before any return was computed:**

| | no decay | exponential HL=4y |
|---|---|---|
| median ESS (of top-k 100) | **100.0** | 99.9 |
| weighted mean analog age | **0.40 y** | 0.24 y |
| top-k overlap vs no-decay | 1.00 | 0.80 |

Three consequences, and they belong in the report:

1. The engine **already** draws almost entirely from the recent past — five
   months with no recency weighting at all. λ moves that to three months. The
   recency kernel is close to redundant because macro states are persistent.
2. **ESS is 100 of 100.** Weights are effectively uniform; σ=1.5 is wide enough
   that the similarity kernel barely discriminates. The "similarity-dominant"
   weighting in the locked design is **not occurring**.
3. The engine behaves closer to **"average the recent same-regime past"** than to
   "find the 2008 analog and learn from it." Not a bug — nothing computes
   incorrectly — but **the word *analog* currently promises more than the
   mechanism delivers.**

**The lever is σ, not λ.** σ is frozen in `models.yaml` for the live test and was
not touched.

---

## 8. DECISIONS DEFERRED — before any product launch, not before submission

1. **Manual-collection sources cannot scale to a daily product.** `transcript`
   and `bank_research` have no free structured feed. Options: buy a vendor feed;
   declare a coverage gap to the customer; or drop them from the live product and
   keep them for research. **None chosen.**
2. **The political source is biased toward DECIDED policy.** Federal Register
   carries executive orders and proclamations — all high-specificity by
   construction. Statements, posts and rhetoric — precisely where a market-moving
   threat-to-act lives — are **not covered**. X's historical archive is the paid
   tier and Truth Social has no public API, so this is a **purchasing decision**.
   **An absence of low-specificity political events in any result is a COVERAGE
   GAP, not evidence that rhetoric does not move markets.**
3. **Foreign private issuers file 6-K, not 8-K.** 6-K carries no item codes, so
   the Item 2.02 filter that isolates earnings releases for domestic filers has
   no equivalent. Foreign issuers arrive with **lower precision**; cross-firm
   comparison must account for the asymmetry.

---

## 9. STALE PASSAGES IN `PROJECT_STATE.md` — corrected here

| stale claim | correct as of 2026-08-23 |
|---|---|
| Status block + open thread 1: drift-existence "PRE-REGISTERED and UNRUN" | **RUN and NULL.** See `docs/drift_existence_results.md` |
| Appendix: recency kernel "was designed and never built" | **BUILT** (`analog_core._kw` takes `half_life_years`), prereg committed. **The SWEEP is unrun** |
| Thread 17: political source "not working" | **WORKING.** 60 docs fetched, 0 unfetchable. Full pull pending |

**FILE HAZARD:** a standalone `PROJECT_STATE.md` in `~/Downloads` was **98 lines
shorter** than the copy inside `briefing.md` — it predates the 08-23 appendices
(λ gap, event source registry, deferred decisions, thread 17). **Do NOT `cp` it
over the repo copy; it would delete all of them.** Check `ls -lt ~/Downloads`
first — this is the `name-1.md` hazard the process notes already warn about.

---

## 10. SECURITY

An Anthropic API key was pasted into a chat transcript on 2026-08-23. **Revoke it
at console.anthropic.com if not already done.** The replacement lives in
`~/.zshrc` as `ANTHROPIC_API_KEY` and appears in no file. `.gitignore` covers
`.env`, `*.key`, `**/secrets*`.

Also required in the environment: `SEC_CONTACT` (EDGAR requires a contact email
in the User-Agent).

---

## 11. THE REPORT'S SPINE

Two clean nulls that survived every basis change thrown at them. Two
positive-looking results that collapsed the moment they were split by time. One
measured engine with its caveats declared rather than defended. One
pre-registered test held back with a power argument. A live forward test with
timestamps and no matured rows. And one mechanism — instant overnight
propagation — that explains why the earlier entry convention found nothing.

**The honesty is the finding.** Every null came from an instrument demonstrated
to detect a planted effect *first*: `--inject` recovered a planted lead at
d = +0.502, p = 0.0005 on the real panel before any null was reported.

---

document did not cover. Sections 0a and 0b are report-blocking; 0c and 0d are
not.*

---

## 0a. AMENDMENT LOG — `prereg_drift_existence.md` §9 is EMPTY and must not be

`docs/drift_existence_results.md` reports an amendment that was made. The log
that exists specifically to make amendments visible does not contain it.

The amendment is defensible on its merits — it was recorded in-file **before any
result was read**, and the registered design was genuinely infeasible. But an
empty amendment log sitting next to a documented amendment is **the one place a
reader can pull at the pre-registration discipline that is this report's spine.**
Highest value per minute of anything outstanding.

**Paste this into §9 of `docs/prereg_drift_existence.md`:**

| date | change | reason |
|---|---|---|
| 2026-08-23 | §4.2 control buffer changed from a flat ±20 sessions to **H+2** sessions | The registered ±20 buffer is **infeasible on a 659-session panel**. At z≥1.0 there are 70 episodes; 70 × 41 slots cover the panel several times over, so **no control day survives**. The first run returned empty pools and `p(matched)=1.0000` for every cell. The registered relaxation order covers the era window and the vol quintile but **not** the buffer, so the buffer bound to zero. H+2 is what the buffer's stated purpose — stopping a control's forward window overlapping an event's — actually requires; the flat 20 was sized for the longest horizon and applied to all. **Recorded before any result was read.** Estimands, thresholds, ladder, de-clustering, entry convention, nulls and success criterion all UNCHANGED. |

---

## 0b. REGISTRATION STATUS — three results are registered IN CODE, not in a
## prereg document. Say so precisely.

`docs/` contains four prereg documents: cross-asset rotation, drift-existence,
recency kernel, sector rotation. **FOMC→GLD, PEAD and cross-firm spillover have
none.**

Their parameters were fixed in a **script docstring committed before the run** —
estimand, nulls, horizons and success criterion all stated in advance, with a git
timestamp that predates execution. That is real evidence. It is **weaker than
`8273be4`** (a standalone registration reviewed before any code existed) and
**stronger than exploratory**.

| result | registration | commit |
|---|---|---|
| Drift-existence | standalone prereg document | `8273be4`, 2026-08-21 13:18:53 |
| Cross-asset + sector rotation | standalone prereg documents | `b4a942a` |
| Recency kernel (λ) | standalone prereg document | committed, sweep unrun |
| **FOMC → GLD** | **docstring in `macro_event_test.py`, committed before the run** | `8640d2d` |
| **PEAD** | **docstring in `pead_test.py`, committed before the run** | `8be9fcd` |
| **Cross-firm spillover** | **docstring in `spillover_test.py`, committed before the run** | `78419d0` |

**Required phrasing in the report** — use this, not "pre-registered" unqualified:

> *"Parameters were registered in a script docstring committed before the run
> (commit `<hash>`), rather than in a standalone pre-registration document."*

**DO NOT back-fill prereg documents for these three now.** Writing a registration
after seeing results and dating it today would be materially worse than the
honest description — and the honest description is genuinely strong, because the
commits verifiably predate the runs. `git log --format='%H %cd' -- <script>`
proves it.

**FOMC→GLD is the sentence most likely to be challenged**, being the only
positive event result. It is also — separately — **not yet a finding**: no
temporal split, no cost test. The −0.3% clears a 4bps hurdle comfortably, which
is more than either rotation pair managed, but neither check has been run.

---

## 0c. PROJECT_STATE READS WRONG LINEARLY at three points (cosmetic, not
## correctness)

CURRENT_STATE §9 supersedes them, and a supersede pointer is appended at the end
of the file — but anyone reading top-to-bottom hits the stale version first.

| line | stale text | correct |
|---|---|---|
| ~89 | event engine "UNRUN" | run, null |
| ~671 | thread 1 "PRE-REGISTERED, UNRUN" | run, null |
| ~960 | thread 17 heading "BUILT BUT NOT YET WORKING" | **CLOSED** — 60 docs, 0 unfetchable |

Fix after the report:

```bash
cd ~/Projects/regime-aware-signal
python - <<'PY'
from pathlib import Path
p = Path("docs/PROJECT_STATE.md"); s = p.read_text(); n = 0
for a, b in [
    ("OPEN THREAD 17 — political source, BUILT BUT NOT YET WORKING",
     "OPEN THREAD 17 — political source, CLOSED 2026-08-23 (60 docs, 0 unfetchable)"),
    ("the event-engine **drift-existence test** — still unrun",
     "the event-engine **drift-existence test** — RUN 2026-08-23, NULL"),
]:
    if a in s:
        s = s.replace(a, b); n += 1
p.write_text(s); print(f"patched {n}")
PY
```

Assertion-free by design: if an anchor has already changed it patches nothing
rather than corrupting the file.

---

## 0d. PIPELINE.md DOCUMENTS NONE OF THE LAST TWO DAYS' SCRIPTS

Missing: `macro_event_test.py`, `spillover_test.py`, `doc_read.py`,
`fetch_sources.py`, `recency_diagnostic.py`, and also `episode_rotation.py`,
`pair_confirm.py`, `conditional_order.py`, `universe_scan.py`,
`drift_existence.py`, `pead_test.py`, `fomc_corpus.py`, `fomc_llm_read.py`,
`fetch_fomc_dates.py`, `recency_patch.py`, `make_gdelt_csv.py`, `app.py`.

**That is every script behind the FOMC result, the spillover mechanism, the
corpus and the terminal.** PIPELINE.md exists so a reviewer — Dr. Lee — can
navigate the repo. It currently describes a repo that stopped changing on
2026-08-21.

Post-submission. Add a section per group: event tests, LLM/corpus layer,
diagnostics.

---

## REVISED ACTION ORDER

| # | action | blocking? |
|---|---|---|
| **0a** | Paste the amendment row into `prereg_drift_existence.md` §9 | **yes, 10 min** |
| **0b** | Adopt the "registered in a committed docstring" phrasing | **yes, wording only** |
| **1** | **Write the report.** Spine in CURRENT_STATE §11 | **yes — the deadline** |
| 2 | Full political pull; commit; close thread 17 | no |
| 3 | `doc_read --all`; gate = does `specificity` separate sources | no |
| 4 | λ sweep {2,4,8,16,∞}, all rungs | no |
| 5 | Build step 3 — the analog-conditioned event effect | no |
| 6 | Fix PROJECT_STATE lines 89 / 671 / 960 (0c) | no |
| 7 | Update PIPELINE.md with 17 scripts (0d) | no |

**Standing:** `forward_log` daily, never retro-filled. Clean — last signal 08-21,
08-22 was a Saturday.

**Security:** revoke the API key pasted into chat on 2026-08-23.

---

## 12. FILE DISCIPLINE — one state document, appended, never forked

**Everything new goes at the end of THIS file.** No new state documents, no
addenda, no handoffs. Two files describing the same state is how the drift in §9
happened in the first place.

`app.py` (the Streamlit terminal) was written in chat on 2026-08-23 and **never
saved to the repo — it does not exist**. Rebuild it from this document when the
engines are settled, or drop it: it is a demo, not a deliverable. Its earlier
version showed an evidence tab that predated the rotation closure, the PEAD
result and the spillover finding, so rebuilding beats recovering.

---

## 13. STEPS 1 AND 2 — WHAT IS ACTUALLY COMPLETE (2026-08-23)

Neither step is finished. Precisely:

**Step 1 — BUILT, UNTESTED.** The λ mechanism is in `analog_core._kw`,
invariance-verified (bit-identical when `half_life_years=None`, so frozen live
models are untouched). Pre-registration committed. Four `model_1_recency_*`
entries added to `models.yaml`. **The sweep has NOT been run — zero rungs
executed. λ has never touched a return.**

**Step 2 — ONE SOURCE OF SIX READ.**

| source | fetched | read |
|---|---|---|
| fomc_statement | 131 | **131** (validated against known policy) |
| fomc_minutes | 125 | **0** |
| earnings_8k | 307 | **0** |
| political | 60 | **0** |
| transcript | 0 | 0 — not yet collected |
| bank_research | 0 | 0 — not yet collected |

**492 of 623 documents unread.**

Two further gaps that matter more than the count:

- **The common schema has been exercised on 3 documents.** The 131 FOMC reads
  used the EARLIER stance-only schema (`fomc_llm_read.py`). The cross-source
  schema in `doc_read.py` — direction per asset class, magnitude, specificity,
  novelty — has only run under `--limit 3`.
- **The `specificity` gate is UNCHECKED.** That field is what makes step 5
  possible: decided policy and reported earnings should score high, rhetoric and
  opinion low. If it does not discriminate across sources there is nothing to
  weigh with, and the prompt is wrong before any conditioning matters. Untested,
  because only one source has been read.

**Honest sentence for the report:** *step 1 built and untested; step 2
infrastructure built and validated on one source, 79% of the corpus unread, two
sources uncollected, the discriminating gate unverified.*

## 14. DECISIONS TAKEN IN THIS SESSION — reasoning, not just outcome

**Anthropic API, not Claude Code, as the runtime.** The business plan sequences
**institutional software licensing first**. That means a system running on a
customer's schedule and producing reports for them — it has to be embeddable and
programmatic. Claude Code is a developer's workstation tool and cannot be the
runtime inside a licensed product. Use it to BUILD if convenient; the pipeline
calls the API.

**Bank research: top-4 investment banks, published SUMMARIES only, collected
manually.** Not all institutions, and not the reports themselves — actual
research is a licensed product, and redistributing it inside something you sell
is real exposure for the institutional-licensing line, which is exactly the
segment that audits for it. Media write-ups ("Goldman raises S&P target to X")
are public and fine.

**Transcripts: collected manually by Steven**, saved directly to
`data_provenance/docs/transcript/YYYYMMDD_id.txt` in the repo — not sent through
chat, which would leave them unversioned and unreproducible.

**Trump / Iran: route through GDELT, not the X API.** ACTION, not just a deferred
decision. GDELT infrastructure and 944 days of history already exist and are
backtestable; the X archive is the paid tier and without history a source can
never enter step 3. Needs a themes/actor filter added to the existing GDELT
query. GDELT returns article COUNTS, not text, so it is a TRIGGER for step 3
conditioning rather than a document for `doc_read` — a different role from the
Federal Register source, and it should not be conflated with it.

**Governing principle, stated by Steven:** `PROJECT_STATE.md` and `briefing.md`
are where the core research design lives, and the build follows them. Where an
implementation has drifted from the design, **the design is correct and the
implementation is the defect** — which is how the λ gap was found.

---

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
