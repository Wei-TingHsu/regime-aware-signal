# SESSION HANDOFF — 2026-08-23

*Append to `docs/PROJECT_STATE.md`, or upload alongside `briefing.md` to start a
new conversation. Written because the current chat is at its limit.*

---

## HOW TO START THE NEXT SESSION

```bash
cd ~/Projects/regime-aware-signal
for f in docs/*.md; do echo "===== $f ====="; cat "$f"; echo; done > ~/Downloads/briefing.md
```

Upload `briefing.md`. It contains everything below plus the full project state.

**Environment that must be set** (already in `~/.zshrc`):
`ANTHROPIC_API_KEY`, `SEC_CONTACT`.

---

## THE DEADLINE

**Report due to Dr. Lee 2026-08-24 (tomorrow).** It does not exist yet. Nothing
below is more important than writing it. model_1 matures ~08-26, model_3
mid-September — **no forward-test row matures before submission**, so the live
test contributes its design and timestamps, not numbers.

---

## WHERE THE PROJECT ACTUALLY IS

### Engine status

| engine | verdict |
|---|---|
| Macro analog | **measured**, Sharpe 0.25–0.51, permutation p 0.001/0.038 |
| Rotation | **closed, null** — 7 hypotheses, 4 instruments |
| Event drift (macro GDELT) | **null** at the registered criterion |
| Event drift (firm PEAD) | criterion not met; H=1 positive but survivorship-contaminated |
| FOMC → GLD | **−0.3% at h=2,3,5, p 0.028/0.0096/0.0104** — first cell to meet its criterion |
| Cross-firm spillover | propagation is **instant**: 5/7 peers on GAP, 0/7 INTRA, 0/7 NEXT |

### The single finding that ties the nulls together

`spillover_test.py` showed NVDA's earnings reprice TSM/ASML/MU/SOXX/SMH/XSD
**entirely in the overnight gap**, with nothing left after the open and nothing
the next session. **Every earlier test entered at t+2 — after the event had fully
propagated.** Those were not four independent nulls; they were one mechanism.

That is why `macro_event_test.py` changed the entry convention to close-of-event
-day, and why the FOMC→GLD result appeared at all.

### Look-ahead caught and fixed (keep in the report — it is the strongest
methodological demonstration in the project)
v1 of the spillover test used the announcer's *close* to predict peers'
*open-to-close* on the same session. Result: **6/7 peers "significant"**. With the
tradeable signal (announcer's gap, known at the open): **0/7**, four flipping
sign. The announcer's own INTRA went +2.319% (p=0.0002) → +0.012% (p=0.976).
`INTRA_LA` is retained in the output, labelled, as a measured demonstration of
what look-ahead is worth on real data.

---

## PROBLEM 3 — the LLM layer, the actual product

Steven's design, restated and confirmed 2026-08-23:

1. Match today's macro state to historical analogs, weighted by similarity **and
   recency**.
2. Read today's news **content** — not just its timestamp.
3. **Ask what this kind of news did to each asset IN THE MACRO-SIMILAR PAST**,
   weighted by similarity and recency. ← the core; never attempted
4. If no macro-matched precedent exists, fall back to the unconditional effect,
   labelled as weaker.
5. Weigh competing sources landing the same day into a net view.
6. Emit a decision report: which force dominates, which direction, what evidence.

### Built

- **λ recency kernel** — `analog_core._kw(dist, spec, age_years)`. Opt-in via
  `half_life_years`; `None` reproduces prior weights bit-identically, so the
  frozen live models are untouched. Pre-registered exponential, HL=4y, ladder
  {2,4,8,16,∞}. **Registered but the sweep has NOT been run.**
- **Document corpus + reader** — `data_provenance/docs/<source_type>/YYYYMMDD[_id].txt`
  drop folder; `doc_read.py` emits ONE common schema across all sources
  (direction per asset class, magnitude, horizon, **specificity**, novelty,
  confidence, evidence). Source-specific prompts, comparable output — which is
  what makes step 5 possible at all.

### Corpus counts

| source | docs | how |
|---|---|---|
| fomc_statement | 131 | fetched, **all read**, validated |
| fomc_minutes | 125 | fetched, not yet read |
| earnings_8k | 307 | fetched (8-K + 6-K), not yet read |
| political | **0** | see OPEN THREAD 17 |
| bank_research | 0 | manual drop |
| transcript | 0 | manual drop |

FOMC stance reader validated against known policy: 2015-12 +0.6 (first hike),
2020-03 −0.95 (emergency cuts), 2022-03 +0.6, 2022-06 +0.7. Range −0.95..+0.70,
|shift|>0.3 on 28 of 131.

---

## IMMEDIATE NEXT ACTIONS, in order

1. **Fix the Federal Register query** — the `fields[]` parameters were dropped in
   a rewrite, so the API returned summary records with no `raw_text_url`. 4,652
   documents were found; none had a text link to fetch. One-line patch; then
   `--types executive_order`.
2. **`python -m src.doc_read --all`** — read minutes + 8-K through the common
   schema. **Check that `specificity` SEPARATES sources**: decided policy and
   reported earnings high, rhetoric and opinion low. If everything scores alike
   the field is not discriminating and step 5 has nothing to weigh with.
3. **Run the λ sweep** on the registered ladder, all rungs reported.
4. **Build step 3** — the analog-conditioned event effect. Nothing else is the
   product.
5. **`python -m src.forward_log`** daily. Skipped days are lost permanently.

---

## THINGS THAT WILL BE FORGOTTEN IF NOT READ

- **OPEN THREAD 17**: political source built, not working, not done until
  `docs/political/` is non-empty.
- **λ characterisation**: with NO decay the weighted mean analog age is already
  0.40y and median ESS is 100/100. The engine averages the recent same-regime
  past with near-uniform weights rather than locating distinctive analogs. The
  lever for that is **σ, not λ**, and σ is frozen for the live test. Say this in
  the report — "analog" currently promises more than the mechanism delivers.
- **Three deferred decisions** (recorded in PROJECT_STATE): manual-collection
  sources cannot scale to a daily product; the political source is biased to
  decided policy so absent rhetoric is a coverage gap not evidence; foreign
  issuers (6-K) arrive with lower precision than domestic (8-K Item 2.02).
- **Nine wrong priors recorded.** The pattern across the first three: results are
  more *basis-carried* and less *phenomenon-carried* than expected. The fourth
  showed that correction can be over-applied.
- **The API key pasted into chat on 2026-08-23 must be revoked** if it has not
  been already.

---

## THE REPORT'S SPINE

Two clean nulls that survived every basis change; two positive-looking results
that collapsed the moment they were split by time; one measured engine with
declared caveats; one pre-registered unrun test with a power argument; a live
forward test with timestamps and no matured rows; and a single mechanism —
instant overnight propagation — that explains why the earlier entry convention
found nothing.

**The honesty is the finding.** Every null came from an instrument demonstrated
to detect a planted effect first.
