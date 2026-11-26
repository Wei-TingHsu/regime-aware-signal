"""record_26nov_cds4_result.py -- TRACK 3.136: the result of CDS-4 (priors #238-#240 scored); the CDS line closed for now. Idempotent."""
from pathlib import Path
t = Path("docs/TRACK.md"); s = t.read_text()
A = """

### 3.136 CDS-4: result -- does not pass; the CDS line as it stands (26 Nov 18:40)
**Result (commit 77857a4; `docs/cds_oracle.md`).** 561 sessions; 159 days with a given Oracle spread; 25 jumps of 5% or more (Sep 2025 to Nov 2026). Oracle's share: on the jump day -1.46% on average; the next session -1.56%; after the look-alike days (same move that day, no jump) -0.36%. **Difference -1.20 percentage points; chance 0.14 (521 copies; limit 0.05): does not pass.**
**Reading.** The sign and the size are what CDS-3 hinted (the share is weaker the session after a jump, and by more than a bad day alone explains), but 25 days cannot tell it from luck: about 1 time in 7 the slid copies show as much. The next session was down after 15 of the 25 jumps, and five large falls (-8.8%, -7.0%, -6.9%, -5.6%, -5.1%) carry most of the average. A hint kept alive, not a finding.
**Priors.** #238 (fewer than 30 jumps): RIGHT, 25. #239 (negative but does not pass): RIGHT in the verdict; the part 'most of the effect is a bad day following a bad day' is NOT what the numbers say -- the look-alike days explain -0.36 of the -1.56, the rest stays unexplained and unproven. #240 (the share below -1% on the jump day): RIGHT, -1.46%.
**The forward record is running** (`python -m src.cds_oracle forward`, in the daily block): 0 of 20 jumps so far. The jump of 24 Nov (317 -> 365, followed by -5.1% on 25 Nov) is before the start date of 27 Nov and is not counted -- it was seen before the record was registered.
**The CDS line after five tests (LI-1, CDS-1 to CDS-4).** (1) Semiconductor shares: no lead by the CDS in any situation the data allows. (2) Oracle's own share after a jump in Oracle's CDS: a hint, not passing, on forward record. (3) The level: every large AI spender's CDS rose strongly in 2025-2026. (4) Not testable with this data: other market conditions; the trades with a hidden size; when each trade became public. (5) Rights: own testing only (3.127). The files are collected daily; CDS-1 and CDS-3 can be run again when a second market condition has days.
**The daily block of 26 Nov 16:29 Taipei** printed 'no changes added to commit': nothing had changed since the run of 16:01 -- not an error.
**Next, in the founder's order:** the test 'debt news of the AI spenders -> shares', then 'turns are caused by news'.
"""
if "### 3.136 CDS-4: result" not in s: t.write_text(s.rstrip("\n") + A); print("  TRACK.md: 3.136 added")
else: print("  TRACK.md: 3.136 already there -- skipped")
