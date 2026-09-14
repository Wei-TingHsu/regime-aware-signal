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


---

## 15. SESSION 2026-08-24/25 — STEP 1 CLOSED, GATE PASSED, ESTIMATOR BUILT

*Appended per §12: everything new goes at the end of this file. This section
supersedes §2, §3, §7, §11, §13 and the REVISED ACTION ORDER above wherever they
conflict. The earlier text is left in place deliberately — several findings below
are corrections to it, and deleting the error would delete the evidence.*

---

### 15.1 THE ONE-LINE STATE

Step 1 is **closed** — seven items, all run. The specificity gate **passed** on a
tightened criterion. The step 3 estimator is **built blind and passes 6/6**
acceptance tests. The corpus read is **in progress** after an overnight credit
exhaustion. Steps 4–6, `app.py` and automation remain unbuilt.

**The report does not exist. The deadline (§1) has passed.**

---

### 15.2 STEP 1 — ALL SEVEN ITEMS, WITH VERDICTS

| # | item | verdict |
|---|---|---|
| 1a | λ ladder {2,4,8,16,∞}, both engines | Engine A POSITIVE, Engine B NULL — **reframed exploratory**, see 15.3 |
| 1a′ | rung-level selection diagnostic | **RESELECTION on both engines** |
| 1a″ | fine λ scan around the incumbent | surface **jagged**; dip **unexplained** |
| 1a‴ | adjacent-rung count | **4**, strictly monotone (code said 5, an earlier reading said 3 — both wrong) |
| 1b | `_z()` full-panel look-ahead | **measured**: small for level, large for trend |
| 1c | same-horizon level-vs-trend | **the trend advantage IS the look-ahead** |
| 1d | ESS characterisation | superseded by 1a′, which answers it better |
| 1e | Engine B no-decay vs incumbent, paired | **NOT DISTINGUISHABLE** — retires a claim, see 15.4 |

---

### 15.3 λ EXISTED ALL ALONG, AND THE LADDER DOES NOT MEASURE WHAT IT CLAIMS

**`prereg_recency_kernel.md` §1 and PROJECT_STATE both asserted "no λ exists
anywhere in the codebase, not in config.yaml." FALSE.** `config.yaml` carries
`analog.recency_decay_lambda: 0.0008` and `analog_backtest.py` applies it in
**sessions** — HL = ln2/0.0008/252 = **3.44 years**. `analog_backtest.py` is the
engine behind the reported 0.51 / 0.25, so **those figures always carried decay.**

Two engines, not one, and they are different estimators:

| | `analog_core` (Engine A) | `analog_backtest` (Engine B) |
|---|---|---|
| features | z-scored PCs | **raw** PCs, PC1 dominates distance |
| regimes | one GMM on all history | refit expanding, every 20 sessions |
| decay | none by default | λ = 0.0008/session all along |
| baseline Sharpe | 0.40 | 0.25 long-history |

Ladder verdicts **disagree**: Engine A POSITIVE (primary 0.3205 > control
0.2526, strictly monotone over 4 rungs), Engine B NULL (primary 0.3200 <
control 0.3800). At 16y, 8y and 4y the two engines agree within 0.04 — **the
entire flip comes from Engine B's ∞ rung.**

**The rung diagnostic (`docs/rung_diagnostic_results.md`) settles what λ is
doing, and it is not what the locked design claims.** Registered threshold:
top-k overlap ≥ 0.90 versus the no-decay control = tie-breaking. Measured at the
primary rung: **Engine A 0.765, Engine B 0.850. Both RESELECTION.** ESS holds at
~99.6 of 100 at every rung on both engines — λ does not concentrate weight, it
**swaps membership**. Combined with σ=1.5 being too wide to discriminate, both
engines reduce to:

> pick the 100 most recent same-regime days, then average them with equal weight.

**The word *analog* describes neither engine.** The ladder measures "does
restricting to recent history improve returns", not "does gentle recency decay
improve analog quality". The report must say the latter.

**Status: the ladder result is REFRAMED AS EXPLORATORY.** The numbers stand; the
interpretation registered in `prereg_recency_kernel.md` §6 does not.

---

### 15.4 THE λ SURFACE IS JAGGED, AND THE 0.38-vs-0.25 GAP IS NOT REAL

`docs/fine_lambda_sweep_results.md`, exploratory and post-hoc by construction.
Engine B long-history across λ steps of 1e-4:

| λ | 0.0007 | 0.0008 | 0.0009 | 0.0010 |
|---|---|---|---|---|
| Sharpe | 0.30 | **0.25** | 0.22 | 0.29 |

The incumbent re-ran at exactly 0.2500 — **not a measurement error**. Per
`prereg_rung_diagnostic.md` §3.3 the interior dip is **unexplained**: Engine B
top-k overlap runs 0.950 / 0.910 / 0.850 / 0.800, smooth, no discontinuity
between 4y and 2y to attribute it to.

**Consequence: rung-to-rung differences on Engine B are the same order as the
jitter between adjacent λ values.** Engine B's NULL verdict rests on differences
indistinguishable from surface roughness.

**1e tested the headline gap directly** (`docs/engine_b_paired_results.md`),
sign-flip on 836 paired rebalances, criterion registered before implementation:

| universe | no-decay | incumbent | Sharpe diff | mean spread diff | p |
|---|---|---|---|---|---|
| ALL | 0.5251 | 0.5165 | +0.0087 | **−0.0105%** | 0.896 |
| LONG-HISTORY | 0.3837 | 0.2528 | +0.1309 | +0.0579% | **0.485** |

> **RETIRED CLAIM.** On 2026-08-24 it was asserted that "the incumbent decay was
> costing you Sharpe — long-history 0.25 → 0.38 with it removed" and that this
> belonged in the report. **Not supported.** p = 0.485. Reported as *not
> distinguishable at this sample size*, which per §3.2 is **not** evidence the
> two are equal.

**Keep the ALL row.** Sharpe favours no-decay (+0.0087) while mean spread favours
the incumbent (−0.0105%) — **they disagree in sign.** Sharpe is mean/sd, so a
Sharpe gap can be produced entirely by volatility. A live demonstration on real
data that a Sharpe difference cannot be read as a mean difference.

**λ=0.0008 stays in `config.yaml` permanently.** It is the reproduction constant
for the recorded headline figures; setting it to zero makes them unreproducible.
It has never been in the live path (model_1/2/3 carry no `half_life_years`) and
is off-ladder, so it can never be promoted.

---

### 15.5 THE DECLARED `_z()` LOOK-AHEAD, MEASURED — AND THE TREND EFFECT IS IT

Open thread 12 said *"expected to be small is not measured."* Now measured
(`docs/scaling_check_results.md`), identical spec, identical rebalance dates,
only the standardisation window differing, min_periods 252:

| model | universe | full-panel | expanding | diff | paired p |
|---|---|---|---|---|---|
| model_1 (level) | long-hist | 0.2526 | 0.2406 | +0.012 | 0.940 |
| **model_2 (trend)** | **long-hist** | **0.4131** | **0.1522** | **+0.261** | **0.057** |
| model_3 (trend) | long-hist | 0.4947 | 0.3568 | +0.138 | 0.500 |

**Small for level, large for both trend models.** Mechanism: `sim_mode='trend'`
z-scores the **differenced** PCs, and macro momentum volatility is dominated by
2008 and 2020, so a full-panel sd for that block encodes future volatility
regimes far more than the level block's does.

Pool shrinkage is **0.0%** for all three, which rules out the alternative
explanation that a smaller analog pool caused it.

**Thread 8 then resolves** (`docs/trend_check_results.md`). model_1 and model_2
differ in horizon AND sim_mode, so that comparison supported neither the original
claim nor its retirement. Fixing horizon and varying only `sim_mode`, across
4 horizons × 2 sigmas × 2 universes:

| basis | mean trend−level (long-hist) | trend ahead in |
|---|---|---|
| full-panel | **+0.1137** | 6/8 cells |
| expanding | **−0.1213** | 3/8 cells |

> **On this panel the trend advantage IS the look-ahead.** Both cells reaching
> significance on the expanding basis favour **level**. model_2's retirement now
> rests on two independent grounds, not on a confound.

**The phrase "expanding-window walk-forward, no look-ahead" stays wrong.** It is
now wrong by a measured amount rather than an unmeasured one. `analog_backtest`'s
headline figures are untouched — that engine never z-scores.

---

### 15.6 THE SPECIFICITY GATE — PASSED, ON A TIGHTENED CRITERION

`docs/gate_check_results.md`. Two amendments, both made **after** seeing a
marginal spread of 0.26 on n=20, both declared:

1. **`political` split by Federal Register document type** into
   `political_order` (executive order, presidential order, determination — 873
   docs) and `political_other` (proclamation, notice, memorandum — 816 docs).
   The partition uses the **government's own tag**, an external pre-existing
   taxonomy, not a judgement applied per document. This also corrects §8's claim
   that rhetoric is not covered — ceremonial documents were there all along,
   mislabelled.
2. **Criterion changed from a point spread > 0.25 to the LOWER BOUND of a 95%
   bootstrap CI > 0.25.** A **tightening**: at n=20 the spread carried se ≈
   0.063, so 0.26 was indistinguishable from failing and the point criterion
   could not say so. Pilot raised to n=60 per source.

Result at n=60 × 4 sources, uniform read condition v1-2026-08-23:

| source | n | mean specificity |
|---|---|---|
| earnings_8k | 60 | 0.631 |
| political_order | 60 | 0.603 |
| fomc_minutes | 60 | 0.489 |
| political_other | 60 | 0.268 |

Spread **0.363**, 95% CI **[0.279, 0.453]**. Both clauses pass.

`fomc_minutes` was moved to **unclassified**: its low-group placement was mine,
not registered, and minutes are genuinely ambiguous (a decision public for three
weeks, deliberative new content). Removing it makes clause 2 **harder**, and the
gate survived.

> **`specificity` therefore enters the content-class definition
> (`prereg_analog_event.md` §2.1) and the step 5 weighting rule (§7.2).**
>
> **Caveat:** `political_other` was measured at n=60 of 816. Re-run
> `gate_check` once the corpus read completes.

---

### 15.7 THE 8-K CORPUS WAS 307 SEC COVER PAGES

`fetch_sources.cmd_edgar` fetched `primaryDocument`. For an Item 2.02 filing that
is a one-page form saying *"a press release is attached as Exhibit 99.1"*. The
numbers live in **EX-99**, never fetched. The `len(txt.split()) < 60` guard was
written to catch this and never fired, because cover-page boilerplate runs to
hundreds of words — **a silent filter that passed 307 empty documents.**

**The reader was not wrong.** It correctly reported that a cover page contains no
market information. The corpus was wrong.

| earnings_8k pilot | \|dir\| eq | specificity | novelty |
|---|---|---|---|
| v1 (cover pages) | 0.07 | 0.20 | 0.09 |
| v2 (EX-99.1) | **0.47** | **0.66** | **0.37** |

Filename matching alone still lost NVDA (0/25), TSLA (4/25) and INTC (2/25) —
issuers share no naming convention and TSLA files PDFs. Fixed by a **content
scan**: when filename matching yields nothing, fetch every other document in the
accession and keep whatever contains reported figures. NVDA 8/8, TSLA 8/8, INTC
6/8 after. When both passes fail the accession's actual filenames are printed, so
the next failure names itself.

**6-K foreign issuers file the whole submission as one document with no separate
exhibits** — TSM and ASML yield little. Deferred decision §8.3 observed rather
than anticipated.

The 307 cover pages are kept at `data_provenance/docs/earnings_8k_coverpages/`
as evidence.

---

### 15.8 CORPUS — IN PROGRESS

The overnight read **exhausted the API balance** partway through
`political_order` and then failed every remaining document — **897 failures over
four hours**, each retried first, producing a log that looked like a completed
pass.

`doc_read` now **aborts the whole run** on a credit or auth error and prints how
many documents remain unread. Transient errors (overload, rate limit, malformed
reply) keep one-retry-then-continue. The classifier matches on the **message**,
not the exception class, because the SDK raises `BadRequestError` for both a
malformed request and an exhausted balance.

State at the abort:

| source | read | total |
|---|---|---|
| fomc_statement | 131 | 131 |
| fomc_minutes | 125 | 125 |
| earnings_8k | 364 | 364 |
| political_order | 732 | 873 |
| political_other | 65 | 816 |

**Re-run in progress.** Cached reads are skipped, so only the ~890 unread are
billed. **Update this table when `corpus2.log` reports CORPUS READ COMPLETE.**

Also fixed: the word cap 6,000 → 20,000, which had been dropping **105 of 125**
FOMC minutes; `--max-prev-words 3000` so `--with-prev` does not double an
already-large call; and JSON salvage plus one retry so a reply with preamble does
not cost a document.

---

### 15.9 STEP 3 ESTIMATOR — BUILT BLIND, 6/6

`docs/prereg_analog_event.md` (commit 74b88dc) registers steps 3–6 **before the
corpus read**. `src/analog_event.py` implements the estimator and was built
**blind**: real macro PCs, real regimes, real returns with real volatility, fat
tails, missing values and holidays — only the event-date ↔ return correspondence
destroyed, with a known effect planted on top.

Key registered choices:

- **Steps 3 and 4 are ONE estimator.** `ŷ = w·conditional + (1−w)·unconditional`,
  `w = ESS/(ESS+k)`. Step 4 is the `w = 0` limit. The hard "<10 precedents"
  cutoff is **replaced** — nothing real changes between 9 and 10 precedents.
- **k is ESTIMATED, never chosen.** `k = σ²_within / τ²`, τ² by
  DerSimonian–Laird across regime cells, re-estimated **inside every LOO fold**.
  τ² = 0 → w = 0 → **registered NULL**, not a reason to try another estimator.
- **All three PCs**, no per-source axis selection. An axis mapping was proposed
  and **rejected before any data**: it could not be checked afterwards without
  trying mappings until one worked.
- **Agreement flag displayed, never weighted.** On divergence the report shows
  both numbers and **issues no combined figure**.
- **σ by registered bisection** on median ESS, target `clip(0.15·n_pool, 8, 30)`.
  Uses no returns, so it cannot be tuned toward an outcome.
- **Abstention floor ESS < 8.** Tier 3 only.

Acceptance tests, all six pass. Three were repaired after failing, each declared:

- **Test 1 was vacuous** (`ok = isfinite(estimate)`) — it passed with an interval
  166× the planted effect. Now judged against the **oracle**: what a perfect
  estimator returns given those exact weights. Kernel attenuation of ~90% across
  a step is expected of any smoother and is reported separately. Its standard
  error was also wrong by **8×** — `d_est` is a linear functional of y, so
  `Var = σ_y²·Σaⱼ²`; verified against 200 simulated draws, 96.5% coverage.
- **Test 3 never exercised tiers 1 or 2** — it evaluated one query that sat in a
  sparse region. Now scans every query and **requires all three tiers**. With
  strong planted structure: 347/0/53 of 400 queries. With none: 0/260/140.
- **Test 5 FAILED and that result is preserved** in
  `docs/analog_event_selftest_v1_FAILED.md` (rejection 0.005, median p 0.906).
  Diagnosis, demonstrated in simulation before any change: when τ² = 0 the
  registered null path makes the statistic **identically zero**, so p = 1 by
  ties. Re-specified with the band **[0.02, 0.08] unchanged**, applied only to
  reps where the estimator conditioned, minimum 40 or INCONCLUSIVE.

**The null gained a second implementation, its third change after a failure —
declared.** `permute_y` (shuffle outcomes, weight geometry identical every draw)
is PRIMARY; `permute_Z` (the original) is **retained and reported permanently**.
Final: **permute_y 0.066** (in band), **permute_Z 0.000** (out). They disagree,
and that disagreement is reported as the finding with no tie-break. τ² = 0 in
32% of 200 reps.

**Conditioning moved to the LIVE BASIS** — expanding-window standardisation and
expanding-window regime labels, canonically ordered by ascending mean PC1. Not
because the look-ahead was large, but because **a deployed system has no future
data to standardise with or fit regimes on**, and a backtest that cannot be run
live is not a backtest of the product. This also closed **thread 3**: picks
verified bit-identical on 826 rebalances, only the reported `regime` integer
changes. Ledger rows before 2026-08-25 keep the old ordering and are **not**
retro-relabelled.

> **UNBLINDING IS AUTHORISED** once the corpus read completes.

---

### 15.10 WRONG PRIORS — NINE TO SEVENTEEN

Added this session, all Claude's:

10. "No λ exists anywhere in the codebase, not in config.yaml" — false.
11. Monotone rung count given as 3 — wrong (it is 4).
12. Code printed 5 for the same count under an unregistered ±0.02 tolerance.
13. "The `--types` filter is not filtering" — it was; the 50 non-EO documents
    were residue from an earlier unfiltered pull.
14. Test 1 written as a vacuous `isfinite` check.
15. Test 3 written to scan one query, concluding the tiers were unreachable.
16. Test 1's standard error understated **8×** by treating correlated smoothed
    estimates as independent.
17. "Removing the incumbent λ raises Sharpe from 0.25 to 0.38 and belongs in the
    report" — **not distinguishable**, p = 0.485.

**Every one was caught by RUNNING something, not by reasoning about it.** That is
this project's stated posture and this session is its largest single body of
evidence. Item 17 in particular was retired by a test registered before it was
implemented.

*(PROJECT_STATE's working-principles list still says "five so far". Reconcile.)*

---

### 15.11 WHAT IS ACTUALLY LEFT

| # | item | state |
|---|---|---|
| 1 | **the report** | **does not exist; deadline passed** |
| 2 | corpus read completion | running |
| 3 | re-run `gate_check` with full `political_other` | after 2 |
| 4 | unblind step 3 — the LOO test | after 2 |
| 5 | step 5 source weighing | not started; count same-day collisions first |
| 6 | step 6 decision report | not started — the customer-facing artifact |
| 7 | rebuild `app.py` | not started; **rebuild, do not recover** |
| 8 | step 7 launchd automation | not started |
| + | FOMC→GLD temporal split + cost test | not started — the Tier-1 exemplar |
| + | PROJECT_STATE / PIPELINE / EXECUTION_PLAN updates | pending |

---

### 15.12 THE REPORT'S SPINE — REVISED

§11's spine still holds and gains a second half.

Two clean nulls that survived every basis change. Two positive-looking results
that collapsed when split by time. One measured engine with its caveats declared
rather than defended. A live forward test with timestamps and no matured rows.
One mechanism — instant overnight propagation — explaining why the earlier entry
convention found nothing.

**And now: an engine whose central metaphor did not survive being measured.**
Both engines were shown to reselect rather than tie-break, so *analog* promises
more than the mechanism delivers. The trend advantage was shown to **be** a
look-ahead. A headline gap of 0.25 → 0.38 was **retired by a test registered
before it ran**. A corpus of 307 documents was found to contain nothing. Eight
silent-continuation defects were caught, one of which cost money.

**The honesty is still the finding, and it is now load-bearing rather than
decorative.** Every null came from an instrument demonstrated to detect a planted
effect first. Every retracted claim was retracted by a criterion written before
the number was seen. That is the negative-results moat argument, evidenced.


---

## 16. DEMONSTRATION TERMINAL — `app.py` (2026-08-25)

*Supersedes §15.11's line "rebuild `app.py` — not started". A minimal version now
exists. The full version still waits on steps 5–6.*

### 16.1 What it is

`app.py` at the repo root, Streamlit, eight tabs. Run with
`pip install streamlit && streamlit run app.py`.

It shows **no predictions and no signal**, because steps 3–6 are registered but
not unblinded and any signal display would be fabricated. What it shows instead
is the project's actual argument: an instrument that grades its own evidence,
prints what it cannot see, and keeps the record of what it got wrong.

**Every number on every live tab is read from the repository at run time** —
`processed/*.json`, `forward_ledger.csv`, file counts under `data_provenance/`.
If a results file is missing the tab says so rather than showing a stale figure.
Ten figures are hard-coded, all from committed `docs/*_results.md` files.

| tab | source of its numbers |
|---|---|
| What this is | narrative + three counts |
| **Today's report (SPECIMEN)** | **invented — see §16.2** |
| Universe | `config/config.yaml`; live screening logic |
| Engines | `recency_sweep.json`, `rung_diagnostic.json`, `scaling_check` figures |
| Document layer | file counts on disk, `gate_check.json` |
| Forward test | `forward_ledger.csv` |
| What we got wrong | the wrong-prior tally, §15.10 |
| Behind the scenes | narrative; working principles and commercial read |

### 16.2 The specimen tab — a labelled mockup, and the step 6 spec

Tab 2 is a **UI mockup with invented numbers**. It carries a red banner, a
fictional date (2027-03-15), and the word SPECIMEN eighteen times, because a
fabricated figure that escapes its context becomes a claimed result — and an
untraceable number is the one thing that would genuinely damage this submission.

**It doubles as the specification for step 6.** Its fields are exactly those
registered in `prereg_analog_event.md` §8, so building the real decision report
becomes filling a shape that already exists rather than designing from a
paragraph:

- macro regime and **posterior confidence** (below 0.60 prints as a warning)
- every document read: source, direction, magnitude, specificity, novelty,
  evidence quote
- per asset: estimate, precedent count, **ESS**, **precedent strength w**, tier,
  dominant source, reader-vs-history agreement flag
- one **abstention** (ESS 4.1 < 8) shown as an abstention, not a thin number
- one **divergence** where reader and history disagree in sign: both numbers
  shown, **no combined figure issued**
- the coverage-gap block
- **no performance number, specimen or real**

**The guardrails survive the mockup deliberately.** Even the invented report
abstains, flags divergence, prints what it cannot see, and shows no performance
figure. A demo whose fake version behaves better than the real one would be worth
nothing.

### 16.3 What it does not do

No conditional estimate, no source weighing, no report emission to
`outputs/reports/`, no scheduling. Those are steps 3, 5, 6 and 7. The Universe
tab screens a ticker against the real ≥8y rule but does not fetch it or write to
`config.yaml`.

### 16.4 Revised remaining list

§15.11 stands with one line changed:

| # | item | state |
|---|---|---|
| 1 | **the report** | **does not exist; deadline passed** |
| 2 | corpus read | in progress; over-cap documents now truncated, not skipped |
| 3 | re-run `gate_check` with the full corpus | after 2 |
| 4 | unblind step 3 — the registered LOO test | **authorised**, after 2 |
| 5 | step 5 source weighing | not started; count same-day collisions first |
| 6 | step 6 decision report | not started — **spec exists as `app.py` tab 2** |
| 7 | `app.py` full version | **minimal version DONE**; wire to steps 3–6 |
| 8 | step 7 launchd automation | not started |
| + | FOMC→GLD temporal split + cost test | not started — the Tier-1 exemplar |

---

## CORPUS STATE — counted from disk 2026-08-25 15:24

*Supersedes the table in §15.8, which was written by hand and went stale. These counts come from the filesystem — cached JSON reads against text files in the drop folder — not from a log, because a log can be truncated by a double launch and the cache cannot lie.*

| source | read | documents | unread | status |
|---|---|---|---|---|
| `fomc_statement` | 131 | 131 | 0 | **COMPLETE** |
| `fomc_minutes` | 125 | 125 | 0 | **COMPLETE** |
| `earnings_8k` | 645 | 834 | 189 | 77% read |
| `political_order` | 873 | 873 | 0 | **COMPLETE** |
| `political_other` | 73 | 816 | 743 | 9% read |
| `bank_research` | 0 | 0 | 0 | no documents — no free structured feed |
| `transcript` | 0 | 0 | 0 | no documents — no free structured feed |
| **TOTAL** | **1847** | **2779** | **932** | |

Estimated cost to finish: **~$8.91**. Cached reads are never re-billed — a re-run costs only the unread.

**The read is INCOMPLETE.** It has been interrupted three times: twice by API credit exhaustion (the second time it aborted correctly on the first error instead of retrying) and once by a cache file corrupted by an accidental double launch, since fixed by atomic writes.

Finish with a **single** launch of `./run_corpus.sh`, then re-run `python -m src.gate_check` — the gate was measured before the corpus was complete and before over-cap documents were truncated rather than skipped, so both the `political_other` and `earnings_8k` arms will move.


---

## 17. SESSIONS 2026-08-25 / 26 — CORPUS CLOSED, GATE PASSED, READER AUDITED, STEP 3 UNBLINDED

*Appended per §12. Supersedes nothing. §16.4's list is revised at §17.10.*

---

### 17.1 STATE IN ONE PARAGRAPH

The corpus read is **closed at 2,616 of 2,779**; four sources complete, 163
over-cap 8-Ks deferred on budget and explicitly kept, not abandoned. The
specificity gate **PASSED on the full corpus** at the registered 10,000
iterations. A cross-source audit of the reader found the reader sound and found
two things that are not: a fetcher bug that had truncated the political corpus,
and a schema that cannot represent a sector shock. Three pre-registrations were
filed before the step 3 unblinding — two amendments on the agreement flag and
one for schema v2. **The step 3 unblinding is running as this is written; its
result is recorded at §17.7 and is not known here.**

**The report deadline is 2026-08-28.** §1 of this file carries 24 August. That
is wrong and has been wrong all along; the correction is recorded at §17.9.

---

### 17.2 THE CORPUS IS CLOSED

| source | read | documents | status |
|---|---|---|---|
| `fomc_statement` | 131 | 131 | COMPLETE |
| `fomc_minutes` | 125 | 125 | COMPLETE |
| `earnings_8k` | 671 | 834 | 80% — 163 over-cap 6-Ks deferred |
| `political_order` | 873 | 873 | COMPLETE |
| `political_other` | 816 | 816 | COMPLETE |
| `bank_research`, `transcript` | 0 | 0 | no free structured feed |
| **total** | **2,616** | **2,779** | |

Read condition audited **before** the final launch, not after: 1,847 cached
reads, all `claude-sonnet-5` / `v1-2026-08-23`, zero unparseable. Finishing kept
it uniform.

**The fourth interruption.** The read was interrupted four times in total: two
credit exhaustions, one cache corrupted by an accidental double launch, and a
fourth exhaustion on 08-25 after a top-up sized by an estimate that was wrong
for the third time (§17.4). The abort mechanism added after interruption two
worked correctly under real conditions on the fourth: it stopped on the *first*
fatal error, named the unread count, exited 1, and `set -e` prevented the
remaining sources from launching against a dead balance. The morning of 08-25,
before that mechanism existed, 897 documents had failed over four hours and
produced a log that read as a completed pass.

**The 163 deferred 8-Ks — decision recorded.** Reading them does not improve
quality; it adds coverage at *degraded* quality. Truncated reads measure
specificity 0.458 and confidence 0.431 against 0.696 and 0.610 for whole
documents (confounded with document type — 6-K complete submissions versus EX-99
press releases — and reported unadjusted). They cost ~127,000 input tokens each,
roughly $35–55 for the set. **Not read.** Declared consequence: `earnings_8k` at
671 is US-issuer-biased, because the deferred set is disproportionately foreign
issuers filing 6-K.

---

### 17.3 THE SPECIFICITY GATE — PASS ON THE FULL CORPUS

Registered criterion (`prereg_analog_event.md` §11): the lower bound of a 95%
bootstrap CI on the spread must exceed 0.25, and every expected-high source must
sit above every expected-low source.

| source | n | mean specificity | expected |
|---|---|---|---|
| `earnings_8k` | 671 | 0.687 | HIGH |
| `fomc_statement` | 131 | 0.563 | HIGH |
| `political_order` | 873 | 0.550 | HIGH |
| `fomc_minutes` | 125 | 0.494 | — |
| `political_other` | 816 | 0.170 | low |

Spread **0.517**, 95% CI **[0.494, 0.539]**, 10,000 resamples, read condition
uniform, coverage clean on all five sources. **Clause 1 PASS** (0.494 > 0.25).
**Clause 2 PASS** (min HIGH 0.550 > max low 0.170).

`specificity` therefore enters the content-class definition (§2.1) and the step 5
weighting rule (§7.2).

Two things worth recording about how this result was reached. `fomc_statement`
entered clause 2 **for the first time** at n=131 — the n=60 gate had only 3 of
its documents and it had never been evaluated. It was kept in `EXPECT_HIGH` as
registered, and the decision to include it was committed before the number was
seen. And `political_other` fell from 0.268 at n=60 to 0.170 at n=816, widening
the spread; the low arm is genuinely empty, which §17.5 explains.

---

### 17.4 WRONG PRIORS 18–23 — SIX IN TWO SESSIONS, ALL CLAUDE'S, ALL CAUGHT BY RUNNING SOMETHING

**18. The cost estimate priced the wrong documents.** `corpus_status` valued the
189 unread `earnings_8k` documents at the corpus mean of 8,421 tokens. Those 189
were *exactly* the 189 the old cap had skipped for being over `max_words` — they
were unread *because* they were over-cap, so the mean could not describe them.
$8.91 → $15.94. The tell sat two numbers apart in a comment in the same file.

**19. Five green anchors over code that would not run.** `patch_gate_check.py`
verified five anchors, applied cleanly, reported success, and shipped a
`NameError` — the new `load_all()` calls `Path(f).name` and `gate_check.py` had
never imported `pathlib`. *Anchor verification proves an edit landed where it was
aimed; it says nothing about whether the file still runs.* A `py_compile` check
that reverts on failure was added to the patch protocol. Separately, that
patch's `--write` was never executed, so the gate then ran on the **unpatched**
file and overwrote the registered result with a fresh timestamp — the exact
failure the patch existed to prevent, produced by the patch not being applied.
Caught by comparing the run's output against what the patch should have changed.
Commit `a31d0a9`'s false third bullet is left in history, corrected by `bf921f1`.

**20. The corrected estimate was calibrated on the wrong population — again.**
`measure_unread.py` derived tokens-per-word from documents *already read*, which
are ordinary press-release prose. The remainder is dense 6-K financial tables at
about 6.3 tokens per word. $15.94 → measured **~$46**. The identical error as
#18, one level deeper, made while explicitly fixing #18.

**21. The `political_other` null was interpreted without checking the corpus.**
816 documents, mean |direction| below 0.005, read as "the reader correctly finds
nothing in ceremonial documents". That interpretation was made without asking
whether the documents that would falsify it were present. They were not — see
§17.5.

**22. A timing test whose premise was wrong.** The audit asserted novelty should
fall with publication lag. FOMC statements read at the *lowest* novelty of the
market sources (0.289), which is correct: they are the most telegraphed
documents in finance. The field was right and the test was wrong. **Retracted —
`novelty` is not to be reported as a defect.**

**23. "Ten of 28 hikes read backwards, a genuine defect."** Four were false
positives from a regex matching *"an increase in the target range … remains
**unlikely**"*. The remaining six all carried dovish forward guidance in their
own evidence quotes, and `stance` was correctly hawkish on every one. The test
was cruder than the thing it was testing.

**Tally: 23.** Every one caught by running something rather than by reasoning
about it.

---

### 17.5 THE READER IS SOUND. THE CORPUS AND THE SCHEMA ARE NOT.

`docs/read_audit_results.md`, run 2026-08-25 over 2,616 cached reads at zero
cost. Seven checks: timing order, signal classes against source baseline, sign
consistency, within-reader consistency, landmark documents, field population,
flat-tail.

**Evidence the reader works:**

| check | result |
|---|---|
| `corr(stance, dir_duration)`, statements | **−0.802** — hawkish means bond price down, as the schema demands |
| `corr(stance, dir_duration)`, minutes | −0.527 |
| `extra.surprise` vs own `dir_equity` | agree 431, disagree 11 (**92%**) |
| `is_decided=True` vs `False` specificity, `political_order` | 0.586 vs 0.281 |
| landmarks | COVID emergency cut novelty 0.95; NVDA May-2023 guidance 0.90; 2022 75bp hike, 2013 taper, 2025 IEEPA and reciprocal tariffs all read large and correctly signed |

**Finding A — the political corpus was truncated by two bugs in the fetcher.**
Every 2018 and 2025 Section 232 proclamation was **ABSENT**. Two independent
caps: `--types` matched `executive_order` (underscore) against the API's
`executive order` (space), silently dropping five of six document types; and
`--max-pages 6` at 1,000 per page capped an oldest-first pull near 2016. Both
fixed. Re-fetch on 2026-08-26 at **$0**: proclamations 1,674 → 2,440, executive
orders 0 → 870, notices, memoranda, determinations and presidential orders all
now retained. **4,595 documents on disk in `docs/political/`, unread and
unbilled.** They sit outside every source `run_corpus.sh` names, so no accidental
read is possible.

**Finding B — the schema cannot represent a sector shock.** `direction` has five
axes: equity, duration, gold, dollar, oil. A Section 232 steel tariff's
first-order effect is on steel and aluminium equities and on input costs. There
is no axis to point at.

| `political_order` class | n | specificity | max\|dir\| |
|---|---|---|---|
| baseline (all) | 873 | 0.550 | 0.073 |
| TARIFF / trade action | 235 | **0.669** | 0.129 |
| ceremonial / administrative | 135 | 0.475 | 0.037 |

The reader marks tariff documents as markedly more specific than baseline and
than ceremonial documents — *it knows what it is looking at.* Its direction
barely moves because the vocabulary has nowhere for it to go. **This is the same
finding as the analog metaphor collapsing in §15.3, one layer up: what the
instrument can detect is bounded by the language it was given.**

**Finding C — FOMC `direction` is guidance-net, not decision-net.** Six genuine
hikes read with positive `direction.duration`, every one carrying softening
forward guidance. `stance` was hawkish on all six. The reader puts the decision
in `stance` and the net of the guidance in `direction`. Coherent, arguably
correct, and undocumented anywhere until this audit.

**On `political_other` (correcting wrong prior #21):** measured directly, 816
documents carry **33 non-zero direction readings in total across five axes**.
`dir_duration` is literally 0.000 on all 816. Only 5 documents exceed 0.05 on
any axis. So the source contributes **zero events to step 3 under any
negligibility floor**, not merely under the chosen one — checked before the
unblinding, because the floor was Claude's operational reading of §2.1's "both
non-zero" and not a registered constant. The source is not a reader failure: 798
of 816 are commemorative, and the documents that would have carried direction
are the tariff proclamations that Finding A shows were never fetched.

---

### 17.6 THREE PRE-REGISTRATIONS, ALL BEFORE THE UNBLINDING

**Amendment 2** (`docs/prereg_amendment_2_agreement_flag.md`, `87dff26`).
Permits the agreement flag to set a conviction label
(`CONCORDANT` / `DISCORDANT` / `UNINFORMATIVE`) in the step 6 report, displayed
prominently and usable to order and filter. Prohibits any effect on the number.
Registers a falsification test: mean signed realised return, `CONCORDANT` versus
`DISCORDANT`, permutation p < 0.05, with an `n < 20` UNDERPOWERED clause.

**Amendment 3** (`docs/prereg_amendment_3_agreement_moves_number.md`,
`d8b40b9`). **Supersedes Amendment 2's prohibition, filed the same day.
Amendment 2 is left unaltered** — the sequence of decisions, including one
reversed within a day, is part of the record. The interval may now move; the
point estimate may not, because the reader carries a sign and a specificity but
no magnitude. ρ̂ — the ratio of residual dispersion among `CONCORDANT` events to
pooled — is **estimated inside each LOO fold from training events only**, exactly
as `k` already is, and clipped to [0.70, 1.30]. Three registered clauses set
ρ = 1: the Amendment 2 test fails; either arm has n < 20; or **out-of-fold
empirical coverage of the adjusted intervals falls below 0.90**. The third is
the one that matters — reader and history are keyed to the same event, and if
agreement is being double-counted, narrow intervals missing their coverage
target is what that looks like from outside. Amendment 2 handled the concern by
assertion; Amendment 3 handles it by measurement.

§7 of that document records that permitting movement was Steven's decision,
taken after the display-only recommendation was given and argued.

**Schema v2** (`docs/prereg_schema_v2.md`, `87dff26`). Written from the measured
deficiencies in §17.5. Adds a `sector` object with a closed name list rather than
fixed sector axes; splits FOMC `direction_decision` from `direction_guidance`;
documents `novelty` as content-novelty; sets `earnings_8k` `max_words` by a
registered measurement procedure. **The five macro axes are unchanged**, which is
what keeps v1 and v2 comparable. Acceptance on a 100-document paired pilot with
three criteria written in advance, including A2: v2 must show non-negligible
`sector.direction` on ≥ 60% of tariff documents — *if it also reads them flat,
the schema was not the binding constraint and Finding B was misdiagnosed.*
**Mixed corpus explicitly prohibited.** Not funded; v1 ships with the limitation
declared and diagnosed.

---

### 17.7 STEP 3 UNBLINDING — RUNNING

`unblind_step3.py`, committed at `3863d6c`. The estimator is frozen at `9062391`
and every function is **imported** from `src/analog_event.py`, never
reimplemented — if the runner reimplemented any of it, the six blind acceptance
tests would no longer be evidence about the thing being run.

The delta from `build_blind()` is three lines: real document dates instead of
`rng.choice(valid)`, `y = fwd[pos]` instead of `fwd[donor]`, and no planted
effect.

**Assembly, from the dry run:** 45 cells ready, 6 abstaining at the ESS floor,
15 `political_other` cells empty. Panel 5,194 sessions, 2,616 documents, C=4.

**Declared as chosen, not registered** — the prereg left these open and they are
Claude's, recorded before the run: horizons (3, 5, 20) with 3 primary; the five
liquid proxies GLD/SPY/TLT/UUP/USO, one per schema axis; the 0.05 negligibility
floor; and enforcing the content class by running the estimator separately
within each sign class, so a query is never predicted from an opposite-sign
document, with the null permuting outcomes *within* class.

**OBSERVED BEFORE THE RUN AND DELIBERATELY NOT FIXED — the ESS knife-edge.**
§4 sets `target_ESS = clip(0.15·n_pool, 8, 30)` and §3.5 abstains below ESS 8.
Split across two content classes, most pools give 0.15·n < 8, so the target
clips to 8 — and σ is bisected to land median ESS *exactly on the abstention
boundary*. `political_order` UUP abstains at **7.993**; `earnings_8k` UUP
proceeds at **8.051**. A difference of 0.007 decides a registered abstention.
Changing the rule after seeing which cells fall on which side is the move this
project exists to forbid. **It runs as written; the knife-edge is reported as a
limitation; a corrected rule is registered as an amendment after this run
completes.** Also recorded: five cells have `n_classes = 1`, so the content-class
filter is not filtering in those, and they test something weaker than the
two-class cells.

> **RESULT: [pending — the run is in progress at the time of writing. It is
> recorded here on completion, whatever it says. §5.2's criterion is BOTH lower
> MSE AND higher sign hit-rate at p < 0.05; one of two is inconclusive, not a
> partial success. §10 pre-states the failure modes, including τ² = 0 across
> most cells, which is reported as a null with every asset at Tier 3 and does
> not stop the product shipping.]**

A runner defect found and fixed before the real launch: the first version
iterated sources alphabetically, so the first cell computed was the most
expensive in the run (`earnings_8k` SPY, n=462, ~2 billion kernel evaluations),
and with stdout block-buffered to a file it produced a 0-byte log for hours with
no way to distinguish working from hung. Rewritten to assemble all cells first,
sort cheapest-first, seed each cell from its own identity so ordering cannot
affect any cell's draws, report progress with measured time estimates, and
checkpoint each completed cell to `processed/unblind_cells.jsonl` so an
interrupted run resumes rather than restarting.

---

### 17.8 COMMERCIAL — WHAT THESE SESSIONS CHANGED

**Cost accounting is now measured, not estimated.** Three successive estimates
were wrong by 1.8× and then 3× (§17.4). The lesson generalises past this
project: an LLM pipeline's unit cost cannot be carried as a per-document average
when the remainder is selected on length. `docs/prereg_schema_v2.md` §7 prices
v2 from *measured* token counts, and any pricing model in the business plan
should be built the same way.

**The corpus is not the binding constraint, and that is a commercial finding.**
2,616 documents were read for roughly $30 in total. The deferred 163 would add
$35–55 for measurably worse reads, and 4,595 political documents sit fetched at
$0. What limits the product is the *schema* — five macro axes — not the data
volume. That reframes the roadmap: v2's sector axes are worth more than more
corpus, and v2 is costed at $200–400 for a full re-read.

**The declared limitation is a product artifact, not only an academic one.** A
client who asks "what does this say about a steel tariff" gets a diagnosed
answer — the instrument's vocabulary cannot express it, here is the measurement
showing that, here is the registered v2 that would. That is a stronger position
than a product that quietly returns zero.

---

### 17.9 CORRECTIONS TO THE RECORD

- **The report deadline is 28 August, not 24 August.** §1 of this file is wrong.
  Work had been paced against a date that was never right.
- `processed/doc_reads.csv` moved to `processed/superseded/`. Three rows written
  before `prompt_version` and `model` entered the schema, which tripped MIXED
  READ CONDITIONS on a corpus the pre-run audit had just proved uniform.
- `corpus_status.py` still reports **~$9.27** to finish. Measured cost for the
  163 remaining is **$35–55**. The file has now been wrong three times on this
  number and remains unfixed at the time of writing — recorded here rather than
  patched mid-run.

---

### 17.10 WHAT IS LEFT

| # | item | state |
|---|---|---|
| 1 | **the report** | **does not exist. Due 2026-08-28. Nothing below is what Dr. Lee is waiting for.** |
| 2 | corpus read | **CLOSED** at 2,616/2,779 |
| 3 | gate re-run, full corpus | **CLOSED — PASS**, 0.517, CI [0.494, 0.539] |
| 4 | unblind step 3 | **running**; result at §17.7 |
| 5 | Amendment 2/3 agreement tests | after 4; runs on the predictions CSV, $0 |
| 6 | step 5 source weighing | not started; count same-day collisions first |
| 7 | step 6 decision report | not started; spec is `app.py` tab 2 |
| 8 | `app.py` wiring to steps 3–6 | minimal 8-tab version exists |
| 9 | step 7 launchd automation | not started |
| 10 | ESS knife-edge amendment | drafted after item 4 completes, never before |
| 11 | `corpus_status` cost figure | wrong three times, unfixed |
| + | FOMC→GLD temporal split + cost test | not started — the Tier-1 exemplar for the demo |

**Everything between here and submission costs $0.** The only remaining uses for
API credit are the 163 deferred 8-Ks (declined), the 4,595 political documents
(not needed for the report), and the schema v2 pilot (registered, not funded).

---

## 17.7 (REPLACES THE PENDING BLOCK) — STEP 3 UNBLINDED, AND THEN RE-TESTED

*The `[pending]` block written earlier in §17.7 is superseded by this section.
It is not deleted: it recorded that the run was in progress and that the result
would be reported whatever it said. This is that report.*

---

### 17.7.1 THE RESULT IN ONE LINE

**Step 3 did not demonstrate a conditional effect that survives correct
inference.** Seven of 45 cells met the registered criterion on the unblinding;
one of those seven survived re-testing under a null that respects overlapping
outcomes, and that one is the cell whose original null was already valid.

This is the failure mode `prereg_analog_event.md` §10 registered on 24 August,
before the corpus was read: *"τ² = 0 across most cells → macro conditioning adds
nothing measurable. Reported as a null; the report still ships, with every asset
at Tier 3."* The product ships as designed.

### 17.7.2 THE UNBLINDING — 7 OF 45

Run 2026-08-26. Estimator frozen at `9062391`, every function imported from
`src/analog_event.py`, never reimplemented. The delta from `build_blind()` was
three lines: real document dates, `y = fwd[pos]`, no planted effect.

| cell | n | MSE reduction | hit gain | p_mse | p_hit |
|---|---|---|---|---|---|
| `political_order`/SPY/h20 | 232 | 23% | +5.2pp | 1e-4 | 1e-4 |
| `political_order`/SPY/h5 | 233 | 10% | +1.7pp | 1e-4 | 0.0052 |
| `political_order`/SPY/h3 | 233 | 8% | +2.1pp | 1e-4 | 0.0093 |
| `political_order`/GLD/h20 | 76 | 10% | +2.6pp | 0.0020 | 0.0060 |
| `fomc_minutes`/USO/h5 | 69 | 13% | +8.7pp | 0.0010 | 0.0121 |
| `earnings_8k`/SPY/h20 | 459 | 9% | +0.4pp | 1e-4 | 0.0030 |
| `earnings_8k`/SPY/h5 | 462 | 1.4% | +0.2pp | 0.0031 | 0.0222 |

Six cells abstained at the ESS floor; 15 `political_order_other` cells were
empty; the rest did not meet the criterion. Reported in full at
`docs/unblind_step3_results.md` per §5.4.

**The transfer check (§4.1) came back 0.95–1.00** against a 0.90 threshold. On
the document pool λ is **tie-breaking, not reselecting** — the opposite of the
step 1 engines at 0.765 and 0.850 which forced the retraction of "analog" in
§15.3. σ = 0.38 on `political_order` is a tight kernel and k=20 drawn from 231
candidates cannot be reordered by decay. **One measurement, two pools, opposite
answers, and the difference is explained by pool size and kernel width.** At
n=76 the overlap of 1.000 is partly a small-n artifact (k=15 of 75) and only the
SPY cells carry this cleanly.

### 17.7.3 WRONG PRIOR #25 — THE NULL IGNORED OVERLAPPING OUTCOMES

**The estimator was never the problem.** `analog_event.py` computes leave-one-out
predictions and overlapping outcomes do not affect that computation. The MSE and
hit gains above are descriptive and they stand.

The defect was in the null that `unblind_step3.py` used — code written for this
run, not registered code. It permuted outcomes freely within content class. But
at h=20 the passing cells overlap 61–87%: most events share most of their
forward window with their neighbours, so `y` is strongly autocorrelated. Free
permutation destroys that dependence, the permuted draws are less variable than
the observed data, the null is too narrow and **every p-value is too small.**

| cell | overlap at h | 2025+ share |
|---|---|---|
| `earnings_8k`/SPY/h20 | 87% | 17% |
| `political_order`/SPY/h20 | 81% | 51% |
| `political_order`/GLD/h20 | 61% | 57% |
| `political_order`/SPY/h5 | 56% | 52% |
| `political_order`/SPY/h3 | 44% | 52% |

`political_order` compounds it: median event gap **5 days**, **52% of events
from 2025–26** (239 executive orders in 2025 against 18 in 2024).

The check was one line — event spacing against horizon — and was not done. The
prereg registered `permute_y` for a pool where it was appropriate; the runner
applied it to a clustered pool without checking.

**Wrong priors #26** followed while fixing #25, twice: `int(round(h/gap))`
returned a block length of 1 at h=5 — and a block of 1 *is* free permutation,
the broken null relabelled as fixed; and calibrating on the **median** gap
ignored the clustered tail, since `political_order`/SPY has a median gap of 3.5
sessions so `ceil(3/3.5) = 1` at h=3 while 44% of its events measurably overlap.
Both caught by reading the dry run against what the fix claimed to change. Final
rule: 25th-percentile gap with `ceil`, which errs toward **larger** blocks and
makes the test **harder** to pass.

### 17.7.4 THE RE-TEST — 1 OF 7

Registered in `step3_robustness.py`'s docstring before it ran. Three checks,
no new criteria invented: **N1** non-overlap subsample (valid, costs power),
**N2** block permutation preserving within-block dependence (retains n),
**S** temporal split with the same S1/S2 clauses as `fomc_gld_split_cost.py`.
CONFIRMED requires all three. Only the seven passing cells were re-tested —
re-testing failures under a new null until one passes is the error this project
exists to avoid.

| cell | N2 block | N1 non-overlap | split ratio | verdict |
|---|---|---|---|---|
| `fomc_minutes`/USO/h5 | p 0.0024 / 0.0138 | p 0.0022 / 0.0122 | 2.28×, agree | **CONFIRMED** |
| `political_order`/GLD/h20 | p 0.0039 / 0.0129 | p 0.0018 / 0.0149 | **14.86×, sign flip** | not confirmed |
| `political_order`/SPY/h20 | p_hit **0.2244** | mse gain **negative** | 7.08× | not confirmed |
| `political_order`/SPY/h5 | p_hit 0.0611 | hit gain **−0.040** | 1.44× | not confirmed |
| `political_order`/SPY/h3 | p 0.0001 / 0.0337 | p 0.1333 / **0.8793** | 4.62× | not confirmed |
| `earnings_8k`/SPY/h20 | p_hit 0.1177 | mse gain **negative** | 4.10× | not confirmed |
| `earnings_8k`/SPY/h5 | p 0.1022 / 0.0769 | mse gain **negative** | 12.64×, sign flip | not confirmed |

**The h=20 cells collapsed exactly where the null was broken.** `p_hit` on
`political_order`/SPY/h20 went from 1e-4 to 0.2244. And on the non-overlap
subsamples several went **negative**: with independent events the conditioned
estimator does no better, and slightly worse, than the unconditional one.

### 17.7.5 THE SURVIVOR, AND TWO REASONS NOT TO OVERREAD IT

`fomc_minutes`/USO/h5: n=69, MSE reduction 13%, hit gain +8.7pp, temporal split
2.28× with sign agreement.

**It survived because its original inference was already sound.** FOMC minutes
are released roughly six weeks apart, so at h=5 no overlap exists: block length
computes to 1 and `n_nonoverlap = n_full = 69`. Its p-values were never
inflated. The cells whose inference was broken did not survive; the cell whose
inference was valid did. That is a coherent story and it is the strongest thing
in this section.

**Declared, two ways it must not be overread:**

1. **N1 and N2 are the same test on this cell.** Block = 1 *is* free
   permutation, and the non-overlap subsample *is* the full sample. The
   identical numbers give it away (+3.201e-04 at p 0.0024 and 0.0022). The
   R1/R2 structure awards two ticks for one piece of evidence. **It passes one
   null, not two.**
2. **One cell of 45 is inside the chance expectation.** Between 0.11 (if the
   two statistics were independent) and 2.25 (if perfectly correlated) passes
   were expected by construction. On multiplicity grounds a single survivor
   cannot be distinguished from noise.

### 17.7.6 WHAT WOULD CHANGE THIS — ROADMAP, NOT PROMISE

**The binding constraint is independent events, not method.** Non-overlap caps
each cell at 41–317, and everything else follows from that. Three routes, none
available before 2026-08-28 and none a claim that step 3 would then work:

1. **Read the 4,595 political documents already fetched at $0.** More events
   means more *independent* events at any horizon. Cost to read ~$30–60. The
   cheapest real lever, and it is already on disk.
2. **Schema v2's sector axes** (`docs/prereg_schema_v2.md`, registered).
   `political_order`'s tariff class scores specificity 0.669 against a 0.550
   baseline but direction only 0.129 — the reader knows what it is looking at
   and has nowhere to point. If direction carries more signal the content-class
   filter partitions better. $200–400.
3. **Shorter horizons on naturally spaced events.** The one confirmed cell is
   the one whose events are six weeks apart. FOMC statements, minutes and
   scheduled macro releases have that property; earnings and executive orders do
   not.

### 17.7.7 WHAT SHIPS

Per §10, every asset at **Tier 3**: the decision report states the regime, the
evidence and the precision, and **abstains from a conditional forecast** where
the evidence floor is not met. `fomc_minutes`/USO/h5 is the single cell with a
confirmed conditional estimate and is labelled as one cell of 45, passing one
null, inside the chance expectation.

The FOMC→GLD exemplar is also unavailable — split FAIL at 4.62× on the same day
(`docs/fomc_gld_split_cost.md`). **The demo therefore abstains rather than
showing a Tier-1 cell, and that abstention is the product working as specified,
not a gap in it.** A system that declines to forecast when its own registered
evidence floor is not met is the thing the pivot to risk-management signals in
Week 11 committed to building.

---

## 18. SESSIONS 2026-09-13 / 14 — HARNESS AUDIT: FOUR SILENT DEFECTS, SIX COMMITS

*Appended 2026-09-14. Nothing above is altered. TRACK §5 carries the one-line summary;
this section is the evidence.*

### 18.1 WHAT WAS FOUND, BY READING THE LOGS RATHER THAN TRUSTING THEM

The forward-test log folder was checked against the calendar before anything was made
public. Every weekday 28 Aug–11 Sep had a dated file (eleven of eleven). The
`forward_ledger.csv` held 48 rows = 16 signal dates × 3 models, and those sixteen dates
were exactly every US session 19 Aug–10 Sep: no Labor Day row, no duplicate, and the
11 Sep run — which fired at 02:03 SGT on the 12th, mid-session in New York — correctly
refused the live bar and used the 10 Sep close. **The ledger itself was clean.** The
same logs showed four things the ledger could not:

1. **Nightly document reads had been dead since 29 Aug.** Every log from the 29th
   carried `doc_read.py: error: unrecognized arguments: --unread-only`. The flag had
   never existed; `daily_run.sh` had passed it from the day launchd was set up. The
   evidence was the coverage line, byte-identical across fourteen logs: `sessions
   carrying documents 1566 (30%)`. TRACK §1 (written 7 Sep) said the read count was
   "creeping up". It was not. Further: even without the bad flag the read would have
   been a no-op, because `--limit` sliced the file list *before* the cache check and
   the list is date-ascending — the cap would have been spent re-touching the forty
   oldest cached documents every night.
2. **`outputs/reports/` was rewritten every night.** Step 7/7 of `daily_run.sh` ran
   `generate_reports.py --docs-only --limit 30 --recent 10`, regenerating the 30 most
   recent document-bearing dates plus the 10 most recent sessions. A report dated 8 Jul
   carried a 12 Sep `generated` stamp and a `w_shrink` that had moved from 0.295 to
   0.390. Nothing in the folder was ever final. Cause of the drift: the PCA is refit on
   the extended panel nightly and yfinance's adjusted closes revise history, so
   regeneration can never be idempotent.
3. **Reports were written a day early.** `step6_report.py --latest` took the panel's
   last index date, which runs a day ahead of the price data (the log line "panel index
   runs to 2026-09-11 but those rows have no prices yet"). The 11 Sep report was
   therefore written at ~03:00 ET on the 11th, before any document dated 11 Sep could
   have been published or fetched. Defect 2 had been silently patching defect 3: each
   report received its documents on the next night's rewrite.
4. **One ticker aborted the whole run on 8 Sep.** yfinance returned nothing for AMLP
   (a transient — it fetched normally on the 9th); `cached_fetch` exhausted its retries
   and raised; `daily_run.sh` stopped at step 1 of 7 with no forward row and no
   report. It cost nothing only because 4 Sep had already been entered on the 7th and
   Labor Day meant no new close existed. On any other weekday it would have been a
   permanent gap.

Also recorded: the **28 Aug vendor gap** (Close/Adj Close NaN, same pattern as
17 Aug) surfaced on 31 Aug as `latest US close WITH PRICE DATA: 2026-08-27 (4d old)`
and as SHORT WINDOW flags on four entries through 3 Sep; it healed by 4 Sep and the
flags cleared. And the **machine sleeps at 15:00 most days**: runs landed at 16:59,
17:11 and 02:03 (launchd fires a missed job on wake), and the 11 Sep run was
*suspended mid-way* for ten hours between its forward-log step and its report step.

### 18.2 WHAT WAS CHANGED — SIX COMMITS, NO MODEL TOUCHED

| commit | change |
|---|---|
| `8533969` | `doc_read.py`: `--unread-only` exists and filters *before* `--limit`; `--since YYYYMMDD` drops documents before a cutoff. `daily_run.sh`: reads all six sources (`political` added — the nightly fetcher had been writing to a folder the read loop never visited) with `--since 20260827`, so the deferred sets (4,595 political, 163 over-cap 6-Ks) are never consumed by the nightly cap |
| `e740751` | `generate_reports.py --index-only`: rebuilds `report_index.json` from files on disk, writes no report. `daily_run.sh` step 7/7 uses it. Index now spans all 1,585 reports (2006-01-03 → 2026-09-11), not the 47 dates the old merge had accumulated |
| `562dedb` | `step6_report.py --latest` resolves to the last panel session ≤ `last_completed_session()` (the forward log's rule) and is write-once (`--force` to overwrite). The mid-session 11 Sep report was deleted so it can be written correctly |
| `2296725` | `download_data.py`: per-ticker failure warns and continues, cached history kept; majority failure fatal. `forward_log.py`: catch-up entry of every completed-but-unlogged close, oldest first, with `logged_at`. Registered in `docs/forward_test_amendment_2026-09-13_catchup.md` |
| `4f17d2e` | TRACK: §5 rows for the above; §3.8 report-level scoreboard |
| this commit | This section; the amendment file; `docs/prereg_report_scoreboard.md` committed with placeholders; TRACK corrections |

### 18.3 CONSEQUENCES FOR THE RECORD

- **Reports dated 27 Aug–11 Sep have no "as emitted" version.** What is on disk is
  their last regeneration (7 Sep for most; 12 Sep for the forty most recent). They
  are backfill, and the report-level scoreboard treats them as such.
- **Nightly document reads remain paused** — the API balance is exhausted and the
  founder is not funding it at present. The read pipeline is now correct; it is
  idle for lack of credit, not broken.
- **Therefore: a report written while its session's documents are fetched but
  unread would be frozen incomplete.** The rule adopted is that `step6 --latest`
  **defers** a report whose session has unread documents, and writes deferred
  sessions oldest-first once their documents are read. Enforcement is the next code
  item (§18.5); until it lands, `daily_run.sh` should not be relied on to produce a
  correct 11 Sep report.
- **The report-level forward ledger starts at the first session whose report is
  written with all its fetched documents read** — not 14 Sep as TRACK said on the
  13th. Corrected in TRACK and in the prereg §7.1/§11.
- **Wrong prior #29 — founder to decide.** "The nightly reads are running and the
  count is creeping up" (TRACK §1, 7 Sep) was a belief about the system, held in
  writing, overturned by reading a log. By this project's definition it qualifies.
  The tally is not changed here.

### 18.4 THE SCOREBOARD WORKSTREAM

`docs/prereg_report_scoreboard.md` is committed with three `[FILL]` placeholders
(horizon set from the unblinding script; primary horizon, proposal 5; source-expansion
tolerance, proposal 2 points). The eight-step plan is TRACK §3.8. Nothing in it costs
money until step 8, which is deferred.

### 18.5 OPEN — NEXT CODE ITEM

`step6_report.py`: (a) refuse to write a report for a session that has fetched-but-
unread documents (count files under `data_provenance/docs/<source>/` dated that
session with no entry under `doc_reads/`), printing the count and "deferred"; (b) a
`--pending` mode that lists completed sessions with no report on disk, so
`daily_run.sh` can loop `--date` over them once reads resume. Neither is written yet.
