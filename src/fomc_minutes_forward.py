"""
fomc_minutes contrarian -- FORWARD-ONLY test of a hypothesis found by looking.

Registered: docs/overlays/fomc_minutes_contrarian.md (2026-09-15).
Origin:     backfill 986e0d65b6df_n2616 (14 Sep 2026): calls with fomc_minutes as the
            dominant source hit 37.8% on 74 rows at h=3. Found by looking; not a finding.

What this script does, and does not do
  - reads processed/report_ledger.csv (the FORWARD ledger, write-once reports only);
  - keeps rows with dominant_source == "fomc_minutes", h == 3, kind == call, matured;
  - non-overlap rows only (every 3rd report date per asset, first fixed);
  - prints "too few to report" until MIN_ROWS non-overlap rows exist;
  - then: hit-rate vs the within-asset block-permutation null, 10,000 draws;
          criterion = hit-rate BELOW the null's 5th percentile (the calls are wrong more
          often than chance). Pass -> the rule "take the opposite side, 0.25 x dial" is
          registered as an overlay; fail -> hypothesis dropped.
  - it NEVER reads the backfill ledger. The rows that produced the observation cannot
    also test it.

Usage:  python -m src.fomc_minutes_forward
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src import report_scoreboard as rs   # noqa: E402

LEDGER = Path("processed/report_ledger.csv")
OUT = Path("docs/fomc_minutes_forward.md")
SOURCE = "fomc_minutes"
H = 3
MIN_ROWS = 30
N_PERM = 10_000
ALPHA = 0.05          # one-sided, BELOW the null


def main():
    print("=" * 72)
    print("fomc_minutes CONTRARIAN -- forward-only (docs/overlays/fomc_minutes_contrarian.md)")
    print("=" * 72)
    if not LEDGER.exists():
        rows = pd.DataFrame(columns=rs.LEDGER_COLS)
    else:
        rows = pd.read_csv(LEDGER, parse_dates=["date"])
    sub = rows[(rows.get("dominant_source") == SOURCE) & (rows.get("h") == H)
               & (rows.get("kind") == rs.CALL) & (rows.get("status") == "matured")] if len(rows) else rows
    sub = sub[np.isfinite(sub["ret_primary"].to_numpy(float))] if len(sub) else sub
    no = rs.nonoverlap(sub, H) if len(sub) else sub
    n_all, n_no = len(sub), len(no)
    lines = ["# fomc_minutes contrarian -- forward-only test", "",
             f"*Registered docs/overlays/fomc_minutes_contrarian.md. Forward ledger only; the backfill "
             f"rows that produced the 37.8% observation are excluded by construction. Minimum {MIN_ROWS} "
             f"non-overlap rows. Criterion: hit-rate below the within-asset null's 5th percentile.*", "",
             f"- matured forward calls with `{SOURCE}` dominant at h={H}: **{n_all}** (non-overlap **{n_no}**)"]
    if n_no < MIN_ROWS:
        verdict = f"too few to report ({n_no} of {MIN_ROWS} non-overlap rows)"
        lines += [f"- verdict: **{verdict}**", "",
                  "No figure is printed below the minimum. Rows accumulate only while nightly reads are "
                  "running (paused for credit as of 15 Sep 2026)."]
        print(f"  {verdict}")
    else:
        m = rs.metrics(no["call"], no["ret_primary"])
        nd = rs.null_distribution(no, "ret_primary", block=H, n_perm=N_PERM, seed=0)
        q05 = float(np.percentile(nd["hit"], 100 * ALPHA))
        p_low = float((nd["hit"] <= m["hit"]).mean())
        passed = m["hit"] < q05
        verdict = "PASS -- calls are wrong more often than chance; register the contrarian overlay" if passed \
            else "FAIL -- not below the null's 5th percentile; hypothesis dropped"
        lines += [f"- hit-rate {100*m['hit']:.1f}% on {m['n']} rows; null 5th percentile {100*q05:.1f}%; "
                  f"one-sided p (below) {p_low:.4f}; asymmetry {m['asym']:.3f}",
                  f"- verdict: **{verdict}**"]
        print(f"  hit {100*m['hit']:.1f}%  null q05 {100*q05:.1f}%  p {p_low:.4f}  -> {verdict}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n")
    print(f"  -> {OUT}")


if __name__ == "__main__":
    main()
