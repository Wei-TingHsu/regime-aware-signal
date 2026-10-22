"""19 Oct: PROJECT_MASTER register row 45 (H-programme) and src/history_tables.py with the shared engine + H0 (regime return table).
Run from the repo root:  python h0_setup.py ; python -m src.history_tables selftest ; python -m src.history_tables h0"""
from pathlib import Path
import sys

m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "| 45 | History tables" in s: print("  MASTER row 45: already")
else:
    i = s.index("| 44 | Inverse rule"); j = s.index("\n", i) + 1
    row = ("| 45 | History tables H0–H7: conditional path tables (Fed days, prints, dollar/rate shocks, regime changes, drawdown entries, vol spikes, "
           "today's regime) feed the app's Context block as `measured`; one uniform test per table (20-session sign share vs base rate ≥ 15 pts, n ≥ 30, "
           "random-date null p < 0.05) | registered 19 Oct before code; build H0, H1, H3, H4, H5 first | priors #49–#53: all tests FAIL, tables informative "
           "| `docs/prereg_history_tables.md`, TRACK 3.25 |\n")
    m.write_text(s[:j] + row + s[j:]); print("  MASTER row 45: done")

h = Path("src/history_tables.py")
if h.exists(): print("  history_tables.py: already")
else:
    h.write_text(r'''"""
History tables H0–H7 (prereg_history_tables.md, TRACK 3.25). Shared engine: event dates -> forward paths per market -> medians, IQR, n;
one uniform conditional test (20-session sign share vs the market's base rate, >= 15 pts, n >= 30, random-date null p < 0.05).
Outputs: docs/history_<id>.md (table) and processed/history_tables.json (what the app reads). Values stored as log returns; the app shows simple %.

  python -m src.history_tables selftest
  python -m src.history_tables h0          # today's-regime return table (measured only, no test)
"""
from __future__ import annotations
import json, sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.oil_shock import load, regime_labels, ASSETS  # same price panel, same labels as A3

PROC, DOCS = Path("processed"), Path("docs")
H = (5, 10, 20, 40, 60)
GAP, HOLD = 20, 60
GAP_PTS, MIN_N, N_NULL, ALPHA = 0.15, 30, 10000, 0.05
OUT = PROC / "history_tables.json"


# ---------------------------------------------------------------- engine
def paths(r: pd.Series, pos: int) -> dict:
    """Forward log returns of one market after index position pos (NaN-aware; needs HOLD sessions)."""
    seg = r.iloc[pos + 1:pos + HOLD + 1]
    if len(seg) < HOLD or seg.isna().any(): return {}
    cum = seg.cumsum().to_numpy()
    d = {f"f{h}": float(cum[h - 1]) for h in H}
    d["worst"], d["worst_t"] = float(min(cum.min(), 0)), int(cum.argmin()) + 1
    d["best"], d["best_t"] = float(max(cum.max(), 0)), int(cum.argmax()) + 1
    return d


def collapse(idx: pd.DatetimeIndex, events: list) -> list:
    """Events within GAP sessions of the previous kept event are dropped (prereg §1)."""
    pos, keep, last = [], [], -10 ** 9
    for d in sorted(events):
        p = idx.searchsorted(pd.Timestamp(d))
        if p >= len(idx) or p - last < GAP: continue
        keep.append(idx[p]); last = p
    return keep


def summarise(rows: pd.DataFrame) -> dict:
    if rows.empty: return {"n": 0}
    out = {"n": int(len(rows))}
    for c in [f"f{h}" for h in H] + ["worst", "best"]:
        out[c] = float(rows[c].median()); out[c + "_q25"], out[c + "_q75"] = float(rows[c].quantile(.25)), float(rows[c].quantile(.75))
    out["worst_t"], out["best_t"] = float(rows.worst_t.median()), float(rows.best_t.median())
    out["sign20"] = float((rows.f20 > 0).mean())
    return out


def base_rate(r: pd.Series) -> tuple[float, np.ndarray]:
    """Unconditional 20-session sign share and the array of all 20-session forward returns (for the null)."""
    f20 = r.rolling(20).sum().shift(-20).dropna()
    return float((f20 > 0).mean()), f20.to_numpy()


def cond_test(rows: pd.DataFrame, r: pd.Series, seed=0) -> dict:
    """Prereg §1: sign share after events vs base rate, >= GAP_PTS, n >= MIN_N, random-date null p < ALPHA."""
    n = len(rows)
    if n < MIN_N: return {"verdict": "INCONCLUSIVE", "n": n, "reason": f"n < {MIN_N}"}
    br, allf = base_rate(r); obs = float((rows.f20 > 0).mean()); gap = obs - br
    rng = np.random.default_rng(seed)
    null = np.array([(rng.choice(allf, n, replace=False) > 0).mean() - br for _ in range(N_NULL)])
    p = float((np.abs(null) >= abs(gap)).mean())
    return {"verdict": "PASS" if (abs(gap) >= GAP_PTS and p < ALPHA) else "FAIL", "n": n, "sign20": obs, "base": br, "gap": gap, "p": p}


# ---------------------------------------------------------------- H0
def h0() -> dict:
    """Each market's 20/60-session forward return inside each regime label vs all history. Measured only (prereg: no test)."""
    lo = load(); rets = lo[0] if isinstance(lo, tuple) else lo
    lab = regime_labels(rets.index)
    res = {"id": "H0", "run": datetime.now().strftime("%Y-%m-%d %H:%M"), "markets": {}}
    L = ["# H0 — what each market did inside each regime (measured, no test)", "",
         f"*{res['run']}. Forward 20- and 60-session returns, simple %, median [IQR], sessions counted. The regime label is the engine's own input; "
         "prereg_history_tables §2: measured only, no claim. Label 'all' is the unconditional row for comparison.*", ""]
    for a in [x for x in ASSETS if x in rets.columns]:
        r = rets[a]; f20, f60 = r.rolling(20).sum().shift(-20), r.rolling(60).sum().shift(-60)
        d = pd.DataFrame({"f20": f20, "f60": f60, "lab": lab}).dropna()
        tab = {}
        for k, g in [("all", d)] + [(str(int(k)), g) for k, g in d.groupby("lab")]:
            tab[k] = {"n": int(len(g)), "f20": float(g.f20.median()), "f20_q25": float(g.f20.quantile(.25)), "f20_q75": float(g.f20.quantile(.75)),
                      "f60": float(g.f60.median()), "sign20": float((g.f20 > 0).mean())}
        res["markets"][a] = tab
        L += [f"## {a}", "", "| regime | sessions | 20-session median [IQR] | share positive at 20 | 60-session median |", "|---|---|---|---|---|"]
        for k, v in tab.items():
            pc = lambda x: f"{np.expm1(x):+.1%}"
            L.append(f"| {k} | {v['n']:,} | {pc(v['f20'])} [{pc(v['f20_q25'])}, {pc(v['f20_q75'])}] | {v['sign20']:.0%} | {pc(v['f60'])} |")
        L.append("")
    allj = json.loads(OUT.read_text()) if OUT.exists() else {}
    allj["H0"] = res; OUT.write_text(json.dumps(allj, indent=1))
    (DOCS / "history_H0.md").write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {DOCS/'history_H0.md'}, {OUT}")
    return res


# ---------------------------------------------------------------- selftest
def selftest():
    idx = pd.bdate_range("2000-01-03", periods=400); r = pd.Series(0.0, index=idx); r.iloc[101:121] = 0.01
    p = paths(r, 100); assert abs(p["f20"] - 0.20) < 1e-9 and p["best_t"] >= 20; print("  T1 paths: PASS")
    ev = collapse(idx, [idx[10], idx[15], idx[40]]); assert len(ev) == 2; print("  T2 collapse GAP: PASS")
    rng = np.random.default_rng(1); rr = pd.Series(rng.normal(0, 0.01, 3000), index=pd.bdate_range("1995-01-02", periods=3000))
    rows = pd.DataFrame([paths(rr, p) for p in range(100, 2900, 60)]); t = cond_test(rows, rr); assert t["verdict"] == "FAIL", t; print("  T3 null data -> FAIL: PASS")
    rr2 = rr.copy(); pos = list(range(100, 2900, 60))
    for p in pos: rr2.iloc[p + 1:p + 21] += 0.004
    rows = pd.DataFrame([paths(rr2, p) for p in pos]); t = cond_test(rows, rr2); assert t["verdict"] == "PASS", t; print("  T4 planted effect -> PASS: PASS")
    print("selftest: 4/4")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    {"selftest": selftest, "h0": h0}[cmd]()
''')
    print("  history_tables.py: written (engine + H0)")
print("done -- python -m src.history_tables selftest ; python -m src.history_tables h0")
