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
- **Wrong-prior tally: nine.** Several are Claude's. Pattern across the first
  three: results are more *basis-carried* and less *phenomenon-carried* than
  expected. The fourth showed that correction can be over-applied.

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
