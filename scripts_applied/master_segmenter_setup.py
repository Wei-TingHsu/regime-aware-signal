"""23 Oct: (1) PROJECT_MASTER brought up to date — §2 story 24 Sep → 23 Oct, §5 wrong priors to #67, §3/§7 addendum, change log, section numbering,
Appendix A marked superseded; (2) alternative turning-point rules (founder's persistence/gradient rule, swing highs/lows) in why_moved + T-I test;
(3) prereg T-I. Run from the repo root:  python scripts_applied/master_segmenter_setup.py ; python -m src.why_moved segmenter-test GLD | sed -n 1,22p"""
from pathlib import Path
import re, sys

# ---------------------------------------------------------------- 1. PROJECT_MASTER
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "### Post-submission · 22 Sep–23 Oct" in s: print("  MASTER §2: already")
else:
    story = """
### Post-submission · 22 Sep–23 Oct · The engine learns what it cannot see

- **24 Sep:** two more silent defects — the API key and the FOMC statements nobody had fetched; the statement corpus replaced, re-read, re-baselined (CURRENT_STATE §18.7–18.8).
- **29 Sep:** instrument robustness **CONSISTENT** (verdicts unchanged on desk instruments); surprise conditioning stage A **INCONCLUSIVE**, level 3 **FAIL**; T14 phase A — the initial FOMC reaction neither extends nor reverses by the close (§18.9–18.12).
- **7 Oct:** fourteen failed nights traced to a secrets file appended without a newline (§18.13). **7–8 Oct:** T1 exposure dial Test A — nothing enters the product; vol-targeting PASS on one of five (USO), regime tilt 0/5 (§18.14); wrong priors #29–#37 written in human terms (§18.15).
- **8 Oct:** T13 case A — coverage on big-move days measured, the oil → dollar → rates chain rule calibrated to the two wars (§18.16); the two-wars case study and the oil instrument amendment registered (TRACK 3.13–3.14).
- **9 Oct:** T16 prints as a source — first measured cut in the blind rate, first earned influence weight (payrolls → gold); primary horizon amended 3 → 2 and re-scored (§18.17–18.18); E4 event-bin alignment **FAIL**; twenty BLS releases transferred to disk behind the bot wall (§18.19).
- **10 Oct:** E1, E3, E2 asymmetry levers **FAIL**; the lever programme closed — asymmetry ≈ 1 is a property of the calls; priors #40–#43 wrong (§18.20–18.22).
- **11 Oct:** founder's review of the levers in plain words; the jobs report's World Cup disclosure; the event calendar registered with an admission rule; prompt v1 approved; A4 reader consistency **PASS 20/20** with three runner defects recorded; #44 (§18.23–18.24).
- **12 Oct:** the oil column — USO's drag, a chain rule partly fitted to the ETF, the founder's decision to read spot with a futures tail (§18.25); the edge analysis (§12) and the four moat items agreed.
- **13 Oct:** the 08:30 event-time reader built and scheduled; the oil amendment closed, T1's oil cell holds on spot; design scorecard 13/18 (§13); §18.26–18.27.
- **16 Oct:** after an oil shock — the path table (116 shocks since 1995; gold flat-to-up after plain shocks, lower after all five chain firings), the nearest-neighbour estimate **FAIL** on all six markets, a leverage number under the founder's 20%/5× limits, the tail (A3d, severe cases inside bear markets); the coin-flip check; §3.24 implied-vs-realised registered; USO inverse held-out **FAIL 47%**; #45–#48; the app Context block ordered (§18.28–18.30).
- **19 Oct:** history tables H0–H7 registered; H0 measured (gold +2.4%/month in regime 3, #49 wrong); H1, H4, H5 **FAIL** on every testable cell, H3 too few events (#51 wrong); the founder's horizon amendment (5 sessions, 10-point floor, per-table Bonferroni): no PASS in 72 cells. **The live document feed found dry** — zero documents on 29 of 30 report days — and repaired (nightly 8-K fetch, presidential documents routed); the Today tab rewritten in plain words (§18.31–18.32).
- **22 Oct:** the gold/silver/oil week outside the engine's sight; input latency audit registered and running (Yahoo a session late at the nightly hour; Stooq/short-window fallback); target-range Stage 1 **0 of 24 cells PASS** (#55 wrong); SPEC_GRID — the alternatives track — written; blind-spot fill plan; 8-K pool amended (§18.33–18.34).
- **23 Oct:** factor attribution built at the founder's direction — T-A **FAIL 0.177** (swept 3-year cell 0.224 survives its null), T-B dollar/oil/macro stable, real/hikes/VIX/war unstable (#58–#59 wrong); gold's 2026 fall ≈ 90% outside the standard factors; dynamic issuer pool from BEA growth contributions (25 issuers); "why it moved" daily engine — adaptive legs, impulse **FAIL** (#63), **causal window rule PASS** 53% vs 31% (#64 wrong) and **beats noise by 48 points**, patience/look-back sweep → 64–71%, promoted within the registered leg definition (#66 right); the founder's "crowd as alpha" question registered with three conditions and tested as residual momentum — **FAIL on five assets** (#67 wrong). Tally 56, register row 48 (§18.35–18.36).
"""
    anchor = "\n## 3. What the machine does today\n"
    assert anchor in s, "§3 anchor"; s = s.replace(anchor, story + anchor, 1); print("  MASTER §2: story extended to 23 Oct")

if "**24 Sep–23 Oct** (#29–#67" in s: print("  MASTER §5: already")
else:
    wp = """
**24 Sep–23 Oct** (#29–#67, tally 56 — each with its rule and trading reading in CURRENT_STATE §18.15 and the test's prereg file).
#29–#39 (14 Sep–9 Oct): the dead nightly reads · the surprise-conditioning and T14 candidates (#32–#33) · the exposure-dial and chain-rule
priors of 7–9 Oct. **#40–#43** the four asymmetry levers would lift asymmetry by +0.20 — none did. **#44** the July 2026 jobs calendar
expectation ("undetermined"; the text contradicted it). **#45** the oil-shock pool would be small (116). **#46** gold would fall after a plain oil
shock (flat-to-up; it fell only after the five chain firings). **#47** the shock-week legs would carry direction (A3b FAIL). **#48** the USO inverse
rule would hold out at 55–60% (47%). **#49** no regime's gold return would sit more than a point from all-history (+2.4% vs +0.7%). **#51** sixty to
eighty dollar shocks (six and three; the series starts 2006). **#55** regime-conditional reach probabilities would be about as good as
unconditional (worse, on 15 of 24 cells — a 100-session floor admitting under two independent cases). **#58** the factor model would explain
25–40% of gold's daily variance out of sample (17.7%). **#59** real yields and hike speculation would be stable in sign, oil not (the reverse).
**#63** the initial plunge would be the best-explained window (it was not: 17%). **#64** a forward-walking window rule would do no better than the
full leg (it did: 53% vs 31%, and 48 points above noise). **#67** the unexplained part would carry predictability in metals and single names (none
beyond noise on five assets). Right along the way: #50, #52–#54 (history tables fail), #65 (the rule beats noise), #66 (patience 20–30 wins).

"""
    anchor = "\n---\n\n## 6. The business\n"
    if anchor in s: s = s.replace(anchor, "\n" + wp + "---\n\n## 6. The business\n", 1); print("  MASTER §5: wrong priors to #67")
    else: print("  MASTER §5 anchor not found -- add by hand")

if "### 3.A What runs and what the page shows, as of 23 Oct 2026" in s: print("  MASTER §3 addendum: already")
else:
    add = """
### 3.A What runs and what the page shows, as of 23 Oct 2026

Nightly (weekdays ~15:10 SGT, `daily_run.sh`): prices refreshed with a forced pull, the missing session filled from a second source if Yahoo is
a session behind, macro and PCA rebuilt → the registered forward row (`--no-refresh`) → documents fetched (8-K/6-K for the dynamic issuer pool,
FOMC statements, presidential documents routed to the folders the report reads) → read under the 40-per-source cap → reports for completed
sessions whose prices exist → blind-spot monitor and chain alarm (spot oil, futures tail) → oil columns rebuilt, oil forward rows → input latency
audit → "why it moved" (legs, impulse, window rule, base-rate target, last-session reasons, for the five markets, silver, Nvidia, Meta).
The page: a plain-words track-record banner; "Documents with a direction" as a clickable count; per market the Context block — why it moved and
where this leg stands, today's condition's own return table, what history says after shocks and events with each table's verdict, the severe case,
what is not known — every sentence tagged measured / tested / hypothesis / running. Nothing is a forecast unless a PASS says so.
"""
    anchor = "\n## 4. Everything that has been tested — the complete register\n"
    assert anchor in s, "§4 anchor"; s = s.replace(anchor, add + anchor, 1); print("  MASTER §3.A: added")

# numbering: second §12/§13 and the sections after them
fixes = [("## 12. The standing rules", "## 14. The standing rules"), ("## 13. Backup and restore", "## 15. Backup and restore"),
         ("## 14. Glossary", "## 16. Glossary"), ("## 15. File map", "## 17. File map"), ("## 16. Change log of this master file", "## 18. Change log of this master file")]
if "## 18. Change log" in s: print("  MASTER numbering: already")
else:
    for a, b in fixes: s = s.replace(a, b, 1)
    print("  MASTER numbering: standing rules 14, backup 15, glossary 16, file map 17, change log 18 (edge 12 and scorecard 13 keep their cited numbers)")
if "superseded by the live docs/TRACK.md" in s: print("  Appendix A note: already")
else:
    s = s.replace("# APPENDIX A — TRACK.md (status board, as of 21 Sep 2026)", "# APPENDIX A — TRACK.md (status board, as of 21 Sep 2026 — superseded by the live docs/TRACK.md, §3.1–3.34 as of 23 Oct 2026; kept as the submission-time snapshot)", 1)
    print("  Appendix A: marked superseded")
if "| 2026-10-23 |" in s: print("  MASTER change log: already")
else:
    rows = """| 2026-10-07 | Fourteen failed nights (secrets file newline); T1 Test A: nothing enters the product; wrong priors #29–#37 in human terms. |
| 2026-10-08 | T13 case A coverage; chain rule calibrated; oil instrument amendment and two-wars study registered. |
| 2026-10-09 | T16 prints: first measured blind-rate cut, first earned influence weight; h* 3 → 2 re-scored; E4 FAIL; 20 BLS texts on disk. |
| 2026-10-10 | E1, E3, E2 FAIL; lever programme closed; #40–#43. |
| 2026-10-11 | Prompt v1 and event calendar registered; A4 PASS 20/20; #44. |
| 2026-10-12 | Oil column built; chain re-defined to spot (founder's option 2); §12 edge written. |
| 2026-10-13 | 08:30 reader built and scheduled; oil amendment closed; §13 scorecard 13/18. |
| 2026-10-16 | T13 A3: path table, A3b FAIL, A3c leverage, A3d tail; inverse diagnostic; held-out FAIL; §3.24 registered; rows 42–44; #45–#48. |
| 2026-10-19 | History tables H0–H5 (all testable cells FAIL; horizon amendment); live feed repaired; Today tab rewritten; rows 45; #49, #51. |
| 2026-10-22 | Latency audit; price fallback; target-range Stage 1 0/24 PASS; SPEC_GRID; blind-spot plan; 8-K pool; row 46; #55. |
| 2026-10-23 | Factor attribution (T-A/T-B, sweeps), dynamic issuer pool, why-it-moved engine (T-E FAIL, T-F PASS, T-F′ PASS, T-G promoted), residual momentum FAIL ×5; rows 47–48; #58–#59, #63–#64, #67; §2 story and §5 log brought to date; sections renumbered. |
"""
    # append after the last change-log table row
    i = s.index("## 18. Change log of this master file"); j = s.find("\n# APPENDIX A", i)
    seg = s[i:j]; last = seg.rstrip("\n").rfind("\n|")
    if last > 0:
        end_row = seg.rstrip("\n").find("\n", last + 1); end_row = len(seg.rstrip("\n")) if end_row < 0 else end_row
        seg2 = seg.rstrip("\n")[:end_row] + "\n" + rows + seg.rstrip("\n")[end_row:] + "\n\n"
        s = s[:i] + seg2 + s[j:]; print("  MASTER change log: 7–23 Oct rows")
    else: print("  MASTER change log table not found -- add by hand")
m.write_text(s)

# ---------------------------------------------------------------- 2. alternative turning-point rules + T-I
wm = Path("src/why_moved.py"); s = wm.read_text()
if "def turning_points_persist(" in s: print("  segmenters: already")
else:
    block = '''

# ---------------------------------------------------------------- alternative turning-point rules (founder, 23 Oct) — T-I
def turning_points_persist(r: pd.Series, n_days: int = 3, x: float = 0.02):
    """Founder's rule: a turning point needs the direction to PERSIST — n_days consecutive sessions against the trend — and a minimum
    counter-move x from the extreme (x = 0 is the pure gradient rule)."""
    rr = r.fillna(0.0); px = np.exp(rr.cumsum().to_numpy()); d = np.sign(rr.to_numpy())
    hi = lo = 0; trend = 0; tps = []; run_ = 0
    for i in range(1, len(px)):
        if trend >= 0 and px[i] > px[hi]: hi = i
        if trend <= 0 and px[i] < px[lo]: lo = i
        against = (d[i] < 0) if trend >= 0 else (d[i] > 0)
        run_ = run_ + 1 if against else 0
        if trend >= 0 and run_ >= n_days and px[i] <= px[hi] * np.exp(-x):
            tps.append((hi, "peak")); trend = -1; lo = i; run_ = 0
        elif trend <= 0 and run_ >= n_days and px[i] >= px[lo] * np.exp(x):
            tps.append((lo, "trough")); trend = 1; hi = i; run_ = 0
    return tps, trend, (hi if trend > 0 else lo), px


def turning_points_swing(r: pd.Series, k: int = 10):
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


SEGMENTERS = [("zigzag 1.5× / 8% (registered)", lambda r: turning_points(r)[:4])] + \\
             [(f"persist N={n}, X={x:.0%}", (lambda n, x: (lambda r: turning_points_persist(r, n, x)))(n, x)) for n in (2, 3, 5, 10) for x in (0.0, 0.02, 0.04, 0.08)] + \\
             [(f"swing k={k}", (lambda k: (lambda r: turning_points_swing(r, k)))(k)) for k in (5, 10, 20)]


def segmenter_test(asset, patience=None, min_k=None, window=None):
    """T-I: every turning-point rule side by side — legs found, median length, share of legs under 5 sessions, and the explained share the
    promoted window rule reaches on each rule's legs. Descriptive comparison (same factor series for all); the registered zigzag stays the
    recorded rule unless another beats it by >= 5 points on median explained share with at least as many legs."""
    r = returns(asset).dropna(); F = factors(r.index); idx = r.index
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    bb = ((J.get("tests", {}).get(asset, {}).get("TG", {}) or {}).get("by_rule") or {}).get(f"{MULT},{FLOOR}") or {}
    patience = patience or bb.get("patience", 20); min_k = min_k or bb.get("min_k", 3); window = window or bb.get("window", 252)
    rows = []
    for name, fn in SEGMENTERS:
        tps, trend, ext, px = fn(r)[:4]
        legs = [(a, b, 1 if ka == "trough" else -1) for (a, ka), (b, kb) in zip(tps[:-1], tps[1:])]
        if not legs: rows.append(dict(rule=name, legs=0)); continue
        lengths = np.array([b - a for a, b, _ in legs]); sizes = np.array([abs(np.log(px[b] / px[a])) for a, b, _ in legs]); shares = []
        for a, b, d_ in legs:
            if b - a < MIN_EP or a < window + 10: continue
            cv = attr_curve(r, F, idx[a], max_k=min(b - a, MAX_K), window=window)
            if cv is None: continue
            wr = window_rules(cv, min(b - a, MAX_K), 1, patience, min_k)
            if wr and np.isfinite(wr["R5_causal"][1]): shares.append(wr["R5_causal"][1])
        rows.append(dict(rule=name, legs=len(legs), med_len=float(np.median(lengths)), short=float((lengths < 5).mean()), med_size=float(np.median(sizes)),
                         scored=len(shares), r5=float(np.median(shares)) if shares else np.nan))
    df = pd.DataFrame(rows); reg = df.iloc[0]
    better = df[(df.r5 >= reg.r5 + 0.05) & (df.scored >= reg.scored)] if np.isfinite(reg.r5) else df.iloc[0:0]
    L = [f"# T-I turning-point rules — {asset}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. Window rule used on every segmentation: patience {patience}, min window {min_k}, look-back {window} "
         f"(the promoted cell). 'short' = share of legs under 5 sessions (noise legs). Verdict rule: another segmentation replaces the zigzag only if its median explained share is "
         f"≥ 5 points higher with at least as many scored legs.*", "", f"**{'PASS for ' + ', '.join(better.rule) if len(better) else 'FAIL — no rule beats the registered zigzag by 5 points'}**", "",
         "| rule | legs since 2006 | median length (sessions) | share < 5 sessions | median size | legs scored | median explained share |", "|---|---|---|---|---|---|---|"]
    for _, q in df.iterrows():
        L.append(f"| {q.rule} | {q.legs} | {q.get('med_len', float('nan')):.0f} | {q.get('short', float('nan')):.0%} | {np.expm1(q.get('med_size', 0)):.1%} | {q.get('scored', 0)} | {q.r5 if 'r5' in q and np.isfinite(q.r5) else float('nan'):.0%} |")
    L += ["", "Reading: X = 0% is the pure gradient rule — direction flips with N consecutive closes; its legs are counted in days and mostly noise. Adding a minimum counter-move X "
          "turns it into a zigzag with a persistence condition; swing k is the local-extremum family. The founder's point stands as a rule in the grid; the data says which scale is useful."]
    J.setdefault("tests", {}).setdefault(asset, {})["TI"] = dict(rows=rows, better=list(better.rule), params=dict(patience=patience, min_k=min_k, window=window), run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1)); out = DOCS / f"segmenter_test_{asset}.md"; out.write_text("\\n".join(L) + "\\n"); print("\\n".join(L)); print(f"-> {out}")

'''
    s = s.replace("\n\ndef window_test(asset):", block + "\n\ndef window_test(asset):", 1)
    s = s.replace('    elif cmd == "window-grid": window_grid(sys.argv[2])', '    elif cmd == "window-grid": window_grid(sys.argv[2])\n    elif cmd == "segmenter-test": segmenter_test(sys.argv[2])', 1)
    wm.write_text(s); print("  why_moved: persistence/gradient and swing segmenters, T-I")

p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "T-I" in s: print("  prereg T-I: already")
else:
    s = s.replace("- Nightly: `src/why_moved.py`; app:", """- **T-I turning-point rules (founder, 23 Oct: "a reversal should be a trend — at least two sessions, not one bounce").** Alternatives to the
  zigzag: persistence — N consecutive sessions against the trend AND a counter-move ≥ X (X = 0 is the pure gradient rule), N ∈ {2,3,5,10},
  X ∈ {0, 2, 4, 8%}; swing highs/lows within k sessions, k ∈ {5,10,20}. Compared on legs found, median length, share of noise legs (< 5 sessions)
  and the explained share the promoted window rule reaches on each. A rule replaces the zigzag only if its median explained share is ≥ 5 points
  higher with at least as many scored legs. **Prior #68:** X = 0 rules produce hundreds of 3–6-session legs and lower shares; persistence with
  X = 4% and swing k = 10 land within 5 points of the zigzag; nothing replaces it.
- Nightly: `src/why_moved.py`; app:""", 1)
    p.write_text(s); print("  prereg: T-I registered")
print("done -- python -m src.why_moved segmenter-test GLD")
