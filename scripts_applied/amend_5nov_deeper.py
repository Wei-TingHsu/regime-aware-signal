"""amend_5nov_deeper.py -- TRACK: the deeper-tests registration (3.40) and the forward log, appended once; also adds the nightly
forward-log line to daily_run.sh after step 5 (anchor verified, dry run by default, --write to apply).
    python scripts_applied/amend_5nov_deeper.py            # TRACK append + daily_run dry run
    python scripts_applied/amend_5nov_deeper.py --write    # also patch daily_run.sh (backup daily_run.sh.bak_20261105)
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path

TRACK_PARA = """
### 3.40 Deeper tests — from measured patterns to candidate signals (founder, 5 Nov)
Registered in `docs/prereg_deeper_signals.md` before any run: seven tests on one recipe (path statistics after costs; the best cell against the best-of-search null; survivors into a forward log; a learner only afterwards). D1 gold after an S&P drawdown (the 5 Nov survivor, widened with filters and both directions), D2 the liquidity link as an on/off meta-signal, D3 the gold–equity correlation regime as a sizing input, D4 Fed-day drift from the surprise and the statement rubric, D5 gold after oil shocks, D6 COT positioning extremes, D7 the report's calls selected by a walk-forward learner; D8 chain spillover and D9 vol-targeting registered, not yet coded. Priors #93–#99. First forward rule registered: **D1-5nov** (buy GLD when SPY's 20-session return crosses −6%, hold 15 sessions), logged nightly by `python -m src.deeper forward` into `processed/forward_signals.csv`, judged at n ≥ 30 — years, not weeks, at this event rate. `src/deeper.py`; each run writes `docs/deeper_<test>.md`.
"""

INSERT = 'python -m src.deeper forward || echo "  forward-signal log failed -- continuing"   # 5 Nov: registered rules (prereg_deeper_signals §4) logged daily\n'


def main():
    t = Path("docs/TRACK.md"); s = t.read_text()
    if "### 3.40 Deeper tests" in s:
        print("  TRACK: 3.40 already present -- skipped")
    else:
        t.write_text(s.rstrip("\n") + "\n" + TRACK_PARA); print("  TRACK: 3.40 appended")
    P = Path("daily_run.sh"); s = P.read_text()
    if "src.deeper forward" in s:
        print("  daily_run.sh: forward-log line already present -- skipped"); return
    m = list(re.finditer(r'^step\s+"6/7.*$', s, re.M))
    print(f"  daily_run.sh anchor (step 6/7 line): {len(m)} match(es)")
    if len(m) != 1:
        sys.exit("anchor not unique -- daily_run.sh unchanged")
    if "--write" not in sys.argv:
        print("  dry run: add --write to insert the forward-log line before step 6/7"); return
    bak = P.with_name("daily_run.sh.bak_20261105"); shutil.copy2(P, bak)
    s2 = s[:m[0].start()] + INSERT + s[m[0].start():]; P.write_text(s2)
    r = subprocess.run(["zsh", "-n", str(P)], capture_output=True, text=True)
    if r.returncode != 0:
        shutil.copy2(bak, P); sys.exit(f"zsh -n FAILED, reverted: {r.stderr}")
    print(f"  applied; backup {bak.name}")


if __name__ == "__main__":
    main()
