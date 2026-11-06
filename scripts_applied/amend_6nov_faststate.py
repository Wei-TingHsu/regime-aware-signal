"""amend_6nov_faststate.py -- prereg_regime_audit.md: section 3b (fast-state discovery, R6b, priors) appended once; TRACK note.
    python scripts_applied/amend_6nov_faststate.py"""
import sys
from pathlib import Path
SEC = """
## 3b. Fast-state discovery and the honest k comparison (founder, 6 Nov evening: "a full discovery, not one pattern")

**R6b** (`src/regime_k.py compare`): k = 3…6 through the engine's own `regime_labels_expanding` (refit every 20 sessions, first 504 unlabelled,
canonical PC1 order, confirmed labels) — the same three jobs as R6, without the full-sample look-ahead. The count is chosen on this table by dated
amendment. **R2** (`regime_k lag`): one full-sample mixture (hindsight) vs the live expanding labels, matched by canonical label.

**Fast states** (`src/faststate.py`): the slow regimes classify LEVELS; the fast states classify the day's MOVES — standardised daily changes of the
eight dials and the five assets (13 inputs, trailing-504 standardisation) → PCA(3) → mixture k ∈ {3, 4, 5, 6, 8}, expanding refit, canonical order.
Tests per k: **F1** forward 5/10/20-session returns per state × asset × direction, best-of-search null (returns time-shifted); **F2** state frequency in
the 60 sessions before a slow-regime change vs elsewhere, change dates shifted at random; **F3** Fed-day reaction by fast state (interaction p);
**F4** the environment → favoured-asset map's stability (first vs second half of each state's days) against block-permuted labels.

**Priors (Claude, counted if wrong).** **#111 R6b:** on expanding labels k = 6 loses its full-sample lead — Fed-day p 0.02–0.10 for k = 5 and 6, no k
reaches asset-map stability p < 0.05; k = 4 is still last on the factor spread. **#112 R2:** median lag 20–40 sessions; live and hindsight labels agree on
70–85% of sessions. **#113 F1:** no survivor at any k — a day's move pattern does not forecast the next 5–20 sessions. **#114 F2:** no fast state is
over-represented before slow-regime changes beyond the null. **#115 F3:** the Fed-day interaction by fast state is inside the null at every k (the fast
state on the statement day is mostly the statement's own move). **#116 F4:** stability below +0.3 at every k, p > 0.1. In words: fast states will read as
"risk-on day / risk-off day / rates-up day / flat day" and will describe the day well and the next days not at all.
"""
TRACK = """
6 Nov 22:40: founder — the count must be chosen on understanding, not tidiness; and the discovery must be full (all move patterns), not one example. R6b (expanding-refit k comparison), R2 (lag) and the fast-state layer registered in prereg_regime_audit §3b with priors #111–#116; `src/regime_k.py`, `src/faststate.py`. Today's R3 on confirmed labels: gold's Fed-day reaction differs by regime (p 0.005; stimulus and high-rates regimes ~2.5× more reactive) — the first regime-conditioned result to clear its bar; R5: the k = 4 favoured-asset map does not repeat within regimes (stability +0.25, p 0.19); R6 (full-sample): four wins none of the three usefulness jobs, six wins two, three has the most stable asset map — decision deferred to R6b.
"""
p = Path("docs/prereg_regime_audit.md"); s = p.read_text()
if "## 3b. Fast-state discovery" in s: print("  prereg_regime_audit: 3b already present -- skipped")
else:
    anchor = "\n## 4. Results"
    if s.count(anchor) != 1: sys.exit("anchor not unique")
    p.write_text(s.replace(anchor, "\n" + SEC.rstrip("\n") + "\n" + anchor, 1)); print("  prereg_regime_audit: section 3b added")
t = Path("docs/TRACK.md"); s = t.read_text()
if "6 Nov 22:40: founder" in s: print("  TRACK: already present -- skipped")
else: t.write_text(s.rstrip("\n") + "\n" + TRACK); print("  TRACK: appended")
