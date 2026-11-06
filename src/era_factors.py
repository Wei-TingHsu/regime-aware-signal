"""era_factors.py -- the factor sensitivities by era, and the 2026 gold episode re-attributed with each era's betas
(prereg_subperiod_audit.md, group B, item B4: the founder's 'change of habit' asked of the named reasons).

  python -m src.era_factors --asset GLD            # per era: joint betas, in-sample R2, each factor's sign vs the pooled sign; T-A's walk-forward
                                                   # OOS R2 by era for W in {252, 504, 756, 1008} (sweep, null = factors time-shifted together);
                                                   # the current episode (peak -> last session) attributed with pre-episode, 2009-21 and 2022-> betas
  python -m src.era_factors --asset GLD --episode-start 2026-01-28 --episode-end 2026-10-21

Inputs: src.factor_attribution.factors(idx) and .returns(asset) (the registered proxies, 23/27 Oct). Outputs docs/era_factors_<asset>.md (+ .json).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.sweep import grid, run, write_md

DOCS = Path("docs")
ERAS = [("2004-08", "2004-01-01", "2008-12-31"), ("2009-14", "2009-01-01", "2014-12-31"), ("2015-19", "2015-01-01", "2019-12-31"),
        ("2020-21", "2020-01-01", "2021-12-31"), ("2022-26", "2022-01-01", "2026-12-31")]
BLOCK = 20


def era_of(d) -> str:
    for name, a, b in ERAS:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b): return name
    return "other"


def fit(X: np.ndarray, y: np.ndarray):
    Xc = np.column_stack([np.ones(len(y)), X]); c, *_ = np.linalg.lstsq(Xc, y, rcond=None); e = y - Xc @ c
    r2 = 1 - (e @ e) / (((y - y.mean()) ** 2).sum() or np.nan); return c[1:], float(r2), e


def oos_r2(X: np.ndarray, y: np.ndarray, dates: pd.DatetimeIndex, W: int, block: int = BLOCK) -> pd.DataFrame:
    rows = []
    for s in range(W, len(y) - block, block):
        b, _, _ = fit(X[s - W:s], y[s - W:s]); yb = y[s:s + block]; pred = X[s:s + block] @ b + y[s - W:s].mean()
        r2 = 1 - ((yb - pred) ** 2).sum() / (((yb - yb.mean()) ** 2).sum() or np.nan)
        rows.append(dict(date=dates[s], r2=float(r2), era=era_of(dates[s])))
    return pd.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--asset", default="GLD"); ap.add_argument("--episode-start"); ap.add_argument("--episode-end"); ap.add_argument("--n-null", type=int, default=100)
    ap.add_argument("--drop-late", action="store_true", help="drop every factor whose series starts after 2006-01-01, so the 2004-14 eras enter (v2, 6 Nov)")
    ap.add_argument("--drop", default="", help="comma-separated factor names to drop")
    a = ap.parse_args()
    from src.factor_attribution import factors, returns
    r = returns(a.asset); r.index = pd.to_datetime(r.index)
    F = factors(r.index); F.index = pd.to_datetime(F.index)
    starts = {c: F[c].first_valid_index() for c in F.columns}
    late = [c for c, d0 in starts.items() if d0 is not None and d0 > pd.Timestamp("2006-01-01")]
    print("factor start dates: " + ", ".join(f"{c} {d0.date() if d0 is not None else '—'}" for c, d0 in starts.items()))
    drop = set(x for x in a.drop.split(",") if x) | (set(late) if a.drop_late else set())
    if drop: print(f"dropped: {sorted(drop)}"); F = F.drop(columns=[c for c in drop if c in F.columns])
    d = pd.concat([r.rename("y"), F], axis=1).dropna(); names = [c for c in d.columns if c != "y"]
    X, y, dates = d[names].to_numpy(float), d["y"].to_numpy(float), d.index
    era = np.array([era_of(t) for t in dates])
    b_all, r2_all, _ = fit(X, y)
    rows = [dict(era="all", n=len(y), r2=r2_all, **{k: v for k, v in zip(names, b_all)})]
    for e in [e[0] for e in ERAS]:
        m = era == e
        if m.sum() < 250: continue
        b, r2, _ = fit(X[m], y[m]); rows.append(dict(era=e, n=int(m.sum()), r2=r2, **{k: v for k, v in zip(names, b)}))
    tab = pd.DataFrame(rows)
    signs = pd.DataFrame({k: [np.sign(tab.loc[i, k]) == np.sign(b_all[j]) for i in tab.index] for j, k in enumerate(names)}, index=tab["era"])
    # T-A by era x window, the sweep
    cells = grid(W=[252, 504, 756, 1008], era=["all"] + [e[0] for e in ERAS if (era == e[0]).sum() >= 250])
    def stat(dd, c):
        oo = oos_r2(np.asarray(dd["X"]), y, dates, c["W"]); sub = oo if c["era"] == "all" else oo[oo.era == c["era"]]
        return (float(sub["r2"].median()) if len(sub) >= 10 else np.nan), len(sub)
    def null_gen(dd, rng):
        Xn = np.asarray(dd["X"]); s = int(rng.integers(250, len(Xn) - 250)); return dict(X=np.roll(Xn, s, axis=0))
    sw = run(cells, stat, dict(X=X), null_gen, n_null=a.n_null, seed=0, label=f"T-A by era × window — median out-of-sample R² ({a.asset})")
    # the episode re-attributed with each era's betas
    ep = None
    if a.episode_start or True:
        cum = np.cumsum(y); end_i = len(y) - 1 if not a.episode_end else int(dates.searchsorted(pd.Timestamp(a.episode_end)))
        if a.episode_start: s_i = int(dates.searchsorted(pd.Timestamp(a.episode_start)))
        else: lo = max(0, end_i - 300); s_i = lo + int(np.argmax(cum[lo:end_i + 1]))          # the peak of the prior 300 sessions
        move = float(cum[end_i] - cum[s_i]); dF = X[s_i + 1:end_i + 1].sum(0)
        sets = {"pre-episode 504": (max(0, s_i - 504), s_i), "2009-21": (int(dates.searchsorted(pd.Timestamp("2009-01-01"))), int(dates.searchsorted(pd.Timestamp("2022-01-01")))),
                "2022-start": (int(dates.searchsorted(pd.Timestamp("2022-01-01"))), s_i), "all": (0, len(y))}
        ep = dict(start=str(dates[s_i].date()), end=str(dates[end_i].date()), move_log=move, attributions={})
        for k, (lo, hi) in sets.items():
            if hi - lo < 250: continue
            b, _, _ = fit(X[lo:hi], y[lo:hi]); contrib = b * dF; expl = float(contrib.sum())
            ep["attributions"][k] = dict(window=(str(dates[lo].date()), str(dates[min(hi, len(y)) - 1].date())), explained_log=expl, explained_share=float(expl / move) if move else np.nan,
                                         by_factor={n: float(v) for n, v in zip(names, contrib)})
    tag = a.asset + ("_full" if drop else ""); out = DOCS / f"era_factors_{tag}.md"
    L = [f"# Factor sensitivities by era — {a.asset} ({dates[0].date()} → {dates[-1].date()}, {len(names)} reasons" + (f"; dropped {sorted(drop)}" if drop else "") + ")", "",
         "Joint OLS per era (no ordering: the question is whether the sensitivities moved, not how to split shared variance). `r2` is in-sample within the era.", "",
         "| era | n | R² | " + " | ".join(names) + " |", "|---|---|---|" + "---|" * len(names)]
    for _, r_ in tab.iterrows(): L.append(f"| {r_['era']} | {r_['n']} | {r_['r2']:.3f} | " + " | ".join(f"{r_[k]:+.4f}" for k in names) + " |")
    L += ["", "Sign agreement with the pooled beta (✓ same sign):", "", "| era | " + " | ".join(names) + " |", "|---|" + "---|" * len(names)]
    for e_, row in signs.iterrows(): L.append(f"| {e_} | " + " | ".join("✓" if v else "✗" for v in row) + " |")
    L += ["", f"## T-A by era × window (median out-of-sample R², blocks of {BLOCK} sessions)", "",
          f"Best `{sw.best}` = {sw.best_stat:.3f}; best-of-sweep null (factors time-shifted together) q95 {sw.q95:.3f}; p_family {sw.p_family:.3f}. Surface in `era_factors_{tag}_sweep.md`.", ""]
    if ep:
        L += [f"## The current episode re-attributed: {ep['start']} → {ep['end']}, move {ep['move_log'] * 100:+.1f}% (log)", "",
              "| betas from | window | explained (log %) | explained share | largest contributions |", "|---|---|---|---|---|"]
        for k, v in ep["attributions"].items():
            top = sorted(v["by_factor"].items(), key=lambda kv: -abs(kv[1]))[:3]
            L.append(f"| {k} | {v['window'][0]} → {v['window'][1]} | {v['explained_log'] * 100:+.2f} | {v['explained_share']:+.2f} | " + ", ".join(f"{n} {c * 100:+.2f}" for n, c in top) + " |")
        L += ["", "If the 2022→ betas explain much more of the episode than the 2009–21 betas, the sensitivities changed (a habit); if neither explains it, the move sits outside the named reasons in every era (T-A's reading of 23 Oct)."]
    out.write_text("\n".join(L) + "\n"); write_md(sw, DOCS / f"era_factors_{tag}_sweep.md", axis_rows="era", axis_cols="W", fmt="{:.3f}")
    out.with_suffix(".json").write_text(json.dumps(dict(eras=json.loads(tab.to_json(orient="records")), signs=json.loads(signs.astype(int).to_json()), sweep=sw.to_json(), episode=ep), indent=1, default=float))
    print(tab[["era", "n", "r2"]].to_string(index=False)); print(f"T-A sweep: best {sw.best} {sw.best_stat:.3f}, q95 {sw.q95:.3f}, p_family {sw.p_family:.3f}")
    if ep: print("episode:", {k: round(v["explained_share"], 2) for k, v in ep["attributions"].items()})
    print(f"-> {out}")


if __name__ == "__main__":
    main()
