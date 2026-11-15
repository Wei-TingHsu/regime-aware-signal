"""register_15nov_aichain.py -- TRACK 3.61: AI-chain news scored (two readers) and the test registered before running (docs/prereg_ai_chain.md, priors #145-#152). Idempotent."""
from pathlib import Path
TRACK = """
### 3.61 AI-chain news: both types scored; the test registered (15 Nov)
`docs/prereg_ai_chain.md`, `src/ai_earnings.py`, `src/ai_chain_test.py`, `docs/ai_chain_scores_summary.md`.
**Founder (15 Nov):** score two kinds of company news. Type 1, results releases: reported figures against the company's previous guidance, and the new guidance. Type 2, other events (for example a chief executive's sudden resignation): scored against the latest type 1 report — the change to future free cash flow, balance sheet and guidance, the uncertainty added, and the competitors, suppliers and customers affected.
**Collected (SEC filings only, exact acceptance times):** 756 results releases (662 US 8-K Item 2.02 + 94 TSMC quarterly 6-K) and 1,854 other events (1,698 event filings: officer / director changes 412, other events 392, disclosures 237, material agreements 165, new debt 80, and smaller groups; plus 156 TSMC monthly revenue reports).
**Scored:** 754 results (reader `ai-earn-v3-2026-11-15`, each release sees the guidance of the one before; facts found: revenue 99%, free cash flow 78%, next guidance 67%) and 1,854 events (reader `ai-event-v2-2026-11-15`, each against the latest results). 469 events are material 0.3 or more. LLM spend: US$0.34 sample + US$0.54 trial (both superseded: the trial showed the cash-flow tables sat beyond the text sent, and one answer was cut short) + US$40.44 full run.
**Registered before any price was joined:** seven families (results -> Nasdaq future, own stock, affected companies; events -> own stock, affected companies, Nasdaq future; foreign filers), 311 cells, family p by shuffled scores, bar 0.05 / 7 = 0.0071, costs 2 bp future / 10 bp stock (assumed). Priors #145–#152. No cost; the prices are on disk.
"""
t = Path("docs/TRACK.md"); s = t.read_text()
if "### 3.61 AI-chain news: both types scored" in s: print("  TRACK: 3.61 already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: 3.61 appended (AI-chain scored and registered, priors #145-#152)")
print("  docs/prereg_ai_chain.md " + ("present" if Path("docs/prereg_ai_chain.md").exists() else "MISSING -- unzip again"))
