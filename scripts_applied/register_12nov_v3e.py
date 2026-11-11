"""register_12nov_v3e.py -- TRACK 3.55: the intraday tests registered before running (docs/prereg_intraday_v3e.md, priors #136-#139). Idempotent."""
from pathlib import Path
TRACK = """
### 3.55 v3e intraday tests registered (12 Nov 00:10)
`docs/prereg_intraday_v3e.md`, `src/intraday_v3e.py`. **E1 Fed statement days** (from June 2010): release time dated by the 10-year note's largest 5-minute move among 12:30 / 14:00 / 14:15; (a) where in the day each asset's move sits; (b) the test — watch the note k minutes, enter gold / S&P / Nasdaq / the note in its direction, hold 15 / 30 / 60 minutes or to the close, against shuffled directions and against placebo days at 14:00; (c) signed by the statement's own score, incl. days after ≥ 4% semiconductor falls. **E2 the 08:30 releases:** does the first move continue or reverse, does the composition score tell the direction, and does price come round to the score when the first move disagreed. Verdict rule fixed: gold in E1(b) is the primary — GRADE A candidate only if family p < 0.05, different from placebo at p < 0.05, and above the 2 bp cost; eleven secondary families count only at p < 0.005. Priors #136–#139. No cost; the data is on disk.
"""
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.55 v3e intraday tests registered" in s: print("  TRACK: 3.55 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.55 appended (v3e registered, priors #136-#139)")
print("  docs/prereg_intraday_v3e.md " + ("present" if Path("docs/prereg_intraday_v3e.md").exists() else "MISSING -- unzip again"))
