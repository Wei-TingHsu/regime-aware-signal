"""23 Oct evening: restore turning_points_swing (cut by the fidelity patch); PROJECT_MASTER §2.1 — the founder's ideas as a story in blocks.
Run from the repo root:  python scripts_applied/story_swing_setup.py ; python -m src.why_moved segmenter-test GLD | sed -n 5,8p ;
  python -m src.why_moved segmenter-test GLD | grep "zigzag\\|hl-oc\\|retrace f=38%, N=3, c=0.5" ; python -m src.why_moved run | grep -A3 "^## gold" | sed -n 3,4p | cut -c1-300"""
from pathlib import Path
import sys

wm = Path("src/why_moved.py"); s = wm.read_text()
if "def turning_points_swing(" in s: print("  swing rule: present")
else:
    swing = '''def turning_points_swing(r: pd.Series, k: int = 10):
    """Swing highs/lows: a peak is the highest close within k sessions either side (confirmed k sessions later); alternation enforced."""
    rr = r.fillna(0.0); px = np.exp(rr.cumsum().to_numpy()); n = len(px); cand = []
    for i in range(k, n - k):
        w = px[i - k:i + k + 1]
        if px[i] == w.max(): cand.append((i, "peak"))
        elif px[i] == w.min(): cand.append((i, "trough"))
    tps = []
    for i, kind in cand:
        if tps and tps[-1][1] == kind:
            j, _ = tps[-1]
            if (kind == "peak" and px[i] > px[j]) or (kind == "trough" and px[i] < px[j]): tps[-1] = (i, kind)
        else: tps.append((i, kind))
    trend = 0 if not tps else (-1 if tps[-1][1] == "peak" else 1)
    return tps, trend, (int(np.argmax(px[tps[-1][0]:])) + tps[-1][0] if trend > 0 else int(np.argmin(px[tps[-1][0]:])) + tps[-1][0]) if tps else 0, px


'''
    s = s.replace("SEGMENTERS = [(", swing + "SEGMENTERS = [(", 1); wm.write_text(s); print("  swing rule: restored")

m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "### 2.1 The founder's ideas, one block at a time" in s: print("  MASTER §2.1: already")
else:
    story = """
### 2.1 The founder's ideas, one block at a time — 22–23 October 2026

*Each block: the idea as it came, where it led next, the mathematical and statistical terms the method needed, and what was found.*

**Block 1 — "Why did gold fall? Name the reasons and weigh them."**
*Idea.* A fall from a peak has reasons — a war, rate-hike talk — and each reason should have a weight; multiply weight by the move and you have dollars
per reason; when the reason reverses, expect those dollars back. Take one reason as the prime factor and push everything else into the macro-state
line; then swap the prime factor and look again.
*Then.* The median path the engine first offered was dismissed as elementary; the method had to be a decomposition, not an average.
*Terms.* Return decomposition by linear regression (ordinary least squares); sensitivities (betas) with standard errors; a declared ordering by
Gram–Schmidt orthogonalisation (the prime factor keeps all it co-moves with, the next keeps what is left — the two orderings and the joint fit always
shown, their spread the attribution's uncertainty); out-of-sample R² on walk-forward blocks (T-A); sign stability of each beta across rolling windows (T-B).
*Findings.* T-A 0.177 (FAIL at 0.20; the swept 3-year/20-session cell 0.224 survives its null); the dollar, oil and the macro lines stable in sign, real
yields, hike talk, volatility and the war index not. Gold's 2026 fall: the named reasons ≈ $90 of $1,200; ≈ 90% outside the model — the proxies it lacks
are positioning and flows (registered next).

**Block 2 — "Every fixed number is a variable. Sweep them all."**
*Idea.* 20 sessions, 8%, 60 sessions, 15 points — each was chosen by convention; the diligent researcher tries 19, 21, 22 … and all the rest, on every test,
old ones included.
*Then.* A track beside TRACK — SPEC_GRID — listing every variable, every range, every family; the danger named: a thousand tries always produce a winner.
*Terms.* Specification curve; the best-of-sweep null (White's reality check, Hansen's SPA): run the same sweep on shuffled or time-shifted data, keep the
best cell each time, and judge the real best cell against that distribution; promotion to a forward test, never adoption in place.
*Findings.* The daily-model sweep: explanatory power rises with block length (negative at 2–3 sessions, 0.22 at 20 with a 3-year look-back), and the best
cell beats the best noise cell (p = 0.000). The history tables: no cell in 72 survived.

**Block 3 — "Analyse the purest, shortest window; the system should find its length."**
*Idea.* A six-month leg carries too much other news; the first plunge of five to seven sessions is where one reason acts alone — but the length must be
found, not fixed.
*Then.* First a fixed "impulse" (the stretch before the first pullback); then a forward-walking rule that lengthens the window and stops when the explained
share stalls; then its own variables — patience, minimum window, look-back — swept; the after-the-fact best window shown beside it as a ceiling.
*Terms.* Explained share = 1 − |residual| / |move|; a causal stopping rule with patience (how many sessions without a new best before stopping);
in-sample ceiling vs usable rule; shifted-series null for a rule that picks the best of several windows.
*Findings.* Fixed impulse FAIL (17% vs 63% for the full leg). The forward-walking rule PASS: 53% vs 31%, in 83% of legs, and 48 points above what it scores
on noise. Patience 20–30 and a one-year look-back lift it to 64–71%; the best cell survives the sweep's null. Gold's current leg: 61% explained over its
first 22 sessions against 12% for noise.

**Block 4 — "Is the unexplained part the crowd — and therefore our alpha?"**
*Idea.* If reasons explain 80% and nothing explains the rest, the rest is emotion, trend-followers, institutions valuing differently; measure it and lean on it.
*Then.* Three conditions written before any test: the label is not the test (what the model has no series for also lands in the residual); predictability,
not cause, is what pays; it must beat the price trend itself. The literature's name for it: residual momentum.
*Terms.* Residual from a rolling fit; signal = cumulative residual over w sessions, forward return over h; rank information coefficient; sign hit-rate;
long-short Sharpe; continuation (slow information) vs reversal (price pressure unwinding) by the sign of the IC; best-of-grid null; plain momentum as the benchmark.
*Findings.* FAIL on gold, silver, oil, equities and Nvidia — no cell beyond noise; oil leaned to continuation, metals to reversal at 60 sessions, neither
better than the trend. Re-run once flows and positioning shrink the residual.

**Block 5 — "A reversal is a trend, not one bounce."**
*Idea.* The zigzag calls a turn on one counter-move of 9%; a turn should need the direction to persist — at least two sessions; use the gradient from the
last big turning point to today, and if its sign changes along the way a turn was missed; measure on the day's high and low, let open-to-close say whether
the day rose or fell.
*Then.* "Persist" first read as consecutive closes: it won the registered test (74% vs 68%) and the noise test, was promoted — and showed gold "rising since July"
with a 14% fall inside, because that fall had no five-day losing streak. Withdrawn within two hours; a second criterion written: fidelity — no leg may hide a
counter-move larger than the zigzag's own threshold, measured at the date of the move. Persistence re-read as "sessions since the extreme"; the gradient test
recognised as the drawdown from the leg's high; tolerance set relative to the leg (a retracement fraction) with a volatility floor, capped at the coarse
threshold so long trends cannot freeze it; extremes from highs and lows; open-to-close as the day's sign.
*Terms.* Zigzag segmentation; persistence; drawdown from the running extreme; retracement fraction (38%); volatility-scaled floor; fidelity (missed reversals);
confirmation lag; two-scale legs (coarse context, fine current); shifted-factor null for a rule chosen from a grid.
*Findings.* The founder's two-step — high/low extremes, open-to-close day sign, three such days, 38% retracement — explains 79% of gold's legs on 114 legs
against the zigzag's 68% on 54, 2 missed vs 3, lag 11; 79% real vs 11% on noise → promoted as the leg definition. Five open-to-close days in a row freezes
(34 legs, lag 55), as five closes did. A quarter-scale leg and a five-week leg give opposite readings of "typical" for the same fall — the scale shown must be named.

**Block 6 — "Choose the earnings issuers by what drives the economy, round by round."**
*Idea.* The GDP report says about 70% of the economy is AI-related consumption; pick issuers from whatever sector tops the list each quarter.
*Then.* Premise corrected — ~70% is personal consumption's share of the level; AI investment is a few percent of the level and a large share of growth — so
the rule ranks contributions to growth. The BEA table arrives via FRED (no BEA key needed).
*Terms.* NIPA table 1.1.2 contributions to percent change in real GDP; a fixed line-to-sector map; market-value ranking within chosen sectors; a registered cell
to test whether the pool's releases move the index at all.
*Findings.* 2026 Q2: Information Technology, Industrials, Health Care, Communication Services cover 70% of the positive contributions → a pool of 25 issuers
(the original nine, the ten largest weights, four per chosen sector). NEM and FCX dropped — miners follow the metal, they do not move it.

**Block 7 — "Does our engine receive lagged information? If so every test must be re-assessed."**
*Idea.* The founder's live quotes ran a session ahead of what the engine (and this assistant) quoted.
*Then.* An input latency audit, every input, every night; free sources before paid; the price panel's own refresh moved ahead of the registered forward row.
*Terms.* As-of alignment; publication lag; latency measured in sessions behind the last completed close; provisional fills.
*Findings.* Yahoo's long-history request lags one session at the nightly hour; its short-window request does not; FRED series publish a day late by design;
the oil columns had been stale for eight sessions. Backtests are unaffected where the backfill used the same as-of alignment — checked per flagged series.

**Block 8 — "A target price, not a median."**
*Idea.* Where does the trend go ultimately? The engine should name a level, daily, beside the day's wind direction.
*Then.* Stage 1 answered how far and how likely by regime (reach probabilities); its calibration failed (0 of 24 cells — the regime conditioning made the
probabilities worse); the honest level became the base rate of past legs at the scale shown, with the reason-conditioned target as the registered test still open.
*Terms.* Reach probability (touching ±X within h); walk-forward Brier skill against the unconditional probability; independent cases vs overlapping sessions.
*Findings.* Unconditional: a 32% chance of gold touching +10% within 60 sessions from 4,090; the regime's 58% uncalibrated. On the page: the typical size of past
legs of this kind, how far along this one is, and the explicit words "base rate, not a forecast" until a conditional cell passes.
"""
    anchor = "\n## 3. What the machine does today\n"
    assert anchor in s, "§3 anchor"; m.write_text(s.replace(anchor, story + anchor, 1)); print("  MASTER §2.1: the founder's ideas as a story in blocks")
print("done -- python -m src.why_moved segmenter-test GLD")
