"""23 Oct: T-I result (founder's persistence rule PASS; #68 wrong, tally 57); shifted-factor null for the winning rule and automatic promotion
(processed/leg_rule.json); why_moved cuts legs with the promoted rule; the page names the rule. Run from the repo root:
  python scripts_applied/leg_rule_setup.py ; python -m src.why_moved segmenter-null GLD ; python -m src.why_moved run | grep -A4 "^## gold" ; python -m src.context show GLD | sed -n 3,3p | cut -c1-400"""
from pathlib import Path
import sys

wm = Path("src/why_moved.py"); s = wm.read_text()
if "def segment(" in s: print("  why_moved leg rule: already")
else:
    block = '''

# ---------------------------------------------------------------- promoted leg rule (T-I) and the dispatcher every nightly step uses
LEG_RULE = PROC / "leg_rule.json"


def segment(r: pd.Series):
    """Turning points under the promoted leg rule if one is on file (processed/leg_rule.json), else the registered zigzag.
    Returns tps, trend, extreme position, price path, per-session reversal threshold array, and the rule's label for the page."""
    if LEG_RULE.exists():
        j = json.loads(LEG_RULE.read_text())
        if j.get("rule") == "persist":
            n, x = int(j["n"]), float(j["x"]); tps, trend, ext, px = turning_points_persist(r, n, x)
            thr = np.full(len(r), x if x > 0 else FLOOR)
            return tps, trend, ext, px, thr, f"a reversal needs {n} consecutive sessions against the trend and a counter-move of at least {x:.0%} (persistence rule, promoted {j.get('promoted', '')})"
    tps, trend, ext, px, thr = turning_points(r)
    return tps, trend, ext, px, thr, "a reversal needs a counter-move of 1.5 × the asset's own monthly volatility, floor 8% (zigzag rule)"


def segmenter_null(asset, rule_name=None, n_shift: int = 20, seed: int = 0):
    """T-I′: the winning segmentation's median explained share on time-shifted factors (legs do not depend on the factors; the attribution does).
    PASS if the real share beats the null median by >= 10 points and its 95th percentile -> the rule is promoted (processed/leg_rule.json)."""
    J = json.loads((PROC / "factor_attribution.json").read_text()); TI = J["tests"][asset]["TI"]
    rule_name = rule_name or (TI["better"][0] if TI.get("better") else None)
    if not rule_name: print("  no rule passed T-I; nothing to test"); return
    import re
    mm = re.match(r"persist N=(\\d+), X=(\\d+)%", rule_name)
    if not mm: print(f"  only persistence rules are promotable here ({rule_name})"); return
    n_, x_ = int(mm.group(1)), int(mm.group(2)) / 100; P = TI["params"]
    r = returns(asset).dropna(); F = factors(r.index); idx = r.index; tps, trend, ext, px = turning_points_persist(r, n_, x_)
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
         "", f"**{verdict}** — the rule's share on noise is {med0:.0%}; the real series adds {real - med0:+.0%} points." + (f" **Promoted**: legs are cut by this rule from the next run (processed/leg_rule.json); the zigzag stays on record as the superseded rule." if verdict == "PASS" else "")]
    J["tests"][asset]["TInull"] = dict(rule=rule_name, real=real, null_median=med0, null_p95=p95, n_shift=int(len(nulls)), verdict=verdict, run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1))
    if verdict == "PASS":
        LEG_RULE.write_text(json.dumps(dict(rule="persist", n=n_, x=x_, promoted=datetime.now().strftime("%Y-%m-%d"), asset_tested=asset, real=real, null_median=med0, superseded="zigzag 1.5x / 8%"), indent=1))
    out = DOCS / f"segmenter_null_{asset}.md"; out.write_text("\\n".join(L) + "\\n"); print("\\n".join(L)); print(f"-> {out}")

'''
    s = s.replace("\n\ndef window_test(asset):", block + "\n\ndef window_test(asset):", 1)
    # run() uses the dispatcher
    old = "        F = factors(r.index); tps, trend, ext, px, thr = turning_points(r); idx = r.index\n        if not tps: continue"
    assert old in s, "run segment anchor"
    s = s.replace(old, "        F = factors(r.index); tps, trend, ext, px, thr, rule_label = segment(r); idx = r.index\n        if not tps: continue", 1)
    s = s.replace("                                                               extreme_so_far=dict(date=idx[ext].strftime(\"%Y-%m-%d\"), move=ext_move), threshold_now=float(thr[-1])),",
                  "                                                               extreme_so_far=dict(date=idx[ext].strftime(\"%Y-%m-%d\"), move=ext_move), threshold_now=float(thr[-1]), rule=rule_label),", 1)
    s = s.replace('''              f"- Current episode: **{'up' if direction > 0 else 'down'} since {s0.date()}** ({kind} confirmed; {len(idx) - 1 - s0_pos} sessions), move so far {pc(move)}; extreme so far {pc(ext_move)} on {idx[ext].date()}; reversal threshold now {thr[-1]:.1%}.",''',
                  '''              f"- Current episode: **{'up' if direction > 0 else 'down'} since {s0.date()}** ({kind} confirmed; {len(idx) - 1 - s0_pos} sessions), move so far {pc(move)}; extreme so far {pc(ext_move)} on {idx[ext].date()}; {rule_label}.",''', 1)
    s = s.replace('    elif cmd == "segmenter-test": segmenter_test(sys.argv[2])', '    elif cmd == "segmenter-test": segmenter_test(sys.argv[2])\n    elif cmd == "segmenter-null": segmenter_null(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)', 1)
    wm.write_text(s); print("  why_moved: segment() dispatcher, T-I' null, promotion file, page label")

c = Path("src/context.py"); s = c.read_text()
old = '''f"{_pct(ep['extreme_so_far']['move'])} on {ep['extreme_so_far']['date']}; a move of {ep['threshold_now']:.1%} against the trend would end this leg "
             f"(the reversal rule: 1.5 × the asset's own monthly volatility, floor 8%) {tag('measured')}.")'''
new = '''f"{_pct(ep['extreme_so_far']['move'])} on {ep['extreme_so_far']['date']}; how a leg ends: {ep.get('rule', 'a counter-move of 1.5 × the asset\\'s monthly volatility, floor 8%')} {tag('measured')}.")'''
if old in s: c.write_text(s.replace(old, new, 1)); print("  context: names the leg rule")
else: print("  context leg-rule wording: already/absent")

# records
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "| 2026-10-23 | T-I (GLD) |" in s: print("  prereg T-I result: already")
else:
    s = s.replace("- Nightly: `src/why_moved.py`; app:", """- **T-I′ (registered 23 Oct after T-I passed, before running):** the winning rule's median explained share on 20 time-shifted factor series; PASS if
  real ≥ null median + 10 points and > 95th pct → promoted automatically (processed/leg_rule.json), the zigzag superseded on record. **Prior #69:** PASS.
- Nightly: `src/why_moved.py`; app:""", 1)
    s = s.rstrip("\n") + ("\n| 2026-10-23 | T-I (GLD) | 17 rules. **Founder's persistence rule N = 5 sessions, X = 4%: median explained share 74% on 34 legs vs the zigzag's 68% on 24 → PASS** "
        "(≥ 5 points, more legs). Pure gradient rules (X = 0, N = 2–3): 350–900 legs, 16–49% under five sessions, 48–61%; N = 10 never fires; swing k = 5: 554 legs, 53%. "
        "`docs/segmenter_test_GLD.md` | **#68 wrong** (predicted nothing replaces the zigzag). Tally 57 |\n")
    p.write_text(s); print("  prereg: T-I result, T-I' registered")
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "| 49 | Leg definition" in s: print("  MASTER row 49: already")
else:
    i = s.index("| 48 | Residual momentum"); j = s.index("\n", i) + 1
    s = s[:j] + ("| 49 | Leg definition (T-I): the founder's persistence rule — a turning point needs N consecutive sessions against the trend and a counter-move ≥ X — beats the zigzag's legs "
                 "on explained share by ≥ 5 points with as many legs | 23 Oct, 17 rules on GLD | **PASS: N = 5, X = 4% → 74% vs 68%** (#68 wrong); pure gradient rules (X = 0) cut gold into "
                 "hundreds of noise legs; T-I′ shifted-factor null decides promotion | `docs/segmenter_test_GLD.md`, prereg_factor_attribution §4 |\n") + s[j:]
    s = s.replace("#67 residual momentum, all Claude's)", "#67 residual momentum, #68 leg-definition rule (the founder's persistence rule won), all Claude's)", 1).replace("tally 56 (#40", "tally 57 (#40", 1)
    m.write_text(s); print("  MASTER: row 49, tally 57")
c2 = Path("docs/CURRENT_STATE_2026-08-23.md"); s = c2.read_text()
if "founder's persistence rule" in s: print("  CURRENT_STATE: already")
else:
    c2.write_text(s.rstrip("\n") + """

### 18.37 The founder's turning-point rule wins (23 Oct, evening)

The founder objected to the zigzag's logic — a reversal should be a trend, at least two sessions, not one bounce — and proposed a gradient /
persistence rule. Seventeen segmentations were compared under the registered criterion: his rule at N = 5 consecutive sessions with a 4%
counter-move explains a median 74% of gold's legs against the zigzag's 68%, on more legs — PASS, prior #68 wrong (tally 57). The pure gradient
versions (no minimum move) cut gold into hundreds of noise legs, as predicted. Before promotion the winning rule faces the same shifted-factor
null the window rule did (T-I′); on PASS the nightly cuts legs with it and the page says so. PROJECT_MASTER brought to date the same day
(story to 23 Oct, wrong priors to #68, numbering fixed, Appendix A marked superseded).
"""); print("  CURRENT_STATE 18.37: appended")
print("done -- python -m src.why_moved segmenter-null GLD")
