# TRACK — Regime-Aware Cross-Asset Signal Framework

**This is the one file to bring to a new conversation.** It supersedes the Track
tables in `CURRENT_STATE_2026-08-23.md` §17.10 and is updated in place; the
date at the top is the last edit. `POST_SUBMISSION_STATE.md` holds the fuller
reasoning behind each item and `CURRENT_STATE` §17 holds the evidence record.
This file holds *status only*, so it stays short enough to read in one sitting.

**Last updated:** 2026-09-07
**Project state:** submitted 2026-08-28; forward test running unattended;
supervisor review pending.

---

## How to use this file

- **Read §1 first.** If the forward log has gapped, that is the only thing on
  this page that gets worse by waiting, and it cannot be repaired.
- Items move between sections; nothing is deleted. A finished item goes to §5
  with its date, so the record of what was done stays with the record of what
  was not.
- Every item in §3 requires its own pre-registration before it runs. That rule
  is not restated per item — it applies to all of them.
- To add an item: put it in the right section with a one-line reason and, if it
  costs money, the cost. Don't add items without a reason.

---

## 1. Running — needs periodic checking, not work

| item | what should be true | how to check | if it isn't |
|---|---|---|---|
| **Forward test, launchd** | One dated log per weekday since 28 Aug | `ls ~/Projects/regime-aware-signal/logs/` | The gap is permanent. Find the cause (Mac asleep at 18:30 is the usual one) and record the gap dates in `CURRENT_STATE` |
| **Matured positions** | Count rising weekly; H=5 first, H=20 from ~16 Sep | `tail -3 docs/forward_scoreboard.md` | Too few to report a figure until late October at the earliest; do not report one |
| **Nightly document reads** | Read count ≥ 2,616 and creeping up | `python -m src.corpus_status` | If it stopped, check the API balance — the cap is 40/night but the balance can still run dry |
| **Supervisor review** | Feedback from Dr Lee on the 28 Aug submission | inbox | When it arrives, log it here before acting on any of it |
| **Collaborator access** | Dr Lee accepted the invite | GitHub → Settings → Collaborators | Re-invite by email address if the handle failed again |

---

## 2. Open questions — no registered answer

These are unresolved, not deferred. Each would need a test designed before it
could be closed, and none has one yet.

**Capacity / AUM.** No dollar-volume history exists in the repo, so no ceiling
is stated anywhere. The 46 names ever held are enumerated in
`processed/backtest_evidence.json`. Closing it needs a volume pull and a
participation assumption, then a one-line calculation.

**Per-name borrow.** A flat annualised rate is applied to the short leg. A
historical borrow curve per security is not available; the plan says so rather
than inventing one.

**Does reader–history agreement mark already-priced information?** The
registered test failed backwards — discordant cases outperformed by 0.21%.
Three readings fit: noise, pseudo-replication, or agreement marking information
the market has absorbed. They cannot be separated on n = 2,024. Recorded as a
[HYPOTHESIS]; turning a failed test into a new claim requires a fresh
pre-registration written first.

**Does the compliance function veto an unlicensed vendor?** The highest-risk
assumption in the business plan. Falsifiable in the first ten customer
conversations, none of which has happened.

**Does the reader's logic match the founder's?** The prompts in
`src/doc_read.py` `PROFILES` were written by the assistant under deadline and
encode the assistant's judgement about what matters in each source type. The
founder has not reviewed them line by line. Any disagreement is a schema v2
item and goes through the paired-pilot protocol, not a direct edit.

---

## 3. Undone — registered, costed, not built

Ordered by value per dollar. Each needs its own pre-registration; the
pre-registration is the first step, not the code.

### 3.1 Read the 4,595 political documents — ~US$60

**What it is.** Federal Register documents already fetched at zero cost on
26 Aug and sitting in `data_provenance/docs/political/`, unread. They are the
notices, memoranda, determinations and executive-order variants the original
fetcher dropped through a string-match bug (`executive_order` vs
`executive order`).

**Why it is first.** Current session coverage is 30% — on 70% of trading days
no document lands, so every asset abstains for the plainest reason. These
documents plausibly raise that to 55–70%. And every political content-class
pool gains precedents, which raises realised ESS and reduces tier-3 abstentions
on exactly the days a political shock moves markets.

**What it needs.** A short pre-registration stating the expected coverage
gain and the criterion for judging it (e.g. session coverage ≥ 50%). Then
`run_corpus.sh` on the new types under the *existing* prompt version — no
prompt change, so no mixed-corpus problem. Then re-run the specificity gate on
the enlarged corpus; if it fails, the new documents are reported separately
rather than pooled.

**What could go wrong.** 2,440 of the 4,595 are proclamations, and
`political_other` already measured near-zero direction on 816 of those. The
directional gain will be smaller than the coverage gain. The pre-registration
should say so.

### 3.2 Source expansion — ~US$850–1,150 backfill, ~US$180/year to maintain

**What it is.** Four further US government sources, all public-domain and free
to fetch: White House statements and remarks (~500–1,000/yr), Federal Reserve
speeches and testimony (~150/yr), Treasury and OFAC releases (~300/yr), USTR
announcements (~200/yr).

**Why it matters.** Everything read today is a *filed decision*. A tariff
warning, a sanctions signal, a shipping-lane threat — the moment a market
usually moves first — is invisible until it becomes a Federal Register document
days later. This closes that gap with sources that carry no copyright problem,
unlike news text.

**What it needs.** One fetcher per source (about a day each), then a
pre-registration covering three things: which axis each source is expected to
load on, the expected same-day collision rate, and a decision on §7.3. That
last one matters: at 279 collision days the estimated weighting rule is already
admissible; four more sources will push collisions high enough that the fixed
§7.2 rule starts making arbitrary choices daily, and §7.3 becomes worth
registering rather than deferring.

**Commercial framing.** Registered in the business plan §3.4.2 as a paid tier
— reading intentions rather than decisions is a materially different service —
not folded into the base product.

### 3.3 Schema v2 — sector axes — ~US$200–400

**What it is.** The reader's five macro axes (equity, duration, gold, dollar,
oil) cannot represent a sector shock. A steel tariff scores 0.669 specificity
against a 0.550 baseline and near-zero direction: the model sees it clearly and
has no field to report it in.

**Why it matters.** The registered prediction in `asset_extension.py` held
trivially: non-proxy equity assets show lower precedent strength than SPY, and
both are near zero. Macro conditioning adds nothing on any equity asset, so
sector specificity cannot be evaluated until a sector axis exists to evaluate
it on. This is also the item the founder's own reading logic (§2 above) most
likely feeds into.

**What it needs.** `docs/prereg_schema_v2.md` already registers a 100-document
paired pilot with three acceptance criteria. Run the pilot first. **A mixed
corpus is prohibited** — v1 and v2 reads may not be pooled — so a full v2
re-read is a separate, later decision and costs the full corpus again.

### 3.4 GDELT reader profile — ~1 week, plus a design decision

**What it is.** GDELT's event records (CAMEO codes, actors, themes, tone) as a
sixth source, so that a Hormuz closure is seen the hour it happens rather than
when it reaches a filing.

**The obstacle, which is structural rather than time.** A GDELT record has no
magnitude, specificity, novelty or confidence — the four fields §7.2's
registered weighting formula multiplies. A GDELT-derived direction cannot be
weighted by the registered rule without a schema amendment defining how a
machine-coded event maps onto those fields. GDELT also double-counts heavily:
one event, two hundred outlets, two hundred records.

**Two routes.** *(a) Structured:* map codes and tone to the five axes by fixed
rule, no LLM, cheap — needs the schema amendment above and deduplication.
*(b) Text:* fetch article bodies and run the existing reader — blocked by
paywalls, scraper blocks, copyright on article text (which matters in a
regulated business) and recurring cost. Route (a) is the realistic one.

### 3.5 Macro panel extension — UNRATE, ICSA — free, but a re-validation

**What it is.** Add unemployment and weekly claims to the eight FRED series
that define the regimes.

**Why it is not trivial.** Both are revised series, so they need **ALFRED
point-in-time vintages** — which is also the fix for the declared M2SL
look-ahead. And any panel change refits the PCA and moves the regimes, so the
full regime-count validation (seed stability, run length, silhouette) must be
re-run.

**Required protocol, so the app never shows a maintenance state.** Build the
new panel beside the old one as a versioned artifact; validate; switch only on
pass. The app reads whichever artifact is marked current.

### 3.6 Counsel opinion on the exemption — S$20,000

**What it is.** The commercial gate. Route A is cited from MAS Form 20 as a
primary source, but its application to this service, the counting of the
30-investor cap, and the notification deadline are all unresolved. Business
plan §7.4 holds nine questions in writing; §12 budgets the fee.

**Why it is here and not in §2.** It has a registered answer — engage counsel —
that hasn't been executed. Nothing downstream in the commercial track can
proceed without it.

### 3.7 Customer interviews — time, not money

**What it is.** Business plan §4.1 dates an access plan; no conversation has
happened. Every price, segment size and conversion assumption is a labelled
[HYPOTHESIS].

**The one question to ask first.** Whether a boutique's compliance function
would accept an exempt vendor's output in client-facing documents. If not,
§5's value proposition collapses to internal time-saving and the price must
fall. That is the single interview finding that changes the business most.

---

## 4. Potential upgrades — not registered, not costed

Improvements with no pre-registration behind them. Worth doing when there is a
reason; none has one yet.

- **Persist the expanding regime labels to disk** at build time so the app's
  first asset lookup is instant rather than a minute. Touches
  `regime_labels_expanding`, which the whole pipeline depends on — not to be
  done during an active evaluation.
- **Streamlit Community Cloud deployment** so a reviewer gets a URL instead of
  four commands. Ten minutes once the repo is public; not worth it while it is
  private and under review.
- **Client watchlists in the nightly batch** — the paid-tier feature from deck
  slide 8. Technically trivial; commercially meaningless until a client exists.
- **§7.3 estimated source weighting.** Admissible since the collision count
  cleared 50; never authorised. Becomes worth writing when 3.2 raises the
  collision count, not before.
- **Block-bootstrap interval on the forward test**, so that when it has enough
  matured trades it reports an interval, per §3.4.1's "distribution, not a
  point" rule.
- **Founder review of `PROFILES`** in `src/doc_read.py`, as the input to 3.3.

---

## 5. Done — with dates

Kept so that "what was done" stays beside "what was not".

| date | item |
|---|---|
| 2026-08-25 | Corpus read closed at 2,616 / 2,779; gate PASS on full corpus (0.517) |
| 2026-08-26 | Step 3 unblinded: 7 of 45; robustness re-test: 1 of 7; wrong prior #25/#26 (null ignored overlap) |
| 2026-08-26 | FOMC→GLD split FAIL at 4.62×; not a finding |
| 2026-08-27 | Agreement test FAIL in the opposite direction; label ships display-only |
| 2026-08-27 | Step 5 (§7.2 fixed rule), step 6 (decision report), asset extension, regime profiles built |
| 2026-08-27 | App rewritten as a product: three tabs, plain English, any ticker |
| 2026-08-28 | Backtest evidence: costs, short leg, block-permutation p, family test — closes plan §3.3 items 1–6 |
| 2026-08-28 | Business plan revised against all 19 supervisor feedback items; 41 pages |
| 2026-08-28 | Pitch deck, 10 slides; learning journal corrected; Amendment 4 registered |
| 2026-08-28 | `daily_run.sh` on launchd; README; repo made runnable from a fresh clone |
| 2026-08-28 | **Submitted** |
| 2026-09-07 | This file created; Track consolidated here |

---

## 6. Standing rules — apply to every item above

- Every criterion is written and committed before the test exists.
- Amendments are recorded before results are read.
- A result that goes against the project is published, not re-run.
- A grid, not a shot; a distribution, not a point; split data with criteria
  fixed first (business plan §3.4.1).
- The frozen models in `models.yaml` are not touched. The forward test's
  value is that they haven't been.
