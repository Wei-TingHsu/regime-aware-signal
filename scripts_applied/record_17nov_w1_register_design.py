"""record_17nov_w1_register_design.py -- (1) W1 result on record (TRACK 3.66, priors #154-#155, selling point SP-1 updated with the wire-clock evidence);
(2) the design test registered BEFORE running (TRACK 3.67, priors #156-#157). Numbers are those of the run pushed in commit 43027bd7. Idempotent."""
from pathlib import Path
T66 = """
### 3.66 W1 result: the SEC stamp is late, and the earlier clock is worth more (17 Nov 03:30)
`docs/wire_lag.md`, `docs/wire_rerun.md`, `data_provenance/ai_earnings/wire_times.csv` (5,029 dated items, column `source`).
**Collected.** PR Newswire company pages: Meta 76, Oracle 1,787, Broadcom 139, Microsoft 1,882 items. Own lists: Intel 576, AMD 490 releases with a time (from Feb 2018). Mirror (secondary source): Amazon 23 of 34 past results releases, CrowdStrike 21 of 31, SanDisk 7 of 7, Micron 17 of 34, Intel 11 of 35, **NVIDIA 0 of 36** (the guessed address pattern is wrong). Alphabet: no wire, not collected.
**Lag (SEC stamp minus wire time), 227 matched results releases of 10 companies:** wire first on 85%; median 4 minutes; 0-2 min: 34, 2-10 min: 120, 10-30 min: 32, over 30 min: 7, SEC first: 34. By company (median): AMD 2, CrowdStrike 2, Meta 4, Broadcom 5, SanDisk 6, Intel 8, Oracle 9, Amazon 10 minutes. **Two exceptions:** Microsoft (median -2: its wire item is a notice that the release is on its own site, posted after the SEC filing) and Micron (median -1). #154 right.
**Rerun, same releases, same cells, two clocks (before cost):**
| score | enter after | hold | from the wire time | from the SEC stamp |
|---|---|---|---|---|
| own stock | 1 min | 60 min | +86.3 bp, t +2.76, 55% of 217 | +36.4 bp, t +1.60, 55% of 216 |
| own stock | 5 min | 60 min | +37.4 bp, t +1.99, 54% of 216 | +16.0 bp, t +0.91, 52% of 216 |
| own stock | 15 min | 60 min | +18.8 bp, t +1.19, 53% of 216 | +18.3 bp, t +1.16, 54% of 217 |
| market | 5 min | 30 min | +51.2 bp, t +3.00, 59% of 199 | +24.0 bp, t +1.66, 52% of 199 |
#155 right. **Reading.** Entering from the wire time earned more than twice what the SEC clock earned on the same releases; by 15 minutes the two are equal -- the extra is in the first minutes. The share of winning trades is the same (about 55%): the gain comes from the SIZE of the moves caught, not from being right more often. A description on a subset (about two thirds of the 2018+ releases of ten companies), no new pass/fail; the F2 verdict (near miss) stands.
**Open:** NVIDIA and Alphabet have no wire time; Microsoft's and Micron's true first source is not the wire item found; the mirror lacks older releases.
"""
T67 = """
### 3.67 Design questions registered: overlapping signals, the size of the score, costs (17 Nov 03:45)
`src/ai_chain_design.py` -> `docs/ai_chain_design.md`. **Founder (17 Nov):** how were the costs calculated; how were the holds made; if two news items in the same hour point opposite ways for one stock, what position does the code hold; does the score represent each item's significance, and how is significance measured; is it a different approach from the macro engine's.
**What the first test did (stated plainly).** (i) Costs: NOT deducted. Every return on record is before cost. Costs entered only the pass rule (2 bp for the future, taken from v3e; 10 bp for a stock, an assumption) and a 'net of cost' line. No bid-ask quotes are on disk, so real after-hours costs are not measured. (ii) Holds: every signal is its own one-unit trade, entered and exited at fixed minutes; there is no book, no netting, no limit on overlapping positions. Two opposite signals on one stock in the same hour are counted as two separate trades (in a real account they would cancel). Only F1 combined signals (the average score of an afternoon's releases, equal weights). (iii) Significance: the trade used only the SIGN of the score. The readers do give a size (-1 to +1) and, for other events, a 'material' mark (0 to 1, judged against the latest results); these were used only as a check (large against small scores) and as a cut-off (0.2 / 0.3 / 0.5), never as position size. (iv) The macro engine's 'influence weights' are a different thing: weights estimated from history per document type, asset and regime, where these are the reader's judgement of one document.
**D0 (count):** how often signals on one stock within 60 minutes disagree -- own signals, other companies' releases naming it, and a reporter named by another reporter the same afternoon. **D1 (test):** the four cells already on record (F2 own-stock 1 min / 60; F2 market 5 / 30; F1 results-against-guidance 5 min to next 09:35; F4 own stock, material 0.2+, next session 60 min), split by the size of the score (0-0.3, 0.3-0.6, 0.6-0.9, 0.9-1), with 'only 0.5+', 'only 0.8+' and 'sized by the score'; one test per cell: rank correlation between the size of the score and the trade's return against shuffled sizes (5,000), one-sided; a cell counts at p < 0.0125 (0.05 / 4).
**Priors.** #156: no cell reaches p < 0.0125. #157: in F2 own-stock 1 min / 60, the 0.9-1 group has a higher average than the 0-0.3 group.
**Next, the founder's decision:** D2 netting (one net position per stock per hour from all signals, sized by score) as a registered rule; D3 measured costs (bid-ask quotes around the event minutes from Databento; price to be quoted first).
"""
SP = """
**Update 17 Nov 2026 — measured from the true release time (W1).** On 217 past results releases of ten companies where the news wire's own time could
be found, the same trade was entered from both clocks:
> "Entering 1 minute after the news wire earned +0.86% on average in the next hour. Entering 1 minute after the regulator's stamp earned +0.36% on the
> same releases. The regulator's stamp came a median 4 minutes after the wire. Fifteen minutes after the release the advantage is gone. The first
> minutes are where the money is, and the first minutes are what the product gives the user."

Evidence: `docs/wire_rerun.md`, `docs/wire_lag.md` (TRACK 3.66). Limits: about two thirds of the 2018+ releases of ten companies (no wire time for
NVIDIA or Alphabet); right on 55% of trades either way, so the gain comes from the size of the moves caught, not from being right more often; before
cost; a description, not a new pass.
"""
def add(path, marker, text, before=None):
    p = Path(path); s = p.read_text()
    if marker in s: print(f"  {path}: already recorded -- skipped"); return
    s = s.replace(before, text.rstrip("\n") + "\n\n" + before, 1) if before and before in s else s.rstrip("\n") + "\n" + text
    p.write_text(s); print(f"  {path}: recorded")
add("docs/TRACK.md", "### 3.66 W1 result", T66); add("docs/TRACK.md", "### 3.67 Design questions registered", T67)
add("docs/SELLING_POINTS.md", "Update 17 Nov 2026 — measured from the true release time", SP, before="**Why that matters to the customer.** The customer does not need to know where the release appears")
