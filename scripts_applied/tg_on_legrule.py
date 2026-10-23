"""24 Oct (SGT evening 23 Oct): T-G re-run on the promoted current-leg rule's legs — patience x min window x look-back (72 cells), best cell vs the
best-of-sweep null on time-shifted factors; run() reads the window cell that belongs to the leg rule in use.
Run from the repo root:  python scripts_applied/tg_on_legrule.py ; python -m src.why_moved window-grid-rule GLD | tail -12 ; python -m src.why_moved run | grep -A6 "^## gold" | grep "Window where" | cut -c1-500"""
from pathlib import Path
import sys

wm = Path("src/why_moved.py"); s = wm.read_text()
if "def window_grid_rule(" in s: print("  window_grid_rule: already")
else:
    block = '''

def window_grid_rule(asset, n_shift: int = 10, seed: int = 0):
    """T-G on the legs of the promoted current-leg rule (processed/leg_rule.json): patience x min window x look-back; best cell judged against the best
    cell of the same sweep on time-shifted factors. Stored under TG['by_rule'][<rule name>] so run() uses the cell that belongs to the legs it shows."""
    if not LEG_RULE.exists(): print("  no promoted leg rule on file; the zigzag grid (window-grid) applies"); return
    lj = json.loads(LEG_RULE.read_text()); name = lj.get("name", "leg rule")
    r = returns(asset).dropna(); F = factors(r.index); idx = r.index; tps, trend, ext, px = run_rule(r, lj, asset)
    legs = [(a, b, 1 if ka == "trough" else -1) for (a, ka), (b, kb) in zip(tps[:-1], tps[1:]) if b - a >= MIN_EP]
    cells = [(w, p, k) for w in GRID_WINDOW for p in GRID_PATIENCE for k in GRID_MINK]
    def sweep(Fx):
        out = {}; curves = {}
        for w in GRID_WINDOW:
            curves[w] = [(attr_curve(r, Fx, idx[a], max_k=min(b - a, MAX_K), window=w), a, b, d) for a, b, d in legs if a >= w + 10]
        for (w, p, k) in cells:
            v5, v1 = [], []
            for cv, a, b, d in curves[w]:
                if cv is None: continue
                wr = window_rules(cv, min(b - a, MAX_K), 1, p, k)
                if wr and np.isfinite(wr["R5_causal"][1]): v5.append(wr["R5_causal"][1]); v1.append(wr["R1_full"][1])
            v5, v1 = np.array(v5), np.array(v1)
            out[(w, p, k)] = dict(n=int(len(v5)), r5=float(np.median(v5)) if len(v5) else np.nan, beat=float((v5 > v1).mean()) if len(v5) else np.nan)
        return out
    real = sweep(F); df = pd.DataFrame([dict(window=c[0], patience=c[1], min_k=c[2], **v) for c, v in real.items()]).dropna(subset=["r5"])
    best = df.loc[df.r5.idxmax()]; rng = np.random.default_rng(seed); mx = []
    for _ in range(n_shift):
        sh = int(rng.integers(120, len(F) - 120)); Fx = pd.DataFrame(np.roll(F.to_numpy(), sh, axis=0), index=F.index, columns=F.columns)
        vals = [v["r5"] for v in sweep(Fx).values() if np.isfinite(v["r5"])]
        if vals: mx.append(max(vals))
    mx = np.array(mx); p = float((mx >= best.r5).mean()) if len(mx) else np.nan
    L = [f"# T-G on the current-leg rule — {asset}: {name}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. {len(legs)} legs; {len(df)} cells (look-back × patience × min window); statistic = median R5 explained share; "
         f"best cell vs the best cell of the same sweep on {len(mx)} time-shifted factor series.*", "",
         f"**Best cell:** look-back {int(best.window)}, patience {int(best.patience)}, min window {int(best.min_k)} → median **{best.r5:.0%}**, beats the full leg in {best.beat:.0%} (n {int(best.n)}); "
         f"null best median {np.median(mx) if len(mx) else float('nan'):.0%}, **p = {p:.2f}** → " + ("survives — this is the window cell the page uses for these legs" if p < 0.05 else "does not beat the best noise cell — the registered 5/5 cell stays"), "",
         "By patience: " + ", ".join(f"{int(pp)}: {df[df.patience == pp].r5.median():.0%}" for pp in GRID_PATIENCE),
         "By look-back: " + ", ".join(f"{int(w)}: {df[df.window == w].r5.median():.0%}" for w in GRID_WINDOW),
         "By min window: " + ", ".join(f"{int(k)}: {df[df.min_k == k].r5.median():.0%}" for k in GRID_MINK), "",
         "| rank | look-back | patience | min k | median R5 | beats full | n |", "|---|---|---|---|---|---|---|"]
    for i, (_, q) in enumerate(df.sort_values("r5", ascending=False).head(10).iterrows(), 1):
        L.append(f"| {i} | {int(q.window)} | {int(q.patience)} | {int(q.min_k)} | {q.r5:.0%} | {q.beat:.0%} | {int(q.n)} |")
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    TG = J.setdefault("tests", {}).setdefault(asset, {}).setdefault("TG", {}); TG.setdefault("by_rule", {})
    TG["by_rule"][name] = dict(window=int(best.window), patience=int(best.patience), min_k=int(best.min_k), r5=float(best.r5), beat=float(best.beat), n=int(best.n), p=p,
                               null_median=(float(np.median(mx)) if len(mx) else None), legs=len(legs), run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1)); out = DOCS / f"window_grid_rule_{asset}.md"; out.write_text("\\n".join(L) + "\\n"); print("\\n".join(L)); print(f"-> {out}")

'''
    s = s.replace("\n\ndef ceiling_null(", block + "\n\ndef ceiling_null(", 1)
    # run(): the window cell that belongs to the legs in use
    old = '''        bb = (tg.get("by_rule") or {}).get(f"{MULT},{FLOOR}")       # best cell under the registered leg definition -> no re-cut'''
    new = '''        bb = (tg.get("by_rule") or {}).get((json.loads(LEG_RULE.read_text()).get("name") if LEG_RULE.exists() else f"{MULT},{FLOOR}"))   # the window cell swept on the legs actually shown'''
    assert old in s, "run bb anchor"; s = s.replace(old, new, 1)
    s = s.replace('    elif cmd == "segmenter-null": segmenter_null(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)',
                  '    elif cmd == "segmenter-null": segmenter_null(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)\n    elif cmd == "window-grid-rule": window_grid_rule(sys.argv[2])', 1)
    wm.write_text(s); print("  why_moved: window_grid_rule; run() reads the cell for the leg rule in use")
import ast; ast.parse(Path("src/why_moved.py").read_text()); print("  why_moved parses")

p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "T-G re-run on the current-leg rule" in s: print("  prereg: already")
else:
    s = s.replace("| date | change | reason |\n|---|---|---|\n", "| date | change | reason |\n|---|---|---|\n| 2026-10-23 (night) | **T-G re-run on the current-leg rule's legs** (look-back × patience × min window, 72 cells; best-of-sweep null, 10 shifts). The page uses the cell swept on the legs it shows. "
        "**Prior #75:** patience 15–30 and the one-year look-back win again; best cell 76–82%, survives the null. | The window cell on the page had been tuned on zigzag legs; the current leg is now cut by the founder's rule. |\n", 1)
    p.write_text(s); print("  prereg: T-G re-run registered (#75)")
print("done -- python -m src.why_moved window-grid-rule GLD")
