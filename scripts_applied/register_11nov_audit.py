"""register_11nov_audit.py -- TRACK 3.51: the horizon audit registered (docs/prereg_horizon_audit.md, priors #132-#135), the app naming rule and the
intraday data decision recorded. Idempotent.    python scripts_applied/register_11nov_audit.py"""
from pathlib import Path
TRACK = """
### 3.51 Horizon audit registered; app naming rule; intraday data route (11 Nov 16:45)
**Horizon audit** — `docs/prereg_horizon_audit.md`, `src/horizon_audit.py`: nine audits rebuild the events of every test marked "day 0 checked? no" and measure day −1, day 0, +1, +1…+2, +1…+3, +1…+5 against a time-shift null; label rule fixed beforehand (days after → QUANT candidate; day 0 on an information event → SUBJECTIVE grade B candidate; day 0 on a price-move event → CONTEXT; else NEITHER). Priors #132–#135. No cost.

**App naming rule (founder, 11 Nov; standing; redesign to be done AFTER the tests).** Every block on the page carries a proper dashboard title — the standard professional name of what it shows — not a conversational phrase: "Why it moved" becomes "Factor attribution", and the same logic is applied to every block name on the page. Where two blocks would end up with the same or a similar name, they are separated — placed in different corners / areas of the page — so a reader can tell which block to look at. The redesign must follow this rule and no other naming idea.

**Intraday data route (founder's decision).** Databento first (new accounts receive free credit); if the credit does not cover what the test needs, Alpha Vantage (monthly plan). TradingView is ruled out: its support page states it has no API that gives access to data. The fetcher asks Databento for the cost of each request BEFORE downloading. Until intraday prices are in, no SUBJECTIVE finding can be graded A.

| # | step | why it matters to the business | founder decides |
|---|---|---|---|
| 1 | Horizon audit — run, record, relabel TEST_BOOK Part B | applies both new rules to the past tests; decides how many nulls change category | nothing — run |
| 2 | v3e intraday — Databento fetcher (cost check first), then the registered test | the only route to SUBJECTIVE grade A | create the Databento account and API key |
| 3 | Test book parts 2–6 | a quant specialist can rebuild every test alone | — |
| 4 | Reader consistency (30 documents read twice) | reliability of the document score | yes / no (≈ US$0.50) |
| 5 | §3.46 items 3–9, then the main track | — | — |
| 6 | App redesign under the naming rule above | the page reads as a professional dashboard | after the tests |
"""
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.51 Horizon audit registered" in s: print("  TRACK: 3.51 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.51 appended (audit registered; app naming rule; data route)")
print("  docs/prereg_horizon_audit.md " + ("present" if Path("docs/prereg_horizon_audit.md").exists() else "MISSING -- unzip again"))
