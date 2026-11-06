"""record_6nov_pm.py -- 6 Nov afternoon rows into prereg_subperiod_audit.md section 4 (factor eras on the full span; T-H by era) and a
compendium update (two lines), appended once.    python scripts_applied/record_6nov_pm.py
"""
import sys
from pathlib import Path

ROWS = """| 2026-11-06 | B4 re-run — factor eras on the full span (Bitcoin dropped; 11 factors, 2006–26) | in-sample R²: all 0.176; 2006–08 0.324, 2009–14 0.183, 2015–19 0.327, 2020–21 0.253, 2022–26 0.213. T-A by era × window: best 504 × 2015–19 median OOS R² 0.339 vs q95 −0.020, p_family 0.000 (survives). The 2026 fall: pre-episode betas 4%, **2009–21 betas 29%**, 2022→ 13%, all 20% — the old sensitivities explain more than the recent ones; most of the fall is outside the named reasons in every era. A first pass that dropped every factor starting after 1 Jan 2006 also removed the dollar and the macro lines (they start 4 Jan 2006) and is superseded. docs/era_factors_GLD_full.md | **#89** re-judged on the full span: 2015–19 is the best-explained era (not the worst) — wrong; '< 0.3 under 2022→' right; '< 0.2 under 2009–21' wrong |
| 2026-11-06 | B8 — T-H residual momentum by era | 5 × 5 × 6 cells: best w 20 / h 40 / 2009–14, \\|rank IC\\| 0.257 vs best-of-sweep q95 0.504, **p_family 0.930 → null in every era**. The 23 Oct FAIL ×5 stands; residual momentum is closed. docs/era_resid_GLD.md | no prior registered (B8 was 'next'); recorded as measured |
"""

COMP = """
## 6. Added 6 Nov afternoon

- Factor eras on the full 2006–26 span (Bitcoin dropped): the factors explain 18% of gold's daily moves overall, 32% in 2006–08 and 2015–19, 18% in 2009–14; the 2026 fall is explained 29% by 2009–21 sensitivities and 13% by 2022→ ones — **discretionary input (attribution)**, unchanged.
- Residual momentum by era: null in every era (p_family 0.93) — **neither**; closed.
- The oil → rates → gold chain with tradeable timing (D5c): null (p_family 0.905) — **neither**; closed.
"""


def main():
    p = Path("docs/prereg_subperiod_audit.md"); s = p.read_text()
    if "B4 re-run — factor eras on the full span" in s: print("  prereg_subperiod_audit: rows already present -- skipped")
    else:
        anchor = "## 4. Results\n\n| date | item | result | prior |\n|---|---|---|---|\n"
        if s.count(anchor) != 1: sys.exit("results header not where expected -- nothing changed")
        p.write_text(s.replace(anchor, anchor + ROWS, 1)); print("  prereg_subperiod_audit: two rows added")
    c = Path("docs/RESULTS_COMPENDIUM.md")
    if not c.exists(): sys.exit("RESULTS_COMPENDIUM.md missing")
    s = c.read_text()
    if "## 6. Added 6 Nov afternoon" in s: print("  compendium: section 6 already present -- skipped")
    else: c.write_text(s.rstrip("\n") + "\n" + COMP); print("  compendium: section 6 appended")
    print("done")


if __name__ == "__main__":
    main()
