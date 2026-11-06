"""amend_6nov_news.py -- TRACK 3.42 (N1 registered; the no-tertiary-sources rule; k decision pending the founder's word) and F2b registered in
prereg_regime_audit. Appended once.    python scripts_applied/amend_6nov_news.py"""
import sys
from pathlib import Path
TRACK = """
### 3.42 N1 — news-attributed large moves and the releases that follow (founder, 6 Nov)
Registered in `docs/prereg_news_events.md` before any run: every ≥ 4% close-to-close move in SOX, QQQ and the S&P since 1995; the same-day cause read by the LLM under a fixed schema from GDELT, the project's own corpus and primary releases (**standing rule from 6 Nov: no tertiary sources — Wikipedia and the like are never used**); every scheduled release in the next five sessions read for its *composition* and scored for whether it contradicts the cause; reversal tables under the H-table standard; a walk-forward learner against the plain "buy after a −4% day" rule; the annual OEWS AI-occupation series as the slow check (the monthly jobs report has no occupation detail). Priors #117–#121. Cap US$25. Module `src/news_events.py` next, built against `gdelt_ingest`.
Regime count: R6b on the honest method leaves four competitive (Fed-day p 0.008) with six ahead only on the factor spread; the proposal on the table is a FIXED k = 4 for the product and, optionally, a second fixed six-state fit as the attribution lens — never a k that changes with time. Awaiting the founder's word.
"""
F2B = """| 2026-11-06 | F2b registered (before running) | lead time of the abnormal-day signal: for each live slow-regime change, the share of calm-type days in rolling 20-session windows from −120 to +20 sessions; the first window in which the share falls below its unconditional 10th percentile = the lead. Prior **#122:** median lead 10–30 sessions before the live label change (which itself confirms ~6 sessions after hindsight), so the signal arrives inside the season's last month, not before it; the event-rate rise is driven by the big-move days that cause the level shift. | — |
"""
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.42 N1" in s: print("  TRACK: 3.42 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.42 appended")
p = Path("docs/prereg_regime_audit.md"); s = p.read_text()
if "F2b registered" in s: print("  prereg_regime_audit: F2b already present -- skipped")
else:
    anchor = "| 2026-11-06 | R6b k by usefulness (expanding refit"
    if anchor not in s: sys.exit("anchor missing -- run the earlier record snippet first")
    p.write_text(s.replace(anchor, F2B + anchor, 1)); print("  prereg_regime_audit: F2b registered")
