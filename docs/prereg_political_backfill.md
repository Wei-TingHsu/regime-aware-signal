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
| 2026-10-28 | source expansion `97d9bf07dd2c_n5793` vs `48a6c4e879a1_n2617_h2` | gate (C2) PASS; calls 1,064 → 1,646; call-day coverage 39% → 35%; session coverage before 38.1%; after 61.0%; hit-rate on the 572 shared days 55.4% → 56.2% (+0.7 pts, 95% [-0.5, +2.0]); same sign on 100% of shared asset-days; 441 calls added (hit 56.2%; SPY 127, TLT 90, USO 82, GLD 81); 163 day(s) carrying documents outside the registered expansion set aside (on them: calls 31 → 210, hit-rate 54.8% → 50.5%, unregistered observation) → **PASS — C1 coverage, C2 gate and C3 hit-rate all met**. docs/source_compare_97d9bf07dd2c_n5793.md | #83: judged by the founder against the prior's clauses |

## 6. Amendments (after the run of 28 Oct 01:06–04:11 SGT)

| date | change | reason |
|---|---|---|
| 2026-10-28 | **The 165 unread `earnings_8k` documents — the over-cap 6-K submissions declined in CURRENT_STATE 17.2 and excluded by §4 above — were read.** `run_corpus.sh` reads every source; the runner's cost cap guarded only the routed political files; `measure_unread.py` printed the 165 and their price and the runner did not act on it. Billed for them: 35,262,700 input tokens (≈ 214k per document — 17.2's measured 127k/doc was itself low), about US$71 at the US$2/M the scripts assume; the political read 7.4M in / 0.65M out ≈ US$21, as measured beforehand; T-K3 US$1.02. The console carries the true figures. Consequences: (a) corpus hash `97d9bf07dd2c_n5793` carries two expansions — the registered political backlog and 165 truncated 6-Ks — so C3 is judged on the shared days that carry no new 8-K (`source_compare compare --exclude-dates`), and the 8-K days are reported as an unregistered observation; (b) the 165 reads are cached (reads are never deleted) and are now in `read_8k.csv` and therefore in live step 6 — whether they stay in the live corpus is the founder's decision, informed by (a); 17.2's reason for declining them stands (truncated reads: specificity 0.458 vs 0.696 for whole documents). | Claude's error in the runner, not a prior: the guard was on the wrong quantity. `overnight.sh` v2 measures the whole unread set, refuses any unread `earnings_8k` unless `READ_8K=1`, and reads the political sources directly instead of through `run_corpus.sh` |
| 2026-10-28 | **C2 was not evaluated at 04:11.** `gate_check` aborted: `read_political.csv` carries 1 row against 47 cached reads under the nightly `political` profile (a different role text; a source the report never reads). The 04:11 results row ("PASS") is void and is replaced by the re-run: the gate with `--allow-partial` (the shortfall — those 47 orphan reads — recorded in the gate's results file), then the comparison with the gate's verdict passed in (`--gate`). The nightly job is patched to route new Federal Register documents into the typed folders and to stop reading the `political` profile (`scripts_applied/patch_daily_route_political.py`), so no further orphans. Expect the gate's spread to be far thinner than August's 0.517: `political_other` now reads 0.34 pooled (the 2,675 new proclamations, notices and memoranda average ≈ 0.39 against the August set's 0.17) and the truncated 6-Ks pull `earnings_8k` from 0.687 to 0.67 — a spread near 0.33 against the 0.25 bar. | PASS = C1 ∧ C2 ∧ C3; a verdict written without C2 is not a verdict |
| 2026-10-28 | **Prior #83 against the run.** C1: 61.0% — clause met; the stated 50–60% range missed by one point. C2: `political_other` mean specificity rose to 0.34 pooled, the opposite of "falls below 0.17" — wrong. C3: +0.3 points on the 588 shared days (within ±1 ✓); the backfill's own primary cell FAIL ✓; the asset mix of the added calls is in the re-run's row. Two clauses wrong → counted if the founder agrees (tally 68 after #82). Descriptive clause (≥ 95% of the new documents at |direction| < 0.05 on every axis): `political_other` reads |dir| mean 0.01 / 0.00 / 0.00 — consistent, not tested. | the tally rule |
| 2026-10-28 | **T-K3's first run (04:11) is superseded.** 4 of 132 rubric replies failed to parse (20150128, 20220727, 20251029, 20260617), so the test ran on Warsh's 2 readable statements and the comparison sets shifted to the next statement read. `chair_style.py` v2: lenient JSON with one corrective retry and the raw reply kept on failure; acceptance/test refuse to run unless every member of the registered sets (folder listing) has a read; #79 written as "not yet judged" below n = 4. The acceptance result stands in substance — both past transitions separate (Bernanke→Yellen p 0.017 on guidance strength; Yellen→Powell p 0.005 on balance-sheet language and hedging density — the two dimensions #82 named) — and is re-run on the registered sets after the four re-reads; **#82 wrong** (Bernanke→Yellen separated). One rubric reading to check by eye: 20260429 dissents read 4 against a "– 1" vote line in the text. | a test must run on the sets its registration names |
