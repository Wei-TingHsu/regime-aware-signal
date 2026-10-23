"""
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
