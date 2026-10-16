"""
T13 A3d -- the tail after an oil shock (prereg_blindspot §3b A3d, registered 16 Oct 2026).

For each market: the worst 10% of p8 post-shock paths by worst interim loss over 60 sessions. Measured: how far, by which
session, and the conditions at the shock (legs, regime, oil vs trailing-year median, S&P drawdown from its 1-year high).
Tested, walk-forward from the 30th shock: a nearest-neighbour tail score on those features; PASS if, at the threshold flagging
<= 25% of shocks, it finds >= 50% of tail cases (base rate 10%). Shown on the app regardless as the "severe case" line with today's
resemblance (low / moderate / high by the same score), labelled measured-not-forecast.

  python -m src.oil_tail selftest
  python -m src.oil_tail run          -> docs/oil_tail.md, processed/oil_tail.json (the app reads this)
"""
import argparse, json, sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.oil_shock import ROWS, ASSETS, HOLD, build_rows, load, regime_labels
OUT_MD, OUT_JSON = Path("docs/oil_tail.md"), Path("processed/oil_tail.json")
FEATS = ["dxy5", "dgs2_5bp", "oil5", "oil_vs_year", "spx_dd"]


def features(rets, dxy, dgs2, oil_px, spx_px, pos):
    i = pos
    oil_vs_year = float(np.log(oil_px.iloc[i] / oil_px.iloc[max(0, i - 252):i + 1].median()))
    spx_dd = float(np.log(spx_px.iloc[i] / spx_px.iloc[max(0, i - 252):i + 1].max()))
    return oil_vs_year, spx_dd


def tail_score(F_pool, y_pool, f, lab_pool, lab):
    """Share of tail cases among the nearest neighbours, Gaussian kernel on standardised features, half weight on regime mismatch."""
    mu, sd = np.nanmean(F_pool, 0), np.nanstd(F_pool, 0) + 1e-12
    Z, z = (F_pool - mu) / sd, (f - mu) / sd
    w = np.exp(-0.5 * ((Z - z) ** 2).sum(1)) * np.where(lab_pool == lab, 1.0, 0.5)
    return float((w * y_pool).sum() / w.sum()) if w.sum() > 0 else np.nan


def run(a):
    df = pd.read_csv(ROWS) if ROWS.exists() else build_rows(); p8 = df[df.pool == "p8"].copy()
    rets, dgs2, dxy = load(); lab_all = regime_labels(rets.index)
    oil_px = np.exp(rets["WTI_SPOT"].fillna(0).cumsum()); spx_px = np.exp(rets["SPY"].fillna(0).cumsum())
    extra = {int(pz): features(rets, dxy, dgs2, oil_px, spx_px, int(pz)) for pz in p8.pos.unique()}
    p8["oil_vs_year"] = p8.pos.map(lambda z: extra[int(z)][0]); p8["spx_dd"] = p8.pos.map(lambda z: extra[int(z)][1])
    today = dict(dxy5=float(dxy.iloc[-1] / dxy.iloc[-6] - 1), dgs2_5bp=float((dgs2.iloc[-1] - dgs2.iloc[-6]) * 100),
                 oil5=float(rets["WTI_SPOT"].fillna(0).iloc[-5:].sum()), oil_vs_year=float(np.log(oil_px.iloc[-1] / oil_px.iloc[-253:].median())),
                 spx_dd=float(np.log(spx_px.iloc[-1] / spx_px.iloc[-253:].max())), regime=int(lab_all.iloc[-1]))
    L = ["# T13 A3d — the tail after an oil shock", "",
         f"*{datetime.now():%Y-%m-%d}. Pool p8 (oil +8% in 5 sessions, 116 shocks since 1995; ETF rows from launch). Tail = worst 10% of paths by "
         f"worst interim loss over {HOLD} sessions for a long position. Classifier: nearest-neighbour tail share on the shock's features "
         f"(dollar 5s, DGS2 5s bp, oil 5s, oil vs its trailing-year median, S&P drawdown from its 1-year high) with half weight on a regime "
         "mismatch, walk-forward from the 30th shock; PASS = at the threshold flagging ≤ 25% of shocks it finds ≥ 50% of tail cases. "
         "The severe-case line is shown on the app whatever the verdict, as history.*", "",
         f"Today's features: dollar 5s {today['dxy5']:+.2%}, DGS2 5s {today['dgs2_5bp']:+.0f} bp, oil 5s {today['oil5']:+.1%}, oil vs year "
         f"{today['oil_vs_year']:+.1%}, S&P from 1-year high {today['spx_dd']:+.1%}, regime {today['regime']}.", ""]
    out = {"as_of": datetime.now().strftime("%Y-%m-%d"), "today": today, "markets": {}}
    for asset in ASSETS:
        s = p8[p8.asset == asset].dropna(subset=["worst"]).sort_values("date").reset_index(drop=True)
        if len(s) < 20: L.append(f"## {asset}: too few rows ({len(s)})"); continue
        thr = s.worst.quantile(0.10); tail = s[s.worst <= thr]
        y = (s.worst <= thr).to_numpy(float); F = s[FEATS].to_numpy(float); lab = s.regime.to_numpy(int)
        # severe case: the tail's median depth and timing, and the single worst
        worst_row = s.loc[s.worst.idxmin()]
        # walk-forward classifier
        scores = np.full(len(s), np.nan)
        for k in range(30, len(s)):
            ok = np.arange(k)[np.isfinite(F[:k]).all(1)]
            if len(ok) >= 20 and np.isfinite(F[k]).all(): scores[k] = tail_score(F[ok], y[ok], F[k], lab[ok], lab[k])
        m = np.isfinite(scores); sc, yy = scores[m], y[m]
        verdict, found, flagged, cut = "UNTESTED", np.nan, np.nan, np.nan
        if yy.sum() >= 10:
            cut = float(np.quantile(sc, 0.75)); flag = sc >= cut
            flagged = float(flag.mean()); found = float((flag & (yy == 1)).sum() / yy.sum())
            verdict = "PASS" if (flagged <= 0.25 + 1e-9 and found >= 0.50) else "FAIL"
        elif yy.sum() > 0: verdict = f"UNTESTED ({int(yy.sum())} tail cases in the scored window)"
        # today's resemblance
        okall = np.isfinite(F).all(1); f_today = np.array([today[c] for c in FEATS])
        res = tail_score(F[okall], y[okall], f_today, lab[okall], today["regime"])
        base = float(y.mean()); level = "high" if res >= 2 * base else "moderate" if res >= base else "low"
        cond = tail[FEATS + ["regime"]].median()
        L += [f"## {asset} — tail = worst {len(tail)} of {len(s)} shocks (threshold {thr:+.1%})", "",
              f"**Severe case (measured):** in the worst 1 in 10 past shocks the position fell a median {tail.worst.median():+.1%} "
              f"(range {tail.worst.min():+.1%} to {tail.worst.max():+.1%}), reaching the low around session {tail.worst_t.median():.0f}; the single worst was "
              f"{worst_row.date}: {worst_row.worst:+.1%} at session {worst_row.worst_t:.0f}. Still down {tail.f60.median():+.1%} at 60 sessions, "
              f"{tail.f90.median():+.1%} at 90.", "",
              f"**What those shocks looked like (medians):** dollar 5s {cond.dxy5:+.2%}, DGS2 5s {cond.dgs2_5bp:+.0f} bp, oil 5s {cond.oil5:+.1%}, oil vs year "
              f"{cond.oil_vs_year:+.1%}, S&P from 1-year high {cond.spx_dd:+.1%}, regime {cond.regime:.0f}. Dates: {', '.join(tail.date.tolist())}.", "",
              f"**Did the features predict the tail?** {verdict}" + (f" — at the top-quartile threshold the score flagged {flagged:.0%} of shocks and found {found:.0%} of tail cases (base rate {base:.0%})." if np.isfinite(found) else "."), "",
              f"**Today's resemblance to those shocks:** {level} (nearest-neighbour tail share {res:.0%} vs base rate {base:.0%}) — measured, not a forecast.", ""]
        out["markets"][asset] = dict(n=int(len(s)), tail_n=int(len(tail)), threshold=float(thr), tail_median_worst=float(tail.worst.median()),
                                    tail_min=float(tail.worst.min()), tail_max=float(tail.worst.max()), tail_t=float(tail.worst_t.median()),
                                    worst_date=str(worst_row.date), worst=float(worst_row.worst), worst_t=float(worst_row.worst_t),
                                    tail_f60=float(tail.f60.median()), tail_f90=float(tail.f90.median()), tail_dates=tail.date.tolist(),
                                    conditions={k: float(cond[k]) for k in FEATS + ["regime"]}, verdict=verdict, flagged=flagged, found=found,
                                    resemblance=res, resemblance_level=level, base_rate=base)
    L += ["What this does not say: that the next tail will look like the past ones, or that a low resemblance means safety. The verdict column is "
          "the only tested statement; everything else is the record of what happened."]
    OUT_MD.write_text("\n".join(L) + "\n"); OUT_JSON.write_text(json.dumps(out, indent=1)); print("\n".join(L)); print(f"-> {OUT_MD}, {OUT_JSON}")


def selftest(a):
    F = np.array([[0., 0.], [0., 0.], [3., 3.], [3., 3.]]); y = np.array([0., 0., 1., 1.]); lab = np.zeros(4, int)
    assert tail_score(F, y, np.array([3., 3.]), lab, 0) > 0.9 and tail_score(F, y, np.array([0., 0.]), lab, 0) < 0.1; print("  T1 tail score separates: PASS")
    assert abs(tail_score(F, y, np.array([1.5, 1.5]), lab, 0) - 0.5) < 1e-9; print("  T2 midpoint = 0.5: PASS")
    print("selftest: 2/2")


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True); sub.add_parser("selftest"); sub.add_parser("run")
    a = ap.parse_args(); {"selftest": selftest, "run": run}[a.cmd](a)


if __name__ == "__main__":
    main()
