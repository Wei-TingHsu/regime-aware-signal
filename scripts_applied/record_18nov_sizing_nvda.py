"""record_18nov_sizing_nvda.py -- (1) S and N results on record (TRACK 3.68 result; priors #158, #159, #160 right; #161 waits for the cost download);
(2) the first live results release (NVIDIA, 17 Nov): the live read FAILED, why, and the fix (TRACK 3.69). Numbers from commit 26ff5f1f and the
founder's listener output of 18 Nov. Idempotent."""
from pathlib import Path
T68 = """
**3.68 results, S and N (18 Nov; `docs/ai_chain_sizing.md`, `docs/ai_chain_netting.md`).**
**S, in sample (365 releases; description only):** M0 sign b +64.9 bp, per unit +64.9 (t +3.53); M1 linear b +121.3, per unit +93.5 (t +4.28); M2 power b +135.7, **g = 1.65**, per unit +104.7 (t +4.25); M3 step b +143.7, **h = 0.7**, per unit +143.7 (t +4.74, 163 traded). The shapes explain 3-7% of the squared returns: the score moves the average, most of each move is still noise.
**S, out of sample (2020-2026, 302 releases; each year's parameters fitted on earlier releases only):**
| shape | per unit of position | t | traded | parameter by year |
|---|---|---|---|---|
| M0 sign | +77.5 bp | +3.76 | 302 | - |
| M1 linear | +98.4 bp | +4.00 | 302 | - |
| M2 power | +105.6 bp | +3.78 | 302 | g 2.95, 2.50, 1.55, 1.05, 1.45, 1.80, 1.45 |
| M3 step | **+141.5 bp** | **+4.16** | 140 | h 0.8 in 2020, then 0.7 every year |
Sizing by the score beat equal sizing out of sample in every shape; the step shape (trade only scores of 0.7 or more) earned most per unit and its threshold was the same in six of seven years. #158 right (g above 1), #159 right.
**N (1,464 stock-afternoons):** per unit of capital -- each signal alone +17.1 bp (t +3.55); net of signs +19.5 (t +3.89); net of scores +38.1 (t +4.47). The stock itself reported (361): +45.6 / +56.4 / +82.8 (t +3.83). Only named by others (1,103): +6.7 / +7.4 / +11.5 (t +2.58 to +2.90). Two or more signals (160): -1.2 / +0.1 / +15.3 (t under 1). Signals pointing opposite ways (54): -8.9 / -16.4 / +4.5 (t under 1). #160 right.
**Reading.** The founder's idea holds on this data: the score should set the size. Netting itself changes little (collisions are rare, 54 afternoons, and earn nothing either way); what lifts 'net of scores' is that it sizes by the score. Being named by another company's release carries a small positive drift (+7 bp, t about 2.7), below any plausible cost. **Candidate rule from this:** trade a results release in its own stock only when the own-stock score is 0.7 or more in size. Caution, stated: the trade was chosen after F2's table was seen; the forward record decides. **C (costs) not yet run** -- the Databento key in the terminal was the placeholder text; #161 waits.
"""
T69 = """
### 3.69 First live results release: NVIDIA, 17 Nov 16:20 New York -- the live read failed; cause and fix (18 Nov)
**What happened.** The listener saw NVIDIA's 8-K (items 2.02, 9.01) through the SEC route at 16:22:13 New York, 83 seconds after the SEC stamp, and returned a read 6 seconds later -- with every score 0 and no revenue. NVIDIA's own newsroom carried the release 196 seconds AFTER the SEC route (for NVIDIA the SEC was the faster source), and was not scored because the first source already 'had a score'.
**Cause (Claude's code).** The SEC text fetch took only exhibit files whose names contain 'ex99', 'press' or 'release'. NVIDIA names its exhibits differently, so the reader was given the filing's cover page alone and correctly found no results in it. The listener then treated that empty read as a valid score, which blocked the second source. The AMD drill had gone through AMD's own feed, so the SEC text path was never exercised on a results release before the first live one.
**Fix.** (1) The SEC fetch now takes the three largest exhibit documents of the filing whatever their names. (2) A results read with no revenue and every score 0 is an EMPTY read: logged as not scored, and the next source is tried. (3) `python -m src.news_listener rescore --ticker NVDA` redoes the read from the filing. **Rule for the forward record, fixed before any NVIDIA price is looked at:** a rescored read is made from the text alone, so the rules that depend only on the release time (FA-3, QC-3) may use it, flagged 'rescored'; it is NOT a customer-view observation -- no user could have acted on it -- so CV-1 does not count it.
**Also seen live:** an NVIDIA newsroom item ('Board of Directors Establishes National Security and Export Control Oversight Committee') was scored as an event through the company's own feed (material 0.25, own stock -0.15, uncertainty +0.35), 16 s after it was seen -- the route added on 17 Nov works. Listener stability: 3,457 passes over 10 hours; sources silent only when the machine was offline.
"""
t = Path("docs/TRACK.md"); s = t.read_text()
for marker, text, msg in (("**3.68 results, S and N (18 Nov", T68, "3.68 results recorded (priors #158-#160 right)"), ("### 3.69 First live results release: NVIDIA", T69, "3.69 appended (NVIDIA live read failed; cause and fix)")):
    if marker in s: print(f"  TRACK: {msg.split(' ')[0]} already present -- skipped")
    else: s = s.rstrip("\n") + "\n" + text; print(f"  TRACK: {msg}")
t.write_text(s)
