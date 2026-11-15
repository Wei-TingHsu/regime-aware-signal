"""record_15nov_aichain.py -- the AI-chain news test on record: prereg results rows, TRACK 3.62, TEST_BOOK B9. All seven families recorded (none passes).
Numbers are those of the run pushed in docs/ai_chain_test.md / .json (commit fb78328f). Idempotent."""
from pathlib import Path
ROWS = """| 2026-11-15 | Scoring completed before the run | The two failed reads were retried and scored (US$0.07): 756 of 756 results releases, 1,854 of 1,854 events. Prices on disk for 13 of 14 companies (SK Hynix missing). Observations: F1 506 days, F2 384, F3 1,588 mentions, F4 277, F5 493 mentions, F6 360, F7 99. |
| 2026-11-15 | **The seven families (bar: family p < 0.0071)** | **None passes.** F1 results -> Nasdaq future: best = results against prior guidance, enter 5 min after the stamp, hold to the next 09:35: +16.7 bp, t +3.54, 61% of 294 days; family p 0.0925; four periods +13.9 / +13.0 / +28.2 / +12.0; nothing before the stamp (-1.7 bp, t -0.75). **F2 results -> own stock: best = market score, enter 5 min after, hold 30 min: +41.4 bp, t +3.72, 58% of 330; family p 0.0100 (misses the bar); without the ten largest moves +24.0; BEFORE the stamp +55.0 bp, t +2.89 -- the stock was already moving with the score before the SEC stamp, so the stamp is late against the news wire and the check 'nothing before the stamp' fails.** Own-stock score in F2: 1 min after, hold 60 min +64.9 bp (t +3.53, n 365); 5 min after +40.8; 15 min after +25.0 -- the drift shrinks the later the entry. Price-only rule at F2's best cell: +2.4 bp (t +0.23). F3 results -> affected companies: best = copy the reporter, 1 min after, hold 15 min: +6.0 bp, family p 0.2480. F4 events -> own stock: best = free-cash-flow outlook, material 0.2+, next regular session, hold 60 min: +22.6 bp, t +2.42, n 238; family p 0.3605. F5 events -> affected companies: family p 0.6280. F6 events -> Nasdaq future: best cell AGAINST the score (-8.7 bp); family p 0.4980. F7 foreign filers: -17.4 bp, family p 0.5650. |
| 2026-11-15 | Priors | #145 right, #146 right (does not pass; own-stock score positive in 13 of 15 windows), **#147 wrong** (F3 does not pass, but 'copy the reporter' beat the reader's direction in only 5 of 15 windows, not more than half), #148 right, #149 right, #150 right, #151 right, **#152 wrong** (the price-only rule earned +2.4 bp against the score rule's +41.4 bp). |
| 2026-11-15 | Reading | Type 2 (other events) shows no usable link in any family: NEITHER. Type 1 (results) shows two near misses, not signals: (i) the Nasdaq future held overnight after results that beat prior guidance (F1; clean before the stamp, positive in all four periods, family p 0.09); (ii) the company's own stock in the first hour after the stamp (F2; family p 0.010, but the move started before the stamp and the 10 bp cost is an assumption for after-hours trading). Both go to a forward log (FA-3, QC-3); neither is called a signal. |
"""
TRACK = """
### 3.62 AI-chain news test: result (15 Nov 19:20)
`docs/ai_chain_test.md`, `docs/ai_chain_test.json`, `docs/prereg_ai_chain.md` §7. **None of the seven families passes** (bar: family p < 0.0071 = 0.05 / 7).
| family | best cell | result | family p |
|---|---|---|---|
| F1 results -> Nasdaq future | results against prior guidance; enter 5 min after the stamp, hold to the next 09:35 | +16.7 bp, t +3.54, 61% of 294 days | 0.0925 |
| F2 results -> own stock | market score; enter 5 min after, hold 30 min | +41.4 bp, t +3.72, 58% of 330; before the stamp +55.0 bp (t +2.89) | 0.0100 |
| F3 results -> affected companies | copy the reporter; 1 min after, hold 15 min | +6.0 bp, t +2.33 | 0.2480 |
| F4 events -> own stock | free-cash-flow outlook, material 0.2+; next regular session, hold 60 min | +22.6 bp, t +2.42, n 238 | 0.3605 |
| F5 events -> affected companies | copy the reporter; next regular session to 16:00 | +22.3 bp, t +1.72 | 0.6280 |
| F6 events -> Nasdaq future | own-stock score, material 0.3+; 5 min after, hold 60 min | -8.7 bp (against the score) | 0.4980 |
| F7 foreign filers | own stock; next regular session to 16:00 | -17.4 bp (against the score) | 0.5650 |
**Reading.** Other company events (type 2): no usable link, NEITHER. Results releases (type 1): two near misses. F1 — the Nasdaq future held overnight after results that beat the company's prior guidance: clean before the stamp, positive in all four periods, but family p 0.09. F2 — the company's own stock in the first hour after the stamp: family p 0.010 (bar 0.0071), the drift shrinks the later the entry (own-stock score, hold 60 min: +64.9 bp entering after 1 min, +40.8 after 5, +25.0 after 15), and the stock was ALREADY moving with the score before the SEC stamp, which means the stamp is late against the news wire; the 10 bp stock cost is an assumption for after-hours trading. The reader's spill-over directions (who gains, who loses) did not pay: F3 and F5 null.
**Priors:** #145, #146, #148, #149, #150, #151 right; #147, #152 wrong. **Forward log (not signals):** FA-3 = F2's cell on each new results release; QC-3 = F1's cell. LLM spend for this test: US$41.39 (0.34 + 0.54 + 40.44 + 0.07). SK Hynix prices still to download.
"""
B9 = """### B9. AI-chain company news (15 Nov 2026) — results releases and other events of fourteen companies, scored by Claude

Registration and full tables: `docs/prereg_ai_chain.md`, `docs/ai_chain_test.md`; code `src/ai_earnings.py` (collection, two readers), `src/ai_chain_test.py` (TRACK §3.61–3.62).

| id | claim tested | result | category |
|---|---|---|---|
| F1 | results release score → Nasdaq-100 future (from 2010) | best: results against prior guidance, 5 min after the stamp to the next 09:35: +16.7 bp, 61% of 294 days; family p 0.0925 — does not pass | NEITHER as registered; near miss, forward log QC-3 |
| F2 | results release score → the company's own stock (from May 2018) | best: market score, 5 min after, hold 30 min: +41.4 bp, 58% of 330; family p 0.0100 — misses the 0.0071 bar; the stock was already moving with the score before the SEC stamp | NEITHER as registered; near miss, forward log FA-3 |
| F3 | results → the other companies the reader named as affected | family p 0.2480 — does not pass | NEITHER |
| F4 | other events (material) → own stock | family p 0.3605 — does not pass | NEITHER |
| F5 | other events → affected companies | family p 0.6280 — does not pass | NEITHER |
| F6 | other events → Nasdaq-100 future | best cell against the score; family p 0.4980 — does not pass | NEITHER |
| F7 | foreign filers (TSMC) → own stock at the next regular session | against the score; family p 0.5650 — does not pass | NEITHER |

"""
def add(path, marker, text, where=None):
    p = Path(path); s = p.read_text()
    if marker in s: print(f"  {path}: already recorded -- skipped"); return
    if where and where in s: s = s.replace(where, text + where, 1)
    else: s = s.rstrip("\n") + "\n" + text
    p.write_text(s); print(f"  {path}: recorded")
add("docs/prereg_ai_chain.md", "The seven families (bar: family p < 0.0071)", ROWS)
add("docs/TRACK.md", "### 3.62 AI-chain news test: result", TRACK)
add("docs/TEST_BOOK.md", "### B9. AI-chain company news", B9, where="---\n\n## Part C")
