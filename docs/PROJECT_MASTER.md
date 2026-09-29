# PROJECT MASTER — the one file
## Regime-Aware Cross-Asset Signal · Hsu Wei-Ting (Steven) · NUS MSc Finance · May–September 2026

*Assembled 21 September 2026. This is the single document to bring to any new conversation.
Part A (sections 0–16) is written so that a reader with no finance background can follow it,
and so that a new conversation knows everything without opening another file. Part B binds the
canonical documents in full — nothing is summarised away there. If you read only one thing, read
Part A. If you need a number, its evidence is in Part B.*

---

## 0. Read me first

**What this file is.** Four months of work — an academic capstone that became a business plan
that became a product-in-progress — in one place, with every idea kept, including the ones that
were tested and did not work. Ideas that failed are recorded with the same care as ideas that
survived, because knowing what does *not* work is most of what this project has produced, and
each one cost hours of thought.

**Authority.** This file supersedes, and embeds in full, these earlier documents:
`roadmap_signal_trees_v2.md` (now v2.2, Appendix B), `MODEL_EVOLUTION.md` (Appendix C),
`POST_SUBMISSION_STATE.md`, `SESSION_HANDOFF.md`, `EXECUTION_PLAN.md`,
`TRACK_report_scoreboard.md` (Appendices G–H, kept for the record), and `briefing.md` (a
concatenation made for a chat session). Three files stay live *beside* this one, each with one
job: `docs/TRACK.md` is the short daily status board (what is running, what to check);
`docs/CURRENT_STATE_2026-08-23.md` is the append-only evidence record (every result, in order,
never rewritten; also Appendix D); `docs/prereg_*.md` and `docs/overlays/*.md` are the
registrations (a test's rules, committed before the test exists). The Learning Journal
(`Learning_Journal.docx`), the Business Plan (`Business_Plan.docx`, Appendix F) and the Pitch
Deck (`Pitch_Deck.pptx`, Appendix E) are the submitted artefacts and are not changed.

**How a new conversation should start.** Read Part A. Then run the checks in section 7. Then
open `TRACK.md` §5 for what happened since this file's change log (section 16) ends. Only then
open Part B for detail. Do not re-derive anything that has a verdict here; do not re-run a test
whose criterion is already recorded without reading its registration first.

**Dates.** Everything is Singapore time unless marked ET. "Session" means a New York Stock
Exchange trading day.

---

## 1. What this project is

### 1.1 For a ten-year-old

Imagine a very careful weather station for money.

Every morning it looks at eight dials about the economy — things like how expensive it is to
borrow, and how much money is around — and decides what kind of "season" the markets are in.
There are four seasons, and the station found them by itself, by looking at twenty years of
dials, not by being told.

Then it reads the day's important letters: what the central bank said, what big companies
announced, what the government ordered. A computer program reads each letter and answers a few
fixed questions: *Is this good or bad for stocks? For bonds? For gold? For the dollar? For oil?
How sure is it? How specific is the letter? How new is what it says?*

Then it looks back through history for days that had the *same season* and the *same kind of
letter*, and asks: what happened next, back then?

And then comes the most important part. If it can find at least eight days in history that
really match, it tells you what usually happened. If it cannot find eight, **it says "I don't
know"** — out loud, in writing — instead of guessing. Most days, for most things, it says
"I don't know." That is not a bug. Most people who sell market predictions never say it, and
that is why this one is different.

Everything it does is written down *before* it does it, so nobody can go back and pretend they
predicted something. And it keeps a list of every time its builder was wrong. That list is at
29 and counting.

### 1.2 For an adult

A regime-aware cross-asset signal framework with a language-model document layer. Eight FRED
macro series → PCA → a four-state Gaussian mixture, refit on an expanding window, gives a daily
monetary regime. Every FOMC statement, FOMC minutes, earnings 8-K, executive order and
proclamation is read by an LLM under one fixed schema (direction on five axes, magnitude,
specificity, novelty, confidence, stance). Historical days matching both the regime and the
document class form a precedent pool; a precision-weighted estimator with an effective-sample-size
floor of 8 produces a conditional estimate or an abstention. Three price-only models run a
frozen forward test since 19 August; a second, report-level scoreboard scores the daily report
itself since 14 September. Every threshold is committed to version control before the code that
uses it; every negative result is published. The commercial form is a research service to
accredited investors under a Singapore exemption, selling a regime label, a document reading,
an explicit precision and a fixed rule for silence — not a return stream.

### 1.3 For an investor, in one paragraph

Every signal vendor outputs a number every day, so a buyer cannot tell which days matter. This
one has a rule, fixed in advance, for when it stays silent, and it publishes what did not work.
For a fiduciary who must justify an allocation to a committee regardless of outcome, a dated
record of what the evidence was — regime, documents, precedents, precision — is the product. It
is early: no customers, no revenue, no counsel opinion, no live performance figure, and the plan
says so on its first page.

---

## 2. The story so far — every week, every idea

*Digest of the Learning Journal (Weeks 1–15) and the post-submission record. Nothing is
omitted that changed a decision; the journal itself is preserved unchanged as a separate
document.*

### Week 1 · 18–22 May · Foundation

- Scope locked: three problems — **P1** does gold decouple from equities in stress (the
  "safe-haven inversion")? **P2** is there a stable rotation order along supply chains (the
  semiconductor chain: design → memory → packaging → power)? **P3** can an LLM turn policy,
  filings and news text into structured features?
- Data plan: prices via yfinance using liquid ETF proxies (GLD, SLV, CPER, USO — not raw
  futures); macro from FRED (real yields, M2, SOFR, EFFR, DXY, spreads); SEC EDGAR for filings;
  the Fed website and FRASER for FOMC text; the Federal Register and BIS/USTR for trade and
  export-control actions; **GDELT** for event detection. Storage as Parquet on disk queried with
  DuckDB (SQLite as fallback). A RAG layer planned: sentence-transformers embeddings with
  ChromaDB or FAISS, LLM via API.
- Design ideas recorded: track GDELT by *theme* (tariffs, export controls, sanctions, military
  action), not by person's name — theme-anchored beats name-anchored for signal quality. Build
  the rotation engine general in architecture but validate on one chain (semiconductors);
  metals and rare earths deferred to the roadmap. Two analytical layers: the named-factor,
  regime-conditional analysis as the academic core; a discovered-factor PCA layer as the product
  differentiator. Survivorship bias of a today's-ticker universe: accepted and documented.
- Concepts learned (Datacamp AI course): vector size as a hyperparameter; emergent embedding
  dimensions; learning rate is step size, not sample size; SGD/momentum/Adam/regularisation;
  supervised vs unsupervised learning; AI team roles; model degradation and re-training.
- Literature anchors: Hamilton 1989 regime switching; HMMs in finance; Baur & Lucey and Baur &
  McDermott on gold; "dash for cash 2020"; Cohen & Frazzini on economic links; Loughran &
  McDonald; FinBERT; Lewis et al. on RAG; Fama–French; Chen–Roll–Ross.
- Engineering notes: exponential backoff (2/4/8 s) for transient fetch failures; log returns
  over simple; never forward-fill a return; reindex then forward-fill macro series.
- Supervisor's recommendation: Bill Aulet's *Disciplined Entrepreneurship* (24 steps).

### Weeks 2–5 · 25 May–21 Jun · The reading weeks

- Week 2: a book on Taiwan's venture-capital ecosystem, to decide the jurisdiction. Findings:
  jurisdiction is a design decision; Taiwanese venture money follows hardware clusters and is
  thin for software-only fintech; "where to set up" cannot be separated from "who is the first
  customer" (DE step 1). Taiwan effectively ruled out later on licensing grounds (SICE).
- Weeks 3–5: a history of central banking. The policy rate is an overnight rate; transmission
  to the long end is expectations-driven; QE, Operation Twist and yield-curve control are the
  named exceptions; an FOMC statement is a document about the *expected path*. This is why the
  reader's schema later separates *stance* (today's decision) from *direction.duration* (what
  the text implies for bond prices). Monetary regimes are discrete, not continuous — the
  justification for a regime engine. The rule adopted for the macro panel: one series per link
  in the transmission chain, not every series FRED offers — which kept the panel to eight.
- Week 5: DE steps 1–3 begun; a list of friends in Singapore and Taiwan with finance backgrounds
  drawn up for problem interviews.
- **The process lesson, stated where it happened:** five reading weeks before the first line of
  code. Every reading was used, but the ordering cost the project its buffer. The
  manufactured-calendar rows, the panel-extension problem and the hard-coded axis would all have
  been found in June had the data pipeline started in Week 1.

### Week 6 · 22–28 Jun · First commit and first customers

- Conversations with friends in finance: a buy/sell signal from an unknown vendor would be
  ignored; **a structured view of *why* an asset moved — regime, factor attribution, what the
  news said — would be read.** This is the origin of the later pivot from prediction to
  explanation and, in September, the reason T13 ranks sources by explanation first.
- 26 June: repository created (commit `79733ee`, "Week 2 Thread 1" — the week count then
  started from the first coding week); cache-first raw fetcher (`e586c7b`). `config.yaml` as the
  single source of truth for every script.

### Week 7 · 29 Jun–5 Jul · Universe and the moat question

- The asset universe designed as three groups by history length: long-history core (must span
  several crises; for regime discovery and backtests), modern-theme overlay (tracked live,
  excluded from backtests), spotlight single names (analysed only within their own history).
  Inception dates for 47 assets entered by hand, several approximate, recorded as such.
- DE step 8, "define your core": the honest answer was "nothing yet" — a regime engine on public
  data is reproducible. This discomfort produced the 18 July email.

### Week 8 · 6–12 Jul · Data lock

- 7 July: 47-asset basket committed (`95878bf`); retry-with-backoff; processed panel builder
  (`5251c0f`). 8 July: methodology evolution log started (`79d30fd`) — the habit of recording
  every change with its reasoning. Email to Dr Lee on company setup (re-raised 18 July).
- Mistake made here, found 18 August: the panel indexed on `pd.bdate_range`, a Monday–Friday
  calendar that includes market holidays — ~196 rows with macro values and no prices entered the
  clustering as near-duplicates. Fixed by the NYSE session calendar; backtest Sharpe fell from
  0.57 to 0.51. **Lower and correct beats higher and wrong.**

### Week 9 · 13–19 Jul · The exclusivity conversation (18 July, Dr Lee)

- Question asked: would institutions demand exclusivity and foreclose retail? Answer, which
  became the commercial thesis: exclusivity is rare for tools and is a signal about a weak
  buyer; **alpha never leaves the house** — everything a vendor sells is a piece of a puzzle;
  reliability versus meaning — a client wants a unique, orthogonal input, not something to rely
  on; the market is not necessarily short-cycled — vendors sell a unique dataset for years; and
  the primary questions come first: who buys, what their pain is, what they pay, whether there
  are enough of them, how to reach them.
- Mistakes corrected: conflating reliability with meaning; assuming exclusivity was desirable;
  worrying about replication before the customer. Precedents: Barra/MSCI, RavenPack.

### Week 10 · 20–26 Jul · Draft business plan

- DE steps 9–14 worked through; Y Combinator's start-up library used for structure. The
  three-stage growth path: research firm → data vendor → classification standard (the regime
  taxonomy itself as the product). The legal question raised: does the product require a
  financial-advisory licence in Singapore?

### Week 11 · 27 Jul–2 Aug · The pivot to risk-management signals

- 28 July email: the draft plan exists; does "pivot from buy/sell signals to risk-management
  signals" resolve the legal issue? The honest answer adopted: only if the product is
  *actually* informational — hence the later guardrails (abstain below the evidence floor; show
  both numbers on disagreement; never issue a combined figure).
- 1 August: exchange-calendar utility with early closes (`912edf0`) — built, then not wired into
  the panel builder for seventeen days (lesson: when a hazard is fixed in one place, grep every
  other consumer in the same commit).

### Week 12 · 3–9 Aug · Pricing and licensing

- 7 August, two emails: a three-tier pricing structure from friends who had founded firms —
  Signal US$29/month (daily regime label, one-line attribution, weekly summary), Analyst
  US$99 (full universe, analog forecasts, LLM queries, CSV), Professional US$299 (intraday
  re-scoring, API, custom watchlists, portfolio decomposition); each tier mapped to a DE
  persona. Licensing compared across Singapore, Hong Kong and Taiwan (SICE); the open question
  whether structured information rather than recommendations falls outside licensing. Report
  format proposed (framework, pipeline, backtest report, MVP demo, 15–20-slide plan, 10-slide
  deck).
- **Reversal that came later:** the 7 August plan led with retail. The MAS framework reversed
  the order — institutional first (no advisory licensing burden), retail last. The tiers
  survived as the eventual structure; the sequencing did not.

### Week 13 · 10–16 Aug · The engineering week

- Six commits in five days: GDELT macro-theme mapping locked (`9b9ea35`, `561af6a`);
  regime–event alignment validation with permutation test and window sweep (`eb09000`); core
  pipeline backfilled (`673ce71`); **panel extended from 2018 to 2006** by dropping SOFR
  (R² 0.998 with EFFR — "extend by removing redundancy, never by imputation"); data-driven
  stress axis (`stress_axis.py`: the PC most correlated with VIX — after a refit moved it from
  PC2 to PC3 and every hard-coded index silently mislabelled); **Problem 1 null** (`4aeba9e`);
  pipeline map and **Problem 2 stage 1 null** (`b6c3ed8`); analog engine with a pre-registered
  three-model grid (`54db141`, 14 Aug).
- Results: safe-haven inversion NULL, robust across windows and transforms — gold co-moves
  slightly *more* in stress, consistent with dash-for-cash; regime count n=4 stands on internal
  structure (seed-stability ARI 1.000, median run 52.5 sessions, best silhouette) but external
  event-alignment on 2024 collapsed (p 0.32) — documentation corrected to "structurally best,
  weakly corroborated externally"; unconditional lead-lag NULL.
- Circularity avoided: a separate liquidity classifier (2-state GMM on correlation breadth and
  realised vol, excluding gold and equity) so the safe-haven test does not condition on a regime
  built from VIX.

### Week 14 · 17–23 Aug · Twenty-seven commits

- 17 Aug: three models frozen in `models.yaml`; forward-test harness; daily logger (`ce18d34`).
  18 Aug: calendar migration to NYSE sessions (`949fb0a`; 5,382 → 5,188 rows; zero-coverage rows
  ~196 → 2); regime count pinned to n=4; window-integrity rule; forward log staleness guard;
  ledger wiped on basis change. **19 Aug: forward test live on the session basis.** 20 Aug:
  GDELT reproducibility gap closed (lost BigQuery query recovered and scripted; the 500-row
  console export cap found; the hard-coded 2024 window found — "caught only because the
  2025–26 run crashed on zero overlap"); GDELT panel 366 → 944 days; the pre-registered GDELT
  test answered NO. 21 Aug: drift-existence pre-registered before its code; chain-rotation
  look-ahead removed; **Problem 2 closed as null**. 22 Aug: cross-asset and sector rotation
  pre-registered. **23 Aug (nineteen commits):** rotation closed at every level; drift-existence
  NULL; PEAD criterion not met (the H=1 positive lived entirely in three hindsight-selected
  names); cross-firm spillover pre-registered — announcer intraday +2.319% (p 0.0002) became
  +0.012% (p 0.976) once entry used only tradeable information, preserved as a demonstration of
  what look-ahead is worth; scheduled macro-event drift pre-registered with a tradeable window;
  recency kernel pre-registered (HL 4y); sources decided (6-K for foreign issuers, Federal
  Register for political); `CURRENT_STATE_2026-08-23.md` written as the single state file; the
  full Problem 3 execution plan (steps 0–7) appended.
- The declared look-ahead in `_z()`: features standardised on full-panel moments — corrected
  rather than defended. The phrase "no look-ahead" retired.
- Mechanism found: **event-initiated rotation, instant propagation** — peers reprice in the
  overnight gap; every earlier test entered at t+2, after propagation was complete. One
  mechanism explaining every prior null.
- An API key pasted into a chat on 23 Aug: revoked; credential files gitignored (`fc6125d`).
- Backtest revised: all-47 Sharpe 0.57 → 0.51 (p 0.0010 then); long-history 35: 0.40 → 0.25.
  The claim "survives dropping recent-inception tickers" retired.
- The wrong-prior tally began: nine.

### Week 15 · 24–28 Aug · The corpus, the estimator, the submission

- 24 Aug: the "no λ exists" claim retracted (λ = 0.0008 had been in `config.yaml` all along —
  half-life 3.44 years; the reported 0.51/0.25 always carried decay); rung-level selection
  diagnostic registered before computation; steps 3–6 pre-registered (precision blend by
  DerSimonian–Laird τ², k estimated never chosen, all three PCs, agreement flag display-only,
  blind-build protocol); the estimator built blind with the event–return correspondence
  destroyed and a known effect planted; six acceptance tests, three repaired after failing.
- 25 Aug: step 1 closed; specificity gate PASS (0.363 at n=60; **0.517 on the full corpus at
  10,000 iterations**); the 8-K corpus discovered to be **307 SEC cover pages** and rebuilt from
  EX-99 exhibits; the corpus read launched and interrupted four times (credit exhaustion twice,
  a cache corrupted by a double launch, a cost estimate wrong three times: $8.91 → $15.94 →
  ~$46); atomic cache writes, a fatal-error classifier, a launch lock; **2,616 of 2,779 documents
  read** under one prompt version and one model; 163 over-cap 6-Ks deferred; 1,674 Federal
  Register proclamations fetched at $0 (other types dropped by a string-match bug, later
  re-fetched: 4,595 documents, unread); `app.py` evidence terminal built.
- Findings from the read audit: the reader separates decision from guidance (six genuine hikes
  read with positive duration, all with softening forward guidance); FOMC statements read at the
  *lowest* novelty — correct, they are the most telegraphed documents in finance; the five macro
  axes cannot represent a sector shock (a steel tariff scores high specificity and near-zero
  direction — schema v2's reason to exist); earnings surprise vs own-equity direction agrees
  431/442; truncated 8-Ks read measurably worse.
- Retired by registered tests: "λ is tie-breaking" (it *reselects* — top-100 overlap 0.765 and
  0.850 against a 0.90 threshold); "the trend advantage" (it *is* the look-ahead: on the expanding
  basis level beats trend by 0.12); "removing λ raises Sharpe 0.25 → 0.38" (p 0.485).
- 26 Aug: **step 3 unblinded — 7 of 45 cells; robustness re-test 1 of 7** (`fomc_minutes`/USO
  at h=5, inside the range expected by chance); FOMC→GLD split FAIL at 4.62×; wrong priors #25/#26
  (a null that ignored overlap). 27 Aug: **agreement test FAIL in the opposite direction**
  (concordant +0.193% vs discordant +0.406%) — label ships display-only; step 5 (§7.2 fixed
  weighting), step 6 (decision report), asset extension, regime profiles; the app rewritten as a
  product (three tabs, plain English, any ticker). 28 Aug: backtest evidence with costs, short
  leg, block-permutation p, family test — all-47 **Sharpe 0.51, p 0.045**; long-history
  **0.25, p 0.184, retired**; best-of-54 grid 0.73 vs null best 0.56, **family p 0.090**;
  break-even 60.6 bp/side; the short leg *lost* +0.169%/week; business plan revised against 19
  supervisor feedback items (41 pages); pitch deck (10 slides); Amendment 4 registered (ESS
  target 12 above the floor of 8, non-retrospective); `daily_run.sh` on launchd; README.
- **Submitted 28 August.** Wrong-prior tally: 26 at submission.

### Post-submission · 29 Aug–21 Sep

- 29 Aug–13 Sep: the nightly document reads were silently dead (a flag that never existed) —
  found on 13 Sep.
- 7 Sep: `TRACK.md` created as the single status file.
- **8 Sep:** Model 4 (long top-5 vs the equal-weight universe) **FAIL** — skill exists, lives
  after 2018, is not survivorship-robust, is "picking momentum names in a momentum market". The
  three-kernel family **NULL** (family p 0.114); **the floor is zero** — regime-only equal
  weighting gives Sharpe 0.04, so the kernel does all the work (wrong prior #28); Model 1 fails
  the chronological split at 3.88× (never checked before); Mahalanobis is the only kernel stable
  across time (2.94×) and still not a finding. FOMC→GLD *by regime* found by looking — gold rises
  after FOMC only in the flat-curve/strong-dollar regime — registered for **forward** testing
  only (first observation 17 Sep, ~two years to a verdict). `MODEL_EVOLUTION.md` written.
  launchd moved to 15:00.
- **13 Sep — harness audit, five commits, no model touched.** (1) Reads dead since 29 Aug:
  `--unread-only` never existed and `--limit` sliced before the cache check; fixed, plus
  `--since 20260827` so deferred sets are never consumed by the nightly cap; `political` added
  to the read loop (the fetcher had been writing to a folder the reader never visited).
  (2) `outputs/reports/` was rewritten nightly by a `--limit 30 --recent 10` regeneration —
  frozen; the nightly job rebuilds the index only. (3) Reports were written a day *early* (the
  panel index runs ahead of the close) — `step6 --latest` now targets the last completed session
  and is write-once. (4) One failed ticker (AMLP, 8 Sep) had aborted a whole run — a failed refresh
  now warns and continues; catch-up entry logs every completed-but-unlogged close with a
  `logged_at` column (forward-test amendment, registered before it could fire). Forward ledger
  verified complete 19 Aug–10 Sep: 16 signal dates × 3 models, no Labor Day row, no duplicates.
  The 28 Aug vendor gap (Close NaN) healed by 4 Sep. The Mac sleeps at 15:00 most days; the 11 Sep
  run was suspended mid-way for ten hours — `caffeinate -is` added to the launchd job.
- **14 Sep — the report-level scoreboard, steps 1–7 in one day, $0.** Registered
  (`docs/prereg_report_scoreboard.md`, `97dd490`): horizons {3, 5, 20} from `unblind_step3.py`,
  primary h*=3 (the estimator's own registered primary), source-expansion tolerance 2 points
  point-estimate and lower bound above −5, revisable only before a comparison runs; seven
  acceptance tests registered then passed on the founder's machine with no repair; first real run
  printed zero coverage and "too few to report" — correct, since every report since 11 Sep is
  deferred; wired into `daily_run.sh` as 6c/7; `build_report`'s precedent pool restricted to
  `session ≤ t − 3` (closes a backfill look-ahead); **the backfill: 1,531 as-of reports under
  corpus hash `986e0d65b6df_n2616`, generated in five minutes, verdict INCONCLUSIVE** — h=3
  non-overlap n=345, hit-rate 59.4% against a within-asset null 95th percentile of 59.1%
  (p 0.0497, met by 0.3 points); asymmetry 1.116 with CI [0.91, 1.40] (not met); SPY carries the
  pooled figure (68% on 171 rows); tier 2 (51.5%) worse than tier 3 (57.5%) — the tiers do not
  grade; `fomc_minutes`-driven calls 37.8% on 74 rows (a hypothesis, registered forward-only on
  15 Sep, 0 of 30 rows); h=5 tradeable 49.5% — no one-week edge at the next open. Coverage
  baseline: the report spoke on 585 of 1,531 document days (38%). A ledger dtype bug found by
  the run, fixed. A deferral guard added: a report is not written while its session has unread
  documents. Backup: the forward ledger force-tracked (it had never been in git), nightly
  commit-and-push (step 8/7), `.env.example` with names only, `tools/make_env_example.py`,
  TRACK §7 restore recipe; a credential scan of the repo and its full history found nothing to
  revoke.
- **15 Sep — the roadmap.** v1 (five trees) → v2 (eleven) → v2.1 (twelve, with four universes
  and Test A/B per tree, T12 regime engine v2) — `docs/roadmap_signal_trees_v2.md` (`a9b019d`).
  The founder's requirements: unique and sellable, not replications; the "affordable LLM" niche
  designed as selectivity rather than cheaper code; regime/vol allocation designed around the
  published erosion (the "Cederburg answer"); prioritise success over reuse of the project's own
  data — hence the expanded universes.
- **17 Sep — gold and silver rose 2.5% and 3.9% at 20:00 SGT** on a Saudi pipeline repair and a
  yield pullback, the day after the Fed hiked 25bp with a hawkish dot plot (16 of 18 officials
  wanting more) and the BoJ hiked with the *opposite* long-end response. None of it in the
  corpus; the engine's reports for 11–16 Sep were deferred. From this: **T13** — the blind-spot
  monitor and provisional source pool — and four amendments (T12 foreign-yield features; a
  jurisdiction-aware duration axis in schema v2; foreign central banks as a source class; a PCA
  gate on reading spend). Design decisions taken: no retrospective suspension; the haircut only
  forward; search returns structure and a citation, never article text; sources enter the pool
  instantly with dated admission and are scored only on later days; two scores (explanatory and
  predictive), never merged, ranked by explanation ("Sort A"); graduation by the registered
  step-8 rule; decay-out by half-life; PCA for de-duplication, not ranking. LinkedIn drafts v1–v3
  and a coffee-chat script written.
- **21 Sep — this file.**

---

## 3. What the machine does today

**Five steps, every trading day, nothing hand-adjusted.**

| step | what happens | in plain words |
|---|---|---|
| Locate | eight FRED series → PCA (3 PCs) → 4-state GMM, expanding refit every 20 sessions; first 504 sessions unlabelled | "which season is it?" |
| Read | every document published that session is read by the LLM under one schema: direction on five axes (equity, duration, gold, dollar, oil), magnitude, specificity, novelty, confidence, stance | "what did the letters say, and how sure is the reader?" |
| Combine | documents weighted by magnitude × specificity × novelty × confidence (§7.2 fixed rule); where sources disagree, both are shown and neither is combined | "add up the letters — but don't average a yes and a no" |
| Compare | historical sessions matching the regime and the document class, with outcomes already closed by day t (`session ≤ t − 3`), weighted by similarity and recency | "find the days that looked like this one" |
| Report or refuse | a precision-weighted estimate with ESS; **fewer than 8 effective precedents → abstain**; tiers 1–3 by ESS; agreement flag (display-only); the reasons for abstaining printed | "say what usually happened — or say I don't know" |

**What is frozen.** `config/models.yaml` (three price models, 17 Aug) — never touched; the
forward ledger — append-only, committed nightly; `outputs/reports/` — each report written once,
on the first run after its session's close, only when all its documents are read; the corpus
under prompt version `v1-2026-08-23` and one model — never mixed with another version.

**The two referees.** The *forward scoreboard* marks Models 1–3 (long-5/short-5 spreads, H = 5,
10, 20; H = 5 rows mature first). The *report scoreboard* marks the daily report's own calls
(hit-rate, asymmetry, coverage; h = 3 primary; 30 non-overlap rows before any figure prints;
block-permutation null within asset; block bootstrap on asymmetry). Both print "too few to
report" until they can say otherwise.

**The app.** `streamlit run app.py` reads the report JSON — regime, documents, per-asset call or
abstention with reason, evidence quotes, and a live asset lookup. It shows whatever reports exist
on disk. Every roadmap tree, once its verdict is recorded, adds a block to the same JSON; the app
grows, it is not replaced.

**The nightly job** (`daily_run.sh` on launchd at 15:00 SGT, held awake by `caffeinate`): load
`.env` → refresh prices and macro → forward-test row (catch-up if any close was missed) → fetch
documents → read new documents (≤ 40/night, dated ≥ 27 Aug only) → rebuild read CSVs → write
every pending complete report → FOMC→GLD forward ledger → report scoreboard → index rebuild →
commit and push the record.

---

## 4. Everything that has been tested — the complete register

*Verdicts as recorded. "Registered" means the criterion was committed before the test existed.*

| # | claim or question | when | verdict | recorded in |
|---|---|---|---|---|
| 1 | Gold decouples from equities under liquidity stress (P1) | 11 Aug | **NULL**, robust (liquidity-state gap +0.017, p 0.44; macro-regime gap +0.16, wrong direction) | CURRENT_STATE; journal W13 |
| 2 | Regime count n=4 is right | 11/18 Aug | structurally best (ARI 1.000; run 52.5 sessions; silhouette); event-alignment collapsed on 2024 (p 0.32) — "weakly corroborated externally" | CURRENT_STATE |
| 3 | Unconditional lead-lag along the semiconductor chain (P2 stage 1) | 12 Aug | **NULL** | `b6c3ed8` |
| 4 | Rotation has a stable order — seven hypotheses, four instruments (chain, episode, cross-asset, sector; drift existence; PEAD; spillover; scheduled macro-event drift) | 21–23 Aug | **NULL** at every level; the two pairs surviving discovery (SPY→GLD, SOXX→XAR) failed temporal splits and cost tests; spillover +2.319% → +0.012% on tradeable entry | CURRENT_STATE §15 |
| 5 | GDELT-conditioned test on 944 days | 20 Aug | **NO** | CURRENT_STATE |
| 6 | Trend-mode similarity beats level | 24 Aug | the advantage **is the look-ahead**; on the expanding basis level wins by 0.12 | §15.3 |
| 7 | `_z()` look-ahead size | 24 Aug | level +0.012 (p 0.94); trend +0.261 (p 0.057) | §15.3 |
| 8 | Recency decay tie-breaks | 24 Aug | it **reselects** (overlap 0.765/0.850 vs 0.90) | §15.3 |
| 9 | Removing λ raises Sharpe 0.25 → 0.38 | 24 Aug | not distinguishable, p 0.485 — **retired** | §15.3 |
| 10 | Step 3 estimator, six blind acceptance tests | 24 Aug | 6/6 after three declared repairs | §15 |
| 11 | Specificity gate (does the reader discriminate sources?) | 25 Aug | **PASS** 0.363 (n=60); **0.517** full corpus, CI [0.494, 0.539] | §15 |
| 12 | Read audits: stance vs duration; earnings surprise vs equity direction; truncated vs whole 8-Ks | 25 Aug | corr −0.802 (statements); agree 431 / disagree 11; specificity 0.458 vs 0.696 | §15 |
| 13 | Step 3 unblinding — 45 cells (source × asset × horizon {3,5,20}) | 26 Aug | **7 of 45**; robustness re-test **1 of 7** (`fomc_minutes`/USO/h5) — inside chance | §17.7 |
| 14 | FOMC → GLD (retired cell) | 26 Aug | split FAIL 4.62× | §17 |
| 15 | Reader–history agreement predicts better | 27 Aug | **FAIL, backwards** (+0.193% vs +0.406%) — display-only | §17 |
| 16 | Model 1 on all 47 | 28 Aug | Sharpe 0.51, block-permutation p 0.045 — survives, marginally | `backtest_evidence.md` |
| 17 | Model 1 on the survivorship-controlled 35 | 28 Aug | Sharpe 0.25, p 0.184 — **retired** | same |
| 18 | Best of 54 grid configurations | 28 Aug | 0.73 vs null best 0.56; **family p 0.090** | same |
| 19 | Costs are the binding problem | 28 Aug | no — break-even 60.6 bp/side; the short leg (+0.169%/wk) is | same |
| 20 | Model 4: long top-5 vs the universe | 8 Sep | **FAIL** — p 0.035 on all-47 but 9.08× split and p 0.0995 on the 35 | `model4_long_vs_universe.md` |
| 21 | Kernel family {regime-only, similarity-only, Mahalanobis} | 8 Sep | **NULL**, family p 0.114; K0 = 0.04 (the floor is zero); Model 1 split 3.88× | `kernel_family.md` |
| 22 | FOMC → GLD by regime | 8 Sep | hypothesis only; forward-registered (`9c5ad8e`) | `fomc_gld_by_regime.md` |
| 23 | Report scoreboard acceptance tests (seven) | 14 Sep | 7/7 on the founder's machine, no repair | `report_scoreboard_selftest.md` |
| 24 | The report's directional calls beat drift (backfill `986e0d65b6df_n2616`) | 14 Sep | **INCONCLUSIVE** — hit 59.4% vs q95 59.1% (p 0.0497); asymmetry CI includes 1 | CURRENT_STATE §18.6 |
| 25 | The tiers grade confidence | 14 Sep | no — tier 2 51.5% < tier 3 57.5%; tier 1 too few | §18.6 |
| 26 | `fomc_minutes`-driven calls are wrong more often than chance | registered 15 Sep | forward-only, 0 of 30 rows | `overlays/fomc_minutes_contrarian.md` |
| 27 | The report's directional calls beat drift, re-run on the corrected statement corpus `48a6c4e879a1_n2617` | 24 Sep | **FAIL** — hit 58.2% vs q95 58.8% (p 0.0879); asymmetry 0.880; row 24's INCONCLUSIVE not robust | CURRENT_STATE §18.8 |
| 28 | Display instruments change a verdict (instrument robustness) | 29 Sep | **CONSISTENT** — C1–C4 met; hit-rate within 1.7 pts, agreement 94.8% | CURRENT_STATE §18.9 |
| 29 | The market reacts to the surprise, not the decision (T9b stage A, level-1 proxy) | 29 Sep | **INCONCLUSIVE** — gold yes (p 0.039), Treasuries no; the reverse of the prior | CURRENT_STATE §18.10 |
| 30 | Same claim, published 30-minute surprise measure (level 3) | 29 Sep | **FAIL** — gold p 0.49, Treasuries p 0.57; level-1 result proxy-driven; stage B not run | CURRENT_STATE §18.11 |

---

## 5. The wrong-prior log

*Every entry is a plausible belief, held in writing, overturned by running code. The canonical
numbered list is in `CURRENT_STATE`; this is the complete set as known on 21 Sep, in the order
they were caught.*

**Week 13.** Hard-coded PC2 as the stress axis · the macro cross-check conditioning on the
money/dollar axis (a spurious −0.207 gap) · the n=4 event-alignment claim overstated.

**Week 14** (tally to nine). The `bdate_range` calendar (~196 manufactured rows; cost 0.06 of
Sharpe and the survivorship claim) · hard-coded PC2 in `safe_haven_robustness.py` (two scripts
reported opposite signs, −0.209 vs +0.167) · the hard-coded 2024 window in `load_scores_2024()`
(returned the 2024 result for any input — caught only by a crash) · the 500-row BigQuery console
export cap (silently truncated a 595-row pull) · the locked recency kernel never implemented ·
`gdelt_2024_clean.csv` not reproducible from the repo · the phrase "expanding-window
walk-forward, no look-ahead".

**Week 15** (fourteen added, tally 23). "No λ exists anywhere in the codebase" · monotone rung
count given as 3 (it is 4) · code printed 5 under an unregistered tolerance · "the `--types`
filter is not filtering" · Test 1 was a vacuous `isfinite` check · Test 3 scanned one query ·
Test 1's standard error understated 8× · "removing λ raises Sharpe 0.25 → 0.38" · the corpus
cost priced 189 over-cap documents at the mean ($8.91 → $15.94) · a patch script verified anchors
and shipped a NameError, and its `--write` was never run · the corrected estimate calibrated
tokens-per-word on press releases when the remainder was dense 6-K tables ($15.94 → ~$46) · the
`political_other` null read as "the reader finds nothing" without checking the falsifying
documents were in the corpus (they were not) · a timing test asserting novelty falls with
publication lag (FOMC statements are telegraphed and correctly read low) · "ten of 28 hikes read
backwards" (four regex false positives; six real, all with dovish guidance, stance correct).

**26 Aug** (#25, #26). A null that ignored overlap, twice.

**8 Sep** (#28). "Regime-only equal weighting should match Model 1 closely" — it gives 0.04.

**Candidate #29** (14 Sep, founder to decide). "The nightly reads are running and the count is
creeping up" (TRACK §1, 7 Sep) — they had been dead since 29 Aug.

---

## 6. The business

**Positioning** (from the 18 July insight). Specialist vendors sell a unique, orthogonal input,
not alpha. The product: a regime label, a document reading, an explicit precision, and a fixed
rule for silence — an audit trail a fiduciary can put in front of a committee.

**First customers** (Disciplined Entrepreneurship, 24 steps). Beachhead: Singapore boutique
managers and single-family offices (~250 firms, structural estimate); adjacent: regional
independent managers in Hong Kong and ASEAN (~1,200); eventual: the global factor/regime data-feed
market (precedents Barra, RavenPack). Persona and decision-making unit identified; the highest-risk
assumption is whether a boutique's **compliance function** accepts an exempt vendor's output in
client-facing documents. **No customer interview has been conducted.** Every price, segment and
conversion number is a labelled [HYPOTHESIS].

**Why institutional first, retail last.** In Singapore the retail segment needs a licence a
one-person company cannot hold; accredited investors (≤ 30) are serviceable under FAA
s.20(1)(g) / FAR reg 27(1)(d) — a reading of MAS Form 20, **not yet confirmed by counsel**
(nine questions written; S$20,000 budgeted). This reversed the 7 August retail-first sequencing.

**Phases.** 1 (0–12 mo): research service to ≤ 30 accredited investors, S$10,000/firm/year;
break-even at the 8th client against a S$77,400 steady-state cost base. 2 (12–24 mo): licensed
data feed. 3 (24 mo+): the taxonomy as the standard. 4: retail, licence-gated, US$29 / $99 /
$299 per month.

**The ask.** Seed S$139,265 for 18 months: compliance retainer (the binding constraint), the
counsel opinion, founder subsistence, data and inference.

**Risks stated plainly** (deck slide 8): regulatory (the exemption reading); evidential (every
figure gross of costs); signal (one cell of 45 survived); coverage (filed decisions, not rhetoric
— the 17 Sep metals move is the worked example); key person.

**Communications.** LinkedIn post and article (v3, 17 Sep) and a coffee-chat script exist as
drafts (Appendix I). Rules: no performance figures; frame the record as settled questions, not
wasted time; the ask is to compare notes, not to invite criticism of routes that have not run.

---

## 7. What runs every day, and how to check it

*Plain-language version of `TRACK.md` §1. Commands assume the repo root and the activated venv.*

| what | should be true | check |
|---|---|---|
| the nightly job | a dated log per weekday in `logs/`; runs at ~15:00 SGT; late runs are caught up, not lost | `ls logs/ \| tail -3` |
| forward test | one row per model per completed US close; `logged_at` shows any late entry | `tail -3 processed/forward_ledger.csv` |
| document reads | **paused for credit as of 17 Sep** unless topped up; when running, count rises ≤ 40/night on documents dated ≥ 27 Aug only | `python -m src.doc_read --list` |
| reports | written once per completed session, only when its documents are read; pending ones listed | `python step6_report.py --pending` |
| report scoreboard | regenerated each weekday; "too few to report" until 30 rows | `head -15 docs/report_scoreboard.md` |
| the record on GitHub | 0 commits behind; ledgers, scoreboards and reports pushed nightly by step 8/7 | `git log origin/main..main --oneline \| wc -l` |
| fomc_minutes contrarian | "too few to report (n of 30)" | `python -m src.fomc_minutes_forward` |
| FOMC→GLD forward test | observations accrue on FOMC days in the flat-curve/strong-dollar regime | `tail -4 docs/fomc_gld_forward.md` |

**Known state on 17 Sep:** reports for 11, 14, 15, 16 Sep pending behind 13 unread political
documents; the app frozen at 10 Sep; a US$5 top-up runs the nightly reads for months (~US$1–3 a
month at the `--since` cutoff) and unfreezes the app the next evening. Whether the top-up
happened is not recorded here — check `TRACK.md` §5.

---

## 8. Open questions — no registered answer

Capacity/AUM (no dollar-volume history in the repo) · per-name borrow (a flat rate is applied) ·
does reader–history *agreement* mark already-priced information (three readings, inseparable on
n = 2,024) · does the compliance function veto an unlicensed vendor (the plan's highest-risk
assumption; falsifiable in ten conversations) · does the reader's logic match the founder's (the
prompts in `src/doc_read.py` `PROFILES` were written under deadline and never reviewed line by
line) · wrong prior #29 (founder to decide).

---

## 9. Registered but not built (TRACK §3, in plain words)

| item | cost | what it would do |
|---|---|---|
| read the 4,595 political documents (§3.1) | ~US$60 | coverage 30% → 55–70% of document days |
| four intention-bearing sources: White House remarks, Fed speeches, Treasury/OFAC, USTR (§3.2) | US$850–1,150 backfill, ~180/yr | see a threat before it becomes a filing; registered as a paid tier |
| schema v2 — sector axes, now also a jurisdiction-aware duration axis (§3.3) | US$200–400 pilot | let a steel tariff, or a BoJ hike, be reported where it belongs |
| GDELT structured route (§3.4) | time | see a Hormuz closure the hour it happens; now scoped as T13's data remedy |
| macro panel extension UNRATE, ICSA via ALFRED vintages (§3.5) | free, re-validation | also fixes the declared M2 look-ahead |
| counsel opinion on the exemption (§3.6) | S$20,000 | the commercial gate |
| customer interviews (§3.7) | time | the one finding that changes the business most |
| the report scoreboard — steps 1–7 done (§3.8) | $0 | step 8 (source expansion) waits on credit |
| Amendment 4 — ESS target 12 above the floor of 8 | $0 | non-retrospective; if run, reported beside the original |
| §7.3 estimated source weighting | $0 | admissible since collisions cleared 50; worth writing when T5 raises them |
| potential upgrades: persist the expanding regime labels (now has a reason — the backfill); Streamlit Cloud; client watchlists; block-bootstrap interval on the forward test; founder review of `PROFILES` | — | — |

---

## 10. The thirteen trees — where the project goes next

*Full tracks, criteria, costs, capacity and the four universes are in Appendix B (roadmap
v2.2). This is the plain-language map.*

**The principle.** Three things are established: document direction over days is absorbed in
the overnight gap (and the published literature says the remaining edge belongs to
market-makers); the confidence tiers do not grade; the report speaks on 38% of document days. So
the next phase **stops leading with direction** and builds what a desk actually uses each
morning. Direction stays as one block with its abstention rule; it is no longer the headline.

| rank | tree | what a trader gets every morning | success (judgement) | level |
|---|---|---|---|---|
| 1 | **T1 Exposure dial** | how much to hold — cruise control that eases off in rough conditions and never floors it; designed around the published reasons volatility-managed strategies fail (no fitted constant, no leverage, regime-gated changes) | A 55–70% → B 60–75% | master's → PhD |
| 2 | **T8 Announcement-day premium × regime** | which scheduled days pay; a calendar with the historical premium per regime; Test B trades the announcement-day beta premium across 30 ETFs | 60–75% | master's → PhD |
| 3 | **T12 Regime engine v2** | a second weather station with price-based dials (realised vol, cross-asset correlation, credit, and now JGB 30Y / BoJ rate / USDJPY), built beside v1 and adopted only if downstream trees improve | 50–65% | PhD |
| 4 | **T13 Blind-spot monitor + provisional source pool** | "something is moving this market that we cannot see" — detected, sized, attributed to a driver class, with new sources admitted instantly and ranked daily by measured explanatory power | detection 60–75%; pool 50–65% | PhD |
| 5 | **T2 Expected-move engine** | how big today could be — the reader's fields as volatility inputs, the part the gap does not absorb | forecast 65–80%; strategy 35–50% | master's → PhD |
| 6 | **T7 Distilled local reader** | a free reader trained on the paid reader's 2,616 answers, gated on 300 unseen documents; no client document leaves the machine | 70–85% (engineering) | ML engineering |
| 7 | **T11 Unprecedentedness index** | one number for how unfamiliar today is versus anything since 2006, feeding position size | 50–65% | PhD |
| 8 | **T9 Text-derived path factor → bond drift** | the reader's decision-vs-guidance split tested against the weeks-long post-FOMC drift in Treasuries, across the whole curve and credit | 35–55% | PhD |
| 9 | **T10 Surprise/novelty engine** | the reader's novelty as a surprise meter: big surprises → big moves (short branch); quietly changed filing language → slow trouble (slow, cheap-to-trade branch) | 30–55% | PhD |
| 10 | **T4 Meta-labelling** | a learned confidence that replaces the tiers, or proof that none can be learned | 30–50% | top industrial |
| 11 | **T3 Arbitrage tree + your overlays** | relative bets after a document (bonds vs stocks, gold vs dollar, sector pairs) **and the founder's own rules** — entry, size, stop, exit — as registered files or logged fills, scored by the same referee; implementation shortfall reported | systematic 15–35%; overlays valuable regardless | master's / PhD |
| 12 | **T6 Affordable LLM drift capture** | the founder's "affordable LLM" niche: selectivity, not cheaper code — per-name cost model, act only when calibrated drift clears 2× cost, opening-auction limit orders, negative-news mid-caps, filings only; the declined-trades table is the product | 15–30% | PhD / industrial |
| — | **T5 Coverage & vocabulary** | plumbing: §3.1–3.4, made ~free by T7 | multiplier | — |

**Order:** T1(A) → T8(A) → T2(A) → T12 → T13 detection on the backfill → the B tests on v2
regimes → T11 → T7 → T9 → T10 → T4 → T3 (overlays from day one) → T6 → T5 when funded. The
next artefact is `docs/prereg_exposure_dial.md`, committed before a line of `src/exposure_dial.py`.

---

## 11. Ideas parked, not erased

*Every idea raised in four months that is not yet built or has no verdict, kept by name so it
cannot be lost. Where it now lives is given.*

From the journal: the RAG layer (sentence-transformers + ChromaDB/FAISS) — not built, the reader
is API-based · DuckDB/Parquet storage — Parquet adopted, DuckDB not needed · GDELT
theme-anchored tracking — mapping locked, reader route unbuilt → T13 data remedy · the
semiconductor chain thesis (design → memory → packaging → power) — tested null on rotation;
lives on as T3 chain pairs and the founder's NAND overlay slot · metals and rare-earths chain —
deferred to the roadmap since Week 1 · discovered-factor PCA layer as product differentiator —
the classification-standard phase · vector store / RAG for the analyst tier — the US$99 tier ·
three retail tiers and their personas — phase 4 · retail-first sequencing — reversed, both orders
recorded · the exclusivity framing — retired in favour of "unique input" · the report format
proposed 7 Aug — delivered · GDELT 15-minute resolution — preserved for later · Barra/MSCI and
RavenPack as precedents — in the plan.

From August: schema v2 (sector axes; now jurisdiction-aware duration) · Amendment 4 (ESS
knife-edge) · §7.3 estimated source weighting · the 163 over-cap 6-Ks (read at a lower cap, or
not) · the 4,595 unread political documents · client watchlists · Streamlit Cloud · persisting
the expanding labels · block-bootstrap interval on the forward test · the disagreement premium
(agreement backwards — three readings, inseparable) → T11's disagreement branch as a
*magnitude* hypothesis · the M2SL look-ahead via ALFRED.

From September: Model 4's finding that ranking skill is post-2018 momentum — retired, kept ·
Mahalanobis as the only time-stable kernel — not adopted, kept · FOMC→GLD by regime — forward
test running · `fomc_minutes` contrarian — registered · the "affordable LLM" niche via marketing
or "easier code" → T6 (selectivity) and the plan's own vendor thesis · designing around
Cederburg's estimation-error erosion → T1's design table · expanded universes for success over
reuse → §1b and Test A/B · the sub-corpus pool with time-decay ranking "like the weighting we
used before" → T13.3 (EW-R² with half-life and ESS floor) · "PCA for weighing the importance of
news" → PCA is for de-duplicating the pool and for the cross-country spend-gate, not for ranking
(a supervised question) · US and Japan hiking with opposite long-end responses → T13.6's four
amendments · **large-cap technology names showing a gentle, steady intraday trend on catalyst
days** (the founder's own observation, sentence unfinished on 17 Sep) → T13.7, a T6 variant
needing intraday bars · the founder choosing his own entry, size and stop → T3 overlays with
`rule` / `logged` / `intraday` entry modes and implementation shortfall · the wish to see a
"why" for every move → explanatory ranking first (Sort A).

---

## 12. The standing rules (the discipline, in plain words)

1. **Write the rule before the test exists.** Every threshold, criterion and planned amendment
   is committed before the code that uses it. An amendment after a result is read is declared as
   such.
2. **A result that goes against the project is published, not re-run.** Lower and correct beats
   higher and wrong.
3. **A grid, not a shot; a distribution, not a point.** Fewer than 12 cells is not a performance
   result; the best cell is judged against the best of the nulls (the family test); split the data
   with the ratio (≤ 3×) fixed first.
4. **A null deserves the same scrutiny as a positive.** Robustness sweeps before banking.
5. **Frozen means frozen.** `models.yaml`, the forward ledger, the write-once reports, the corpus
   version. New things run *beside* old ones.
6. **Never manufacture an observation.** No imputed returns, no forward-filled prices, no
   calendar rows without sessions, no pooled corpora across prompt versions.
7. **Identify by meaning, not index.** The stress axis is the PC most correlated with VIX,
   whatever its number.
8. **When a hazard is fixed in one place, grep every other consumer in the same commit.**
9. **Costs and capacity inside every test**, gross and net and 3×-net, with a stated AUM at which
   the most illiquid instrument binds.
10. **Admission is dated; a source is scored only on days after its admission.** No source, model
    or rule is credited for the day it was chosen on.
11. **Nothing external claims a performance figure** until the forward record can report an
    interval.
12. **The record leaves the machine every night** (step 8/7), and secrets never enter git.

---

## 13. Backup and restore (summary of TRACK §7)

On GitHub: code, docs, registrations, the forward ledger (force-tracked since 14 Sep), the
report ledger and scoreboards, write-once reports, the 2,616 document reads (10 MB),
`.env.example` (names only). Not on GitHub, on purpose: `.env` (dies with the laptop; keys
re-issued at each provider), raw documents (770 MB, re-fetchable), price/macro caches and panels
(rebuildable), logs, the launchd plist (described in TRACK §7). Restore: clone → venv →
`cp .env.example .env` and fill → `download_data --force`, `build_panel`, `pca_macro` →
`forward_log --no-refresh --dry-run` → `report_scoreboard --selftest` (seven PASS) → recreate the
plist → read the first unattended log against section 7. A credential scan on 14 Sep of the repo
and its full history found nothing to revoke.

---

## 14. Glossary — for anyone

- **Regime / season.** One of four market "weather" states, found by the machine from eight
  economic dials, not chosen by a person.
- **PCA.** A way to squash many dials into a few summary dials that carry most of the movement.
- **GMM.** A method that sorts days into groups (the seasons) by how similar their summary dials
  are.
- **Expanding window.** Only ever using the past — each day's answer uses data up to that day
  and nothing after.
- **Look-ahead.** Accidentally using tomorrow's information today. The project's most-caught
  mistake.
- **Survivorship bias.** Only studying things that still exist today, which flatters results.
- **Backtest.** Pretending to run the system in the past to see what it would have done.
- **Forward test.** Running it for real, day by day, with each answer written down before the
  outcome is known.
- **Ledger.** The write-once list of those answers.
- **Corpus.** All the documents the reader has read, under one fixed set of instructions
  (the *prompt version*).
- **Schema.** The fixed questions the reader answers about every document.
- **Specificity / novelty / magnitude / confidence.** How precise a document is; how new its
  content is versus the last one from the same source; how big an effect it implies; how sure the
  reader is.
- **Precedent.** A past day that matches today's season and document type.
- **ESS (effective sample size).** How many precedents you *really* have once similar ones are
  down-weighted. Below 8, the report abstains.
- **Abstention.** Saying "I don't know" in writing.
- **Tier.** A confidence label from ESS. Found on 14 Sep not to grade.
- **Hit-rate.** How often the direction was right. **Asymmetry.** Whether right calls were bigger
  moves than wrong ones.
- **Null / permutation test.** Shuffling the answers to see what "no skill" would score; a result
  must beat that.
- **Block bootstrap.** Re-sampling in chunks so that days that move together stay together.
- **Family test.** Judging the best of several tries against the best of several random tries.
- **Chronological split.** Checking the first half of history and the second half agree.
- **Sharpe.** Return per unit of risk. **CER.** Return adjusted for how much risk a cautious
  person would accept.
- **Half-life / time decay.** Old evidence counts less; the half-life says how fast.
- **Pre-registration.** Writing the rules of a test before running it, in version control.
- **Wrong prior.** A belief held in writing that a run overturned.
- **Dial (T1).** A position size between 0 and full, set by volatility and season.
- **HAR-RV / QLIKE.** A standard volatility forecast and the right way to score one.
- **Meta-labelling.** Training a second model to say when the first model is right.
- **Mahalanobis distance / turbulence.** How unusual today's combination of movements is.
- **Provisional pool.** The waiting room for new document sources, ranked daily by how much they
  explain, admitted with a date, scored only afterwards.
- **Implementation shortfall.** The gap between what a rule would have done and what your actual
  trade did.

---

## 15. File map — what is live, what is superseded

| file | status | job |
|---|---|---|
| `docs/PROJECT_MASTER.md` (this) | **live — the one file** | everything, plain first, evidence bound behind |
| `docs/TRACK.md` | live | daily status board: §1 running, §2 open, §3 undone, §4 upgrades, §5 done, §6 rules, §7 backup |
| `docs/CURRENT_STATE_2026-08-23.md` | live, append-only | the evidence record (§1–18) |
| `docs/prereg_*.md`, `docs/overlays/*.md`, `docs/forward_test_amendment_*.md` | live | registrations |
| `Learning_Journal.docx`, `Business_Plan.docx`, `Pitch_Deck.pptx` | submitted artefacts | unchanged |
| `docs/roadmap_signal_trees_v2.md` | superseded → Appendix B (v2.2) | archive |
| `docs/MODEL_EVOLUTION.md` | superseded → Appendix C | archive |
| `docs/POST_SUBMISSION_STATE.md`, `SESSION_HANDOFF.md`, `EXECUTION_PLAN.md` | superseded (banners) → Appendix G | archive |
| `TRACK_report_scoreboard.md` | superseded → Appendix H | archive |
| `briefing.md` | a chat concatenation, gitignored | delete when convenient |
| `linkedin_post*.md`, coffee-chat script | drafts → Appendix I | keep outside the repo or under `docs/comms/` |

---

## 16. Change log of this master file

| date | change |
|---|---|
| 2026-09-21 | Created. Consolidates the journal (Weeks 1–15), the post-submission record to 21 Sep, TRACK, CURRENT_STATE §1–18, MODEL_EVOLUTION, POST_SUBMISSION_STATE, the report-scoreboard addendum, the roadmap (brought to v2.2 with T13 and the US/Japan amendments), the business plan and deck, and the communications drafts. Nothing removed. |
| 2026-09-24 | Two silent defects found (API key never in `.env`; no FOMC statement fetcher); fetcher built; statement corpus replaced by a mis-scoped refetch and re-read; backfill re-baselined — verdict INCONCLUSIVE → FAIL (register row 27; CURRENT_STATE §18.7–18.8). Repo made runnable from a fresh clone; LICENSE added. |
| 2026-09-29 | Two registrations added from the founder's observations (TRACK §3.9–3.10): T9b surprise conditioning — the market reacts to the decision minus what was priced, so precedents must condition on the surprise sign (level 1 from DGS2 and the pre-meeting run-up, $0; the published Swanson/Bauer–Swanson surprise series makes the intraday measure free as well); and an instrument-robustness test — the app displays desk instruments (S&P 500, 10Y yield, gold futures, DXY, WTI) while the model runs on ETFs, and the difference (settlement timing, roll, maturity) must be tested, not assumed. App v3 delivered: live Yahoo quotes, click-through detail charts 1m–1wk, glass design, no buy/sell by design. |
| 2026-09-29 | §3.9 extended: surprise measures registered per event class — Fed (published series), earnings (analyst consensus, free via yfinance for recent years), scheduled macro releases (consensus paid; run-up proxy free), executive orders (no consensus; prediction-market odds, run-up), foreign central banks (run-up proxy), and **corporate cooperation / partnership / M&A news as a new source class** (8-K Items 1.01/2.01/7.01/8.01 + EX-99, $0 from EDGAR, entering through T13's provisional pool). Rule: the surprise uses only data available before the close, never the reaction. |
| 2026-09-29 | Both new tests run the same day. Instrument robustness CONSISTENT — the app may say verdicts are unchanged on desk instruments. Surprise stage A INCONCLUSIVE — gold's next three sessions follow the FOMC surprise (hawkish statement + hawkish surprise −1.55% vs + dovish surprise −0.06%); Treasuries show nothing. Register rows 28–29; wrong-prior candidates #32–#33. |
| 2026-09-29 | Surprise level 3 FAIL with the Fed's own published surprise series: the gold effect was the proxy measuring the whole day's move. Stage B withdrawn. Register row 30; wrong-prior candidate #34. |
| 2026-09-29 | T14 registered (TRACK §3.11): event-time reading — read the FOMC statement at 2:00 pm ET when published, not after the close; phases A (free historical continuation test on the FRBSF 30-minute asset reactions) → S5 forward intraday collection → B/C live read + app panel → E press conference → D intraday precedent pool. Professional-tier feature; counsel item. |

*Add a row here whenever a verdict is recorded or a tree changes state, and bump Appendix B's
version line with it.*



---

# PART B — THE CANONICAL DOCUMENTS, BOUND IN FULL

*Nothing below is summarised. A new conversation may stop before Part B; it is here so that no idea or number depends on another file.*


---

# APPENDIX A — TRACK.md (status board, as of 21 Sep 2026)

> *Live file; the copy here is a snapshot. The repo's docs/TRACK.md is authoritative for anything after this date.*

# TRACK — Regime-Aware Cross-Asset Signal Framework

**This is the one file to bring to a new conversation.** It supersedes the Track
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

| item | what should be true | how to check | if it isn't |
|---|---|---|---|
| **Forward test, launchd, 15:00 SGT** | One dated log per weekday since 28 Aug | `ls ~/Projects/regime-aware-signal/logs/` | The gap is permanent. Find the cause (Mac asleep at 15:00 is the usual one) and record the gap dates here in §5 |
| **FOMC→GLD forward test** | Registered `9c5ad8e` on 8 Sep. Ledger gains one row ~3 sessions after each FOMC decision. First observation: 17 Sep decision, matures ~22 Sep | `python fomc_gld_forward.py` or `cat docs/fomc_gld_forward.md` | Criterion is n ≥ 10 with both tests at p < 0.05 — no verdict before early 2028. **Do not change the per-regime sign after a miss; do not trade it.** The model does not forecast this; it is a hypothesis found by looking |
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

---

## 6. Standing rules — apply to every item above

- Every criterion is written and committed before the test exists.
- Amendments are recorded before results are read.
- A result that goes against the project is published, not re-run.
- A grid, not a shot; a distribution, not a point; split data with criteria
  fixed first (business plan §3.4.1).
- The frozen models in `models.yaml` are not touched. The forward test's
  value is that they haven't been.


---

# APPENDIX B — Roadmap v2.2 (thirteen trees)

> *Supersedes docs/roadmap_signal_trees_v2.md. T13 and the four US/Japan amendments were added 21 Sep from the 17 Sep discussion; nothing earlier was removed.*

# Roadmap v2.2 — thirteen trees toward a daily signal a trader can use

*Written 2026-09-15; revised the same day twice — first for plain-language paragraphs, §0 criteria and overlay entry modes; then (v2.1) for **universe expansion**, then (v2.2, 21 Sep) for **T13 — the blind-spot monitor and provisional source pool**, born from the 17 Sep metals move that no covered source could explain, plus four amendments from the same discussion (T12 foreign-yield features, a jurisdiction-aware duration axis for schema v2, foreign central banks as a source class, and a PCA gate on reading spend). Earlier: §1b defines four universes, every tree that gains from breadth now runs Test A (existing data) and Test B (expanded) under one registration, and T12 adds a regime engine v2 built beside v1. Design priority is success, not reuse of the project's existing data. Supersedes `roadmap_signal_trees.md` (v1, five trees). Every tree is a
track: numbered steps, each with a done-criterion, in the order the project always uses —
register, build against acceptance tests, run, record whichever way it falls, wire into the
report only after the verdict is written. All trees inherit §1 (costs and capacity) and §2
(the standing protocol). Ranks in §3.*

*What the trees are built on: the report's abstention rule, the regime engine, 2,616 documents
read under one schema (direction × 5 axes, magnitude, specificity, novelty, confidence,
stance), the write-once reports, the scoreboard, the backfill at hash `986e0d65b6df_n2616`,
and the founder's own trading record and domain knowledge. What they are built against: the
finding that document direction is priced in the overnight gap, that the tiers do not grade,
and that the report speaks on 38% of document days.*

---

## 0. How to read the "knowledge" column — the criteria behind each label

The label says what the builder must already know to run the track **alone**, without a
supervisor catching the silent mistakes. It is not a measure of difficulty of coding.

| label | criterion | the silent mistake it guards against |
|---|---|---|
| **master's** | Every method in the track is taught in an MSc Finance or ML-in-investments course and can be built from a textbook in days: OLS, EWMA volatility, HAR, Sharpe and certainty-equivalent, event windows, block bootstrap, a chronological split. | Overfitting a parameter and not knowing it; the standing protocol (§2) is enough protection. |
| **PhD** | The track needs judgement about *identification and dependence* that a course does not supply: which null is the right one, how overlapping observations inflate a t-statistic, when a within-regime distance is meaningful, how many tests were really run. The methods (Diebold–Mariano with HAC, Mahalanobis within regime, purged cross-validation, deflated Sharpe) come from reading primary papers, and using one wrongly produces a confident wrong answer. | A result that passes every test you ran and fails the one you didn't know to run. |
| **ML engineering** | Not finance theory — systems skill: fine-tuning a language model, constrained decoding, building a held-out evaluation that cannot leak, GPU/Apple-silicon tooling. The risk is engineering risk (a model that looks right on the training set), not inference risk. | A distilled reader that agrees with the teacher on documents it has seen and not on new ones. |
| **top industrial** | The know-how lives in practitioners' desks more than in papers: execution and market-impact modelling, per-name cost curves, meta-labelling with leakage control at production scale, portfolio construction under trading penalties (model predictive control). Published methods exist but the parameters that make them work are unpublished. | A backtest that assumes fills you would not have got. |

Mixed labels (e.g. "master's → PhD") mean the first rungs are one and the last rung is the
other. A tree can be *started* at the lower label; it cannot be *finished* below the higher one.

## 1. Costs and capacity — fixed once, inherited by every tree

| item | assumption |
|---|---|
| ETF half-spread | SPY 0.5 bp · TLT 1 bp · GLD 1 bp · IEF 1 bp · UUP 3 bp · USO 3 bp (round trip = 2×) |
| single names (Trees 3, 6, 10b) | half-spread from a **per-name cost model**: `hs = a + b·(1/√ADV$)` fitted on quoted spreads; impact `η·(trade/ADV)^0.5` with η = 10 bp; never a flat number |
| commission | 0 |
| implementation lag | one full session (signal at close `t`, executed at close `t+1`) for Trees 1, 2, 8, 9, 10, 11; **opening auction of `t+1`** for Trees 3 and 6, where the auction price is the fill and a limit at the prior close ± 0.5·spread is the order |
| short borrow | 50 bp/yr ETFs; per-name from the cost model for stocks; none in Trees 1, 2, 8, 11 (long-only or cash) |
| turnover control | hysteresis band δ on every continuous dial; registered per tree |
| reporting rule | every performance table shows gross, net at §1, and **net at 3× §1**; the 3× column is the one quoted |
| capacity | each tree states the AUM at which the most illiquid instrument's 1%-of-ADV cap binds |

## 1b. Universes — defined once, so "Test A / Test B" means the same thing in every tree

The regime engine is built on eight FRED macro series and is **universe-independent**; these
universes are where its labels are applied and where signals are measured. Expanding them does
not change the regimes (that is T12's job); it changes how much the regimes have to act on.

| code | contents | history | survivorship note (declared, not solved) |
|---|---|---|---|
| **U5** | SPY, TLT, GLD, UUP, USO — the reader-schema assets | 2007+ (UUP) | none |
| **U47** | the existing three-group basket (long-history 35 + modern overlay + spotlight) | mixed | existing declared bias |
| **U-ETF30** | liquid multi-asset ETFs with data from ≤ 2007: equities SPY QQQ IWM EFA EEM VWO; sectors XLE XLF XLK XLV XLU XLI XLP XLY XLB VNQ; rates SHY IEF TLT EDV TIP; credit LQD HYG; commodities GLD SLV GDX USO DBC; FX UUP FXE FXY | 2007+ | ETFs alive today only — dead ETFs excluded; stated in every Test B table |
| **U-Curve** | SHY, IEF, TLT, EDV, TIP, MBB, LQD, HYG — the duration/credit ladder for T9 | 2007+ | as above |
| **U-Liquid200** | US single names, top 200 by 2019–2026 average dollar volume, mega-caps (top 20) excluded, for T6 and T10(b) | 2010+ | selected on *recent* liquidity, so tilted to survivors; the split test is the guard |

Data for all: yfinance ($0). Costs per §1: ETF half-spreads by name; single names from the
cost model. **Rule for every amended tree:** Test A and Test B are registered in the same file
with the expected sign of (B − A) written first; both are reported; if only B passes, the
result is "diversification, not signal" unless A's criterion was met on its own universe too.

## 2. The standing protocol (business plan §3.4.1, unchanged)

Criterion committed before code; acceptance tests on synthetic data before real data; a
family test when more than one variant runs; chronological split with the ratio (≤ 3×) fixed
first; a result that goes against the tree is published, not re-run; nothing enters
`step6_report.py` until its verdict is recorded in `CURRENT_STATE` and TRACK §5.

---

## 3. Ranking

*Success* = the tree yields a daily, dynamically computed output a trader acts on, **and** its
registered test shows value at the 3× cost column on a ≤ 3× chronological split. The
percentage is my judgement of that whole sentence. *Knowledge* is what the builder must
already know to run the track without a supervisor.

| rank | tree | success (A → B) | knowledge | cost | first verdict | unique to this project? |
|---|---|---|---|---|---|---|
| 1 | **T1 Exposure dial** (Cederburg-answer design) | A 55–70% → B 60–75% | master's → PhD (B: MPC) | $0 | 3–5 days (A), +3 (B) | the regime engine's *sizing* power across a multi-asset book |
| 2 | **T8 Announcement-day premium × regime** + cross-sectional beta tilt | A 60–70% → B 60–75% | master's → PhD | $0 | 3–4 days | regime-conditioned; B adds the announcement-day beta premium on U-ETF30 |
| 3 | **T12 Regime engine v2** (asset-return and jump features, built beside v1) | 50–65% that v2 improves ≥1 downstream tree net | PhD | $0 | 1–2 weeks | the foundation; every tree above inherits it |
| 4 | **T13 Blind-spot monitor + provisional source pool** | detection 60–75% (testable on the backfill now); pool ranking as a product 50–65% | PhD | ~US$1–2/month (searches) | detection: 3 days; pool: forward from admission | the only vendor output that says "something is moving this market that I cannot see", with the driver class ranked by measured explanatory power |
| 5 | **T2 Expected-move engine** | forecast A 65–80% → B 70–85%; strategy 35–50% | master's → PhD | $0 | 3–5 days | pooled panel with asset fixed effects on U-ETF30 |
| 6 | **T7 Distilled local reader** | engineering 70–85% | ML engineering | ~$0–50 | 1–2 weeks | makes B universes readable at $0 |
| 7 | **T11 Unprecedentedness index** (+ asset-turbulence component) | 50–60% → 55–65% | PhD | $0 | 3–4 days | three-component distance: macro, documents, cross-asset |
| 8 | **T9 Text path factor → bond drift** on U-Curve | 35–50% → 40–55% | PhD | $0 | 1 week | LLM path factor tested across the whole ladder and credit |
| 9 | **T10 Surprise/novelty** | short 40–55%; slow 30–45% (U-Liquid200) | PhD | $0 | 1–2 weeks | reader-measured novelty, regime-conditioned |
| 10 | **T4 Meta-labelling** | 30–45% → 35–50% with B's larger call set | top industrial | $0 | 1–2 weeks | learned confidence replaces tiers |
| 11 | **T3 Arbitrage tree + overlays** | systematic 15–30% → 20–35% with sector pairs; overlays valuable regardless | master's / PhD | $0 → $200–400 | days / months | your calls, scored |
| 12 | **T6 Affordable LLM drift** on U-Liquid200 | 15–30% | PhD / industrial | $0 with T7 | 2–3 weeks | cost-aware abstention |
| — | **T5 Coverage & vocabulary** | multiplier | — | $60 → $1,200 | weeks | plumbing |

The B numbers are higher for one reason only: more assets give a regime tilt, a beta tilt, or a
document effect more places to show up, and a pooled test more power. They are not higher
because breadth creates edge. Where a tree does not gain from breadth (T7) the number is unchanged.

Suggested order: T1(A) → T8(A) → T2(A) → T12 → **T13 detection on the backfill** → T1(B), T8(B), T2(B) re-run on v2
regimes → T11 → T7 → T9 → T10 → T4 → T3 (overlays from day 1 in parallel) → T6 → T5 when funded. The A tests
fit in one week; T12 and the B re-runs are the second week.

---

## T1 — Exposure dial

**In plain words.** This tree decides *how much* to own each day, never *which way* prices go. Think of cruise control on a car: on a rough road (markets jumping around) it eases off the accelerator; when the weather report says a storm regime, it eases off further; it never floors it. You wake up, read "SPY: hold 62% of your normal size, no change from yesterday", and that is the whole instruction. It is ranked first because it does not need to be right about direction — the thing every earlier test showed cannot be predicted — and because it trades rarely, which is what lets it survive costs.


**Hypothesis.** Holding SPY, TLT, GLD, UUP, USO at a size that scales down with forecast
volatility and tilts by regime beats holding them at fixed size, net of costs, on a
chronological split, using no directional forecast.

**Why it can work when direction did not.** Regimes persist (median run 52 sessions at n=4),
so a regime-gated dial trades a handful of times a year — the property that gives
regime-based allocation a break-even above 200 bp one-way in the literature. Volatility is the
most forecastable quantity in markets. Neither needs tomorrow's sign.

**The Cederburg answer — what this design changes relative to the literature that failed.**

| failure mode in the literature | design choice here |
|---|---|
| out-of-sample gains vanish because the scaling constant `c` in `w = c/σ̂²` is estimated (Cederburg et al. 2020) | no `c`: `w = min(1, σ*/σ̂)`, long-only, **de-risk only, never lever up**; σ* is the asset's own trailing 10-year vol, not a fitted parameter |
| transaction costs erode gains for factor portfolios (Barroso & Detzel 2021) | five liquid ETFs, not factors; hysteresis band δ; regime gate so the dial moves in steps |
| many regimes → many transitions → turnover (Nystrup) | four regimes already validated on persistence; tilt changes only on a *confirmed* label change (posterior > 0.8 for 3 sessions) |
| Sharpe as objective rewards leverage | certainty-equivalent return at γ = 3 and max drawdown as primary; Sharpe secondary |

**Daily output.**
```
SPY  target 0.62 × base   vol 18.4% vs σ* 15.1% → 0.82; regime 3 tilt −0.20 (posterior 0.98, confirmed 41 sessions)
     band: |Δ| = 0.03 < δ 0.05 → NO TRADE.  Held 0.65 since 02 Sep.
```

**Track.**

| step | do | done when |
|---|---|---|
| 1 | Register `docs/prereg_exposure_dial.md`: rungs R0–R3 below; null; CER objective; split 2010–17 / 2018–26 at ≤ 3×; δ = 0.05; cap 1.0; costs from §1; expected: R1 beats R0 on drawdown not Sharpe, R2 adds ≤ 0.05 CER | committed, hash in TRACK |
| 2 | Acceptance tests (synthetic): a dial fed constant vol reproduces R0 exactly; a dial fed a perfect-foresight regime label beats R0 with p < 0.001; the band produces zero trades when the target is inside it; a shuffled label produces CER within the null band | 4/4 pass, recorded |
| 3 | Build `src/exposure_dial.py`: EWMA σ̂ (λ = 0.94), expanding σ*, expanding per-asset-per-regime shrunk Sharpe (James–Stein toward 0), soft tilt from posterior (R3), band, one-session lag, cost accounting | runs on the panel |
| 4 | Run rungs: R0 constant · R1 vol-only · R2 R1 × label tilt · R3 R1 × posterior tilt. Family = {R1, R2, R3} vs best-of-three nulls (shuffled 52-session regime blocks; time-reversed vol). 10,000 draws | table gross / net / 3× net |
| 5 | Record in prereg §amendments, TRACK §5, CURRENT_STATE §19; verdict per rung | written before discussion |
| 6 | If any rung passes: add the dial block to `step6_report.py` **as an addition**, with the verdict printed beside it. If none passes: add the R1 dial anyway, labelled "descriptive — did not beat constant weight net of costs", because a sized position with its reason is still the product | report shows it |
| 7 | Forward: the dial's realised CER accrues in `processed/dial_ledger.csv`, scored monthly, never rewritten | §1 row in TRACK |

**Capacity.** UUP binds: 1% of ADV ≈ US$0.5m/trade; at a 20% UUP sleeve and δ = 0.05, ≈ US$50m
AUM. Stated in the plan.

**Test A / Test B (v2.1).**

| | Test A | Test B |
|---|---|---|
| universe | U5, each asset sized independently | **U-ETF30 as one book** |
| construction | rungs R0–R3 as above | R0 = risk parity (inverse-vol) at fixed weights; R1 = vol-targeted risk parity; R2 = R1 with regime-conditional *expected-return tilts* from expanding shrunk Sharpe per asset per regime, capped ±25% of the risk-parity weight; **R3 = R2 solved by model predictive control** with an explicit trading penalty λ·‖Δw‖₁ at the §1 cost table (the Nystrup et al. formulation), so turnover is optimised rather than banded |
| what B adds | — | diversification across 30 assets, so a regime tilt has somewhere to go; the MPC penalty replaces the crude δ band |
| registered expectation | R1 > R0 on drawdown | B's R2/R3 CER − A's best CER > 0; if B passes and A does not, "diversification, not signal" |
| extra risk | — | ETF survivorship; MPC has a tunable λ — **fix λ at the cost table before running**, never sweep it |
| knowledge | master's | PhD (constrained optimisation, MPC) |

---

## T2 — Expected-move engine

**In plain words.** This tree answers "how *big* could today's move be, and why?" It reads today's documents and says, for each asset, "today is a 1.6-times-normal-risk day for bonds, because the Fed minutes are unusually specific." It does not say up or down. A trader uses it to shrink or widen positions and stops before the move, not to bet on the move. It is the part of the reader's work that the market does *not* absorb in the overnight gap.


**Hypothesis.** The reader's fields at `t` improve a forecast of the next-3-session realised
absolute move and realised variance per asset over a HAR-RV baseline.

**Why.** The sign is absorbed in the gap; the *size* need not be. A proclamation scored 0.67
specificity with zero direction is a "large move, unknown sign" document — the exact case the
current report abstains on.

**Daily output.**
```
TLT  expected |3-session move| 1.9%  (HAR baseline 1.2%, ×1.6)
     drivers: FOMC minutes spec 0.71 nov 0.55 (+0.5%); regime 3 × specificity (+0.2%)
     sign: not forecast — see abstention above
```

**Track.**

| step | do | done when |
|---|---|---|
| 1 | Register `docs/prereg_expected_move.md`: M0–M3 below; QLIKE and MAE; Diebold–Mariano HAC; expected: improvement on document days only; split ≤ 3× on the improvement | committed |
| 2 | Acceptance: on synthetic RV with planted document effects, M1 recovers the planted coefficient within 2 SE; with no planted effect, DM rejects ≤ 8% of the time | pass |
| 3 | Build `src/expected_move.py`: per asset, expanding OLS. M0 HAR-RV (`RV_t`, `RV_{t−4:t}`, `RV_{t−21:t}`); M1 = M0 + `n_docs`, max specificity, mean \|magnitude\|, max novelty, mean confidence, source dummies, `sources_disagree`; M2 = M1 + regime dummies + regime × max-spec; M3 = M1 + \|net_view\| | runs on the backfill |
| 4 | Run; DM tests per asset and pooled; then **plug M1's σ̂ into T1-R1** and re-run T1's registered comparison — that is the strategy test | tables |
| 5 | Record | written |
| 6 | Wire the expected-move block into the report with the verdict beside it | shown daily |
| 7 | Optional branch (paid, separate registration): options data → straddle when M1's forecast exceeds the implied move by a registered margin | not in v1 |

**Costs.** None beyond T1's; the engine is a forecast. **Capacity.** Inherits T1.

**Test A / Test B (v2.1).**

| | Test A | Test B |
|---|---|---|
| universe | U5 | **U-ETF30**, pooled panel regression with asset fixed effects and asset-specific HAR lags |
| document mapping | five axes → five assets | a **mapping table** `config/doc_asset_map.yaml`: FOMC → rates & credit ETFs; earnings 8-K → the issuer's sector ETF (and the issuer if in U47); political → sector by the reader's `direction` axes now, by schema v2's sector axis later |
| what B adds | — | ~6× the rows; the question "do documents move *sector* volatility" that U5 cannot ask |
| registered expectation | improvement on document days only | pooled DM p < 0.05 and ≥ 60% of assets individually; the sector-ETF cells are where the gain should concentrate |
| extra risk | — | mapping errors are a silent bias — the mapping file is committed before the run and never edited after |

---

## T3 — Arbitrage tree: event-time relative value + registered overlays (your slots)

**In plain words.** Two things live here. First, *pairs*: instead of asking "will bonds go up after the Fed?" (which the market answers overnight), it asks "will bonds do better than stocks over the next few days after this kind of statement?" — a relative bet, which markets digest more slowly. Second, and more important, *your own rules*: anything you already do as a trader — when you buy, how much, where your stop is — written down as a rule or logged as an actual fill, then scored by the same referee as everything else. This is the tree where the project stops being a replication and becomes yours.


**Systematic half — lowest prior on this page**, because outright rotation, lead-lag, PEAD and
spillover were all null in August. What was *not* tested: the **relative** response of two
assets to one document class, which is what a macro desk trades on a Fed day.

| pair | document class | registered relative hypothesis |
|---|---|---|
| TLT − SPY | FOMC statement, hawkish stance + dovish guidance (the six-hike pattern) | the spread drifts 2–5 sessions after the initial gap |
| GLD − UUP | proclamation/sanctions class; real-rate-relevant FOMC | your USD–gold co-appreciation thesis as a spread |
| MU − SNDK, ASML − TSM, … | earnings 8-K in the chain | the pair drifts after both legs have gapped |
| **Test B — sector pairs on U-ETF30** | XLE − SPY on oil-relevant documents; XLF − SPY on rates documents; XLK − SPY on export-control / tariff proclamations; GDX − GLD on real-rate documents | the sector spread digests a document class over 3–5 sessions after the index has gapped — testable *now* on the five axes, sharper after schema v2 |

**Track (systematic half).**

| step | do | done when |
|---|---|---|
| 1 | Register one file per pair: spread definition (log ratio, hedge ratio fixed at 1 or beta-from-expanding-window, stated), entry at the opening auction of `t+1`, exit at `t+1+h`, h ∈ {3, 5}, null = within-pair block permutation, criterion = scoreboard §6 on the spread as the "asset" | committed |
| 2 | Build `src/pair_events.py` reusing the scoreboard (the spread is a synthetic asset with its own return series) | selftest passes |
| 3 | Run on the backfill; family across the three pairs; split | tables |
| 4 | Record; prior is null on pairs 1 and 3 | written |

**Overlay half — the slots.** An overlay is a rule you already trade by, turned into a
committed file and a scored row. Template, `docs/overlays/<name>.md`:

```
name:        [SLOT]
trigger:     [SLOT — a condition in fields the report carries: regime, posterior, stance,
              direction.<axis>, specificity, novelty, n_docs, dial level, trailing returns]
direction:   [SLOT]
entry:       [SLOT — one of three modes:
              rule     = a price the ledger can model from daily bars: next close, next
                         opening auction, or a limit level (filled if that session's
                         low/high crosses it);
              logged   = your actual fill (time, price) typed into the ledger the day you
                         trade — the referee scores what you DID, not a model of it;
              intraday = a clock-time rule (e.g. 10:30 ET after the open settles) —
                         allowed only once intraday bars are on disk; until then use
                         `logged`]
size:        [SLOT — in units of the T1 dial; an overlay cannot exceed the risk budget]
stop:        [SLOT — a level or a %; the ledger assumes the stop is hit if the session's
              low (long) / high (short) crosses it — conservative by construction; or
              `logged` for your actual exit]
exit:        [SLOT — sessions, regime change, target, or `logged`]
falsifier:   hit-rate below the within-asset null after 30 non-overlap forward rows;
             for `logged` entries the same test on your fills, plus implementation
             shortfall = your fill vs the modelled `rule` price, reported
prior:       [SLOT — two sentences: what you expect and why]
```

**Why the other trees fix entry at the close or the open, and why that does not bind you.**
Those trees are *tests*: the fixed convention makes every result comparable and free of
look-ahead, and daily bars are the only prices in the repository. It is a testing rule,
not a trading rule. Any tree's signal can be executed your way through an overlay in
`logged` mode, and the ledger then reports two numbers side by side: what the rule would
have done, and what your execution did. The gap between them is your implementation
shortfall — the number every desk tracks and almost no individual trader knows.

Slots to fill from your own record:

- **`doc_read` logic** — "stance hawkish AND direction.duration > 0 ⇒ guidance dovish ⇒ long TLT
  3 sessions" (the Week-15 pattern as a rule).
- **NAND / DRAM cycle** — chain names conditioned on contract-price direction or 8-K guidance
  language the reader scores; your prior work.
- **Stagflation / precious metals** — the FOMC→GLD-by-regime hypothesis (registered 8 Sep) is
  this slot's first entry; add the gold–silver ratio rule you actually watch.
- **IRP / carry / EUR–USD under stress** — UUP-side rules; the dollar axis is in the schema.
- **`fomc_minutes` contrarian** — the 37.8% observation, as a rule *before* any second look
  (see §fomc_minutes at the end of this file for the registration text).

**Track (overlay half).**

| step | do | done when |
|---|---|---|
| 1 | Write three overlay files from the slots above | committed |
| 2 | Build `src/overlays.py`: reads the files, evaluates triggers on today's report, appends `processed/overlay_ledger.csv` (append-only), scored by `report_scoreboard` with `--tag overlays` | rows begin |
| 3 | Wire into `daily_run.sh` after 6c/7; report shows "founder overlays (discretionary, registered, scored)" | daily |
| 4 | First verdict at 30 non-overlap rows per overlay; until then "too few to report" | months |

**Why the overlay half matters at zero alpha.** It turns thirty months of market notes and a
live book into a timestamped, falsifiable record — the one artefact no regime-label vendor
has and no investor can call a backtest.

---

## T4 — Meta-labelling: learn when the report is right

**In plain words.** A second opinion on the first opinion. The report makes a call; this tree has learned, from the past, that "calls like this one — this regime, this source, this much volatility — have been right 61% of the time; calls like that one, 45%." It replaces the current confidence tiers (which turned out not to grade) with a probability that has been checked. A trader sizes up the 61s and skips the 45s.


**Hypothesis.** A secondary classifier on features available at `t` (regime, posterior,
realised vol, reader fields, source, agreement flag, ESS, tier, days-to-FOMC,
unprecedentedness from T11) predicts whether a report call will be correct, out of sample,
above the base rate; its probability replaces the tiers.

**Track.**

| step | do | done when |
|---|---|---|
| 1 | Register: triple-barrier labels (+1σ / −1σ / 3 sessions); purged & embargoed 5-fold on the 1,026 backfill calls; walk-forward expanding; **deflated Sharpe** against the number of feature sets tried (declare the number now: 3); precision/recall criterion; split | committed |
| 2 | Acceptance: on synthetic calls with planted "correct when vol low" structure, the learner's purged-CV precision exceeds base rate; on shuffled labels it does not | pass |
| 3 | Build `src/meta_label.py` (gradient boosting, shallow; logistic as the control) | runs |
| 4 | Run; MDA feature importance on purged folds; sized strategy = dial × 2(P − 0.5)⁺ at 3× costs; deflated Sharpe | tables |
| 5 | Record. Prior: modest precision gain from vol and source; deflated Sharpe not above zero; a null here **closes** the "tiers don't grade" question: nothing grades on this data | written |
| 6 | If precision passes: `P(correct)` replaces the tier in the report; abstain below 0.5 | daily |

**Danger.** The beautiful in-sample curve. Steps 1 and 4 are not optional.

---

## T5 — Coverage & vocabulary (multiplier, not a strategy)

**In plain words.** Teaching the reader more documents and more words. Today it reads filed decisions and speaks on 38% of document days; this tree adds the documents that come *before* a decision (speeches, statements) and adds a vocabulary for sector shocks (a steel tariff currently scores "important, direction unknown"). It makes every other tree see more; it is not a strategy by itself.


Unchanged from TRACK §3.1–3.4: read the 4,595 political documents (~US$60), the four
intention-bearing sources (US$850–1,150), schema v2 sector axes (US$200–400 pilot), GDELT
structured route. Each judged by the registered source-expansion rule against the backfill
hash and, once T2 exists, by QLIKE improvement. **With T7 built, the marginal read cost of all
of this goes to ~$0** — which is why T7 outranks T5.

---

## T6 — Affordable LLM drift capture (the niche from your point 1)

**In plain words.** After the close, a company files bad news. Research shows the price keeps drifting the next day, but the profit is smaller than the cost of trading it — unless you are a market-maker. This tree does not try to be faster; it tries to be *choosier*: it estimates, for each filing, how much drift to expect and how much that name costs to trade, and it only acts when the first clearly beats the second. The daily output is often "twelve filings read; none clears your costs today" — and telling a user *not* to trade is the product.


**What the literature establishes.** LLM headline direction predicts the initial reaction
(non-tradable) and a 1–2 day drift of ~34 bps/day gross; the drift is concentrated in smaller
stocks and negative news; exploiting it is feasible only for participants with very low
costs; returns decline as adoption rises.

**What your own test established.** Large-cap 8-K announcers: day-1 open-to-close +0.012% once
entry was tradeable. There is nothing there for large caps.

**The design.** Not cheaper code — **selectivity and execution**:

1. Universe: US names with ADV$ between US$5m and US$200m (mid-cap, where spreads are wide but
   the drift lives), filings-based events only (8-K Item 2.02 / 8.01 / 1.01, EX-99), public
   domain, arriving after the close.
2. Reader: the existing schema on the filing; add one field, `expected_drift_bp`, calibrated
   *out of sample* from the backfill's (direction, magnitude, specificity) → realised
   open-to-close return on `t+1`, per size bucket and sign.
3. Cost model per name (§1): `cost_bp = 2·hs + impact(size)`.
4. **Trade rule (the product): act only if `expected_drift_bp > k · cost_bp`, k = 2 registered;
   otherwise the report prints "does not clear your costs".** Negative-news only in v1.
5. Execution: limit order into the opening auction at prior close − 0.5·spread (for shorts,
   +); unfilled = no trade; exit at the close of `t+1` (v1) or `t+2` (registered variant).
6. Position count capped (10 names/day); capital per name capped at 1% of ADV$.

**Track.**

| step | do | done when |
|---|---|---|
| 1 | Register `docs/prereg_llm_drift.md`: universe, event types, calibration method, k, execution rule, sample split by year, family {exit t+1, exit t+2}, null = within-event-type permutation; expected: gross positive on negative news; net at 3× ≈ 0 | committed |
| 2 | Data: fetch 8-K/EX-99 for the universe 2019–2026 from EDGAR ($0, slow: ~3–5k filings/yr); ADV and spreads from the raw cache (spreads need daily high/low proxy or a one-off quote snapshot) | on disk |
| 3 | Read: with T7 (free) or API (~US$0.02–0.10 per filing) — **this is why T7 comes first** | cache |
| 4 | Build `src/llm_drift.py`: calibration, cost model, rule, auction execution simulation, scoreboard scoring on the *traded* subset and on the *declined* subset separately (the declined subset is the abstention audit) | selftest |
| 5 | Run; record. The unique output is the declined-subset table: what the vendor told you not to trade, and what it did | written |
| 6 | If net at 3× > 0 on the split: daily block "cost-cleared events (N of M)"; else the block ships as "events read; none cleared costs today" — still a product | daily |

**Marketing half.** The trading half is for a user with a broker; the vendor sells the filter.
That is the business plan's thesis, made concrete: cost-aware abstention.

**Success 15–30%.** Stated because the two papers and your own test agree on where the edge is
and who can reach it.

---

## T7 — Distilled local reader (zero marginal cost)

**In plain words.** The reader you pay for by the document has already answered 2,616 questions. This tree trains a small free model, running on your own laptop, to give the same answers, then checks it on 300 documents it has never seen before it is trusted. If it passes, reading costs nothing from then on, the nightly cap disappears, and no client document ever leaves your machine — which matters to the compliance people in the business plan.


**Hypothesis.** A 7–8B open model fine-tuned (LoRA) on the 2,616 existing (document → JSON)
pairs reproduces the API reader's fields with registered agreement, so every future read costs
electricity, the nightly cap disappears, step 8 and T6 become free, and documents never leave
the machine.

**What the literature says.** 7–8B models fine-tuned on financial text reach or exceed larger
models on sentiment tasks; on FOMC minutes specifically, an open 70B model outperformed GPT-4
on a labelled set; LoRA fine-tunes of 7–8B run on a single consumer GPU or Apple silicon.

**Track.**

| step | do | done when |
|---|---|---|
| 1 | Register `docs/prereg_distilled_reader.md`: held-out 300 documents stratified by source (never trained on); agreement criteria — direction sign per axis ≥ 90%, specificity/novelty/confidence within ±0.15 MAE, stance exact ≥ 90%, JSON validity 100%; a **paired pilot** rule as in schema v2: distilled reads are a *separate corpus version* until the gate passes, never pooled | committed |
| 2 | Build the training set from `data_provenance/doc_reads` (input: document text truncated as the API reader saw it + the same prompt; target: the JSON) | 2,316 train / 300 held-out |
| 3 | Fine-tune: Qwen3-8B or Llama-3-8B-Instruct, QLoRA, on your Mac (M-series: MLX) or a rented GPU (~US$20–50); 3 epochs; constrained JSON decoding | model on disk |
| 4 | Gate: run the 300 held-out; compute the criteria; **run the specificity gate** (`gate.py`) on the distilled corpus of the same 300 | pass / fail recorded |
| 5 | Shadow month: the distilled reader reads every new document beside the API reader (when funded) or alone (when not) into a `v1-distilled` corpus; agreement tracked weekly | 4 weekly rows |
| 6 | If the gate passes and shadow agreement holds: `doc_read.py --model local` becomes the nightly default; the corpus version string changes; T5 and T6 proceed at $0 | switched |

**Compliance note for the plan.** A local reader means client-relevant documents are never sent
to a third party — a sentence a compliance function will read.

---

## T8 — Announcement-day premium × regime, plus a document risk calendar

**In plain words.** Most of what the stock market pays investors for holding risk arrives on a few scheduled days a year — Fed decisions, jobs numbers, inflation prints — about one day in eight. This tree asks whether your regime engine can tell *which* of those days pay most, and puts a calendar in the report: "Thursday: Fed decision — in this regime those days have paid +14 bp on average." A trader uses it to be invested when the market is paying and lighter when it is not, at almost no trading cost.


**What the literature establishes.** The average excess stock return is about 11.4 bp on the
~13% of days carrying a scheduled macro announcement (FOMC, employment, CPI, PPI) versus about
1.1 bp on other days; the CAPM holds on those days and not otherwise; the pattern persisted
after publication. The premium is described as conditional on the information environment,
which is the invitation to regime-condition it.

**Hypothesis.** (a) The announcement-day premium is present in your panel 2006–2026 for SPY and,
with maturity, for TLT; (b) it varies by regime — larger when the regime posterior is low or
the regime is "stress" — and (c) the reader's document count and specificity on the day add to
the calendar dummies.

**Daily output.**
```
CALENDAR   Thu 17 Sep: FOMC decision (scheduled)  — historical SPY announcement-day premium in regime 3: +14 bp (n=61), non-announcement days +1 bp
           expected |move| from T2: 1.4× baseline.   Dial: T1 exposure applies; announcement overlay +0.15 (registered T8 rule)
```

**Track.**

| step | do | done when |
|---|---|---|
| 1 | Register `docs/prereg_announcement_premium.md`: the calendar (FOMC decision dates already fetched; add BLS employment, CPI, PPI release dates — public); hypotheses a/b/c; test = mean excess return on A-days vs non-A-days with HAC t, then A-day return regressed on regime dummies and posterior, then + document fields; strategy = hold SPY on A-days only vs always (cost: 2 trades per A-day at §1) and regime-tilted variant; family; split | committed |
| 2 | Data: release calendars 2006–2026 from BLS and the Fed ($0) into `data_provenance/calendar/` | on disk |
| 3 | Build `src/announcement_premium.py`; acceptance: on a synthetic panel with a planted A-day premium the test recovers it; with none, rejects ≤ 8% | pass |
| 4 | Run; record | written |
| 5 | Wire: the calendar block into the report with the historical premium per regime printed; the announcement overlay into T1's dial if (b) passes | daily |

**Costs.** ~120 A-days/yr × 2 SPY trades × 1 bp = 2.4 bp/yr. Trivial. **Capacity.** SPY: effectively
unbounded at your scale.

**Test A / Test B (v2.1).**

| | Test A | Test B |
|---|---|---|
| universe | SPY (time series), TLT | **U-ETF30, cross-section** |
| hypothesis | announcement-day premium; regime dependence | on announcement days beta is priced (the security market line holds); a **beta-sorted long-high/short-low portfolio held only on A-days**, regime-conditioned, earns the announcement-day beta premium; on non-A-days it earns nothing |
| construction | as above | expanding 252-session betas to SPY; terciles; long top / short bottom, entered at the close before an A-day, exited at its close; costs per name; regime split of the A-day SML slope |
| registered expectation | premium present; regime interaction uncertain | A-day SML slope > 0 and non-A-day slope ≈ 0 (the published pattern); the *regime* dependence of the slope is the new claim and gets the prior "uncertain" |
| extra risk | — | 30 assets × 2 trades × 120 days = 7,200 trades/yr — costs are the binding constraint; report break-even bp |

---

## T9 — Text-derived path factor → post-FOMC bond drift

**In plain words.** When the Fed speaks, bond yields react a little on the day and then keep moving for weeks in the same direction, because investors adjust slowly. Your reader already tells apart *what the Fed did today* from *what it said about the future*. This tree tests whether that reading of the future — extracted from the words, for free — predicts which way the weeks-long bond drift goes. Eight decisions a year, one trade each, costs negligible.


**What the literature establishes.** Treasury yields underreact to Fed Funds surprises and drift
for weeks: the same-day response of 10-year yields to a 10 bp surprise is ~1.7 bp, but after 50
days ~14 bp; the mechanism is slow adjustment of extrapolative expectations and mutual-fund
flows.

**What your reader already does.** It separates `stance` (today's decision) from
`direction.duration` (what the text implies for bond prices); six genuine hikes read with
positive duration because their guidance was dovish. That is a *text-derived path factor* —
the target/path split that the standard method extracts from futures prices, which you don't
have — at zero data cost.

**Hypothesis.** Sign and size of the reader's duration reading on statement day predict the
sign of the 10–50-session drift in TLT (and IEF) after FOMC, beyond the announcement-day move
itself; the effect is regime-dependent (your FOMC→GLD-by-regime finding suggests the
flat-curve/strong-dollar regime behaves differently).

**Track.**

| step | do | done when |
|---|---|---|
| 1 | Register `docs/prereg_text_path_factor.md`: events = FOMC statements 2006–2026 (n ≈ 160); features = stance, `direction.duration`, specificity, novelty, announcement-day TLT return; outcome = TLT return over sessions [2, 20] and [2, 50]; test = sign agreement rate vs within-regime null; family {20, 50}; split; strategy = hold TLT in the reader's direction for 20 sessions after each statement, 8×/yr, at §1 costs | committed |
| 2 | Build `src/text_path_factor.py` on the read CSVs and the panel | selftest |
| 3 | Run; record. Prior: the announcement-day move alone predicts the drift (that is the published finding); the question is whether the text adds — expect a modest addition in the hike/dovish-guidance cases | written |
| 4 | Wire: on statement days, the report prints "path reading: dovish guidance under a hawkish decision → historical 20-session TLT drift in this regime: +x% (n)" | 8×/yr |

**Costs.** 16 TLT trades/yr × 1 bp. **Capacity.** TLT ADV ~US$3bn; unbounded at scale.

**Test A / Test B (v2.1).**

| | Test A | Test B |
|---|---|---|
| universe | TLT, IEF | **U-Curve**: SHY, IEF, TLT, EDV, TIP, MBB, LQD, HYG |
| hypothesis | text path factor predicts the 20/50-session drift | the drift and the text factor's predictive power **increase with duration** along the ladder and **spill into MBS and credit** (the published spillover), while TIP separates the real-rate component |
| registered expectation | modest addition over the announcement-day move | monotone in duration (SHY < IEF < TLT < EDV) on sign-agreement rate; LQD/HYG in the same direction with smaller magnitude; TIP weaker — a monotonicity test, one p-value, not eight |
| extra risk | — | eight assets, one family; the ladder is one hypothesis, not eight |

---

## T10 — Surprise / novelty engine

**In plain words.** Markets move on *surprise*, not on news. Your reader already scores how different each document is from the previous one from the same source — a surprise meter. Short branch: big surprises should mean big moves over the next few days, whatever the direction. Slow branch: companies that quietly change the wording of their filings tend to do worse over the following months — a slow, cheap-to-trade signal. This tree tests both.


**Two branches from one field.** The reader's `novelty` — computed with the previous document
of the same source in context — is a text-based *surprise* measure. FOMC statements read at
the lowest novelty of all sources (0.289), which is correct: they are the most telegraphed
documents in finance. Novelty is where the unexpected component lives.

**(a) Short branch.** Novelty × specificity predicts the size of the 3-session move and the
*persistence* of post-event volatility (extends T2 with an interaction and a 5-session RV
outcome). Register as an amendment to T2 rather than a separate file.

**(b) Slow branch — the affordable route by construction.** Changes in filing language predict
returns over the following months (the "lazy prices" finding on 10-K/10-Q text); a long-short
on low-novelty vs high-novelty filers rebalanced quarterly has turnover a retail account can
afford. Your version: (i) the reader's novelty on 10-Q/10-K risk-factor and MD&A sections
rather than cosine similarity; (ii) regime-conditioned — does the effect concentrate in
particular macro states; (iii) the 47-name universe first, then a 200-name liquid extension.

**Track (b).**

| step | do | done when |
|---|---|---|
| 1 | Register `docs/prereg_filing_novelty.md`: sections read, novelty definition, quarterly formation, holding 63 sessions, long low-novelty / short high-novelty (the published direction — state it as the prior), costs per name from §1 model, family {47 names, 200 names}, split | committed |
| 2 | Fetch 10-Q/10-K sections for the universe 2010–2026 via EDGAR ($0) | on disk |
| 3 | Read with T7 (free) or API (200 names × 4/yr × 16 yr ≈ 12,800 reads — **only affordable with T7**) | cache |
| 4 | Build `src/filing_novelty.py`; run; record | written |
| 5 | Wire: quarterly "novelty tilt" block; per-name novelty shown on the asset page | quarterly |

**Costs.** Quarterly turnover; ~200 names × 4 × per-name spread ≈ 40–80 bp/yr — survivable.
**Capacity.** Liquid 200: US$50–100m before impact binds.

---

## T11 — Unprecedentedness index (+ the disagreement branch)

**In plain words.** One number a day for "how unfamiliar is today compared with everything since 2006?" The report already abstains when it finds no precedent; this tree turns that into a dial reading: "today is in the top 10% of unfamiliar days." Unfamiliar days are where drawdowns live, so the number feeds straight into how much to own. The side branch checks whether days when the reader and history *disagree* are the big-move days.


**The idea no paper has.** Your report already computes, every day, how far today is from
history: the number of precedents, the ESS, and whether it abstains for lack of any. Aggregate
that into one daily number — **how unprecedented is today** — and test it as a risk indicator.
The nearest published relative is the turbulence index (Mahalanobis distance of returns from
their history), which predicts drawdowns; yours adds the macro state *and* the document state,
and it comes free from the pipeline.

**Definition (register exactly).** `U_t = w₁·(1 − ESS_t/ESS_max) + w₂·D_macro(t) + w₃·D_doc(t)`
where `D_macro` is the Mahalanobis distance of today's PC vector from the expanding history
within regime, `D_doc` is the share of today's documents whose (source, specificity, novelty)
cell has fewer than 8 precedents, and the weights are fixed at ⅓ each *before* any test.

**Hypothesis.** High `U_t` predicts higher next-5-session realised vol and larger drawdowns;
feeding `U_t` into T1's dial (`w × (1 − φ·U_t)`, φ registered at 0.5) improves CER net of
costs.

**Disagreement branch.** The 27 Aug test found discordant reader-vs-history cases outperformed
concordant ones by 0.21%. Register the *magnitude* version: disagreement predicts a larger
absolute move (uncertainty), tested as a T2 regressor — not a direction claim, and not a
second look at the sign.

**Track.**

| step | do | done when |
|---|---|---|
| 1 | Register `docs/prereg_unprecedentedness.md`: definition above; outcomes (RV₅, 20-session max drawdown); tests (HAR + U_t, DM; drawdown quintile by U_t); T1 integration criterion; disagreement as a T2 regressor with its own DM test; split | committed |
| 2 | Build `src/unprecedented.py` from the backfill's per-report fields (ESS, n_matched, PCs, document cells) | runs |
| 3 | Run; record | written |
| 4 | Wire: the report's first line becomes "today is unprecedented at U = 0.62 (top decile since 2006)", with the two components named | daily |

**Costs / capacity.** Inherits T1.

**Test A / Test B (v2.1).**

| | Test A | Test B |
|---|---|---|
| definition | `U = ⅓(1 − ESS/ESS_max) + ⅓ D_macro + ⅓ D_doc` | **four components**: add `D_asset` = Mahalanobis distance of today's U-ETF30 return vector from its expanding covariance (the turbulence index proper), weights ¼ each, fixed before running |
| what B adds | — | the cross-asset dimension your regime engine does not see (a day when correlations break) |
| registered expectation | U predicts RV₅ and drawdowns | B's U has higher rank correlation with next-20-session drawdown than A's; and `D_asset` alone is *not* sufficient (else the document layer adds nothing — that is a legitimate outcome and would be published) |

---

## T12 — Regime engine v2: asset-return and jump features, built beside v1

**In plain words.** The current weather station reads eight macro dials once a day and sorts
the day into one of four seasons. It never looks at what prices themselves are doing — how
jumpy they are, whether assets that usually move apart have started moving together. This tree
builds a second weather station that adds those readings, runs it *next to* the first one, and
only replaces it if every downstream tree does measurably better on the new seasons. It is the
one tree whose success lifts all the others.

**Why it is the foundation.** Every tree above inherits the regime label. v1's labels are
persistent (good) and structurally best at n=4 (good) but *weakly corroborated externally*
(the event-alignment claim collapsed in Week 13) and blind to price behaviour. The literature's
best-performing regime models for allocation use realised volatility and jump-penalised
persistence, not macro levels alone.

**Design.**

| component | v1 (today) | v2 (beside it) |
|---|---|---|
| features | 8 FRED series, forward-filled, PCA | v1's PCs **plus** U-ETF30 realised vol (20-session), cross-asset average correlation (60-session), equity–bond correlation sign, credit spread (HYG − LQD return differential), all expanding-standardised |
| model | GMM on PCs, n=4, expanding refit every 20 sessions | **jump model** (Nystrup, Kolm & Lindström 2020/2021: clustering with an explicit penalty on state changes), n ∈ {3, 4, 5} selected by the same three criteria as v1 (seed-stability ARI, median run length, silhouette) — plus a **statistical jump model** variant if time allows |
| persistence | emergent | enforced by the jump penalty λ_jump, fixed before running at the value that reproduces v1's median run length on v1's features |
| look-ahead | declared full-panel PCA | same declaration; the asset features are expanding by construction |

**Track.**

| step | do | done when |
|---|---|---|
| 1 | Register `docs/prereg_regime_v2.md`: features, model, n-selection criteria (copied from v1's, unchanged), λ_jump fixing rule, the downstream criterion below, the switch protocol from TRACK §3.5 (build beside, validate, switch only on pass; the app reads whichever artifact is marked current) | committed |
| 2 | Build `src/regime_v2.py` producing `processed/regime_labels_v2_expanding.parquet` beside v1's; acceptance: on synthetic data with planted regimes, v2 recovers them with ARI > 0.9 and v1's own re-run reproduces v1's labels exactly | pass |
| 3 | Validate v2 on its own terms: stability, run length, silhouette, and the event-alignment test that v1 failed — reported, with the prior "v2 may also fail it" | tables |
| 4 | **Downstream criterion (the only one that authorises a switch):** re-run T1(A), T8(A), T2(A) with v2 labels in place of v1; v2 is adopted only if at least two of the three improve their registered primary metric net at 3× costs on the split, and none degrades by more than its tolerance | verdict |
| 5 | Record; if adopted, the report shows both labels for 60 sessions ("v1 regime 3 / v2 regime 2") before v1 is retired to the record | switched or not |

**Danger.** Any change to the regime labels moves every result in the repository. Step 4 exists so
that the switch is justified by *downstream* value, not by v2 looking nicer in-sample. Nothing in
`models.yaml` changes; the frozen forward test keeps v1 forever by construction.

## T13 — Blind-spot monitor and provisional source pool

**In plain words.** On 17 September gold rose 2.5% and silver 3.9% because a Saudi oil pipeline
was being repaired faster than feared — and the engine's sources (Fed statements, filings,
executive orders) will never contain that. Worse, the Fed *had* just spoken, and a confident
reading of that document alone would have said "metals down." This tree does two things about
that. First, it notices when the market moves much more than the day's documents can account
for, and says so: *"metals moved 2.8× what our sources explain — we are blind here today."*
Second, when it finds the likely driver, it puts that source class into a **waiting room**
(the provisional pool) where it is read every day, ranked every day by how much it actually
explains, and allowed to fade out on its own if it stops mattering. A source earns its way in
by measurement, never by hindsight.

**Why it exists.** Adding more sources on the *same* blind side (a press conference, a speech)
raises confidence without raising coverage — the exact failure that would have lost money on
17 Sep. Coverage has to grow where the misses are, fast enough to matter (a war that ends
before its source is validated is a useless source), and without breaking the rule that the
validated corpus and its backfill baseline stay comparable.

**What is genuinely ours, and what is not.** A link to an article is worth nothing; search is
free. What a customer cannot reproduce: (1) *the detection* — "this move is 2.8× what the
day's documents and the regime account for" needs the expected-move model, the coverage map
and the regime engine; (2) *the attribution over time* — "commodity-supply events now carry an
explanatory score of 0.34 for metals, up from 0.08 a month ago" is a measured property of the
customer's assets; (3) *the self-distrust* — "our validated corpus says short; the driver is
outside it; confidence on metals is haircut to 0.4 today." The third is the product. Article
text is never stored or shown; a one-line description and a URL are a citation.

### 13.1 Detection — three cases, testable on the backfill today

For each asset `a` and session `t`, with `E|r|` the expected absolute move from T2 (or, until
T2 exists, the HAR-RV baseline) and `z = |r_{a,t}| / E|r|_{a,t}`:

| case | condition | what it means | behaviour change |
|---|---|---|---|
| **A** | `z > 1.5` and no document dated `t` touches `a`'s axis | engine was silent, correctly | none — but the day is logged: this is where the blind spots are found |
| **B** | `z > 1.5`, a call was issued, realised sign **opposite** | something invisible overran a confident read | the *forward* haircut below |
| **C** | `z > 1.5`, a call was issued, realised sign same | right, possibly by accident | logged for honest attribution |

Nothing is ever suspended retrospectively — a published call stays in the ledger. The only
behavioural change is forward: `haircut_a = 1 − φ · B_rate_a`, where `B_rate_a` is the
exponentially-weighted share of case-B days for asset `a` (half-life 20 sessions) and φ is
fixed at 0.5 before running. It multiplies the displayed confidence of the next call on `a`;
it never changes `net_view` or the estimate. The registered detection test: on the 1,531-day
backfill, are realised outcomes on case-B days worse, and does the haircut applied one day
later improve hit-rate net of nothing (no trades change, only the displayed confidence)? Prior:
yes on the first, small on the second.

### 13.2 The search — forward only, structured output only

Nightly, for each asset flagged A or B: one API call with the web-search tool enabled, asking
what moved that asset on that date. The model returns **JSON only** — `driver` (one line),
`source_class` ∈ {geopolitical, supply_disruption, central_bank_speech, foreign_central_bank,
data_release, flows_positioning, corporate, other}, `url`, `confidence`, `covered_by_corpus`
(true/false). Appended to `processed/blind_spots.csv` and `docs/blind_spots.md`, never
rewritten. Cost: 1–3 searches a night, about US$1–2 a month. Historical dates are not
searched — the search half is forward from the day it is switched on; the detection half runs
on history.

### 13.3 The provisional pool — fast in, measured, decays out

A source class enters the pool **the day it is proposed**, with a dated `admitted` field. It is
fetched (official or public-domain sources only; GDELT structured records; company IR), read by
the **same reader under the same prompt version**, and shown on the report in its own block,
labelled *provisional*. It never touches the corpus hash, the backfill baseline, the §7.2
weighting, or `net_view`.

**Admission is dated, and a source is scored only on days after its admission.** Worked
example: on 17 Sep the search finds the pipeline story and `commodity_supply` is admitted with
`admitted: 2026-09-17`. That day's move does **not** count — the source starts at n = 0 and
"too few to rank." From 18 Sep every reading is scored against that day's residual; by late
October it has ~25 scored days and a real rank. Without this rule every source would arrive
with a perfect score on the one day it was picked *for*.

**Two scores, never merged.** For source `s`, asset `a`, at date `T`, with `z_{a,t}` the
standardised residual from T2 and `d_{s,a,t}` the source's signed reading on `a`'s axis:

```
w_t     = 2^(−(T−t)/H)                       H = half-life in sessions, registered at 40, never swept
E(s,a)  = [Σ w_t z_{a,t} d_{s,a,t}]² / [Σ w_t z²_{a,t} · Σ w_t d²_{s,a,t}]      explanatory (same day)
P(s,a)  = same with z_{a,t+1:t+3} in place of z_{a,t}                            predictive (h = 3)
ESS     = (Σ w_t)² / Σ w_t²                  below 20 → "too few to rank", as everywhere else
C(s)    = EW share of sessions on which s produced a reading                    coverage
```

`E` says the source is *relevant* to that asset; `P` says it is *tradeable*. A source can be
high on `E` and near zero on `P` — most news is, by this project's own findings — and that is
not a failure: the Week-6 customer conversations said a buy/sell number would be ignored but
"a structured view of why an asset moved" would be read. Explanation is the validated value
proposition. The short half-life means a source that stops mattering **decays out of the
ranking on its own**; the war-ends case needs no manual removal.

**Display — Sort A, decided 17 Sep.** The block ranks by `E`, shows `P`, `n`, `ESS` and
status beside it, and never sorts by `P` by default: at these sample sizes a 0.04-vs-0.02
ordering on `P` is noise and would invite a customer to trade a number that is not there.

**Graduation to the validated corpus** — only by the registered step-8 rule (coverage gain,
pooled hit-rate not down by > 2 points, lower bound > −5, specificity gate re-run), *and*
`E` sustained above 0.15 with ESS ≥ 30 for 60 consecutive sessions. Until then it is useful on
the report and absent from every registered estimate.

**De-duplication when the pool is large.** Once it holds ≥ 20 source classes with overlapping
readings, PCA on the source-reading matrix finds the three or four independent "news factors"
and removes double-counting — GDELT's one-event-two-hundred-records problem, solved where it
belongs. PCA is the wrong tool for *ranking* (that is a supervised question) and the right tool
for *de-duplicating*.

### 13.4 Track

| step | do | done when |
|---|---|---|
| 1 | Register `docs/prereg_blind_spot.md`: the z-threshold 1.5, the three cases, φ = 0.5, H = 40, ESS floor 20, the graduation rule, Sort A, the dated-admission rule, the "never store article text" rule, and the backfill detection test with its prior | committed |
| 2 | Build `src/blind_spot.py` detection on the backfill; acceptance: planted case-B days are recovered; a shuffled ledger produces the base rate | pass |
| 3 | Run detection on the 1,531-day backfill; record case rates per asset and the case-B outcome test | written |
| 4 | Build the nightly search call (`src/blind_spot_search.py`), JSON-only, appended to the log; wire into `daily_run.sh` after 6c/7 | first entries |
| 5 | Build the pool: `config/provisional_sources.yaml` (name, class, fetch route, `admitted`), reader profile per class, `src/source_pool.py` computing E/P/C/ESS nightly, block in `step6_report.py` and `app.py` | block shows "too few to rank" |
| 6 | First admissions: `commodity_supply` (official OPEC/EIA/ministry releases), `foreign_central_bank` (BoJ, ECB statements — amendment iii), `central_bank_speech` (Fed speeches, already costed in TRACK §3.2) | rows accrue |
| 7 | Monthly: graduation check; PCA de-dup once ≥ 20 classes | §5 rows |

### 13.5 Test A / Test B

| | Test A | Test B |
|---|---|---|
| universe | U5 | U-ETF30 |
| what B adds | — | sector ETFs make case A informative for sector shocks the five axes cannot represent (a steel tariff, a chip export control) — the same days schema v2 is for |
| expectation | case rates ~5–10% of asset-days; case-B days worse | case-A rate higher on sector ETFs than on U5; that gap is the coverage-gap measurement schema v2 needs |

**Costs / capacity.** Inherits T1. **Knowledge.** PhD — the null for "worse outcomes on case-B
days" is a dependent-sample problem, and the pool scores need the same care as any EW
regression.

### 13.6 Four amendments from the 17 Sep discussion (US and Japan hiked; long ends diverged)

A Fed hike into a fully priced expectation is credibility-positive at the long end — the 30-year
can rally as the 2-year sells off. A BoJ hike removes yield suppression — the 30-year JGB rises.
Same instrument, opposite long-end response, because the *starting regime of each central bank*
differs. The engine cannot see this today for three separate reasons, each amended in a
different place:

| blind spot | where it lives | amendment |
|---|---|---|
| macro panel is eight **US** series | T12 feature set | add JGB 30Y, BoJ policy rate, USDJPY, and a US–JP long-end spread (FRED carries the first three; the spread is derived) |
| `direction.duration` implicitly means **US** duration | schema v2 (`docs/prereg_schema_v2.md`) | add a `jurisdiction` field per document and split the axis into `duration_us` / `duration_foreign` — the same defect as the steel tariff: the reader sees it clearly and has no field to report it in |
| corpus is Fed, SEC, Federal Register — **US only** | sources | `foreign_central_bank` as a provisional class (13.3), entering through the pool, not the corpus |
| reading every foreign document costs credit | **PCA spend-gate** | a rolling PCA on a multi-country long-yield panel (US, JP, DE, UK 10Y/30Y): when US and JP long ends load on the same factor, the existing US duration reading covers both and no foreign read is spent; when their loadings diverge (same direction for different reasons, or opposite directions), the foreign document is read. The decoupling state itself is a T12 feature. |

The trading relevance is not academic: Japanese repatriation flows sell Treasuries, so JP 30Y is
a TLT input. LLM and PCA answer different questions here — PCA says *whether* the two long
ends have decoupled; the reader says *why*.

### 13.7 Parked here, not erased — an idea from 17 Sep still to finish

"Most news does not predict" is a finding about five macro ETFs at h = 3, not a law. The
founder's observation from his own trading: large-cap technology names on catalyst days
sometimes show a gentle, steady intraday trend from before the open to after the close, unlike
metals, where the move is over in the gap. That is a distinct hypothesis — different universe,
intraday bars needed, a different entry — and it belongs to T6 as a registered variant once the
sentence is finished. Recorded so it is not lost.

## Execution calendar (first two weeks)

| day | tree | step |
|---|---|---|
| 1 | T1 | register; T3 overlay files 1–3 written in parallel |
| 2 | T1 | acceptance tests, build |
| 3 | T1 | run, record; T8 register |
| 4 | T8 | data, build, run, record |
| 5 | T2 | register, build |
| 6 | T2 | run, T1 re-run with M1's σ̂, record; T11 register |
| 7 | T11 | build, run, record; T3 overlay ledger wired |
| 8–10 | T12 | register, build beside v1, validate, downstream re-runs of T1/T8/T2 on v2 labels (this is also the Test B week for T1, T8, T2) |
| 11–13 | T7 | register, training set, fine-tune, gate |
| 14–15 | T9 on U-Curve; T11 Test B | register, build, run, record |
| 16–17 | T10(a) as T2 amendment; T4 register | — |
| when T7 passes | T5 at $0; T10(b); T6 | — |

Each tree ends with its block in the report, verdict printed beside it, and a §1 row in TRACK
for whatever it leaves running.

---

## §fomc_minutes — the registration text (so it exists before any second look)

```
docs/overlays/fomc_minutes_contrarian.md

hypothesis:  on sessions where fomc_minutes is the dominant source for asset a, the report's
             net_view sign is WRONG more often than chance: forward non-overlap hit-rate at h=3
             below the within-asset null's 5th percentile.
origin:      backfill 986e0d65b6df_n2616, 14 Sep 2026: 37.8% on 74 rows, found by looking.
data:        FORWARD ONLY. The backfill rows that produced the observation are excluded from
             the test by construction; no chronological re-cut of the backfill counts.
minimum:     30 non-overlap forward rows (≈ 1 year at 8 minutes/yr × 5 assets, if reads resume).
falsifier:   hit-rate at or above the null's 5th percentile after 30 rows → hypothesis dropped;
             a positive result → registered as an overlay rule (take the opposite side, size
             0.25 × dial), NOT as a change to the reader.
code:        src/overlays.py filter on dominant_source == "fomc_minutes"; reads
             processed/report_ledger.csv; prints "too few to report" until the minimum.
blocked by:  nightly reads (paused for credit) — no minutes-driven calls are generated until
             they resume.
```


---

# APPENDIX C — MODEL_EVOLUTION.md (as of 13 Sep 2026)

> *Superseded by this master; kept verbatim as the external-reader record of every price model.*

# How the models evolved

*A record for readers outside the project — investors, a supervisor, a
prospective client — of every model this project has run, what each one was
for, what it found, and what is registered next. Written 2026-09-08, last
edited 2026-09-13. Every
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
| **Backtest** | Sharpe **0.51** on 47 assets, 837 weekly rebalances 2010–2026 (838 by 8 Sep as the panel extends; the kernel-family run reports 0.54 on the longer sample) |
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


---

# APPENDIX D — CURRENT_STATE_2026-08-23.md (the evidence record, §1–18)

> *Live, append-only file in the repo; snapshot as of 15 Sep. Every number in Part A traces here or to a file it names.*

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

### 18.5 NEXT CODE ITEM — DONE `e761072`, 14 Sep, before the 15:00 run

Implemented as written below. First test: `--pending` listed 20260911; `--date 20260911`
deferred with two unread executive orders dated 11 Sep listed by name. Confirms the
defect: without the guard, the first write-once report would have been frozen empty.
Reports now accumulate as PENDING until reads resume, then are written oldest-first.

*Original item, for the record:*

`step6_report.py`: (a) refuse to write a report for a session that has fetched-but-
unread documents (count files under `data_provenance/docs/<source>/` dated that
session with no entry under `doc_reads/`), printing the count and "deferred"; (b) a
`--pending` mode that lists completed sessions with no report on disk, so
`daily_run.sh` can loop `--date` over them once reads resume. Neither is written yet.

### 18.6 STEP 7 — THE BACKFILLED REPORT SCOREBOARD, FIRST RESULT (14 Sep, 14:30)

*The first hit-rate this project has produced for the decision report. Recorded here
before any interpretation beyond the registered criterion.*

**Setup.** `build_report` re-run as-of over every document-bearing labelled session
(1,531 dates), same function, prompt version and model as the live reports; precedent
pool `session ≤ t − 3` (registered 14 Sep, closes the backfill look-ahead); expanding
regime labels and standardisation; corpus hash `986e0d65b6df_n2616`. Scored by
`src/report_scoreboard.py` — the same scorer as the forward ledger, seven acceptance
tests passed — at the registered 10,000 permutations and 2,000 bootstrap draws.

**Coverage.** 803 document days; the report issued at least one net view on 585 (38%).
Asset-days: 1,026 call, 844 abstain, 51 divergence, 5,734 no-document. SPY accounts for
511 of the 1,026 calls.

**Primary cell — h=3, close-to-close, non-overlap, n=345.**

| | value | criterion | met |
|---|---|---|---|
| hit-rate | 59.4% | > null 95th pct (59.1%); p 0.0497 | yes, by 0.3 pts |
| asymmetry | 1.116 | > 1 with 95% block-bootstrap lower bound > 1; CI [0.910, 1.402] | no |
| verdict | **INCONCLUSIVE** | both required | — |

The null's 95th percentile is 59%, not ~50%, because permuting calls within asset
preserves each asset's call mix and its drift. A report that said "up" on SPY every day
lives inside that null. The report clears it by 0.3 points at p 0.0497 — the same
boundary the kernel family sat on (§5 of `docs/kernel_family.md`, Mahalanobis 0.0498)
and it earns the same sentence: a real but weak effect, or none; not separable here.

**Secondary cells (reported, not tested).** h=3 tradeable 57.1%; h=5 close-to-close
54.3%, tradeable 49.5% (mean signed −0.05%); h=20 non-overlap n=54, 59.3%.

**Breakdowns (reported, not tested).** By asset: SPY 68.4% (n=171), USO 55.6%, TLT
53.4%, UUP 47.6%, GLD 44.7%. By tier: tier 2 51.5% (n=66) < tier 3 57.5% (n=273); tier 1
n=6, too few — §6.1's expectation is unevaluable, and what is visible does not show the
tiers grading. By dominant source: `earnings_8k` 62.4% (n=117); `fomc_minutes` 37.8%
(n=74). The last is below a coin flip on 74 rows; if it held it would mean the reader's
sign on minutes is reversed or the market has priced them. It is a hypothesis for a
registration, not a finding, and no test is run on it here.

**What this is the baseline for.** Every step-8 source is judged against this hash by
the registered rule (§8 of the prereg): coverage must rise by the registered amount and
pooled hit-rate on shared days may not fall by more than 2 points (point estimate) with
bootstrap lower bound above −5.

**Repair found by the run.** The scorer's timestamp columns were all-NaN float and
refused a string on the first real write. Fixed in scorer and backfill; the seven
acceptance tests do not cover ledger maintenance and did not catch it.

**Not claimed.** No live figure — the forward ledger has zero rows. No per-asset, per-tier
or per-source significance. Nothing in this section reaches any external document.



---

# APPENDIX E — Pitch deck text (10 slides, 28 Aug 2026)

> *Extracted from Pitch_Deck.pptx; the deck itself is unchanged.*


### Slide 1

Regime-Aware Signal
A cross-asset signal service that tells fiduciaries when it does not know
Hsu Wei-Ting  ·  NUS MSc Finance  ·  August 2026
Seed round: S$139,265 for 18 months

### Slide 2

A fiduciary cannot defend a number they cannot source
The buyer is not short of signals. They are short of signals they can put in front of a committee.
1
The explanation is the deliverable, not the number
An allocator must justify a decision after it loses money. Every existing vendor sells a score; none sells the reasoning, the precedent set, or the confidence attached to it. That gap is what gets a product declined in diligence.
2
A vendor that is always confident is uninformative
If a feed produces a view every day, the buyer cannot tell the days it knows from the days it is guessing. Distinguishing those is worth more than being right slightly more often.
3
Nobody has industrialised policy text
Fed statements, filings and executive orders move markets and are read by hand, one desk at a time. There is no cheap, consistent, auditable machine reading of them — and the cost of building one has collapsed.
The third is the opening. The first two are why the buyer pays for it.

### Slide 3

What the product does
Five steps, every trading day, nothing hand-adjusted
1
Locate
Eight macro series place the day in one of four monetary environments.
2
Read
Every Fed statement, earnings release and executive order published that day is classified by a language model — what it says, how specific, how new.
3
Combine
Multiple documents are weighted by size, specificity, novelty and confidence. Where two disagree, both are shown and neither is combined.
4
Compare
Past situations matching both the macro state and the document reading are located and weighted by similarity and recency.
5
Report, or refuse
Fewer than eight genuinely comparable precedents and no number is issued.
The fifth step is the product. On most days, for most markets, the honest answer is that no usable precedent exists — and the tool says so.

### Slide 4

The expensive part is already behind us
A decade of policy and company text, machine-read into one schema, running daily without a human in the loop.
2,616
documents read, classified and stored
~US$150
total inference spend to build the corpus
5,194
trading days of macro state, 2006 to today
0
marginal cost of adding a market
Why the cost line is the business
A hedge fund pays an analyst more in a week than this corpus cost to build outright. The instrument was the capital expenditure and it is spent.

Adding a market costs nothing — the same reading is reused. Adding an entire new document source runs to tens of dollars, not hundreds of thousands.
Already fetched, waiting on capital
4,595 further policy documents, sourced at zero cost — roughly US$60 of inference from being live
Any listed instrument addable on request, no new reading required
A sector-aware extension specified, costed and pre-registered
A working demonstration terminal exists today. A prospect can operate it unaided.

### Slide 5

The advantage is the instrument, not any one signal
Three things exist separately in this market. Nobody has put them in one product.
Regime conditioning
Ask not what a document says, but what it meant the last time the macro backdrop looked like today.
Machine-read policy text
Every filing and order classified on one schema, at a cost that makes daily coverage trivial.
A fixed rule for silence
Written before any result was seen, so the vendor cannot rationalise a view when the evidence is thin.
And a second asset that compounds while the first is being sold
Twenty-seven documented cases where a plausible market belief was tested and overturned — each with the criterion that judged it, fixed in writing beforehand. Competitors cannot publish theirs without admitting they have them. A null result never expires, never gets arbitraged away, and is worth more to a risk committee than another buy signal.
Sold as a feed, this is a subscription. Sold as a standard, it is infrastructure others report against.

### Slide 6

Market and beachhead
Narrow first, by regulatory burden — not by enthusiasm
The ceiling we design to
30
accredited-investor clients — the statutory limit of the exemption we operate under, and the reason retail comes last rather than first.
Beachhead
Singapore boutiques and single-family offices
~250 firms
estimate
Adjacent
Regional independent managers, HK and ASEAN
~1,200 firms
estimate
Eventual
Global data-vendor market for factor and regime feeds
precedent: Barra, RavenPack
reference
* Firm counts are structural estimates from public registers, not primary research. No customer interviews have been conducted; the plan says so and dates the access plan.

### Slide 7

What competitors do, and the gap they leave
Everyone classifies regimes. Nobody publishes an abstention rule.
Regime labels
Document reading
Publishes failures
Refuses to call it
MSCI / Barra
Yes
No
No
No
RavenPack
No
Yes
No
No
Macro research desks
Yes
Manual
No
Sometimes, informally
Retail signal vendors
Marketed
No
No
Never
This product
Yes
Yes
Yes
Yes, by a fixed rule
The gap is not accuracy. It is calibrated refusal — a rule, fixed in advance, that decides when the vendor stays silent.

### Slide 8

How the money is made
One price, one ceiling, and a break-even that is eight clients away
The Phase 1 product
S$10,000
per firm, per year — unlimited users at that firm, plus a custom watchlist. Roughly 40% of a single Bloomberg seat.
3–6 clients
year one, one founder selling
S$30–60k
8 clients
break-even against the running cost
S$80k
30 clients
the statutory ceiling of the exemption
S$300k
Running cost, steady state: S$77,400 a year. Adding a client costs seconds of compute and no inference spend — the corpus is already read.
Then the price ceiling lifts, twice
Phase 2 — licensed feed
the regime label becomes an input other firms build on
Phase 3 — the taxonomy
others report against our definitions, as they do Barra's
Phase 4 — retail, licence-gated
$29 / $99 / $299 a month, deliberately last
Year one does not cover the cost base, and this deck does not pretend otherwise — that gap is what the round funds.

### Slide 9

What could go wrong
Stated plainly, because a diligence process will find these anyway
Regulatory
High impact
The 30-client exemption is our reading of the statute, not counsel’s. If it does not apply, the beachhead needs a licensed partner and the timeline slips.
Evidential
Measured 28 Aug
Under inference that respects serial dependence, only the model specified in advance survives (p 0.045). The survivorship-controlled subset does not (p 0.184), nor does the best of 54 grid configurations (family p 0.090).
Signal
Measured
One conditional cell of 45 survived correct inference. The product today sells process and abstention, not forecasting accuracy.
Costs
Measured, low
Turnover 23–25% per leg. Break-even is 60.6 bps per side against execution well inside that — this risk is smaller than assumed.
Coverage
Known
We read policy documents, not rhetoric. A market-moving statement that never becomes a filing is invisible to us.
Key person
Structural
One founder. The binding constraint on this venture is qualifying compliance personnel, not technology or capital.
* A full list of what the current evidence does not establish, with the test that would close each item, is section 3.3 of the business plan.

### Slide 10

Twelve weeks from zero to a running product
The instrument is what has been de-risked. The market is what this round tests.
Standing today
Instrument built, corpus read, demonstration terminal live and operable by a prospect unaided
Regulatory route identified and costed
Every threshold and every failure in version control, dated
What this round buys
Counsel opinion on the exemption
unlocks the first thirty clients
Cost and capacity analysis
the two questions every allocator asks first
Sector-aware reading
turns a macro view into a sector view
Founder, full-time
through first revenue
S$139,265
18-month runway to first revenue
No customers and no revenue yet — stated here rather than found in diligence. The base capital for a full advisory licence is deliberately not in this round; it is funded from Phase 1 revenue, which is why the accredited-investor beachhead was chosen.

---

# APPENDIX F — Business plan text (41 pages, revised 28 Aug 2026)

> *Extracted from Business_Plan.docx; the document itself is unchanged. Every commercial number is a labelled [HYPOTHESIS].*

Business Plan

A Regime-Aware Cross-Asset Signal Framework

Hsu Wei-Ting

MSc Finance, NUS Business School · BMF5391C Applied Faculty Project

Faculty Supervisor: Dr Lee Yen Teik

Revised 28 August 2026

Contents

Business Plan

A Regime-Aware Cross-Asset Signal Framework

Hsu Wei-Ting · MSc Finance, NUS Business School · BMF5391C Applied Faculty Project

Faculty Supervisor: Dr Lee Yen Teik · Date: 28 August 2026 (revised from 20 August against supervisor feedback and the project record through 26 August)

A note on evidence standards

Every substantive claim in this plan carries an evidence tag. This convention exists because the underlying research project adopted a working principle — every claim about project data must come from data actually run — and a business plan that abandoned that principle at the commercial boundary would be inconsistent with its own foundation.

  -----------------------------------------------------------------------------------------------------------------------------------------------
  Tag                                 Meaning
  ----------------------------------- -----------------------------------------------------------------------------------------------------------
  [VALIDATED]                         Tested against data, with a statistic and a p-value, under a criterion written before the result was seen

  [RETIRED]                           Previously claimed, since withdrawn — the withdrawal is cited, not deleted

  [BUILT]                             Running code, not yet formally validated

  [DESIGNED]                          Specified in detail, not yet built

  [PLANNED]                           Intended, dependent on resources not yet secured

  [HYPOTHESIS]                        Asserted, with the test that would falsify it stated
  -----------------------------------------------------------------------------------------------------------------------------------------------

Currency. All amounts are Singapore dollars (S$) unless marked US$. Inference and data costs are incurred in US dollars and are shown as US$; every cost, price and funding figure is S$.

Commercial assumptions — market sizes, pricing, conversion rates — are labelled [HYPOTHESIS] unless supported by primary evidence. At the date of writing, none are. Section 4.1 explains why, and what it would take to change that.

The research record behind this plan includes a log of 26 wrong priors — plausible beliefs the founder held and running code overturned, six of them in the two days before this revision. Several claims in the 20 August draft are marked [RETIRED] here for that reason. A plan that hides its retractions is less trustworthy than one that dates them; this one dates them.

1. Executive summary

Active market participants lose money for two distinct reasons that have nothing to do with picking the wrong instrument. The first is being positioned against the dominant macro regime — right about the asset, wrong about the environment. The second is subtler and, we believe, commercially unclaimed: after a major event triggers a thematic rotation, capital moves through a chain of related assets over days and weeks, and participants know a move is underway but not which asset moves next or when. Between headlines, they guess or sit out.

This venture builds a system that addresses both. A regime engine reads the macro state and matches current conditions to historically analogous periods, producing directional calls with factor attribution. An event layer detects rotation triggers from news and, conditional on those episodes, sequences the cascade. An LLM layer converts unstructured text into structured features and narrates the resulting scenarios — with all numerical inference handled by classical statistics whose properties are understood.

What exists today. The regime engine and the analog-matching directional engine are built and walk-forward tested on 837 weekly rebalances from 2010 to 2026, producing a Sharpe of 0.51 on the full 47-asset universe and 0.25 on the 35-asset long-history subset. Under dependence-correct inference, run on 28 August at the supervisor's request, only the first survives: p = 0.045 against p = 0.184 [§3.1 and §3.3]. Net of a realistic 10 bps round trip the first is 0.43; break-even is 60.6 bps. An earlier draft of this plan reported 0.60 and 0.43; those figures predated a calendar correction that removed ~196 manufactured rows, and are [RETIRED]. Three models are pre-registered, frozen and running in a version-controlled forward test that had zero matured trades at the date of writing [BUILT]. The event layer and the LLM document layer, listed as [DESIGNED] on 20 August, have since been built and tested: 2,616 documents read, a registered specificity gate passed, and the conditional estimator unblinded [VALIDATED — §3.1].

What was tested and failed. More than the earlier draft admitted, and every item below is in the repository with the criterion that judged it. The list now includes the survivorship-controlled backtest itself. Gold does not decouple from equities under liquidity stress (gap +0.017, p = 0.44). Rotation has no stable order — null across seven hypotheses and four instruments, with the two pairs that survived discovery both failing temporal splits. Post-event drift is null at its registered criterion. The one macro-event cell that met its criterion, FOMC→GLD at −0.3%, failed its temporal split at a 4.62× magnitude ratio. Of 45 document-conditioned cells, seven met the registered criterion and one survived a null that respects overlapping outcomes — inside the range expected by chance. A registered test of whether reader–history agreement predicts outcomes failed in the opposite direction. §3.3 lists what this evidence does not establish.

What this means for the product. The system that ships is one that abstains: it states the regime, the evidence and its precision, and declines to forecast where its own registered evidence floor is not met. That is the pivot to risk-management signals from July, delivered as measurement rather than assertion. The commercial claim rests on the process — a record of 26 logged wrong priors, every one caught by running code — not on a Sharpe.

The commercial position. The differentiator is not "AI applied to macro" — that market is contested by at least five funded competitors. It is the information-quiet gap: positioning along a cascade once triggered, when no fresh news is arriving. No identified competitor sells this.

The binding constraint is regulatory, not technical. In Singapore, issuing research analyses concerning investment products is a licensed activity requiring S$250,000 base capital and three qualifying individuals. The venture is currently one person. This inverts the intuitive go-to-market: the retail tier that looks easiest to sell is the hardest to serve legally, and the accredited-investor tier that looks hardest is reachable under an existing exemption. Section 8 sets out the resulting sequence.

Ask. Seed funding of S$139,265 (Section 12) for an 18-month runway to reach the first regulatory milestone and 30 paying accredited-investor clients — or, alternatively, an introduction to a licensed financial adviser willing to host the venture as an appointed representative, which would substitute for a substantial portion of that capital.

2. The problem

2.1 Regime blindness

Standard practice treats cross-asset relationships as stable, or at best as varying across discrete macro states. In practice, participants discover the regime has changed only after it has cost them. The information required to identify the shift exists — yields, dollar strength, volatility term structure, credit spreads, cross-asset correlation breadth — but it is distributed across sources and requires synthesis that most participants do not have time to perform daily.

2.2 The information-quiet gap

This is the sharper problem and the one the venture is built around.

Thematic rotation is real and widely observed by practitioners: capital flows from chip designers through memory, packaging, cooling and connectivity; from gold through silver into industrial metals. What the research established is that this flow has no fixed running order when measured across all history [VALIDATED — null]. The order is not mechanical.

The explanation is that rotation is event-initiated. A discrete trigger — an earnings line-item, a policy shock, a technology release — names which assets are in focus. It does not name the order or the timing. Those are determined by price dynamics within the episode.

The commercial consequence: after the trigger, there is a window of days to weeks in which the theme is live, the news flow has gone quiet, and participants must decide where capital moves next with no fresh information. Institutions cannot sit out — they must stay invested continuously. This gap is where the product creates value [HYPOTHESIS].

Falsification test: if customer interviews show participants do not experience this gap as a distinct problem — if they report simply holding the first-mover or exiting the theme entirely — the positioning must change. This test has not yet been run.

2.3 The defensibility problem

A third pain, specific to those managing other people's money: allocation decisions must be explainable to clients and committees independently of outcome. A framework that outputs an auditable rationale ("the regime classifier indicated stress; factor attribution showed dollar strength dominant; we reduced duration") has value even in periods when it is not profitable, because it converts a discretionary judgment into a documented process. This is a materially different product requirement from the retail case — it prices transparency above accuracy.

3. The solution and its evidence base

3.1 Architecture

Four components, deliberately modular so each can be improved or replaced independently.

Regime engine [VALIDATED, with a declared look-ahead]. Principal component analysis over eight FRED series from 2006 onward — DGS10, DFII10, DGS2, T10Y2Y, EFFR, M2SL, VIXCLS and DTWEXBGS (config/config.yaml) — resolving to four regimes. The count was selected on structural criteria: seed stability (adjusted Rand index 1.000, against 0.774 for five), persistence (median run length 52.5 days, against 3 days for three), and separation. It was explicitly not selected on BIC, which decreases monotonically to the edge of the candidate range.

Vintage treatment, stated because the supervisor's feedback asked and the answer matters. Seven of the eight series are market prices or administered rates that are not revised. M2SL is a monthly release, published with a lag and subject to revision, and the panel uses its current vintage. So the sentence "no look-ahead" in the 20 August draft was wrong for the regime engine, not merely unproven. Two further look-aheads are declared: the regime model was fit once on the full panel (a live system has no future data to fit on; an expanding-refit variant now exists, §3.1 below), and feature standardisation used full-panel moments. The last was measured: it moves the level model by +0.012 Sharpe (p 0.94) and the trend model by +0.261 (p 0.057) — the trend model's apparent advantage was the look-ahead, and that model is no longer preferred. Replacing M2SL with its ALFRED point-in-time vintage is listed in §3.3.

On the regime count: an earlier version of this work claimed three lines of support. After the panel extension two weakened — event-alignment against 2024 news fell to p ≈ 0.32 from p < 0.001. Four regimes stands on internal structure alone. Corrected rather than retained.

Directional analog engine [VALIDATED, with retirements]. Expanding-window walk-forward, 2010–2026, weekly rebalances.

  -----------------------------------------------------------------------------------------------------------------------------------
  Universe                 Sharpe (20 Aug)   **Sharpe**   p, incumbent null   **p, dependence-corrected**     Status
  ------------------------ ----------------- ------------ ------------------- ------------------------------- -----------------------
  All 47 assets            0.60              0.51         0.0010              0.0448 (8 exceedances of 200)   marginal

  Long-history (35, ≥8y)   0.43              0.25         0.0380              0.1841 (36 of 200)              [RETIRED] as a result
  -----------------------------------------------------------------------------------------------------------------------------------

The long-history result is no longer claimed. It was the survivorship-controlled block — the one that mattered most — and under a null that respects serial dependence it is indistinguishable from noise. The supervisor's feedback predicted precisely this: permuting asset-weeks as independent understates the p-value through pseudo-replication. It did, by a factor of roughly five on the ALL universe and by enough to overturn the long-history one entirely.

The revision is the NYSE session-calendar migration of 18 August, which removed ~196 rows that had entered the PCA and regime fit as near-duplicate holiday observations. The earlier claim that the edge "survives dropping recently-listed tickers" is [RETIRED]: the survivorship-controlled block is what degraded most. Two further disclosures the earlier draft lacked. The engine applies a recency decay, λ = 0.0008 per session, half-life 3.44 years — present in the configuration throughout, and asserted absent in an earlier pre-registration, which was amended. A registered rung diagnostic then showed the decay reselects rather than tie-breaks (top-k overlap 0.765 and 0.850 against a 0.90 threshold), so the engine reduces to the 100 most recent same-regime days, equally weighted. The word "analog" describes the design intent, not the mechanism as measured.

On the permutation p-value. The supervisor's feedback correctly notes that an iid t-test on 706 weekly returns at Sharpe 0.60 gives p ≈ 0.027, not 0.0010, and that a permutation scheme treating asset-weeks as independent understates p through pseudo-replication. That criticism was confirmed on 26 August in a different part of the pipeline: the document-conditioned estimator's null permuted outcomes freely across events whose forward windows overlapped 61–87%, and correcting it reduced seven passing cells to one (§3.1, event layer). The same correction has not yet been applied to the backtest's permutation test, and until it is the 0.0010 should be read as an upper bound on significance, not a measurement. The reconciliation table the feedback asked for — statistic, null, permutation scheme, exceedance count, dependence structure, effective n — is item 1 of §3.3.

Live forward test [BUILT — zero matured trades]. Three models were frozen before any live data, with all 48 grid configurations committed as the registration record. The valid log begins 19 August 2026 on a session-calendar basis.

  --------------------------------------------------------------------------------------------------------------------
  Model                Specification      Selection                              In-sample Sharpe (pre-calendar-fix)
  -------------------- ------------------ -------------------------------------- -------------------------------------
  Baseline             5d, level, σ1.5    Specified in advance                   +0.21

  Horizon-trend        10d, trend, σ1.5   Specified in advance                   +0.39

  Deliberate overfit   20d, trend, σ1.0   Best-in-sample of 48 — grid-selected   +0.50
  --------------------------------------------------------------------------------------------------------------------

The third model is a labelled control, and its p-value is not evidence after selection; the feedback is right that a family-level test is what would be valid, and none has been run. After the calendar fix the ranking of the first two flipped — the level model now leads the trend model — consistent with the trend advantage having been the standardisation look-ahead.

What the forward test can and cannot show. At the date of writing it holds eighteen rows and zero matured trades; the first five-day horizon matured on 26 August. The feedback's power arithmetic is accepted: at Sharpe 0.60, six months of weekly returns carries roughly 11% power against zero, and the frozen models' own in-sample Sharpes give 7–10%. The forward test is not a decision gate at month six and this plan does not treat it as one. Its value is different and real: it can reveal operational failure or severe drawdown, and its version-controlled timestamps make retrospective claim-fitting impossible. It reports intervals, not verdicts.

Event layer [VALIDATED — null]. Built and run between 20 and 26 August. Every registered test is in the repository with its criterion written before the run.

  ---------------------------------------------------------------------------------------------------------------------------------------------------------
  Test                                     Registered criterion                Result
  ---------------------------------------- ----------------------------------- ----------------------------------------------------------------------------
  Rotation, 7 hypotheses × 4 instruments   pre-registered                      null at every level

  SPY→GLD, SOXX→XAR (survived discovery)   temporal split + cost               both failed the split

  Post-event drift existence               prereg 8273be4                      NULL

  PEAD, firm-level                         criterion in docstring              not met; the H=1 positive lives entirely in TSLA/NVDA/MSFT

  Cross-firm spillover                     intraday decomposition              propagation is instant: 5/7 peers on the overnight gap, 0/7 after the open

  FOMC→GLD, −0.3% at h=2,3                 split: sign agreement, ratio ≤ 3×   split FAIL, 4.62× at h=2 (cost test passed)
  ---------------------------------------------------------------------------------------------------------------------------------------------------------

The spillover result is the mechanism that unifies the nulls: events reprice in the overnight gap, and every earlier test had entered at t+2, after propagation was complete. It also produced the project's cleanest self-caught error — an entry convention that used the announcer's close showed 6/7 peers significant; the tradeable convention showed 0/7. That comparison is retained in the output as a labelled demonstration of what look-ahead is worth on real data.

LLM document layer [VALIDATED — one cell of 45]. 2,616 documents read across FOMC statements, FOMC minutes, earnings 8-K/6-K and Federal Register political documents, at a total inference cost of roughly US$30, under one prompt version and one model. A registered specificity gate — does the reader's specificity field discriminate between source types? — passed on the full corpus (spread 0.517, 95% CI [0.494, 0.539]). A seven-check audit found the reader internally consistent (hawkish stance against bond-price direction at −0.80; its own surprise field against its own equity direction agreeing 92% of the time) and correct on every landmark document it was given.

The conditional estimator was built blind, accepted under six tests, and unblinded on 26 August. Seven of 45 cells met the registered criterion. One survived re-testing under a null that respects overlapping outcomes — fomc_minutes/USO at a five-session horizon — and one of 45 is inside the range expected by chance. A separately registered test of whether reader–history agreement predicts better outcomes failed in the opposite direction (discordant cases outperformed by 0.21%, CI excluding zero); the conviction label it would have justified does not ship.

Two limitations the audit measured rather than assumed. The reader's five macro axes cannot represent a sector shock — a steel tariff proclamation scores high on specificity and near zero on direction because there is no axis to point at — and a schema v2 with sector axes is pre-registered but unfunded. And the political corpus was found truncated by two fetcher bugs; the corrected fetch retrieved 4,595 further documents at zero cost, unread pending budget.

3.2 What the null results are worth commercially

Two headline hypotheses failed. In a research context these are findings. In a commercial context they are usually buried. They are surfaced here for three reasons.

They are differentiating. A vendor willing to publish what did not work is making a credibility claim that competitors selling uniformly positive backtests cannot match.

They are load-bearing. The rotation null is what generated the event-conditioning insight — the core product thesis exists because a simpler hypothesis was tested honestly and rejected.

They are defensive. Any sophisticated buyer will stress-test claims. A vendor who has already disclosed the failures cannot be ambushed by them.

3.3 What this evidence does not yet establish

The supervisor's feedback asked for this subsection by name. Six of its items were closed on 28 August by backtest_evidence.py, which measured rather than assumed; the results are below and the remainder is stated as an open boundary.

Closed — transaction costs and turnover

Turnover is measured from actual basket membership, not assumed: 23% of the long leg and 25% of the short leg are replaced at each weekly rebalance, so 0.49 legs trade per rebalance, or about 25 one-way leg-turnovers a year.

  -------------------------------------------------------------------------
  Cost per side           ALL 47 net Sharpe       Long-history net Sharpe
  ----------------------- ----------------------- -------------------------
  0 bps                   0.51                    0.25

  5 bps                   0.47                    0.20

  10 bps                  0.43                    0.15

  20 bps                  0.34                    0.06

  50 bps                  0.09                    −0.22
  -------------------------------------------------------------------------

Break-even round-trip cost: 60.6 bps per side on ALL, 26.3 bps on long-history. Realistic ETF execution sits well inside both. The feedback's concern that "a 0.6 Sharpe can be 0.25 after one round trip a week" does not hold here — costs cost about 0.08 of Sharpe at a realistic level, not 0.35. This is the one item where the measurement came back better than the criticism assumed.

Closed — the short leg, and it is a finding

The short leg contributes −0.169%/week on ALL and −0.216% on long-history. The names ranked worst went up. Borrow barely matters by comparison: 300 bps annualised costs 0.10 of Sharpe.

Long-only: +0.464%/week, Sharpe 0.83, carrying full market beta. That number must not be read as alpha — over 2010–2026 the S&P itself ran a Sharpe near 0.7–0.9, so a long-only basket at 0.83 is approximately the market. The spread is the only quantity that could be alpha, and the spread is what dependence-correct inference just weakened to p = 0.045.

Closed — the family-level test, and it is the most important number here

The feedback: "Your third frozen model is explicitly best-in-sample of 48 configurations, so its p-value of 0.0390 is not valid evidence after selection." Correct. A maximum-statistic test across 54 grid cells now quantifies it.

  ------------------------------------------ -----------------------------------
  Best observed Sharpe                       +0.73 (H=5, N=5, topk=200, σ=2.0)

  Null distribution of the best cell, mean   +0.56

  Null 95th percentile                       +0.77

  Exceedances                                17 of 200

  Family p                                   0.0896
  ------------------------------------------ -----------------------------------

Searching 54 configurations of a process with no signal yields a Sharpe of 0.56 on average. That single fact is the strongest argument in this document against trusting any grid-selected backtest, including ones sold by competitors. The observed best of 0.73 falls inside that null distribution and is not distinguishable from search noise.

What survives is narrower and must be stated exactly: the one model specified in advance (H=5, topk=100, σ=1.5) reaches p = 0.045 under a dependence-correct null. Everything found by searching does not. That is the shape of a real but weak effect — and also the shape of no effect at all. On this evidence the two cannot be separated, and this plan does not claim otherwise.

Still open

1.  Capacity. Dollar-volume history is not in this repository, so no AUM ceiling is stated. The 46 names ever held are enumerated in processed/backtest_evidence.json so the constraint can be computed the day volume data is pulled. Market impact is not modelled at all.

2.  Borrow is a flat annualised rate, not security-by-security. A historical per-name borrow curve is not available here, and inventing one would be worse than saying so.

3.  Point-in-time macro data. M2SL uses its current vintage; an ALFRED rebuild is needed before any live-basis claim.

4.  A conditional forecast that survives correct inference. One document-conditioned cell of 45 survived, inside chance (§3.1).

5.  Any validated customer demand or price. No primary research has been run; §4.1 and §8.2 stand as [HYPOTHESIS].

6.  LTV, COCA and retention, which require a sales cycle that has not occurred.

Registered future amendment — source expansion

The five sources currently read are all filed decisions. The class of document where a market-moving political shock usually first appears — a threat to act, rather than an act — is not covered. Four further sources would close that gap; all are US government works, so free to fetch and free of the copyright constraint that rules out news text.

  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Source                                   Volume                  Why it matters                                                                             Backfill cost
  ---------------------------------------- ----------------------- ------------------------------------------------------------------------------------------ -----------------
  White House statements and remarks       ~500–1,000/yr           Where threats to act live: tariff warnings, sanctions signals, foreign-policy statements   

  Federal Reserve speeches and testimony   ~150/yr                 Eight statements a year are read; roughly 150 speeches are not                             

  Treasury releases and OFAC sanctions     ~300/yr                 Sanctions are immediate and market-moving                                                  

  USTR press releases                      ~200/yr                 Trade actions before they reach the Federal Register                                       

  Federal Register types not yet read      4,595 already fetched   On disk at zero fetch cost, unread                                                         ~US$60

  All four new sources, 2011–2026          ~15,000–20,000 docs                                                                                                ~US$850–1,150

  From 2020 only                           ~7,000 docs                                                                                                        ~US$400

  Ongoing, once backfilled                 5–10 docs/day                                                                                                      ~US$180/yr
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

The ongoing figure is the commercially relevant one: backfill is a one-time capital cost and currency is nearly free. This is deliberately postponed until after submission and is listed here as a costed roadmap item, not a claim. It requires its own pre-registration, because deciding which sources map to which axes is a design choice that must be fixed before anyone sees whether it works — and because more sources means more same-day collisions, which moves §7.3's estimated weighting rule from rarely-fires to worth-registering.

Commercially, expanded coverage is a paid tier, not a general upgrade. Reading intentions rather than only decisions is the difference between seeing a tariff when it is proclaimed and seeing it when it is threatened; that is a subscription feature, and it is priced as one.

What this means commercially. The product sold in Phase 1 is not a backtested return stream. It is a regime label, a document reading, an explicit precision, and a rule for when to stay silent — and the evidence above is disclosed to the buyer rather than dressed up. A vendor whose own family-level test says "grid search yields 0.56 from nothing" is a vendor a fiduciary can put in front of a committee.

3.4 Registered future amendments

Two amendments are registered here rather than left implicit. Neither is built. Both are stated with the criterion they would have to meet, in the same form as every test already run, so a reader can hold the venture to them.

The standing testing protocol — grid, distribution, split

The most damaging thing a research vendor can do is report one configuration, one number and one sample. This plan's first draft did all three: a Sharpe of 0.60, from one cell, on one split, with one p-value. Every correction since has come from relaxing exactly one of those constraints. The protocol below is registered as a standing requirement for any future strategy claim this firm makes, internally or to a client.

A — a grid, not a shot. No performance figure may be reported from a single hyperparameter configuration. Every claim reports the full grid it was evaluated over — horizon, basket size, neighbourhood size and kernel width at minimum — with the cell count stated. The 28 August work set the standard: 54 cells, all reported, including the thirty that underperformed the headline.

Criterion: fewer than 12 grid cells and the figure is not reportable as a performance result. It may be shown as an illustration, labelled as one.

B — a distribution, not a point. The deliverable is the distribution of the statistic across the grid — median, interquartile range, minimum, maximum — alongside the null distribution of the best cell under a dependence-respecting permutation. The maximum on its own is meaningless, because selecting it is itself an operation with a null.

Measured, not hypothetical: across 54 cells the best observed Sharpe was +0.73, while the best of 54 nulls averaged +0.56 and reached +0.77 at the 95th percentile. Searching a grid of pure noise produces a Sharpe of 0.56. A vendor quoting a single best-cell figure without that comparison is quoting a number their own data cannot support.

Criterion: family-level p ≥ 0.05 means the grid as a whole has not demonstrated skill, and no cell within it may be quoted as evidence — including cells that individually clear 0.05.

C — split data, on criteria fixed before the split is read. Every claim survives a chronological split at the median date:

  ----------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------
  S1 — sign agreement                 both halves carry the same sign as the pooled estimate

  S2 — magnitude stability            neither half exceeds 3× the other in magnitude

  S3 — pooled significance            the pooled result clears p < 0.05 under a dependence-respecting null

  N1 — non-overlap                    where forward windows overlap, the criterion holds on a non-overlapping subsample, or the cell is reported UNDERPOWERED rather than passing
  ----------------------------------- ---------------------------------------------------------------------------------------------------------------------------------------------

A claim failing any of these is a subsample artifact and is reported as one. This is not a new invention: it is the rule that killed the FOMC→GLD cell at a 4.62× magnitude ratio, and the rule that reduced seven passing document cells to one. Registering it makes it standing rather than ad hoc.

Why this belongs in a business plan and not only in a methods appendix. It is the product. A firm whose differentiator is calibrated refusal must be able to state, in advance and in writing, the conditions under which it will decline to make a claim. These are those conditions.

Source expansion

Costed in §3.3: four further government sources — White House statements, Federal Reserve speeches, Treasury and OFAC releases, USTR announcements — letting the system read intentions rather than only decisions. Roughly US$850–1,150 to backfill and US$180 a year to maintain. Postponed until after submission, requiring its own pre-registration, and intended as a paid tier rather than a base upgrade.

4. Market and customer

4.1 Status of the primary research — read this before the segments

The deliverable specification for this project requires customer segmentation informed by primary research, based on five to ten interviews. That research has not been conducted.

What exists is a set of informal conversations with university cohort members, friends and relatives, in which the question asked was broadly whether they would be interested in a signal product. This does not constitute primary market research, for three reasons that are worth stating precisely:

-   The question was leading. "Would you be interested in X" invites agreement and reliably overstates demand. Discovery research must establish that a pain exists before the solution is described.

-   The sample is non-representative. None of the respondents work in financial institutions or manage money professionally. They cannot speak for Tier 2 or Tier 3 at all, and for Tier 1 they are a convenience sample drawn from a single social network.

-   No structured instrument was used, so responses are not comparable across respondents and cannot be aggregated.

The segmentation below is therefore presented as [HYPOTHESIS] throughout. It is derived from the founder's own contemporaneous market observation across the project period and from structural reasoning about who bears which pain — a legitimate basis for a hypothesis, and not a substitute for evidence.

A structured discovery instrument has been prepared (see accompanying interview guide) testing three named hypotheses with defined falsification conditions. Executing it against 8–10 respondents, weighted toward Tier 3, is the highest-priority action item and the gating requirement before any pricing or TAM figure in this plan should be relied upon.

Identified access routes to qualified respondents

The reason the research has not been conducted is access, not intent: Tier 3 respondents are professionals who do not take calls from students without a warrant for the introduction. The following venues resolve that, and constitute a concrete execution plan rather than an aspiration.

Singapore FinTech Festival — 18–20 November 2026, Singapore EXPO. Organised by MAS with GFTN, the festival runs SFF MeetUp, which arranges up to 20 pre-scheduled introductions per attendee alongside Investor Hours and Founders Peak. Passes are SGD 1,000 if booked by 24 September 2026. Twenty scheduled meetings in three days is, on its own, twice the sample this plan requires, drawn from exactly the institutional population the convenience sample lacked. NUS has historically offered alumni registration discounts through its alumni network. This is the single highest-yield action available and it is budgeted in Section 12.

Investment Management Association of Singapore (IMAS). Runs an annual Investment Conference and Masterclass plus a Digital Summit. The membership is asset managers and investment professionals — the closest available match to the Tier 3 fiduciary segment.

Singapore FinTech Association. Runs an industry roundtable series through the year. Smaller and more conversational than SFF, therefore better for depth interviews rather than volume.

CFA Society Singapore. Directly relevant given the founder's CFA candidacy, which supplies a legitimate reason to be in the room. Membership is practitioner-heavy and skews toward exactly the risk-managing fiduciary profile.

NUS Business School alumni network and faculty introductions. The lowest-friction route and the fastest. Alumni in wealth management and asset management are reachable with a warm introduction, and the faculty supervisor relationship provides institutional credibility that a cold approach lacks.

Secondary events: Fintech Week Singapore (16–17 September 2026) and TOKEN2049 (7–8 October 2026), the latter adjacent rather than core.

Sequencing. The alumni network and CFA Society routes are available immediately and should produce the first three to five interviews. SFF in November converts the research from a small qualitative sample into a defensible evidence base, and simultaneously serves the Section 7 objective of identifying candidate licensed host firms — the same room contains both. The two problems have one solution.

This is stated plainly rather than papered over because the alternative — presenting convenience-sample agreement as market validation — is precisely the failure mode that produces confidently wrong business plans.

4.2 Candidate segments

Tier 1 — Self-directed active traders [HYPOTHESIS]

Retail participants managing their own capital, actively trading, information-saturated. Pain: cannot distinguish "my thesis is wrong" from "the regime is against my thesis." Buy signal subscriptions, not managed products. Fear losing autonomy and missing regime shifts. Reachable through content-led channels — written analysis, video, social. High word-of-mouth density, which satisfies a key beachhead condition.

Regulatory note: this segment is retail, which is the most heavily regulated case. See Section 7.

Tier 2 — Liquidity-sensitive high-net-worth individuals [HYPOTHESIS]

Individuals with meaningful capital who have become averse to products that trap it, following redemption gates and illiquidity events in private credit vehicles. They value revocability and transparency over headline return. Reachable essentially only by referral. Smallest and least accessible segment; least evidence behind it.

Tier 3 — Risk-managing fiduciaries [HYPOTHESIS]

Independent advisers, boutique wealth managers, small family offices. They manage other people's money, and the career consequences of a bad allocation are asymmetric — a loss attributable to a documented process is survivable in a way that a loss attributable to personal judgment is not. They buy defensibility. Longer sales cycle, higher contract value, direct sales motion.

4.3 Beachhead selection

Applying the eight standard beachhead criteria produces a result that contradicts the intuitive ordering.

  --------------------------------------------------------------------------------------------
  Criterion                        Tier 1                Tier 2             Tier 3
  -------------------------------- --------------------- ------------------ ------------------
  Customer can fund purchase       Moderate              Strong             Strong

  Reachable by a solo founder      Strong                Weak               Moderate

  Compelling reason to buy         Moderate              Moderate           Strong

  Can deliver whole product        Weak — needs polish   Weak               Moderate

  Manageable competition           Weak — crowded        Moderate           Moderate

  Leverage into adjacent markets   Strong                Moderate           Strong

  Consistent with founder goals    Strong                Moderate           Strong

  Can dominate quickly             Weak                  Moderate           Moderate

  Legally serviceable today        No                    Yes, ≤30 clients   Yes, ≤30 clients
  --------------------------------------------------------------------------------------------

The final row is decisive and is developed in Section 7. Serving retail requires a licence the venture cannot presently obtain. Serving accredited investors is possible under an existing exemption.

Selected beachhead: Tier 3, risk-managing fiduciaries, restricted to accredited investors.

The reasoning is that a segment which is legally serviceable, has the strongest compelling reason to buy, and carries the highest contract value dominates a segment which is easier to reach but cannot be lawfully served. Tier 1 is not abandoned — it is deferred, and reachable in the interim through a non-advisory analytics product and a content channel that builds the audience for later conversion.

4.4 End-user profile and persona

The supervisor's feedback identified the end-user profile, the persona and the decision-making unit as missing. All three are written from structural reasoning about the selected segment. None is validated. No customer interview has taken place, and §4.1 dates the access plan that would change that. They are working hypotheses precise enough to be falsified by the first ten conversations, which is their purpose.

End-user profile — who actually opens the product

The end user is not the buyer. The end user is an investment professional inside a boutique manager or single-family office who holds discretionary or advisory responsibility for a multi-asset portfolio and who personally assembles the macro view each morning. Characteristically:

-   Firm size 3–20 professionals. Large enough to have a formal investment process and a client-reporting obligation; too small to employ a dedicated macro strategist. This is the whole opening: the work exists and nobody is assigned to it.

-   Assets from roughly S$50m to S$500m. Below that, the fee base cannot support a S$10,000 subscription. Above it, the firm hires the strategist and builds internally.

-   Multi-asset mandate. Equities, fixed income, gold and currency exposure at minimum, so a cross-asset regime view is relevant rather than peripheral.

-   Already pays for data. Bloomberg or Refinitiv, at least one seat. A firm that pays nothing for market data is not a candidate at any price.

-   Spends 5–10 hours a week on macro synthesis and regards that time as necessary but not differentiating.

Persona — "Adrian Lim", Head of Investments

A single named persona, in the Disciplined Entrepreneurship sense: one specific person the product is built for, not an average of the segment.

  ----------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Role                                Head of Investments, Singapore boutique, 8 professionals, ~S$180m AUM, ~40 accredited-investor families

  Background                          15 years, formerly at a bank's private-banking arm; CFA charterholder

  Reports to                          The managing partner, and quarterly to an investment committee

  A normal morning                    06:45–08:00 reading overnight wires, the Fed calendar and two sell-side notes, forming a view he will have to defend

  What he is measured on              Not beating a benchmark. Retaining families, and never being unable to explain a decision

  His actual fear                     A client asks "why were we in gold in March?" and the honest answer is "it felt right at the time"

  What he currently buys              One Bloomberg seat; two sell-side research relationships that come with brokerage; nothing else

  What would make him buy             A dated artefact he can attach to a committee paper, that says what the regime was, what the evidence was, and — on the days it does not know — that it does not know

  What would make him refuse          Anything resembling a black-box signal, anything that produces a confident number every day, and anything his compliance officer flags

  How he is reached                   IMAS events, the CFA Society Singapore network, and referral from another boutique — not through advertising
  ----------------------------------- -----------------------------------------------------------------------------------------------------------------------------------------------------------------------

Adrian is why the product abstains rather than always producing a number. A vendor that is never uncertain is, to him, a vendor he cannot defend.

Decision-making unit

For a S$10,000 annual subscription at a firm of this size, three roles matter and one of them is not on anyone's list.

  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Role                          Who                                                                                       What they decide                                                                          What stops them
  ----------------------------- ----------------------------------------------------------------------------------------- ----------------------------------------------------------------------------------------- ---------------------------------------------------------------------------------------------------------------
  Champion / end user           Head of Investments (Adrian)                                                              Whether the product is useful and worth the process change                                Cannot see how it differs from research he already receives free with brokerage

  Economic buyer                Managing partner                                                                          Whether S$10,000 is worth it against a fee base                                           Cannot connect the spend to retention or to a mandate win

  Veto — the one that matters   Compliance officer, or the outsourced compliance consultant most firms of this size use   Whether an unlicensed vendor's output may inform, or appear in, client-facing documents   Concludes that citing an exempt vendor in a client paper creates a regulatory exposure the firm does not need
  ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

The compliance veto is the highest-risk assumption in this plan and the supervisor identified it as such. It runs the wrong way from ordinary software procurement: the more useful the product is — the more Adrian wants to cite it in a committee paper — the more likely compliance is to look at it. A product that stayed in Adrian's own workflow and never reached a client document would face no veto and would also be worth much less.

Three things are designed against that veto, though none is yet tested with a compliance officer:

7.  The product issues no recommendation and no buy or sell instruction. It states a regime, the evidence and a precision, and abstains where its own registered floor is not met.

8.  Every output is dated, versioned and reproducible, so a firm can show a regulator exactly what it was told and when — which is a compliance asset rather than a liability.

9.  The registered abstention rule means the vendor is on record declining to opine, which is the opposite of the posture that creates advisory exposure.

Falsification. If interviews show that compliance functions treat an exempt vendor's output as unusable in client documents regardless of how it is framed, the value proposition in §5 collapses to internal time-saving alone, and the price must fall accordingly. That is a materially different business and it is the single question the first ten conversations must answer.

5. Value proposition

For the selected beachhead, the value proposition is:

  A documented, auditable framework for identifying the prevailing macro regime and the factors driving it — one that can be cited in a client conversation, that publishes its failures alongside its results, and that positions along thematic rotations in the periods when no news is arriving.

Three quantifiable value claims, each with its measurement method and current status:

Time compression. Daily synthesis of macro state, factor attribution and news flow currently consumes an estimated 5–10 hours per week for a practitioner doing it manually. Measurement: self-reported hours, pre- and post-adoption. Status: not yet measured — Question 7 of the discovery instrument.

Documented rationale. Each output is an artefact that can be attached to a client file or committee paper. Measurement: whether respondents currently produce such documentation and what it costs them. Status: Question 8 of the instrument.

Rotation positioning. Where a theme is live and no fresh news is arriving, the system indicates likely next-links and timing. Status: this depends on the event layer, which is [DESIGNED] and not built. It must not be sold until Stage 1 establishes that tradeable drift exists.

6. Competitive positioning

6.1 The landscape

  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Competitor              Position                                                                 Buyer                                 Overlap
  ----------------------- ------------------------------------------------------------------------ ------------------------------------- ---------------------------------
  42 Macro                Discretionary macro research with regime overlay, personality-led        Retail to professional                Regime framing

  Macrosynergy            Institutional quantamental macro signal infrastructure, build-your-own   Institutional quant                   Signal construction

  Permutable AI           Alternative macro signals, news-derived, API-first                       Hedge funds                           News-to-signal pipeline

  OpenMacro               Rules-based macro strategies with transparent regime classification      Professional / active retail          Closest direct overlap

  MacroMicro              Macro data platform, now adding an AI research layer                     Retail to professional, Asia-strong   Data breadth, Asia distribution

  Bloomberg / Macrobond   Institutional data and analytics infrastructure                          Institutional                         Data, not signals

  Build-your-own          The real default for sophisticated buyers                                Quant-capable                         Everything
  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------

MacroMicro in particular is building an AI decision engine unifying global macro, industry and company data, and has established distribution in exactly the Asian markets this venture would target first. It is the most serious competitive threat, not because its technology is superior but because its distribution already exists.

6.2 Where the venture does not win

Stated first, because a competitive section that finds only advantages is not credible.

Data breadth — comprehensively outmatched. Brand and distribution — nonexistent against incumbents with established audiences. Institutional credibility — a solo founder with a three-month project cannot match a firm with a track record. Capital — no comparison. Standalone signal strength — a Sharpe of 0.4–0.6 is respectable for a single ingredient but is not, on its own, an institutional-grade product.

6.3 Where it can win

Event-conditional rotation sequencing. No identified competitor sells positioning within a live thematic cascade during information-quiet periods. This is the intended wedge — and its evidential status must be stated exactly. The rotation-sequencing hypothesis has been tested and is null so far (§3.1, event layer): no stable order unconditionally, and the pairs that survived discovery failed their splits. What survives is the narrower, mechanistic finding that repricing is event-initiated and completes in the overnight gap. The commercial wedge therefore rests on a [HYPOTHESIS] that the within-episode conditional structure is tradeable, which the drift tests have not yet confirmed. Selling it before Stage 1 confirms it would be selling a null.

Published falsification. Competitors publish what worked. This venture publishes what did not, with statistics. For the fiduciary buyer — who must defend a process rather than a result — a vendor demonstrating methodological honesty is directly more useful, because that honesty is the thing being purchased.

Timestamped live forward testing. The forward log is version-controlled, so entries provably precede outcomes, and includes a deliberate overfit control. This is a stronger evidentiary standard than a backtest and is cheap to maintain while expensive to fake.

Aggregate attention as a published product — the crowding indicator. The platform observes what its own users are collectively researching. Published back to subscribers as a live indicator of where attention is concentrating — which themes, which links in a chain, which assets — this becomes a data product no competitor can replicate without an equivalent user base, and one that strengthens with every additional subscriber. It is a genuine network effect: each user makes the indicator more informative for every other user, which raises switching costs and makes the product harder to leave as it grows.

It also has direct analytical value inside the framework rather than beside it. Crowding is information. A rotation cascade entered by everyone simultaneously behaves differently from one entered quietly, and an attention measure is a plausible input to the event layer's episode detection — a candidate feature, testable against the same drift-existence protocol as any other [HYPOTHESIS].

Critically, publishing it simultaneously to all subscribers is what makes it lawful and defensible. The same underlying data used privately to trade ahead of those subscribers would be a front-running conflict (Section 7.3); released to everyone at once it is a transparency feature. The distinction is not cosmetic — it is the difference between extracting value from users and creating it for them, and it converts the venture's sharpest ethical exposure into its most defensible commercial asset.

Asia-Pacific and bilingual coverage. The founder operates in English and Mandarin and has domain depth in the semiconductor supply chain — the single most active thematic rotation chain of the current cycle. Most Western competitors treat Asian semiconductor dynamics superficially.

6.4 Moat: what compounds, and how the company grows on it

One honest sentence first, then the assets. The methods themselves — the regime taxonomy, the residualisation approach, the system integration — are head starts measured in months, not barriers: they are documented, and a funded competitor can reproduce them. What cannot be reproduced quickly is set out below, followed by the growth path each asset unlocks.

The five compounding assets, in plain terms

Asset 1 — The library of documented failures.

What it is: a record of every hypothesis this venture has tested and rejected, with the statistics. Today it holds two entries: gold does not decouple from equities under liquidity stress, and semiconductor rotation has no fixed running order.

Why it grows: every future hypothesis tested adds an entry. It held two entries on 20 August; it holds more than a dozen on 26 August, plus a running log of 26 wrong priors — each a documented case of a plausible belief overturned by running code. That log is the asset in its purest form.

Why a competitor can't copy it: they cannot see it. A rival entering this space must spend their own months and money rediscovering each dead end, and they will not publish what they find.

Who pays for it: nobody directly — it is what makes the research faster and the claims trustworthy, which is what everything else is sold on.

Asset 2 — The trust machinery.

What it is: the working practices that stop the firm from fooling itself: models frozen and registered before live data arrives; a deliberately overfit model included as a control that is expected to fail; permutation tests instead of raw p-values; pipelines that halt on stale data rather than logging phantom results; corrections published when new evidence weakens an old claim.

Why it grows: each practice was installed in response to a real failure (the wiped first forward log, the silent PC-renumbering bug), so the machinery improves precisely when things go wrong — it converts mistakes into permanent process.

Why a competitor can't copy it: any one practice is copyable in an afternoon. The discipline of applying all of them, always, including when the result is embarrassing, is a culture — and culture is the slowest thing in business to build.

Who pays for it: the fiduciary client. What Tier 3 buys is a defensible process, and this machinery is the process.

Asset 3 — The timestamped track record.

What it is: a live forward test whose entries are committed to version control before outcomes exist, so no one — including the founder — can quietly rewrite history.

Why it grows: by one entry per trading day, automatically, forever.

Why a competitor can't copy it: time. A rival starting today is permanently behind by however long this log has run, and no budget compresses a calendar.

Who pays for it: every prospective client, because it is the answer to the only question that matters in this industry — "how do I know your backtest isn't fiction?"

Asset 4 — The labelled event corpus.

What it is: the historical news archive, tagged and organised into rotation episodes — each marked with its trigger, the assets involved, the order capital moved, and how it ended. Raw news is a commodity anyone can buy; news labelled with judgment is scarce, because no data vendor supplies the judgment.

Why it grows: by every new episode the market produces. The corpus now exists — 2,616 documents read for roughly US$30, not the $620 the earlier draft budgeted, because the pilot-then-gate discipline caught a 307-document cover-page error before it was paid for. A further 4,595 political documents are fetched and awaiting read budget.

Why a competitor can't copy it: they can buy the same raw feed, but the labels embody accumulated domain judgment — and the analogue-matching engine is only as good as the labelled history it matches against.

Who pays for it: initially the subscription product it powers; eventually, as Stage 2 below describes, it can be sold directly.

Asset 5 — The crowding indicator.

What it is: an anonymised, simultaneous-to-everyone view of what the platform's own users are collectively researching (Section 6.3).

Why it grows: each new subscriber makes the reading more representative, so the product literally improves with adoption — the definition of a network effect.

Why a competitor can't copy it: without an equivalent user base there is nothing to aggregate. This is the only asset here that scale alone can defend.

Who pays for it: subscribers, as a feature — and it raises the cost of leaving, because a departing user loses access to a signal their own presence helped create.

Summary view:

  ------------------------------------------------------------------------------------------------
  Asset                   Grows by                  Copyable?             Status
  ----------------------- ------------------------- --------------------- ------------------------
  Failure library         Every hypothesis tested   Invisible to rivals   Accruing now

  Trust machinery         Every mistake survived    Culturally slow       Operating now

  Timestamped record      Every trading day         Time-locked           Running since Aug 2026

  Labelled event corpus   Every market episode      Judgment-locked       Awaiting $620 backfill

  Crowding indicator      Every new user            Scale-locked          Needs a user base
  ------------------------------------------------------------------------------------------------

How the moat becomes growth: three stages with precedents

These assets are not just defensive. Each one, once mature, becomes the raw material of the next business. This is a well-trodden path in financial information — the venture does not need to invent its growth model, only execute a smaller version of one that demonstrably works.

Stage 1 (years 0–2) — Research firm. Sell regime and rotation research to at most 30 accredited-investor clients, as Sections 4–9 describe. Assets 1–3 are the product: the client is buying trustworthy answers, and the failure library, the trust machinery and the public track record are what make the answers trustworthy. Precedent: independent macro research houses such as 42 Macro sustain real subscription businesses on exactly this — actionable regime and risk-management signals sold directly to investors — with far less methodological transparency than this venture publishes.

Stage 2 (years 2–4) — Data and analytics vendor. Once the labelled event corpus (Asset 4) reaches critical mass, it stops being an internal input and becomes a sellable feed: institutions buy the data — episode labels, regime classifications, crowding readings — through an API and build their own strategies on it. This is a fundamentally better business than research: it scales without the founder's hours, and it sells to quant teams who would never buy narrative research. Precedent: RavenPack built exactly this business turning raw news into structured signals for institutions, and the majority of investors surveyed said they would continue sourcing such alternative data from specialist vendors rather than building it themselves — the market has already voted that labelled event data is worth paying a specialist for. The regulatory bonus: selling data is not giving financial advice, so Stage 2 revenue is largely outside the licensing perimeter that constrains Stage 1.

Stage 3 (years 4+) — Classification standard and benchmark licensing. The end-state, and the reason the regime taxonomy matters beyond its predictive power. If the firm's regime classifications become the reference vocabulary — if allocators say "we de-risked when the model entered Regime 3" the way they now say "we tilted to quality" — then the classification itself becomes licensable: to product issuers building regime-conditional strategies, to platforms displaying regime state, to academics citing the taxonomy. The precedent is Barra, which began as academic factor research and whose models became infrastructure that institutions license rather than replicate; the business was later acquired and merged into MSCI, where index and model licensing is a recurring-subscription revenue line. Specific figures for institutional reach, enterprise licence pricing, acquisition value and revenue composition have been removed from this draft rather than asserted without a dated source — the supervisor's feedback was that an uncited exact claim reads exactly like a wrong one, and these were exact claims from memory. The structural point does not depend on them: factor models were once one firm's research method, they became the industry's shared vocabulary, and the firm that wrote the vocabulary collects rent on it.

The honest scaling of this ambition. This venture will not become MSCI, and the plan does not claim it will. The claim is narrower and therefore credible: the same mechanism — research method → data product → reference standard — operates at every scale, and executing it within a defined niche (regime and rotation analytics for Asia-Pacific cross-asset investors, bilingually) is what "top 30% of the market" means in practice. Specialist categories reward the firm that defines their vocabulary, and this category's vocabulary is not yet written.

Why the position survives method change. None of the five assets is welded to today's techniques. If the four-regime taxonomy is superseded, the trust machinery validates its successor, the failure library records why the old one fell, the track record runs unbroken across the transition, the corpus re-labels under the new scheme, and the crowding indicator is method-agnostic. The firm can therefore adopt each new generation of methods as it arrives — which is the actual requirement for staying in the leading tier of any research field, where techniques age but reputations for rigour do not.

7. Regulatory analysis

This section is placed before pricing and go-to-market because it constrains both.

7.1 The licensing position

Under Singapore's Financial Advisers Act, financial advisory services include advising others concerning investment products and issuing or promulgating research analyses or research reports concerning any investment products. A subscription product that tells subscribers which assets to buy or sell falls within this definition. This is not a grey area and cannot be disclaimed away.

The requirements for a firm whose only activity is issuing research analyses:

  -----------------------------------------------------------------------------------------------------------------
  Requirement                         Threshold
  ----------------------------------- -----------------------------------------------------------------------------
  Minimum base capital                S$250,000

  Professional indemnity insurance    S$500,000 limit

  Qualifying individuals              Minimum 3 full-time Singapore-based, each with ≥5 years relevant experience

  Representatives                     Must pass CMFAS examinations and appear on the MAS public register
  -----------------------------------------------------------------------------------------------------------------

The venture is currently one person with no relevant multi-year professional track record in an advisory capacity. The three-person requirement is not solvable with capital alone — it requires recruiting two qualifying individuals. This is the single largest structural obstacle in the plan and is treated as such rather than deferred.

7.2 Four routes, assessed

Route A — Exempt financial adviser, accredited investors only. The exemption is section 20(1)(g) of the Financial Advisers Act 2001 read with regulation 27(1)(d) of the Financial Advisers Regulations, for a person providing financial advisory services to not more than 30 accredited investors in respect of investment products other than life policies.

Source: MAS Form 20 — Notice of Commencement of Business by an Exempt Person — whose explanatory notes define "exempt person" by reference to exactly those two provisions. This is a primary source, not an inference. What it does not establish is whether this particular service falls within the regulated activity at all, how the cap is counted and monitored, or what deadline applies to the notice; those are §7.4's questions to counsel and are unresolved.

Obligations the form itself makes visible, which the earlier draft did not account for:

-   A resident executive director. Form 20's contact person must be an executive director of the exempt person and resident in Singapore. For a solo founder this is satisfied personally, but it fixes a residency requirement into the corporate structure.

-   Fit and proper criteria. The exempt person, its key officers and its controllers must satisfy the Authority's Guidelines on Fit and Proper Criteria, declared on the form and supported where any affirmative disclosure arises.

-   Controller disclosure at 20% of voting power or issued shares — relevant if this round issues equity, since an investor crossing 20% becomes a disclosable controller.

-   The exemption is withdrawable. Section 20(10) empowers the Authority to withdraw an exemption where the person ceases to satisfy the conditions. The route is a continuing obligation, not a one-time filing.

-   Section 114 makes providing false information to the Authority an offence.

Still not established: the notice deadline. Form 20 is the notice of commencement of business, and it is submitted through a designated MAS portal, but the form does not itself cite the provision that imposes the filing period. The supervisor's feedback was specific that the regulation imposing the deadline should be cited rather than the form. This plan does not name that provision, because naming the wrong one would be worse than acknowledging the gap. It is question 4 in §7.4. This is the only route available to the venture in its current form, and it is the reason Tier 3 was selected as the beachhead. It caps the client count at 30, which forces high contract value and is entirely compatible with the fiduciary segment. Recommended first step.

Route B — Appointed representative of an existing licensed adviser. The licence attaches to the firm; an appointed representative is an individual registered on the MAS public register under that firm's permissions, with the firm assuming compliance oversight. The founder would be that individual. This is the arrangement previously suggested to the founder. Note that Singapore does not have a mature regulatory-hosting or umbrella market comparable to the UK's Appointed Representative industry, so this must be negotiated bilaterally with a specific firm rather than purchased as a service.

No counterparty has been identified. Stating this plainly: the plan does not currently have a named host firm, and any figure premised on one would be fabricated. The search criteria are defined — a licensed financial adviser or CMS licensee, small enough to value differentiated research capability, without a competing in-house quantitative macro product, and open to a revenue-share rather than employment structure. Candidates should be identified from the MAS Financial Institution Directory and the Financial Institution Representatives Register, both public. Approaching five to eight such firms is an action item, not an achievement.

Route C — MAS FinTech Regulatory Sandbox. MAS operates a sandbox enabling financial institutions and FinTech players to experiment with innovative financial products in a live environment within a defined space and duration, with specific regulatory requirements relaxed for the duration. Applicable if the product is genuinely novel and the experiment is well-defined. Realistically a Phase 2 consideration; it demands preparation the venture cannot currently resource.

Route D — Non-advisory analytics positioning. Sell the analytical tool rather than the recommendation: the user supplies inputs, the system returns regime classification and factor attribution, and the user forms their own view. Whether this escapes the FAA definition depends on whether outputs constitute "research analyses concerning investment products" — a question requiring qualified legal advice, not a founder's judgment. If viable, it is the route to serving Tier 1 without a licence, and it is the reason Tier 1 is deferred rather than abandoned.

I am not qualified to give legal advice and this analysis is not a substitute for it. Every route above requires review by a Singapore-qualified financial services lawyer before any revenue is taken.

7.3 The query-aggregation conflict

The long-term concept of aggregating user queries to infer what informed participants are attending to, and routing that inference to a proprietary trading account, is strategically elegant and should not be pursued in that form.

The conflict is direct: the firm would be trading ahead of, and informed by, the attention of its own clients. This engages front-running and fiduciary-duty concerns, and under an advisory licence it would likely be disqualifying. The reputational exposure alone — a single disclosure that subscriber queries fed the house account — would end the fiduciary segment permanently.

Two governed alternatives preserve most of the value. Aggregate query data may be used to prioritise research and product direction, which is standard practice and unobjectionable. Or anonymised attention data may be published back to subscribers as a product feature — a positioning-crowding indicator — which converts a conflict into a transparency asset. Either is defensible. Proprietary trading on client attention is not.

7.4 Questions put to counsel, in writing

The supervisor's feedback asked for one question in particular to be put to counsel in writing. It is the first below; the others accompany it because a single engagement should resolve the whole route, not one clause of it.

On Route A — the exemption itself

10. How is "not more than 30 accredited investors" counted, and how must the cap be monitored? Specifically: is it thirty on any occasion, thirty in aggregate over the life of the firm, or thirty concurrently? Does a client who lapses free a place? Is a family office one investor or several? What monitoring record must be kept, and what happens on inadvertent breach?

11. Does the service as described constitute financial advisory activity at all? The product issues no recommendation, states a regime with its evidence and precision, and abstains below a registered floor. If it falls outside the regulated activity, the exemption is unnecessary; if it falls inside, the exemption is load-bearing. The plan currently assumes the second, conservatively.

12. What conditions attach to the exemption, and which conduct, disclosure and record-keeping obligations continue to apply to an exempt person?

13. What notification is required on commencement, on what form, and within what period — and, per the supervisor's point, which provision imposes that deadline, since the form itself is not the source of the obligation. This plan does not state the regulation number, because stating a wrong one would be worse than acknowledging the gap.

14. Do the accredited-investor opt-in requirements apply, and what verification of investor status must be obtained and retained?

On Route B — appointed representative

15. The licence attaches to the firm; an appointed representative is an individual on the MAS public register under that firm's permissions. Can the company itself contract with clients under this route, or only the founder personally? If only personally, the corporate structure in §12 needs revisiting.

16. What liability does the licensed principal assume for the representative's output, and would a principal accept a product whose method it does not control?

On the product boundary

17. Would the output as designed be treated differently if a client cites it in a document shown to their own clients? This is the compliance veto identified in §4.4 and is commercially decisive.

18. Does publishing negative results and an abstention rule — that is, being on record declining to opine — help or hinder the regulatory position?

Status: not yet engaged. §12 budgets S$20,000 for this opinion and §10 records the regulatory route as the highest-impact unresolved risk in the plan.

8. Business model and unit economics

8.1 Cost structure

The defining economic feature is that the expensive component is shared and fixed, not per-user. News tagging, document extraction and scenario generation run once daily and serve every subscriber. Only interactive queries scale per user.

Estimated monthly LLM cost at current API pricing, tiered by task (bulk tagging on a small model, synthesis on a larger one):

  -------------------------------------------------------------------------------------
  Component                  Volume                 Model tier        Cost
  -------------------------- ---------------------- ----------------- -----------------
  News tagging               6,000 articles/month   Small             $9.30

  Document extraction        50 documents/month     Large             $3.30

  Daily scenario narrative   30/month               Large             $2.70

  Shared core total                                                   $15.30/month

  Marginal per user          20 queries/month       Large             $0.72/month
  -------------------------------------------------------------------------------------

Scaling behaviour:

  -----------------------------------------------------------------------
  Users                   Total LLM cost          Per user
  ----------------------- ----------------------- -----------------------
  100                     $87                     $0.87

  1,000                   $735                    $0.74

  5,000                   $3,615                  $0.72
  -----------------------------------------------------------------------

Assumptions: 200 articles/day tagged at ~800 input and ~150 output tokens; 20 user queries/month at ~8,000 input and ~800 output tokens. Sensitivity: the estimate scales roughly linearly with article volume, so a tenfold increase in coverage takes the shared core to approximately $150/month — still immaterial against any plausible revenue.

Scaling to an operating company

The table above describes the current research deployment, which runs on a founder-scale footprint: 47 instruments, macro-level news only, and a handful of users. That is the honest present state. It is not the business.

At operating scale — a 300-instrument universe, multi-source news ingestion, entity-level event coverage, thematic narratives generated per theme rather than once daily, and a full retrieval corpus — the cost structure is as follows.

  --------------------------------------------------------------------------------------------------------
  Component                       Volume at scale                                  Monthly cost
  ------------------------------- ------------------------------------------------ -----------------------
  News tagging                    60,000 articles (2,000/day)                      $93

  Entity-level event extraction   15,000 items (500/day)                           $37

  Deep document analysis          500 earnings calls, filings, policy statements   $41

  Retrieval corpus embeddings     Rolling ingestion                                $11

  Thematic narratives             600/month (20/day across live themes)            $68

  Shared core at full scale                                                        $250/month

  Marginal per active user        40 queries/month                                 $1.92/month
  --------------------------------------------------------------------------------------------------------

  -------------------------------------------------------------------------------------------------
  Users          Total inference   Per user       Revenue at $99 ARPU   Inference as % of revenue
  -------------- ----------------- -------------- --------------------- ---------------------------
  500            $1,210            $2.42          $49,500               2.4%

  2,000          $4,090            $2.04          $198,000              2.1%

  5,000          $9,850            $1.97          $495,000              2.0%

  20,000         $38,650           $1.93          $1,980,000            2.0%
  -------------------------------------------------------------------------------------------------

One-time historical backfill — tagging the full news archive from 2015 to build the analogue corpus — costs approximately $620. This is a rounding error against any funding round and unlocks the historical-analogue matching that the entire Problem 1 engine depends on. It has not been done only because it has not been budgeted.

Two conclusions for investors. First, inference settles at roughly 2% of revenue and stays there — the cost curve is flat in users because the expensive work is shared. This is a software-margin business, not a compute-constrained one. Second, the expensive component of this venture is regulatory and human, not technological: legal, compliance, insurance and qualifying personnel exceed inference cost by an order of magnitude at every scale modelled above.

On the ETF-universe constraint. The original project scope limited the universe to ETFs on token-cost grounds. That was the correct decision for an unfunded student project and it produced a tighter piece of research. The figures above show it is not a constraint on the business: expanding to 300 instruments adds roughly $200 per month. The universe was designed from the outset to be expandable rather than fixed at 47, and the economics confirm that expansion is a funding question, not an architectural one.

The real costs:

  ------------------------------------------------------------------------------------------------
  Item                               Monthly                 Note
  ---------------------------------- ----------------------- -------------------------------------
  LLM inference                      $20–150                 Above

  Commercially licensed price data   $200–500                See below

  Macro data (FRED)                  $0                      Public domain

  Event data (GDELT)                 $0–100                  Free; query costs at scale

  Hosting and infrastructure         $50–150                 

  Pre-compliance total               $270–900                

  Professional indemnity insurance   ~$300–600               Required under any advisory route

  Legal and compliance               $1,500–3,000            Amortised; front-loaded in year one

  Post-compliance total              ~$2,000–4,500           
  ------------------------------------------------------------------------------------------------

A licensing flag that must not be overlooked. The current data pipeline uses yfinance, which scrapes Yahoo Finance. This is acceptable for academic research and is not licensed for commercial redistribution. Any revenue-generating deployment requires a commercially licensed feed. This is a genuine cost and a genuine legal exposure, and it is easy to carry forward unnoticed from a research prototype into a product.

8.2 Pricing and the beachhead economics

All price points below are [HYPOTHESIS]. They have never been tested against a customer. The discovery instrument in §4.1 contains a revealed-preference sequence — what respondents currently pay, then a three-point sensitivity ladder — designed to replace them with evidence.

Revised 28 August, downward and materially. The earlier draft priced the fiduciary tier at $2,000–5,000 per month and reported a 90% gross margin against a "S$54,000 fully-loaded" annual cost base. Both figures were wrong and the supervisor's feedback flagged the second. The corrected version is below.

  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Tier                                   Price             Basis                                                                                                                             Status
  -------------------------------------- ----------------- --------------------------------------------------------------------------------------------------------------------------------- -------------------
  B2B firm licence (Phase 1 beachhead)   S$10,000 / year   Roughly 40% of a single Bloomberg terminal seat (~US$24,000). Unlimited users at the subscribing firm, plus a custom watchlist.   Untested

  B2C Professional                       US$299 / month    Intraday re-scoring, API, portfolio decomposition                                                                                 Untested, Phase 4

  B2C Analyst                            US$99 / month     Full universe, analog forecasts, LLM queries                                                                                      Untested, Phase 4

  B2C Signal                             US$29 / month     Daily regime label, factor attribution, weekly summary                                                                            Untested, Phase 4
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Why the firm licence is priced below a terminal seat. The product is one orthogonal input to a client's own process, not a system they run their desk on. A vendor with no track record, no customers and — as §3.1 records — one conditional cell of 45 surviving correct inference, cannot defend institutional pricing. S$10,000 is a price a boutique can approve without a committee, which is itself a distribution advantage at this stage.

The B2C tiers are Phase 4 and licence-gated. They are listed here for completeness; the §7 analysis puts retail last precisely because that is where the licensing burden falls hardest.

Cost base — reconciled against §12

The "S$54,000 fully-loaded" figure in the earlier draft is [RETIRED]. It reconciles with nothing. §12's funding table is the authoritative statement of what this costs to run, and the arithmetic from it is:

  -------------------------------------------------------------------------------------------------------------------------
  Basis                                                                                 Amount
  ------------------------------------------------------------------------------------- -----------------------------------
  §12 total, 18 months                                                                  S$139,265

  Monthly average                                                                       S$7,737

  Annualised over the funded period                                                     S$92,843

  Steady-state annual, excluding one-time legal (S$20,000) and contingency (S$18,165)   ≈ S$77,400
  -------------------------------------------------------------------------------------------------------------------------

Steady state is the number that matters for margin: founder subsistence S$33,600, compliance retainer S$24,000, professional indemnity S$6,000, licensed data feed S$4,800, business development S$4,000, inference and infrastructure S$3,000, accounting S$2,000.

What that means for the beachhead

  ------------------------------------------------------------------------------------------------
  Clients                   Revenue at S$10,000     Against S$77,400 steady state
  ------------------------- ----------------------- ----------------------------------------------
  3                         S$30,000                operating at a loss; the round funds the gap

  4 (year-one assumption)   S$40,000                still a loss — this is what the raise is for

  8                         S$80,000                break-even

  15                        S$150,000               S$72,600 surplus

  30 (statutory ceiling)    S$300,000               S$222,600 surplus
  ------------------------------------------------------------------------------------------------

Year-one revenue does not cover the cost base and this plan does not claim it does. With one founder selling, no track record and no referral base, three to six clients is the honest expectation. Break-even is the eighth client, and the ceiling of the exemption is S$300,000 a year.

Why the ceiling is not a limitation. At break-even the business funds itself; between there and thirty clients it accumulates the revenue and the operating history needed for a full advisory licence, which is the Phase 4 gate. The cap buys time rather than costing opportunity.

Marginal cost. Adding a client costs almost nothing: the corpus is already read, the regimes already fitted. Adding a client's custom watchlist adds seconds of nightly compute and no inference spend at all. Gross margin above break-even is therefore very high — but it is high on a small base, and that is the honest shape of this business until Phase 2.

LTV, COCA and retention are not estimated here. All three require a real sales cycle to observe and none has occurred; §3.3 lists them among what this evidence does not establish.

8.3 Market sizing

Presented as [HYPOTHESIS] with the method stated, because the bottom-up count requires the interviews.

The rigorous approach counts identified customers from primary research and extrapolates. That is not yet possible. What follows is top-down, which is the weaker method and is offered only as an order-of-magnitude check.

Beachhead TAM: Singapore hosts several hundred licensed financial advisory firms and boutique wealth managers. Assuming 300 addressable firms and the annual contract value of S$10,000 set in §8.2, the beachhead TAM is approximately S$3 million — small enough to dominate and large enough to build on, though the honest reading is that a beachhead this size is a staging post rather than a destination, which is why §6.4's three-stage path matters. (The earlier draft assumed S$30,000 per client and reported S$9 million; that contract value was retired on 28 August when the price was revised down — see §8.2.)

Adjacent expansion: Hong Kong and Taiwan present structurally similar segments with the same language coverage, plausibly tripling the addressable base.

Tier 1, on eventual regulatory resolution: the global self-directed active trader population is in the millions, but the fraction paying for macro research is small and unmeasured. Any figure here would be the classic error of assuming a capturable fraction of a very large number, and none is offered.

9. Go-to-market

Phase 1 (months 0–6) — Evidence and access. Execute the discovery interviews. Continue the forward test uninterrupted; its value is entirely a function of unbroken duration. Publish research openly — including the null results — to build credibility with the fiduciary segment, who are reachable by reputation rather than advertising. Approach 5–8 candidate licensed firms regarding Route B. Obtain legal opinion on Route D.

Phase 2 (months 6–12) — First revenue. Lodge as an exempt adviser, or execute an appointed-representative arrangement. Convert 3–5 accredited-investor clients. Build the event layer and run the Stage 1 drift-existence test. Ship the Streamlit interface for client-facing use.

Phase 3 (months 12–24) — Scale within the cap. Reach 15–30 accredited-investor clients. Build the LLM narration layer. Ship the crowding indicator (Section 6.3) once the subscriber base is large enough for aggregate attention to be meaningful — approximately 100 active users. Recruit the two qualifying individuals required for a licence application — realistically the hardest task in the plan and the one most likely to slip.

Phase 4 (months 24+) — Licence, retail, and the Stage 2 transition. (Note: the per-user economics in §8.1 model a Tier-1 retail subscription product and belong to this phase, not to the Route A beachhead, whose economics are the 30-client model in §8.2.) Apply for a full FA licence with capital funded from operating revenue. Open Tier 1 on the content audience accumulated through Phases 1–3. In parallel, begin productising the labelled event corpus as an institutional data feed — the Stage 2 evolution described in Section 6.4, which scales without founder hours and sits largely outside the advisory-licensing perimeter.

Channel logic differs sharply by tier. Tier 3 is reached through published research and direct approach — a slow, referral-dense motion where each satisfied client is a credible referrer, satisfying the word-of-mouth condition for a valid market. Tier 1 is a content and funnel motion, deferred but seeded from day one, since the audience built during Phase 1 is the asset that makes Phase 4 possible.

10. Risks

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Risk                           Severity                Assessment and mitigation
  ------------------------------ ----------------------- ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Solo founder                   Critical                Blocks the licence, concentrates all execution and all key-person risk in one individual. No mitigation exists short of recruiting. Should be the primary use of any funding.

  Forward test degrades          High                    Live results may not reproduce in-sample performance — the deliberate overfit control exists precisely to detect this. Mitigation: continue publishing regardless of outcome. A published failure is survivable; a concealed one is not.

  Regulatory misjudgment         High                    Operating without required authorisation carries serious penalties. Mitigation: qualified legal opinion before any revenue, exempt route first.

  No validated demand            High                    The entire segmentation rests on untested hypotheses. Mitigation: the interviews, which are the immediate next action.

  Event layer fails Stage 1      Medium-High             If no tradeable post-event drift exists, the central differentiator collapses. Mitigation: the drift-existence test is deliberately staged before any commercial claim, so the failure is cheap and early.

  Data licensing                 Medium                  yfinance is not licensed for commercial use. Mitigation: budgeted feed replacement before first revenue.

  Incumbent moves first          Medium                  MacroMicro has distribution and is adding AI. Mitigation: compete on the narrow wedge, not on breadth.

  Signal too weak to sell        Measured, high          Under dependence-correct inference only the pre-specified model survives (p 0.045); the survivorship-controlled subset does not (p 0.184) and the grid-selected best does not (family p 0.090). Mitigation: the product sells process and abstention, not a Sharpe.

  Costs                          Measured, low           Turnover 23–25% per leg; break-even 60.6 bps per side against realistic execution well inside that. This risk is smaller than assumed.

  The short leg destroys value   Measured                −0.169%/week gross. Long-only is 0.83 Sharpe but is approximately the market. Mitigation: a long-only variant is honest but is not a product.
  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

What would falsify this plan. If the interviews show the information-quiet gap is not experienced as a distinct pain; if the Stage 1 drift test returns null; or if the live forward test converges to zero over six months — any one of these requires a material rewrite rather than an adjustment. Each is testable within twelve months, which is the appropriate standard for a plan of this stage.

11. The team

The supervisor's feedback noted that this document has no team section. For a company of one, that section is a risk disclosure rather than a credentials list, and it is written as one.

11.1 The founder

Hsu Wei-Ting. MSc Finance, NUS Business School (Aug 2025 – Jan 2027). BCom Finance and Management, Curtin Singapore, Distinction. Read physics at University College London 2019–2022, not completed. CFA in progress.

Quantitative intern at J.P. Morgan (Hong Kong, remote, Nov 2024 – Jan 2025), a part-time three-month engagement: liquidity research and multi-factor screening across three years of China A-shares, backtesting code for four strategy types, and a brief presented to three portfolio managers. Earlier, a cost-accounting internship in China. Python, R, SQL, VBA; Bloomberg and Refinitiv.

12.2 Why this founder for this venture

The venture is a quantitative research product whose value is methodological discipline rather than headcount, and the evidence for that discipline is this project's own record rather than a résumé line:

-   27 documented wrong priors, each a plausible belief overturned by running code, logged rather than quietly corrected.

-   Every test criterion committed to version control before the test existed. When results contradicted a registered criterion, the criterion held — the FOMC→GLD cell failed its split at 4.62× and was retired rather than relaxed.

-   Claims retired against the founder's own interest. The headline Sharpe fell from 0.60 to 0.51 on a calendar correction; the survivorship-controlled result was withdrawn entirely when dependence-correct inference put it at p = 0.184.

That is the specific competence this business sells. A vendor whose product is calibrated refusal must be run by someone who refuses.

What is deliberately absent. No track record of personal investment performance is offered in this plan. The founder manages a personal portfolio, but a self-reported, unaudited return has no place in a document that retires its own measured results for failing a registered test, and including one would undermine every disclosure above it.

11.3 What is missing, and what it costs

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Gap                                     Consequence                                                                                                Response
  --------------------------------------- ---------------------------------------------------------------------------------------------------------- -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  No qualifying compliance professional   Route A cannot be operated, and Route D is unreachable                                                     §12 funds a part-time retainer at S$2,000/month for 12 months — the first hire, before any engineer

  No sales function                       30 clients must be reached by the founder personally, through IMAS and CFA Society networks and referral   §12 funds business development access; §4.1 dates the customer-access plan

  No second engineer                      Every line of the pipeline is single-sourced; illness or departure stops the product                       Mitigated only by documentation: registered methodology, versioned state and reproducible outputs mean the work is transferable, not that it is currently transferred

  No board or advisers                    No external challenge except academic supervision                                                          Currently the faculty supervisor for this project. No adviser, co-founder or employee has agreed to join, informally or otherwise, and none is assumed anywhere in this plan.
  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

11.4 Key-person risk, stated plainly

This is a single-founder venture with no succession, no redundancy and no committed second party. §10 lists it as a structural risk and does not claim to mitigate it. The honest position for an investor is that this round funds one person and a compliance retainer, and that the binding constraint on the venture is qualifying regulatory personnel rather than technology or capital — which is why the compliance professional is the first hire and the engineer is not hired at all in this phase.

12. The ask

S$139,265 over 18 months.

This figure supersedes the S$138,100 in the 20 August draft, which the supervisor's feedback correctly identified as inconsistent with the phased table. The two tables below now reconcile exactly: the line items total S$139,265, the monthly average is S$7,737, and the three period blocks sum to the same figure. Every amount is Singapore dollars.

  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Item                                             Basis                                                                                    Monthly        Months         Total
  ------------------------------------------------ ---------------------------------------------------------------------------------------- -------------- -------------- --------------
  Founder subsistence                              Rent S$1,500; food S$700; transport S$150; utilities, phone, insurance, personal S$450   S$2,800        18             S$50,400

  Compliance professional (part-time retainer)     One qualifying individual, advisory retainer toward the FA licence requirement           S$2,000        12             S$24,000

  Legal — financial services counsel               Licensing opinion on Routes A and D, entity structuring, subscription terms              —              —              S$20,000

  Contingency (15%)                                                                                                                         —              —              S$18,165

  Commercially licensed data feed                  Replaces yfinance before any revenue                                                     S$400          18             S$7,200

  Professional indemnity insurance                 Required once advisory activity begins                                                   S$500          12             S$6,000

  Business development and research access         SFF pass S$1,000; IMAS and CFA Society membership and events; travel; materials          —              —              S$6,000

  LLM inference and infrastructure                 Per Section 8.1, including one-time historical backfill                                  S$250          18             S$4,500

  Incorporation, corporate secretary, accounting   Standard Singapore private limited setup and annual filing                               —              —              S$3,000

  Total                                                                                                                                                                   S$139,265
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Rounded, the ask is S$140,000; the precise figure is used throughout this plan and in the pitch deck.

12.1 Where the money goes each month

Founder subsistence is S$2,800 per month and accounts for S$50,400, or 36% of the round. The remaining 64% is regulatory, professional and operating cost. Averaged across 18 months, total company burn is approximately S$7,700 per month, composed as follows.

  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Line                                             Monthly average   Share             Notes
  ------------------------------------------------ ----------------- ----------------- ----------------------------------------------------------------------------------------
  Founder subsistence                              S$2,800           36%               Rent S$1,500; food S$700; transport S$150; utilities, phone, insurance, personal S$450

  Compliance professional                          S$1,333           17%               S$2,000/month retainer over 12 of the 18 months

  Legal counsel                                    S$1,111           14%               S$20,000 total, heavily front-loaded

  Contingency                                      S$1,009           13%               15% of all other lines

  Commercially licensed data feed                  S$400             5%                Runs from month 1; replaces yfinance

  Professional indemnity insurance                 S$333             4%                S$500/month, begins when advisory activity starts

  Business development and research access         S$333             4%                SFF pass, IMAS and CFA Society membership, travel

  LLM inference and infrastructure                 S$250             3%                Per Section 8.1, including historical backfill

  Incorporation, corporate secretary, accounting   S$167             2%                Setup in month 1, annual filing thereafter

  Total                                            S$7,736           100%              
  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

The average conceals real variation — legal work concentrates early, insurance only begins once advisory activity does, and the compliance retainer does not run for the full period. The actual profile is:

  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Period                                Total             Monthly average   What drives it
  ------------------------------------- ----------------- ----------------- --------------------------------------------------------------------------------------------------
  Months 1–6 — setup and access         S$50,254          S$8,376           Legal opinion (S$12,000), incorporation, SFF attendance, compliance retainer begins month 4

  Months 7–12 — first revenue           S$48,754          S$8,126           Compliance retainer at full run-rate, PII insurance begins, residual legal on subscription terms

  Months 13–18 — scale within the cap   S$40,257          S$6,710           Legal and business development taper; retainer ends month 15

  Total                                 S$139,265         S$7,737           
  ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Burn declines across the period rather than rising, because the expensive items are one-off regulatory setup rather than recurring operating cost. From month 13 the business is running at roughly S$6,700 per month against a target of 15–30 clients — meaning break-even sits at approximately three clients at S$2,500 per month, or eight at S$1,000. That threshold is the single most important number in this plan, because it determines how little has to go right for the venture to become self-funding. ### 11.2 Three notes on the budget

Subsistence is set at a working-founder Singapore level — a rented room or shared unit rather than a private apartment — because runway matters more than comfort at this stage, and an inflated founder salary is the fastest way to lose credibility with an investor who knows this market.

The budget deliberately does not include the S$250,000 base capital required for a full FA licence. That is not needed for Route A, and the intention is to fund it from operating revenue in Phase 3 rather than from this round — which is the substantive reason the accredited-investor beachhead was chosen.

The largest single line after subsistence is the compliance retainer, which reflects the assessment in Section 10: the binding constraint on this venture is qualifying personnel, not technology or capital.

Alternatively, and possibly more valuable than capital: an introduction to a licensed financial adviser or CMS licensee willing to host the venture as an appointed representative. This would compress the regulatory timeline from years to months and substitute for a substantial portion of the capital requirement. Given the analysis in Section 7, this introduction is the highest-leverage form of support available to this venture at its current stage.

Appendix A — Evidence register

  -----------------------------------------------------------------------------------------------------------------------------------------------
  Claim                                               Tag                     Source
  --------------------------------------------------- ----------------------- -------------------------------------------------------------------
  Four-regime classification, structurally selected   VALIDATED               ARI 1.000; median run length 52.5d; best silhouette

  Four-regime external corroboration weakened         VALIDATED (negative)    Event-alignment p ≈ 0.32 on extended panel

  Directional engine, 47 assets                       VALIDATED               Sharpe 0.51, p = 0.0010 (dependence-uncorrected), 706 rebalances

  Prior 0.60 / 0.43 figures                           RETIRED                 Predated the 18 Aug calendar fix

  "Edge survives dropping recent tickers"             RETIRED                 Survivorship block degraded most under the fix

  Recency decay reselects, not tie-breaks             VALIDATED               Top-k overlap 0.765 / 0.850 vs 0.90

  Directional engine, long-history subset             VALIDATED               Sharpe 0.25, p = 0.0380

  No safe-haven inversion under stress                VALIDATED (null)        Gap +0.017, p = 0.44; robust across 4 windows

  No stable semiconductor rotation order              VALIDATED (null)        Spearman −0.100, p = 0.597; stability −0.250

  Three models pre-registered and live                BUILT                   Frozen pre-registration; log from 2026-08-18

  Rotation / drift / spillover                        VALIDATED (null)        Run 20–26 Aug; drift NULL at criterion; spillover instant

  FOMC→GLD −0.3%                                      RETIRED as finding      Split FAIL 4.62×, cost test passed

  Document specificity gate                           VALIDATED               Spread 0.517, CI [0.494, 0.539], full corpus

  Document-conditioned estimator                      VALIDATED               7/45 cells, 1 survives dependence-correct null

  Reader–history agreement predicts outcome           VALIDATED (null)        Discordant outperform 0.21%, CI excludes zero

  LLM document layer                                  BUILT                   2,616 docs read ~US$30; audit clean

  Schema v2 sector axes                               DESIGNED                Pre-registered, unfunded

  Streamlit interface                                 PLANNED                 

  Negative-results library as compounding asset       BUILT                   Two documented nulls with statistics; grows per hypothesis tested

  Labelled event corpus                               BUILT                   2,616 read; 4,595 more fetched, unread

  Crowding indicator as event-layer feature           HYPOTHESIS              Testable under the Stage 1 drift protocol

  All customer segments                               HYPOTHESIS              No primary research conducted

  All price points                                    HYPOTHESIS              Never tested with a customer

  Beachhead TAM ~S$3M                                 HYPOTHESIS              Top-down only; bottom-up requires interviews

  Information-quiet gap is a real pain                HYPOTHESIS              Falsification test defined, not run
  -----------------------------------------------------------------------------------------------------------------------------------------------

Appendix B — Immediate action items

19. Execute 8–10 discovery interviews, weighted toward Tier 3 (gates Sections 4, 5, 8.2, 8.3)

20. Obtain Singapore legal opinion on Routes A and D (gates all revenue)

21. Identify and approach 5–8 candidate host firms from the MAS public registers (gates Route B)

22. ~~Run Stage 1 drift-existence test~~ DONE — NULL at criterion. The differentiator now rests on the within-episode conditional [HYPOTHESIS], not the unconditional drift.

23. Maintain the forward test without interruption (compounding asset; irreplaceable if broken)

24. Price a commercially licensed data feed (gates lawful commercial deployment)

References

The supervisor's feedback noted that this document made exact claims about statutory thresholds, competitor positions and empirical results without citation, and that "an uncited correct claim reads exactly like a wrong one." This section is the response. Where a source has not been verified, that is stated rather than concealed.

Statutory and regulatory

25. Financial Advisers Act 2001 (Singapore), s.20(1)(g) — power to exempt prescribed persons from holding a financial adviser's licence. Also s.20(10) (withdrawal of exemption) and s.114 (false information to the Authority).

26. Financial Advisers Regulations (Singapore), reg. 27(1)(d) — prescribes the person providing financial advisory services to not more than 30 accredited investors in respect of investment products other than life policies.

27. Monetary Authority of Singapore, Form 20 — Notice of Commencement of Business by an Exempt Person under section 20(1)(g) of the Financial Advisers Act 2001 read with regulation 27(1)(d) of the Financial Advisers Regulations. The explanatory notes to this form are the source for items 1 and 2 above and for the key-officer, controller and fit-and-proper obligations described in §7.2.

28. Monetary Authority of Singapore, Guidelines on Fit and Proper Criteria — referenced in the Form 20 declaration.

29. Financial Advisers Act 2001, s.23 — appointed representative (Route B). Provision identified from the supervisor's feedback; not independently verified.

Not cited, and deliberately so. The provision imposing the deadline for filing Form 20 is not stated in this plan. Form 20 does not cite it, and naming an unverified regulation in a document of this kind would be worse than acknowledging the gap. It is question 4 of §7.4.

Methodological and academic

30. Baur, D. and Lucey, B. — gold as a hedge versus a safe haven. Framing for the Problem 1 test in §3.1.

31. Baur, D. and McDermott, T. — international evidence on gold as a safe haven.

32. Cohen, L. and Frazzini, A. — Economic Links and Predictable Returns. The supply-chain framing behind the rotation hypotheses in §3.1.

33. DerSimonian, R. and Laird, N. (1986) — random-effects estimator, used for the between-regime variance term in the precision-weighted blend.

34. Hamilton, J. D. (1989) — regime-switching econometrics; the origin of the regime layer's framing.

35. Loughran, T. and McDonald, B. — textual analysis and financial sentiment dictionaries.

36. Lewis, P. et al. — retrieval-augmented generation.

37. Fama, E. and French, K. — three- and five-factor models. Chen, Roll and Ross — macroeconomic factors and asset pricing.

38. Aulet, B., Disciplined Entrepreneurship: 24 Steps to a Successful Startup. The framework structuring §4 through §8.

Items 6–13 are the anchor literature identified at project inception and used for framing rather than for quantitative results. Full citations are in the project's methodology log.

Background reading

39. Aziz, A., Advanced Techniques in Day Trading: A Practical Guide to High Probability Strategies and Methods. ISBN 978-986-384-481-5 (Traditional Chinese edition).

40. The Privilege of Getting Rich. ISBN 978-986-06337-3-3. A history of interest rates and central banking — how policy rates are set, how and whether they propagate to long-dated government bonds, and how different nations have intervened at each end of the curve. This is the background to the FRED series chosen for the macro panel in §3.1 and to the separation of stance from direction in the document reader's schema.

41. Venture Capital in Taiwan. ISBN 978-626-98639-0-7. The basis for the jurisdiction discussion in §7.1 — the finding that Taiwanese venture activity concentrates in hardware and semiconductors and is thin for software-only financial products.

Read during the project's first weeks. Items 16 and 17 inform arguments that appear here — the macro panel design and the jurisdiction discussion respectively. Item 15 does not, and is listed for completeness.

Empirical results

All quantitative claims in §3 are reproducible from the project repository. The relevant artefacts:

  ----------------------------------------------------------------------------------------------------------------------------------------
  Claim                                                       Where it is produced
  ----------------------------------------------------------- ----------------------------------------------------------------------------
  Backtest, Sharpe 0.51 / 0.25                                src/analog_backtest.py; estimator frozen at commit 9062391

  Turnover, cost ladder, break-even, short leg, family test   backtest_evidence.py → docs/backtest_evidence.md

  Dependence-corrected p-values                               as above; block-permutation null, 200 iterations, seed 42

  Problem 1 safe-haven null                                   docs/ methodology log, robustness sweep across windows and transformations

  Rotation nulls, spillover, PEAD                             pre-registrations in docs/prereg_*.md, results alongside

  Specificity gate, spread 0.517                              src/gate_check.py, 10,000 iterations, full corpus

  Step 3 unblinding, 7 of 45                                  unblind_step3.py → docs/unblind_step3_results.md

  Robustness re-test, 1 of 7                                  step3_robustness.py → docs/step3_robustness.md

  Agreement-flag test                                         agreement_test.py → docs/agreement_test.md

  Corpus cost, ~US$150                                        src/corpus_status.py, from measured billed tokens
  ----------------------------------------------------------------------------------------------------------------------------------------

Competitor and market claims

Not independently sourced. The competitor positions in §6 (MSCI/Barra, RavenPack, macro research desks, retail signal vendors) and the firm counts in §4 are the founder's characterisation from public materials and structural reasoning. They are labelled [HYPOTHESIS] in the text and no headcount, revenue or licence-price figure for any competitor is asserted in this version. The earlier draft's claims about Barra's institutional reach and MSCI's revenue composition have been removed rather than sourced.


---

# APPENDIX G — POST_SUBMISSION_STATE.md (28 Aug 2026) — SUPERSEDED

> *Kept for the record. Where it conflicts with Part A or TRACK, they win (e.g. launchd is now 15:00, not 18:30; reports are write-once; the wrong-prior tally is 28+).*

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


---

# APPENDIX H — TRACK addendum: report-level scoreboard (8 Sep 2026) — SUPERSEDED

> *The plan that became TRACK §3.8; steps 1–7 done 14 Sep. Kept for the record; proposals here (e.g. h*=5) were revised by registration.*

# TRACK addendum — report-level scoreboard

*Drafted 2026-09-08. To be merged into `TRACK.md` as §3.11 (undone), with one
row added to §1 (running) once step 5 is live. Nothing below touches
`models.yaml`, `forward_ledger.csv`, or any report already emitted under
`outputs/reports/`. API cost of steps 0–6 is zero — everything runs on cached
reads and cached prices.*

**What this delivers.** A second ledger beside the forward test that scores the
decision report itself — hit-rate and asymmetry when the report speaks,
coverage when it doesn't — appended nightly by `daily_run.sh` and never
rewritten. Plus a backfilled version of the same ledger so a new document
source can be judged in weeks rather than months.

---

## 3.11 Report-level scoreboard — registered, not built

Ordered. Each step has a done-criterion; a step is not done until that line is
true. Steps 0–1 need the founder; 2–6 are build; 7 is the first use.

### 0. Close the three placeholders in the pre-registration — founder, 1 hour

`docs/prereg_report_scoreboard.md` carries three `[FILL]` marks:

| placeholder | where the answer lives | proposal |
|---|---|---|
| horizon set `h ∈ {…}` | the unblinding script that produced the 7-of-45 result (not `analog_event.py` — it carries no horizons) | inherit that script's set unchanged |
| primary horizon `h*` | founder decision | 5, matching Model 1 and the forward scoreboard |
| source-expansion tolerance (§8) | founder decision | 2 percentage points on pooled hit-rate |

**Done when:** no `[FILL]` remains and the file is committed. **Commit hash
recorded here before step 2 starts.** This is the standing rule — criterion in
version control before the code exists.

### 1. Confirm the report JSON carries what the scoreboard needs — 1 hour

Open the reports emitted since 27 Aug (`outputs/reports/*.json`) and check for,
per asset: `net_direction`, tier, ESS, `w`, matched-event count, dominant
source, agreement flag; per report: regime, posterior confidence, the document
list with source/direction/magnitude/specificity/novelty/confidence.

If a field is missing, amend the step 6 emitter to add it **going forward**.
Reports already on disk are not regenerated; the scoreboard scores only what a
report actually contained on the day.

**Done when:** a field checklist is written into the prereg §1 as an amendment
(dated), and the emitter matches it.

### 2. Register the acceptance tests — before any scoring code, 1 hour

Same protocol as `analog_event.py` §9.2: the scorer is built against ledgers
whose truth is known, and no real figure is computed until all pass.

| test | what it checks |
|---|---|
| planted-perfect | a ledger whose calls equal realised signs scores 100% hit-rate and clears the null at p < 0.001 |
| planted-shuffled | calls permuted across dates score inside the null band (rejection at α=0.05 within [0.02, 0.08] over 200 reps) |
| min-count | any cell with < 30 non-overlap rows prints "too few to report" and no number |
| non-overlap sampler | every `h`-th report date per asset, first date fixed — verified by hand on a synthetic 20-date ledger |
| exclusions | abstentions, divergences, zero net-direction and zero-return rows land in coverage, never in hit-rate |
| two entries | primary (close `t`) and tradeable (open `t+1`) columns differ by exactly the overnight gap on a synthetic path |

**Done when:** the table is committed as prereg §12 before `report_scoreboard.py`
exists.

### 3. Build `src/report_scoreboard.py` — 1–2 days

Reads `outputs/reports/*.json` → one row per (date, asset, horizon) →
realised returns from the price cache (primary and tradeable) → coverage
block → naive and non-overlap metrics → block-permutation null (10,000 draws)
→ writes:

- `processed/report_ledger.csv` — **append-only**, one row per matured
  (date, asset, horizon); a matured row is never edited;
- `processed/report_scoreboard.json` — regenerated from the ledger each run;
- `docs/report_scoreboard.md` — regenerated, same layout as
  `forward_scoreboard.md`: coverage first, then a running summary with naive
  and non-overlap columns, then the full log.

Idempotent: if no new US close has landed since the last run, it skips, as
`forward_log` does. Pending rows show `pending`, not a blank.

**Done when:** all six acceptance tests pass on synthetic ledgers, results
committed to `docs/report_scoreboard_selftest.md`, any test repaired after
failing declared there.

### 4. First real run — 10 minutes

Run on the reports since 27 Aug. Expected output: every cell prints "too few
to report" and a coverage block. **That is the correct result** and it is
committed as the first real scoreboard file. If a number prints, step 3's
min-count rule is wrong and the run is a defect, not a finding.

**Done when:** `docs/report_scoreboard.md` exists with coverage figures and no
hit-rate.

### 5. Wire into `daily_run.sh` after `forward_log` — 30 minutes

One line, after the forward log and after the nightly document reads, so the
day's report has been emitted before it is scored. Same launchd slot (15:00).
A staleness guard like the forward log's: if the report for the last US close
is missing, log the gap date and continue — never score a report that does
not exist.

**Done when:** three consecutive weekdays show a scoreboard regenerated
unattended, and a row is added to `TRACK.md` §1:

| item | what should be true | how to check | if it isn't |
|---|---|---|---|
| Report scoreboard | `docs/report_scoreboard.md` regenerated each weekday; ledger row count rising | `tail -5 processed/report_ledger.csv` | Same as the forward log: the gap is permanent, record the dates |

### 6. Backfilled ledger — `src/report_backfill.py` — 1–2 days, $0

Runs the full live-basis pipeline over every historical document date in the
corpus: expanding standardisation, expanding regime labels, step 3 with
leave-one-out on the query document, §7.2 fixed weighting, step 6 emitter.
Writes `outputs/reports_backfill/<corpus_hash>/YYYYMMDD.json`, then scores
them with step 3's scorer into `docs/report_scoreboard_backfill_<hash>.md`.

Compute cost only — every document read is cached. Runtime unknown until
tried; the expanding regime labels are the slow part (TRACK §4 already lists
persisting them as an upgrade — do that here if the backfill takes over an
hour, since the backfill is the reason it's worth doing).

**This is the baseline every new source is compared against.** Its hash is
recorded in `TRACK.md` §5 with the date.

**Done when:** the backfill scoreboard exists, its `corpus_hash` is logged, and
the prereg §6 criterion has been applied to it once — pass, inconclusive or
"too few" — and the verdict written into §5 with the date.

### 7. Source expansion — one registration per source, cost per source

Waits on the founder's source list. For each source, in this order:

1. one-paragraph registration under prereg §8: fetch route, public-domain
   status, date rule (publication, not event), expected docs/year, expected
   axis, expected coverage gain as a number, expected hit-rate direction
   (including "none");
2. **read cost stated up front** from a token count on a 20-document sample,
   not from a corpus average — the August lesson;
3. fetcher (`src/fetch_sources.py`), and a `PROFILES` entry in
   `src/doc_read.py` **reviewed by the founder line by line** before the first
   paid read (TRACK §2, "does the reader's logic match the founder's");
4. read under the **existing prompt version** — no prompt change, so no
   mixed corpus;
5. specificity gate re-run on the enlarged corpus;
6. backfill regenerated under the new hash; paired comparison against the old
   hash on shared days; §8 verdict: pooled or reported separately;
7. `TRACK.md` §5 row with date, hash, verdict.

**Done when:** each source has a §5 row. A source read but not yet compared is
not done.

---

## What is deliberately not on this list

- **TRACK §3.1** (4,595 political documents, ~US$60) — deferred by the founder,
  stays in §3. It is the first candidate for step 7 when the balance allows,
  because it needs no fetcher and no new profile.
- **Any change to `models.yaml`, `forward_ledger.csv` or the three frozen
  models.** The scoreboard reads the report; it never feeds back into it.
- **Any change to the report's tiers, thresholds or abstention floor** on the
  strength of a scoreboard result. A tier reversal (prereg §6.1) is published;
  it is not fixed by moving a threshold.
- **A public or investor-facing view** until a cell clears the 30-row rule.
  Until then the scoreboard is coverage figures and the words "too few to
  report", and that is what any reader sees.


---

# APPENDIX I — Communications drafts (17 Sep 2026)

> *LinkedIn v3 post and article, and the coffee-chat script. Drafts, not published; no performance figures by rule.*

# LinkedIn — two pieces, v3 (17 Sep)

Reframed: what was built and what it established, in a builder's voice. No performance
figures. Publish the article first, then the post with the link. Brackets are yours.

---

## 1. The post (~1,400 characters)

Over the summer I built a system that reads the market every morning — and knows when to say "not enough evidence."

For my MSc Finance capstone at NUS I built a regime-aware cross-asset framework. Eight macro series place each day in one of four monetary environments. A language model reads every Fed statement, earnings release and executive order published that day — what it says, how specific, how new. The engine matches the day to its closest precedents in twenty years of history and reports what followed, or abstains when fewer than eight comparable cases exist.

It has run unattended every weekday since August. 2,616 documents read under one schema. Every threshold committed to version control before any result was seen. And a referee that scores the report's own calls, tested on synthetic data with known answers before it saw a real one.

What the tests settled is as valuable as what they found. Several textbook beliefs about gold, sector rotation and trend signals did not hold on this data, and the record says so with dates. That is what allowed the next phase to be designed on evidence rather than intuition: twelve registered routes toward what a trader actually uses each morning — how much to hold, how big today could be, how unfamiliar today is — with transaction costs and capacity inside every test.

The full write-up is in the article. If you work in macro or quant research, or run a book in Singapore or Hong Kong, I'd enjoy comparing notes.

[link to article]

#quantfinance #fintech #NUS #MScFinance #Singapore

---

## 2. The article (~1,800 words)

### Building a market-reading engine that knows what it doesn't know

*[Optional subtitle: An NUS capstone, a daily report, a referee, and twelve routes]*

Between May and August this year I built a system for my Applied Faculty Project at NUS Business School. The brief was open: a piece of applied research that could stand as the foundation of a business. I chose to build a regime-aware cross-asset signal framework — an engine that reads the macro environment and the day's documents, compares today to its closest precedents, and tells the reader plainly how much evidence there is.

This is what it does, what its own tests established, and where it goes next. Performance figures are absent on purpose: the project's rules don't permit one until the forward record is long enough to carry an interval rather than a point.

**What the system does**

Five steps, every trading day, nothing hand-adjusted.

It locates: eight macro series from FRED place the day in one of four monetary environments, found by unsupervised clustering rather than chosen by hand. It reads: every Federal Reserve statement, earnings release and executive order published that day is classified by a language model — what it says, how specific it is, how new. It combines: where several documents land on one day, they're weighted by size, specificity and confidence, and where two disagree, both are shown and neither is merged. It compares: past days matching both the macro state and the document reading are located and weighted. And then it reports — or abstains. Fewer than eight comparable precedents and no number is issued.

The abstention is a feature, not a gap. On most days, for most assets, the honest answer is that no usable precedent exists, and a tool that says so is worth more to a fiduciary than one that always has a view.

**What the tests established**

Before running anything I wrote each belief down as a testable claim with a pass criterion, committed the criterion to version control, and only then ran the test. That order — register, build, run — is the spine of the project, and it produced a set of settled questions that I'd now consider its most durable output.

On this panel, gold does not decouple from equities under liquidity stress; if anything the two co-move slightly more, consistent with dash-for-cash selling. Sector rotation has no stable running order: the semiconductor supply chain reprices in the overnight gap after an announcement, and by the next open the move is complete. A model that matched on the *direction* of macro movement appeared to beat one matching on the *level*, until features were standardised on a live basis and the gap closed — a look-ahead, now declared. And the one price model that survived a dependence-corrected test did so on the full universe and not on the survivorship-controlled one, which is stated beside it.

Each of those is a dated entry in a log that now runs to 29 items. Every entry is a plausible belief overturned by running code, and together they are what let the next phase be designed on evidence.

**Three rules that held**

*Pre-register before test code exists.* When a hard-coded window was found silently returning the same result whatever its input — which could have recorded a false confirmation of a registered test — it was the register-then-build order that made the failure visible.

*Lower and correct beats higher and wrong.* A calendar fix removed about 196 phantom rows from the clustering and lowered the headline backtest figure. The lower figure is the one in the record.

*A null deserves the same scrutiny as a positive.* The gold result went through a robustness sweep across four window lengths and two transforms before it was banked.

**The referee**

The project had a scoreboard for its price models and none for the thing it actually produces — the daily report. So I built one under the same rules: criterion first, then seven acceptance tests on synthetic ledgers with planted answers (a report that was right every time must score 100%; coin-flip calls must be recognised as noise; fewer than thirty observations must print "too few to report" and nothing else), and only then real data.

Then I re-ran the whole pipeline as-of over fifteen hundred historical document days, with each day's precedent pool restricted to what was knowable at the time, and let the referee mark it. The verdict was registered in advance as "fail or inconclusive," and it was inconclusive: the report's short-horizon directional calls sit at the edge of what following the market's own drift would give. That is a useful result. It says where the value in a document reading does *not* live — in calling the next three days' sign — and points to where it might: the size of the move, the appropriate exposure, and how unusual the day is.

**How it became a business plan**

The commercial idea came from a conversation in July with my supervisor, Dr Lee Yen Teik, about whether institutional clients would demand exclusivity. His answer reframed everything: specialist data vendors don't sell alpha — alpha never leaves the client's building. They sell a unique input, one piece of a puzzle the client assembles. Barra started that way. So did RavenPack.

That gave the positioning: a regime label, a document reading, an explicit precision and a fixed rule for silence — sold to people who manage other people's money and must justify an allocation to a committee regardless of outcome. For that buyer, a vendor whose record shows what was tested and retired is the more credible one.

The plan follows the Disciplined Entrepreneurship framework, and the beachhead choice was the surprising part. The intuitive first customer is the self-directed trader, and in Singapore that segment requires a licence a one-person company can't hold. Accredited investors and family offices are serviceable under an existing exemption. So the sequence inverts — institutional first — and the plan states which statutory reading that rests on and that counsel has not yet confirmed it. Every commercial number is labelled as a hypothesis to be tested in customer conversations.

**What comes next: twelve routes**

The referee's verdict and the published literature point the same way: what a language model reads from a filed document is largely absorbed in the overnight gap. So the next phase leads not with direction but with what a macro desk actually consumes each morning.

Twelve routes, each a registered track — criterion first, acceptance tests on synthetic data, then real data, then the verdict recorded whichever way it falls — ranked by likelihood of success and by the knowledge each needs, with transaction costs, capacity and a one-session execution lag inside every test. Among them:

- *How much to hold today.* A long-only position-size dial that scales with forecast volatility and tilts by regime, designed around the documented reasons volatility-managed strategies disappoint out of sample: no fitted scaling constant, no leverage, changes only on a confirmed regime.
- *How big today could be.* The reader's specificity, novelty and magnitude as inputs to a volatility forecast — the part of a document's effect the overnight gap doesn't take.
- *How unfamiliar today is.* One daily number for how far today's macro state and document mix sit from anything since 2006, feeding straight into position size.
- *Which scheduled days pay.* Most of the equity premium arrives on a handful of announcement days a year; the regime engine may be able to tell which.
- *A reader that runs locally.* A small model trained on the paid reader's own 2,616 past answers, checked on 300 it has never seen, so that no client document leaves the machine.
- *A ledger for one's own trading.* Any rule a trader already follows — entry, size, stop — written down or logged as an actual fill, and scored by the same referee as the models. A timestamped, falsifiable record of one's own calls is something few traders have of themselves.

Each route runs on the existing universe and a broader one, both registered together, so that "it needs more assets" is reported as diversification rather than presented as signal. The existing report stays; each route adds a block to it.

**Where it stands**

The engine runs unattended every weekday. Three frozen models have logged forward since 19 August in a ledger committed to version control each night. The report referee runs beside them. A corpus of 2,616 filings has been read under one schema and passed a registered discrimination test. The first routes are registered and building.

What is not yet there: customers, revenue, a counsel opinion, or a live performance figure. The forward record will carry one when it is long enough to report an interval.

**If this is your field**

If you work in macro or quant research, or run a book in Singapore or Hong Kong, I'd enjoy comparing notes on how a daily read of regime, documents and precedent would fit the way you already work. If one of the twelve routes is something you've built before — model predictive control for sizing, fine-tuning a small reader, execution and cost modelling, the Fed-path work — the plan is written to be extended, and I'd rather build it with people than alone.

I graduate in January 2027. `[Optional: "I'm also open to conversations about quantitative research and data roles starting then."]`

The full record — every test, every date, and the twelve routes with their criteria — is in the repository, and I'm glad to walk anyone through it.

---

*Notes: Dr Lee is named once — send him a line first. "29" assumes the nightly-reads entry is logged; change to 28 if not. Five hashtags on the post, none on the article. Weekday morning Singapore time.*


## Coffee-chat script (17 Sep)

**30 seconds.** "I built a system for my MSc capstone at NUS that reads the macro environment every
morning — eight Fed data series place the day into one of four monetary regimes — and reads every
Fed statement, earnings release and executive order published that day through a language model.
It finds the closest precedents in twenty years of history and tells you what followed. When there
isn't enough evidence, it says so and issues nothing. That's turned into a business plan: a research
service for family offices and boutique managers, where the product is a documented reason and an
honest confidence, not a buy signal."

**Two minutes.** It started as an academic requirement and became something I want to build. The
engine runs unattended every weekday; it has read 2,616 filings under one schema; everything is
pre-registered so nothing can be fitted after the fact. Much of what it tested came back negative —
gold doesn't decouple in a liquidity crunch on my data; sector rotation has no stable order; a model
that looked better had a look-ahead — and that record is what makes the commercial idea work:
specialist vendors don't sell alpha, they sell a unique input. Right now: no customers, no revenue,
no counsel opinion. Next phase: registered routes toward how much to hold, how big today could be,
how unfamiliar today is.

**"Does it make money?"** "I can't show a performance figure yet and won't invent one. The forward
test has run since 19 August in a ledger committed nightly. Its own scorer said the directional calls
are not distinguishable from following the market's drift — which is why the next phase leads with
exposure and risk rather than direction."

**"Why would anyone buy it?"** For an allocator: a dated, written record of what the evidence was
when they acted — an audit trail they currently assemble by hand. For a trader: a fixed rule for
when the vendor refuses, so that when it speaks, that is itself information — and the next version
tells you when it cannot see. For diligence: I publish what didn't work; nobody can ambush me with a
failure I've documented.

**What I want from them.** "To find out whether the problem I've described is one you actually
have. If it isn't, that's the most useful thing you could tell me." Then listen.

**Avoid.** Opening with "most of it didn't work"; quoting Sharpe or hit-rates; counting routes as a
selling point; claiming the routes fix gaps in published research.
