"""
Horizon amendment, 9 Oct 2026: primary horizon h* 3 -> 2 sessions (founder's drift hypothesis).
Run from the repo root with the venv active. Registers first, then patches, never reruns h*=3.

What changes          where                                   how
  estimator estimand  step6_report.py PRIMARY_H               3 -> 2 (pool cutoff, forward returns, report label follow)
  referee primary     src/report_scoreboard.py PRIMARY_H      3 -> 2; HORIZONS (2, 3, 5, 20) so h=3 stays reported beside
  surprise test       src/surprise_stageA.py H                3 -> 2 (re-run writes *_h2.md; h3 files kept)
  app                 app.py                                  'next 3 trading days' -> reads the report's own horizon
What does NOT change: models.yaml, the forward ledger (old rows keep 3-session maturity, marked), any file already written.
"""
from pathlib import Path
import re

def sub1(path, old, new, label):
    p = Path(path); s = p.read_text()
    if new in s: print(f"  {label}: already"); return
    if old not in s: print(f"  {label}: ANCHOR NOT FOUND"); return
    p.write_text(s.replace(old, new, 1)); print(f"  {label}: done")

# 1. registration amendments (before code)
AMEND = ("| 2026-10-09 | **Primary horizon h* = 3 → 2 sessions.** Founder's hypothesis: a document's drift is strongest on the "
         "session it lands, weaker the next, and by the third session new documents overwrite or extend it, so a 3-session outcome "
         "mixes the effect with its successor's. Horizon set becomes {2, 3, 5, 20} so h=3 stays reported beside h=2; the "
         "non-overlap sampler takes every 2nd report date; the permutation block is 2. Every result on file at h*=3 stands as "
         "written and is not rerun; the backfill is re-scored at h*=2 under a new tag and the two are shown side by side. "
         "Prior, stated: hit-rate similar or slightly higher at h=2 (less time for intervening news), non-overlap n larger "
         "(~1.5×), asymmetry unchanged within 0.1 | Founder's instruction; the estimand follows the drift evidence |\n")
for f in ("docs/prereg_report_scoreboard.md", "docs/prereg_surprise.md"):
    p = Path(f); s = p.read_text()
    if "h* = 3 → 2" not in s:
        # append to the amendments table (last table in file)
        s = s.rstrip("\n") + "\n" + AMEND; p.write_text(s); print(f"  {f}: amendment appended")
# the estimator's own registration carries the estimand
p = Path("docs/prereg_analog_event.md"); s = p.read_text()
if "h* = 3 → 2" not in s:
    s = s.rstrip("\n") + "\n\n**Amendment 2026-10-09.** The estimand's horizon is 2 sessions from this date (was 3). See prereg_report_scoreboard §11, 2026-10-09. Results dated before this stand at 3.\n"
    p.write_text(s); print("  prereg_analog_event: amendment appended")

# 2. code
sub1("step6_report.py", "NEGLIGIBLE, PRIMARY_H, CONF_WARN = 0.05, 3, 0.60", "NEGLIGIBLE, PRIMARY_H, CONF_WARN = 0.05, 2, 0.60   # h* 3 -> 2 on 2026-10-09 (amendment)", "step6 PRIMARY_H")
sub1("src/report_scoreboard.py", "HORIZONS = (3, 5, 20)\nPRIMARY_H = 3", "HORIZONS = (2, 3, 5, 20)   # 2 added 2026-10-09; 3 kept so the old primary stays reported\nPRIMARY_H = 2              # h* 3 -> 2 on 2026-10-09 (amendment)", "scoreboard PRIMARY_H")
sub1("src/surprise_stageA.py", "H, RUNUP, THRESH_BP, N_PERM = 3, 5, 2.0, 10_000", "H, RUNUP, THRESH_BP, N_PERM = 2, 5, 2.0, 10_000   # h 3 -> 2 on 2026-10-09", "surprise H")
# surprise outputs: write beside, not over
p = Path("src/surprise_stageA.py"); s = p.read_text()
if 'OUT = Path("docs/surprise_stageA.md")' in s and "_h2" not in s:
    s = s.replace('OUT = Path("docs/surprise_stageA.md")', 'OUT = Path("docs/surprise_stageA_h2.md")')
    s = s.replace('OUT = Path(f"docs/surprise_stageA_level{level}.md") if level == 3 else OUT', 'OUT = Path(f"docs/surprise_stageA_level{level}_h2.md") if level == 3 else OUT')
    p.write_text(s); print("  surprise outputs: *_h2.md")
# app: the horizon label reads the report's own value
sub1("app.py", 'f"{est[\'estimate\']:+.2%} over the next 3 trading days"', 'f"{est[\'estimate\']:+.2%} over the next {est.get(\'horizon\', 2)} trading days"', "app horizon label")
sub1("app.py", "next 3 sessions", "next sessions", "app text")
# forward ledger: new rows mature at 2; old rows keep 3 -- the ledger carries its horizon per row already if a column exists
p = Path("src/report_scoreboard.py"); s = p.read_text()
print("  scoreboard reads per-row horizon from the report:", "estimate_horizon" in s)
print("patch complete -- now: python -m src.report_scoreboard --selftest ; then the backfill rescore")
