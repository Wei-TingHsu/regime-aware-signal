"""
Target-range engine, Stage 1 (docs/prereg_target_range.md). How far and how likely, by regime: reach probabilities and path quantiles.
  python -m src.target_range selftest
  python -m src.target_range build                      # processed/target_range.json + docs/target_range.md
  python -m src.target_range calibrate                  # the registered walk-forward test -> docs/target_range_calibration.md
  python -m src.target_range ask GLD --price 4090 --target 4500 --h 60
"""
from __future__ import annotations
import json, sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.oil_shock import load, regime_labels, ASSETS

PROC, DOCS = Path("processed"), Path("docs")
H = (20, 60, 120); X = (0.025, 0.05, 0.10, 0.15, 0.20)
OUT = PROC / "target_range.json"
SKILL_PASS, YEAR_SHARE, FIRST_YEAR = 0.05, 0.60, 2012


def extremes(r: pd.Series, h: int):
    """Per start session i: max and min cumulative log return over i+1..i+h, and the end value. NaN where the window is incomplete."""
    c = np.nancumsum(r.to_numpy()); n = len(r)      # c[i] = cumulative through session i
    mx = np.full(n, np.nan); mn = np.full(n, np.nan); end = np.full(n, np.nan)
    if n > h:
        w = sliding_window_view(c, h + 1)            # w[i] = c[i..i+h]
        seg = w[:, 1:] - w[:, [0]]                   # = returns of sessions i+1..i+h, cumulative from the close of session i
        k = seg.shape[0]                             # = n - h windows, for starts 0..n-h-1
        mx[:k], mn[:k], end[:k] = seg.max(1), seg.min(1), seg[:, -1]
    bad = r.isna().rolling(h).sum().shift(-h).fillna(1).to_numpy() > 0   # any NaN inside the window -> drop
    mx[bad] = mn[bad] = end[bad] = np.nan
    return mx, mn, end


def _probs(mx, mn, end, mask):
    m = mask & np.isfinite(mx); n = int(m.sum())
    if n == 0: return {"n": 0}
    d = {"n": n, "end_med": float(np.median(end[m])), "end_q25": float(np.quantile(end[m], .25)), "end_q75": float(np.quantile(end[m], .75)),
         "worst_med": float(np.median(mn[m])), "best_med": float(np.median(mx[m]))}
    for x in X:
        d[f"up_{x}"] = float((mx[m] >= np.log1p(x)).mean()); d[f"dn_{x}"] = float((mn[m] <= np.log1p(-x)).mean())
    return d


def build():
    lo = load(); rets = lo[0] if isinstance(lo, tuple) else lo; lab = regime_labels(rets.index).to_numpy()
    res = {"run": datetime.now().strftime("%Y-%m-%d %H:%M"), "horizons": list(H), "targets": list(X), "markets": {}}
    L = [f"# Target range — reach probabilities and path quantiles by regime (Stage 1, measured)", "",
         f"*{res['run']}. For each start session, the max/min cumulative return over the next h sessions. 'up 10%' = share of starts whose "
         "price touched +10% within h; 'end' = median path end [IQR]. Overlapping starts; independent cases ≈ n ÷ h. Measured only until the "
         "calibration test (prereg_target_range §Stage 1) has run.*", ""]
    for a in [x for x in ASSETS if x in rets.columns]:
        r = rets[a]; res["markets"][a] = {}
        L += [f"## {a}", "", "| h | regime | n (indep.) | end median [IQR] | typical worst | typical best | up 5% | up 10% | up 20% | down 5% | down 10% | down 20% |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for h in H:
            mx, mn, end = extremes(r, h); res["markets"][a][str(h)] = {}
            for k in ["all"] + sorted(set(int(v) for v in lab if v >= 0)):
                mask = np.ones(len(r), bool) if k == "all" else (lab == k)
                d = _probs(mx, mn, end, mask); res["markets"][a][str(h)][str(k)] = d
                if d["n"] == 0: continue
                pc = lambda v: f"{np.expm1(v):+.1%}"
                L.append(f"| {h} | {k} | {d['n']:,} ({d['n'] // h}) | {pc(d['end_med'])} [{pc(d['end_q25'])}, {pc(d['end_q75'])}] | {pc(d['worst_med'])} | {pc(d['best_med'])} | "
                         f"{d['up_0.05']:.0%} | {d['up_0.1']:.0%} | {d['up_0.2']:.0%} | {d['dn_0.05']:.0%} | {d['dn_0.1']:.0%} | {d['dn_0.2']:.0%} |")
        L.append("")
    OUT.write_text(json.dumps(res, indent=1)); (DOCS / "target_range.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:40])); print(f"... -> docs/target_range.md, {OUT}")


def calibrate():
    """Walk-forward: probabilities from windows ending before year y, applied to non-overlapping starts in y, Brier vs unconditional."""
    lo = load(); rets = lo[0] if isinstance(lo, tuple) else lo; lab = regime_labels(rets.index).to_numpy(); idx = rets.index
    h = 60; last_year = idx[-1].year - 1; rows = []
    for a in [x for x in ASSETS if x in rets.columns]:
        r = rets[a]; mx, mn, end = extremes(r, h); yrs = idx.year.to_numpy()
        for x in (0.05, 0.10):
            for side, arr, thr in (("up", mx, np.log1p(x)), ("down", mn, np.log1p(-x))):
                per_year = []
                for y in range(FIRST_YEAR, last_year + 1):
                    train = (yrs < y) & np.isfinite(arr) & (np.arange(len(r)) + h < idx.searchsorted(pd.Timestamp(f"{y}-01-01")))
                    if train.sum() < 500: continue
                    starts = [i for i in range(idx.searchsorted(pd.Timestamp(f"{y}-01-01")), idx.searchsorted(pd.Timestamp(f"{y + 1}-01-01")), h) if np.isfinite(arr[i])]
                    if len(starts) < 2: continue
                    hit_tr = (arr[train] >= thr) if side == "up" else (arr[train] <= thr)
                    p_unc = hit_tr.mean(); lab_tr = lab[train]
                    b_reg = b_unc = 0.0; cnt = 0
                    for i in starts:
                        k = lab[i]; sel = lab_tr == k
                        p_reg = hit_tr[sel].mean() if (k >= 0 and sel.sum() >= 100) else p_unc
                        y_ = float((arr[i] >= thr) if side == "up" else (arr[i] <= thr))
                        b_reg += (p_reg - y_) ** 2; b_unc += (p_unc - y_) ** 2; cnt += 1
                    per_year.append((y, cnt, b_reg / cnt, b_unc / cnt))
                if not per_year: rows.append(dict(market=a, x=x, side=side, verdict="INCONCLUSIVE", years=0)); continue
                py = pd.DataFrame(per_year, columns=["year", "n", "b_reg", "b_unc"])
                skill = 1 - py.b_reg.sum() / py.b_unc.sum() if py.b_unc.sum() > 0 else np.nan
                share = float((py.b_reg < py.b_unc).mean())
                verdict = "PASS" if (skill >= SKILL_PASS and share >= YEAR_SHARE) else ("FAIL" if skill <= 0 else "INCONCLUSIVE")
                rows.append(dict(market=a, x=x, side=side, years=len(py), cases=int(py.n.sum()), skill=skill, years_better=share, verdict=verdict))
    df = pd.DataFrame(rows)
    L = [f"# Target range — Stage 1 calibration (registered test)", "",
         f"*{datetime.now():%Y-%m-%d %H:%M}. h = 60; targets ±5%, ±10%; years {FIRST_YEAR}–{last_year}; Brier skill of regime-conditional reach probabilities "
         f"over unconditional ones, walk-forward. PASS: skill ≥ {SKILL_PASS} and better in ≥ {YEAR_SHARE:.0%} of years; FAIL: skill ≤ 0. "
         f"{len(df)} cells — about {int(0.1 * len(df))} could pass by chance.*", "",
         "| market | target | side | years | cases | Brier skill | years better | verdict |", "|---|---|---|---|---|---|---|---|"]
    for _, q in df.iterrows():
        L.append(f"| {q.market} | {q.x:.0%} | {q.side} | {q.years} | {q.get('cases', '')} | {q.skill:+.3f} | {q.years_better:.0%} | {q.verdict} |" if "skill" in q and pd.notna(q.skill)
                 else f"| {q.market} | {q.x:.0%} | {q.side} | {q.years} | | | | {q.verdict} |")
    vc = df.verdict.value_counts().to_dict()
    L += ["", f"Verdict counts: {vc}. Per market, majority PASS: " + ", ".join(f"{m}: {'yes' if (g.verdict == 'PASS').mean() > 0.5 else 'no'}" for m, g in df.groupby('market'))]
    (DOCS / "target_range_calibration.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print("-> docs/target_range_calibration.md")


def _passed() -> bool:
    cal = DOCS / "target_range_calibration.md"
    return cal.exists() and any(ln.strip().endswith("| PASS |") for ln in cal.read_text().splitlines())


def ask(asset, price, targets, h, regime=None):
    """The output form of the prereg, computed exactly from history for any list of price levels. Calibrated (unconditional) numbers first;
    the regime-conditional ones are marked uncalibrated until a Stage 1 cell passes."""
    lo = load(); rets = lo[0] if isinstance(lo, tuple) else lo; lab = regime_labels(rets.index).to_numpy(); r = rets[asset]
    if regime is None: regime = int(lab[-1])
    mx, mn, end = extremes(r, h); ok = np.isfinite(mx); m_all = ok; m_reg = ok & (lab == regime)
    px = lambda v: price * np.exp(v)
    def block(mask, name):
        e, hi, lo_ = end[mask], mx[mask], mn[mask]; n = int(mask.sum())
        q25, q50, q75 = np.quantile(e, [.25, .5, .75])
        print(f"{name} (n {n:,}, ≈{n // h} independent {h}-session cases):")
        print(f"  central target {px(q50):,.0f}  (band {px(q25):,.0f} – {px(q75):,.0f}); typical worst on the way {px(np.median(lo_)):,.0f}, typical best {px(np.median(hi)):,.0f}")
        print(f"  levels history gave a chance of touching within {h} sessions:  1-in-2: {px(np.quantile(hi, .5)):,.0f}   1-in-3: {px(np.quantile(hi, 2/3)):,.0f}   1-in-10: {px(np.quantile(hi, .9)):,.0f}"
              f"   | downside 1-in-2: {px(np.quantile(lo_, .5)):,.0f}   1-in-3: {px(np.quantile(lo_, 1/3)):,.0f}   1-in-10: {px(np.quantile(lo_, .1)):,.0f}")
        for tgt in targets:
            x = np.log(tgt / price); pr = float((hi >= x).mean()) if x > 0 else float((lo_ <= x).mean())
            print(f"  chance of touching {tgt:,.0f} ({x:+.1%}) within {h} sessions: {pr:.0%}")
    print(f"{asset} at {price:,.0f}, horizon {h} sessions.")
    block(m_all, "Over all history — the calibrated form")
    block(m_reg, f"In today's condition ({regime}) — " + ("calibrated cell on record" if _passed() else "NOT calibrated (Stage 1: 0 of 24 cells passed), shown for comparison"))
    print("Measured counts, not forecasts. Reasons (Stage 2) and weights (Stage 3) will shift these once they pass their tests.")


def selftest():
    idx = pd.bdate_range("2000-01-03", periods=300); r = pd.Series(0.0, index=idx); r.iloc[11:21] = 0.01; r.iloc[21:31] = -0.03
    mx, mn, end = extremes(r, 20)
    assert abs(mx[10] - 0.10) < 1e-9 and abs(mn[10] - (0.10 - 0.30)) < 1e-9 and abs(end[10] - (-0.20)) < 1e-9, (mx[10], mn[10], end[10]); print("  T1 extremes: PASS")
    assert np.isnan(mx[-1]) and np.isfinite(mx[0]); print("  T2 window bounds: PASS")
    d = _probs(mx, mn, end, np.ones(len(r), bool)); assert 0 <= d["up_0.05"] <= 1 and d["n"] == 280; print("  T3 probabilities: PASS")
    print("selftest: 3/3")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    for c in ("selftest", "build", "calibrate"): sub.add_parser(c)
    q = sub.add_parser("ask"); q.add_argument("asset"); q.add_argument("--price", type=float, required=True); q.add_argument("--target", type=float, nargs="*", default=[])
    q.add_argument("--h", type=int, default=60); q.add_argument("--regime", type=int, default=None)
    a = ap.parse_args()
    if a.cmd == "ask": ask(a.asset, a.price, a.target or [a.price * k for k in (1.05, 1.10, 1.20, 1.30, 0.95, 0.90)], a.h, a.regime)
    else: {"selftest": selftest, "build": build, "calibrate": calibrate}[a.cmd]()
