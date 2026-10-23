"""23 Oct evening: fidelity measured at the counter-move's own date; segmenters(asset) shared; generic null + promotion for any rule (leg_rule.json spec);
segment() dispatches retrace/persist with hl/daysign; fine promotion withdrawn automatically when no cell qualifies; records (#72 wrong, tally 60; #73 right; #74).
Run from the repo root:  python scripts_applied/fidelity_fix_setup.py ; python -m src.why_moved segmenter-test GLD | sed -n 5,8p ; python -m src.why_moved segmenter-test GLD | grep "zigzag\\|hl-oc f=38%, N=3\\|retrace f=38%, N=3, c=0.5" ;
  python -m src.why_moved segmenter-null GLD ; python -m src.why_moved run | grep -A3 "^## gold" | sed -n 3,4p | cut -c1-330"""
from pathlib import Path
import sys

wm = Path("src/why_moved.py"); s = wm.read_text()
if "def segmenters(asset" in s: print("  why_moved: already")
else:
    # 1. fidelity at the move's own date
    old = s[s.index("def missed_reversals(tps, px, r: pd.Series):"):s.index("SEGMENTERS = [(")]
    new = '''def missed_reversals(tps, px, r: pd.Series):
    """Fidelity: inside each leg, the largest counter-move against the leg's direction, compared with the zigzag threshold AT THE DATE OF THAT MOVE
    (max(FLOOR, MULT x monthly vol at the time)); a counter-move above it is a turning point the rule failed to see. Returns the count and the worst one."""
    rr = r.fillna(0.0); thr = np.maximum(FLOOR, MULT * rr.rolling(20).std().bfill().fillna(rr.std()).to_numpy() * np.sqrt(20))
    missed, worst = 0, 0.0
    for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]):
        seg = px[a:b + 1]
        if ka == "trough": cm = seg / np.maximum.accumulate(seg) - 1          # up leg: drawdowns (negative)
        else: cm = -(seg / np.minimum.accumulate(seg) - 1)                     # down leg: rallies, as negatives
        t = int(np.argmin(cm)); dd = float(cm[t])
        if -dd >= thr[a + t]: missed += 1
        worst = min(worst, dd)
    return missed, float(-worst)


def segmenters(asset: str):
    """Every turning-point rule in the grid, for one asset (the high/low cells need its OHLC)."""
    HL = ohlc(asset)
    hl_cells = ([(f"retrace-hl f=38%, N={n}, c={c}", (lambda n, c: (lambda rr_: turning_points_retrace(rr_, 0.382, n, c, True, HL, "close")))(n, c)) for n in (3, 5) for c in (0.5, 1.0)]
                + [(f"retrace-hl-oc f=38%, N={n}, c={c}", (lambda n, c: (lambda rr_: turning_points_retrace(rr_, 0.382, n, c, True, HL, "oc")))(n, c)) for n in (2, 3) for c in (0.5, 1.0)]) if HL is not None else []
    return SEGMENTERS + hl_cells


def rule_from_name(name: str):
    """Parse a grid rule name into the spec the dispatcher runs."""
    import re
    m = re.match(r"persist-(time|closes) N=(\\d+), X=(\\d+)%", name)
    if m: return dict(rule="persist", mode=m.group(1), n=int(m.group(2)), x=int(m.group(3)) / 100)
    m = re.match(r"retrace(-hl)?(-oc)? f=(\\d+)%, N=(\\d+), c=([\\d.]+)", name)
    if m: return dict(rule="retrace", hl=bool(m.group(1)), daysign=("oc" if m.group(2) else "close"), f={25: 0.25, 38: 0.382, 50: 0.5}.get(int(m.group(3)), int(m.group(3)) / 100), n=int(m.group(4)), c=float(m.group(5)))
    m = re.match(r"swing k=(\\d+)", name)
    if m: return dict(rule="swing", k=int(m.group(1)))
    return None


def run_rule(r: pd.Series, spec: dict, asset: str):
    if spec["rule"] == "persist": return turning_points_persist(r, spec["n"], spec["x"], spec.get("mode", "time"))[:4]
    if spec["rule"] == "retrace": return turning_points_retrace(r, spec["f"], spec["n"], spec["c"], True, (ohlc(asset) if spec.get("hl") else None), spec.get("daysign", "close"))[:4]
    if spec["rule"] == "swing": return turning_points_swing(r, spec["k"])[:4]
    return turning_points(r)[:4]


'''
    s = s.replace(old, new, 1)
    # 2. segmenter_test uses segmenters(asset); fine promotion withdrawn when nothing qualifies
    i0 = s.index("    r = returns(asset).dropna(); F = factors(r.index); idx = r.index; HL = ohlc(asset)"); i1 = s.index("if HL is not None else [])\n", i0) + len("if HL is not None else [])\n")
    s = s[:i0] + "    r = returns(asset).dropna(); F = factors(r.index); idx = r.index; SEGS = segmenters(asset)\n" + s[i1:]
    old = '''    else:
        J["tests"][asset]["TJ"] = dict(verdict="FAIL")
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))'''
    new = '''    else:
        J["tests"][asset]["TJ"] = dict(verdict="FAIL")
        fr = PROC / "fine_rule.json"
        if fr.exists():   # the earlier fine promotion no longer qualifies under the current measure: withdraw, keep the file with the reason
            fj = json.loads(fr.read_text()); fj["withdrawn"] = datetime.now().strftime("%Y-%m-%d %H:%M"); fj["reason"] = "no retracement cell met 0 missed / lag <= 10 / share within 5 / legs >= zigzag on re-run"
            fr.replace(PROC / f"fine_rule_withdrawn_{datetime.now():%Y%m%d%H%M}.json"); (PROC / f"fine_rule_withdrawn_{datetime.now():%Y%m%d%H%M}.json").write_text(json.dumps(fj, indent=1)); print("  fine promotion withdrawn (no qualifying cell)")
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))'''
    assert old in s, "TJ json anchor"; s = s.replace(old, new, 1)
    # 3. generic segmenter_null + promotion; generic segment()
    old = s[s.index("def segment(r: pd.Series):"):s.index("def segmenter_null(")]
    new = '''def segment(r: pd.Series, asset: str = ""):
    """Turning points under the promoted leg rule if one is on file (processed/leg_rule.json), else the registered zigzag.
    Returns tps, trend, extreme position, price path, per-session reversal threshold array, and the rule's label for the page."""
    if LEG_RULE.exists():
        j = json.loads(LEG_RULE.read_text()); tps, trend, ext, px = run_rule(r, j, asset)
        if j["rule"] == "persist":
            x = j["x"]; thr = np.full(len(r), x if x > 0 else FLOOR)
            how = (f"{j['n']} consecutive sessions against the trend" if j.get("mode") == "closes" else f"the price staying off its extreme for {j['n']} sessions")
            return tps, trend, ext, px, thr, f"a reversal needs {how} and a counter-move of at least {x:.0%} (persistence rule, promoted {j.get('promoted', '')})"
        if j["rule"] == "retrace":
            rr = r.fillna(0.0); sig = rr.rolling(20).std().bfill().fillna(rr.std()).to_numpy() * np.sqrt(20)
            thr = np.maximum(j["c"] * sig, 0.0)   # the floor the rule applies today; the leg-relative part depends on the leg
            how = (f"{j['n']} open-to-close days against the trend" if j.get("daysign") == "oc" else f"{j['n']} sessions off the extreme")
            ex = "; extremes from the high and low of the day" if j.get("hl") else ""
            return tps, trend, ext, px, thr, (f"the founder's retracement rule — a turn is confirmed when the price has given back {j['f']:.0%} of the leg's own move "
                                              f"(floor {j['c']}× monthly volatility, never more than the zigzag's threshold) and {how}{ex} (promoted {j.get('promoted', '')}, superseding the zigzag)")
    tps, trend, ext, px, thr = turning_points(r)
    return tps, trend, ext, px, thr, "a reversal needs a counter-move of 1.5 × the asset's own monthly volatility, floor 8% (zigzag rule)"


'''
    s = s.replace(old, new, 1)
    old = s[s.index("def segmenter_null("):s.index("\n\ndef window_test(")]
    new = '''def segmenter_null(asset, rule_name=None, n_shift: int = 20, seed: int = 0):
    """T-I′: a winning segmentation's median explained share on time-shifted factors (legs do not depend on the factors; the attribution does).
    PASS if the real share beats the null median by >= 10 points and its 95th percentile -> promoted as the leg definition (processed/leg_rule.json)."""
    J = json.loads((PROC / "factor_attribution.json").read_text()); TI = J["tests"][asset]["TI"]
    rule_name = rule_name or (TI["better"][0] if TI.get("better") else None)
    if not rule_name: print("  no rule passed T-I; nothing to test"); return
    spec = rule_from_name(rule_name)
    if not spec: print(f"  cannot parse rule {rule_name}"); return
    P = TI["params"]; r = returns(asset).dropna(); F = factors(r.index); idx = r.index; tps, trend, ext, px = run_rule(r, spec, asset)
    legs = [(a, b) for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]) if b - a >= MIN_EP and a >= P["window"] + 10]
    def med_share(Fx):
        v = []
        for a, b in legs:
            cv = attr_curve(r, Fx, idx[a], max_k=min(b - a, MAX_K), window=P["window"])
            if cv is None: continue
            wr = window_rules(cv, min(b - a, MAX_K), 1, P["patience"], P["min_k"])
            if wr and np.isfinite(wr["R5_causal"][1]): v.append(wr["R5_causal"][1])
        return float(np.median(v)) if v else np.nan, len(v)
    real, n = med_share(F); rng = np.random.default_rng(seed); nulls = []
    for _ in range(n_shift):
        sh = int(rng.integers(120, len(F) - 120)); Fx = pd.DataFrame(np.roll(F.to_numpy(), sh, axis=0), index=F.index, columns=F.columns); nulls.append(med_share(Fx)[0])
    nulls = np.array([v for v in nulls if np.isfinite(v)]); med0, p95 = float(np.median(nulls)), float(np.quantile(nulls, .95))
    verdict = "PASS" if (real - med0 >= 0.10 and real > p95) else "FAIL"
    L = [f"# T-I′ null for the winning leg rule — {asset}: {rule_name}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. Real median explained share {real:.0%} over {n} legs; on {len(nulls)} time-shifted factor series: median {med0:.0%}, 95th pct {p95:.0%}.*",
         "", f"**{verdict}** — the rule's share on noise is {med0:.0%}; the real series adds {real - med0:+.0%} points." + (" **Promoted** as the leg definition from the next run (processed/leg_rule.json); the zigzag stays on record as superseded." if verdict == "PASS" else "")]
    J["tests"][asset]["TInull"] = dict(rule=rule_name, real=real, null_median=med0, null_p95=p95, n_shift=int(len(nulls)), verdict=verdict, run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))
    if verdict == "PASS":
        LEG_RULE.write_text(json.dumps(dict(spec, name=rule_name, promoted=datetime.now().strftime("%Y-%m-%d"), asset_tested=asset, real=real, null_median=med0, superseded="zigzag 1.5x / 8%"), indent=1))
    out = DOCS / f"segmenter_null_{asset}.md"; out.write_text("\\n".join(L) + "\\n"); print("\\n".join(L)); print(f"-> {out}")'''
    s = s.replace(old, new, 1)
    s = s.replace("        F = factors(r.index); tps, trend, ext, px, thr, rule_label = segment(r); idx = r.index", "        F = factors(r.index); tps, trend, ext, px, thr, rule_label = segment(r, a); idx = r.index", 1)
    # two-scale: the coarse scale is the promoted leg definition when one is on file
    s = s.replace("def two_scale(r: pd.Series, fine=None, hl=None, daysign: str = \"close\"):", "def two_scale(r: pd.Series, fine=None, hl=None, daysign: str = \"close\", coarse_fn=None):", 1)
    old = "    tps_c, trend_c, ext_c, px, thr = turning_points(r); idx = r.index"
    assert old in s, "two_scale coarse anchor"; s = s.replace(old, "    tps_c, trend_c, ext_c, px = (coarse_fn(r)[:4] if coarse_fn else turning_points(r)[:4]); idx = r.index", 1)
    old = '''            fj = json.loads(FINE.read_text()); ts = two_scale(r, (fj["f"], fj["n"], fj["c"]), hl=(ohlc(a) if fj.get("hl") else None), daysign=fj.get("daysign", "close"))'''
    assert old in s, "run two_scale anchor"
    s = s.replace(old, '''            fj = json.loads(FINE.read_text()); ts = two_scale(r, (fj["f"], fj["n"], fj["c"]), hl=(ohlc(a) if fj.get("hl") else None), daysign=fj.get("daysign", "close"),
                                                                coarse_fn=((lambda rr_: run_rule(rr_, json.loads(LEG_RULE.read_text()), a)) if LEG_RULE.exists() else None))''', 1)
    s = s.replace("Big picture (zigzag): {'up' if big['direction'] > 0 else 'down'}", "Big picture (leg definition): {'up' if big['direction'] > 0 else 'down'}", 1)
    s = s.replace('rule_label = (f"big picture by the zigzag; the current leg by the founder\'s retracement rule', 'rule_label = (f"big picture by the leg definition; the current leg by the founder\'s retracement rule', 1)
    wm.write_text(s); print("  why_moved: fidelity at the move's date, shared segmenters, generic null/promotion, dispatcher, auto-withdrawal, two-scale on the promoted coarse")

p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "at the move's own date" in s: print("  prereg: already")
else:
    s = s.replace("| date | change | reason |\n|---|---|---|\n", "| date | change | reason |\n|---|---|---|\n| 2026-10-23 (evening) | **Fidelity measured at the move's own date** (the zigzag threshold when the counter-move happened), not at the leg's end. | "
        "Under the leg-end version the cap produced 'more turning points, more missed': two 15% counter-moves from a volatile stretch counted once leg ends moved into calm periods. A rule is not at fault for not calling a 15% move a turn when monthly volatility was 15%. "
        "Prior #72 (cap → 0 missed, ~74%) wrong as measured (2 missed, 63–64%); #73 right (high/low extremes: ≤ 2 points, 0–1 sessions). Grid change: the open-to-close cells run at N ∈ {2, 3} (N = 5 freezes: 34 legs, lag 55). **Prior #74:** under the corrected measure the zigzag keeps ~3 missed, the fine cells 0–1; the founder's two-step cell (retrace-hl-oc f = 38%, N = 3) — 79% on 114 legs — clears the shifted-factor null by 60+ points and is promoted as the leg definition. |\n", 1)
    s = s.rstrip("\n") + ("\n| 2026-10-23 | T-J re-run with cap, high/low, open-to-close | **Founder's two-step cell best in the table: retrace-hl-oc f = 38%, N = 3 → 79% explained on 114 legs** (zigzag 68% / 54), 2 missed, lag 11 — passes the outright criterion, misses the fine-scale lag bar by one session; "
        "N = 5 open-to-close freezes (34 legs, lag 55), as consecutive closes did. Close-based retrace cells 61–66% with 2 missed under the leg-end fidelity measure (re-judged under the corrected one). f = 50% now finds 92–130 legs (the cap worked). | **#72 wrong**, **#73 right**. Tally 60 |\n")
    p.write_text(s); print("  prereg: fidelity amendment, T-J re-run")
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "tally 60" in s: print("  MASTER: already")
else:
    s = s.replace("#71 retracement cell, all Claude's)", "#71 retracement cell, #72 cap effect, all Claude's)", 1).replace("tally 59 (#40", "tally 60 (#40", 1)
    s = s.replace("| 23 Oct evening | **PASS**: f = 38%, N = 3, floor 0.5× vol — 215 legs, 0 missed, lag 6, 70% (#71 wrong on the cell); capped and high/low variants registered (#72, #73) |",
                  "| 23 Oct evening, three runs | fine scale f = 38%, N = 3, c = 0.5 promoted then re-judged; **the founder's two-step (high/low extremes, open-to-close days, N = 3) is the best cell: 79% on 114 legs** vs the zigzag's 68% on 54 — null and promotion as the leg definition pending the corrected fidelity measure (#72 wrong, #73 right, #74 open) |", 1)
    m.write_text(s); print("  MASTER: row 50, tally 60")
print("done")
