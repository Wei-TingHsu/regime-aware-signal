"""daytype.py -- the day-type layer (docs/prereg_regime_audit.md section 3): each session typed by the signs of five same-day moves
(2-yr yield, 10-yr yield, gold, S&P, dollar), 32 patterns; the founder's case = 2y down, 10y up, gold up.

  python -m src.daytype counts     # Y1: pattern counts, by era; the founder's pattern highlighted
  python -m src.daytype turning    # Y2: pattern frequency in the 60 sessions before a regime change vs elsewhere; change dates shifted at random; family null
  python -m src.daytype forward    # Y3: next 5/10/20 sessions per pattern x asset, net Sharpe, best-of-search null (returns time-shifted)
  python -m src.daytype conditioner --csv processed/report_backfill_<tag>.csv   # Y4: the report's call hit-rate on each day-type vs its null
  python -m src.daytype all
Outputs docs/daytype_<part>.md (+ .json). Nothing here writes the register.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.sweep import grid, run, write_md, shift_null
from src.deeper import returns, macro, path_stats, fwd, era_of, COST, MIN_N, ERAS

PROC, DOCS = Path("processed"), Path("docs")
FLAT = 0.25                    # |move| under 0.25 trailing-60 sd = flat (no sign)
ASSETS = ["SPY", "TLT", "GLD", "UUP", "USO"]
FOUNDER = dict(dgs2=-1, dgs10=+1, gld=+1)      # the founder's case: front end rallies, long end sells off, gold up


def build() -> pd.DataFrame:
    r = returns(); m = macro()
    if m is None or not {"DGS2", "DGS10"} <= set(m.columns): raise SystemExit("macro_panel.parquet needs DGS2 and DGS10")
    d = pd.DataFrame(dict(dgs2=m["DGS2"].reindex(r.index).ffill().diff(), dgs10=m["DGS10"].reindex(r.index).ffill().diff(), gld=r["GLD"], spy=r["SPY"], uup=r["UUP"] if "UUP" in r.columns else np.nan)).dropna()
    for c in ("dgs2", "dgs10", "gld", "spy", "uup"):
        sd = d[c].rolling(60).std(); d[f"s_{c}"] = np.where(d[c] > FLAT * sd, 1, np.where(d[c] < -FLAT * sd, -1, 0))
    d = d.dropna(); d["type"] = ["".join({1: "+", -1: "-", 0: "0"}[int(d.loc[i, f"s_{c}"])] for c in ("dgs2", "dgs10", "gld", "spy", "uup")) for i in d.index]
    d["founder"] = (d.s_dgs2 == FOUNDER["dgs2"]) & (d.s_dgs10 == FOUNDER["dgs10"]) & (d.s_gld == FOUNDER["gld"])
    d["era"] = [era_of(t) for t in d.index]
    return d


def cmd_counts(d):
    tab = d.groupby(["type", "era"]).size().unstack(fill_value=0); tab["all"] = tab.sum(1); tab = tab.sort_values("all", ascending=False)
    f = d[d.founder]; out = DOCS / "daytype_counts.md"
    L = ["# Y1 — day-type counts (signs of 2y, 10y, gold, S&P, dollar; 0 = flat)", "", f"{len(d):,} typed sessions {d.index[0].date()} → {d.index[-1].date()}; {d.type.nunique()} distinct patterns occur.", "",
         f"**The founder's pattern** (2y ↓, 10y ↑, gold ↑, any S&P / dollar): {len(f)} sessions — by era: " + ", ".join(f"{e} {int((f.era == e).sum())}" for e in [x[0] for x in ERAS]) + ".", "",
         "| type (2y 10y gold SPX USD) | " + " | ".join(tab.columns.astype(str)) + " |", "|---|" + "---|" * len(tab.columns)]
    for t, row in tab.head(40).iterrows(): L.append(f"| `{t}` | " + " | ".join(str(int(v)) for v in row) + " |")
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(tab.to_json(indent=1)); print(f"founder's pattern: {len(f)} sessions; top types: {list(tab.index[:5])}"); print(f"-> {out}")


def _labels(d):
    try:
        import src.exposure_dial as ED
        idx, rets, lab, post, rf = ED.load_inputs(); return pd.Series(np.asarray(lab), index=pd.DatetimeIndex(idx)).reindex(d.index).ffill().to_numpy()
    except Exception as e:
        print(f"  regime labels unavailable ({type(e).__name__}: {e})"); return None


def cmd_turning(d):
    lab = _labels(d)
    if lab is None: return
    ch = np.where((lab[1:] != lab[:-1]) & (lab[1:] >= 0) & (lab[:-1] >= 0))[0] + 1; n = len(d)
    def pre_mask(changes):
        m = np.zeros(n, bool)
        for c in changes: m[max(0, c - 60):c] = True
        return m
    types = sorted(d.type.unique()); T = d.type.to_numpy(); pre = pre_mask(ch)
    def excess(mask):
        return {t: (T[mask] == t).mean() - (T[~mask] == t).mean() for t in types}
    obs = excess(pre); rng = np.random.default_rng(0); null_max = []
    for _ in range(500):
        s = int(rng.integers(60, n - 60)); ex = excess(pre_mask((ch + s) % n)); null_max.append(max(abs(v) for v in ex.values()))
    q95 = float(np.quantile(null_max, 0.95)); best = max(obs, key=lambda t: abs(obs[t])); p_family = float((np.array(null_max) >= abs(obs[best])).mean())
    out = DOCS / "daytype_turning.md"
    L = ["# Y2 — do day-types cluster in the 60 sessions before a regime change?", "", f"{len(ch)} live regime changes; pre-change windows cover {pre.mean():.0%} of sessions.", "",
         f"Largest excess frequency: `{best}` {obs[best] * 100:+.2f} points; best-of-32 null 95th percentile {q95 * 100:.2f}; **p_family {p_family:.3f}**. Founder's pattern excess: {(d.founder.to_numpy()[pre].mean() - d.founder.to_numpy()[~pre].mean()) * 100:+.2f} points.", "",
         "| type | share pre-change | share elsewhere | excess (pts) |", "|---|---|---|---|"]
    for t in sorted(types, key=lambda t: -abs(obs[t]))[:15]: L.append(f"| `{t}` | {(T[pre] == t).mean():.1%} | {(T[~pre] == t).mean():.1%} | {obs[t] * 100:+.2f} |")
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(json.dumps(dict(best=best, excess=obs[best], q95=q95, p_family=p_family, changes=int(len(ch))), indent=1)); print(f"Y2: best `{best}` {obs[best] * 100:+.2f} pts vs q95 {q95 * 100:.2f}, p_family {p_family:.3f} -> {out}")


def cmd_forward(d):
    r = returns().reindex(d.index); assets = [a for a in ASSETS if a in r.columns]; T = d.type.to_numpy(); n = len(d)
    types = [t for t in d.type.unique() if (T == t).sum() >= MIN_N] + ["FOUNDER"]
    data = {a: np.nan_to_num(r[a].to_numpy()) for a in assets}
    def stat(dd, c):
        g = np.asarray(dd[c["asset"]]); cum = np.concatenate([[0], np.cumsum(g)]); ev = np.where(d.founder.to_numpy())[0] if c["type"] == "FOUNDER" else np.where(T == c["type"])[0]
        ev = ev[ev < n - c["h"] - 1]; f = fwd(cum, ev, c["h"]); ps = path_stats(f, c["h"], COST, c["sign"]); return ps["sharpe"], ps["n"]
    cells = grid(type=types, asset=assets, h=[5, 10, 20], sign=[1, -1])
    def null_gen(dd, rng):
        out = {}
        for a, g in dd.items(): s = int(rng.integers(250, len(g) - 250)); out[a] = np.roll(g, s)
        return out
    sw = run(cells, stat, data, null_gen, n_null=200, seed=0, label="Y3 day-type → next 5/10/20 sessions, every asset, both directions — net Sharpe", meta=dict(tag="sweep", rows="type", cols="h"))
    fr = sw.surface[sw.surface.type == "FOUNDER"].sort_values("stat", ascending=False).head(6)
    out = DOCS / "daytype_forward.md"
    L = ["# Y3 — does a day-type predict the next sessions?", "", f"{len(types) - 1} patterns with ≥ {MIN_N} occurrences plus the founder's pattern; {len(cells)} cells.", "",
         f"Best `{sw.best}`: net Sharpe {sw.best_stat:+.2f}; best-of-search null q95 {sw.q95:+.2f}; **p_family {sw.p_family:.3f}**; survivors {len(sw.survivors)}.", "",
         "## The founder's pattern (2y ↓, 10y ↑, gold ↑), strongest cells", "", "| asset | h | direction | net Sharpe | n |", "|---|---|---|---|---|"]
    for _, r_ in fr.iterrows(): L.append(f"| {r_['asset']} | {r_['h']} | {'long' if r_['sign'] == 1 else 'short'} | {r_['stat']:+.2f} | {int(r_['n'])} |" if np.isfinite(r_["stat"]) else f"| {r_['asset']} | {r_['h']} | {'long' if r_['sign'] == 1 else 'short'} | · | {int(r_['n'])} |")
    out.write_text("\n".join(L) + "\n"); write_md(sw, DOCS / "daytype_forward_sweep.md", fmt="{:+.2f}"); out.with_suffix(".json").write_text(json.dumps(sw.to_json(), indent=1, default=float))
    print(f"Y3: best {sw.best} {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}, survivors {len(sw.survivors)} -> {out}")


def cmd_conditioner(d, csv):
    df = pd.read_csv(csv); df["date"] = pd.to_datetime(df["date"]); df = df[(df.h == 2) & (df.kind == "call")].dropna(subset=["call", "ret_primary"])
    df["type"] = d["type"].reindex(df["date"]).to_numpy(); df["hit"] = (np.sign(df.call) == np.sign(df.ret_primary)) & (df.ret_primary != 0); df = df.dropna(subset=["type"])
    rng = np.random.default_rng(0); rows = []; types = [t for t, g in df.groupby("type") if len(g) >= MIN_N]
    for t in types:
        sub = df[df.type == t]; obs = float(sub.hit.mean()); null = []
        for _ in range(300):
            c2 = df.call.to_numpy().copy(); rng.shuffle(c2); h2 = (np.sign(c2) == np.sign(df.ret_primary.to_numpy())) & (df.ret_primary.to_numpy() != 0); null.append(h2[(df.type == t).to_numpy()].mean())
        rows.append(dict(type=t, n=len(sub), hit=obs, q95=float(np.quantile(null, 0.95)), p=float((np.array(null) >= obs).mean())))
    tab = pd.DataFrame(rows).sort_values("hit", ascending=False); out = DOCS / "daytype_conditioner.md"
    L = ["# Y4 — the report's calls by day-type", "", f"{len(df):,} calls; types with ≥ {MIN_N} calls. Null: call signs shuffled.", "", "| type | n | hit-rate | null q95 | p |", "|---|---|---|---|---|"] + [f"| `{r['type']}` | {r['n']} | {r['hit']:.1%} | {r['q95']:.1%} | {r['p']:.3f} |" for _, r in tab.iterrows()]
    L += ["", f"Types beating their null: {int((tab.hit > tab.q95).sum())} of {len(tab)} (≈ {0.05 * len(tab):.1f} expected by chance)."]
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(tab.to_json(orient="records", indent=1)); print(tab.head(8).to_string(index=False)); print(f"-> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["counts", "turning", "forward", "conditioner", "all"]); ap.add_argument("--csv", default="processed/report_backfill_97d9bf07dd2c_n5793.csv")
    a = ap.parse_args(); DOCS.mkdir(exist_ok=True); d = build()
    for c in (["counts", "turning", "forward", "conditioner"] if a.cmd == "all" else [a.cmd]):
        try:
            {"counts": lambda: cmd_counts(d), "turning": lambda: cmd_turning(d), "forward": lambda: cmd_forward(d), "conditioner": lambda: cmd_conditioner(d, a.csv)}[c]()
        except Exception as e:
            print(f"{c}: did not run -- {type(e).__name__}: {e}")
            if a.cmd != "all": raise
