# Pre-registration — the Federal Register backlog read (TRACK §3.1)

*Registered 2026-10-28, before the read. TRACK §3.1 has carried this item since 7 September as "the cheapest real improvement
available to the product": the presidential documents re-fetched on 26 August at zero cost and never read.*

## 1. What is read

`data_provenance/docs/political/` holds every Federal Register presidential document since January 2011 (4,643 files on
28 Oct). 1,697 of them are the executive orders, presidential orders, determinations, proclamations, notices and memoranda the
corpus already read from the typed folders in August; the other **2,946** have never been read, and nothing in `political/`
has ever reached a report or the backfill, because step 6 reads only `read_political_order.csv` and `read_political_other.csv`.

`src/political_route.py` copies each unread file into the folder the report reads, by the type code in the fetcher's filename:
executive order, presidential order, determination → `political_order/`; proclamation, notice, memorandum → `political_other/`
(an unrecognised code goes to `political_other/` and is listed). Files already present are never touched; `political/` is
never moved or deleted. Counted on 28 Oct: about 2,670 of the 2,946 are proclamations, notices and memoranda — the class that
read at mean specificity 0.17 and near-zero direction in August.

The 47 documents the nightly job read between 27 Aug and 19 Oct under the `political` profile never entered a report either
(same reason). That profile's role text differs from the typed profiles', so its cached reads are **not** copied; those
documents are re-read under the typed profiles (about US$0.25) so the read condition stays one condition.

## 2. Read condition (unchanged)

Model `claude-sonnet-5`, prompt `v1-2026-08-23`, word cap 20,000, no `--with-prev` — exactly `run_corpus.sh`, which also holds the
launch lock and aborts on the first credit or auth error. The cost is **measured on disk first** (`political_route` counts the
words in the files themselves and applies the tokens-per-word ratio calibrated on the typed folders' observed token counts) and
the runner refuses to read above `CAP_USD` (default 40). Claude's estimate before measuring: US$15–25. A measured number above
the cap stops the run; nothing is priced by a corpus average (wrong priors #18 and #20).

## 3. Criteria, written before the read

| clause | statistic | criterion |
|---|---|---|
| **C1 coverage** | share of NYSE sessions since 2011-01-03 carrying at least one read document, from the read CSVs step 6 uses (`src/source_compare.py coverage`), measured before routing and after the read | PASS if the *after* value is ≥ 50% |
| **C2 gate** | the specificity gate re-run on the enlarged corpus (`src/gate_check.py`, 10,000 iterations, prereg_analog_event §11: lower bound of the 95% CI on the spread > 0.25; every expected-high source above every expected-low source) | PASS required; if it FAILS the new documents are reported separately and never pooled |
| **C3 source expansion** | the §8 rule of prereg_report_scoreboard: the backfill regenerated under the new corpus hash and scored by the same referee; on the days both backfills issued a call, the pooled hit-rate at the primary horizon (2) may not fall by more than 2 points (point estimate) and the 95% block-bootstrap lower bound must be above −5 (`src/source_compare.py compare`, block 2, 2,000 draws) | met / not met |

PASS on the item = C1 and C2 and C3. The baseline is `48a6c4e879a1_n2617_h2`; the new backfill carries its own hash and the old
folder, CSV and scoreboard stay. Forward reports already written keep their as-of state (the 15 Aug–19 Oct outage is recorded as
an outage, not regenerated); the write-once rule is untouched. `models.yaml` and the forward ledgers are untouched.

**Prior #83 (Claude, before the read).** C1: coverage rises from the measured 'before' value (about 30%) to 50–60% → PASS.
C2: the gate PASSES; `political_other`'s mean specificity falls further (below 0.17, more proclamations) and `political_order`'s
is unchanged within 0.03. C3: on shared days the hit-rate moves within ±1 point (tolerance met); the new calls land mostly on SPY;
the backfill's own primary cell stays FAIL (hit-rate at or below its null). In words: **coverage, not signal** — the reader sees
these documents clearly and they carry almost no direction under the five macro axes; the 2018 and 2025 Section 232 proclamations
read high specificity and low direction, as Finding B of 25 Aug predicts for a schema without a sector axis. Descriptive, not
tested: at least 95% of the newly read proclamations, notices and memoranda carry |direction| < 0.05 on every axis.

## 4. What this does not do

It does not change the nightly cap or the `--since 20260827` guard; it does not read the 163 deferred over-cap 6-Ks (declined,
17.2); it does not change the schema (v2 stays registered and unfunded). The 4,643 files in `political/` stay where they are so
the de-duplication is reproducible from the folder listing alone.

## 5. Results

| date | test | result | prior |
|---|---|---|---|
| 2026-10-28 | source expansion `97d9bf07dd2c_n5793` vs `48a6c4e879a1_n2617_h2` | calls 1,064 → 1,646; call-day coverage 39% → 35%; session coverage before 38.1%; after 61.0%; hit-rate on the 588 shared days 55.4% → 55.8% (+0.3 pts, 95% [-1.0, +1.6]); same sign on 100% of shared asset-days → **PASS — coverage up, hit-rate within tolerance**. docs/source_compare_97d9bf07dd2c_n5793.md | #83: judged by the founder against the prior's three clauses |
