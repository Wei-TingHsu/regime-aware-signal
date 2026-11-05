"""amend_28oct_pm.py -- 28 Oct afternoon: the founder's two standing rules (grid by default; every test re-run by sub-period) and the
T-K3 n = 3 result go into the record, appended, anchored, once.

  docs/prereg_factor_attribution.md   one row at the top of the Amendments table: the 23 Oct sweep rule becomes grid-by-default
  docs/TRACK.md                        a 28 Oct 16:30 paragraph under 3.37 (the audit widened to every test; the registration file; the modules)
                                       and a new item 3.39 (the sweep engine as the standing instrument)
Idempotent (marker strings). Run from the repo root:  python scripts_applied/amend_28oct_pm.py
"""
import sys
from pathlib import Path

FA_ROW = ("| 2026-10-28 | **Grid by default (founder).** The sweep rule of 23 Oct ran after a registered cell failed; from today every fixed number in every test "
          "is a grid axis from the first run, the whole surface is published, and the strongest cell is judged against the strongest cell the same search finds "
          "on time-shifted or block-permuted data (`src/sweep.py`: `p_family`, survivors above the null's 95th percentile). The registered cell's verdict stands "
          "as recorded; a survivor is promoted to a forward test by dated amendment. Era is an axis under the same null. Full statement and the per-test grids: "
          "`docs/prereg_subperiod_audit.md` §1. | the founder, 28 Oct: 'we are prioritising finding the relationship' — a wide search is fine when the null is as wide as the search |")

TRACK_PARA = """
28 Oct 16:30: founder — the sub-period audit covers **every** registered test, not five, and every test's fixed numbers become grid axes. Registered as `docs/prereg_subperiod_audit.md` (the two standing rules; all 52 rows classified: already era-aware / not applicable / group A backfill CSVs / group B series on disk / group C returns only / group D reader drift; priors #85–#92). Instrument: `src/sweep.py` (grid, best-of-sweep null, survivors; selftest PASS). Written and tested on synthetic data: `era_scoreboard.py` (group A, all rows from one CSV), `era_liquidity.py` (T-L6 with sequential breaks and the watershed dates; P1 by era; T-L5b as a 147-cell grid in both directions), `era_factors.py` (betas and T-A by era; the 2026 episode re-attributed with 2009–21 and 2022→ betas), `era_fomc.py` (T9b by era), `era_events.py` (oil shocks by era). Next adapters: T1 by era, T-H by era, target range, H-tables, COT state, T14. `prereg_silver_stocks.md` v2 carries the grid (lag windows ±3/6/12/26 weeks; horizons 5/7/10/13/15/20/30/60; rally thresholds 4–10%; event sizes 0.25–3 Moz; eras); CME's host refused the plain client (403), fetcher v2 tries browser headers and curl; the one third-party API is paid and ruled out. T-K3 at n = 3 on the registered sets: energy 3.39, exact p 0.042 — Warsh's three statements separate from Powell's last eight, on inflation-vs-labour emphasis (0.018) and hedging density (0.055), not balance-sheet language (0.41); #79 is judged Thursday at n = 4 as registered. Gate re-run with the orphan shortfall recorded: PASS (spread 0.326, CI [0.308, 0.344]); C3 on the 572 political-only shared days +0.7 points, 441 calls added at 56.2% across all five assets (#83's 'mostly SPY' wrong); the 165 declined 6-Ks produced 190 calls at 50.5% — chance, as 17.2 predicted; whether they stay in the live corpus is the founder's decision. Nightly routing patch v2 (loop-aware) ready.

### 3.39 The sweep engine as the standing instrument
`src/sweep.py` is the one place the best-of-sweep null lives; every new test registers its grid and its null generator against it, and every re-run of an old test goes through it. Selftest: a planted lag-10 relationship in a 21-cell grid found at p_family 0.000; pure noise's best cell (r +0.05, 'significant' alone) at p_family 0.67. ML forms (walk-forward learners on the grid variables) enter through the same null, registered per family after the grid run.
"""


def main():
    fa = Path("docs/prereg_factor_attribution.md")
    if not fa.exists():
        sys.exit("docs/prereg_factor_attribution.md missing")
    s = fa.read_text()
    if "**Grid by default (founder).**" in s:
        print("  prereg_factor_attribution: grid-by-default row already present -- skipped")
    else:
        anchor = "## Amendments\n| date | change | reason |\n|---|---|---|\n"
        if s.count(anchor) != 1:
            sys.exit("prereg_factor_attribution: the Amendments table header is not where expected -- nothing changed")
        fa.write_text(s.replace(anchor, anchor + FA_ROW + "\n", 1)); print("  prereg_factor_attribution: grid-by-default row added at the top of the Amendments table")
    t = Path("docs/TRACK.md"); s = t.read_text()
    if "### 3.39 The sweep engine" in s:
        print("  TRACK: 28 Oct 16:30 paragraph and 3.39 already present -- skipped")
    else:
        if "### 3.37" not in s:
            sys.exit("TRACK anchor '### 3.37' missing (run amend_28oct_night.py first) -- nothing changed")
        t.write_text(s.rstrip("\n") + "\n" + TRACK_PARA); print("  TRACK: paragraph and 3.39 appended")
    print("done -- review `git diff docs/`")


if __name__ == "__main__":
    main()
