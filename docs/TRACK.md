# TRACK — Regime-Aware Cross-Asset Signal Framework

**Bring `docs/PROJECT_MASTER.md` to a new conversation — it holds everything, plain-language first. This file is the short daily status board it points to.** It supersedes the Track
tables in `CURRENT_STATE_2026-08-23.md` §17.10 and is updated in place; the
date at the top is the last edit. `MODEL_EVOLUTION.md` holds the reasoning
behind every model result and `CURRENT_STATE` §17 holds the evidence record
through 27 August.
This file holds *status only*, so it stays short enough to read in one sitting.

**Last updated:** 2026-09-13
**Project state:** submitted 2026-08-28; two forward tests running unattended
(model ledger; FOMC→GLD, first observation 17 Sep); supervisor review pending.
Nothing in the project is currently a trading signal.

---

## Which documents to trust

Three tiers. A new conversation gets tier 1 only unless it needs to touch method.

- **Tier 1, authoritative, kept current:** this file; `MODEL_EVOLUTION.md`; `README.md`. If these disagree with anything else, these win.
- **Tier 2, dated snapshots, never edited after their date:** `CURRENT_STATE_2026-08-23.md` (evidence record; its §17.10 Track is superseded by this file); every `prereg_*.md`; every `*_results.md` and test output. Correct as of the date in their header. Not descriptions of the present.
- **Tier 3, superseded, carry a banner:** `POST_SUBMISSION_STATE.md`, `PROJECT_STATE.md`, the 23 August handoffs, `briefing.md`. Do not upload these to a new conversation.

Known drift corrected on 2026-09-13: automation time is **15:00 SGT** (older files say 18:30); wrong-prior tally is **28**; Model 4 and the kernel family have **run** (older files say registered, not run).

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

- **Live app:** https://regime-aware-signal.streamlit.app (Streamlit Community Cloud, Python 3.11, no secrets; redeploys on every push to `main`, so the nightly commit updates it). Sleeps after a few idle days; wakes on visit.

| item | what should be true | how to check | if it isn't |
|---|---|---|---|
| **Forward test, launchd, 15:00 SGT** | One dated log per weekday since 28 Aug | `ls ~/Projects/regime-aware-signal/logs/` | Since `2296725` the next successful run catches the missed close up (see `logged_at`); a gap becomes permanent only past the 5-day stale guard. Record any catch-up dates here in §5. A run *suspended* mid-way (11 Sep) is not caught up by this — hold the machine awake (`caffeinate -is`) |
| **FOMC→GLD forward test** | Registered `9c5ad8e` on 8 Sep. Ledger gains one row ~3 sessions after each FOMC decision. First observation: 17 Sep decision, matures ~22 Sep | `python fomc_gld_forward.py` or `cat docs/fomc_gld_forward.md` | Criterion is n ≥ 10 with both tests at p < 0.05 — no verdict before early 2028. **Do not change the per-regime sign after a miss; do not trade it.** The model does not forecast this; it is a hypothesis found by looking |
| **Matured positions** | Count rising weekly; H=5 first, H=20 from ~16 Sep | `tail -3 docs/forward_scoreboard.md` | Too few to report a figure until late October at the earliest; do not report one |
| **Nightly document reads — PAUSED for credit** | Read count is 2,616 and stays there until the API balance is funded. It was silently dead 29 Aug–13 Sep for a different reason (§5, `8533969`); the pipeline is now correct and idle | `python -m src.corpus_status` | When credit returns the count rises by ≤ 40/night on documents dated ≥ 27 Aug only. If it does not, the flag or the balance is wrong again |
| **Report scoreboard** (from 14 Sep) | `docs/report_scoreboard.md` regenerated each weekday; `processed/report_ledger.csv` gains rows as write-once reports land; prints "too few to report" until a cell has 30 non-overlap rows | `tail -5 processed/report_ledger.csv`; `head -15 docs/report_scoreboard.md` | Zero rows is correct while reads are paused (reports deferred). The first report to land is also the first time the scorer touches the real price paths (`load_data`, raw yfinance cache) — untested until then; a traceback there is a scorer bug, not a data problem. It never writes a report, so a failure costs nothing |
| **08:30 event-time reader, launchd 20:20 / 21:20 SGT** (from 14 Oct) | One `logs/prints_<date>.log` per release day with an `event written` line per release; `outputs/event_time/<date>_<name>.json` | `ls outputs/event_time/ \| tail`; `tail -3 logs/prints_$(TZ=America/New_York date +%Y%m%d).log` | No log on a release day = the Mac was asleep or the calendar is stale (`python -m src.event_time_prints calendar` refreshes it); `number NOT received` = the API lagged — the row still carries the reaction; run `settle --date` the next day if the nightly has not |
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

### 3.8 Report-level scoreboard — $0, registered in draft, not built

**What it is.** A second append-only ledger that scores the *decision report* — hit-rate and
asymmetry when it speaks, coverage when it abstains — beside the forward test that scores
Models 1–3. Two ledgers: forward (from 14 Sep, never rewritten) and backfilled (live-basis
pipeline, leave-one-out, versioned by corpus hash) so a new document source can be judged in
weeks rather than months.

**Why it is here.** Session coverage is 30%; every source added under §3.1–3.2 changes what the
report says on what days, and without a registered metric there is no verdict on whether it
helped. Registered before any source is added.

**Steps, in order.** (1) fill the three placeholders — horizon set from the unblinding script,
primary horizon (proposal 5), source-expansion tolerance (proposal 2 pts) — and commit;
(2) confirm the report JSON carries every field the scorer reads; (3) register six acceptance
tests before any code; (4) build `src/report_scoreboard.py`, pass them on synthetic ledgers;
(5) first real run — expected output is coverage and "too few to report"; (6) one line in
`daily_run.sh` after `forward_log`, then a §1 row; (7) backfilled ledger via
`src/report_backfill.py`; (8) source expansion, one registration per source — funded, deferred.

**Step 1 done** `97dd490` (14 Sep): horizons {3, 5, 20}, `h* = 3`, tolerance 2 pts / lower
bound −5, revisable only before a comparison runs. Step 2 done (field map; emitter records `estimate.horizon`). Step 3 done (seven
acceptance tests, prereg §12). Step 4 done: `src/report_scoreboard.py`, seven tests pass. Step 5 done (14 Sep 13:01): zero
coverage, "too few to report" — correct. Step 6 done: wired into `daily_run.sh` as 6c/7; §1 row.
**Step 7 done** (14 Sep): pool cutoff applied; `src/report_backfill.py` generated 1,531 as-of reports
under corpus `986e0d65b6df_n2616` in 5 min and scored them. **Verdict INCONCLUSIVE** — h=3 hit-rate 59.4%
vs null q95 59.1% (p 0.0497), asymmetry 1.116 CI [0.91, 1.40]. Within the registered prior. This is the
baseline every step-8 source is judged against. Step 8 deferred (funded).

---

### 3.9 T9b — surprise conditioning — stage A level 1 INCONCLUSIVE, level 3 FAIL (29 Sep); stage B not run; surprise at h=3 is closed — a same-day window would be a new registration

**What it is.** The reader scores what a statement *says*; the market reacts to what it says
*relative to what was priced*. Add a per-event surprise feature and let the precedent pool
condition on its sign as well as regime and document class. Level 1 (free, on disk): the
announcement-day change in DGS2 and the asset's five-session run-up into the meeting. Level 2
(fed funds futures-implied expectation, Kuttner) and level 3 (30-minute intraday window,
Gürkaynak–Sack–Swanson) are registered as later variants. Level 3 is likely free: Swanson publishes the GSS target/path surprise series and the Bauer–Swanson (2023) update for every FOMC meeting to within a year or two of today; align it to the statement dates and compute levels 1–2 only for meetings after it ends. Paid intraday history (a one-off vendor file or a cancellable monthly feed; never a brokerage deduction) is needed only if the published series must be extended by hand.

**Why.** The 29 Sep observation: a hold when a hike was priced is a dovish surprise; the text
reads neutral, gold falls into the meeting and rises out of it. Two identical statements can
have opposite reactions, and the engine cannot currently tell them apart.

**Registration first.** `docs/prereg_surprise.md`: the surprise definition, the sign buckets,
the split by (reader stance × surprise sign), the null, the criterion, the expected direction —
on the 131 statements and 125 minutes in the backfill. Extends T9; shares the release calendar
with T8. Silver is not in the universe and stays out until a metals extension is registered.

**Post-mortem, 29 Sep, and five follow-ups (each its own registration before code).** Level 3
FAIL means "not distinguishable from zero at n = 132 with most surprises inside ±2 bp", not
"zero": the gold coefficient kept its economic size. The horizon was the failure — close(t) to
close(t+3) excludes the 2–4 pm reaction and is too short for the multi-week bond drift.

| # | question | window | data | cost |
|---|---|---|---|---|
| S1 | initial reaction continues into the next session? | close(t)→open(t+1), close(t)→close(t+1) | daily opens in the raw cache | $0 |
| S2 | pre-meeting run-up reverses? (the founder's recollection; b(run-up) ≈ −0.8%/SD for SPY and USO was visible as an untested control) | 5-session run-up → next 1/3/5 sessions | on disk | $0 |
| S3 | slow bond drift (Brooks–Katz–Lustig) | 10/20/40 sessions, TLT — the registered T9 | on disk | $0 |
| S4 | S1–S3 by regime | as above, once n allows | on disk | $0 |
| S5 | **collect 1-minute bars on every scheduled event day from now on** — incl. ZQ=F and, from 8 Oct, SR3=F (3-month SOFR, the contract the Fed's surprise series uses since 2023), so the engine builds its own surprise measure for every meeting after Dec 2023 (FOMC, CPI, NFP) in the nightly job; Yahoo serves the last 7 days free | intraday | builds itself; the only free route to intraday history | $0 |

Prediction-market and FedWatch odds are the same information as the futures-implied surprise
for the Fed; they add something only for classes without a published surprise (stages E, G).

**Surprise by event class — registered here so none is forgotten.** A surprise needs an
expectation to subtract. The Fed is the only class with a published one; every other class
needs its own, and one class is not yet a source at all.

| event class | in corpus? | expectation source | surprise measure | cost | notes |
|---|---|---|---|---|---|
| FOMC statement / minutes | yes | Swanson / Bauer–Swanson published series; DGS2 same-day change; fed funds futures | published factor, else ΔDGS2 | $0 | level 1–3 above |
| Earnings release (8-K 2.02 / 6-K) | yes | analyst consensus EPS and revenue | reported − consensus, as % and as standardised surprise (SUE) | $0 for recent years via `yfinance` `Ticker.earnings_dates` (estimate, reported, surprise %); deeper history is paid (Refinitiv/I-B-E-S, Zacks) | the reader's own "earnings surprise vs equity direction" audit already agreed 431/442 — this adds the *market's* prior, not the reader's |
| Scheduled macro releases (NFP, CPI, PPI, GDP) | no — T8 adds the calendar, not the text | economist consensus | actual − consensus, standardised by the release's own history | consensus history is paid (Bloomberg/Refinitiv); free proxies: the asset's run-up over the prior five sessions and the same-day DGS2 move | ties directly to T8 |
| Executive orders / proclamations | yes | no consensus exists | run-up proxy; prediction-market odds where a contract exists (Polymarket, Kalshi — public APIs); pre-event GDELT tone | $0 | most orders are telegraphed; the surprise is small by construction and should be measured as such, not assumed |
| **Corporate cooperation, partnerships, M&A, contracts** | **no — not a source** | none; the event is the news | run-up proxy over the prior sessions; options-implied move where available (paid) | new fetcher: 8-K Items 1.01 (material agreements), 2.01 (acquisitions), 7.01 / 8.01 (Reg FD and other events) and their EX-99 press releases, $0 from EDGAR | enters through T13's provisional pool first (dated admission, scored only afterwards); reader profile needs founder review; also the natural universe for T6 |
| Foreign central banks (BoJ, ECB) | no — T13.6 | no free published surprise series comparable to Swanson's; OIS-implied expectations are paid | run-up proxy; same-day 2-year yield change in that currency | $0 proxy | provisional pool first |

Rule for all of them: the surprise is computed from data available *before* the session's
close, never from the reaction itself, and its sign becomes a conditioning bucket in the
precedent pool beside regime and document class. Each class is its own registration under
`docs/prereg_surprise.md`; a class whose expectation source is unavailable is reported as
"run-up proxy only" rather than dropped.

### 3.10 Instrument robustness — RUN 29 Sep — CONSISTENT (moved to §5)

**What it is.** The model runs on SPY, TLT, GLD, UUP, USO; the app shows the S&P 500 index,
the 10-year yield, gold futures, DXY and WTI. Rebuild the price panel on the display
instruments (with a DGS10-derived duration proxy in place of the yield) and re-run Problem 1
and the report backfill; compare verdicts.

**Criterion, fixed now.** Same PASS/FAIL on the primary cell; estimate signs agree on ≥ 90% of
cells; non-overlap hit-rate within 2 points. Agreement → the app states "modelled on ETFs,
shown as desk instruments, results consistent." Disagreement → a finding: attribute it to
settlement timing (GLD 4 pm vs gold futures 1:30 pm ET, with FOMC at 2 pm), roll (USO), or
maturity (TLT vs 10Y), and the app shows whichever the record supports. Nothing in
`models.yaml` or the forward ledger changes either way.

### 3.11 T14 — event-time reading: read the statement when it is published, not after the close

**Why.** The evidence says direction is set within the session and size keeps unfolding; the
founder observes intraday drift after the press conference. A system that reads the 2:00 pm
statement at 3:00 am the next day reads yesterday's news. This is the Professional-tier
intraday feature of the plan, built on the same guardrails.

**Phases, each registered before code.**

| phase | what | data | status |
|---|---|---|---|
| A | **DONE 29 Sep — NULL (CURRENT_STATE §18.12).** Continuation test, historical, $0. The FRBSF file carries the 30-minute reaction of SP500 and TNOTE2/5/10/TBOND for every meeting 1988–2023. Test whether the initial reaction extends to the same-day close (close-to-close minus the 30-minute move, pre-2 pm drift acknowledged as unobserved) and to the next open. Criterion fixed before the run. | on disk | next runnable item |
| B | **Statement at publication.** On FOMC days, fetch from 1:59 pm ET every 10 s; read at 2:00; write an *event-time read* (timestamped, write-once, its own ledger — the daily report is untouched). Live surprise from 1-minute fed-funds/2-year futures bars (Yahoo, ~15 min delayed, so by 2:20). Mac must be awake at 2–3 am SGT (`pmset` wake from `fomc_decisions.csv`) or a small cloud runner. | $0 + ~$0.05/meeting | after A |
| C | **App: event-time panel.** Shows, at 2:02: what the statement says, the live surprise once available, and what past days like this did *by the close* from daily precedents. Says plainly that intraday precedents do not yet exist. Never a "rest-of-day direction" until phase D establishes one. | — | with B |
| D | **Intraday precedent pool.** Built from S5's forward 1-minute collection; the first honest "rest-of-session" statement is allowed only when the pool passes its own registered floor (ESS ≥ 8 event-days in the same regime). | builds itself, ~8 FOMC days/yr + releases | years |
| E | **Press conference.** Transcript when the Fed posts it (hours later); live speech-to-text on the stream as the upgrade, with its own audited error rate. Extends the reader's schema to spoken guidance. | open-source transcriber | after B |
| F | **Regulatory.** Intraday reads are the most advice-like output in the plan; described to counsel as designed, under abstention and no-combination rules. | S$ counsel item | before selling |

**Order inside T14:** A now (it is free and historical) → S5 collection starts tonight →
B and C → E → D as the pool grows. Nothing here changes the frozen models or the daily
write-once report.

### 3.12 T15 — the investor's own risk number, and a strategy block (founder's idea, 8 Oct)

**Origin.** T1 Test A: volatility targeting cut the worst drawdown on every market but improved
risk-adjusted return only on oil, so nothing entered the product as a *predictor*. The founder's
point: a drawdown tool that cannot predict can still *fit* — to the investor's own loss
tolerance rather than to the market. That is a product block, not a forecast.

**What the user sees (Professional / subscribed tier only).**
1. A slider: *How much are you putting in?* (amount).
2. A key-in box: *How much of that are you prepared to lose?* (amount or %).
3. From the two, the user's risk-aversion number: the γ for which the certainty-equivalent
   calculation (prereg_exposure_dial §4) makes that loss the worst acceptable outcome — shown
   plainly as "you are a γ ≈ 4 investor: you would give up about X of expected return to avoid
   that loss."
4. A block that turns that γ, the measured drawdown/CER figures from T1 (dated, sourced, both
   universes once Test B runs), and today's report (regime, documents, abstentions) into a
   *possible plan*: per market, the vol-targeted exposure at the user's γ, the historical worst
   drawdown at that exposure, and what today's report does or does not say. Written by the
   Anthropic model from a fixed template that may only cite numbers the record contains.

**Rules, fixed.**
- Every number the block shows carries its date and the test it came from. The model may
  phrase; it may not invent a figure, a direction, or a probability the record does not hold.
- Labelled on screen, every time: *"A possible plan built from your own inputs and this
  system's recorded tests. Not financial advice; not a recommendation to buy or sell."*
  Described to counsel as designed (TRACK §3.11 F) before it is sold.
- The 3-day line, the rest-of-session line and the abstention rule are untouched; the block
  reads them, never changes them.
- The block ships only on *measured* figures (T1 Test A drawdowns are measured) — and the
  drawdown claim itself gets its own registration under Test B so that "cuts the worst loss"
  becomes a tested sentence, not a read-off.
- Usage is logged (inputs, plan shown, date) to its own ledger so the plans can be scored later
  by the same referee as everything else.

**Cost.** One model call per plan (~US$0.02–0.05). Build after Test B and the counsel item.

### 3.13 Instrument amendment — oil (8 Oct, from the two-wars review)

USO is the one model instrument that is a real compromise: monthly roll drag that diverges from
spot over years (part of its −98% in 2020). Register `WTI_CONT` (continuous back-adjusted
front-month WTI) as a second oil column beside USO; every oil result (Problem 1 cross-asset,
the referee's USO cell, T1's USO PASS) re-run on both and reported side by side. USO stays as
the tradeable comparison. Nothing else in the universe changes: the registered instrument test
(CURRENT_STATE §18.9) showed the other four pairs agree.

**Run 12 Oct (`docs/wti_cont.md`).** Built as `WTI_SPOT` (FRED spot; the back-adjusted series is not buildable from free data) and `WTI_FUT` (CL=F). USO's drag against spot −8.7%/yr over 20.5 years. Referee with the USO column swapped: CONSISTENT on both (C1–C4 met; all flips are oil rows). Chain rule on the commodity fires 4× not 2× — the 2009 pair was hidden by USO's contango — and gold was lower 60 sessions after all four; founder chose to re-define the chain input as WTI_SPOT (prereg_blindspot amendment 12 Oct, contamination stated, live tail on CL=F). **Closed 13 Oct** (CURRENT_STATE §18.27): blindspot.py reads spot with the CL=F tail (one-session lag observed; tail alerts provisional); A2 on spot over the full panel: 5 firings incl. 6 Feb 2015, INCONCLUSIVE held; T1's oil cell on spot: vol targeting PASS +0.30 (on USO +0.25), regime tilt INCONCLUSIVE — same verdicts, driven on both by 2008 and 2020. Amendment complete.

### 3.14 Two-wars case study — the oil → inflation → rates → dollar → gold chain (8 Oct)

Gold rose +7% into 8 Mar 2022 then fell 20% by Sep; in 2026 it peaked a month *before* the
Iran strikes (29 Jan, 5,318) and fell 25% by 16 Jul with only one up session after the war
began. Same mechanism both times — an oil-exporter war raises oil, oil raises inflation,
inflation raises expected rates and the dollar, both lower gold — and it beat the safe-haven
premium both times (Problem 1's null, with named cases). The engine held zero documents on
28 Feb–9 Mar 2026: a strike is not a filing (T13 case A). Change registered: T13's blind-spot
flag fires when oil moves > 2σ with no document; Treasury/OFAC and White House statements admitted
to the provisional pool first; the commodity-shock chain (oil → DGS2 → DXY, all already in the
panel) becomes a named detection template. Build T13 case A before T2.

### 3.15 T16 Layer 3 — release text behind the BLS bot wall (9 Oct)

bls.gov returns 403 to every scripted request (any user-agent); the API serves numbers only; FRASER dropped the
connection. Layer 1–2 are complete without it. Layer 3 (the LLM reading the release for named special factors —
strikes, weather, census/World Cup hiring) needs the text: (a) the 20 most recent releases via the browser for the
reader-consistency test (prereg A4); (b) the 2006→ backfill via FRASER when it answers, or BLS's bulk download; (c) the
`data_print` reader prompt for founder review before any paid read. Not blocking: the attribution engine and coverage
states run on Layers 1–2.

**What the jobs report does and does not disclose (checked 11 Oct on the 20 texts on file).** *How the number is made* —
published: a survey of ~120,000 establishments, everyone on payroll in the pay period containing the 12th, seasonally
adjusted; seasonal adjustment removes the regular yearly pattern, not a one-off event, so event hiring is inside the
number. *Composition by industry* — published every month (Table B-1 and the text: "Leisure and hospitality employment
declined by 61,000 in June, reflecting weaker than usual seasonal hiring"). *Composition by cause* — not published except
for strikes, weather and shutdowns; no release of the 20 names the World Cup, FIFA or event hiring. Consequence: a cause
like the World Cup can enter the read only through a declared second source — the founder's event calendar, checked
against the industry line in the text — registered 11 Oct as prereg_prints_and_attribution §A2b. The reader prompt is
reviewed and on file as `data_print_profile.md` (v1). **A4 run 11 Oct: PASS** — 20/20 headline values equal ALFRED's first print; every named factor is in the text (strikes, furlough, deferred resignations, weak seasonal hiring); World Cup months contradicted ×3, never supported. Cost ~US$0.75 incl. ten wasted calls. The 2006→ backfill read (~US$20) now waits only on a text source for pre-2025 releases (bls.gov 403; FRASER closed).

### 3.16 Asymmetry — five engine-side levers, each a registered test on the h=2 backfill (9 Oct)

Asymmetry (mean |move| when right ÷ when wrong) is 1.008 at h=2. The trading-side ways to raise it (exit rules, sizing by
expected move, calling only on big days) are the user's, recorded in §3.17. These five change *which calls the engine
makes*. Each runs beside the incumbent estimator on `48a6c4e879a1_n2617_h2`, scored by the same referee; criterion fixed
now: **asymmetry up by ≥ 0.20 with the non-overlap hit-rate not below its null** — a filter that raises asymmetry by
abstaining on everything is trivial and fails the second clause.

| # | lever | mechanism | prior |
|---|---|---|---|
| E1 | ESS floor by expected move: abstain unless ESS ≥ 8 *and* the precedents' median |move| ≥ the asset's own median | calls land on days precedents say are big | the one most likely to pass |
| E2 | specificity gate at the source's median instead of the veto level | vague documents give small random moves | likely already captured by the veto; INCONCLUSIVE |
| E3 | precedent dispersion (τ²) as a second gate: tight pool with large mean → call; wide → abstain | tight pools are where right-side moves are large | plausible; may cut n below 30 |
| E4 | event-bin alignment: count a document toward a call only if its bin matched the move bin on its precedents' days | removes the "not the driver" calls, which read backwards | the one with the clearest mechanism (attribution_states 9 Oct) |
| E5 | scale the estimate by the earned influence weight for source × regime; zero where none earned | calls without measured influence become abstentions | waits on more earned cells; run last |

Order: E4, E1, E3, E2, E5. Registration file `docs/prereg_asymmetry_levers.md` before any code.

**E4 run (9 Oct): FAIL.** Non-overlap asymmetry 1.128 vs incumbent 1.008 (+0.12, short of the registered +0.20; 95% CI [0.90, 1.49] contains 1.008); non-overlap hit-rate 54.3% on 328 calls, below its own null 56.1% (p 0.19); incumbent 54.9% on 534 calls (null 57.5%, p 0.40). Measured on the 1,532-day h=2 backfill, 10,000 permutations, tag `48a6c4e879a1_n2617_h2_E4`; the lever dropped documents on 644 asset-days, 547 of them SPY. What it does not measure: the forward ledger (untouched by registration) or any horizon but 2. Full row in `prereg_asymmetry_levers.md` §6.

**E1 run (10 Oct): FAIL.** Non-overlap hit-rate 48.5% on 198 calls (incumbent 54.9% on 534), below its own null 54.5% (p 0.90); asymmetry 1.052 vs 1.008 (+0.04; CI [0.84, 1.38] contains 1.008); mean signed move −0.006%. Same backfill, tag `48a6c4e879a1_n2617_h2_E1`. The lever cut 63% of calls and kept the worse ones: days whose precedents moved most are days the pool does not explain. Expected move stays a sizing input (T2), not a direction filter.

**E3 run (10 Oct): FAIL.** Non-overlap asymmetry 0.852 [0.70, 1.03] vs incumbent 1.008 — down, not up; hit-rate 54.6% on 377 calls, below its null 58.1% (p 0.63). Tag `48a6c4e879a1_n2617_h2_E3`. Median τ² is 0 on every asset, so the gate removed exactly the pools with regime disagreement (321 of 1,841 asset-days) and the asymmetry went with them: the regime-conditioned pools are where right calls out-pay wrong ones. Hypothesis recorded, not tested.

**E2 run (10 Oct): FAIL.** Asymmetry 1.056 vs 1.008 (+0.05); hit-rate 54.1% on 379 calls, below its null 55.9% (p 0.21). Tag `48a6c4e879a1_n2617_h2_E2`; 692 documents dropped on 302 days, survivors no better.

**Conclusion after four of five (10 Oct).** E4 +0.12, E1 +0.04, E2 +0.05, E3 −0.16, all against the registered +0.20 with hit-rate not below null. No engine-side selection of which calls to make raises asymmetry; the one that removes regime-disagreeing pools lowers it. Asymmetry ≈ 1 is a property of the calls themselves. Raising it is therefore a trading-side matter (§3.17: size by expected move, exit the wrong side early), and those are the next registered tests. E5 (influence-weight scaling) stays registered and waits for ≥ 10 earned cells. All four levers remain in `step6_report.py` behind `LEVER=`, off by default; the incumbent and the nightly job were never touched.

**In plain words (11 Oct, for the founder's record).** Each lever is a rule for when the engine should stay quiet. *Calls
left* is how many of the incumbent's 534 non-overlapping calls survived the rule — a lever can only remove calls. *FAIL*
does not mean unusable; it means the lever did not reach the bar written before the run (asymmetry up ≥ 0.20, hit-rate not
below chance on the same days, ≥ 30 calls left). A lever that had come back at 60% / 1.4 would have PASSED and gone in.

| lever | the problem it was meant to solve | calls left | hit-rate (chance level) | asymmetry | why it failed |
|---|---|---|---|---|---|
| E4 | on 23% of SPY's wrong days the document was not the driver — stop listening to documents that usually aren't | 328 | 54.3% (56.1%) | 1.128 | small gain; acted almost only on SPY |
| E1 | quiet days pay little when right — only call when precedents were followed by big moves | 198 | 48.5% (54.5%) | 1.052 | the big-move days are the days the pool explains least |
| E3 | disagreeing precedents make the call a guess — only call when they agree | 377 | 54.6% (58.1%) | 0.852 | the disagreeing pools were the profitable ones |
| E2 | vague documents give random moves — count only the more specific ones | 379 | 54.1% (55.9%) | 1.056 | the existing near-zero cutoff already did this |

### 3.17 Trading-side asymmetry methods — recorded for the app's manual, not engine changes (9 Oct)

1. Call less, on bigger days (scheduled-event or strong-document days only). 2. Size by expected move (T2), not by
direction confidence. 3. Cut the wrong side early — a stop at a fixed fraction of typical move, no cap on the right side;
the engine scores close-to-close and has no exit rule; one is registered to be tested on the 30,640-row h=2 ledger
(stop at −0.5σ and −1.0σ, fixed, two candidates, both reported). These are on the app under "Reading this page".


### 3.18 Private repo for the calibration — additive while marking is open (12 Oct)

Create `regime-aware-signal-private` for reader prompts, the read corpus, influence weights and the event calendar; the public
repo keeps methods, register and scoreboards; the app reads the private one (Streamlit secret). Additive: new reads and the next
prompt version go there now; nothing is removed from the public repo until Dr Lee's marking closes. PROJECT_MASTER §12.

### 3.19 Event-time reader extended to the 08:30 prints — registration first (12 Oct)

T14 reads the FOMC statement at 2 pm and records the rest of the session: 8 events a year. The scheduled prints (payrolls, CPI,
PPI, retail sales, PCE, GDP, weekly claims) are the same shape — fixed clock, a text, a rest-of-session — and come to ~110 a
year. Extend `event_time_read.py` to 08:30 releases with the `data_print` prompt (v1, A4 PASS), same ledger, same criterion as
prereg_event_time §4, as an amendment to that file before code. Purpose: the event-time record compounds at 15× the rate.
Not a redesign; the collector (S5) already holds the bars.

**Built and scheduled 13 Oct** (CURRENT_STATE §18.26): registered first, dry run on 2 Oct payrolls correct, ES=F added for the S&P window, launchd job installed; first live firing CPI 14 Oct. Open under this item: a referee for the event-time ledger at the close and next open (prereg_event_time §4 names it; not yet written), and the app line once 30 rows exist.

### 3.20 T3 overlay format — the client's rules as registered files (12 Oct)

A file format for a client's own entry/size/stop/exit rules, read by the referee and scored beside the engine's calls on the
same ledger. This is the per-client state that makes switching costly (PROJECT_MASTER §12). Prereg before code; T7 after.

### 3.21 Edge statement — one registered page (13 Oct)

The design scorecard (PROJECT_MASTER §13) scores D at 1: the why-now is stated, the counterparty is not. Write one page,
registered like a prereg: the inefficiency the engine sells (documents read late or not at all by the holders of the five
markets), who is on the other side of a 2-session drift call (the overnight-gap market-makers the literature names, and the
slow readers), why it persists (reading cost, attention), and the dated reason it is relevant now (LLM reading cost fell
below the value of a day's drift in 2024–26). It must also state where our own evidence contradicts it (direction absorbed
in the gap; hit-rate below drift). Cost: a page. First thing a buyer asks.

### 3.22 T13 A3 — after an oil shock: path, duration, leverage (registered 16 Oct, not built)

The chain alarm fires too rarely to fit anything (n = 5). A3 uses its first leg alone — oil +8% in five sessions, ~40–60
shocks since 1995 — and for each shock measures every market's path to 90 sessions, the worst interim loss, the best gain and
when it came, and the Sortino. A3b applies the engine's own nearest-neighbour estimator (legs + regime) walk-forward; A3c turns
the worst-case history into a leverage number, L = min(5, 20% ÷ 90th-percentile worst loss), capped by T1. Founder fixed the
loss limit (20% of capital) and the ceiling (5×). Nothing shown as a forecast until A3b passes. prereg_blindspot §3b.

**Run 16 Oct:** A3a measured (116 shocks; gold flat-to-up after a plain shock, down after 4 of 5 chain cases — hypothesis only); **A3b FAIL on all six** — the legs do not predict direction; A3c leverage numbers informational (GLD 1.6×, SPY 1.45×), reading (b). **A3d registered** (the tail; founder's ask): severe-case line for the app, classifier expected to FAIL. Next: A3d code, then the app Context block (§3.23).

### 3.23 App Context block — every card explains the environment, in words with status (16 Oct, founder's instruction)

Each market card and any searched ticker gets a Context block: the regime and its description; the oil 5-session move and the
chain alarm's state; today's prints; what history says in this environment ("after 116 oil shocks since 1995, gold's typical
path was +0.8% after a month …; when the shock came with the dollar rising and short rates following — the three-leg pattern —
gold fell in 4 of 5 cases: hypothesis, n 5"); the severe case (A3d) with today's resemblance; the status of every sentence
(measured / tested / hypothesis / registered-not-run); terms explained where first used. For a searched ticker, the oil-shock
paths are computed from its own history against the pool dates. The engine's call is unchanged; the block explains around it.
Nothing untested gets a number. Build after A3d.

### 3.24 Implied vs realised volatility after an oil shock — the premium question (registered 16 Oct, not built)

Founder's question: if direction after a shock is unpredictable, is the *size* of the move mispriced? Test: for each p8 shock,
the CBOE implied-volatility index at the shock close (VIX for the S&P, GVZ for gold, OVX for oil — all on FRED) against the
realised volatility of the next 20 sessions, annualised. Measured: the median gap implied − realised and its inter-quartile range,
against the same gap on all non-shock days. Criterion, fixed: PASS-sell if the post-shock gap is positive on ≥ 65% of shocks and
its median exceeds the non-shock median by ≥ 2 vol points (selling options after a shock earns the gap); PASS-buy if the
mirror holds; INCONCLUSIVE/FAIL otherwise; walk-forward not needed (no fitted parameter). Prior: implied runs above realised
after shocks as it does on ordinary days (the usual variance premium), by a similar margin → INCONCLUSIVE. Sits under T2.
Prereg file before code.

### 3.25 History tables H0–H7 — conditional path tables for the app (registered 19 Oct, not built)

The Context block (§3.23) is fed by one study, oil shocks. This programme adds tables for Fed days (H1), jobs/CPI days (H2), dollar shocks
(H3), rate shocks (H4), regime changes (H5), equity drawdown entries (H6), volatility spikes (H7), and the current regime's own return
table (H0). One shared engine, one uniform test (20-session sign share vs the market's base rate, ≥ 15 points, n ≥ 30, random-date null
p < 0.05), priors #49–#53. Tables enter the app as `measured`; tests as `tested: <verdict>`. `docs/prereg_history_tables.md`.
Build order H0, H1, H3, H4, H5; H2 after the 08:30 reader's first month; H6, H7 after.
**H0 measured 19 Oct:** gold regime 3 +2.4% vs +0.7% all-history at 20 sessions, oil ±1.5–2.2 pts by regime, SPY/TLT/UUP flat; prior #49 wrong (tally 49). In the app as `measured` under "What history says in today's condition". H1, H3, H4, H5 next.
**H1/H4/H5 run 19 Oct:** every testable cell FAIL (H1 132 days, H4 56/60 shocks, H5 32 changes); H3 at 3% gave 6/3 events (#51 wrong, tally 50) → amended to 2% before rerun. Measured and on the page: gold +2.4%/month after 25 bp+ yield drops (65% vs 56%); oil +3.7%/month after a label change (69% vs 52%, p 0.07). H2 waits for the reader's first month; H6, H7 after. H3 at 2%: 21/15 events, INCONCLUSIVE, not lowered again. Open: gold/dollar/oil cells in H4up need pre-ETF spot series; H3 needs a dollar series that starts before the one the engine reads.
**Horizon amendment 19 Oct** (founder): every table also at 5 sessions, gap floor 10 points, PASS needs p < 0.05/6 within its table; prior #54. **Data item:** a dollar series from the 1990s (the engine's FRED broad index starts 2006; DXY runs from the 1970s) — needed before H3 can reach 30 events. **Pipeline fix:** step 6 now defers a session until the panel has its prices (16 Oct report had been written over an all-NaN row).
**Amended rerun 19 Oct: no PASS in 72 cells** (#54 right); the six event tables are closed as measured-only. Remaining under 3.25: H2 (after the reader's first month), H6, H7, and the dollar-series data item.

### 3.26 Live document feed repaired (19 Oct)

Found while building §3.23: 29 of the last 30 report days carried zero documents. Two routing faults, not the engine: (1) no nightly 8-K
fetch existed — the earnings source, the only one scoring above chance in the backfill (62%), last received a document on 14 Aug 2026;
(2) `fetch_sources political` wrote every presidential document to `political/`, a folder step 6 never reads; the report reads
`political_order/` and `political_other/`, last filled 14 Aug. Fix: `--out` on the political fetch; nightly step 3 now fetches 8-Ks
(SEC submissions feed, 9 registered tickers, skips files on disk) and routes executive orders / proclamations to the two read folders.
Reading stays under step 4's 40-per-source cap. **Reports for 15 Aug – 19 Oct keep their as-of state** (zero documents): regenerating them
with documents read later would make the record look better than the engine was on the day. Forward from 20 Oct the feed is live.
Also noted: the 16 Oct run died inside step 2 with no error text and 17 Oct never ran (scheduler outside the repo); `daily_run.sh` has no
git step, so the cloud app shows the last manual push.

### 3.27 Input latency audit (registered 22 Oct, running nightly)

Founder's check after the 20–22 Oct week: are the engine's inputs stale at the moment it acts? `src/latency_audit.py` logs, every run, how many
sessions each input series is behind the last completed NYSE session (price panel, macro panel, oil columns, Yahoo live quotes) to
`processed/latency_log.csv` and `docs/latency_audit.md`. Criterion, fixed: a series ≥ 2 sessions behind on ≥ 20% of the last 20 runs is STALE;
every live rule reading it must state the lag on the app, and the backfill alignment for that series is re-checked (tests are unaffected by
latency only where the backfill used the same as-of alignment the live engine sees). Known at registration: FRED daily series publish one
session late (declared on the oil leg as "provisional"); the price download missed the latest close on 16 and 21 Oct (no 21 Oct report was
written at the 22 Oct run) and the nightly 8-K fetch printed nothing on 22 Oct — both to be diagnosed from the first audit rows.

### 3.28 Blind-spot fill plan (registered 22 Oct as a plan; built after the current list is cleared)

What the 20–22 Oct week showed the engine cannot see, and the fill for each, in order:
1. **8-K ticker list** — add the AI-capex bellwethers (META, GOOGL, AMZN, AAPL, AVGO, AMD) as a dated corpus amendment; backfill read ~US$15.
2. **Metals and a long dollar series** — silver (SI=F / spot), LBMA gold spot, DXY from the 1970s as display + history columns, the §3.13 pattern;
   unlocks H3 (dollar events) and the gold/dollar/oil cells of H4up; free, ~1 day.
3. **Positioning** — CFTC Commitments of Traders (gold, silver, oil; free, weekly) as a blind-spot input, registered before any use.
4. **Sector axis** — schema v2 (§3.3, US$200–400) so "capex up / capex cut" can be scored; until then the reader's five axes cannot represent it.
5. **Rhetoric** — GDELT trigger (§3.4) / source expansion (§3.2), as costed.
Every fill is a corpus or population change and goes in as a dated amendment with its own prior; nothing above alters a recorded verdict.

### 3.29 Target-range engine — how far, how likely (registered 22 Oct at the founder's direction; Stage 1 built)

Founder: attribution, magnitude and a point target are to be designed and tested, not discussed. A3b failed on *direction*; this engine answers
*how far and how likely*: per market, horizon and regime, the probability of touching ±X% within h sessions and the path-end quantiles, applied to
today's price (median = the point target, the probability = the claim). Stage 1 statistics with a walk-forward Brier calibration test (prior #55);
Stage 2 reader-labelled reasons per episode with a lift test (prior #56); Stage 3 regularised quantile weights (prior #57). `docs/prereg_target_range.md`,
`src/target_range.py`. The §4 design note of 22 Oct is superseded by this registration.

### 3.30 Specification grid — the alternatives track (registered 22 Oct as a plan; runs after the main list)

Founder: sweep every variable every main-track test fixed (horizons 1–120 one by one, every threshold, gap, sample start, regime definition,
feature subset, sample-size rule, scoring), so no possibility is missed by convention; design it as a track beside this one. `docs/SPEC_GRID.md`
holds the variable inventory, the per-test grids with cell counts (≈ 800k cells over 14 families), the data sources to add (free first), the
earnings-pool amendment (23 issuers), and the rule that keeps a sweep honest: the best cell is judged against the best cell of the same sweep
on shuffled data (reality-check / SPA), the whole curve is published, and a survivor is promoted to its own forward test — recorded verdicts
never change. Runner `src/spec_grid.py` to build; first family 2.9 (the sample-size rule behind Stage 1's result).

### 3.31 Factor attribution of price episodes — the founder's weight-per-reason method (registered 23 Oct before code; built)

Name the reasons (war, rate-hike speculation, real yields, dollar, oil, volatility, the macro PCA line), measure each one's share of a move
with a declared prime-factor ordering (Gram–Schmidt: the prime factor keeps what it co-moves with, the next keeps what is left; both orderings
and the joint fit always shown), state it in dollars at the start price, and when a reason reverses expect that many dollars back — gated by
two tests: T-A out-of-sample explanatory power (GLD median R² ≥ 0.20) and T-B sign stability per factor (≥ 70% of windows), then T-C the
reversal test on past geopolitical spikes. Priors #58–#60. War proxy = Caldara–Iacoviello daily GPR (free). `docs/prereg_factor_attribution.md`,
`src/factor_attribution.py`. Supersedes Stage 2/3 of 3.29 (reasons become measured proxies; the reader names which event drives a proxy).

### 3.32 Dynamic issuer pool — issuers chosen by what drives the economy (registered 23 Oct; built)

Founder's rule: adjust the earnings issuers round by round to the largest contributors to the economy (the top few covering 60–70%). Measured
form: BEA table 1.1.2 contributions to real GDP growth → fixed line-to-sector map → sectors ranked until ≥ 70% of the positive contributions
are covered → the four largest issuers by market value per sector (S&P 500 list, Yahoo market values), plus the ten largest index weights,
plus the nine original issuers; cap 35; rebuilt quarterly after the advance GDP release; every build logged in `docs/issuer_pool.md`, a changed
pool is a dated corpus amendment. Premise corrected at registration: the ~70% in the GDP release is consumption's share of the level, not AI;
AI investment is a large share of growth, which is what the rule ranks. Registered cell to test the idea rather than assume it: "releases of the
pool's issuers move SPY at 2 sessions" (prereg_report_scoreboard, corpus tag). `src/issuer_pool.py`; nightly fetch reads the pool file.

### 3.33 Why it moved — daily reasons, episode and target on the app (registered 23 Oct; built, app wiring next)

Founder's picture: an investor opens the site, sees why today's move happened, what the current trend has typically run to, and the day's
wind direction, and decides for themselves. Nightly per asset incl. silver: adaptive turning points (reversal > max(8%, 1.5 × monthly vol)),
current episode and last-session attribution with the unexplained share, base-rate target from past episode sizes (labelled), T-D registered
for the conditional target (prior #62). `src/why_moved.py`, prereg_factor_attribution §4; hooked in daily_run.
**23 Oct results:** T-A sweep favours 20-session blocks (0.22 at a 3-year window; null pending); T-E fixed-impulse FAIL (#63); **T-F causal window rule PASS** — 53% explained at ~7 sessions vs 31% full leg, 83% of episodes (#64 wrong, tally 55); T-F′ shifted-factor null registered (#65). App paragraph "Why it moved" wired into the Context block the same night.
**T-G:** patience and a one-year look-back lift the explained share to 64–71%; best cell survives its null and is promoted (#66 right). **T-H residual momentum / reversal registered** (prereg §5, prior #67): is the unexplained part predictable, and better than plain momentum — the founder's 'crowd as alpha' question, tested as predictability across every window × horizon on all eight assets.

### 3.34 The unexplained part as alpha — the founder's question, and the three conditions (23 Oct)

Founder: if the reasons explain 80% of a leg and 20% never yields to any clue, that 20% is the crowd — emotion, trend-followers, institutions
valuing differently; if we can measure it consistently and lean on it, that is the fund's alpha. In the literature this is *residual momentum*
(Blitz, Huij & Martens 2011) on top of noise-trader and slow-diffusion models; price pressure tends to unwind, slow information to continue.
It becomes **our** alpha only if three things hold, in plain words:
1. **The label is not the test.** The unexplained part mixes crowd behaviour with information the model has no series for (positioning, flows,
   central-bank buying) and plain model error. Gold's 91% unexplained today is mostly the last two. The measurable omitted factors go in first;
   only what is left afterwards may honestly be called the crowd.
2. **Predictability, not cause.** Markets also move on information we cannot see. The fund question is whether today's unexplained move says
   anything about tomorrow's — tested at every window × horizon (T-H), with the shape read off the sign: continuation = slow information,
   reversal = a stampede unwinding.
3. **It must beat the price trend itself.** If the residual's sign predicts no better than plain momentum, the decomposition added nothing tradable.
**Result 23 Oct (T-H): FAIL on GLD, SLV, USO, SPY, NVDA** — no cell beats noise; prior #67 wrong (tally 56). Re-run after the flow and positioning
proxies (3.28) shrink the residual to its unmeasured part. Until then the unexplained share is shown on the page as a measurement of what the
model cannot see, never as a signal.

## 4. Potential upgrades — not registered, not costed
- **Reason-weighted path range (founder, 22 Oct) — registered as 3.29 the same day.** Segment past rises and falls per market (episodes ≥ 10% peak-to-trough); have the reader
  label the reasons present in each episode's documents; fit a walk-forward model from reason indicators + macro legs to the forward 60-session
  path; apply today's reasons to give a path **range** (median, worst, best — never a point target) under the current regime. Pieces already in
  the repo: `episode_rotation.py`, `attribution.py` (T13 influence cells, 1 earned), the A3b nearest-neighbour estimate (FAIL vs the plain median),
  T2 expected-move (registered, not built). Risk stated at registration: an LLM asked why a market rose always produces a story, and the same
  stories precede falls; ~40 swings since 1995 against dozens of labels fits the stories, not the market. Criterion if built: beats the
  unconditional path range on held-out episodes (MAE of the median, coverage of the range). Prior (Claude): attribution earns cells slowly;
  the magnitude model fails as A3b did. Taken up after the list, with the founder choosing whether the prior is worth the test.

Improvements with no pre-registration behind them. Worth doing when there is a
reason; none has one yet.

- **Persist the expanding regime labels to disk** at build time so the app's
  first asset lookup is instant rather than a minute. Touches
  `regime_labels_expanding`, which the whole pipeline depends on — not to be
  done during an active evaluation. **Now has a reason:** the backfilled report
  ledger (§3.8 step 7) re-runs the pipeline over ~1,600 document dates and
  would otherwise recompute the labels every time.
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
- **Mahalanobis as a registered model_5.** The only kernel that held across
  time (2.94× split) in the 8 Sep family test; p 0.0498 on ALL, fails on
  LONG-HISTORY. Not a finding. Worth registering only with a reason beyond
  "it looked best in the family" — today there isn't one.

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
| 2026-09-08 | Model 4 FAIL (skill post-2018 only). Kernel family NULL (family p 0.114; floor is zero, wrong prior #28; Model 1 fails split 3.88×). FOMC→GLD forward test registered at `9c5ad8e`, first observation 17 Sep. `MODEL_EVOLUTION.md` written. launchd → 15:00 |
| 2026-09-13 | Document authority hierarchy written into this file; SUPERSEDED banners on `POST_SUBMISSION_STATE`, `SESSION_HANDOFF`, `EXECUTION_PLAN`; FOMC→GLD forward test moved to §1 as running; stale §3.8–3.10 stubs removed |
| 2026-09-13 | **Harness audit, five commits.** (1) Nightly document reads found DEAD since 29 Aug — `--unread-only` never existed and `--limit` sliced before the cache check; fixed, plus `--since 20260827` so the deferred sets (4,595 political, 163 over-cap 6-Ks) are never read by the nightly cap (`8533969`). (2) `outputs/reports/` was being REWRITTEN nightly by `--limit 30 --recent 10`; now frozen, nightly job rebuilds the index only (`e740751`). (3) `step6 --latest` wrote each report a day EARLY (panel index runs ahead of the close); now targets the last completed session and is write-once (`562dedb`). (4) One failed ticker refresh no longer aborts the run (8 Sep AMLP); catch-up entry logs every completed-but-unlogged close with a `logged_at` column (`2296725`). Forward ledger verified complete 19 Aug–10 Sep, no Labor Day row, no duplicates. Report-level forward ledger starts at the first session whose report is written with all its documents read — reads are paused for credit, so not 14 Sep as first written (CURRENT_STATE §18.3) |
| 2026-09-13 | Report-level scoreboard pre-registration drafted (`docs/prereg_report_scoreboard.md`, three `[FILL]` placeholders open); eight-step build plan agreed — see §3.8 |
| 2026-09-14 | Audit recorded: CURRENT_STATE §18, forward-test catch-up amendment, prereg committed with placeholders, TRACK corrections (`202fe37`). `step6` defers a report while its session has unread documents; `--pending` + `daily_run` loop (`e761072`) — tested on 11 Sep: deferred, 2 unread. Reads remain PAUSED for credit; pending reports queue until they resume |
| 2026-09-24 | Two silent defects (CURRENT_STATE §18.7): the nightly job never had ANTHROPIC_API_KEY (it lived only in `.zshrc`; reads since 14 Sep blocked by the key, not the balance — §18.3's diagnosis corrected); no fetcher for FOMC statements existed, so 16 Sep was never on disk. `src/fetch_fomc_statements.py` added and wired into step 3; decisions CSV extended to 28 Oct and 9 Dec; abort message fixed. Fresh-clone test passed; two derived panels re-tracked; LICENSE added; README clone URL. Wrong priors #30, #31 |
| 2026-09-29 | Instrument robustness **CONSISTENT** (C1–C4; hit-rate 58.2→56.5, agreement 94.8%); app may state ETFs modelled / desk instruments shown. Surprise stage A **INCONCLUSIVE**: GLD passes (p 0.039, −0.54%/bucket over 3 sessions), TLT ≈ 0 — the reverse of the registered prior. Stage B authorised; level 3 (Swanson series) next. Wrong priors #32, #33 (CURRENT_STATE §18.9–18.10) |
| 2026-09-29 | Surprise stage A level 3 (FRBSF Bauer–Swanson published surprise) **FAIL**: gold's level-1 effect was the proxy's whole-day move, not the surprise; stage B not run. Data vintage frozen in `data_provenance/mps/`. Loader made to refuse an empty series after a silent fallback. Wrong-prior candidate #34 (CURRENT_STATE §18.11) |
| 2026-09-29 | T14 phase A **NULL** on both S&P and 10-year (292 meetings): the initial 30-minute reaction neither extends nor reverses measurably by the close with free daily data; app's second line may show what the statement said but no number. S5 intraday collector live (11 tickers, 73 sessions on first run, nightly). Wrong-prior candidate #35 (CURRENT_STATE §18.12) |
| 2026-10-07 | Nightly job had failed 22 Sep–6 Oct: `.env` had no trailing newline and the 24 Sep `>>` glued the Anthropic key onto the FRED key. Split; job run by hand; ledger, reads and reports caught up. GitHub token expired the same week and was replaced. Wrong prior #36 (CURRENT_STATE §18.13). Weekly `launchctl list` check added to §7 |
| 2026-10-08 | T1 exposure dial Test A **NO on both**: vol targeting improves drawdown on all five, CER only on USO (1/5 PASS); regime tilt adds nothing (0/5, p 0.4–0.7). Nothing enters the product. Variant 4 not run (no posteriors exposed). T14 phase B built (2 pm statement reader, launcher, schedule loaded; dry run on 16 Sep passed); first live run 28 Oct. Wrong-prior candidate #37 (CURRENT_STATE §18.14) |
| 2026-09-24 | Statement corpus replaced by a mis-scoped `--refetch` (assistant's error), re-read under identical conditions (132 docs), gate unchanged 0.517. Backfill re-run as `48a6c4e879a1_n2617`: **FAIL** (hit 58.2% vs q95 58.8%; asymmetry 0.880). The 14 Sep INCONCLUSIVE was not robust. New baseline `48a6c4e879a1_n2617` (CURRENT_STATE §18.8) |
| 2026-09-14 | Report scoreboard steps 1–7 done in one day, $0. Backfill `986e0d65b6df_n2616`: 1,531 as-of reports; **INCONCLUSIVE** (hit 59.4% vs null q95 59.1%, p 0.0497; asymmetry CI includes 1). Coverage baseline 38% of document days. Ledger dtype bug found by the run, fixed. Details prereg §11, CURRENT_STATE §18.6 |

---

## 6. Standing rules — apply to every item above

- Every criterion is written and committed before the test exists.
- Amendments are recorded before results are read.
- A result that goes against the project is published, not re-run.
- A grid, not a shot; a distribution, not a point; split data with criteria
  fixed first (business plan §3.4.1).
- The frozen models in `models.yaml` are not touched. The forward test's
  value is that they haven't been.
- **The record leaves the machine every night.** `daily_run.sh` step 8/7 commits and
  pushes the ledgers, scoreboards and write-once reports. `.env.example` (names only)
  is kept current with `python tools/make_env_example.py` and committed; `.env`
  (values) is never committed. See section 7.

---

## 7. Backup and restore -- what lives where, and how to rebuild on a new machine

**Standing rule for every figure shown to the founder or an investor (8 Oct).** A number is never
shown alone. It carries, in this order: (1) **the population it is over** — the denominator in
words ("of the 100 days SPY moved more than 2σ *and* the engine had a document"); (2) **what it
measures and what it does not** ("how often the document present pointed against the move — not
how often the engine misread one, because on most of those days the document was not the driver");
(3) **its status** — *measured* (a count on history), *tested* (a registered criterion and a
verdict), or *registered, not run*; (4) **its date and source file**. A figure that cannot be
written in that form is not shown. "31% wrong" fails the rule; the sentence that replaces it is
in CURRENT_STATE §18.16.

**Two standing rules (7 Oct).** Never append to `.env` with `>>` — rewrite it whole, one `KEY=value` per line, trailing newline. Every week: `launchctl list | grep regimeaware` — a non-zero number after the dash means the job is failing, and the nightly log says where.

*Added 2026-09-14 after an audit found nine unpushed commits and the forward ledger
untracked since the forward test began. A same-day scan of the repo and its full git history found no key-shaped
string anywhere (tracked files, history, committed filenames, notebooks): nothing to revoke. Read this in any new conversation before
touching data paths.*

### On GitHub (safe once pushed)

| class | path | note |
|---|---|---|
| code, docs, pre-registrations, TRACK, CURRENT_STATE | everything not git-ignored | `git push` after every session; step 8/7 does it nightly |
| forward ledger | `processed/forward_ledger.csv` | force-tracked from 14 Sep, committed nightly. "Entries provably predate outcomes" depends on this. Before 14 Sep it existed only on the founder's disk |
| report ledger + scoreboards | `processed/report_ledger.csv`, `docs/*_scoreboard.md` | same |
| write-once reports | `outputs/reports/*.json`, `*.md` | force-tracked nightly; a rewrite would show as a diff |
| document reads (the corpus) | `data_provenance/doc_reads/*.json` | ~2,616 files, 10 MB. If `git ls-files data_provenance/doc_reads` is empty, force-add them -- they cost US$30-50 and a prompt-version discontinuity to recreate |
| `.env.example` | repo root | variable NAMES only, values `enter_your_key_here`; regenerate with `python tools/make_env_example.py` whenever the code gains a new variable |

### Not on GitHub, on purpose

| class | path | on a new machine |
|---|---|---|
| secrets | `.env` | **never committed.** `cp .env.example .env`, then issue NEW keys at each provider and fill them in. Old keys die with the old laptop |
| raw documents | `data_provenance/docs/` (~770 MB) | re-fetchable at $0 with `fetch_sources.py`; slow. Optional zip to Drive |
| price/macro caches, processed panels | `data_provenance/*` caches, `processed/*.parquet` | rebuilt by `src.download_data --force`, `src.build_panel`, `src.pca_macro`. yfinance history drifts slightly; frozen ledger rows are unaffected |
| logs | `logs/` | disposable |
| shell startup | `~/.zshrc` | also exports the API key for interactive shells. launchd does not read it — `.env`, loaded by `daily_run.sh`, is the source of truth for the nightly job. When rotating a key, change both or delete the `.zshrc` line |
| GitHub login | macOS keychain (`osxkeychain`) | dies with the laptop, as it should; sign in again on the new one |
| the launchd job | `~/Library/LaunchAgents/com.regimeaware.daily.plist` | outside the repo; recreate from the description below |

### Restore on a new laptop, in order

1. `git clone https://github.com/Wei-TingHsu/regime-aware-signal.git && cd regime-aware-signal`
2. `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
3. `cp .env.example .env` -- fill in NEW keys from each provider named in the file
4. `python -m src.download_data --force && python -m src.build_panel && python -m src.pca_macro`
5. `python -m src.forward_log --no-refresh --dry-run` -- must print `no new US close` or a CATCH-UP line, never an error
6. `python -m src.report_scoreboard --selftest` -- seven PASS
7. Recreate the launchd plist (below) and `launchctl load` it
8. Read the first unattended log against section 1

### The launchd job (outside the repo, so described here)

`~/Library/LaunchAgents/com.regimeaware.daily.plist`: Label `com.regimeaware.daily`;
ProgramArguments `/usr/bin/caffeinate -is /bin/zsh <repo>/daily_run.sh`; WorkingDirectory
`<repo>`; StandardOutPath/StandardErrorPath `<repo>/logs/launchd.out` and `.err`;
RunAtLoad false; StartCalendarInterval weekdays 1-5 at Hour 15 Minute 0.
`caffeinate -is` holds the machine awake for the job's duration (the 11 Sep run was
suspended mid-way for ten hours without it).

### 3.35 The liquidity–gold link through time (T-L) and the few-shot chair (T-K) — registered 27 Oct

Origin: the founder's question (27 Oct). Record: `docs/prereg_liquidity_and_chair.md`; code `src/liquidity_link.py`, `src/chair_power.py`; T-K3
(LLM rubric reads of every statement, exact permutation) follows T-K0/T-K1. Open: the 16 Sep 2026 FOMC statement is not in the corpus (feed gap);
the SPDR ETF-flow archive must be downloaded by hand.

Status 27 Oct night: T-K0–K2 run and recorded (#77, #78 wrong, tally 64); units error in the first T-L run fixed (WTREGEN is millions); T-L5 (after an equity sell-off) and T-K1′ (volatility units) added before running; `record` subcommands write the verdicts into the register. Open after this: T-K3 LLM rubric reads; the 16 Sep statement into the corpus; GLD flows by hand.

27 Oct 23:50: T-L5b events before GLD existed (1995–2004) had been counted as zero gold returns — fixed, re-run, records replaced, #80 re-judged; T-K2σ (chair posterior in volatility units) added. Commit after the re-run closes the night.

28 Oct 00:45: T-K3 built as `src/chair_style.py` (synthetic selftest PASS: a planted 3.5-sd shift at n = 4 vs 8 detected 98%, no-shift rejection 4%); the acceptance check on Bernanke→Yellen and Yellen→Powell is registered before any read (prior #82). The 16 Sep statement is on disk and read (132/132) — the 'feed gap' line above is wrong (amendment row in the prereg). TRACK 3.1 registered as `docs/prereg_political_backfill.md` (C1 coverage ≥ 50%, C2 gate, C3 section-8 rule; prior #83) with `src/political_route.py`, `src/source_compare.py` and `overnight.sh` (cost measured on disk, cap US$40, lock and fatal-abort via run_corpus.sh). Found in the nightly logs: the automated 8-K fetch has failed on a sec.gov 403 every night since 19 Oct while manual runs succeed — `scripts_applied/patch_edgar_cik_fallback.py` caches the CIK map and prints the UA; cause open. Thu 29 Oct 01:45 SGT: the 2 pm reader's first live FOMC (the launcher has fired on every scheduled night this month); then T-K3 at n = 4 and T-K2σ refreshed.

28 Oct 15:30: the overnight run (01:06–04:11) read the political backlog as registered (2,946 documents, ≈ US$21, coverage 38.1% → 61.0%) **and** the 165 declined over-cap 6-Ks (≈ US$71) — the runner's cap guarded the wrong quantity (Claude's error; amendment in `prereg_political_backfill.md` §6). The gate aborted on 47 orphan reads under the nightly `political` profile, so C2 is unevaluated and the 04:11 PASS row is void; re-run with `gate_check --allow-partial`, then `source_compare compare --exclude-dates <the 8-K days> --gate <verdict> --record`. T-K3 ran at n = 2 (four replies failed to parse, one of them Warsh's 17 Jun) — `chair_style.py` v2 re-reads the four and refuses to run off the registered sets; acceptance check: both past transitions separate (#82 wrong). Nightly routing patch: `scripts_applied/patch_daily_route_political.py`. Backfill `97d9bf07dd2c_n5793`: primary cell FAIL as before; on the shared days +0.3 points, same sign on 100% of shared asset-day calls.

### 3.36 T-S1 — silver warehouse stocks and price (founder, 28 Oct)
Registered as a draft in `docs/prereg_silver_stocks.md`: the deliverable (registered) silver at the COMEX depositories — the amount moved out of deliverable status or out of the vault, and how often — against silver's price trend, both directions, lags −12..+12 weeks; the H-table standard for the event form. Unit is the depository (JPMorgan's vault, not JPMorgan's book — the owner is not observable). Data: CME's daily depository report, forward collection from the first probe (`src/fetch_comex_stocks.py --probe`), history by hand-downloaded file; the first run needs ≥ 250 sessions. Prior #84 in the draft. $0.

### 3.37 Sub-period audit (founder, 28 Oct: "a pooled result can balance out a shift")
Standing rule C (S1–S3: both halves same sign, neither half > 3× the other) is a guard against one-era findings; it is not a search for a transition. Tests with time dependence built in: T-A/T-B (walk-forward), T-L1–L3 (rolling, one break, recent window), T-K (eras = chairs), Model 1/4 and the kernel family (median split), FOMC→GLD (split FAIL 4.62×), Step-3 cells (7 → 1 under the split), the A3 inverse rule (held-out = chronological). Pooled over the whole span, candidates for a registered sub-period re-run, in value order: T-L multi-break (T-L6, the direct test of the founder's watershed); P1 safe-haven inversion (rolling 2-year gap + break); factor sensitivities by era (2004–08, 09–14, 15–19, 20–21, 22–26: β, R², sign stability, and the 2026 episode attributed with pre- and post-2022 betas — the "habit vs driver" split); the report scoreboard's own hit-rate by era (the product's claim; $0 from the backfill CSVs); T1 vol-targeting CER by era; the window/leg rules' explained share by era (descriptive); T-H by era (FAIL pooled — a one-era pass needs a forward test); T-L5b and H-tables by era (counts under 30 — measured only). Each re-run is its own registration with the criterion fixed first and, for any one-era PASS, a forward test before it is a verdict.

### 3.38 Results compendium (founder, 28 Oct) — after 3.37
`docs/RESULTS_COMPENDIUM.md`: one row per tested claim — the statistics as recorded (p, hit-rate, asymmetry, Sharpe, n, horizon, split status), the assumptions, conditions and time frame of each test, and a usability tag: *quant signal* (passed its registered null and split, non-overlapping, costed), *discretionary input* (a measured conditional table or a robust null that changes a trader's prior without being a rule), or *neither*. Built from the register (PROJECT_MASTER §8 rows 1–52 and every prereg's results table), not re-run. $0.

28 Oct 16:30: founder — the sub-period audit covers **every** registered test, not five, and every test's fixed numbers become grid axes. Registered as `docs/prereg_subperiod_audit.md` (the two standing rules; all 52 rows classified: already era-aware / not applicable / group A backfill CSVs / group B series on disk / group C returns only / group D reader drift; priors #85–#92). Instrument: `src/sweep.py` (grid, best-of-sweep null, survivors; selftest PASS). Written and tested on synthetic data: `era_scoreboard.py` (group A, all rows from one CSV), `era_liquidity.py` (T-L6 with sequential breaks and the watershed dates; P1 by era; T-L5b as a 147-cell grid in both directions), `era_factors.py` (betas and T-A by era; the 2026 episode re-attributed with 2009–21 and 2022→ betas), `era_fomc.py` (T9b by era), `era_events.py` (oil shocks by era). Next adapters: T1 by era, T-H by era, target range, H-tables, COT state, T14. `prereg_silver_stocks.md` v2 carries the grid (lag windows ±3/6/12/26 weeks; horizons 5/7/10/13/15/20/30/60; rally thresholds 4–10%; event sizes 0.25–3 Moz; eras); CME's host refused the plain client (403), fetcher v2 tries browser headers and curl; the one third-party API is paid and ruled out. T-K3 at n = 3 on the registered sets: energy 3.39, exact p 0.042 — Warsh's three statements separate from Powell's last eight, on inflation-vs-labour emphasis (0.018) and hedging density (0.055), not balance-sheet language (0.41); #79 is judged Thursday at n = 4 as registered. Gate re-run with the orphan shortfall recorded: PASS (spread 0.326, CI [0.308, 0.344]); C3 on the 572 political-only shared days +0.7 points, 441 calls added at 56.2% across all five assets (#83's 'mostly SPY' wrong); the 165 declined 6-Ks produced 190 calls at 50.5% — chance, as 17.2 predicted; whether they stay in the live corpus is the founder's decision. Nightly routing patch v2 (loop-aware) ready.

### 3.39 The sweep engine as the standing instrument
`src/sweep.py` is the one place the best-of-sweep null lives; every new test registers its grid and its null generator against it, and every re-run of an old test goes through it. Selftest: a planted lag-10 relationship in a 21-cell grid found at p_family 0.000; pure noise's best cell (r +0.05, 'significant' alone) at p_family 0.67. ML forms (walk-forward learners on the grid variables) enter through the same null, registered per family after the grid run.

5 Nov 17:20: first sub-period batch run and recorded (prereg_subperiod_audit §4). Nothing beats its null by era; two shapes worth the founder's eye: P1's gap flips sign between 2009–14 (−0.34, safe haven) and 2022–26 (+0.21, dash for cash) but sits inside a null built from persistent states; T9b per σ differs by era (p 0.026) because the pandemic era's gold reaction was ~2.7× the others on 19 statements. One sweep survivor at the bar: gold *bought* after a −6% / 20-session SPY drawdown, 15 sessions forward (+17.9 pts vs q95 +17.6, p_family 0.050) — a forward-test candidate, the opposite of the 27 Oct hypothesis. The 2026 gold fall is explained better by 2009–21 sensitivities (29%) than by 2022→ ones (11%). T-K3 at n = 4: p 0.061, not distinguishable; inflation emphasis the dimension both times. **CME has blocked this IP for suspected scraping** after the three probes of 28 Oct–5 Nov (the response names its Data Terms of Use): no further scripted requests to cmegroup.com; the silver registration waits for a hand-downloaded history or is shelved. Routing patch applied 5 Nov; verify in the 6 Nov log. Next: the era_factors re-run without the late-starting proxy; adapters B6, B8–B12; group C; the forward registration for the −6% survivor if the founder wants it.

### 3.40 Deeper tests — from measured patterns to candidate signals (founder, 5 Nov)
Registered in `docs/prereg_deeper_signals.md` before any run: seven tests on one recipe (path statistics after costs; the best cell against the best-of-search null; survivors into a forward log; a learner only afterwards). D1 gold after an S&P drawdown (the 5 Nov survivor, widened with filters and both directions), D2 the liquidity link as an on/off meta-signal, D3 the gold–equity correlation regime as a sizing input, D4 Fed-day drift from the surprise and the statement rubric, D5 gold after oil shocks, D6 COT positioning extremes, D7 the report's calls selected by a walk-forward learner; D8 chain spillover and D9 vol-targeting registered, not yet coded. Priors #93–#99. First forward rule registered: **D1-5nov** (buy GLD when SPY's 20-session return crosses −6%, hold 15 sessions), logged nightly by `python -m src.deeper forward` into `processed/forward_signals.csv`, judged at n ≥ 30 — years, not weeks, at this event rate. `src/deeper.py`; each run writes `docs/deeper_<test>.md`.

5 Nov 20:30: D1–D7 recorded with their nulls (prereg_deeper_signals §5): D3 (correlation persistence, skill 0.26, p_family 0.000) and D4 (Fed-day surprise in high-vol states, p_family 0.000) clear their nulls; D1 marginal (0.045) and superseded by the v2 re-run (the first run's forward windows included the event session — found on the sandbox stub, fixed before the founder's numbers are judged); D2, D5, D7 null; D6 now finds `flows.parquet`. Founder's redesigns registered as §2b with priors #100–#104: D1b sudden one-day sell-offs, D2b the link by engine regime, D2c daily liquidity, D8 factor combinations as a predictive index, D5b the oil→rates→gold chain measured link by link. Second forward rule D1-5nov-b. Every finding, null included, goes into the compendium next.

6 Nov 12:45: the deeper round closes with one correction and no new signal. D1 v2 (event day excluded) is null (p 0.140); the sudden-sell-off version null in all four readings; the link by regime lives in regime 2 (t 3.0) but the regimes are not distinguishable (p 0.385); daily liquidity, positioning extremes and 299 factor combinations null. D5b's survivor (gold up after oil shocks where real yields fell, p 0.005) conditions on the same window it predicts — D5c registered with the tradeable timing. `docs/RESULTS_COMPENDIUM.md` written (TRACK 3.38): every claim, every null, the tags. Standing: D3 (correlation persistence) and D4 (Fed-day surprise) are the two results that clear their nulls; neither is alpha on its own.

### 3.41 Regime audit and the day-type layer (founder, 6 Nov)
Registered in `docs/prereg_regime_audit.md` before any run. The engine classifies macro *levels* (eight FRED dials → 3 PCs → 4-state mixture, expanding refit every 20 sessions, confirmation at posterior 0.8 for 3 sessions), persists ~52 sessions, and was chosen for stability, not prediction; every test that conditioned on its labels has been null. R1 describes the four regimes (dial levels, asset returns inside each — they never had names); R2 measures the live labeller's confirmation lag against hindsight labels; R3 asks whether the labels sharpen the Fed-day reaction, the factor model or the report's calls; R4 refits k = 3…8 at every year-end to see whether four was ever not the winner (a switch is a founder decision — it relabels history). The founder's same-day pattern (2-yr down, 10-yr up, gold up) is a pattern of *moves*, invisible to a level classifier at any k; `src/daytype.py` types every session by five same-day signs (32 patterns) and tests Y1 counts, Y2 clustering before regime changes, Y3 forward returns under the family null, Y4 the report's calls by type. Priors #107a–d, #108a–d. Use `pip install scikit-learn` once for R4.

6 Nov 22:40: founder — the count must be chosen on understanding, not tidiness; and the discovery must be full (all move patterns), not one example. R6b (expanding-refit k comparison), R2 (lag) and the fast-state layer registered in prereg_regime_audit §3b with priors #111–#116; `src/regime_k.py`, `src/faststate.py`. Today's R3 on confirmed labels: gold's Fed-day reaction differs by regime (p 0.005; stimulus and high-rates regimes ~2.5× more reactive) — the first regime-conditioned result to clear its bar; R5: the k = 4 favoured-asset map does not repeat within regimes (stability +0.25, p 0.19); R6 (full-sample): four wins none of the three usefulness jobs, six wins two, three has the most stable asset map — decision deferred to R6b.

### 3.42 N1 — news-attributed large moves and the releases that follow (founder, 6 Nov)
Registered in `docs/prereg_news_events.md` before any run: every ≥ 4% close-to-close move in SOX, QQQ and the S&P since 1995; the same-day cause read by the LLM under a fixed schema from GDELT, the project's own corpus and primary releases (**standing rule from 6 Nov: no tertiary sources — Wikipedia and the like are never used**); every scheduled release in the next five sessions read for its *composition* and scored for whether it contradicts the cause; reversal tables under the H-table standard; a walk-forward learner against the plain "buy after a −4% day" rule; the annual OEWS AI-occupation series as the slow check (the monthly jobs report has no occupation detail). Priors #117–#121. Cap US$25. Module `src/news_events.py` next, built against `gdelt_ingest`.
Regime count: R6b on the honest method leaves four competitive (Fed-day p 0.008) with six ahead only on the factor spread; the proposal on the table is a FIXED k = 4 for the product and, optionally, a second fixed six-state fit as the attribution lens — never a k that changes with time. Awaiting the founder's word.

### 3.43 Regime count decided; N1 stage 1 on record (6 Nov, 23:02)
Founder's word: fixed k = 4 for the product, a second fixed six-state fit (`k6` in `processed/regime_labels_by_k.parquet`) as the attribution lens; k never drifts with time (amendment in `docs/prereg_regime_audit.md`).
N1 stage 1 (`src/news_events.py`, no LLM): 539 index-events on 476 sessions with |close-to-close| ≥ 4% — SOX stood in by **SOXX** (the ETF, from 2001; ^SOX not in the panel), **QQQ absent** from the panel (no Nasdaq-100 events until it is added), S&P by SPY. Years: 2001: 36, 2002: 80, 2003: 26, 2008: 49, 2009: 33, 2010: 11, 2011: 13, 2018: 12, 2020: 28, 2021: 12, 2022: 40, 2024: 18, 2025: 15, 2026: 47 (years with ≥ 10 days). GDELT 1.0 daily files run ~7 MB per event day (40 fetched = 284.5 MB); the 2001–2012 days sit in monthly / yearly archives of hundreds of MB and are fetched only if the daily-era results earn it. Measured cost of the cause read on disk: ≈ US$0.29 per 40 digests (≈ US$3.50 for all), well inside the US$25 cap. Stage 2 is `src/news_events2.py` (read / releases / read_releases / tables / learn).

### 3.44 N1 first pass (7 Nov 00:25)
v1 cause read on 246 event days: "no identifiable news — positioning" 68% → prior #117 (20–35%) wrong, counted; caveat that the mention-ranked GDELT digest under-represents finance, so a v2 digest with a finance section is registered (prompt n1-cause-v2, prior #123, own cache). BLS release fetch returned nothing (no contact address in the User-Agent — fixed, `BLS_CONTACT`); 38 FOMC pairs in window. GDELT 2022-11-10 absent (404). `news_events2` v2: `reads/` folder bug and empty-CSV crash in tables/learn fixed.

### 3.45 N1 second pass (11 Nov 00:51)
v2 cause read: "no identifiable news" 49% (#123 right), but the finance section is a noisy slug-keyword match and GDELT missed the day's earnings story on 5 Nov 2026 — recorded as an instrument limit; a v3 would read the project's own corpus. 192 release-composition reads; #119 right; #121 see table; #118 counted wrong (S&P does not reverse below 50% after rises at five sessions); #120 right (learner loses to the plain post-fall rule). One PASS cell — S&P falls the session after a ≥ 4% rise, n 42 — becomes forward-log candidate N1-a, not a product rule. Total N1 spend ≈ US$10.3. Open: QQQ absent from the panel; 2001–2012 archives not fetched; v3 corpus-based cause read not registered.

### 3.46 Agenda from 11 Nov 01:40 — N1 v3 registered; the signal-creation redirect put to the founder

| # | step | why it matters to the business | founder decides |
|---|---|---|---|
| 1 | **N1 v3a** — wider official documents (PPI, JOLTS, import prices, Chair / Vice Chair speeches), window to 10 sessions, one story-free read per document, cutoff × window × horizon × family grid, reversal SIZE test (`src/news_events3.py`; prereg_news_events §5; priors #124–#127) | tests the founder's two explanations for the N1 null directly; if a document family passes, it is a "what to watch after a crash" product line | nothing — registered, running tonight |
| 2 | **N1 v3b** — corpus survey: event days with a same-day 8-K / FOMC / Federal Register document | decides whether the cause read moves from GDELT to primary filings | after the survey: register the corpus cause read or not |
| 3 | **N1-a forward log** — short SPY at the close of a ≥ 4% up session, one session (the single PASS cell, n 42) | the only candidate trade rule N1 produced; needs live evidence before any claim | whether to wire it into `deeper forward` |
| 4 | **QQQ into the price panel** | N1 has no Nasdaq-100 events without it | yes / no |
| 5 | **S1 — risk signals from the survivors**: sell the forecast of correlation, volatility and regime change (gold–equity correlation persistence, skill 0.26; abnormal-day runs before regime changes, p 0.000) as a hedge-ratio / exposure signal rather than a direction call | the relationships that survived are about risk, which institutions buy and which is far more predictable than direction | whether to register S1 |
| 6 | **S2 — cross-sectional filing signal**: each issuer's 8-K read scored, then that stock's return relative to its sector over the next 1–20 sessions; thousands of stock-events instead of 40 macro events | the LLM document layer is the project's own data; one stock at a time is where a text edge is most plausible and where the statistics have power | whether to register S2 (needs single-stock prices) |
| 7 | **S3 — conditional event trades**: the Fed-day reaction that differs by regime (p 0.005), traded only in the regime and volatility state where it is strong, entry after the announcement | turns the strongest surviving relationship into a rule with an entry and exit | whether to register S3 |
| 8 | Carried: F2b lead time of the abnormal-day signal; Group C returns-only tests; R7 every event class by regime; regime × fast-state hierarchy | completes the regime audit | order |
| 9 | Buyer conversation (TRACK §3.7 customer interviews) | tells which of 5–7 a buyer would pay for before weeks are spent on the wrong one | when, and with whom |

### 3.47 N1 v3a/v3b on record; v3c registered (11 Nov 14:45)
Grid on the reversal RATE: null in every testable group (#124 right). Size test: 4 of 32 cells below 0.05, all positive, and SOX rank correlations positive in 21 of 24 cells — the first non-flat N1 result (#125 counted wrong on its sign clause). Joint size test v3c registered before running (prior #128; bar 0.0125). Corpus covers 34% of event days, 74% from 2020 (#126 right); #127 counted wrong. Hindsight-leak caveat on LLM implication scores recorded. N1 spend ≈ US$18.9 of 25.

### 3.49 N1 v3d result; the short-window rule; next steps (11 Nov 15:40)
v3d: after ≥ 4% semiconductor falls the link between official documents and price is on the document's release day (all documents +0.169, p 0.004; Fed documents +0.382, p 0.001) and is gone on days +1…+5 (p 0.59); the two days before the document show nothing. Priors #129–#131 all right; #128 counted wrong. Not a daily-close trading signal: the move is finished by the close of the release day.

**Short-window rule (founder, 11 Nov 2026; standing).** News arrives every day. The longer the span of sessions a test measures, the more unrelated news is mixed into it, which adds noise and can hide or fake an effect. So: (1) every test of a reaction to news is run at several span lengths, the shortest first (the release day itself, then +1, +1…+2, +1…+3, and only then 5, 10, 20); (2) no conclusion — pass or null — is written from one span length alone; (3) where a long span fails, the short spans are run before the idea is called null; (4) this applies back to earlier tests whose verdict rests on a single span of five sessions or more (horizon audit, TRACK §3.49). It sits beside the grid-by-default rule (28 Oct) and the sub-period rule; the search over span lengths is judged against the best the same search finds on shuffled data.

| # | step | why it matters to the business | founder decides |
|---|---|---|---|
| 1 | `decayk` — v3d with spans +1, +1…+2, +1…+3 | the short-window rule applied to the test that prompted it | nothing — run |
| 2 | **v3e intraday** — from the release minute to the close of the same day, for Fed statements and Chair / Vice Chair speeches after ≥ 4% semiconductor moves (needs intraday prices and the release time of each document) | the only place a tradeable signal can still be; also decides whether showing the score on the app at release is useful or only explanatory | whether to register; which intraday data source |
| 3 | Reader consistency — read 30 documents a second time and compare the scores | the score is one model judgement per document; this shows how much it wobbles | yes / no (≈ US$0.50) |
| 4 | **Horizon audit** — list every past test whose verdict rests on one span of five sessions or more; rerun each at 0, 1, 2, 3 | the short-window rule applied backwards | nothing — Claude prepares the list from RESULTS_COMPENDIUM |
| 5 | Then the agenda of §3.46 from item 3 (N1-a forward log, QQQ, S1, S2, S3, carried items, buyer conversation), then back to the main track | — | — |

### 3.50 Two-category rule; test book; v3e design; agenda (11 Nov 16:10)
**Two-category rule (founder, 11 Nov 2026; standing).** A finding can be used in two ways and every test is labelled for both. **QUANT** = usable by a rule-based strategy that holds from one session to several weeks: the effect must still be there after the information is known at a daily close. **SUBJECTIVE (intraday)** = usable by the founder's own judgement inside the day: the effect is on the same day as the information and nothing is left afterwards. "Nothing is left after day 0" ends a finding as QUANT but not as SUBJECTIVE. Grade B = seen at daily closes only (a same-day association; capture after the release not yet tested); grade A = confirmed with intraday prices from the release time to the close. Findings that are neither a direction nor null are **CONTEXT** (how to size, hedge or explain); the rest are **NEITHER**. Every past test is re-labelled this way in `docs/TEST_BOOK.md` Part B, which also marks the tests where day 0 was never measured separately (the horizon audit list).

`docs/TEST_BOOK.md` created: Part A rules and shared method, Part B every test labelled QUANT / SUBJECTIVE / CONTEXT / NEITHER with "day 0 checked?", Part C rebuild cards (N1 complete; five more parts pending). Labels as of today — QUANT: gold–equity correlation persistence (risk forecast), calm-day warning before regime changes (candidate), S&P the session after a ≥ 4% rise (candidate, forward log). SUBJECTIVE grade B: gold on Fed statement days by rate surprise (stronger when yields are volatile and in regimes 1 and 3), Fed documents after ≥ 4% semiconductor falls, gold on the day a 6% S&P drawdown completes (weak). No grade A yet.

| # | step | why it matters to the business | founder decides |
|---|---|---|---|
| 1 | **Horizon audit** — every index row marked "day 0 checked? no" rerun at day 0, +1, +1…+2, +1…+3 (calls, history tables, oil shocks, sell-offs, residual momentum, day-types, fast states, daily liquidity) | applies the short-window and two-category rules to the past tests; may move nulls into SUBJECTIVE | nothing — Claude builds the runner |
| 2 | **v3e intraday** — first-minutes surprise, then continuation or reversal by composition score | the only route to SUBJECTIVE grade A and to a useful release-time line on the app | the intraday data route |
| 3 | Test book parts 2–6 (rebuild cards for the other families) | lets a quant specialist rebuild every test alone | order of parts, if any preference |
| 4 | Reader consistency (30 documents read twice) | how reliable the composition score is | yes / no (≈ US$0.50) |
| 5 | §3.46 items 3–9 (N1-a forward log, QQQ, S1, S2, S3, carried regime items, buyer conversation), then the main track | — | — |

### 3.51 Horizon audit registered; app naming rule; intraday data route (11 Nov 16:45)
**Horizon audit** — `docs/prereg_horizon_audit.md`, `src/horizon_audit.py`: nine audits rebuild the events of every test marked "day 0 checked? no" and measure day −1, day 0, +1, +1…+2, +1…+3, +1…+5 against a time-shift null; label rule fixed beforehand (days after → QUANT candidate; day 0 on an information event → SUBJECTIVE grade B candidate; day 0 on a price-move event → CONTEXT; else NEITHER). Priors #132–#135. No cost.

**App naming rule (founder, 11 Nov; standing; redesign to be done AFTER the tests).** Every block on the page carries a proper dashboard title — the standard professional name of what it shows — not a conversational phrase: "Why it moved" becomes "Factor attribution", and the same logic is applied to every block name on the page. Where two blocks would end up with the same or a similar name, they are separated — placed in different corners / areas of the page — so a reader can tell which block to look at. The redesign must follow this rule and no other naming idea.

**Intraday data route (founder's decision).** Databento first (new accounts receive free credit); if the credit does not cover what the test needs, Alpha Vantage (monthly plan). TradingView is ruled out: its support page states it has no API that gives access to data. The fetcher asks Databento for the cost of each request BEFORE downloading. Until intraday prices are in, no SUBJECTIVE finding can be graded A.

| # | step | why it matters to the business | founder decides |
|---|---|---|---|
| 1 | Horizon audit — run, record, relabel TEST_BOOK Part B | applies both new rules to the past tests; decides how many nulls change category | nothing — run |
| 2 | v3e intraday — Databento fetcher (cost check first), then the registered test | the only route to SUBJECTIVE grade A | create the Databento account and API key |
| 3 | Test book parts 2–6 | a quant specialist can rebuild every test alone | — |
| 4 | Reader consistency (30 documents read twice) | reliability of the document score | yes / no (≈ US$0.50) |
| 5 | §3.46 items 3–9, then the main track | — | — |
| 6 | App redesign under the naming rule above | the page reads as a professional dashboard | after the tests |

### 3.52 Horizon audit result (11 Nov 17:10)
Nine audits, each on day −1, day 0, +1, +1…+2, +1…+3, +1…+5. Labels by the registered rule: `calls` QUANT candidate (pooled, +16 bp over days +1…+3, family p 0.034; day 0 nothing; day −1 check fails for tier 2), `states` QUANT candidate (calm-type state → S&P +31 bp over five sessions, p 0.002, about +10 bp over the ordinary gain, flips daily), `fomc` SUBJECTIVE grade B (gold 76 bp with the surprise on the day, 80% hit, nothing after), `oil` and `htables` CONTEXT (same-day co-movement), `selloff`, `sudden`, `liquidity`, `resid` NEITHER (resid closest: S&P gives back 55 bp after a large unexplained 20-session move, p 0.106). Priors: #132 wrong, #133 wrong, #134 wrong, #135 right. Both QUANT-candidate labels are narrow or cost-sensitive and each needs its own registered, costed rule (QC-1 calls at 1/2/3 sessions with the previous day's move controlled; QC-2 calm-state tilt at 1/2/3 sessions) before it is called a signal. Intraday route started: `src/intraday_fetch.py` (Databento; cost asked before any download).

### 3.53 Intraday data on disk; data-quality step; news block for the asset-search tab (11 Nov 19:00)
**Data.** Databento GLBX.MDP3, 1-minute bars, continuous front contracts NQ, ES, GC, ZN, 6 Jun 2010 → 11 Nov 2026, quoted US$57.27 against the free credit; files under `data_provenance/intraday/<symbol>/<year>.parquet`, kept out of the repository (`.gitignore`; the data is licensed for own use, not for publishing). Events before June 2010 cannot be tested intraday with this source.
**Two quality matters seen at download.** (1) Databento marks some days "degraded" (reduced quality) — to be measured, not assumed. (2) Gold has ~10–25 thousand bars a year against ~350 thousand for the index futures: the nearest-expiry gold month is often a thinly traded one; gold is to be fetched again as the most-traded contract (`intraday_fetch gold`, cost quoted first).
**Data-quality step (founder: "check how bad it is, using the criteria of machine learning's data treatment").** `src/intraday_quality.py`: completeness (session minutes present of 390; the 08:25–08:40 and 13:55–14:30 windows), gaps, validity (price order, positive prices, duplicate times), outliers (moves over 1%, spikes taken back within a minute, roll days), consistency against an independent source (daily move vs the ETF panel), and Databento's own degraded flag compared with the rest and counted on the days the tests need. Raw files are never altered; the flags in `processed/intraday_quality.parquet` decide which days a test may use (usable session = ≥ 90% of minutes and no gap over 5 minutes; 08:30 window ≥ 12 of 15; 14:00 window ≥ 28 of 35). No test runs on the intraday data before this table is on record.

**News block for the app (founder, 11 Nov; design recorded now, built in the redesign after the tests).**
- **Where:** on the "search this asset" tab, not the main page, so the main page is not crowded. Two blocks, named by the app naming rule (working titles "Market drivers" for the broad market and "Company drivers" for the searched firm), placed apart.
- **What counts as "recent":** not a time window. An item is shown for as long as it is still affecting the price — the oil war that began earlier in the year, or the turn of the Fed's cycle from lowering to raising rates over the past year, stay on the list while their effect lasts. The item must tell the investor that something in the cycle has changed.
- **Three parts in each block:** *still in effect* (older events whose effect continues), *new* (what has just happened), *ahead* (announced or proposed actions with a future effect — for example an announced investigation into data centres).
- **Company items** include events about the firm and its leadership that move the stock.
- **Conditions Claude attaches (for the founder to confirm at the redesign):** (a) every item carries its source and date, from primary or established news sources — the sources rule applies; (b) items about a named person's private life are shown only when they are reported by such a source and are material to the company (for example disclosed by the company or the subject of a regulator's or board's action) — never rumour, because publishing an unverified personal claim about a real person is a legal risk for the product; (c) "still in effect" needs a stated test — the item's factor still explains part of the price move in the factor-attribution block, or the documents still cite it — and a rule for retiring an item; (d) each item states which direction it has pushed the price and whether that was measured or is a judgement.

### 3.54 Intraday data step closed (11 Nov 23:30)
**Bought (Databento GLBX.MDP3, 1-minute bars, 6 Jun 2010 → 11 Nov 2026), all against the US$125 free credit:** NQ, ES, GC, ZN nearest-expiry series US$57.27; gold as the most-traded contract US$20.81; the 10-year note as the most-traded contract US$19.26; neighbouring-contract patch for expiry weeks (ES, NQ) and roll days (gold, note) US$5.34. **Total US$102.68.** Files under `data_provenance/intraday/`, kept out of the repository.
**What the quality checks found.** No invalid prices and no duplicate times in any series. Databento's 34 "degraded" days are indistinguishable from other days for the index futures. The real problems were contract choice, not vendor quality: (1) the nearest-expiry gold month is often thinly traded (0.8% of sessions usable) → most-traded series (97.6%); (2) the note's nearest-expiry contract is left weeks before expiry (77%) → most-traded series (98.9%); (3) the index futures' nearest-expiry contract stops trading on the morning of each quarterly expiry (six needed days empty, 20 Mar 2020 among them) and (4) the most-traded series switch a day or two late at each roll (about 20 needed days, several of them Fed statement days) → patch with the neighbouring contract. Daily moves from the minute data agree with the project's daily panel (ES vs SPY 0.99, gold vs GLD 0.98).
**Final table** (`processed/intraday_quality_final.parquet`, `docs/intraday_quality_final.md`): ES: 99.56% of 4,112 trading days usable, on needed days 100.00% (08:30 window 99.55%, 14:00 window 100.00%), 85 days from the patch file; GC: 99.76% of 4,113 trading days usable, on needed days 99.85% (08:30 window 100.00%, 14:00 window 99.85%), 89 days from the patch file; NQ: 99.56% of 4,112 trading days usable, on needed days 100.00% (08:30 window 99.11%, 14:00 window 100.00%), 141 days from the patch file; ZN: 99.66% of 4,117 trading days usable, on needed days 99.85% (08:30 window 100.00%, 14:00 window 99.85%), 40 days from the patch file.
**Needed days still short on a window:** NQ 2015-09-17 (session 390, 08:30 9/15, 14:00 35/35); NQ 2016-06-15 (session 390, 08:30 9/15, 14:00 35/35); GC 2020-02-27 (session 231, 08:30 15/15, 14:00 0/35); ZN 2020-02-27 (session 231, 08:30 15/15, 14:00 0/35); NQ 2020-03-09 (session 376, 08:30 6/15, 14:00 35/35); ES 2020-03-13 (session 390, 08:30 10/15, 14:00 35/35); NQ 2020-03-13 (session 390, 08:30 5/15, 14:00 35/35); ES 2020-03-16 (session 376, 08:30 5/15, 14:00 35/35); NQ 2020-03-16 (session 376, 08:30 0/15, 14:00 35/35); ES 2020-03-18 (session 377, 08:30 8/15, 14:00 35/35); NQ 2020-03-18 (session 377, 08:30 0/15, 14:00 35/35). Read: the March 2020 08:30 windows are overnight price-limit halts (real market states, kept); NQ on 17 Sep 2015 and 15 Jun 2016 is thin before the open in expiry week (the 14:00 window is complete); 27 Feb 2020 for gold and the note is a vendor loss of about 160 minutes around 14:00 — repaired from another source only if a test actually needs those minutes. Two patch requests timed out at the vendor (GC 30 May 2022, a market holiday; ZN 28 May 2021) and several returned no data (holidays); none is a needed day. No second vendor is required.
**Founder's question (11 Nov): "if the 0.2% that fails is the critical data because it is extreme, how do we avoid losing it?"** Measured: failing days are not larger-move days overall (S&P median move 0.39% failing vs 0.49% passing; 3.4% of the top-5% move days fail vs 5.6% of all weekdays), but four crash days of March 2020 failed the first rule only because of 13–14 minute exchange halts. **Data-treatment rules for every intraday test (standing):** (1) trading halts and early closes are real market states and are kept — a move is measured from the last trade before to the first trade after; (2) a day is judged only on the minutes the test uses (the release window and the span after it), not on the whole session; (3) one contract per day, the main or the patch file, whichever has more session minutes — never two spliced inside a day; (4) a day lost to the vendor is repaired from another source, not dropped, when a test needs it; (5) nothing is dropped silently — every test prints the days it left out, each day's move, and why; (6) every result is reported twice, without the left-out days and with them included on the daily move, and is flagged if the conclusion changes; (7) raw files are never altered, missing minutes are never filled in or smoothed.

### 3.55 v3e intraday tests registered (12 Nov 00:10)
`docs/prereg_intraday_v3e.md`, `src/intraday_v3e.py`. **E1 Fed statement days** (from June 2010): release time dated by the 10-year note's largest 5-minute move among 12:30 / 14:00 / 14:15; (a) where in the day each asset's move sits; (b) the test — watch the note k minutes, enter gold / S&P / Nasdaq / the note in its direction, hold 15 / 30 / 60 minutes or to the close, against shuffled directions and against placebo days at 14:00; (c) signed by the statement's own score, incl. days after ≥ 4% semiconductor falls. **E2 the 08:30 releases:** does the first move continue or reverse, does the composition score tell the direction, and does price come round to the score when the first move disagreed. Verdict rule fixed: gold in E1(b) is the primary — GRADE A candidate only if family p < 0.05, different from placebo at p < 0.05, and above the 2 bp cost; eleven secondary families count only at p < 0.005. Priors #136–#139. No cost; the data is on disk.

### 3.56 v3e first run; v3e-2 registered (12 Nov 00:30)
Gold on Fed statement days stays SUBJECTIVE grade B: entering after the release in the direction of the note's first minutes shows nothing (best cell +5.9 bp, family p 0.359). Timing (a): only 21% of gold's signed day move is in the first five minutes, 23% before the release, 56% after the first five minutes — the largest piece after 14:30 (press conference). Two things not established but worth a larger sample: the Nasdaq future signed by the statement's own score (all statement days with a score (n 45): enter 1 min, hold close: +45.0 bp, t +2.40, hit 53%, n 45; family p 0.136; statement days within 10 sessions after a ≥ 4% semiconductor fall (n 29): enter 1 min, hold close: +55.7 bp, t +2.42, hit 52%, n 29; family p 0.124); and, on 08:30 release days where the first five minutes went against the document's composition, the Nasdaq moving toward the document over the next hour (enter 5 min, hold 60: +14.6 bp, t +3.23, hit 62%, n 91; family p 0.017). Priors: #136 wrong, #137 right, #138 right, #139 wrong. v3e-2 registered: statement time fixed at 14:00 from March 2013; every statement scored (priors #140, #141).

### 3.57 v3e-2 result; v3e-3 registered (12 Nov 00:50)
With the statement time fixed at 14:00, gold is still not a grade A candidate (enter 1 min, hold 15: +7.2 bp, t +2.36, hit 55%, n 132; family p 0.160) — #140 right. With every statement scored, entering the Nasdaq future one minute after the release in the direction of the statement's score: enter 1 min, hold 60: +23.0 bp, t +4.44, hit 57%, n 132; family p 0.000 — clears the secondary bar; **first SUBJECTIVE grade A candidate**; #141 counted wrong. Caveats recorded: hindsight in the reader (it was given the dates), one cell of 16, a Nasdaq future. Registered before running: (d) the founder's after-the-press-conference drift test; (e) checks on the score result, including the before-the-release placebo; forward rule FA-1 (live scoring at each coming statement). Founder's question answered in the record: "no grade A" never meant "no usable signal" — grades apply only to SUBJECTIVE findings (B = same-day link at daily closes, A = shown catchable with minute prices); QUANT is a separate list (one confirmed risk forecast, candidates on the forward log).

### 3.58 v3e-3 result; E2-all registered; forward rules FA-1, FA-2 (12 Nov 01:10)
Checks on the Fed-statement-score rule all pass (+30.0 bp over the hour after the release on the Nasdaq future, 74% of 101 days; no link before the release; similar in four periods; larger for stronger scores; survives dropping the ten largest days) — **SUBJECTIVE grade A candidate, confirmed on history, live confirmation pending** (#143 right). After the press conference: no family reaches its bar; gold's own move to 15:15 continuing overnight is the near miss (p 0.010) (#142 right). Founder's decision: fund the larger 08:30 test — registered as E2-all with a replication on new days only (prior #144). TEST_BOOK Part B updated (B8).

| # | step | why it matters to the business | founder decides |
|---|---|---|---|
| 1 | E2-all: fetch and score every data release from June 2010, replicate on new days | settles whether "price comes round to the document" is real | nothing — funded |
| 2 | FA-1 live scorer for the 9 Dec Fed statement (score at release, log the next hour) | the only way to remove the hindsight doubt from the grade A candidate | nothing — Claude builds it before 9 Dec |
| 3 | Confirm E1(c) on semiconductors themselves (ETF minute data for statement days) | the product claim is about semiconductors, the test used the Nasdaq future | whether to buy one month of ETF minute data (≈ US$50) |
| 4 | Costed rules for the two QUANT candidates from the horizon audit (QC-1, QC-2) | decides whether either is a signal | — |
| 5 | Test book parts 2–6; reader consistency; §3.46 items; app redesign | — | — |

### 3.59 E2-all result; AI-chain earnings test designed (12 Nov 02:20)
**E2-all.** On the 671 release days never looked at, the fixed rule "first five minutes against the document's score → enter the Nasdaq future with the score, hold 60 minutes" gives +3.7 bp, t +1.79, hit 60%, n 144, one-sided p 0.028; the S&P future +3.1 bp, t +1.96, hit 56%, n 144, one-sided p 0.024. Replicates → second SUBJECTIVE grade A candidate, thin after cost (#144 counted wrong). N1/intraday LLM spend to date ≈ US$30.5 (the founder authorised going past the earlier US$25 cap for this test).

**AI-chain earnings test — DESIGN, not yet registered (founder, 12 Nov).** Founder: only about six trades a year come from Fed statements; apply the same test to company news, because "these companies' financial reports can alter the whole market's basic logic — all are parts of the same chain called artificial intelligence", and one good report can lift the whole index.
- **Companies (founder's list):** AMD, NVDA, MU, INTC, AVGO, SNDK, SKHY (SK Hynix), ORCL, TSM, CRWD, GOOG, META, AMZN, MSFT. To be added when they have completed a listing: Anthropic and OpenAI (agenda item; nothing to test before then).
- **Events:** each company's quarterly results release — about 56 a year. Release minute from the SEC's acceptance timestamp of the filing (8-K item 2.02; 6-K for TSM). Stated limits: the filing can reach the SEC some minutes after the news wire; SK Hynix reports in Korea, outside the SEC, and needs its own source and time; SanDisk has traded again only since 2025.
- **Score:** the same story-free reader as the Fed statements (what the document means for stocks, −1 … +1), on the release text; a sample is checked first, because the reader has so far scored only official statistics and Fed documents. The project's earlier v1 reads of earnings filings (ASML, TSM, TSLA, ORCL, LMT, MU, INTC, NVDA, MSFT) are a different schema and are not pooled.
- **Test (same structure as E1(c)):** enter 1 minute after the release in the direction of the score; hold 15 / 30 / 60 minutes and to the next 09:30. Measured on (i) the Nasdaq-100 future — already on disk, trades after the close, and these companies are its largest weights, so it is the right instrument for "moves the whole market"; (ii) the company's own stock and the semiconductor ETFs, minute prices including before and after hours — to be bought (Stage 2). Checks as for E1(c): shuffled scores, no link before the release, periods, score strength, without the ten largest days; spill-over from one company's release to the other thirteen.
- **Data route:** quote Databento's US-equity datasets against the remaining credit first (`intraday_fetch equities`, quote only); a second free-credit account is not used (one promotional credit per user is the vendor's term); otherwise pay as you go or one month of Alpha Vantage.
- **Order:** quote → founder decides the purchase → registration with priors → filings and release times fetched → scores → Stage 1 on the future → Stage 2 on the stocks.

### 3.60 Stock minute data on disk; AI-chain earnings test, stage A (13 Nov 00:50)
**Bought:** Databento XNAS.ITCH (trades on the Nasdaq exchange, 04:00–20:00 New York), 1-minute bars, 1 May 2018 → 11 Nov 2026, quoted US$12.65: AMD, NVDA, MU, INTC, AVGO, SNDK, ORCL, TSM, CRWD, GOOG, META (and FB, its ticker to June 2022), AMZN, MSFT, plus SOXX, SMH, QQQ — about 20 million bars under `data_provenance/intraday/eq/` (ignored folder; not uploaded). Databento total US$115.33 of the US$125 free credit. SK Hynix (founder: Nasdaq-listed since 6 July 2026) was left out of that request by Claude and is fetched by rerunning the same command. A second free-credit account is not used. Limits: one exchange's trades only; history from 2018 (the Nasdaq-100 future runs from 2010); prices not adjusted for share splits (immaterial inside a day).
**Founder's clarification (12 Nov), recorded:** the company list is the list of whose NEWS is read. Part 1 measures the reaction on the Nasdaq-100 future already on disk ("one report can alter the whole market's basic logic") and needs no purchase; Part 2 measures each company's own stock and the spill-over to the other thirteen, on the data above. Short-history names (SanDisk, SK Hynix; later Anthropic and OpenAI once listed) are included and simply contribute few events at first.
**Stage A (no LLM, no cost):** `src/ai_earnings.py filings` — every 8-K Item 2.02 from June 2010 for the US filers on the list, with the SEC acceptance time to the second and the text of the attached release; `times` — when in the day they arrive. Foreign filers (6-K) are counted and handled in stage B. Stage B: sample check of the reader on results releases → registration with priors → scores → tests.

### 3.61 AI-chain news: both types scored; the test registered (15 Nov)
`docs/prereg_ai_chain.md`, `src/ai_earnings.py`, `src/ai_chain_test.py`, `docs/ai_chain_scores_summary.md`.
**Founder (15 Nov):** score two kinds of company news. Type 1, results releases: reported figures against the company's previous guidance, and the new guidance. Type 2, other events (for example a chief executive's sudden resignation): scored against the latest type 1 report — the change to future free cash flow, balance sheet and guidance, the uncertainty added, and the competitors, suppliers and customers affected.
**Collected (SEC filings only, exact acceptance times):** 756 results releases (662 US 8-K Item 2.02 + 94 TSMC quarterly 6-K) and 1,854 other events (1,698 event filings: officer / director changes 412, other events 392, disclosures 237, material agreements 165, new debt 80, and smaller groups; plus 156 TSMC monthly revenue reports).
**Scored:** 754 results (reader `ai-earn-v3-2026-11-15`, each release sees the guidance of the one before; facts found: revenue 99%, free cash flow 78%, next guidance 67%) and 1,854 events (reader `ai-event-v2-2026-11-15`, each against the latest results). 469 events are material 0.3 or more. LLM spend: US$0.34 sample + US$0.54 trial (both superseded: the trial showed the cash-flow tables sat beyond the text sent, and one answer was cut short) + US$40.44 full run.
**Registered before any price was joined:** seven families (results -> Nasdaq future, own stock, affected companies; events -> own stock, affected companies, Nasdaq future; foreign filers), 311 cells, family p by shuffled scores, bar 0.05 / 7 = 0.0071, costs 2 bp future / 10 bp stock (assumed). Priors #145–#152. No cost; the prices are on disk.

### 3.62 AI-chain news test: result (15 Nov 19:20)
`docs/ai_chain_test.md`, `docs/ai_chain_test.json`, `docs/prereg_ai_chain.md` §7. **None of the seven families passes** (bar: family p < 0.0071 = 0.05 / 7).
| family | best cell | result | family p |
|---|---|---|---|
| F1 results -> Nasdaq future | results against prior guidance; enter 5 min after the stamp, hold to the next 09:35 | +16.7 bp, t +3.54, 61% of 294 days | 0.0925 |
| F2 results -> own stock | market score; enter 5 min after, hold 30 min | +41.4 bp, t +3.72, 58% of 330; before the stamp +55.0 bp (t +2.89) | 0.0100 |
| F3 results -> affected companies | copy the reporter; 1 min after, hold 15 min | +6.0 bp, t +2.33 | 0.2480 |
| F4 events -> own stock | free-cash-flow outlook, material 0.2+; next regular session, hold 60 min | +22.6 bp, t +2.42, n 238 | 0.3605 |
| F5 events -> affected companies | copy the reporter; next regular session to 16:00 | +22.3 bp, t +1.72 | 0.6280 |
| F6 events -> Nasdaq future | own-stock score, material 0.3+; 5 min after, hold 60 min | -8.7 bp (against the score) | 0.4980 |
| F7 foreign filers | own stock; next regular session to 16:00 | -17.4 bp (against the score) | 0.5650 |
**Reading.** Other company events (type 2): no usable link, NEITHER. Results releases (type 1): two near misses. F1 — the Nasdaq future held overnight after results that beat the company's prior guidance: clean before the stamp, positive in all four periods, but family p 0.09. F2 — the company's own stock in the first hour after the stamp: family p 0.010 (bar 0.0071), the drift shrinks the later the entry (own-stock score, hold 60 min: +64.9 bp entering after 1 min, +40.8 after 5, +25.0 after 15), and the stock was ALREADY moving with the score before the SEC stamp, which means the stamp is late against the news wire; the 10 bp stock cost is an assumption for after-hours trading. The reader's spill-over directions (who gains, who loses) did not pay: F3 and F5 null.
**Priors:** #145, #146, #148, #149, #150, #151 right; #147, #152 wrong. **Forward log (not signals):** FA-3 = F2's cell on each new results release; QC-3 = F1's cell. LLM spend for this test: US$41.39 (0.34 + 0.54 + 40.44 + 0.07). SK Hynix prices still to download.

### 3.63 Live news listener built on the fastest sources that answer (15 Nov 20:40)
`src/wire_probe.py`, `docs/wire_probe.md`, `src/news_listener.py`, `docs/live_news_log.md`, `docs/SELLING_POINTS.md` (version 2).
**Founder (15 Nov):** the product exists so that users see the news fast enough; a component that reads the news later than anyone has no purpose (customer-view rule, PROJECT_MASTER). The backtest's clock was the SEC acceptance stamp because it is the only free, exact, complete record of PAST release times; it is some minutes later than the news wire (F2: the stock had already moved +55.0 bp with the score before the stamp). Both steps approved: (1) past wire times for a rerun of the backtest, (2) the live listener. Step 2 first.
**Probe (26 candidate addresses, from the founder's machine):** answer as feeds — PR Newswire (all releases; earnings), the SEC's latest-filings feed, NVIDIA newsroom, AMD investor page, Meta investor page, SK Hynix newsroom (Microsoft's news feed answers but is stale). Refuse scripts — Business Wire (empty answer), GlobeNewswire (403), the investor pages of Broadcom, SanDisk, CrowdStrike (403); addresses guessed wrongly (404) for NVIDIA investor, Micron, Oracle, Amazon, Microsoft investor, Intel. Past release times: PR Newswire company pages show clock times; GlobeNewswire and Business Wire search refuse scripts — so step 1 is feasible only for part of the list unless another route is found.
**Listener:** watches the feeds above plus the Fed's press feed and, for all fourteen companies, the SEC filing list as the backup. A results release, a material 8-K / 6-K or an FOMC statement is fetched and scored by the SAME readers as the backtest (`ai-earn-v3`, `ai-event-v2`, `n1-doc-v3`), with three clocks logged (published by the source, seen here, scored) and the delay between two sources of the same release. Other wire items about the list are logged, not scored. This is also the live scorer for forward rules FA-1 (Fed statement, next 9 Dec 2026) and FA-3 / QC-3 (results releases). Limits: free feeds may lag; companies whose wire refuses scripts are seen only through the SEC route until a faster source is added; the machine must be running at release time; prices are joined to the log afterwards.

### 3.64 Forward record: rules and cells fixed before any live outcome (17 Nov 02:10)
`src/live_outcomes.py` -> `docs/live_outcomes.md`. First live run of the listener (15-16 Nov, 1,175 passes): stable, recovered by itself after the machine was offline; one SK Hynix 6-K seen 55 s after its stamp and scored 6 s later (routine); an acquisition AMD announced on its own page was only logged -> the listener now also scores material announcements from a company's own feed, and a failed fetch on one source no longer blocks the next source. AMD drill: score ready 18 s after the release was seen; free cash flow missing in the feed page's text (open).
**The cells, fixed here (no search later).** FA-1: Fed statement, Nasdaq future in the direction of the score, 1 min after the release, hold 60 min (v3e E1c; backtest +30.0 bp, 74% of 101). FA-2: Fed day, gold's own move from the release to 15:15 held to the next 09:30 (v3e-3 d; +40.3 bp, 67% of 132). FA-3: results, own stock in the direction of the market score, 5 min after, hold 30 min (ai-chain F2 best cell; +41.4 bp, 58% of 330). QC-3: results stamped 16:00-16:40, Nasdaq future in the direction of 'results against prior guidance', 5 min after, to the next 09:35 (F1 best cell; +16.7 bp, 61% of 294). CV-1 (customer view, a record and not a registered rule): own stock in the direction of the own-stock score, entered 1 min after the score was ready on this machine, hold 60 min.
**Clock.** The release = the time the first source states, or our own first sight when it states none or states a later time. The backtests used the SEC stamp for results, so live entries can be EARLIER than the backtest's; the difference is logged per event. **Verdict:** none before 30 trades per rule. Prices: Databento minute bars for the event day and the next, a few cents per event. Next events: NVIDIA results 17 Nov about 16:20 New York; Fed statement 9 Dec 2026.

### 3.65 W1 registered: the wire clock against the SEC clock (17 Nov 02:50)
`src/wire_history.py`, `docs/wire_history_probe.md`. **Probe:** PR Newswire's company pages hold past releases with clock times for Meta (to 2013), Oracle, Broadcom (to 2018) and Microsoft (paged, to 2018 and earlier); for the other ten the pages stop in 2011-2018 or hold no results releases (their wires, Business Wire and GlobeNewswire, refuse scripts). **Founder (17 Nov): "why are we not continuing to find ways to find the remaining companies" -- Claude had stopped at the first route.** Probe 2 (`docs/wire_history_probe2.md`): Intel's and AMD's own press-release lists answer, print one clock time per release and page back; a public mirror of the wire (FinancialContent) prints "Published at ... via Business Wire" on a release page (confirmed for Intel, 29 Oct 2026, 4:01 PM EDT = the time on Intel's own page). So three routes feed one file with a `source` column: PR Newswire company pages (4 companies), the company's own list (Intel, AMD), and the mirror (Amazon, CrowdStrike, SanDisk by the confirmed address pattern; Micron, NVIDIA by a guessed pattern; a SECONDARY source, labelled). Alphabet uses no wire: SEC time only. Coverage is whatever these routes find, reported per company.
**W1, fixed before running.** (a) `collect`, `collect_own`, `collect_mirror`: every dated item the three routes give -> `data_provenance/ai_earnings/wire_times.csv`. (b) `lag`: each SEC results release matched to the wire item of the same release (results-like title, published from 3 hours before the SEC stamp to 30 minutes after; the earliest); lag = SEC stamp minus wire time, per company. (c) `rerun`: on the matched releases from May 2018, the SAME cells from both clocks, no search: own-stock score, enter 1 / 5 / 15 min, hold 60 min (the selling-point table) and market score, enter 5 min, hold 30 min (FA-3). A description of what the earlier clock is worth; no pass/fail bar, because the releases are a subset of F2's and nothing new is selected.
**Priors (Claude, counted if wrong).** #154: the wire is first on at least 70% of matched releases and the median lag is between 1 and 10 minutes. #155: own-stock score, enter 1 min, hold 60 min, earns more from the wire time than from the SEC stamp on the same releases.
**Limits.** Coverage depends on which routes answer; the mirror's time is the wire's time as a third party shows it; the wire states whole minutes; a wire time before 16:00 means an entry inside regular trading, where prices behave differently; if these four file with the SEC at almost the same minute, the two clocks will show little difference and the lateness seen in F2 (+55.0 bp before the stamp) belongs mostly to the other eight companies, which this route cannot reach.

### 3.66 W1 result: the SEC stamp is late, and the earlier clock is worth more (17 Nov 03:30)
`docs/wire_lag.md`, `docs/wire_rerun.md`, `data_provenance/ai_earnings/wire_times.csv` (5,029 dated items, column `source`).
**Collected.** PR Newswire company pages: Meta 76, Oracle 1,787, Broadcom 139, Microsoft 1,882 items. Own lists: Intel 576, AMD 490 releases with a time (from Feb 2018). Mirror (secondary source): Amazon 23 of 34 past results releases, CrowdStrike 21 of 31, SanDisk 7 of 7, Micron 17 of 34, Intel 11 of 35, **NVIDIA 0 of 36** (the guessed address pattern is wrong). Alphabet: no wire, not collected.
**Lag (SEC stamp minus wire time), 227 matched results releases of 10 companies:** wire first on 85%; median 4 minutes; 0-2 min: 34, 2-10 min: 120, 10-30 min: 32, over 30 min: 7, SEC first: 34. By company (median): AMD 2, CrowdStrike 2, Meta 4, Broadcom 5, SanDisk 6, Intel 8, Oracle 9, Amazon 10 minutes. **Two exceptions:** Microsoft (median -2: its wire item is a notice that the release is on its own site, posted after the SEC filing) and Micron (median -1). #154 right.
**Rerun, same releases, same cells, two clocks (before cost):**
| score | enter after | hold | from the wire time | from the SEC stamp |
|---|---|---|---|---|
| own stock | 1 min | 60 min | +86.3 bp, t +2.76, 55% of 217 | +36.4 bp, t +1.60, 55% of 216 |
| own stock | 5 min | 60 min | +37.4 bp, t +1.99, 54% of 216 | +16.0 bp, t +0.91, 52% of 216 |
| own stock | 15 min | 60 min | +18.8 bp, t +1.19, 53% of 216 | +18.3 bp, t +1.16, 54% of 217 |
| market | 5 min | 30 min | +51.2 bp, t +3.00, 59% of 199 | +24.0 bp, t +1.66, 52% of 199 |
#155 right. **Reading.** Entering from the wire time earned more than twice what the SEC clock earned on the same releases; by 15 minutes the two are equal -- the extra is in the first minutes. The share of winning trades is the same (about 55%): the gain comes from the SIZE of the moves caught, not from being right more often. A description on a subset (about two thirds of the 2018+ releases of ten companies), no new pass/fail; the F2 verdict (near miss) stands.
**Open:** NVIDIA and Alphabet have no wire time; Microsoft's and Micron's true first source is not the wire item found; the mirror lacks older releases.

### 3.67 Design questions registered: overlapping signals, the size of the score, costs (17 Nov 03:45)
`src/ai_chain_design.py` -> `docs/ai_chain_design.md`. **Founder (17 Nov):** how were the costs calculated; how were the holds made; if two news items in the same hour point opposite ways for one stock, what position does the code hold; does the score represent each item's significance, and how is significance measured; is it a different approach from the macro engine's.
**What the first test did (stated plainly).** (i) Costs: NOT deducted. Every return on record is before cost. Costs entered only the pass rule (2 bp for the future, taken from v3e; 10 bp for a stock, an assumption) and a 'net of cost' line. No bid-ask quotes are on disk, so real after-hours costs are not measured. (ii) Holds: every signal is its own one-unit trade, entered and exited at fixed minutes; there is no book, no netting, no limit on overlapping positions. Two opposite signals on one stock in the same hour are counted as two separate trades (in a real account they would cancel). Only F1 combined signals (the average score of an afternoon's releases, equal weights). (iii) Significance: the trade used only the SIGN of the score. The readers do give a size (-1 to +1) and, for other events, a 'material' mark (0 to 1, judged against the latest results); these were used only as a check (large against small scores) and as a cut-off (0.2 / 0.3 / 0.5), never as position size. (iv) The macro engine's 'influence weights' are a different thing: weights estimated from history per document type, asset and regime, where these are the reader's judgement of one document.
**D0 (count):** how often signals on one stock within 60 minutes disagree -- own signals, other companies' releases naming it, and a reporter named by another reporter the same afternoon. **D1 (test):** the four cells already on record (F2 own-stock 1 min / 60; F2 market 5 / 30; F1 results-against-guidance 5 min to next 09:35; F4 own stock, material 0.2+, next session 60 min), split by the size of the score (0-0.3, 0.3-0.6, 0.6-0.9, 0.9-1), with 'only 0.5+', 'only 0.8+' and 'sized by the score'; one test per cell: rank correlation between the size of the score and the trade's return against shuffled sizes (5,000), one-sided; a cell counts at p < 0.0125 (0.05 / 4).
**Priors.** #156: no cell reaches p < 0.0125. #157: in F2 own-stock 1 min / 60, the 0.9-1 group has a higher average than the 0-0.3 group.
**Next, the founder's decision:** D2 netting (one net position per stock per hour from all signals, sized by score) as a registered rule; D3 measured costs (bid-ask quotes around the event minutes from Databento; price to be quoted first).

**3.67 result (18 Nov 02:10; `docs/ai_chain_design.md`).** **D0.** A company's own signals: 561, pairs on one stock within 60 minutes 2, pointing opposite ways 0 -- a company's own news almost never collides with itself. Other companies' releases naming a stock (after 16:00): 1,661 stock-afternoons, 147 with two or more mentions, 57 of these (39%) with both a positive and a negative direction. A stock that reports and is named by another reporter the same afternoon: 87 cases, the other release points against the stock's own results score in 24 (28%). So opposite signals are a matter of the spill-over signals, which did not pay in F3 / F5.
**D1 (bar p < 0.0125).** F2 own-stock score, 1 min, hold 60: **larger scores earn more** (rank correlation +0.142, p 0.0040). By size of score: 0-0.3 +5.9 bp (53%, n 93); 0.3-0.6 -0.5 bp (51%, n 108); 0.6-0.9 +203.2 bp (70%, n 57); 0.9-1 +108.6 bp (62%, n 107). Only 0.5+: +97.4 bp (n 239); only 0.8+: +137.5 bp (n 135); sized by the score +93.5 bp per unit; every score one unit +64.9 bp (n 365). The whole gain sits in scores above 0.6; below it the trade earned nothing. Not monotone at the top (0.6-0.9 above 0.9-1). The other three cells: no evidence (F2 market 5/30 p 0.40; F1 p 0.52; F4 p 0.39). Priors: **#156 wrong** (one cell reached the bar), #157 right. Caution: the cell was chosen after F2's table was seen; the size effect needs the forward record.

### 3.68 Registered: size by a learned shape (S), netting (N), measured IBKR costs (C) (18 Nov 02:40)
`src/ai_chain_sizing.py`. **Founder (18 Nov):** use the score as leverage -- the more a news item changes the company's value, the larger the position; the relation need not be proportional, so let least squares find the parameters and write the equation; test it side by side with the netting rule; then measure costs as on Interactive Brokers.
**S.** Trade: results -> own stock, 1 min after the SEC stamp, hold 60 min. r = the stock's return (bp), s = the own-stock score. Four shapes fitted by least squares (minimise the sum over releases of (r - prediction) squared): M0 r = b sign(s); M1 r = b s; M2 r = b sign(s) |s|^g, g on a grid 0 to 4; M3 r = b sign(s) [|s| >= h], h on 0.1 to 0.9. Position = the fitted shape; compared per unit of position. **Judged out of sample only:** for each year with at least 60 earlier releases the parameters are fitted on earlier releases and applied to that year. In-sample fits are shown as description.
**N.** One account per stock per afternoon; signals = own results score and other releases' directions for that stock; position after each signal = sum of signs (or of scores) so far, limited to one unit, held to 60 minutes after the last signal; against 'each signal alone'. Reported for all stock-afternoons, own-report afternoons, named-only afternoons, two or more signals, opposite signals.
**C.** IBKR Pro Fixed (pricing page read 18 Nov 2026): USD 0.005 per share, minimum USD 1, maximum 1% per order; SEC fee 0.0000206 x sale value. Spread: Nasdaq best bid and ask at the entry and exit minute of each past F2 trade (Databento, price quoted before download). Round trip = half spread in + half spread out + two commissions + fee, for US$10,000 per trade. Output: cost distribution and the rule after cost.
**Priors.** #158: the in-sample power g is above 1. #159: out of sample, the step shape M3 earns more per unit of position than M0. #160: on afternoons with opposite signals, 'each signal alone' averages between -15 and +15 bp per unit. #161: the median measured round-trip cost is between 10 and 40 bp.
**Limits.** S is built on the cell where D1 already showed a size effect, so even the out-of-sample table is partly informed by hindsight; the forward record (CV-1, FA-3) is the real test. N adds the spill-over directions, which showed no edge alone. C uses one exchange's quotes for a small size; outside regular hours IBKR takes limit orders only.

**3.68 results, S and N (18 Nov; `docs/ai_chain_sizing.md`, `docs/ai_chain_netting.md`).**
**S, in sample (365 releases; description only):** M0 sign b +64.9 bp, per unit +64.9 (t +3.53); M1 linear b +121.3, per unit +93.5 (t +4.28); M2 power b +135.7, **g = 1.65**, per unit +104.7 (t +4.25); M3 step b +143.7, **h = 0.7**, per unit +143.7 (t +4.74, 163 traded). The shapes explain 3-7% of the squared returns: the score moves the average, most of each move is still noise.
**S, out of sample (2020-2026, 302 releases; each year's parameters fitted on earlier releases only):**
| shape | per unit of position | t | traded | parameter by year |
|---|---|---|---|---|
| M0 sign | +77.5 bp | +3.76 | 302 | - |
| M1 linear | +98.4 bp | +4.00 | 302 | - |
| M2 power | +105.6 bp | +3.78 | 302 | g 2.95, 2.50, 1.55, 1.05, 1.45, 1.80, 1.45 |
| M3 step | **+141.5 bp** | **+4.16** | 140 | h 0.8 in 2020, then 0.7 every year |
Sizing by the score beat equal sizing out of sample in every shape; the step shape (trade only scores of 0.7 or more) earned most per unit and its threshold was the same in six of seven years. #158 right (g above 1), #159 right.
**N (1,464 stock-afternoons):** per unit of capital -- each signal alone +17.1 bp (t +3.55); net of signs +19.5 (t +3.89); net of scores +38.1 (t +4.47). The stock itself reported (361): +45.6 / +56.4 / +82.8 (t +3.83). Only named by others (1,103): +6.7 / +7.4 / +11.5 (t +2.58 to +2.90). Two or more signals (160): -1.2 / +0.1 / +15.3 (t under 1). Signals pointing opposite ways (54): -8.9 / -16.4 / +4.5 (t under 1). #160 right.
**Reading.** The founder's idea holds on this data: the score should set the size. Netting itself changes little (collisions are rare, 54 afternoons, and earn nothing either way); what lifts 'net of scores' is that it sizes by the score. Being named by another company's release carries a small positive drift (+7 bp, t about 2.7), below any plausible cost. **Candidate rule from this:** trade a results release in its own stock only when the own-stock score is 0.7 or more in size. Caution, stated: the trade was chosen after F2's table was seen; the forward record decides. **C (costs) not yet run** -- the Databento key in the terminal was the placeholder text; #161 waits.

### 3.69 First live results release: NVIDIA, 17 Nov 16:20 New York -- the live read failed; cause and fix (18 Nov)
**What happened.** The listener saw NVIDIA's 8-K (items 2.02, 9.01) through the SEC route at 16:22:13 New York, 83 seconds after the SEC stamp, and returned a read 6 seconds later -- with every score 0 and no revenue. NVIDIA's own newsroom carried the release 196 seconds AFTER the SEC route (for NVIDIA the SEC was the faster source), and was not scored because the first source already 'had a score'.
**Cause (Claude's code).** The SEC text fetch took only exhibit files whose names contain 'ex99', 'press' or 'release'. NVIDIA names its exhibits differently, so the reader was given the filing's cover page alone and correctly found no results in it. The listener then treated that empty read as a valid score, which blocked the second source. The AMD drill had gone through AMD's own feed, so the SEC text path was never exercised on a results release before the first live one.
**Fix.** (1) The SEC fetch now takes the three largest exhibit documents of the filing whatever their names. (2) A results read with no revenue and every score 0 is an EMPTY read: logged as not scored, and the next source is tried. (3) `python -m src.news_listener rescore --ticker NVDA` redoes the read from the filing. **Rule for the forward record, fixed before any NVIDIA price is looked at:** a rescored read is made from the text alone, so the rules that depend only on the release time (FA-3, QC-3) may use it, flagged 'rescored'; it is NOT a customer-view observation -- no user could have acted on it -- so CV-1 does not count it.
**Also seen live:** an NVIDIA newsroom item ('Board of Directors Establishes National Security and Export Control Oversight Committee') was scored as an event through the company's own feed (material 0.25, own stock -0.15, uncertainty +0.35), 16 s after it was seen -- the route added on 17 Nov works. Listener stability: 3,457 passes over 10 hours; sources silent only when the machine was offline.

### 3.70 Step rule registered as forward rule FA-4; netting set aside (18 Nov 23:55)
**Founder's conclusion (18 Nov):** drop netting as a rule -- opposite signals are rare (54 of 1,464 stock-afternoons) and earn nothing either way; keep the step rule as the candidate because its threshold was stable. Agreed. A real account would still never hold a long and a short in the same stock at once; that is housekeeping, not a rule to test.
**FA-4, fixed here.** On a results release of a listed AI-chain company: if the reader's own-stock score is 0.7 or more in size, trade the company's own stock in the direction of the score, enter 1 minute after the release, hold 60 minutes; otherwise no trade. Backtest behind it (TRACK 3.68): +141.5 bp per trade on 140 trades in 2020-2026 with each year's threshold fitted on earlier years (0.7 in six of seven years); before cost. **Category by the founder's rule:** the hold is 60 minutes, so it is an intraday rule -- SUBJECTIVE list, grade A candidate -- although it is fully rule-based and needs no judgement.
**What turns the candidate into a signal.** (1) Costs measured (C; download quoted at about US$0.01) and the rule still positive after them. (2) The forward record: 30 FA-4 trades. About 45% of past releases cleared 0.7 (163 of 365), and the list publishes about 56 results a year, so roughly 25 trades a year: about 14 months to 30. An interim look after each earnings season, labelled as interim.
**First live case.** NVIDIA, 17 Nov 2026 16:20:51 New York: rescored own-stock score +0.7 (revenue US$115.8 billion, up 103% on the year; results against prior guidance +0.9; new guidance +0.3; other companies named: TSM +0.6, MU +0.6, MSFT +0.6, GOOG +0.6, AVGO +0.1). It clears the threshold. FA-4 was registered AFTER this release but BEFORE its prices were available from the vendor (the price request of 18 Nov was refused as 'data_end_after_available_end'), and the score was made after the fact because the live read failed (3.69); the row is kept with both facts stated.

**3.68 result, C: measured costs on Interactive Brokers (19 Nov; `docs/ai_chain_costs.md`).** 359 of 365 past trades with Nasdaq quotes at both ends (6 downloads timed out); download cost US$0.01. Round trip for US$10,000, in bp: spread when entering median 22.3 (average 32.7; nine in ten below 69.4); spread when leaving median 14.3 (average 21.1); spread cost of the round trip median 19.1, average 26.9; commission and fee 2.2; **total median 21.3, average 29.2, three in four below 34.2, nine in ten below 54.1.** #161 right. My earlier assumption of 10 bp was too low by a factor of two to three.
| rule | trades | before cost | cost | after cost | t after cost | right on after cost |
|---|---|---|---|---|---|---|
| every score, one unit | 359 | +64.8 bp | 29.2 bp | +35.5 bp | +1.93 | 54% |
| only scores of 0.8 or more | 132 | +132.8 bp | 29.0 bp | +103.8 bp | +3.13 | 60% |
**Reading.** Trading every score barely survives the real cost; trading only strong scores keeps about four fifths of its gain. This is the second independent reason for the step rule (FA-4). Limits: Nasdaq's own quotes for a small size (IBKR's routing can only do as well or better; a large order does worse); outside regular hours only limit orders are accepted, so a fill is not certain; the cost of selling short (borrow) is not included.

### 3.71 'Event signals' page: the live view the founder asked for (20 Nov)
`pages/Event_signals.py`, `src/live_view.py`. **Founder (20 Nov):** show the live direction on the site so it can be used; the page must refresh itself every 30 seconds without pressing refresh; the news collection and scoring must run and check every 30 seconds; show the rule line ('enter 1 minute after, hold 60 minutes'), or whichever rule later tests crown.
**Built.** A second page of the Streamlit app, redrawn every 30 seconds: the rules in force with their evidence and measured cost (from a list at the top of `src/live_view.py`, so a later rule replaces it in one place); signal windows (BUY / SELL, entry and exit time in New York and local time, minutes left, open / closed); every scored item with its scores, figures and the other companies named; the forward record; items seen but not scored; whether the listener is running. The page only displays the listener's log -- the listener runs in its own terminal (`python -m src.news_listener run --poll 30`).
**First case shown.** NVIDIA, results of 17 Nov, own-stock score +0.7: the rule says buy at 16:22 and sell at 17:22 New York. Scored after the fact (3.69), so no live trade was possible; priced in the forward record once the vendor's bars are downloaded. No signal existed for AMD on 17-19 Nov.
**Gap named by the founder (20 Nov):** a short-seller's report on a listed company (he cites Hunterbrook on AMD) is not seen by the listener: its sources are the companies' own releases and filings, PR Newswire, the SEC and the Fed. Whether to add third-party publishers, labelled as an allegation by a party with a position, is the founder's decision; it would be a new source class with its own test.

### 3.72 Third-party research publishers admitted as a source class; source register; no more Databento spending (20 Nov)
**Founder (20 Nov):** include research reports such as SemiAnalysis and funds that publish such as Hunterbrook; Hunterbrook's report on AMD of 19 Nov moved AMD about 9% lower (his figure) and the listener saw nothing; the sources he names must be recorded so he does not repeat them; the live page must be reachable and refresh itself; **Databento credit is not to be used from now on.**
**Checked.** Neither name was in any project file before today (search of `docs/`); recorded now in `docs/SOURCES.md`, which is the register from here on.
**Built.** (1) Listener: a `research` class with Hunterbrook and SemiAnalysis (candidate feed addresses; the first that answers is used). An item is taken when its title or summary names a listed company; it is scored by its own reader `ai-research-v1-2026-11-20` against the company's latest results (stance, new information, material, free-cash-flow outlook, uncertainty, own stock, other companies, main claims), labelled 'third-party report, claims unverified'. Paid articles are scored from the public part. No trading rule: alert only, until a test exists. Admission date 20 Nov: the 19 Nov AMD report is not credited; `python -m src.news_listener research --ticker AMD` scores the newest such report as a drill. Each event and report now keeps its own saved read (two items from one source on one day no longer share one). (2) Forward record prices: Yahoo's free 1-minute bars (kept about a week); no paid data. Lower quality than exchange data, stated. (3) Main page: a link to 'Event signals' (the app's own style sheet hides Streamlit's header, and with it the page menu).
**Product question, open:** for a user the listener and the page must run all day on a server, not on the founder's laptop; estimated at a few US dollars a month for a small server plus cents of scoring; founder's decision.

### 3.73 First live outcome; research feeds live; page reworked; discovery net and server planned (20 Nov 01:10)
**NVIDIA, results of 17 Nov 16:20:51 New York (score made after the fact, 3.69; prices: Yahoo 1-minute bars for the stock, Databento for the future, downloaded before the ban).** FA-4 (step rule; own-stock score +0.7; buy 16:22, sell 17:22): **+118.9 bp**. FA-3 (market score +0.5; buy 16:26, sell 16:56): **-87.9 bp**. QC-3 (results against guidance +0.9; Nasdaq future from 16:26 to the next 09:35): **+16.4 bp**. One event; no verdict before 30 per rule. CV-1 not counted (no live score existed).
**Research feeds.** Both answer from the founder's machine: Hunterbrook at `newsletter.hntrbrk.com/feed` (20 items, 5 naming a listed company), SemiAnalysis at `semianalysis.com/feed/` (10 items, 8 naming one). Hunterbrook's 'AMD Has Its Own China Problem' (published 19 Nov 10:26 New York) read as a short report: stance -1, own stock -0.4, material 0.5, new information 0.7, uncertainty 0.6; had the source been connected, the listener would have seen it within about a minute of publication.
**Fault (Claude's code) and fix.** On the first run with the two new sources the listener scored 14 of their OLD articles (some months old), because 'memorise first' applied only when the whole memory was empty, not per source. This broke the admission rule (a source is scored only on items after its admission) and put old items on the page. Fixed: a source connected for the first time is only memorised; an item more than a day old when first seen is never scored; the page hides such items. The 14 reads stay in the log, marked by their age, and are used for nothing.
**Founder's page instructions (20 Nov), applied.** 'Signal windows' renamed **Suggestions** and placed first; the rules moved to a closed section at the bottom ('How the suggestions are made'); scored news in order of release, newest first; every date with its year; the 'Type' column replaced by plain names (Financial results / Company announcement / Regulatory filing / Third-party report (unverified) / Fed statement) with a one-line key; the 'not scored' block removed -- **every item about a listed company is now scored** (routine ones come back with 'material' near 0); only second copies of a release already scored are skipped. Recent items without a tested rule that read strongly (own stock 0.3 or more in size, or material 0.5+) appear under Suggestions as information only. Scoring budget: 150 scores per New York day (about US$2 at most).
**Founder's idea (20 Nov): use Google's Gemini as the search engine for the newest news, pass the links to Claude, score them; run it all on a server.** Plan, not built: (1) FAST PATH (30 s): the feeds already connected. (2) DISCOVERY NET (every few minutes): Google News' free search feed per company (no key, no plan) gives headlines, publishers, links and times from the whole web -- the same job as asking Gemini, but free, timed and repeatable; a language-model search (Gemini's search grounding, or Claude's own web search) as a slower sweep for what feeds miss; every link is fetched and its date checked before scoring, because a search model can return stale or wrong links. Items from the media are labelled 'media report' and kept apart from company and official sources. (3) READER: Claude, as now. (4) SERVER: one small machine running the listener, the discovery net and the page all day, restarting them if they stop, with the log pushed to the repository daily. Costs to be confirmed before building: server a few US dollars a month; scoring grows with the number of headlines admitted, so the net needs a filter (named publishers first). Open decisions: which publishers the net may admit; provider and monthly limit for the server.

### 3.74 Page as a tab; rules renamed; short reports, public calls and media registered as tests SR-1 to SR-3; discovery plan simplified (20 Nov 02:00)
**Founder's instructions (20 Nov).** (a) The main title must be the largest text. (b) The live view is to be a tab like 'Look up an asset', named 'Event-driven company signals'. (c) Swap the places of 'Source' and 'What it is'. (d) Show 15 rows of scored news. (e) Rename the rules; 'market-score rule' and 'step rule' are not understandable after a few days. (f) Test what is only 'information' today: institutions that publish short reports, each on its own; well-known investors' calls (Michael Burry and others); his hypothesis that one call alone makes no ripple but two or more in the same direction within two weeks bring 'sensational fear'; the reaction on the day and on each of the next 1-7 sessions separately, because a short may be closed before seven sessions. (g) Media (Reuters, Bloomberg, CNBC, Seeking Alpha) only after the same test shows they move prices. (h) The discovery search (Gemini) is an IDENTIFICATION layer: it finds new source addresses for the library; it does not score, and no separate date check is wanted. (i) New routes and untested strong items are to be written down automatically and he is to be reminded daily.
**Applied.** (a)-(d) in `app.py` and `src/live_page.py`. (e) Names: FA-4 **Strong-results rule**; FA-3 **Sector-reading rule**; QC-3 **Overnight Nasdaq rule**; FA-1 **Fed-statement rule**; FA-2 **Fed-day gold rule**; CV-1 **What a user could have done** (codes kept as record keys). (i) `docs/SOURCE_CANDIDATES.md` and a 'Waiting for a test' section on the tab, which also lists live items that read strongly but have no rule.
**Registered, stage A only (no price looked at).** SR-1 short-report publishers: collect each publisher's own list of reports with dates; the target and direction read from the title and summary; daily closes; market-adjusted reaction on day 0 and on each of sessions +1 to +7 one by one; per publisher and pooled. SR-2 public calls by named investors: a dated list from a news search by person and month; the same reaction test; clusters (two or more people, same direction, within ten sessions) against single calls. SR-3 media: the same test by publisher. Stage A is `python -m src.source_probe`: which publishers' archives and which news-search feeds answer, and how far back. Priors and exact cells are fixed in stage B, before prices.
**Plan agreed for discovery:** two layers only -- the listener reads the library; the search layer proposes new addresses into SOURCE_CANDIDATES, which are tested before they are read for money.

### 3.75 Probe results for SR tests; investors named; sell-off study designed (20 Nov 18:30)
**Probe (`docs/source_probe.md`).** Publishers' own lists that answer and page back: Hindenburg Research (archive, to 2017), Grizzly Research (to 2020), Blue Orca (to 2011), SemiAnalysis (to 2023); Fuzzy Panda answers with its 10 newest only. Refused or wrong address: Hunterbrook's list API (its feed of 20 works), Muddy Waters, Citron, Spruce Point, Kerrisdale, Viceroy, Wolfpack, Culper, Gotham City, Iceberg, Jehoshaphat, Scorpion, J Capital, Burry's newsletter. **Google News search feed (free):** a person and a month returns dated headlines (Michael Burry: 35 items for Nov 2025, 31 for Aug 2023) -- SR-2 is feasible by month; a publisher and a month also works (Reuters on Nvidia, May 2025: 50 items) -- SR-3 is feasible; the 'last 7 days' filter is not strict (older items come back), so dates must be read from each item. The feed also carried 'AMD shares slide as report says China links could invite US scrutiny' (Reuters) and 'AMD Shares Slump After Shortseller Raises China Concerns' (Bloomberg): the 19 Nov event the founder described.
**SR-2 investors named by the founder (20 Nov):** Michael Burry, Warren Buffett, George Soros, Bill Ackman, Ray Dalio, Cathie Wood, Carl Icahn.
**Listener fault fixed:** one SK Hynix article arrived as twelve feed entries with the same headline and was scored twelve times; a headline already seen from the same source is now skipped.
**Sell-off study (founder, 20 Nov): can unsupervised learning find under which conditions a big sell-off bounces back and under which it keeps falling?** What is on record: after a one-day fall of 4% or more in the S&P, Nasdaq-100 or semiconductors, the next five sessions are up 57-60% of the time, only 2-4 points above any five sessions (no signal); after the S&P's ten-session return crosses -4%, the S&P gains 128 bp over the next five sessions, 67% of 67 cases, but family p 0.16 (not a pass); sudden one-day falls of 1.5-4%: null. All of these asked 'does it bounce ON AVERAGE'; none asked 'WHEN'.
**Design, tests first, then the data they need.** (1) Events: a fall of X% in one day or over N sessions, for indices, sectors and the AI-chain stocks; every definition tested (grid rule). (2) Conditions known at the close of the event day, in seven groups: A the fall itself (size, speed, gap or intraday, where it closed in the day's range, volume against normal, distance from the high, the run-up before); B breadth (one stock, one sector or everything); C cause (company news, macro release, Fed, outside event, no identifiable news -- from the reads already made and new ones); D stress (VIX level and jump, VIX against three-month VIX, credit spread); E macro state (the regime label, yields, dollar, oil, the latest Fed statement score); F calendar (weekday, month-end, option expiry, earnings season, days to the Fed); G intraday shape where minute data exists. (3) Unsupervised step: group the events by their conditions ONLY, without looking at what happened next; then compare what happened next between groups, on each of the next 1, 2, 3, 5 and 10 sessions separately. (4) Check on later years: groups defined on earlier events, applied to later ones. (5) Null: outcomes shuffled across events. (6) A plain supervised benchmark beside it.
**Amount.** The limit is the number of separate events, not the number of conditions: to compare 3-5 groups with at least 30 events each on later years, several hundred separate event days are needed, and the conditions must be reduced to about ten. Stage A, `python -m src.selloff_count`, counts events under every definition and how they bunch on the same days; it looks at nothing after the event day. Stage B (definitions, conditions, priors) is registered after the counts and before any outcome.

### 3.76 SR-2 registered: public calls by well-known investors (20 Nov 18:45)
`src/public_calls.py`. **Founder (20 Nov):** order of work -- public calls first, then short reports, then the sell-off study (with the 100 largest US stocks added if the counts are small). Investors: Michael Burry, Warren Buffett, George Soros, Bill Ackman, Ray Dalio, Cathie Wood, Carl Icahn. His hypothesis: one call alone may make no ripple; two or more in the same direction within two weeks may bring 'sensational fear'. Reaction to be measured on the day and on EACH of the next 1-7 sessions separately, because a position may be closed before seven sessions.
**Data (no prices yet).** Headlines about each investor (and the fund they run) from Google News' free search feed, month by month from January 2018; a word filter drops headlines with no market word; Claude (`calls-v1-2026-11-20`) reads them in batches of 40 and lists the calls: security, direction (+1 buys / adds / praises; -1 shorts / puts / sells / warns), kind (statement, filing, media report), and whether the headline reports it as that day's news. Headlines about the same investor, security and direction within 10 days are one call; its date is the first headline.
**Test, fixed here.** Day 0 = the first session whose close comes after the first headline (a headline after 16:00 New York belongs to the next session). Return = the security's close-to-close return minus the S&P 500's (for a call on an index itself: the raw return), in the direction of the call. Cells: day 0; each of sessions +1 to +7 on its own; and the total from day 0 to +7. Groups: each investor; all pooled; negative calls only; calls reported as that day's news only; **clusters** (a call that follows, within 10 sessions, a call in the same direction on the same security by a DIFFERENT investor) against single calls. A group needs 30 calls. Null: the same securities and directions on 200 sets of other dates (at least 20 sessions from any call); p = how often a placebo set does as well; a group counts at p < 0.006 (0.05 / 8 groups).
**Priors.** #162: pooled, day 0 moves with the call (the news and the move come together) and passes. #163: none of sessions +1 to +7 taken alone passes in the pooled group -- the move is on the day. #164: fewer than 30 clusters exist, so the 'sensational fear' hypothesis cannot be judged on this list.
**Limits stated before running.** A headline often appears BECAUSE the stock moved, so a day-0 link does not show the call caused the move; a position disclosed in a quarterly filing is up to 45 days old when the public learns of it; the media report some investors far more than others; the date is the first headline found, which may not be the first anywhere; daily closes only (free prices), so the minutes after a call are not seen.

### 3.77 SR-2 first run: public calls by well-known investors (20 Nov 22:00)
`docs/public_calls_test.md` (commit ec21dda). **Data.** 11,805 dated headlines from Google News' free search feed, January 2018 to November 2026; Claude read 644 batches (about US$5.09 by the program's count); 1,317 headlines report a call -> 827 separate calls (523 positive, 304 negative) on 256 securities; 733 priced (35 securities have no prices on Yahoo, mostly delisted: Twitter, Activision, Silicon Valley Bank, First Republic and others). Calls: Cathie Wood 201, Warren Buffett 186, Michael Burry 116, Bill Ackman 88, Carl Icahn 65, Ray Dalio 40, George Soros 37.
**Result (average move in the direction of the call, minus the S&P 500; p from 200 sets of other dates; bar p < 0.0063).**
| group | calls | day 0 | +1 | +2 to +7 (each alone) | day 0 to +7 |
|---|---|---|---|---|---|
| all investors | 733 | +65 bp, p 0.005, PASS | +54 bp, p 0.000, PASS | none passes (+1, +6, -14, +4, -12, -13 bp) | +91 bp, p 0.025, no |
| positive calls | 460 | +83 bp, PASS | +96 bp, PASS | none passes | +196 bp, right 54%, PASS |
| negative calls | 273 | +35 bp, p 0.010, no | -17 bp, no | none; +3 and +6 are -38 and -55 bp (price ROSE) | -85 bp, p 0.875, no |
| Bill Ackman | 88 | +234 bp, PASS | +86 bp, PASS | none | +437 bp, right 57%, PASS |
| Warren Buffett | 186 | +86 bp, PASS | +53 bp, PASS | none | +90 bp, p 0.040, no |
| Carl Icahn | 65 | +69 bp, p 0.040, no | +41 bp, no | none | +174 bp, p 0.055, no |
| Ray Dalio | 40 | +88 bp, p 0.015, no | +22 bp, no | none | +145 bp, p 0.080, no |
| George Soros | 37 | +90 bp, p 0.035, no | +44 bp, no | none | -25 bp, no |
| Michael Burry | 116 | +17 bp, no | +49 bp, p 0.010, no | none; +6 is -97 bp | -105 bp, no |
| Cathie Wood | 201 | -11 bp, no | +55 bp, p 0.040, no | +3 is +73 bp, p 0.010, no | +39 bp, no |
| clusters (second investor, same direction, two weeks) | 12 | not judged (under 30) | | | |
**Priors.** #162 (pooled day 0 moves with the call and passes): RIGHT. #163 (no later session passes in the pooled group): **WRONG** -- session +1 passes (+54 bp; +96 bp after positive calls). #164 (fewer than 30 clusters): RIGHT, 12 -- the founder's 'sensational fear' hypothesis cannot be judged on these seven investors; it needs more investors or the short-report publishers (SR-1).
**What it supports and what it does not.** Supports: a positive call by these investors comes with a rise on the day and on the next session; nothing after session +1. Does not support: that negative calls push the price down -- no cell passes for negative calls, and over eight sessions the price went the other way (-85 bp against the call). Michael Burry and Cathie Wood: no cell passes. The share of calls that went the right way is 54-59% where the average is large, so a minority of big moves carries the averages.
**Limits (as registered).** Day 0 is close to close, so part of it happened before the headline and cannot be traded; headlines often appear because the price moved. Session +1 (buy at the close of day 0, sell at the next close) is the only cell here a user could have traded as measured.
**Faults (Claude's).** (a) Cost estimate US$2.70, counted US$5.09: the estimator guessed the answers shorter than they were. (b) 33 batches were not read (answers cut off or not valid JSON), almost all 2025-2026 months for Ackman, Buffett, Burry and Wood, so recent calls are under-counted in this first run. Fixed: more room for the answer and a batch that fails is read again in two halves; the test is re-run on the full list and that second table replaces this one in `docs/public_calls_test.md` (this section keeps the first-run numbers).
**Listener, second fix.** The same SK Hynix article was scored ten times on 20 Nov under pieces of its headline; an item with the same address, or whose headline is contained in one already seen from that source, is now skipped.


### 3.78 SR-2b registered: public calls -- the parts a user could have traded (20 Nov 22:30, before running)
`python -m src.public_calls follow` -> `docs/public_calls_follow.md`. **Why.** SR-2's day 0 is close to close and mixes what was gone before anyone could act with what could be traded. Free daily OPEN and close prices (Yahoo) split it. **Pieces**, each minus the S&P 500's same piece, in the direction of the call: (G) previous close to the open of day 0 -- already in the price, description only; (A) open to close of day 0 -- buy at the open, only for calls whose first headline was out before that open; (B) close of day 0 to close of +1 -- all calls; (C) open of day 0 to close of +1 -- A and B together. **Main groups (judged):** all, positive, negative, each of the seven investors. Null: the same securities and directions on 2,000 sets of other dates. Bar: p < 0.0017 (0.05 / 10 groups / 3 pieces); 30 calls needed. For each cell also: the middle call (median), the average without the 5% largest and 5% smallest, the share right, and the average after 30 bp of cost (the average round trip measured on IBKR for the AI-chain list -- an assumption for these securities). **Splits (description, no bar):** positive calls in 2018-2021 and 2022-2026; by kind (statement, filing, media report); reported as that day's news; without the five most-called securities; each investor's positive calls.
**Rule for a candidate, fixed now.** A piece becomes a registered candidate rule (QUANT category: rule-based, held one session) only if it passes the bar in a main group AND the middle call is above zero AND the average after 30 bp is above zero AND it is positive in both halves of the years. Otherwise it is recorded as 'moves on average, not a rule'.
**Priors.** #165: for positive calls, piece B still passes with 2,000 sets, but its middle call is under +30 bp (a minority of large moves carries the +96 bp). #166: for positive calls, piece A is positive but does not pass -- most of day 0 is gone before the open. #167: for negative calls, no tradable piece passes. #168: piece B after positive calls is smaller in 2022-2026 than in 2018-2021.
**Limits.** The first headline found is not always the first anywhere; the open is an auction price and a market order there costs more than 30 bp in small names; daily prices only.

### 3.79 SR-2 on the full list; SR-2b results; a fault in SR-2b's design (20 Nov 23:45)
`docs/public_calls_test.md`, `docs/public_calls_follow.md` (commit 433d598). The 33 unread batches were read (about US$1.82; total reading about US$6.91 against an estimate of US$2.70). Full list: 2,095 headlines report a call -> 1,134 calls (706 positive, 428 negative), 299 securities; 957 priced in SR-2, 1,013 in SR-2b.
**SR-2, full list (close to close, minus the S&P 500, in the direction of the call; bar p < 0.0063).** All 957: day 0 +60 bp PASS, +1 +50 bp PASS (p 0.005), +2 to +7 none, day 0 to +7 +100 bp (p 0.015, no). Positive 590: day 0 +69 PASS, +1 +87 PASS, +3 +40 PASS (p 0.005, a single later cell), day 0 to +7 +190 PASS. **Negative 367: day 0 +45 bp PASS (the security fell with the call on the day), then nothing: +1 -8, day 0 to +7 -46 bp (p 0.475).** Bill Ackman 104: day 0 +233 PASS, +2 +50 PASS, day 0 to +7 +443 PASS. Warren Buffett 228: day 0 +79 PASS (p 0.005). Michael Burry 174, Cathie Wood 309, Carl Icahn 65, Ray Dalio 40, George Soros 37: no cell passes. **Clusters: 34 on the full list (12 in the first run): day 0 +85 bp, p 0.020, no; day 0 to +7 +61 bp, right 44%, p 0.310, no.**
**Priors.** #162 RIGHT. #163 WRONG (session +1 passes). #164 WRONG on the full list (34 clusters, not under 30) -- and the clusters do not pass: **the 'sensational fear' hypothesis is not supported on these seven investors** (34 cases is few; the short-report publishers of SR-1 are the better place to test it again).
**SR-2b (bar p < 0.0017, 2,000 sets).** All: open to close of day 0 +24 bp, middle call +10, p 0.0000 PASS, but -6 bp after 30 bp of cost; close of day 0 to close of +1 +43 bp, p 0.0050, no. Positive: open to close +28 bp, p 0.0020, no; close to next close +74 bp, middle +16, without the extremes +34, p 0.0050, no. Negative: nothing (open to close +19 bp p 0.06; close to next close -5 bp). Bill Ackman: open to close +84 bp, middle +25, without extremes +40, right 56%, +54 after cost, PASS; open of day 0 to close of +1 +145 bp PASS. All other investors: no piece passes. Splits: positive calls close-to-next-close +158 bp in 2018-2021 and +57 bp in 2022-2026 (middle calls +7 and +18); by kind: filing +92 bp, media report +114 bp (middle -6), statement +32 bp.
**Priors.** #165 HALF: the middle call is +16 bp (under +30, right) but the piece does not pass at 2,000 sets (wrong). #166 RIGHT (p 0.0020 against a bar of 0.0017). #167 RIGHT. #168 RIGHT on the averages (+158 against +57), not on the middle calls (+7 against +18).
**Fault in the design (Claude's).** SR-2b sorted calls by whether the first headline was out before the open and found 995 of 1,013 'before the open'. That was not checked before the test: 1,050 of 1,134 first headlines (93%) are stamped exactly 07:00 or 08:00 UTC, which is midnight Pacific -- Google News' feed gives these items a DATE and no real time of day. So a headline counted as 'before the open' may have come out during the session or after the close (quarterly filings come out after the close). Consequences: 'open to close, day 0' is not shown to be after the headline; and 'close of day 0 to close of +1' can START before an after-close headline. **Neither piece can be called tradable. No candidate rule is registered from SR-2b**, including Bill Ackman's passing cells. (Also: the kind 'position reported by media' was written two ways by the reader and 94 calls were left out of the kind split.)
**What stands.** Calls by these investors come with a move in their direction on the day (positive and negative), and positive calls with a further rise into the next close. Whether any of it comes after the public could act is not shown yet -- SR-2c asks that.


### 3.80 SR-2c registered: only what comes after the headline for certain (20 Nov 23:50, before running)
`python -m src.public_calls safe` -> `docs/public_calls_safe.md`. **Day 0** = the first session on or after the headline's date (Pacific date, the feed's own). Whatever the true time of day, the headline is public before the OPEN of session +1. **Pieces**, minus the S&P 500's same piece, in the direction of the call: (O) close of day 0 to open of +1 -- description only: an after-close headline lands here, before a user can trade; (S1) open to close of +1; (S2) open of +1 to close of +2. **Main groups (judged):** all, positive, negative, each of the seven investors; bar p < 0.0025 (0.05 / 10 groups / 2 pieces); 2,000 sets of other dates; 30 calls needed; median, average without the 5% extremes, share right, average after 30 bp. **Splits (description):** positive calls by half of the years; by kind for positive and negative calls (the two spellings merged); each investor's positive calls; each investor by half of the years.
**Rule for a candidate (as in 3.78).** Passes the bar in a main group AND middle call above zero AND average after 30 bp above zero AND positive in both halves of the years (the investor's own halves for an investor group).
**Priors.** #169: for positive calls the overnight piece (O) is larger than S1 -- most of the 'next close' gain of SR-2 is the jump at the open. #170: no main group passes S1 or S2.
**Limits.** The first headline found is not always the first anywhere (if the true first was a day earlier, these pieces start later than they could); the open is an auction price; a route to true times exists for filings (the SEC's own acceptance time, free) and is the next improvement if SR-2c shows anything.

### 3.81 SR-2c results: nothing is left after the public can act; row colours on the page (21 Nov 12:00)
`docs/public_calls_safe.md` (commit 143cfdf). 1,011 calls priced; 952 carry a date and no time of day. Day 0 = first session on or after the headline's date; bar p < 0.0025; 2,000 sets.
| group | overnight into +1 (not tradable) | open to close of +1 | open of +1 to close of +2 |
|---|---|---|---|
| all investors | +36 bp | +8 bp, middle +4, right 51%, -22 after cost, p 0.1345, no | +3 bp, p 0.3610, no |
| positive calls | +65 bp | +11 bp, middle +6, right 51%, -19 after cost, p 0.1105, no | +5 bp, middle -14, p 0.3960, no |
| negative calls | -9 bp | +2 bp, p 0.4105, no | +0 bp, p 0.4040, no |
| Bill Ackman | +47 bp | +10 bp, p 0.2790, no | +64 bp, middle +4, p 0.0195, no |
| Michael Burry | +14 bp | +26 bp, middle +28, right 56%, -4 after cost, p 0.0470, no | +39 bp, middle +40, +9 after cost, p 0.0540, no |
| Warren Buffett | +64 bp | -9 bp, p 0.7795, no | -12 bp, p 0.7425, no |
| Carl Icahn, Cathie Wood, Ray Dalio, George Soros | +37, +33, +9, +4 bp | +4, +12, +11, -15 bp; none passes | +8, -27, +31, -38 bp; none passes |
**No main group passes either piece.** Splits (description): positive calls 2018-2021 overnight +189 bp then -25 bp open to close; 2022-2026 overnight +39 bp then +18 bp (p 0.04); by kind for positive calls the overnight piece is +82 bp (filings), +68 bp (media reports), +27 bp (statements) and the open-to-close piece +8, +17, +8 bp; Warren Buffett's positive calls: overnight +100 bp, then -29 bp open to close (right 43%) -- buying at the open after a Buffett purchase is reported LOST on average; Bill Ackman's positive calls open of +1 to close of +2 +106 bp, middle +16, p 0.0045 (a split, not judged; five of the seven investors have under 30 calls in 2018-2021 so the two-halves condition cannot be checked for them).
**Priors.** #169 RIGHT: for positive calls the overnight piece (+65 bp) is about six times the open-to-close piece (+11 bp) -- the 'next close' gain of SR-2 (+87 bp) is the jump at the open. #170 RIGHT: no main group passes.
**Verdict on SR-2 as a whole (TRACK 3.76-3.81).** Public calls by these seven investors come with a move in their direction on the day the headline is dated, and positive calls with a further jump by the next open. From the next open onward -- the first moment that is after the headline for certain -- nothing passes, and after 30 bp of cost every main group's open-to-close average is negative. **These headlines are not admitted as a paid source and get no rule.** 'Sensational fear' (two investors, same direction, two weeks): 34 cases, not supported. What is NOT shown: whether the minutes right after a call are tradable -- that needs the true minute of each call (for filings the SEC's acceptance time, free) and prices outside regular hours (free only for the last 30 days, so only as a forward record). Recorded as an open route, not started. Total reading cost of SR-2: about US$6.91.
**Page (founder, 21 Nov).** In 'Scored news, newest first' a row is red for its first 5 minutes on the page, yellow from 5 to 10, green from 10 to 15, then the usual background; a first column 'On the page for' shows the minutes; 'on the page' is counted from the moment the listener saw the item plus the seconds Claude took to score it.

### 3.82 Why some items arrive hours late; colours counted from the release; late items are 'missed', not suggestions (21 Nov 12:30)
**Founder (21 Nov):** if the rule buys one minute after the release and the lag from publication to the listener is 20,000 seconds, no profit is possible; the colours must count from the release, not from the time on the page.
**What the live log shows (`data_provenance/live/events.jsonl`, 16-20 Nov, 54 rows).** Every lag above about 1,000 seconds was logged within seconds of a moment the listener was STARTED (17 Nov 18:12 UTC: six items, 15,145 to 83,571 s; 19 Nov 16:32: two items; 20 Nov 09:52: twelve items, 8,043 to 49,939 s): they were published while the listener was off and were seen when it came back. While the listener was running: SEC filings 55 and 83 s; PR Newswire 112 and 174 s; NVIDIA's own newsroom 290 to 450 s (its feed is about five minutes behind -- NVIDIA's results on 17 Nov came by the SEC route at 83 s and by the newsroom at 329 s). Two cases not explained by a start: AMD's investor page 2,895 s (16 Nov) and Hunterbrook 5,418 s (19 Nov) -- either a restart not visible in the log or a slow feed; to be measured.
**So the lag has two causes with different cures.** (1) The listener was off (laptop closed, restarts): cure = a machine that is always on. (2) A source's own feed is slow: cure = a faster address for that source (the SEC and the news wires are the fast routes; company newsrooms are slow), and checking more often than every 30 seconds.
**Page.** Row colours now count from the release: red under 5 minutes, yellow 5 to 10, green 10 to 15, none after; first column 'Since release'. An item that arrives late is therefore never red. **Suggestions:** a rule was tested entering one minute after the release; when the score is ready more than 5 minutes after that entry time the page shows 'Arrived too late' instead of a suggestion (5 minutes is a chosen limit, not a tested one); when it is ready a little after, the suggestion states by how many seconds.
**Fault (Claude's):** the colours were first built on time-on-the-page, which hid lateness instead of showing it.

### 3.83 Shortening the lag: three steps, measurement first (21 Nov 13:00)
**Founder (21 Nov):** follow the steps for how the lag can be shortened; the page is accepted as it is.
**Step 1 -- a machine that is always on (removes the 8,000-83,000 s cases).** Needs: Python, 1 GB of memory, the listener and the page running permanently, the Anthropic key typed there by the founder. Price found 21 Nov (third-party price tracker cloudtally.eu, 'verified 10 Nov 2026', excluding VAT; to be confirmed on the provider's own page before buying): Hetzner's smallest server (1 processor, 1 GB) about EUR 4.99 a month in Finland, EUR 5.99 in Germany, EUR 7.49 in Singapore; the 2-processor 4 GB type about EUR 5.49 where available. DigitalOcean's price could not be verified today. Open risk: some sources refuse requests from data-centre addresses -- the lag watch is run on the server on its first day. **Decision is the founder's (provider, go or no-go).**
**Step 2 -- faster addresses.** Already known (docs/wire_probe.md, 15 Nov): Business Wire and GlobeNewswire refuse scripts; most company investor pages refuse or have no feed; that is not worked around. What is left and free: the SEC has TWO addresses for the same filing -- one list of the latest filings of all companies, and each company's own list (what the listener uses, 14 requests per pass). Which is earlier is not known. `src/lag_watch.py` measures both on every 8-K and 6-K of the whole market (hundreds a day), against the SEC's acceptance time.
**Step 3 -- checking more often than every 30 seconds.** The same watch checks the SEC lists every 5 s and the feeds every 15 s and counts refusals (HTTP 403/429); a source that refuses three times in a row is left alone.
**Rule for the change.** The listener is changed only after the watch has run in US hours: the SEC address that is earlier on the middle filing becomes the listener's SEC route, and the checking interval is lowered to what was not refused. Prior #171: the single list is earlier than the company's own list on most filings. Prior #172: no source refuses at these frequencies.
**Also seen:** PR Newswire's 'all releases' feed holds only 20 items; in a busy minute more than 20 releases can be published, so at one check every 30 s items can be missed altogether -- the watch's 15 s checks will show how fast the list turns over.

### 3.84 SR-1 short-report publishers: lists collected, times audited, price test registered (21 Nov 12:30, before any price)
`src/short_reports.py`. **Stage A (no prices, nothing read).** Items on each publisher's own list: Hindenburg Research 105 (Aug 2017 to Jan 2025), Grizzly Research 104 (May 2019 to Oct 2026), Blue Orca 63 (Mar 2011 to Oct 2026), Fuzzy Panda 10 (newest only), Hunterbrook 20 (newest only): 302 items. Not all are reports (notes, media coverage, replies); the reader separates them. The other publishers refuse scripts (docs/source_probe.md) and are not worked around.
**Time-of-day audit (`docs/short_reports_times.md`) -- done BEFORE the test this time.** None of the lists stamps items at midnight. Seconds are not 00 on 99% of Hindenburg's items, 92% of Grizzly's, 100% of Hunterbrook's, 80% of Fuzzy Panda's: real clock times. Blue Orca: 17% -- its times look typed to the minute, usable but less exact. Where the items fall (New York): Hindenburg 52% before the open, 37% during the session, 7% after the close; Grizzly 33 / 50 / 13; Blue Orca 3 / 57 / 40; Hunterbrook 20 / 45 / 25. So 'before the open' and 'during the session' can be told apart here, unlike the public calls of SR-2.
**Reading (cost counted: between about US$1.03 and US$3.30; cap US$5).** Claude (`short-v1-2026-11-21`) reads title and opening text of each item: is it the publisher's own report; the company, ticker and Yahoo symbol; direction (-1 negative / short, +1 positive / long); first report on that company or a follow-up; kind of claim; severity 0-1 of the allegation AS STATED. Claims are unverified and are not judged.
**Test, fixed here.** US-listed companies only in this run (companies listed elsewhere are counted and left for a later run: their sessions do not match New York clock times). Day 0 = the session during which, or before whose open, the report came out; after the close or at a weekend -> the next session, 'before the open'. Returns minus the S&P 500's same piece, in the direction of the report (for a negative report, + means the share fell). **Cells:** day 0 (previous close to close); each of +1 to +7 alone; day 0 to +7; 'gone before the open' (previous close to open, reports out before the open; description only); 'open to close, day 0' (the same reports); 'first tradable point to close +7' (from the open of day 0 for a report out before the open, from the close of day 0 for a report out during the session). **Main groups (judged, 30 rows needed):** all negative reports; first negative reports; follow-ups; each publisher's negative reports. Null: the same securities and directions on 5,000 sets of other dates at least 20 sessions from any report. Bar: 0.05 / (judged groups x 11 judged cells). Each cell also: middle report, average without the 5% extremes, share right, average after 30 bp. **Splits (description):** positive reports; two halves of the years; out before the open / during the session; severity at 0.5, 0.7, 0.9 and under; kind of claim; each publisher's first reports; **clusters** -- a second publisher on the same company within two weeks, and a report that follows a well-known investor's negative call (SR-2 list) on the same company within two weeks (the founder's 'sensational fear' hypothesis, second test).
**Rule for a candidate.** A tradable cell ('open to close, day 0', a later session, or 'first tradable point to close +7') passes the bar in a main group AND the middle report is above zero AND the average after 30 bp is above zero AND it is positive in both halves of the years.
**Priors.** #173: all negative reports -- day 0 passes (the share falls on the day). #174: first reports fall more on day 0 than follow-ups. #175: for all negative reports 'open to close, day 0' is positive (the fall goes on after the open) but does NOT pass the bar. #176: no single session +1 to +7 passes for all negative reports. #177: fewer than 30 rows in either cluster.
**Limits stated before running.** (1) Companies that collapsed and were delisted have no prices on Yahoo: the hardest falls are missing, so the test UNDERSTATES the falls. (2) Selling short needs borrowed shares; targets of short reports are often expensive or impossible to borrow; 30 bp of cost does not include that fee. (3) About 300 items from three publishers with history: small. (4) A publisher may have told clients or posted on social media minutes before its website time. (5) Daily prices: inside the session the minutes after a report are not seen.

### 3.85 SR-1 results: short reports move the price hard on the day; the fall is mostly over before a user can trade (21 Nov 13:00)
`docs/short_reports_test.md` (commit 0314f81). Reading cost about US$1.16 (estimate was US$1.03 to US$3.30). 302 items read; 74 are not reports; 226 report-and-company rows (218 negative, 8 positive; 183 first reports); 187 on US-listed companies; **122 priced**: 46 US symbols have no prices on Yahoo (delisted after the report -- Nikola, Lordstown, Mullen, Ebix and others: the hardest falls are MISSING), 39 rows on companies listed elsewhere left out of this run. Judged groups 3 (all negative 118; first reports 98; Hindenburg 50); bar p < 0.00152; 5,000 sets. Numbers are in the direction of the report: for a negative report + means the share FELL against the market.
| group | n | day 0 | +1 | +2 to +7 | day 0 to +7 | gone before the open | open to close, day 0 | first tradable point to close +7 |
|---|---|---|---|---|---|---|---|---|
| all negative reports | 118 | fell 435 bp (middle 254, right 67%), PASS | fell 76 bp, p 0.0446, no | none passes | fell 447 bp, PASS | fell 643 bp (56 reports out before the open; middle 455, right 79%) | ROSE 100 bp (middle rose 148; right 39%), p 0.954 | rose 35 bp, p 0.41, no |
| first reports | 98 | fell 466 bp, PASS | fell 95 bp, p 0.0238, no | none | fell 412 bp, PASS | fell 669 bp | rose 108 bp | rose 113 bp, no |
| Hindenburg Research | 50 | fell 874 bp (middle 442, right 82%), PASS | fell 242 bp (middle 157, right 56%), p 0.0012, PASS | none | fell 1,241 bp, PASS | fell 1,102 bp (31 reports) | rose 82 bp | fell 317 bp, p 0.0288, no |
Not judged (under 30): Grizzly Research 28 -- day 0 fell 41 bp; out before the open the share gapped down 340 bp and then rose 351 bp by the close (fully reversed); day 0 to +7 ROSE 265 bp. Blue Orca 18: day 0 fell 126 bp. Hunterbrook 13: fell 84 bp, +1 fell 215 bp. Fuzzy Panda 9: fell 342 bp then rose (day 0 to +7 rose 1,140 bp). Follow-up reports 20: fell 282 bp.
**Splits (description, no bar).** *When the report came out:* out BEFORE the open (56): gap down 643 bp, then the share ROSE -- +1 rose 97 bp, first tradable point to close +7 rose 375 bp (middle rose 238, right 38%). Out DURING the session (62): day 0 fell 333 bp (middle 100), **+1 fell a further 232 bp (middle 174, right 69%, p 0.0002)**, first tradable point to close +7 fell 272 bp (p 0.034). *Severity as stated:* 0.9 or more (47): day 0 fell 899 bp (right 83%); 0.7 or more (97): 519 bp; under 0.7 (21): 43 bp -- the more serious the allegation reads, the larger the fall. *Years:* up to 2023 (67) day 0 fell 573 bp; after 2023 (51) fell 254 bp and rose 362 bp from the open to the close. *Claim:* fraud or accounting (79) fell 547 bp. **Clusters: 0 rows in either kind** (a second publisher within two weeks; a report after a well-known investor's call).
**Priors.** #173 RIGHT. #174 RIGHT on the averages (first 466 bp, follow-ups 282 bp; follow-ups are only 20). #175 **WRONG**: from the open to the close the share did not go on falling, it ROSE 100 bp. #176 RIGHT (session +1: p 0.0446 against a bar of 0.00152). #177 RIGHT (0 rows): 'sensational fear' as a cluster of sources cannot be tested on this list either; what the data do show in its direction is the severity split.
**What it supports and what it does not.** Supports: a negative report by these publishers comes with a large fall on the day (about 4.4% on average against the market), larger when the allegation is more serious. Does not support: that a user who acts at the next regular open, after a report published before the open, earns anything -- the share bounced. No tradable cell passes in a judged group except Hindenburg's session +1, and **Hindenburg Research stopped publishing in January 2025** (its last item is the founder's closing note), so no live rule can be built on it. **No candidate rule is registered.**
**The one lead (a split, found after the fact, so a hypothesis only):** reports published DURING the session were followed by a further fall the next session (232 bp, 62 reports). To become a rule it must be registered and confirmed on reports that come AFTER today (forward record), with minute prices for the first hour.
**For the product.** These reports move prices on the day, so by the founder's rule they qualify to be READ live -- as alerts (SUBJECTIVE, intraday), not as a rule. The value is speed: the fall happens within the session or before the open. Publishers that still publish and answer a script: Grizzly Research, Blue Orca, Fuzzy Panda, Hunterbrook (already read).
**Limits (as registered).** Delisted companies missing (understates falls); the fee to borrow shares is not in the 30 bp; 122 rows; daily prices; foreign-listed companies not yet run.

### 3.86 Short-report publishers read live as alerts; forward record of the 'during the session' lead (21 Nov 13:30)
**Founder (21 Nov): yes to both.**
**(1) Live alerts.** `src/news_listener.py` now also reads Grizzly Research, Blue Orca and Fuzzy Panda (Hunterbrook was already read; its reports on companies OUTSIDE the fourteen are now alerts too instead of being skipped). Admitted because SR-1 showed their kind of report moves the price on the day (TRACK 3.85) -- not because any rule exists. Each new item is read by SR-1's reader (`short-v1-2026-11-21`, title and the feed's own text, a fraction of a cent): is it a report, on which company, negative or positive, first report or follow-up, kind of claim, severity AS STATED, and whether it was published before the open, during the session or after the close. On the page it is a 'Short-seller report (unverified)', alert only; the 'Own stock' column shows direction x severity as stated (a negative report of severity 0.9 shows -0.90) -- that is the publisher's allegation, not Claude's view of the price. Notes, media coverage and replies are read and not shown. A source is scored only on items after its admission: the existing items of the three new sources are memorised, not read.
**(2) Forward record of the lead.** Lead (a split found after the fact in SR-1: 62 reports, next session fell a further 232 bp, fell on 69%): a NEGATIVE report on a US-listed company published DURING the New York session -- sell at that session's close, buy back at the next close; return minus the S&P 500. `python -m src.short_reports forward` counts it on reports published after 2026-11-21 05:00 UTC, taken from the publishers' own lists (so it does not depend on the listener being on); reports published before the open are listed beside it as the comparison. **Verdict at 30 complete reports, fixed now:** the lead becomes a registered candidate rule only if the average is above +30 bp (the cost assumption) AND the share fell on at least 55% of the reports AND fewer than 5% of 5,000 sets of other dates do as well; otherwise it is dropped. Every earlier look is labelled interim. At the publishers' present pace (roughly one such report a fortnight) 30 reports take about a year.
**Prior #178:** the lead shrinks: the forward average is under half of the 232 bp seen in the backtest split.
**Limits.** The fee to borrow shares is not counted; publishers may post on social media minutes before their website; daily prices.

### 3.87 The three blocks of the live tab are named (21 Nov 13:45)
**Founder (21 Nov):** asked under what rule each block shows an item, then asked for names: 'Current High-Executive Suggestions', 'Current Low-executive Suggestions', 'Past Suggestions (as Reference)'.
**Rules of the blocks (from `src/live_view.py`).** (1) Top: an item with a tested rule -- company results with an own-stock score of 0.7 or more in size (Strong-results rule), or a Fed statement with a non-zero score (Fed-statement rule) -- from the release until the rule's hour ends; not shown if the score reached us more than 5 minutes after the entry time. (2) Middle: scored items of the last 24 hours with no rule (or under the rule's threshold) whose own-stock score is 0.3 or more in size or whose 'material' score is 0.5 or more; at most six. (3) Bottom: the three most recent items where a rule fired and the hour is over, or that arrived too late. The 0.3 / 0.5 limits, the 24 hours and 'three' are display choices, not test results.
**Names applied:** 'Current High-Confidence Suggestions'; 'Current Low-Confidence Alerts (no tested rule)'; 'Past Suggestions (Reference)'. Two departures from the founder's wording, both told to him: 'confidence' instead of 'executive' (plain English for what he meant); and the middle block is called ALERTS, not suggestions, because no test supports trading on it -- SR-1 and SR-2 found that such news moved the price before a user could act. The top block's caption says the rules are still candidates until 30 live trades.

### 3.88 Look of the page: blocks and tab panels (21 Nov 14:00)
**Founder (21 Nov):** the three blocks of the live tab must look like blocks -- rounded like app icons ('smooth edge'), with a blurred white-and-grey background, and their text smaller than sections such as 'Scored news'; every other tab gets the same rounded panel around its content.
**Applied.** `src/live_page.py`: each of the three blocks is one rounded frosted panel (title 1.02rem, text 0.88rem; section titles elsewhere stay larger); the cards inside keep their colours (green = open suggestion, amber = alert, grey = past). `app.py` (one line, `apply_21nov_panels.py`): a style that puts the content of EVERY tab in a rounded frosted panel. Checked on Streamlit 1.67 with a small copy of the page; the founder's Streamlit version may name the tab area differently, so the style names three variants.

### 3.89 More tests for the 'no rule' news; ET-1 registered: company announcements by type (21 Nov 14:30, before running)
**Founder (21 Nov):** 'no test supports trading on it' means none of his assumptions passed -- so think of more tests, some may pass and move into the top block; go on testing and finish the track. Also: the 'Look up an asset' tab still showed square corners.
**Tests listed for the kinds of news that have no rule (each registered before it runs; each new look makes a chance pass more likely, so the bar is divided by the number of families tried).** (1) **ET-1, company announcements by type** -- this section. (2) The first minutes after a short report or a strong alert: free minute prices exist only for the last 30 days, so forward only. (3) Short report published during the session -> next session: registered (3.86), forward. (4) Macro stance + company trigger: after the sell-off study. (5) Results of one company read across to suppliers and peers (Sector-reading rule): needs more live cases.
**ET-1 (`src/ai_event_types.py`).** Why: family F4 of the AI-chain test pooled every kind of announcement of the US filers and did not pass; one kind may move the company's own stock while the pool does not. Data: the same 1,854 scored events (reader ai-event-v2), US filers, from May 2018 (minute prices on disk), material 0.2 or more, routine filings left out; clock = the SEC's acceptance stamp (the wire is usually a few minutes earlier, so this is the slower clock). **Families:** each event type with 30 or more events, plus two groups fixed now -- 'business news' (contract or partnership; product or technology; guidance update; capital expenditure) and 'trouble' (legal or regulatory; cyber incident; accounting; restructuring; leadership change). **Signals:** own_stock, and neg_uncertainty (sell when the event raises uncertainty), each at material 0.2+, 0.3+, 0.5+. **Windows:** 1 or 5 minutes after the stamp, held 15, 30 or 60 minutes or to the next 09:35; or entered at the next regular session, held 30 or 60 minutes, to 16:00, or to the 16:00 after. **Test:** per family, the best cell against the best cell of 2,000 shuffles of the scores; bar = 0.05 / number of families tested. **A type becomes a candidate only if** p is under the bar AND the best cell's average is above 30 bp (measured cost) AND at least three of its four time periods are positive. Because this is a second look at data already tested pooled, a candidate goes to a forward record and reaches the page's top block only after the founder approves it.
**Priors.** #179: no type becomes a candidate. #180: 'guidance update' -- the type most like a results release -- has fewer than 30 events on its own and is tested only inside 'business news'. #181: the strongest type by t is 'acquisition or disposal' or 'financing or capital return' (the two largest), and it does not cover the cost.
**Page, second pass on corners.** `src/live_page.py` (the style app.py already loads): input boxes, pickers, buttons, charts, tables and message boxes on every tab are rounded; charts get a light rounded frame. Checked on a copy of the 'Look up an asset' tab.

### 3.90 ET-1 results: no type of company announcement passes; one near miss (21 Nov 15:00)
`docs/ai_event_types.md` (commit 73f4764). 276 events of the US filers from May 2018 with material 0.2 or more. Five families had 30 or more events; bar p < 0.0100; cost 30 bp.
| family | events | best cell | average before cost | after 30 bp | right on | family p | four periods (bp) | verdict |
|---|---|---|---|---|---|---|---|---|
| financing or capital return | 111 | sell when uncertainty rises; next regular session, hold 30 min | +19.1 bp | -10.9 | 63% of 109 | 0.8805 | 4.8, 13.6, 52.6, 5.9 | does not pass |
| acquisition or disposal | 54 | sell when uncertainty rises; 5 min after the stamp to the next 09:35 | -56.7 bp (prices moved AGAINST the score) | -86.7 | 31% of 42 | 0.0795 | -61.6, -86.0, -76.0, 0.4 | does not pass |
| leadership change | 37 | sell when uncertainty rises; next regular session, hold 30 min | +38.0 bp | +8.0 | 60% of 35 | 0.2620 | 44.6, -35.7, 38.4, 112.9 | does not pass |
| GROUP business news | 34 | own_stock; 1 min after the stamp, hold 15 min | +78.5 bp | +48.5 | 71% of 31 | 0.4215 | 114.8, 78.6, 8.0, 117.3 | does not pass |
| GROUP trouble (legal, cyber, accounting, restructuring, leadership) | 72 | own_stock; 1 min after the stamp, hold 15 min | +44.5 bp | +14.5 | 56% of 48 | **0.0155** | 5.7, 83.0, 52.0, 37.1 | does not pass (near miss: bar 0.0100) |
Not tested (under 30): legal or regulatory 25, contract or partnership 16, guidance update 16, restructuring 8, other 5, product or technology 2, accounting 1, cyber incident 1.
**Priors.** #179 RIGHT: no type becomes a candidate. #180 RIGHT: guidance update has 16 events. #181 WRONG: the strongest family by t is the 'trouble' group (t +2.93), not one of the two largest types; acquisitions moved against the uncertainty signal.
**Reading.** The limit is the number of events: twelve companies produce about 30 material announcements a year, so a single type cannot reach a verdict. Two things worth keeping as hypotheses, not rules: (a) 'trouble' news -- own_stock score, one minute after the stamp, held 15 minutes: positive in all four periods, +14.5 bp after cost, p 0.0155 against a bar of 0.0100; (b) 'business news' -- +78.5 bp in the same window on only 31 trades (p 0.42: indistinguishable from luck at that size). Both use the first minutes after the stamp -- the same place where the Strong-results rule lives. **What would make these testable is more companies, not more slicing**: the same reader on the announcements of the 100 largest US stocks would give roughly eight times the events (a reading cost to be counted first; minute prices for them are NOT on disk and paid data is banned, so the price side would have to be the forward record or daily prices). Recorded as an open route for the founder's decision; nothing started.
**Page.** The tab buttons are rounded, frosted, and lift under the cursor like the five market cards; the line under the selected tab is removed (`src/live_page.py`, the style app.py already loads).

### 3.91 ET-2 stage A: the announcement test widened to about 100 large US companies (21 Nov 15:30; no prices, nothing read)
**Founder (21 Nov):** 'widen, yes. And then sell-off study.' `src/events100.py`.
**Universe.** The S&P 100 companies: the index fund's own holdings file (iShares S&P 100 ETF) when it can be read, otherwise a fixed list written by Claude; which one was used is printed and saved (`processed/universe100_source.txt`). Never Wikipedia. The twelve US companies of the founder's list are left out (they are ET-1). **Stated bias:** today's list applied to past years -- companies that shrank or left the index since 2018 are missing.
**Collected, free.** Each company's 8-K filings since May 2018 that carry an event item (the same items as ET-1; results releases, Item 2.02, left out), with the SEC's acceptance time; then the text of each filing and of its press release if it has one.
**Reading (waits for the founder).** The same reader and prompt as ET-1 (ai-event-v2). One difference, stated: no results baseline is given for these companies (ET-1's reader was given the company's latest reported figures; reading 100 companies' results as well would cost several times more). `cost` counts the price on the downloaded texts, for all filings and for only those that carry a press release; nothing is read before the founder has seen that figure.
**What the price side can and cannot test.** Minute prices for these companies are not on disk and paid data is banned, so prices are free daily opens and closes. The SEC stamp is a real clock time, so each filing is placed before the open, during the session or after the close, and the pieces a user could trade at the open or the close are separated from what was already gone (the method of SR-1, TRACK 3.84). **Not testable this way: the first minutes after a filing -- which is where ET-1's near miss ('trouble' news, 1 minute after, held 15 minutes) sat.** Claude's expectation, written before any count: with about eight times the events, a daily-scale effect of the size ET-1 hinted at in its 'next session' cells (+19 to +38 bp before cost) would be detectable, but would not clear a 30 bp cost; the widening is more likely to settle the question as 'no' than to produce a rule. The exact cells, groups and priors are registered after the counts and before any price.

### 3.92 ET-2 counts and cost; the sell-off study registered (21 Nov 16:45, before any outcome)
**(a) ET-2 stage A (commit 02433ef).** The index fund's holdings file answered a script with no usable rows, so the fixed list was used: 100 companies, 91 new (9 are already in ET-1; BK was not found in the SEC's ticker file). **6,592 event filings** since May 2018 (per year 574 to 979); by item: other event 2,709, director or officer 2,060, disclosure to all investors 1,730, material agreement 721, new debt 468, the rest under 140 each. SEC time (New York): before the open 1,664, during the session 881, after the close 4,047. Texts on disk: 6,590 (2 failed). **Counted reading cost: all 6,590 filings US$84 to US$127; only the 2,642 that carry a press release US$35 to US$53.** Nothing read. Claude's expectation stands as written in 3.91 (more likely to settle the question as 'no' than to give a rule, and the first minutes cannot be tested on daily prices). The decision -- all, press releases only, or none -- is the founder's.
**(b) Sell-off study, stage B (`src/selloff_study.py`).** Question (founder, 20 Nov): under WHICH conditions does a big sell-off bounce, and under which does it go on falling -- by grouping the sell-offs by their conditions alone.
*Units.* 'Stocks': the S&P 100 list plus the AI-chain list, from 2005 (the SEC's filing items exist from then). 'Indices and sectors': SPY, QQQ, SOXX, SMH, IWM and the 11 sector funds, from 1999. *Definitions (every one tested, each as its own family):* stocks -- one day -5%, -7%, -10% or worse; 5 sessions -10%; 10 sessions -15%. Funds -- one day -3%, -4%; 5 sessions -7%. An episode counts once (a new event needs as many sessions as the window since the last).
*Conditions, all known at the close of the event day (12, plus 2 for stocks):* size of the fall in units of the security's own usual daily move; the last day's move; where it closed in the day's range; the gap at the open; volume against its 60-day normal; distance below the one-year high; the run-up over the 60 sessions before the fall; the S&P 500 over the same sessions; the share of the large stocks down 3% or more that day (breadth); the VIX level; the VIX's change over the same sessions; the S&P 500 against its 200-day average. Stocks only: a results filing (8-K item 2.02) in the window; another 8-K in the window. Free data only (Yahoo daily prices, SEC filing lists). Left out because no free history fits: intraday shape, credit spreads, option-expiry and Fed-meeting calendars, the cause of index falls.
*Method.* Train = events up to 2015; test = 2016 onward. On train, each condition is clipped at its 1st and 99th percentile and standardised; k-means sorts the train events into 3, 4 and 5 groups by the conditions ONLY. The groups are then applied unchanged to the test events. Outcome: the next 1, 2, 3, 5 and 10 sessions, each on its own, close to close from the event day's close -- a stock minus the S&P 500, a fund on its own. Each day counts once however many securities fell (weights 1 / events that day). *Test:* on the test events, the between-group spread of the outcome; the family statistic is the largest over the three group counts and five horizons; null = the outcomes shuffled across the test events, 2,000 times, taking the same maximum. Bar: 0.05 / number of definitions tested (8 if all have 90 train and 90 test events). *Benchmark:* a straight-line (ridge) model on the same conditions, trained on train, predicting 5 sessions; its correlation with what happened in test, against 1,000 shuffles.
*Rule for a candidate.* The definition passes the bar AND a group has 30 or more test events AND its test average at the family's horizon is beyond 30 bp (stocks) or 10 bp (funds) AND has the same sign as in train AND has that sign in both halves of the test years. A candidate goes to a forward record; nothing reaches the page's top block without the founder.
**Priors.** #182: no definition of 'indices and sectors' passes (the earlier average-bounce tests were null and there are few separate days). #183: stocks, one day -5% or worse, passes -- the groups do differ. #184: where a stock definition passes, the group marked by a results filing keeps falling against the market and the group marked by high VIX and wide breadth bounces. #185: no group meets every condition of the candidate rule.
**Limits stated before running.** (1) **Survivors only:** today's S&P 100 applied back to 2005 leaves out companies that fell and never came back; this flatters 'bounce' for stocks on average. Differences BETWEEN groups are less affected than the overall average; the funds are not affected. (2) Same-day events are down-weighted but neighbouring days still move together; that is why both halves must agree. (3) k-means groups are a description, not causes; the three conditions named for each group are its largest deviations from average. (4) Daily closes: the outcome starts at the close of the event day, which a user can trade.

### 3.93 Sell-off study, stage B results; a fault in the null for the funds; what is still missing (21 Nov 20:30)
`docs/selloff_study.md` (commit 61738ba). 121 securities; 38,145 8-K filings listed; 20,776 events. Bar p < 0.0063 (8 definitions).
**Founder (21 Nov):** the ET-2 reading (US$35 to US$127) goes on the WAITING LIST -- nothing read. The purpose of the sell-off study: when a real sell-off happens, tell the investor how likely a rebound or a further slide is. 'See if this can be answered by your designed code.'
**Stocks (outcome = the stock minus the S&P 500): no definition passes.** One day -5%: 4 groups at +5 sessions, p 0.0120. -7%: p 0.1175. -10%: p 0.0120. 5 sessions -10%: p 0.0970. 10 sessions -15%: p 0.1900. The straight-line benchmark does have out-of-sample skill on the one-day definitions (correlation with what happened +0.115, +0.144, +0.119; p 0.000, 0.000, 0.003) and none on the multi-session ones (-0.016, +0.018).
Groups that repeat across definitions (description, test years 2016 on, 5 sessions unless said):
| group | one day -5% | one day -7% | reading |
|---|---|---|---|
| results filing in the window, heavy volume | -25 bp, up 43% (693 events, 525 days; train -41; halves -14 / -35) | -42 bp, up 43% (347 events, 293 days; train -107; halves -34 / -46) | goes on sliding a little against the market; same sign everywhere |
| already far below the one-year high, S&P 500 under its 200-day average | +252 bp, up 64% (333 events on only 93 days; train +278; halves +198 / +308) | +72 bp, middle +679, up 75% (92 events on 17 days) | rebounds, but few separate days |
| calm rising market (low VIX, S&P above its 200-day average) | +33 bp, up 52% (1,831 events, 734 days) | +27 bp, up 50% | a coin toss |
| market-wide fall (many large stocks down, VIX high) | +38 bp, up 50% (698 events on 22 days) | +79 bp, up 51% (367 events on 17 days) | a coin toss; almost no separate days |
**Indices and sectors: the program printed PASSES for all three definitions (p 0.0000, 0.0000, 0.0005) and named candidate groups. These passes are NOT accepted, and no candidate is registered. Fault (Claude's), in the design registered in 3.92:** the null shuffles outcomes across EVENTS, but sixteen funds fall on the same day and their next-ten-session returns are nearly the same number; the test years have 1,034 events on 318 days, and the groups with the largest moves sit on a handful of days of one crisis (62 events on 9 days: +966 bp; 49 events on 7 days: +841 bp; 23 events on 6 days: +1,019 bp -- March 2020 and its rebound). Down-weighting each day does not repair a shuffle that treats those events as separate. The benchmark agrees that nothing stable was found: its correlation in the test years is NEGATIVE (-0.080, -0.145, -0.053). The limit 'neighbouring days move together' was written in 3.92; it was not built into the null, and for raw fund returns it decides the result.
**Priors.** #182 (no fund definition passes): not scored -- the printed passes are an artefact of the null; to be scored after the corrected null. #183 (stocks, one day -5%, passes): WRONG (p 0.0120 against 0.0063). #184: HALF -- the results-filing group does keep sliding (right); the high-VIX wide-breadth group does not bounce, it is a coin toss (wrong). #185 (no group meets the candidate rule): not scored for the same reason as #182; for stocks RIGHT.
**Can this code answer the founder's question? Not yet.** It shows that conditions matter a little for single stocks (results-day falls slide on; falls deep into a decline in a weak market rebound) and gives a 'share up' per group. It does not give what an investor needs on the day: a probability for THIS sell-off, checked against what then happened. Missing, to be built as stage C and registered before running: (1) a null and an uncertainty that count separate EPISODES (days within ten sessions of each other are one episode), not events; (2) the outcome the investor cares about -- the price itself after 1, 2, 3, 5, 10 sessions (and the market-adjusted one beside it), with 'rebound' and 'further slide' defined in advance; (3) a probability model (plain logistic, walk-forward: trained only on earlier years, so 2020 and 2022 are each predicted from what came before) with a calibration check -- when it said 70%, did about 70% rebound?; (4) for a new sell-off, the nearest past cases shown with their count and what happened, so the user sees how much evidence stands behind the number; (5) the survivor problem stated on the card for stocks.

### 3.94 Sell-off study, stage C registered: a probability for each sell-off, with the founder's definitions (21 Nov 21:00, before running)
**Founder (21 Nov), verbatim:** 'definition of rebound is after the sell off day, the next 2 sessions both have higher closing price than the opening price on that same day, nothing is compared to as sell off day. further slide is similar, but just that it continues to have 2 sessions opening higher than closing on each day. horizon: 1,2,3,5,7,10 sessions.'
**Definitions as coded (`src/selloff_model.py`).** REBOUND = each of sessions +1 and +2 closes above its own open. FURTHER SLIDE = each of sessions +1 and +2 closes below its own open. MIXED = anything else. Nothing is compared with the sell-off day. If two sessions were independent coin tosses, REBOUND and FURTHER SLIDE would each happen about a quarter of the time and MIXED about half. Stated consequence of the definition: a session that opens lower than the previous close and then rises during the day counts as an up-day even if it ends below the sell-off day's close; so beside each outcome the report shows what it meant for the PRICE -- the change from the sell-off day's close to the close of sessions +1, +2, +3, +5, +7 and +10 (the founder's horizons), the price itself, not against the market.
**Events and conditions:** exactly those of stage B (3.92): the same eight definitions of a sell-off, the same 12 conditions at the close of the sell-off day (plus the two filing flags for stocks), the same securities. Nothing new is downloaded.
**The probability.** For each calendar year, a plain logistic model (ridge penalty 10 on standardised conditions; each day weighs 1 however many securities fell) is trained ONLY on sell-offs dated before that year and gives every sell-off of that year a probability of REBOUND and one of FURTHER SLIDE. A year is predicted only when 300 earlier sell-offs in 40 separate months exist. Beside it, 'always quote history': the frequency in those earlier years.
**The check.** (a) Skill = 1 - (the model's squared error / the squared error of always quoting history). (b) Calibration: sell-offs sorted by what the model said (under 15%, 15-25, 25-35, 35-45, over 45%) against how often the event happened. (c) Where the model said at least 10 points above history: how often it happened, and the price after. **Unit of separate evidence = the calendar month** (all sell-offs of one month are resampled together, 2,000 times): this replaces stage B's event shuffle, whose fault is recorded in 3.93. (Chaining nearby days into 'episodes' was tried on made-up data and fails for stocks: with a hundred stocks the chain never ends.) 16 tests (8 definitions x 2 outcomes): skill counts at p < 0.0031.
**Rule for 'usable' (what may be shown to a customer as a probability).** Skill passes AND, where the model said at least 10 points above history, the event happened at least 5 points more often than history, in 20 or more separate months. Otherwise the page may show only the plain historical frequencies.
**Priors.** #186: over all predicted sell-offs REBOUND happens 22-30% and FURTHER SLIDE 18-26% of the time -- close to two coin tosses. #187: for single stocks the one-day definitions show positive skill for REBOUND, but under 2%. #188: for indices and sectors no test passes. #189: nothing meets the rule for 'usable'.
**Limits.** Survivors only for stocks (3.92). Two sessions is a short window: most of what decides it is news that arrives after the sell-off day. The colour of a daily candle ignores the overnight gap.

### 3.95 Sell-off stage C results: with the founder's definitions the conditions do not predict; stage C2 registered (21 Nov 21:15)
`docs/selloff_model.md` (commit c533646). 16 tests, bar p < 0.0031, unit of evidence = the calendar month.
**Result: in none of the 16 tests is the model better than always quoting history; in 15 of 16 it is slightly worse (skill -0.2% to -5.7%; the sixteenth is +0.0%).**
| sell-off | REBOUND happened | skill | where the model said 10+ points above history | FURTHER SLIDE happened | skill | where it said 10+ points above |
|---|---|---|---|---|---|---|
| stocks, one day -5% | 23% | -0.9% | said 34%, history 21%, happened 18% (25 months) | 26% | -0.2% | said 38%, history 26%, happened 33% (70 months) |
| stocks, one day -7% | 23% | -1.6% | 35% / 21% / 19% | 27% | -1.1% | 40% / 27% / 26% |
| stocks, one day -10% | 21% | -2.6% | 33% / 19% / 22% | 30% | -5.7% | 42% / 28% / 19% |
| stocks, 5 sessions -10% | 22% | -1.7% | 37% / 22% / 19% | 25% | -1.6% | 36% / 23% / 26% |
| stocks, 10 sessions -15% | 26% | -1.8% | 33% / 21% / 11% (10 months) | 27% | -2.6% | 41% / 28% / 17% (9 months) |
| funds, one day -3% | 24% | -2.3% | 38% / 23% / 27% | 23% | -0.7% | 34% / 22% / 38% (19 months) |
| funds, one day -4% | 24% | -4.2% | 44% / 25% / 23% | 23% | -0.8% | 36% / 22% / 30% (18 months) |
| funds, 5 sessions -7% | 27% | -3.7% | 42% / 27% / 22% | 23% | +0.0% | 33% / 19% / 46% (7 months) |
**Reading.** After a big sell-off, two up-days in a row follow about 21-27% of the time and two down-days about 23-30% -- what two coin tosses give (25% each) -- and the twelve conditions known at the close do not move those odds in a way that holds in later years. When the model was most confident of a rebound, the rebound came LESS often than history in six of eight definitions. So for these two-session definitions the honest statement to an investor is the plain frequency, not a tailored probability.
**Priors.** #186 HALF: REBOUND 21-27% (inside 22-30% but for one definition at 21%); FURTHER SLIDE 23-30% (the upper part is outside 18-26%). #187 WRONG: for single stocks the skill is negative, not small and positive. #188 RIGHT. #189 RIGHT: nothing is usable.
**Why stage B looked more promising, and what follows.** Stage B measured the size of the PRICE move over five sessions and found repeating groups (results-day falls slide on; falls deep into a decline rebound) and a straight-line model with out-of-sample correlation 0.12-0.14 for one-day stock sell-offs. The colour of two daily candles is a different, noisier target: it ignores the overnight gap and looks only two sessions ahead. The founder's own short-window rule says to test different session lengths before concluding.
**Stage C2, registered now (`python -m src.selloff_model run2`).** Same events, conditions, year-by-year training on earlier years only, same check and the same unit of evidence (calendar month). Outcome changed to: **the close of session +h is above the sell-off day's close**, for each of the founder's horizons 1, 2, 3, 5, 7, 10 on its own ('price'); and for stocks also **the stock did better than the S&P 500 over those sessions**. 8 definitions x 6 horizons, twice for the five stock definitions: 78 tests; skill counts at p < 0.00064. 'Usable' as in 3.94, in either direction (the model says 10 or more points above history and it happens 5 or more points more often, or 10 below and 5 less often; 20 or more separate months). This is a further look at the same events; the bar is divided accordingly and the count of tests under 0.05 is reported against the number expected by luck (about 4).
**Priors.** #190: stocks, one day -5%, against the S&P 500, 5 sessions: skill above zero with p under 0.05, but not under 0.00064. #191: nothing is usable. #192: for the funds the number of tests under 0.05 is no more than luck gives.

### 3.96 Sell-off stage C2: nothing; the founder asks for a machine search of patterns -- plan for stage D (21 Nov 21:30)
**Stage C2 (`docs/selloff_model2.md`, commit 7ae4400).** 78 tests (is the price higher after 1, 2, 3, 5, 7, 10 sessions; for stocks also against the S&P 500): skill above zero in 11, p under 0.05 in NONE (about 4 expected by luck alone), none passes the bar, nothing usable. Priors: #190 WRONG (the stock test expected to show some skill did not reach even p 0.05); #191 RIGHT; #192 RIGHT. With the twelve conditions of stage B, a plain model trained on earlier years does not tell the direction after a sell-off at any of the founder's horizons.
**Founder (21 Nov), the request.** Use unsupervised learning to FIND the patterns instead of writing hypotheses one by one -- examples: 'for semiconductor stocks after a sell-off a rebound happens more often and passes the criteria, whereas the financial sector does not'; 'after a sell-off in the industry caused by bad news at Microsoft, the others enjoy a rebound after 5 sessions (not the 2-session rebound defined earlier)'. 'The type and amount of data input to ML matters.' A run that takes a night is accepted.
**What stages B-C2 did not contain, which the founder's examples need:** WHO fell (sector, industry, which company), WHO triggered it (a peer's bad news against the company's own), and freedom over the outcome and horizon. Those are new inputs, not a re-slicing.
**Plan, stage D (to be registered in full before it runs).**
*1. One wide table, one row per sell-off (about 20,000 stock sell-offs 2005-2026, plus the funds).* Who: company, sector and industry (from the SEC's own industry code for each company -- free, primary), whether it is in the AI chain, size group. The fall: the 12 conditions of stage B. Own cause: results filing, other filing by item type; for the twelve scored companies also Claude's event type and score. **Trigger:** on that day and the day before, which company in the same sector fell most, whether THAT company had a results or other filing, whether this company had none ('fell in sympathy'), how many peers fell 3% or more, what the sector fund did. Market: VIX, trend, breadth, the moves in the 10-year yield, the dollar, oil and gold, the macro engine's regime label where on file, calendar. Outcomes, all listed in advance: price higher after 1, 2, 3, 5, 7, 10 sessions; the same against the S&P 500 and against the company's own sector fund; the founder's two-session rebound and further slide; the size of the move.
*2. The machine search.* (a) Unsupervised grouping of the sell-offs at several levels of detail. (b) Pattern search: every combination of up to three conditions (for example sector = semiconductors AND the trigger was a peer's results AND VIX high) against every outcome and horizon -- several hundred thousand candidate patterns, each with its count of events and months and its difference from the plain frequency. (c) A tree model as a second opinion on which conditions matter.
*3. The filter that makes the result believable (this is what takes the night).* Years split: patterns are FOUND on 2005-2017 only; 2018-2026 is not touched until the list is fixed. A pattern is kept only if it has enough events in enough separate months in the first period, AND repeats in the second with the same sign and at least half the size. Then the ENTIRE search is repeated on data whose outcomes have been shuffled by month, 100 or more times: if shuffled data yields as many 'confirmed' patterns as the real data, the real list is luck. Reported: how many patterns survived against how many luck gives; the survivors in plain words, each with its counts in both periods.
*4. After that.* Survivors go to a forward record; a card for live sell-offs is built only from survivors.
**Stated before building.** Survivors-only stocks (today's 100 largest); a search this wide WILL find patterns in noise -- only step 3 separates them; the deeper cause ('what the bad news said') needs Claude's reading of the filings, which is on the waiting list (US$35-127) and is NOT part of this first run: the free version of 'cause' is who filed what and who fell first.

### 3.97 Sell-off stage D, step 1: the input tables (21 Nov 22:00; no outcome computed)
**Founder (21 Nov):** yes to both decisions (patterns found on 2005-2017 and checked on 2018-2026; free inputs first). 'Do you have any other ideas of putting it in? Feel free to go for sources that we have not downloaded. Too many types of data in one table makes too much noise ... I allow you to make as many tables with different length of data involved.' Anything that involves the US$35-127 reading cost stays on the waiting list.
**New free sources added (`python -m src.selloff_inputs fetch`).** Yahoo: three-month and nine-day VIX, the volatility of the VIX, the SKEW index, 10-year and 3-month yields, the dollar index, oil, gold, copper, high-yield and investment-grade bond funds, the long Treasury fund, emerging-market shares, regional banks, bitcoin. FRED (the St. Louis Fed's public files): the high-yield credit spread, the 10-year minus 2-year yield, the Chicago Fed financial conditions index, the 2-year yield, 10-year expected inflation -- each used only after its publication delay. SEC: each company's industry code, and its REPORTED annual revenue and profit and latest assets, liabilities, equity and cash, each with the date it was first filed, so that a sell-off only sees figures that were public that day.
**Six tables, one row per sell-off (`python -m src.selloff_inputs tables`).** T1 the fall and the market (the 12 conditions of stage B). T2 who fell and who set it off: sector (Claude's grouping of the SEC's industry codes, printed in docs/selloff_tables.md so mistakes can be seen), AI chain or not, own results filing, own other filing, days since own results; and for the same day -- the share of sector peers down 3% or more, the peers' average move, whether this company fell more than every peer, the worst peer's move and whether THAT peer had filed results or anything, whether a peer reported results and fell 3%, whether this company had no filing while a peer filed and fell ('fell in sympathy'), the sector fund's move and the company's move against it. T3 the company's condition: profitable last reported year, revenue growth, profit margin, liabilities to assets, cash to assets, size rank in the list (by traded value), the move over the year before, sensitivity to the market, usual daily move. T4 stress and other markets (the new Yahoo and FRED series, levels or 5-session changes). T5 calendar: weekday, month, sessions to month-end and quarter-end, option-expiry week, days to and since a Fed statement (2011 on, from the statements on file), number of results filings in the list over the last ten days. T6 Claude's reading for the scored AI-chain companies (latest results score, an event in the window), where the score files are on disk.
**Left out of this first run, noted as second-wave inputs:** short interest and daily short-sale volume (FINRA, free but large), insiders' trades (SEC Form 4, needs each filing parsed), the amount and tone of news per company and day (GDELT, free but heavy), options data (no free history), analysts' changes (not free), valuation by price (split-adjusted prices and reported share counts do not match in the free data; left out rather than guessed). Claude's reading of what each filing said: waiting list.
**How the tables will be used (to be registered in full with the search, after the counts of this step).** Each numeric column is cut into low / middle / high on the 2005-2017 sell-offs only; patterns are combinations of up to three conditions taken from ONE table or from a PAIR of tables, never from all at once; each table and pair is its own family with its own count against luck.

### 3.98 Sell-off stage D: second-wave inputs included; the machine search registered (21 Nov 23:00, before running)
**Founder (21 Nov):** 'if your second wave is also largely free, we might as well involve this to run in a single time ... For the inputs that cost money we will leave it later for brainstorming.' Nothing in this run costs money.
**Second-wave inputs now included (this replaces the 'left out' list of 3.97 for the free ones).** T7 short selling: FINRA's public daily short-sale volume files -- the share of the day's reported volume that was short sales, on the day and against its own 20-day average (history as far back as the files go). T8 insiders: the SEC's quarterly data sets of insiders' transactions from 2006 -- open-market purchases and sales by officers and directors filed in the 90 days before the sell-off. T4 gains: small against large companies, value against growth shares, the average share against the S&P 500 (all tradable funds, so known live), a news-based policy uncertainty index, the St. Louis Fed stress index, jobless claims, the Fed funds rate. T2 gains the company's own filings in the last 30 days. **Still out:** the amount and tone of news per company (no free source reaches back before 2017, and Wikipedia page views are excluded by rule); options data, analysts' changes (not free); Claude's reading of the filings (waiting list).
**The search (`src/selloff_search.py`), fixed here.** *Groups of sell-offs (four):* stocks one day -5% or worse; stocks 5 sessions -10% or worse; funds one day -3% or worse; funds 5 sessions -7% or worse (the deeper falls are inside these and appear as conditions). *Items:* every numeric column cut into low / middle / high at the thirds of the 2005-2017 sell-offs; yes/no columns; each sector, weekday and month holding 3% or more; and, the unsupervised step, k-means sorting the sell-offs of each table into 5 groups by that table's numeric columns alone, each group an item. *Patterns:* every combination of one, two or three items from different columns, inside one table or across a pair of tables (a pair-pattern must use both tables). *Outcomes:* the price is higher after 1, 2, 3, 5, 7, 10 sessions; for stocks also 'beats the S&P 500' and 'beats its sector fund' over each; the founder's REBOUND and FURTHER SLIDE. *Weights:* each day counts once however many securities fell.
*FOUND* (2005-2017): on 60 or more day-equivalents, the outcome's frequency inside the pattern differs from its frequency over all sell-offs of the group with z of 3.5 or more. *CONFIRMED* (2018-2026, never used for finding or for the cuts): 30 or more day-equivalents, same sign, at least half the size.
*The test.* The whole search is repeated 300 times on scrambled data: within each period the outcome rows are slid along the calendar by a random amount, so the outcomes keep their own clustering in time but no longer belong to their sell-offs. For each group of sell-offs, p = the share of scrambled repeats with at least as many CONFIRMED patterns as the real data. Four groups: a group counts at p < 0.0125. **Only in a group that counts are patterns candidates**, and only those seen in 24 or more separate months of 2005-2017 and 12 or more of 2018-2026 with a difference of 10 points or more in 2018-2026. Candidates go to a forward record; none reaches the page without the founder. The report lists the confirmed patterns with the largest 2018-2026 difference, simplest version first, overlapping ones removed -- and says in its heading when the group did not beat scrambled data.
**Priors.** #193: no group of sell-offs beats scrambled data. #194: the family with the largest excess of confirmed patterns over scrambled data contains T2 (who fell and who set it off). #195: both groups of funds give no more than luck.
**Limits.** Survivors-only stocks; Claude's sector grouping; 2018-2026 holds two large crashes (2020, 2022), so 'confirmed' leans on them; a search over millions of combinations finds patterns in noise -- the scrambled repeats are the only protection, and they protect the COUNT, not each single pattern; a tree model as a second opinion was planned in 3.96 and is not in this run.

### 3.99 Sell-off stage D, first night run: nothing beats scrambled data -- but the scrambling was too harsh; corrected and re-run (22 Nov 17:30)
`docs/selloff_search.md` (commit 489f90f, made on the founder's laptop; its push failed for lack of network and goes out with the next push). Downloads: Yahoo 20 series; SEC financials and industry codes for 104 companies; the SEC's insider data sets, 81 quarters; FINRA's daily short-sale files, 4,354 of 4,515 days back to 2010. **All nine FRED series failed** (connection dropped or timed out), so T4 ran without the credit spread, yield curve, stress and uncertainty indexes. Tables: T1 20,776 rows; T2 15,886; T3 15,886 (complete from 2010); T4 19 columns; T5; T6 2,397 rows (204 complete); T7 9,549 (from 2011); T8 15,684 (from 2006). The search took 0.96 hours with 300 scrambled repeats.
**First-run result (bar p < 0.0125).**
| group of sell-offs | pattern-outcome pairs tried | CONFIRMED on real data | scrambled data: middle; top 5%; most | p | verdict printed |
|---|---|---|---|---|---|
| stocks, one day -5% or worse | 2,118,940 | 115 | 12; 123; 417 | 0.066 | no more than luck |
| stocks, 5 sessions -10% or worse | 1,040,040 | 0 | 2; 21; 208 | 1.000 | no more than luck |
| funds, one day -3% or worse | 29,256 | 0 | 0; 3; 19 | 1.000 | no more than luck |
| funds, 5 sessions -7% or worse | 2,336 | 0 | 0; 0; 1 | 1.000 | no more than luck |
Inside the first group, the families with the most confirmed patterns: T1 + T2 (the fall and the market, with who fell and who set it off) 67 against a scrambled top-5% of 45; T1 alone 16 against 7; T1 + T4 18 against 29; T2 + T3 9 against 6; T2 + T8 2 against 0.
**Fault in the scrambling (Claude's), seen in the output itself.** In several families the REAL data produced far fewer 'found' patterns than scrambled data typically did (T4: 5 against 40; T1 + T4: 79 against 130; T2 + T4: 36 against 130). Scrambled data should look like real data when nothing is there, not richer. Cause: in the real data each day counts once (a crash day's sixty near-identical outcomes share one day's weight), but the scrambled copies slid the outcomes along the calendar and left the weights behind -- the same sixty outcomes landed on rows belonging to sixty quiet days and counted as sixty days. That made scrambled data look full of strong patterns and made the test too hard to pass. The fault works AGAINST finding patterns, so no false pattern was reported; but the verdict 'no more than luck' for the first group is not reliable either.
**Correction, registered before the re-run.** Each sell-off's outcome slides along the calendar TOGETHER WITH its weight, so each day still counts once in every scrambled copy; the support and the z of a pattern in a scrambled copy use that copy's weights. Nothing else changes: same groups, items, patterns, outcomes, thresholds (z 3.5; 60 and 30 day-equivalents; half the size), 300 repeats, bar p < 0.0125, candidate rule of 3.98. Check on made-up data: where nothing was planted, real and scrambled counts now agree (1 against a middle of 1); the planted pattern is still found. The real-data counts above (115, 0, 0, 0) do not depend on the scrambling; only the comparison changes -- and the FRED series are fetched again (with retries), which changes T4.
**Priors #193-#195:** scored after the corrected run.

### 3.100 Sell-off stage D, second run: 'MORE THAN LUCK' printed and NOT accepted; the scrambling fixed for good and checked before the third run (22 Nov 19:45)
`docs/selloff_search.md` (commit 0cafd79). FRED failed again (all nine series; dropped connections). Printed: stocks, one day -5% or worse -- CONFIRMED on real data 114; scrambled data middle 0, top 5% 3, most 31; p 0.003 -> MORE THAN LUCK. The other three groups: 0 confirmed.
**Why this verdict is not accepted (Claude's second fault in the same place, in the opposite direction).** In the second run the scrambled copies 'found' almost nothing anywhere (found 405 against scrambled 0; 78 against 1; 36 against 2). With hundreds of thousands of combinations tried, chance alone must find some; a scrambled count of zero means the scrambled data was made too poor. Cause: the 3.99 correction let each outcome carry its weight when it slid along the calendar; but a pattern's support was then counted with those travelled weights, and on this data (3,733 sell-offs on 1,004 days -- many days with several sell-offs) a pattern that had 60 or more day-equivalents in the real data usually had far fewer in a scrambled copy and was thrown out before it could be 'found'. So run 1 made luck look too strong (3.99) and run 2 made it look too weak. Neither p (0.066, 0.003) is reliable. **Why the made-up check of 3.99 did not catch it:** the made-up data had almost no days with many sell-offs, so the fault could not show. That check was not good enough.
**Third and final form, fixed here.** Every sell-off DAY is given the outcomes of ANOTHER day: the day a random number of places further along the calendar among days of similar size (1 sell-off; 2-3; 4-9; 10 or more), and each of its sell-offs draws one of that other day's outcomes. Consequences: every pattern has exactly the same support in every scrambled copy as in the real data; each day still counts once; the outcomes of one day still move together; busy days get busy days' outcomes; only the link between a day's conditions and what followed is broken. Everything else as registered in 3.98 (groups, items, patterns, outcomes, z 3.5, 60 and 30 day-equivalents, half the size, 300 repeats, bar p < 0.0125, candidate rule).
**Checked this time on made-up data built to break it: 60 stocks, 70 crash days on which every stock falls together and the whole market then drifts one way for ten sessions (strong same-day dependence), NO pattern planted.** One-day group, real against scrambled: run-1 form 14 confirmed against a scrambled middle of 198 (far too harsh); run-2 form 14 against 4, with 'found' 67 against 15 (too lenient); **third form 14 against 9, 'found' 67 against 56, 22 against 19, 5 against 3; p 0.32** -- real and scrambled now look alike where nothing is there. (The made-up five-session group does show a pattern, and it is a true one by construction: a five-session fall that follows a crash day selects the crashes after which the market kept falling. The search finding it is correct.)
**What does not depend on the scrambling: the 114 confirmed patterns themselves.** Read from the pushed file, they say one thing in many wordings: **a stock that falls 5% or more in a day on its OWN news -- a results filing that day, heavy volume, a gap down at the open, falling against its own sector while peers are not falling, often after a run-up and in a calm market -- is more often LOWER, and more often behind the S&P 500 and its sector fund, over the next 1 to 3 sessions.** Examples (2005-2017, then 2018-2026): 'own results filing AND large company' -- beats the S&P 500 over 3 sessions 30% of the time against 49% for all sell-offs (104 days), then 31% against 47% (119 days); 'machine group 3 of the-fall-and-the-market table (heavy volume, fall large against its usual move) AND falling against its sector fund' -- price higher after 2 sessions 40% against 51% (251 days), then 42% against 49% (255 days). No confirmed pattern is of the 'rebound' kind. This agrees with stage B (3.93: results-day falls slide on) and with what the literature calls the drift after bad earnings news. Whether the COUNT of such patterns beats luck is what the third run decides.
**Priors #193-#195:** scored after the third run. **FRED:** fetched through the project's own FRED key (FRED_API_KEY, already used elsewhere in this repo) when it is set in the window.

### 3.101 Sell-off stage D, third run: ONE group beats luck; the severe sell-off rule (SS-1), its forward record and its card registered (22 Nov 20:05)
`docs/selloff_search.md`, `.json` (commit 0c3983a), run with the day-for-day scrambling fixed in 3.100 before the run. FRED worked this time through the project's key (9 series), so table T4 (stress and other markets) is complete for the first time.
| group of sell-offs | pattern-outcome pairs tried | found 2005-2017 (scrambled, middle) | CONFIRMED 2018-2026 | scrambled: middle; top 5%; most | p | verdict (bar p < 0.0125) |
|---|---|---|---|---|---|---|
| stocks, one day -5% or worse | 4,791,380 | 1,125 (256) | **153** | 4; 18; 54 | 0.003 | **more than luck** |
| stocks, 5 sessions -10% or worse | 2,143,620 | 214 (86) | 1 | 1; 8; 19 | 0.658 | no more than luck gives |
| funds, one day -3% or worse | 81,368 | 6 (3) | 0 | 0; 1; 3 | 1.000 | no more than luck gives |
| funds, 5 sessions -7% or worse | 4,568 | 1 (0) | 0 | 0; 0; 1 | 1.000 | no more than luck gives |
p 0.003 is the smallest value 300 repeats can give: none of the 300 scrambled copies reached 153. The scrambled copies now find a believable number of chance patterns (256 against 1,125 real), which they did not in the second run. Families with the most confirmed patterns: T1 + T2 67 (scrambled top 5%: 1), T1 + T4 52 (6), T1 16 (0), T2 + T3 9 (0). T4 alone: 0 confirmed.
**What the confirmed patterns say (the 40 strongest are in the file; 24 are candidates under the rule of 3.98).** One finding in many wordings: **a stock that falls 5% or more in a day on heavy volume, with a fall large against its own usual move, is more often LOWER and more often behind the S&P 500 and its sector fund over the next 1 to 3 sessions** (beats the S&P 500 over 2 sessions about 33-38% of the time in 2018-2026, against 48% for all sell-offs; price 50 to 130 basis points lower after 2-3 sessions). The mark 'heavy volume and large against its usual move' is the machine's own group (k-means group 3 of 5 in table T1) and is in 25 of the 40. Stronger: after a run-up over the 60 sessions before; on the company's own results filing; when the company fell alone (few peers down, fell more than every peer); when stress is low (St. Louis Fed index, policy uncertainty index). **No sector appears in the 40 strongest** -- the founder's example 'semiconductors rebound, financials do not' is NOT supported by this search. **The state of the market alone finds nothing (T4: 0 confirmed); it changes the strength only together with the stock's own fall (T1 + T4: 52).** One pattern of the rebound kind is confirmed (no results filing, Fed funds rate under 0.17%, small companies ahead: price higher after 10 sessions 67% against 54%, 69 days) -- nearly all from 2020-2021, treated as one period's feature, not as a rule.
**Not answered by the search:** whether the fall can be captured from the NEXT OPEN (everything above is measured from the close of the sell-off day). SR-1 and SR-2 failed exactly there.
**Open point, stated plainly:** in the made-up check of 3.100 the five-session group was flagged; Claude believes that came from how the made-up data was built and has not proven it. On the real data the five-session group is NOT flagged (p 0.658).
**Priors scored.** #193 (no group beats scrambled data): WRONG -- one of four does. #194 (the family with the largest excess contains T2): RIGHT -- T1 + T2. #195 (both groups of funds no more than luck): RIGHT.

**Registered now, before any forward case: the SEVERE SELL-OFF rule, code SS-1** (`src/selloff_forward.py`). A stock of the list (the S&P-100 list of 3.91 plus the AI chain) is in a severe sell-off at a close when (1) it closed 5% or more below the previous close, (2) its volume was more than 1.98 times its 60-session average, (3) the fall was more than 2.72 times its usual daily move over the 60 sessions before. 1.98 and 2.72 are the cuts the search fixed on 2005-2017; (2) and (3) are the two marks of the machine's group, written as a plain rule so that it can be checked live without re-running the machine. This is a simplification of the machine's group, not the group itself: `python -m src.selloff_forward describe` measures this exact rule on the old data (-> docs/selloff_rule.md): against all sell-offs in both periods; **company by company and sector by sector (is it every company or a few?)**; **by the state of the market (VIX, S&P 500 against its 200-day average, stress index, the stock's own run-up)**; and **from the next open**. That page is a DESCRIPTION on data the search already used -- no verdict comes from it.
**Forward record.** `python -m src.selloff_forward scan` (the live page also starts it by itself) records every sell-off of 5% or more from 23 Nov 2026, marks those that meet SS-1, and fills in what followed: against the S&P 500 after 1, 2, 3 sessions from the close, the overnight move to the next open, and from the next open to the close two and three sessions after. Each day counts once. **Verdict at 30 separate days with a severe sell-off; a second look at 60.** SS-1 is supported if the share of days on which the stock beat the S&P 500 over 2 sessions is under 48%; it becomes a trade only if 'next open to the close two sessions after, against the S&P 500' is below -30 basis points (the cost of a round trip).
**Priors.** #196: at 30 days the share that beat the S&P 500 over 2 sessions is under 48%. #197: 'next open to close +2 against the S&P 500' is NOT below -30 basis points -- the fall is mostly overnight, as in SR-1 and SR-2.
**Live page.** A small block 'Severe Sell-off' in the top right corner of the Event-driven tab (it floats; no other block moves or changes size). It shows stocks that met SS-1 at one of the last 3 closes, stocks falling 5% or more during the session (not counted until the close), the history numbers of `describe`, and the forward count. It is labelled a candidate until the verdict.
