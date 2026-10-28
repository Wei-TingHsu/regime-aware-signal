"""amend_28oct_night.py -- the record of what the 28 Oct overnight run did against its registration, written once, anchored.

Appends (never rewrites):
  docs/prereg_political_backfill.md   a section "## 6. Amendments (after the run)" with three dated rows
  docs/TRACK.md                        a 28 Oct 15:30 status paragraph under 3.35 and three new items 3.36-3.38
Idempotent: a marker string guards each append.  Run from the repo root:
    python scripts_applied/amend_28oct_night.py
"""
import sys
from pathlib import Path

PREREG_SECTION = """
## 6. Amendments (after the run of 28 Oct 01:06–04:11 SGT)

| date | change | reason |
|---|---|---|
| 2026-10-28 | **The 165 unread `earnings_8k` documents — the over-cap 6-K submissions declined in CURRENT_STATE 17.2 and excluded by §4 above — were read.** `run_corpus.sh` reads every source; the runner's cost cap guarded only the routed political files; `measure_unread.py` printed the 165 and their price and the runner did not act on it. Billed for them: 35,262,700 input tokens (≈ 214k per document — 17.2's measured 127k/doc was itself low), about US$71 at the US$2/M the scripts assume; the political read 7.4M in / 0.65M out ≈ US$21, as measured beforehand; T-K3 US$1.02. The console carries the true figures. Consequences: (a) corpus hash `97d9bf07dd2c_n5793` carries two expansions — the registered political backlog and 165 truncated 6-Ks — so C3 is judged on the shared days that carry no new 8-K (`source_compare compare --exclude-dates`), and the 8-K days are reported as an unregistered observation; (b) the 165 reads are cached (reads are never deleted) and are now in `read_8k.csv` and therefore in live step 6 — whether they stay in the live corpus is the founder's decision, informed by (a); 17.2's reason for declining them stands (truncated reads: specificity 0.458 vs 0.696 for whole documents). | Claude's error in the runner, not a prior: the guard was on the wrong quantity. `overnight.sh` v2 measures the whole unread set, refuses any unread `earnings_8k` unless `READ_8K=1`, and reads the political sources directly instead of through `run_corpus.sh` |
| 2026-10-28 | **C2 was not evaluated at 04:11.** `gate_check` aborted: `read_political.csv` carries 1 row against 47 cached reads under the nightly `political` profile (a different role text; a source the report never reads). The 04:11 results row ("PASS") is void and is replaced by the re-run: the gate with `--allow-partial` (the shortfall — those 47 orphan reads — recorded in the gate's results file), then the comparison with the gate's verdict passed in (`--gate`). The nightly job is patched to route new Federal Register documents into the typed folders and to stop reading the `political` profile (`scripts_applied/patch_daily_route_political.py`), so no further orphans. Expect the gate's spread to be far thinner than August's 0.517: `political_other` now reads 0.34 pooled (the 2,675 new proclamations, notices and memoranda average ≈ 0.39 against the August set's 0.17) and the truncated 6-Ks pull `earnings_8k` from 0.687 to 0.67 — a spread near 0.33 against the 0.25 bar. | PASS = C1 ∧ C2 ∧ C3; a verdict written without C2 is not a verdict |
| 2026-10-28 | **Prior #83 against the run.** C1: 61.0% — clause met; the stated 50–60% range missed by one point. C2: `political_other` mean specificity rose to 0.34 pooled, the opposite of "falls below 0.17" — wrong. C3: +0.3 points on the 588 shared days (within ±1 ✓); the backfill's own primary cell FAIL ✓; the asset mix of the added calls is in the re-run's row. Two clauses wrong → counted if the founder agrees (tally 68 after #82). Descriptive clause (≥ 95% of the new documents at |direction| < 0.05 on every axis): `political_other` reads |dir| mean 0.01 / 0.00 / 0.00 — consistent, not tested. | the tally rule |
| 2026-10-28 | **T-K3's first run (04:11) is superseded.** 4 of 132 rubric replies failed to parse (20150128, 20220727, 20251029, 20260617), so the test ran on Warsh's 2 readable statements and the comparison sets shifted to the next statement read. `chair_style.py` v2: lenient JSON with one corrective retry and the raw reply kept on failure; acceptance/test refuse to run unless every member of the registered sets (folder listing) has a read; #79 written as "not yet judged" below n = 4. The acceptance result stands in substance — both past transitions separate (Bernanke→Yellen p 0.017 on guidance strength; Yellen→Powell p 0.005 on balance-sheet language and hedging density — the two dimensions #82 named) — and is re-run on the registered sets after the four re-reads; **#82 wrong** (Bernanke→Yellen separated). One rubric reading to check by eye: 20260429 dissents read 4 against a "– 1" vote line in the text. | a test must run on the sets its registration names |
"""

TRACK_PARA = """
28 Oct 15:30: the overnight run (01:06–04:11) read the political backlog as registered (2,946 documents, ≈ US$21, coverage 38.1% → 61.0%) **and** the 165 declined over-cap 6-Ks (≈ US$71) — the runner's cap guarded the wrong quantity (Claude's error; amendment in `prereg_political_backfill.md` §6). The gate aborted on 47 orphan reads under the nightly `political` profile, so C2 is unevaluated and the 04:11 PASS row is void; re-run with `gate_check --allow-partial`, then `source_compare compare --exclude-dates <the 8-K days> --gate <verdict> --record`. T-K3 ran at n = 2 (four replies failed to parse, one of them Warsh's 17 Jun) — `chair_style.py` v2 re-reads the four and refuses to run off the registered sets; acceptance check: both past transitions separate (#82 wrong). Nightly routing patch: `scripts_applied/patch_daily_route_political.py`. Backfill `97d9bf07dd2c_n5793`: primary cell FAIL as before; on the shared days +0.3 points, same sign on 100% of shared asset-day calls.

### 3.36 T-S1 — silver warehouse stocks and price (founder, 28 Oct)
Registered as a draft in `docs/prereg_silver_stocks.md`: the deliverable (registered) silver at the COMEX depositories — the amount moved out of deliverable status or out of the vault, and how often — against silver's price trend, both directions, lags −12..+12 weeks; the H-table standard for the event form. Unit is the depository (JPMorgan's vault, not JPMorgan's book — the owner is not observable). Data: CME's daily depository report, forward collection from the first probe (`src/fetch_comex_stocks.py --probe`), history by hand-downloaded file; the first run needs ≥ 250 sessions. Prior #84 in the draft. $0.

### 3.37 Sub-period audit (founder, 28 Oct: "a pooled result can balance out a shift")
Standing rule C (S1–S3: both halves same sign, neither half > 3× the other) is a guard against one-era findings; it is not a search for a transition. Tests with time dependence built in: T-A/T-B (walk-forward), T-L1–L3 (rolling, one break, recent window), T-K (eras = chairs), Model 1/4 and the kernel family (median split), FOMC→GLD (split FAIL 4.62×), Step-3 cells (7 → 1 under the split), the A3 inverse rule (held-out = chronological). Pooled over the whole span, candidates for a registered sub-period re-run, in value order: T-L multi-break (T-L6, the direct test of the founder's watershed); P1 safe-haven inversion (rolling 2-year gap + break); factor sensitivities by era (2004–08, 09–14, 15–19, 20–21, 22–26: β, R², sign stability, and the 2026 episode attributed with pre- and post-2022 betas — the "habit vs driver" split); the report scoreboard's own hit-rate by era (the product's claim; $0 from the backfill CSVs); T1 vol-targeting CER by era; the window/leg rules' explained share by era (descriptive); T-H by era (FAIL pooled — a one-era pass needs a forward test); T-L5b and H-tables by era (counts under 30 — measured only). Each re-run is its own registration with the criterion fixed first and, for any one-era PASS, a forward test before it is a verdict.

### 3.38 Results compendium (founder, 28 Oct) — after 3.37
`docs/RESULTS_COMPENDIUM.md`: one row per tested claim — the statistics as recorded (p, hit-rate, asymmetry, Sharpe, n, horizon, split status), the assumptions, conditions and time frame of each test, and a usability tag: *quant signal* (passed its registered null and split, non-overlapping, costed), *discretionary input* (a measured conditional table or a robust null that changes a trader's prior without being a rule), or *neither*. Built from the register (PROJECT_MASTER §8 rows 1–52 and every prereg's results table), not re-run. $0.
"""


def main():
    p = Path("docs/prereg_political_backfill.md")
    if not p.exists():
        sys.exit("docs/prereg_political_backfill.md missing")
    s = p.read_text()
    if "## 6. Amendments (after the run" in s:
        print("  prereg_political_backfill: section 6 already present -- skipped")
    else:
        p.write_text(s.rstrip("\n") + "\n" + PREREG_SECTION); print("  prereg_political_backfill: section 6 appended (four rows)")
    t = Path("docs/TRACK.md"); s = t.read_text()
    if "### 3.36 T-S1" in s:
        print("  TRACK: 28 Oct 15:30 paragraph and 3.36-3.38 already present -- skipped")
    else:
        if "### 3.35" not in s:
            sys.exit("TRACK anchor '### 3.35' missing -- nothing changed")
        t.write_text(s.rstrip("\n") + "\n" + TRACK_PARA); print("  TRACK: status paragraph and items 3.36-3.38 appended")
    print("done -- review `git diff docs/`")


if __name__ == "__main__":
    main()
