"""TRACK §3.16: engine-side asymmetry levers, registered as tests; §3.17: trading-side methods recorded for the manual."""
from pathlib import Path
p = Path("docs/TRACK.md"); s = p.read_text()
if "3.16" not in s:
    k = s.find("## 4. Potential upgrades")
    s = s[:k] + '''### 3.16 Asymmetry — five engine-side levers, each a registered test on the h=2 backfill (9 Oct)

Asymmetry (mean |move| when right ÷ when wrong) is 1.008 at h=2. The trading-side ways to raise it (exit rules, sizing by
expected move, calling only on big days) are the user's, recorded in §3.17. These five change *which calls the engine
makes*. Each runs beside the incumbent estimator on `48a6c4e879a1_n2617_h2`, scored by the same referee; criterion fixed
now: **asymmetry up by ≥ 0.20 with the non-overlap hit-rate not below its null** — a filter that raises asymmetry by
abstaining on everything is trivial and fails the second clause.

| # | lever | mechanism | prior |
|---|---|---|---|
| E1 | ESS floor by expected move: abstain unless ESS ≥ 8 *and* the precedents' median |move| ≥ the asset's own median | calls land on days precedents say are big | the one most likely to pass |
| E2 | specificity gate at the source's median instead of the veto level | vague documents give small random moves | likely already captured by the veto; INCONCLUSIVE |
| E3 | precedent dispersion (τ²) as a second gate: tight pool with large mean → call; wide → abstain | tight pools are where right-side moves are large | plausible; may cut n below 30 |
| E4 | event-bin alignment: count a document toward a call only if its bin matched the move bin on its precedents' days | removes the "not the driver" calls, which read backwards | the one with the clearest mechanism (attribution_states 9 Oct) |
| E5 | scale the estimate by the earned influence weight for source × regime; zero where none earned | calls without measured influence become abstentions | waits on more earned cells; run last |

Order: E4, E1, E3, E2, E5. Registration file `docs/prereg_asymmetry_levers.md` before any code.

### 3.17 Trading-side asymmetry methods — recorded for the app's manual, not engine changes (9 Oct)

1. Call less, on bigger days (scheduled-event or strong-document days only). 2. Size by expected move (T2), not by
direction confidence. 3. Cut the wrong side early — a stop at a fixed fraction of typical move, no cap on the right side;
the engine scores close-to-close and has no exit rule; one is registered to be tested on the 30,640-row h=2 ledger
(stop at −0.5σ and −1.0σ, fixed, two candidates, both reported). These are on the app under "Reading this page".

''' + s[k:]
    p.write_text(s); print("TRACK 3.16-3.17 written")
