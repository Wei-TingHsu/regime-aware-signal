"""amend_6nov_regime.py -- TRACK 3.41: the regime audit and the day-type layer, appended once.    python scripts_applied/amend_6nov_regime.py"""
from pathlib import Path
PARA = """
### 3.41 Regime audit and the day-type layer (founder, 6 Nov)
Registered in `docs/prereg_regime_audit.md` before any run. The engine classifies macro *levels* (eight FRED dials → 3 PCs → 4-state mixture, expanding refit every 20 sessions, confirmation at posterior 0.8 for 3 sessions), persists ~52 sessions, and was chosen for stability, not prediction; every test that conditioned on its labels has been null. R1 describes the four regimes (dial levels, asset returns inside each — they never had names); R2 measures the live labeller's confirmation lag against hindsight labels; R3 asks whether the labels sharpen the Fed-day reaction, the factor model or the report's calls; R4 refits k = 3…8 at every year-end to see whether four was ever not the winner (a switch is a founder decision — it relabels history). The founder's same-day pattern (2-yr down, 10-yr up, gold up) is a pattern of *moves*, invisible to a level classifier at any k; `src/daytype.py` types every session by five same-day signs (32 patterns) and tests Y1 counts, Y2 clustering before regime changes, Y3 forward returns under the family null, Y4 the report's calls by type. Priors #107a–d, #108a–d. Use `pip install scikit-learn` once for R4.
"""
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.41 Regime audit" in s: print("  TRACK: 3.41 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + PARA); print("  TRACK: 3.41 appended")
