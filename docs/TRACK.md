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

## 4. Potential upgrades — not registered, not costed

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

