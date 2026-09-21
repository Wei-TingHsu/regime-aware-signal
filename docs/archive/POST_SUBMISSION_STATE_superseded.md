> **SUPERSEDED 2026-09-13.** This file is a dated snapshot and is no longer maintained. For current status read `docs/TRACK.md`; for model results read `docs/MODEL_EVOLUTION.md`. Statements here about schedules, what is built, or what is pending may be wrong.

# Where this project stands, and what it does next

*Written 2026-08-28, after submission. This is the handover document: what runs
without anyone touching it, what is registered but not built, and the order to
pick things up in. Nothing here is a plan to do work. It is a record of
decisions already made, so that a future session — or a future collaborator —
does not have to reconstruct them.*

---

## 1. What is running now, unattended

| | |
|---|---|
| **The forward test** | `launchd` job `com.regimeaware.daily`, weekdays 18:30 SGT. Appends one row per model per completed US session to the pre-registered ledger. Verified running 28 Aug. |
| **Document fetch** | Federal Register, last 14 days, every run, free. |
| **Document read** | Capped at 40 new documents per night. Most nights there is nothing new, so cost is effectively zero. |
| **Report generation** | The last 30 document sessions plus the last 10 calendar sessions, so today is always selectable in the app. |
| **The demonstration terminal** | `streamlit run app.py`. Reads pre-generated JSON; computes nothing except the live asset lookup. |

**Two conditions on all of it.** The Mac must be awake at 18:30 — `launchd`
catches up on the next wake rather than skipping, but a machine off for a week
gaps genuinely. And a new dated file in `logs/` each weekday is the only proof
it is working; its absence is the failure mode to watch for.

**Why the gap matters more than the cost.** The forward test's entire value is
that its timestamps make retrospective claim-fitting impossible. A back-filled
row is exactly what the design excludes, so a gap cannot be repaired later — it
is permanent. That is why step 2 of `daily_run.sh` is the one step that fails
loudly rather than continuing.

---

## 2. What the evidence currently says

Stated here because every roadmap item below is a response to one of these.

| Claim | Status |
|---|---|
| Directional engine, all 47 assets | Sharpe **0.51**, dependence-corrected **p = 0.045**. Survives, marginally. |
| Directional engine, survivorship-controlled 35 | Sharpe 0.25, **p = 0.184**. **Retired.** |
| Best of 54 grid configurations | Sharpe 0.73, **family p = 0.090**. Not distinguishable from search noise — the null's best cell averages **0.56**. |
| Transaction costs | Break-even **60.6 bps/side**. Costs are *not* the binding problem. |
| Short leg | **−0.169%/week.** Destroys value. Long-only is 0.83 Sharpe but is approximately the market. |
| Document-conditioned estimator | **1 of 45 cells** survives correct inference — inside the range expected by chance. |
| Reader–history agreement | Predicts **backwards**. Concordant +0.193% vs discordant +0.406%. Label ships as display only. |
| Gold decouples under stress | **Null.** Gap +0.017, p = 0.44. |
| Rotation has a stable order | **Null** across seven hypotheses and four instruments. |

**The honest summary:** one pre-specified model is marginally significant and
everything found by searching is not. That is the shape of a real but weak
effect, and also the shape of no effect at all. On this evidence the two cannot
be separated, and no document in this project claims otherwise.

---

## 3. Registered but not built

Each item below is costed, has a criterion, and requires its own
pre-registration before it runs. **Ordered by value per dollar, not by
interest.**

### 3.1 Read the 4,595 political documents — ~US$60

Already fetched at zero cost and sitting on disk unread. They are notices,
memoranda, determinations and the executive-order types the original fetcher
dropped through a string-match bug (`executive_order` vs `executive order`).

*Effect:* session coverage rises from 30% toward 55–70%, and every political
pool gains precedents — which raises realised ESS and reduces tier-3
abstentions on political-driven days. **The cheapest real improvement available
to the product.**

### 3.2 Source expansion — ~US$850–1,150 backfill, ~US$180/year ongoing

Four further US government sources, all public-domain, all free to fetch:
White House statements and remarks (~500–1,000/yr), Federal Reserve speeches
and testimony (~150/yr), Treasury and OFAC releases (~300/yr), USTR
announcements (~200/yr).

*Why it matters:* everything currently read is a **filed decision**. The moment
a policy is *threatened* — a tariff warning, a sanctions signal, a shipping
lane closing — is where a market usually moves first, and it is invisible here.
Registered in business plan §3.4.2 as a **paid tier**, not a base upgrade.

*Consequence to plan for:* more sources means more same-day collisions, which
moves §7.3's estimated weighting rule from rarely-fires to worth-registering.

### 3.3 Schema v2 — sector axes — ~US$200–400

The reader's five macro axes cannot represent a sector shock. A steel tariff
proclamation scores 0.669 specificity against a 0.550 baseline — the reader
knows exactly what it is looking at and has nowhere to point.

Pre-registered in `docs/prereg_schema_v2.md` with a 100-document paired pilot
and three acceptance criteria. **A mixed corpus is explicitly prohibited:**
v1 and v2 reads may not be pooled.

*The measurement that justifies it:* the registered prediction in
`asset_extension.py` held, but trivially — non-proxy equity assets show lower
precedent strength than SPY, and **both are near zero**, because macro
conditioning adds nothing measurable on any equity asset. Sector specificity
cannot be evaluated until there is a sector axis to evaluate it on.

### 3.4 GDELT reader profile — a week of work, plus a design decision

Two routes, and the cheap one has a structural obstacle worth understanding.

**Route (a), structured.** Map CAMEO codes, actors, themes and tone to the five
axes by fixed rule. No LLM, no scraping, cheap. **But a GDELT event record has
no magnitude, specificity, novelty or confidence** — the four fields §7.2's
registered weighting formula multiplies. A GDELT-derived direction therefore
cannot be weighted by the registered rule without a schema amendment defining
how a machine-coded event maps onto those fields. That is a design problem
requiring pre-registration, not a coding problem. GDELT also double-counts
heavily: one event, two hundred outlets, two hundred records.

**Route (b), text.** Fetch article bodies from GDELT's URLs and run the
existing reader. Blocked by more than time: most outlets block automated
fetching or paywall the body, article text is copyrighted — which matters for a
commercial product in a regulated business — and reading thousands of articles
daily is a recurring cost, not a one-off.

### 3.5 Macro panel extension — UNRATE, ICSA

Both are revised series, so this needs **ALFRED point-in-time vintages** rather
than current values — which is also the fix for the declared M2SL look-ahead in
§3.1.

*Required protocol, so the app never shows a maintenance state:* build the new
panel beside the old one as a versioned artifact, re-run the full regime-count
validation against it, and switch only on pass. The app reads whichever
artifact is marked current.

### 3.6 The standing testing protocol — registered, applies from now

Business plan §3.4.1, registered as a standing requirement rather than a
one-off:

- **A grid, not a shot.** Fewer than 12 cells and a figure is not reportable as
  a performance result.
- **A distribution, not a point.** Median, IQR, min, max, plus the null
  distribution of the best cell. Family p ≥ 0.05 and no cell in the grid may be
  quoted, including cells that individually clear 0.05.
- **Split data, criteria fixed before the split is read.** S1 sign agreement,
  S2 magnitude ≤ 3×, S3 pooled significance, N1 non-overlap or UNDERPOWERED.

**This one costs nothing and applies immediately.** It is a constraint on future
claims, not a project.

### 3.7 Amendment 4 — the ESS knife-edge

`docs/prereg_amendment_4_ess_knife_edge.md`. Target ESS raised to 12 while the
abstention floor stays at 8, so selection aims above the floor rather than at
it; a `MARGINAL` band at [7.5, 8.5) resolving to neither side.

**Explicitly non-retrospective.** The 26 August results stand. Re-running under
the new rule and reporting the new number would be a second look at the same
data with a rule adjusted after the first look; if it is ever run, both results
are reported side by side with their registration dates and the original
remains the headline.

---

## 4. Open questions with no registered answer

Listed because they are genuinely unresolved, not deferred.

**Capacity.** No dollar-volume history exists in this repository, so no AUM
ceiling is stated anywhere. The 46 names ever held are enumerated in
`processed/backtest_evidence.json` so the constraint can be computed the day
volume data is pulled. Market impact is not modelled at all.

**Per-name borrow.** A flat annualised rate is applied. A historical borrow
curve per security is not available, and inventing one would be worse than
saying so.

**Does agreement mark already-priced information?** The registered test failed
in the opposite direction: discordant cases outperformed. Three readings are
consistent with that — noise, pseudo-replication, or agreement genuinely
marking information the market has already absorbed with the residual living in
disagreement. **They cannot be separated on n = 2,024.** Business plan §3.3
records it as a [HYPOTHESIS] and explicitly declines to pursue it, because
turning a failed test around into a new claim requires a fresh pre-registration
written before it runs.

**Whether the compliance function vetoes an unlicensed vendor.** §4.4's
decision-making unit identifies this as the highest-risk assumption in the
plan, and notes it runs backwards from ordinary software procurement: the more
useful the product is, the more likely compliance is to examine it. Falsifiable
in the first ten customer conversations, none of which has occurred.

---

## 5. The commercial track

| Phase | Window | What is sold | Gate to the next |
|---|---|---|---|
| **1** | 0–12 months | Research service to ≤30 accredited investors under FAA s.20(1)(g) / FAR reg 27(1)(d). **S$10,000/firm/year.** | Counsel confirms the exemption. Break-even is the **8th client** against a S$77,400 steady-state cost base. |
| **2** | 12–24 months | Licensed data feed — the regime label and its evidence as an input others build on. | Enough operating history to support a licence application. |
| **3** | 24 months + | The taxonomy itself: others report against these regime definitions. | — |
| **4** | Later | Retail, licence-gated. US$29 / $99 / $299 a month. | A full advisory licence, funded from Phase 1–2 revenue. |

**The immediate commercial gate is legal, not technical.** The exemption is
cited from MAS Form 20 as a primary source, but its application to this service,
the counting of the cap and the notification deadline are all unresolved. §7.4
holds nine questions for counsel; §12 budgets S$20,000 for the opinion.

**No customer conversation has taken place.** §4.1 dates the access plan. Every
price, segment size and conversion assumption in the plan is labelled
[HYPOTHESIS] and none has been tested.

---

## 6. What to do first, if picking this up cold

1. **Check `logs/` for a dated file per weekday.** If they stopped, the forward
   test has a permanent gap and the cause needs finding before anything else.
2. **Read `docs/CURRENT_STATE_2026-08-23.md` §17** — the authoritative record,
   including §17.7 on the step 3 unblinding and its re-test.
3. **Read the wrong-prior tally.** 27 entries, every one a plausible belief
   overturned by running code. It is the fastest way to understand what this
   project has already learned not to assume.
4. **Then §3.1 above** — the 4,595 documents, US$60, biggest coverage gain per
   dollar available.

**The discipline that matters more than any of it:** every criterion is written
and committed before the test exists, amendments are recorded before results
are read, and a result that goes against the project is published rather than
re-run. That practice cost this project its headline number twice and is the
reason the remaining numbers are worth anything.
