# Roadmap v2.1 — twelve trees toward a daily signal a trader can use

*Written 2026-09-15; revised the same day twice — first for plain-language paragraphs, §0 criteria and overlay entry modes; then (v2.1) for **universe expansion**: §1b defines four universes, every tree that gains from breadth now runs Test A (existing data) and Test B (expanded) under one registration, and T12 adds a regime engine v2 built beside v1. Design priority is success, not reuse of the project's existing data. Supersedes `roadmap_signal_trees.md` (v1, five trees). Every tree is a
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
| 4 | **T2 Expected-move engine** | forecast A 65–80% → B 70–85%; strategy 35–50% | master's → PhD | $0 | 3–5 days | pooled panel with asset fixed effects on U-ETF30 |
| 5 | **T7 Distilled local reader** | engineering 70–85% | ML engineering | ~$0–50 | 1–2 weeks | makes B universes readable at $0 |
| 6 | **T11 Unprecedentedness index** (+ asset-turbulence component) | 50–60% → 55–65% | PhD | $0 | 3–4 days | three-component distance: macro, documents, cross-asset |
| 7 | **T9 Text path factor → bond drift** on U-Curve | 35–50% → 40–55% | PhD | $0 | 1 week | LLM path factor tested across the whole ladder and credit |
| 8 | **T10 Surprise/novelty** | short 40–55%; slow 30–45% (U-Liquid200) | PhD | $0 | 1–2 weeks | reader-measured novelty, regime-conditioned |
| 9 | **T4 Meta-labelling** | 30–45% → 35–50% with B's larger call set | top industrial | $0 | 1–2 weeks | learned confidence replaces tiers |
| 10 | **T3 Arbitrage tree + overlays** | systematic 15–30% → 20–35% with sector pairs; overlays valuable regardless | master's / PhD | $0 → $200–400 | days / months | your calls, scored |
| 11 | **T6 Affordable LLM drift** on U-Liquid200 | 15–30% | PhD / industrial | $0 with T7 | 2–3 weeks | cost-aware abstention |
| — | **T5 Coverage & vocabulary** | multiplier | — | $60 → $1,200 | weeks | plumbing |

The B numbers are higher for one reason only: more assets give a regime tilt, a beta tilt, or a
document effect more places to show up, and a pooled test more power. They are not higher
because breadth creates edge. Where a tree does not gain from breadth (T7) the number is unchanged.

Suggested order: T1(A) → T8(A) → T2(A) → T12 → T1(B), T8(B), T2(B) re-run on v2 regimes → T11 →
T7 → T9 → T10 → T4 → T3 (overlays from day 1 in parallel) → T6 → T5 when funded. The A tests
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
