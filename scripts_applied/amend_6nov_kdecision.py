"""amend_6nov_kdecision.py -- the founder's regime-count decision (6 Nov 23:02) and N1 stage-1 facts, recorded once.
    python scripts_applied/amend_6nov_kdecision.py"""
from pathlib import Path
import pandas as pd
DEC = """
### Amendment 2026-11-06 23:02 — regime count decided (founder)
**Fixed k = 4 for the product's labels, plus a second fixed six-state fit as the attribution lens.** The lens is the `k6` column of
`processed/regime_labels_by_k.parquet` (R6b: expanding refit every 20 sessions, first 504 unlabelled, canonical PC1 order, confirmed as the product
applies labels — no hindsight). k never changes with time; a change of k is only ever a dated amendment here. Grounds (R6b honest method): four
competitive on the Fed-day job (p 0.008), six ahead only on the factor-R² spread; three the most stable but least informative. The six-state
labels are used to *explain* (which sub-environment a relationship held in) and never to *trade*; the product's precedent pools stay on k = 4.
"""
TRACK = """
### 3.43 Regime count decided; N1 stage 1 on record (6 Nov, 23:02)
Founder's word: fixed k = 4 for the product, a second fixed six-state fit (`k6` in `processed/regime_labels_by_k.parquet`) as the attribution lens; k never drifts with time (amendment in `docs/prereg_regime_audit.md`).
N1 stage 1 (`src/news_events.py`, no LLM): {n_ev} index-events on {n_days} sessions with |close-to-close| ≥ 4% — SOX stood in by **SOXX** (the ETF, from 2001; ^SOX not in the panel), **QQQ absent** from the panel (no Nasdaq-100 events until it is added), S&P by SPY. Years: {years}. GDELT 1.0 daily files run ~7 MB per event day (40 fetched = 284.5 MB); the 2001–2012 days sit in monthly / yearly archives of hundreds of MB and are fetched only if the daily-era results earn it. Measured cost of the cause read on disk: ≈ US$0.29 per 40 digests (≈ US$3.50 for all), well inside the US$25 cap. Stage 2 is `src/news_events2.py` (read / releases / read_releases / tables / learn).
"""
ROW = "| 2026-11-06 | S0 events + fetch + digest + cost | {n_ev} index-events on {n_days} sessions (SOXX stand-in for SOX; QQQ not in panel; SPY for S&P); {n_dig} digests on disk; cost ≈ US$0.29 / 40 digests | — |\n"
ev = pd.read_csv("processed/news_events.csv"); n_ev, n_days = len(ev), ev["date"].nunique()
years = ", ".join(f"{y}: {g['date'].nunique()}" for y, g in ev.groupby("year") if g["date"].nunique() >= 10) + " (years with ≥ 10 days)"
n_dig = len(list(Path("data_provenance/gdelt_days/digest").glob("*.txt")))
p = Path("docs/prereg_regime_audit.md"); s = p.read_text()
if "regime count decided (founder)" in s: print("  prereg_regime_audit: decision already present -- skipped")
else: p.write_text(s.rstrip("\n") + "\n" + DEC); print("  prereg_regime_audit: decision amendment appended")
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.43 Regime count decided" in s: print("  TRACK: 3.43 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK.format(n_ev=n_ev, n_days=n_days, years=years)); print("  TRACK: 3.43 appended")
n = Path("docs/prereg_news_events.md"); s = n.read_text()
if "S0 events + fetch" in s: print("  prereg_news_events: S0 row already present -- skipped")
else: n.write_text(s.rstrip("\n") + "\n" + ROW.format(n_ev=n_ev, n_days=n_days, n_dig=n_dig)); print("  prereg_news_events: S0 row appended")
c = Path("docs/RESULTS_COMPENDIUM.md")
if c.exists():
    s = c.read_text()
    if "fixed k = 4 for the product" in s: print("  compendium: already present -- skipped")
    else: c.write_text(s.rstrip("\n") + "\n\n**Regime count (decided 2026-11-06):** fixed k = 4 for the product's labels; a second fixed six-state fit (`k6`, `processed/regime_labels_by_k.parquet`) as the attribution lens only. Neither is a predictor; both are conditioning variables for the relationships above.\n"); print("  compendium: decision line appended")
