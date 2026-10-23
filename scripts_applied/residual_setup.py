"""23 Oct: (1) best swept rule re-cuts the current leg with its own reversal rule; (2) T-H residual momentum / reversal test (src/residual_momentum.py);
(3) records: T-G result (#66 right), T-H registered (#67). Run from the repo root:
  python scripts_applied/residual_setup.py ; python -m src.residual_momentum selftest ; python -m src.residual_momentum run GLD | sed -n 1,30p ;
  python -m src.why_moved run | grep -A9 "^## gold" | sed -n 5,5p ; grep "Best cell" logs/ta_null_GLD.log"""
from pathlib import Path
import sys

# ---------------------------------------------------------------- 1. best rule re-cuts the leg
wm = Path("src/why_moved.py"); s = wm.read_text()
old = '''        if wr and tg.get("p") is not None and tg["p"] < 0.05:
            bb = tg["best"]; cvb = attr_curve(r, F, s0, max_k=MAX_K, window=bb["window"])
            wr_best = window_rules(cvb, min(Lnow, MAX_K), max(len(r.loc[i0:i1]) - 1, 1), bb["patience"], bb["min_k"]) if cvb is not None else None
'''
new = '''        best_leg = None
        if wr and tg.get("p") is not None and tg["p"] < 0.05:
            bb = tg["best"]
            if (bb["mult"], bb["floor"]) != (MULT, FLOOR):      # the cell's legs are cut by its own reversal rule: re-cut the current leg with it
                tps_b, trend_b, ext_b, px_b, thr_b = turning_points(r, bb["mult"], bb["floor"])
                if tps_b:
                    pb, kb_ = tps_b[-1]; s0b, db = idx[pb], (1 if kb_ == "trough" else -1); Lb = len(idx) - 1 - pb
                    best_leg = dict(start=s0b.strftime("%Y-%m-%d"), direction=db, sessions=int(Lb), move=float(np.log(px_b[-1] / px_b[pb])))
                else: s0b, db, Lb = s0, direction, Lnow
            else: s0b, db, Lb = s0, direction, Lnow
            cvb = attr_curve(r, F, s0b, max_k=MAX_K, window=bb["window"])
            if cvb is not None:
                ib0, ib1, _ = impulse_window(r, s0b, db, float(max(bb["floor"], bb["mult"] * r.rolling(20).std().iloc[-1] * np.sqrt(20))))
                wr_best = window_rules(cvb, min(Lb, MAX_K), max(len(r.loc[ib0:ib1]) - 1, 1), bb["patience"], bb["min_k"])
                if wr_best: wr_best["_attr"] = attribute(r, F, s0b, cvb["dates"][wr_best["R5_causal"][0] - 1])
'''
if old in s:
    s = s.replace(old, new, 1)
    s = s.replace("best_rule=(dict(sessions=int(wr_best['R5_causal'][0]), explained=float(wr_best['R5_causal'][1]), params=tg['best'], p=tg['p']) if wr_best and np.isfinite(wr_best['R5_causal'][1]) else None)",
                  "best_rule=(dict(sessions=int(wr_best['R5_causal'][0]), explained=float(wr_best['R5_causal'][1]), params=tg['best'], p=tg['p'], leg=best_leg, rows=(wr_best['_attr']['rows'][:4] if wr_best.get('_attr') else None)) if wr_best and np.isfinite(wr_best['R5_causal'][1]) else None)", 1)
    s = s.replace('''                     + (f" Best swept rule (patience {tg['best']['patience']}, min {tg['best']['min_k']}, look-back {tg['best']['window']}; p {tg['p']:.2f}): first {wr_best['R5_causal'][0]} sessions, explained {wr_best['R5_causal'][1]:.0%}." if wr_best else ""))''',
                  '''                     + (f" Best swept rule (reversal {tg['best']['mult']}×/{tg['best']['floor']:.0%}, look-back {tg['best']['window']}, patience {tg['best']['patience']}, min {tg['best']['min_k']}; p {tg['p']:.2f})"
                        + (f" cuts the leg as {'up' if best_leg['direction'] > 0 else 'down'} since {best_leg['start']} ({best_leg['sessions']} sessions, {pc(best_leg['move'])})" if best_leg else "")
                        + f": first {wr_best['R5_causal'][0]} sessions, explained {wr_best['R5_causal'][1]:.0%}"
                        + (": " + ", ".join(f"{d['label']} {d['share']:+.0%}" for d in wr_best['_attr']['rows'][:3]) if wr_best.get('_attr') else "") + "." if wr_best else ""))''', 1)
    wm.write_text(s); print("  why_moved: best rule re-cuts the leg, reasons shown")
else: print("  why_moved best-rule: already/absent")

# context paragraph prefers the promoted rule when present
c = Path("src/context.py"); s = c.read_text()
if "best_rule" in s: print("  context best rule: already")
else:
    old = "    r5 = wd.get(\"R5_causal\"); rows = A.get(\"r5_rows\") or []\n    if r5 and r5.get(\"explained\") is not None:"
    new = '''    r5 = wd.get("R5_causal"); rows = A.get("r5_rows") or []; br = A.get("best_rule")
    if br and br.get("explained") is not None:      # the swept rule that survived its null (T-G) replaces the registered 5/5 cell on the page
        rows = br.get("rows") or rows
        leg = br.get("leg"); pre = (f"Under the promoted window rule the leg is cut as {'rising' if leg['direction'] > 0 else 'falling'} since {leg['start']} ({leg['sessions']} sessions, {_pct(leg['move'])}). " if leg else "")
        top = ", ".join(f"{d['label']} {d['share']:+.0%}" for d in rows[:3]) or "—"
        S.append(f"<b>Why it moved.</b> {pre}Over the window where the named reasons explain most on a forward-walking rule (first {br['sessions']} sessions), they account for <b>{br['explained']:.0%}</b> "
                 f"of the move: {top}; the rest is unexplained by rates, the dollar, oil, volatility, geopolitical risk, liquidity or the macro state "
                 f"{tag('tested: PASS')} (rule promoted after a 216-cell sweep beat its noise null, p {br['p']:.2f}; patience {br['params']['patience']}, look-back {br['params']['window']}).")
        r5 = None
    if r5 and r5.get("explained") is not None:'''
    assert old in s, "context anchor"; c.write_text(s.replace(old, new, 1)); print("  context: promoted rule first")

# ---------------------------------------------------------------- 2. residual momentum
rm = Path("src/residual_momentum.py")
if rm.exists(): print("  residual_momentum.py: already")
else:
    rm.write_text(r'''"""
T-H — residual momentum / reversal (prereg_factor_attribution §5). The part of a market's return the named reasons do not explain:
does its recent cumulative value predict the next move (continuation = slow information / crowd), or the opposite (reversal = price pressure
unwinding)? Every window × horizon cell; the same grid on total returns beside it (plain momentum) — the residual has to beat that to matter.

  python -m src.residual_momentum selftest
  python -m src.residual_momentum run GLD [--null 200] [--lookback 252]
"""
from __future__ import annotations
import json, sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.factor_attribution import factors, returns, joint_fit, ORDER_DEFAULT

PROC, DOCS = Path("processed"), Path("docs")
WS = (5, 10, 20, 40, 60); HS = (5, 10, 20, 40, 60); REFIT = 20


def residual_series(asset, lookback=252):
    """Daily residual e_t = r_t - (alpha + F_t·b), betas from the prior `lookback` sessions, refit every REFIT sessions (walk-forward)."""
    r = returns(asset).dropna(); F = factors(r.index); avail = [f for f in ORDER_DEFAULT if f in F.columns and F[f].notna().mean() > 0.5]
    D = F[avail].join(r.rename("r")).dropna(); X, y = D[avail].to_numpy(), D.r.to_numpy(); e = np.full(len(y), np.nan)
    for i in range(lookback, len(y), REFIT):
        Xw, yw = X[i - lookback:i], y[i - lookback:i]; b = joint_fit(yw, Xw); alpha = yw.mean() - Xw.mean(0) @ b; j = min(i + REFIT, len(y))
        e[i:j] = y[i:j] - (X[i:j] @ b + alpha)
    E = pd.Series(e, index=D.index).dropna(); return E, D.r.loc[E.index]


def grid(signal_src: pd.Series, ret: pd.Series):
    """For each (w, h): signal = past-w cumulative of the source (known at t), forward = next-h return of the market; non-overlapping samples (step h).
    IC = Spearman correlation, hit = sign agreement, sharpe = annualised mean/sd of sign(signal) × forward."""
    out = {}
    for w in WS:
        sig = signal_src.rolling(w).sum()
        for h in HS:
            fwd = ret.rolling(h).sum().shift(-h); d = pd.DataFrame({"s": sig, "f": fwd}).dropna().iloc[::h]
            if len(d) < 30: out[(w, h)] = dict(n=len(d)); continue
            ic = float(d.s.corr(d.f, method="spearman")); hit = float((np.sign(d.s) == np.sign(d.f)).mean()); pnl = np.sign(d.s) * d.f
            out[(w, h)] = dict(n=int(len(d)), ic=ic, hit=hit, sharpe=float(pnl.mean() / pnl.std() * np.sqrt(252 / h)) if pnl.std() > 0 else np.nan)
    return out


def run(asset, n_null=200, lookback=252, seed=0):
    E, R = residual_series(asset, lookback); gr_res, gr_tot = grid(E, R), grid(R, R)
    cells = [(k, v) for k, v in gr_res.items() if "ic" in v]; best_k, best = max(cells, key=lambda kv: abs(kv[1]["ic"]))
    rng = np.random.default_rng(seed); mx = []
    for _ in range(n_null):
        sh = int(rng.integers(120, len(E) - 120)); Es = pd.Series(np.roll(E.to_numpy(), sh), index=E.index)
        vals = [abs(v["ic"]) for v in grid(Es, R).values() if "ic" in v]
        if vals: mx.append(max(vals))
    mx = np.array(mx); p = float((mx >= abs(best["ic"])).mean()) if len(mx) else np.nan
    tot_same = gr_tot.get(best_k, {}); beats = ("ic" in tot_same) and (abs(best["ic"]) - abs(tot_same["ic"]) >= 0.02)
    verdict = "PASS" if (p < 0.05 and beats) else ("INCONCLUSIVE" if p < 0.05 else "FAIL")
    shape = "continuation" if best["ic"] > 0 else "reversal"
    L = [f"# T-H residual momentum / reversal — {asset}", "", f"*{datetime.now():%Y-%m-%d %H:%M}. Residual from a rolling {lookback}-session fit of the named reasons (refit every {REFIT}). "
         f"Signal = past-w cumulative residual; forward = next-h return; non-overlapping samples. IC = rank correlation; positive = continuation, negative = reversal. "
         f"Best cell by |IC| judged against the best |IC| of the same grid on {len(mx)} shifted residual series; PASS also needs |IC| ≥ plain momentum's + 0.02 on the same cell.*", "",
         f"**Best cell: w {best_k[0]} → h {best_k[1]}: IC {best['ic']:+.3f} ({shape}), hit {best['hit']:.0%}, long-short Sharpe {best['sharpe']:+.2f}, n {best['n']}; "
         f"null best |IC| median {np.median(mx) if len(mx) else float('nan'):.3f}, p = {p:.3f}; plain momentum on the same cell IC {tot_same.get('ic', float('nan')):+.3f} → {verdict}**", "",
         "## Residual: IC by window (rows) × horizon (columns); sign hit-rate in brackets", "", "| w \\\\ h | " + " | ".join(str(h) for h in HS) + " |", "|---|" + "---|" * len(HS)]
    for w in WS: L.append(f"| {w} | " + " | ".join((f"{gr_res[(w, h)]['ic']:+.3f} ({gr_res[(w, h)]['hit']:.0%})" if "ic" in gr_res[(w, h)] else "—") for h in HS) + " |")
    L += ["", "## Plain momentum (total return) on the same grid", "", "| w \\\\ h | " + " | ".join(str(h) for h in HS) + " |", "|---|" + "---|" * len(HS)]
    for w in WS: L.append(f"| {w} | " + " | ".join((f"{gr_tot[(w, h)]['ic']:+.3f} ({gr_tot[(w, h)]['hit']:.0%})" if "ic" in gr_tot[(w, h)] else "—") for h in HS) + " |")
    pos = sum(1 for v in gr_res.values() if "ic" in v and v["ic"] > 0); neg = sum(1 for v in gr_res.values() if "ic" in v and v["ic"] < 0)
    L += ["", f"Shape across the grid: {pos} cells continuation, {neg} reversal. Reading: continuation at short horizons with reversal at long ones is the slow-information-then-unwind pattern; "
          "reversal everywhere is price pressure unwinding; nothing clearing the null means the residual is not predictable at these horizons — whatever caused it.",
          "Verdicts: PASS = predictable beyond noise AND better than plain momentum; INCONCLUSIVE = predictable but no better than the price trend itself; FAIL = not distinguishable from noise."]
    J = json.loads((PROC / "factor_attribution.json").read_text()) if (PROC / "factor_attribution.json").exists() else {}
    J.setdefault("tests", {}).setdefault(asset, {})["TH"] = dict(best=dict(w=best_k[0], h=best_k[1], **best), p=p, null_median=(float(np.median(mx)) if len(mx) else None), plain_ic=tot_same.get("ic"),
                                                               verdict=verdict, shape=shape, cells_cont=pos, cells_rev=neg, lookback=lookback, run=datetime.now().strftime("%Y-%m-%d %H:%M"))
    (PROC / "factor_attribution.json").write_text(json.dumps(J, indent=1)); out = DOCS / f"residual_momentum_{asset}.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")


def selftest():
    idx = pd.bdate_range("2010-01-01", periods=3000); rng = np.random.default_rng(0); z = rng.normal(0, 0.01, 3000); a = np.zeros(3000)
    for i in range(1, 3000): a[i] = 0.5 * a[i - 1] + z[i]                                              # planted continuation (AR(1), 0.5)
    e = pd.Series(a, index=idx); g = grid(e, e); assert g[(5, 5)]["ic"] > 0.08, g[(5, 5)]; print("  T1 planted continuation shows as positive IC: PASS")
    e2 = pd.Series(rng.normal(0, 0.01, 3000), index=idx); g2 = grid(e2, e2); assert abs(g2[(20, 20)]["ic"]) < 0.2, g2[(20, 20)]; print("  T2 noise shows no IC: PASS")
    print("selftest: 2/2")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True); sub.add_parser("selftest")
    q = sub.add_parser("run"); q.add_argument("asset"); q.add_argument("--null", type=int, default=200); q.add_argument("--lookback", type=int, default=252)
    a = ap.parse_args(); selftest() if a.cmd == "selftest" else run(a.asset, a.null, a.lookback)
''')
    print("  residual_momentum.py: written (T-H)")

# ---------------------------------------------------------------- 3. records
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "## 5. Residual" in s: print("  prereg §5: already")
else:
    s = s.replace("## Amendments\n", """## 5. The unexplained part as a signal — residual momentum / reversal (registered 2026-10-23, before code)
Founder: the share no reason explains is the crowd — emotion, trend-following, differing valuation standards; if it can be measured
consistently it may be the fund's alpha. Literature: residual momentum (Blitz, Huij & Martens 2011), noise-trader and slow-diffusion models;
price pressure unwinds (Campbell–Grossman–Wang; Nagel), information diffuses (Hong–Stein). The test is predictability, not the label.
- Residual e_t from a rolling 252-session fit of the named reasons (refit every 20 sessions). Signal = cumulative residual over the past w ∈ {5,10,20,40,60};
  forward return over h ∈ {5,10,20,40,60}; non-overlapping samples. Statistics: rank IC, sign hit-rate, long-short Sharpe. The same grid on total
  returns (plain momentum) beside it.
- **T-H:** best cell by |IC| vs the best |IC| of the same grid on 200 shifted residual series (p < 0.05), AND |IC| ≥ plain momentum's on that cell + 0.02
  → PASS; predictable but not better than the trend → INCONCLUSIVE; else FAIL. Sign of IC reports the shape (continuation / reversal) by horizon.
  Assets: GLD, SLV, USO, SPY, TLT, UUP, NVDA, META.
- **Prior #67:** GLD and SLV continuation at 20–60 sessions, IC 0.03–0.06, not beating plain momentum (INCONCLUSIVE); SPY, TLT, UUP FAIL; NVDA and META
  residual beats total (PASS) — the equity result of the literature.
- Before quoting any of it as strategy: the omitted-factor proxies (flows, positioning) go in first so the residual is the unmeasured part, not the unmodelled part.

## Amendments
""", 1)
    s = s.rstrip("\n") + "\n| 2026-10-23 | T-G (GLD) | 216 cells. Share rises with patience (2: 43%, 5: 54%, 15: 60%, 20–30: 64%); look-back 252 > 504 > 756 (62 / 54 / 51%); reversal rule flat. Best cell (2.0×/12%, 252, patience 10, min 3) 71% on 13 legs, best-of-sweep null p = 0.00 → **promoted** as the app's rule by this amendment; registered 5/5 cell stays the recorded verdict. Gold's current leg: ceiling 61% vs 12% on shifted series (excess +49 pts). | **#66 right** on patience and survival (predicted 10–20 / 58–65%; actual 20–30 / 64%); excess predicted ≈ 30, actual 49 |\n"
    p.write_text(s); print("  prereg: §5 T-H, T-G result")
t = Path("docs/TRACK.md"); s = t.read_text()
old = "App paragraph \"Why it moved\" wired into the Context block the same night.\n"
if "T-H residual momentum" in s: print("  TRACK: already")
elif old in s: t.write_text(s.replace(old, old + "**T-G:** patience and a one-year look-back lift the explained share to 64–71%; best cell survives its null and is promoted (#66 right). "
                               "**T-H residual momentum / reversal registered** (prereg §5, prior #67): is the unexplained part predictable, and better than plain momentum — the founder's "
                               "'crowd as alpha' question, tested as predictability across every window × horizon on all eight assets.\n", 1)); print("  TRACK: T-G, T-H noted")
else: print("  TRACK anchor not found -- add by hand")
print("done -- python -m src.residual_momentum selftest ; python -m src.residual_momentum run GLD")
