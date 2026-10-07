# Methods and measurables — everything behind app.py, from the beginning

*Written 30 September 2026. One entry per measurement or test, in the order the product is built:
the data and regime layer, the document layer, the precedent estimator, the hypotheses tested on the
way, the price models and forward test, the referees, the post-submission tests, and finally the
numbers the app actually prints. Every entry has the same shape: what is measured, how the question
arose, the method and data pool in plain English, a summary of whether the method answers the
question directly or proves it by an alternative statistic, and the result. No procedure numerics.*

*"Direct" means the method measures the thing itself (e.g. the correlation of gold with equities).
"Alternative" means the question could not be measured directly and was settled by a different
statistic that implies the answer (e.g. a permutation null that asks whether a result could have
arisen by chance).*

---

## A. The data and regime layer

### A1. The macro panel

**Measures.** The state of the US monetary environment on each trading day.
**How the question arose.** The project's first premise: the relationship between news and asset
prices is not the same in every monetary environment, so "which environment are we in" must be
measured before anything else.
**Method and data pool.** Eight series from FRED (the St Louis Fed's public database): nominal and
real 10-year yields, the 2-year yield, the 10y–2y spread, the effective federal funds rate, M2 money
supply, the broad dollar index and VIX. Daily from 2006, on the New York Stock Exchange's own trading
calendar (not a Monday-to-Friday calendar — that distinction later turned out to matter, see A4).
Monthly series are carried forward to each trading day; returns are never carried forward.
**Summary.** Direct: this is the raw measurement everything else conditions on. A choice, not a test.
**Result.** The panel; extended from 2018 back to 2006 by dropping one redundant series (SOFR, which
duplicates the fed funds rate) rather than by inventing values.

### A2. Reducing the panel to its main movements (principal components)

**Measures.** The three dominant patterns of co-movement in the eight macro series.
**How the question arose.** Eight series move together in a few ways; clustering on all eight
would over-weight the overlapping ones.
**Method and data pool.** Principal component analysis on the standardised panel — a standard
way of finding the few directions in which the data varies most. Three components kept.
**Summary.** Direct: a reduction, not a hypothesis.
**Result.** Three components. One lesson: the component that tracks market stress moved from
second to third position when the panel was lengthened, so components are now identified by what
they correlate with (the stress axis is the one most correlated with VIX), never by position.

### A3. Finding the market regimes (Gaussian mixture clustering)

**Measures.** Which of a small number of recurring monetary environments each day belongs to, and
how confident the model is in that label.
**How the question arose.** Monetary regimes are discrete states — easing cycles, tightening cycles,
zero-rate periods, crises — not points on a line; one model averaged across them hides what happens
inside each.
**Method and data pool.** A Gaussian mixture model — a method that assumes the data is a blend of a
few overlapping clouds and assigns each day a probability of belonging to each — fitted on the three
components, re-fitted on an expanding window of history every twenty sessions so that no day's label
uses data after its own date. Labels are ordered consistently across re-fits.
**Summary.** Direct: the clustering *is* the regime measurement. The confidence shown in the app is
the model's own probability for the chosen label.
**Result.** Four regimes, used throughout.

### A4. How many regimes? (model selection)

**Measures.** The right number of clusters.
**How the question arose.** The count is an empirical question; a theory of monetary policy
suggests three or four, the data must decide.
**Method and data pool.** Three criteria fixed in advance and applied to candidate counts: stability
across random starts (does the same partition come back?), persistence (how many days a regime
typically lasts — a regime that flickers every few days is not tradeable), and silhouette (how well
separated the clusters are). A fourth, external check: whether regime changes line up with dated
macro events more often than chance, tested with a permutation null.
**Summary.** Alternative statistics standing in for a question with no direct answer.
**Result.** Four regimes won on all three internal criteria. The external event-alignment check,
which had looked strong on the short panel, became weak on the long one and the documentation was
rewritten to say "structurally best but weakly corroborated externally."

### A5. The trading-calendar correction

**Measures.** Nothing new — a correction. The panel had been built on a Monday-to-Friday calendar
that includes market holidays, so about 196 phantom days with macro values and no prices had
entered the clustering as near-duplicate observations.
**How the question arose.** Found by counting days with zero price coverage, in August.
**Method and data pool.** Rebuilt on the exchange's session calendar.
**Summary.** Direct. Logged because it changed a result: the headline backtest figure fell, and the
lower figure is the one kept ("lower and correct beats higher and wrong").

### A6. The 47-asset price panel

**Measures.** Daily log returns for the assets the engine studies.
**How the question arose.** A regime engine needs assets to be measured against, spanning several
crises so that each regime is observed more than once.
**Method and data pool.** 47 ETFs and single names from Yahoo Finance, in three groups by length of
history: long-history core (used for all backtests), modern-theme overlay (tracked, excluded from
backtests — too short), and spotlight single names (analysed only within their own history). Five of
them — SPY, TLT, GLD, UUP, USO — are the markets the app reports on. A day on which an asset did not
trade is left blank, never filled.
**Summary.** Direct; a data choice. One documented limitation: today's ticker list applied to ten
years of history is survivorship-biased, which is why a survivorship-controlled sub-universe is kept
for every result.

---

## B. The document layer

### B1. The corpus

**Measures.** Every document of five kinds published on each trading day.
**How the question arose.** The product's thesis is that filed decisions — not news coverage of them
— are what to read.
**Method and data pool.** FOMC statements and minutes (the Fed's website), earnings releases (SEC
EDGAR, 8-K item 2.02, and 6-K for foreign issuers, taking the attached press release rather than the
cover page — a 307-document mistake caught early), executive orders and proclamations (the Federal
Register). About 2,600 documents read; several thousand more political documents fetched and
awaiting reads.
**Summary.** Direct. A documented gap: anything that never becomes a filing — a speech, a headline,
a pipeline accident — is invisible, and the app says so.

### B2. The reader (language-model classification)

**Measures.** For each document: the direction it implies for five markets (equities, bond prices,
gold, the dollar, oil), how large, how specific the language is, how new relative to the previous
document of the same kind, how confident the reader is, and — for the Fed — a separate *stance*
(hawkish or dovish today) distinct from the path it implies.
**How the question arose.** Text has to become numbers before it can be compared across history; a
fixed schema makes every document comparable to every other.
**Method and data pool.** One language model, one prompt version, frozen since 23 August; every
document read under the same instructions. Novelty is judged with the previous document of the same
source in view.
**Summary.** Direct: this is the measurement of the text. Its validity is checked by B3–B5.

### B3. The specificity gate

**Measures.** Whether the reader's "specificity" score actually separates decided policy from
rhetoric — the one field the weighting step depends on.
**How the question arose.** If every source scored alike, the field would be decoration and nothing
could be weighted with it.
**Method and data pool.** Registered before running: resample documents within each source many
times (a bootstrap) and ask whether the gap between the high-specificity sources (statements,
earnings) and the low ones (proclamations) is reliably wide, and whether every high source sits above
every low one.
**Summary.** Alternative: the bootstrap proves the separation is not a sampling accident.
**Result.** Passed on the full corpus, and passed again unchanged after the statement texts were
rebuilt and re-read in September.

### B4. Internal-consistency audits of the reader

**Measures.** Whether the reader's fields agree with each other where they must.
**How the question arose.** A reader can be fluent and wrong; its own fields should not contradict
each other.
**Method and data pool.** Three checks on the reads: the Fed stance field against the implied
direction for bond prices (a hawkish read should imply lower bond prices — strongly negative
correlation); the earnings surprise field against the implied direction for the company's own equity
(agreement counted); complete filings against truncated ones (specificity and confidence should
fall when text is cut).
**Summary.** Direct comparisons of the reader with itself.
**Result.** All three behaved as they should. A false alarm along the way: some Fed hikes read as
"positive for bonds" — each turned out to carry softening guidance, and four were regex false
positives on the phrase "increase … remains unlikely."

### B5. The agreement flag

**Measures.** Whether the documents and the history agreeing on direction predicts a better outcome.
**How the question arose.** Intuition says a signal confirmed from two sides is stronger.
**Method and data pool.** Registered before running; outcomes split by whether the reader's direction
and the precedent direction agreed, with a null.
**Summary.** Direct test of the intuition.
**Result.** The reverse: disagreement did better. The flag is now shown but never weighted.

---

## C. The precedent estimator (the number the app prints)

### C1. Combining documents on one day

**Measures.** A single net reading per market when several documents land together.
**How the question arose.** Days like a tariff announcement bring several filings at once.
**Method and data pool.** Each document's direction is weighted by its magnitude, specificity,
novelty and confidence, multiplied together; where two sources point opposite ways both are shown and
nothing is combined.
**Summary.** Direct; a rule, fixed in advance.

### C2. Choosing precedents and weighting them

**Measures.** Which past days are "like today," and how much each counts.
**How the question arose.** The product's question is "when documents like today's landed in
environments like today's, what happened next."
**Method and data pool.** The pool is every past session in the same regime with a document of the
same class whose outcome had already closed by that day (a rule added after a look-ahead was found
in the backfill). Each precedent is weighted by how close its macro state is to today's (a Gaussian
kernel on the three components) and by recency (an exponential decay). Outcome: the asset's return
over the next three sessions.
**Summary.** Direct.
**Result.** A registered diagnostic showed recency weighting *reselects* which days count rather than
fine-tuning among them, so the word "analog" was judged to promise more than the mechanism delivers.
Both engines reduce, roughly, to "take the most recent same-regime days and average them."

### C3. The estimate, the effective sample size, and the abstention rule

**Measures.** The conditional estimate, how many precedents genuinely count, and whether to speak
at all.
**How the question arose.** A view from three similar days is not a view; the product must refuse
when evidence is thin.
**Method and data pool.** A precision-weighted blend with random-effects shrinkage (the
DerSimonian–Laird estimator from meta-analysis, which shrinks a small or noisy sample toward the
long-run average); effective sample size by Kish's formula (a sum of weights squared over a sum of
squared weights). Below eight effective precedents the report abstains. Tiers are bands of effective
sample size.
**Summary.** Direct; the rules are the product.
**Result.** Most days, most markets abstain. That is by design.

### C4. Building the estimator blind

**Measures.** Whether the estimator finds what is planted and nothing else.
**How the question arose.** An estimator built while looking at real outcomes can be tuned to them
without anyone meaning to.
**Method and data pool.** The link between documents and returns was destroyed (shuffled), a known
effect planted, and six acceptance tests run before the real link was restored. Three tests failed
and were repaired; the original failures are kept in the record.
**Summary.** Alternative: synthetic data with known answers, in place of real data with unknown ones.

### C5. Unblinding: does the conditioned estimate predict anything? (45 cells)

**Measures.** Whether the estimator's conditional view beats the unconditional average, per market
and horizon and source.
**How the question arose.** The one result the product depends on.
**Method and data pool.** Pooled leave-one-out on the real link, dependence-correct inference, 45
cells (market × horizon × document class); then a re-test of the survivors with a chronological split.
**Summary.** Direct, with a correction for the many cells tested.
**Result.** Seven of 45 looked positive; one survived the re-test (Fed minutes → oil at five days),
and it is treated as a candidate, not a finding. The product therefore sells process and abstention,
not forecasting accuracy — stated on the deck and in the app.

---

## D. Hypotheses tested along the way

### D1. Gold as a safe haven (Problem 1)

**Measures.** Whether gold decouples from equities under liquidity stress.
**How the question arose.** A popular belief, and the author's own prior from the central-banking
reading.
**Method and data pool.** Rolling correlation of gold with equities, compared across stressed and
calm periods. To avoid circularity (the macro regime is built partly from VIX, which also moves the
correlation), stress was defined by a separate two-state clustering on correlation breadth and
realised volatility across a basket that excludes both gold and equities. Robustness across four
window lengths and two correlation transforms. Daily ETF prices, 2006 onward.
**Summary.** Direct measurement, with the conditioning variable deliberately built apart from the
outcome.
**Result.** Null, robust. If anything gold co-moves slightly *more* in stress — consistent with
dash-for-cash selling. The null was run through the same robustness sweep as a positive would be.

### D2. Sector rotation and lead–lag (Problem 2)

**Measures.** Whether there is a stable running order in which related stocks reprice after news —
the semiconductor supply chain being the test case.
**How the question arose.** The original product idea: predict the second mover from the first.
**Method and data pool.** Seven hypotheses across four instruments: unconditional lead–lag
correlations; chain rotation within sub-periods; episode rotation with predictions declared before
the run; cross-asset and sector rotation; cross-firm spillover with an intraday decomposition; a
post-earnings drift test; a scheduled-macro-event drift test with a tradeable entry window. Every
candidate pair was then split by time and charged costs.
**Summary.** Direct tests of each form of the claim, with chronological splits as the proof that a
discovered pattern is not a one-period accident.
**Result.** Null at every level. The mechanism explains all of it: rotation is event-initiated and
reprices in the overnight gap, so any test entering at the next open sees nothing. The spillover
result went from strongly significant to indistinguishable from zero once entry used only
tradeable information — kept as a measurement of what look-ahead is worth. The post-earnings drift
positive lived entirely in three hindsight-selected names.

### D3. Regime–event alignment (GDELT)

**Measures.** Whether regime switches line up with dated world events more than chance.
**How the question arose.** An external check on the regime labels.
**Method and data pool.** GDELT, a free global events database, filtered by theme (tariffs, export
controls, sanctions, military action — themes rather than names, for signal quality); a baseline-
removed test with a permutation null over windows. A reproducibility episode: the original data pull
had been a manual console export capped at 500 rows, which silently truncated it; the query was
recovered, scripted and extended.
**Summary.** Alternative: a permutation null for a question with no direct measurement.
**Result.** Supported on the short panel; not supported on the long one; the pre-registered
extension answered NO.

### D4. Level versus trend similarity

**Measures.** Whether matching precedents on the *direction* of macro movement beats matching on
the *level*.
**How the question arose.** A trend-aware variant looked better in the first grid.
**Method and data pool.** Sixteen cells with horizon fixed and only the similarity mode varied, on
two bases: features standardised over the whole panel (which lets 2010 be measured in units that
include 2026) and standardised on an expanding, live basis.
**Summary.** Direct comparison; the two bases isolate the look-ahead.
**Result.** The trend advantage *was* the look-ahead: on the live basis, level wins. The look-ahead
was declared and measured rather than argued away.

### D5. Recency weighting and the "no decay" claim

**Measures.** Whether removing recency decay improves the backtest.
**How the question arose.** A design note said no decay existed; the code had it all along (a
wrong prior found by reading the config file).
**Method and data pool.** A ladder of decay strengths on both engines; a paired comparison of the
no-decay engine against the incumbent over 836 rebalances, registered before computation.
**Summary.** Direct paired test.
**Result.** Not distinguishable (a Sharpe gap and a mean gap that disagreed in sign — a lesson that
a Sharpe difference can be produced by volatility alone). The claimed improvement was retired.

### D6. Model 4 — the long-only top five against the universe

**Measures.** Whether holding the estimator's top picks beats the universe.
**How the question arose.** The simplest tradeable form of the signal.
**Method and data pool.** Walk-forward on the long-history universe with a chronological split and a
survivorship-controlled re-run.
**Summary.** Direct, with the split as proof against period-dependence.
**Result.** Failed: skill concentrated after 2018 and not survivorship-robust.

### D7. The kernel family

**Measures.** Whether the similarity kernel adds ranking power beyond regime membership alone.
**How the question arose.** If regime alone did the work, the kernel would be decoration.
**Method and data pool.** Three kernels compared as a family against a family null (best of three
versus best of three nulls — the correction for trying several).
**Summary.** Alternative: a family-wise null for a selection question.
**Result.** Null as a family; regime-only weighting has essentially zero ranking power — the kernel
does the work, but not enough to pass.

### D8. Fed minutes as a contrarian signal (registered, forward only)

**Measures.** Whether oil moves against the minutes' implied direction over five sessions.
**How the question arose.** The one cell that survived C5 pointed this way; discovered by looking,
so it cannot be confirmed on the data that found it.
**Method and data pool.** A written overlay with its criterion fixed; scored only on forward rows;
nothing reported below thirty rows.
**Summary.** Direct, but deliberately forward-only.
**Result.** Waiting on rows.

### D9. FOMC → gold by regime (registered, forward only)

**Measures.** Whether gold's reaction to Fed decisions depends on the regime.
**How the question arose.** A conditional pattern seen in the backfill.
**Method and data pool.** Forward observations only, first on 17 September 2026; years to a verdict.
**Summary.** Direct, forward-only.

---

## E. The price models and the forward test

### E1. The three frozen models and the walk-forward backtest

**Measures.** Whether weekly rebalanced portfolios chosen by the regime engine beat a null.
**How the question arose.** The original "signal" product.
**Method and data pool.** Three model specifications frozen in a file on 17 August; 706 weekly
rebalances walk-forward (the model only ever sees the past); block-permutation nulls that keep
serial dependence; a chronological split; the survivorship-controlled universe; gross and net of
costs; a grid of 54 variants judged best-of-54 against best-of-54 nulls.
**Summary.** Direct, with every correction a referee would demand.
**Result.** The full-universe model survives marginally; the survivorship-controlled version does
not and was retired; the grid's best was not a finding once corrected for selection. The headline
figure fell after the calendar fix and the lower figure is kept.

### E2. The forward test

**Measures.** The same three models, live, on data that did not exist when they were frozen.
**How the question arose.** A backtest that cannot be run live is not a backtest of the product.
**Method and data pool.** Every trading evening since 19 August, one row per model appended to an
append-only ledger after the New York close is confirmed (never a partial bar); rows mature at their
horizon; nothing reported below thirty matured rows.
**Summary.** Direct, and the only evidence the plan allows a performance figure to come from.
**Result.** Too few rows to report. By design.

---

## F. The referees

### F1. The report scoreboard

**Measures.** Whether the daily report's own directional calls beat the market's drift.
**How the question arose.** The models had a scoreboard; the thing the product actually prints did
not.
**Method and data pool.** Registered before the code: hit-rate and asymmetry (the size of the moves
on correct calls over the size on incorrect ones) at a three-session primary horizon; only non-
overlapping rows enter; the null permutes each asset's own calls so that a report that merely follows
the drift cannot pass; seven acceptance tests on planted ledgers before real data.
**Summary.** Alternative statistic (a within-asset permutation null) answering a direct question.

### F2. The backfill, twice

**Measures.** The scoreboard's verdict on every historical document day.
**How the question arose.** The forward ledger will take months; history gives an immediate reading.
**Method and data pool.** The whole pipeline re-run as-of over 1,532 historical document days with
each day's precedent pool restricted to what was knowable then; scored by F1. Run once on the
original corpus and again after the Fed-statement texts were rebuilt (with the vote count the first
extraction had dropped) and re-read under identical conditions.
**Summary.** Direct application of F1.
**Result.** First run inconclusive, clearing its threshold by a hair; second run fail. A result that
one corrected source could flip was never robust; both are recorded side by side. The scoreboard also
showed that its non-overlap sampler is sensitive to its own starting phase at this sample size —
recorded, not fixed, because changing it after seeing the result is the thing the project forbids.

---

## G. Post-submission tests (September 2026)

### G1. Instrument robustness

**Measures.** Whether showing the S&P 500 index, the 10-year yield, gold futures, the DXY and WTI in
the app (instead of the five ETFs the model runs on) would change any verdict.
**How the question arose.** The app was redesigned to show the instruments a desk quotes; the
difference — settlement times, futures roll, bond maturity — had to be tested, not assumed.
**Method and data pool.** The five display instruments substituted for the ETFs under the ETFs'
column names, the backfill re-run and scored, four criteria fixed in advance (same verdict, row-level
agreement, hit-rate within tolerance, asymmetry within tolerance), with the flip rate on Fed days
measured separately.
**Summary.** Direct re-run under a substitution.
**Result.** Consistent on all four; the app may say verdicts are unchanged. Two priors wrong: flips
did not concentrate on Fed days (settlement-time differences are a daily effect), and the Treasury
pair was not the weakest.

### G2. The surprise — level 1 (2-year yield proxy)

**Measures.** Whether the *surprise* in a Fed decision — the decision minus what was priced —
explains what gold and bonds do over the next three sessions, beyond what the statement says.
**How the question arose.** The founder's observation: a hold when a hike was priced is a dovish
surprise; the text reads neutral, gold moves.
**Method and data pool.** 132 Fed statements; surprise measured as the 2-year Treasury yield's
change on the day, bucketed; the reader's stance and the asset's five-session run-up as controls;
per-asset regression with the surprise shuffled across statements as the null.
**Summary.** Direct regression; permutation as proof against chance.
**Result.** Inconclusive: gold passed, Treasuries did not — the reverse of the prior. The jobs
numbers the founder had in mind were *not* used here (they belong to a later, registered stage).

### G3. The surprise — level 3 (the published measure)

**Measures.** The same question with the proper surprise: the 30-minute move in short-rate futures
around each statement, as published by the San Francisco Fed (Bauer and Swanson), free.
**How the question arose.** The level-1 proxy measured the whole day's reaction, not the surprise.
**Method and data pool.** Same statements, controls and inference; the published series used
continuously; statements after the series ends (December 2023) keep the proxy and are counted.
**Summary.** Direct, with the measure the literature uses.
**Result.** Fail: the gold coefficient kept its economic size but could not be told from zero —
most meetings in 2011–2023 carried almost no surprise because rates were pinned. Recorded as a power
result, not an absence. Stage B (conditioning the precedent pool on the surprise) was not run.

### G4. T14 phase A — does the initial Fed reaction extend or reverse?

**Measures.** Whether the 30-minute reaction of the S&P 500 and the 10-year yield continues to the
close or gives back.
**How the question arose.** The founder's trading observation of intraday drift after the press
conference, and the evidence that direction is set within the session while size keeps unfolding.
**Method and data pool.** 292 scheduled announcements 1988–2023 from the same San Francisco Fed
file, which carries the 30-minute reactions; daily closes from Yahoo; rest-of-session proxied as the
day's move minus the 30-minute move (which leaves the pre-announcement drift inside it — stated as
the limit); regression with permutation; the next session reported beside it as the clean window.
**Summary.** Direct, low-powered by construction because free data has no 2 pm price.
**Result.** Null on both markets. Hints below the bar: a partial give-back in equities, a lean toward
continuation in the 10-year since 2006. The app's "rest of session" line may say what the statement
said, but no number.

### G5. The intraday collector (S5)

**Measures.** Nothing yet — it builds the data for the clean versions of G4 and of the expected-move
engine.
**How the question arose.** No free source has minute bars around past Fed days; a free source will
have them for every future one if they are saved now.
**Method and data pool.** Every evening, one-minute bars for eleven instruments for the last seven
days, one file per session, never rewritten. Started 29 September.
**Summary.** Data collection; a test only once the pool exists.

---

## H. What the app prints, and which entry it comes from

| on the page | measure | from |
|---|---|---|
| Market condition and its description | the regime label; description generated from the macro averages inside the cluster | A3 |
| Confidence | the mixture model's probability for that label | A3 |
| Documents today | count of documents from the five sources dated that session | B1 |
| Direction chips, specific / new / confident bars | the reader's fields for each document | B2 |
| Weak / clear signal, "+x% over the next 3 trading days" | the shrinkage estimate from the precedent pool | C3 |
| "No view" and its reason | the abstention rule firing (no document on that axis, too few comparable precedents, too vague) | C1–C3 |
| past situations matched / genuinely comparable / history weight | pool size, effective sample size, shrinkage weight | C2–C3 |
| documents and history disagree | the agreement flag — display only | B5 |
| Look-up: sessions of history, market conditions seen | the asset's own record and how many regimes it has traded through | A3, A6 |
| Live prices on desk instruments | Yahoo Finance, display only, tested for consistency | G1 |
| The record tab: forward rows, referee verdicts | the forward ledger and the two scoreboards | E2, F1–F2 |

---

## I. Reading the whole list

Three patterns run through every entry. First, the question is written down with its pass
criterion before the code that tests it, so a failure cannot be re-run into a success. Second,
wherever a question could not be measured directly, the stand-in statistic is a null that preserves
the data's structure — permutations that keep serial dependence, families judged against families,
chronological splits — rather than a textbook assumption. Third, the negatives are kept: of the
tests above, more rejected their hypothesis than confirmed it, and the product that ships is the one
that abstains and says why.
