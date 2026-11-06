"""deeper2.py -- the founder's redesigns of 5 Nov evening (docs/prereg_deeper_signals.md section 2b), same recipe and engine as deeper.py.

  python -m src.deeper2 sudden      # D1b a SUDDEN sell-off: SPY down x% in ONE session and gold down y% the same session; what SPY and gold do over
                                    #    the next 1/2/3/5/10 sessions (continuation or reversal, each asset), grid x in {1.5..4}%, y in {0.5..2}%
  python -m src.deeper2 regimes     # D2b the liquidity-gold link inside each engine regime (oil_shock.regime_labels): beta, t, n per regime, the
                                    #    regime x liquidity interaction with a permutation p; the standing question 'when the regime returns, so does the link?'
  python -m src.deeper2 daily       # D2c the link traded DAILY: the daily component of net liquidity (overnight reverse repo, published same day) -> gold's
                                    #    next 1/2/5/10 sessions; weekly WALCL/TGA interpolated and flagged; grid horizon x regime x sign rule
  python -m src.deeper2 combo       # D8 which combination of factors explains and predicts gold: every subset of up to 3 factors (plus all) as a walk-forward
                                    #    ridge on trailing 1/5/20-session factor changes -> gold's next h sessions; the best combination is the 'index'
  python -m src.deeper2 oilchain    # D5b the founder's chain: oil shock -> rate expectations / real yields up -> gold down; each link measured and gold
                                    #    conditioned on whether rates actually rose after the shock
  python -m src.deeper2 all
Outputs docs/deeper2_<test>.md (+ _sweep.md, .json). Nothing here writes the register.
"""
from __future__ import annotations

import argparse
import itertools
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from src.sweep import grid, run, write_md, shift_null
from src.deeper import returns, macro, path_stats, fwd, era_of, COST, MIN_N, N_NULL, ERAS

PROC, DOCS = Path("processed"), Path("docs")


def _finish(name, sws, head, extra=None):
    out = DOCS / f"deeper2_{name}.md"; L = [f"# Deeper test {name} — {datetime.now():%Y-%m-%d %H:%M}", ""] + head + [""]
    for sw in sws:
        b = sw.surface.loc[sw.surface["stat"].idxmax()] if sw.surface["stat"].notna().any() else None
        L += [f"## {sw.label}", "", f"Best cell `{sw.best}`: statistic {sw.best_stat:+.2f} on n = {int(b['n']) if b is not None else 0}; null 95th percentile {sw.q95:+.2f}; **p_family = {sw.p_family:.3f}**; survivors {len(sw.survivors)}.", ""]
        write_md(sw, DOCS / f"deeper2_{name}_{sw.meta.get('tag', 'sweep')}.md", axis_rows=sw.meta.get("rows"), axis_cols=sw.meta.get("cols"), fmt="{:+.2f}")
    if extra: L += extra
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(json.dumps([sw.to_json() for sw in sws], indent=1, default=float)); print(f"-> {out}")


def regime_labels(idx: pd.DatetimeIndex) -> np.ndarray | None:
    try:
        from src.oil_shock import regime_labels as rl
        lab = np.asarray(rl(idx)); return lab if len(lab) == len(idx) else None
    except Exception as e:
        print(f"  regime labels unavailable ({type(e).__name__}: {e}) -- regime axis skipped"); return None


# ================================================================================================ D1b sudden sell-off
def cmd_sudden():
    r = returns(); d = pd.DataFrame(dict(spy=r["SPY"], gld=r["GLD"])).dropna(); spy, gld = d["spy"].to_numpy(), d["gld"].to_numpy(); n = len(d)
    cs, cg = np.concatenate([[0], np.cumsum(spy)]), np.concatenate([[0], np.cumsum(gld)])
    def ev(x, y):
        return np.where((spy <= -x) & (gld <= -y))[0] if y > 0 else np.where(spy <= -x)[0]
    def stat_factory(asset, sign):
        def stat(dd, c):
            e = ev(c["spy_down"], c["gold_down"]); e = e[e < n - c["h"] - 1]
            if c["era"] != "all": e = e[np.array([era_of(t) for t in d.index[e]]) == c["era"]] if len(e) else e
            cum = np.concatenate([[0], np.cumsum(np.asarray(dd[asset]))]); f = fwd(cum, e, c["h"]); ps = path_stats(f, c["h"], COST, sign); return ps["sharpe"], ps["n"]
        return stat
    cells = grid(spy_down=[0.015, 0.02, 0.025, 0.03, 0.04], gold_down=[0.0, 0.005, 0.01, 0.015, 0.02], h=[1, 2, 3, 5, 10], era=["all"] + [e[0] for e in ERAS])
    sws = []
    for asset, sign, name in (("gld", 1, "gold continues DOWN (short gold)"), ("gld", -1, "gold REVERSES up (long gold)"), ("spy", 1, "S&P continues down (short)"), ("spy", -1, "S&P reverses (long)")):
        # sign convention: path_stats(sign=+1) is long; we want 'continues down' = short -> sign -1, 'reverses up' = long -> +1
        sg = -1 if sign == 1 else 1
        sw = run(cells, stat_factory(asset, sg), dict(gld=gld, spy=spy), shift_null(asset, 250), n_null=N_NULL, seed=0, label=f"D1b after a one-day sell-off: {name} — net Sharpe", meta=dict(tag=f"{asset}_{'cont' if sign == 1 else 'rev'}", rows="spy_down", cols="h"))
        sws.append(sw); print(f"D1b {name}: best {sw.best} {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}, survivors {len(sw.survivors)}")
    cnt = {(x, y): len(ev(x, y)) for x in (0.015, 0.02, 0.03, 0.04) for y in (0.0, 0.01, 0.02)}
    extra = ["## Event counts (SPY down ≥ x the same day as gold down ≥ y)", "", "| SPY down | gold any | gold ≥ 1% | gold ≥ 2% |", "|---|---|---|---|"] + [f"| {x:.1%} | {cnt[(x, 0.0)]} | {cnt[(x, 0.01)]} | {cnt[(x, 0.02)]} |" for x in (0.015, 0.02, 0.03, 0.04)]
    _finish("sudden", sws, [f"{n:,} sessions {d.index[0].date()} → {d.index[-1].date()}; a sell-off is ONE session; 'gold_down 0' = no gold condition; cells under {MIN_N} events ·."], extra)


# ================================================================================================ D2b the link by regime
def cmd_regimes():
    from src.liquidity_link import weekly_pair
    df, nl, r = weekly_pair("GLD"); lab = regime_labels(r.index)
    if lab is None: return
    reg = pd.Series(lab, index=r.index).resample("W-WED").last().reindex(df.index).ffill(); df = df.assign(regime=reg.astype("Int64").astype(str))
    rows = []
    for g, sub in df.groupby("regime"):
        x, y = sub["x"].to_numpy(), sub["y"].to_numpy()
        if len(x) < 30: rows.append(dict(regime=g, n=len(x), beta=np.nan, t=np.nan, r2=np.nan)); continue
        xm, ym = x.mean(), y.mean(); sxx = ((x - xm) ** 2).sum(); b = ((x - xm) * (y - ym)).sum() / sxx; e = y - ym - b * (x - xm); se = np.sqrt((e @ e) / (len(x) - 2) / sxx)
        rows.append(dict(regime=g, n=len(x), beta=float(b), t=float(b / se), r2=float(1 - (e @ e) / ((y - ym) ** 2).sum())))
    tab = pd.DataFrame(rows)
    # interaction: does the slope differ by regime? permutation of regime labels in blocks of 13 weeks
    from src.chair_power import interaction_F
    labs = df["regime"].to_numpy(); F = interaction_F(df.rename(columns={"y": "gld", "x": "s"}), "gld", labs, "s"); rng = np.random.default_rng(0); null = []
    nb = 13
    for _ in range(1000):
        starts = np.arange(0, len(labs), nb); order = rng.permutation(len(starts)); idx = np.concatenate([np.arange(s_, min(s_ + nb, len(labs))) for s_ in starts[order]])
        null.append(interaction_F(df.rename(columns={"y": "gld", "x": "s"}), "gld", labs[idx], "s"))
    p = float((np.array(null) >= F).mean())
    out = DOCS / "deeper2_regimes.md"
    L = ["# D2b — the liquidity–gold link inside each engine regime", "", f"{len(df)} weeks; regime = the engine's label on the week's Wednesday.", "",
         "| regime | weeks | β | t | R² |", "|---|---|---|---|---|"] + [f"| {r_['regime']} | {r_['n']} | {r_['beta']:+.3f} | {r_['t']:+.2f} | {r_['r2']:.3f} |" if np.isfinite(r_["beta"]) else f"| {r_['regime']} | {r_['n']} | · | · | · |" for _, r_ in tab.iterrows()]
    L += ["", f"Regime × liquidity interaction F {F:.2f}, block-permutation p **{p:.3f}** (1,000 draws, blocks of 13 weeks). If p < 0.05 the link depends on the regime and the standing rule applies: when the engine labels the same regime again, the link is expected with that regime's β — stated as an expectation and logged forward, not as a signal.", ""]
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(json.dumps(dict(table=json.loads(tab.to_json(orient="records")), F=F, p=p), indent=1)); print(tab.to_string(index=False)); print(f"interaction p {p:.3f} -> {out}")


# ================================================================================================ D2c daily liquidity
def cmd_daily():
    from src.liquidity_link import fred
    rrp = fred("RRPONTSYD"); walcl = fred("WALCL"); tga = fred("WTREGEN")
    if rrp is None: print("D2c: no RRPONTSYD series -- skipped"); return
    r = returns(); g = r["GLD"].dropna(); idx = g.index
    rrp = pd.to_numeric(rrp, errors="coerce"); rrp = (rrp / 1000 if rrp.dropna().median() > 50_000 else rrp).reindex(idx).ffill()
    d = pd.DataFrame(dict(gld=g, d_rrp=-rrp.diff()))                # money leaving the RRP facility = liquidity ADDED (sign flipped)
    if walcl is not None and tga is not None:
        w = pd.to_numeric(walcl, errors="coerce"); w = (w / 1000 if w.dropna().median() > 50_000 else w); t = pd.to_numeric(tga, errors="coerce"); t = (t / 1000 if t.dropna().median() > 50_000 else t)
        nl_weekly = (w - t).dropna(); d["d_nl_interp"] = nl_weekly.reindex(idx).interpolate(limit_area="inside").diff()      # weekly series spread evenly: an approximation, flagged
    d = d.dropna(subset=["gld", "d_rrp"]); d = d[d.index >= "2013-09-23"]      # RRP facility starts Sept 2013
    lab = regime_labels(d.index); d["regime"] = lab.astype(str) if lab is not None else "all"
    gld = d["gld"].to_numpy(); n = len(d)
    def stat(dd, c):
        gl = np.asarray(dd["gld"]); drv = d[c["driver"]].to_numpy() if c["driver"] in d.columns else None
        if drv is None: return np.nan, 0
        z = (drv - pd.Series(drv).rolling(60).mean().to_numpy()) / pd.Series(drv).rolling(60).std().to_numpy()
        sig = np.sign(z) * (np.abs(z) > c["bar"]); m = np.isfinite(sig) & (np.abs(sig) > 0)
        if c["regime"] != "all": m &= d["regime"].to_numpy() == c["regime"]
        starts = np.where(m)[0]; starts = starts[starts < n - c["h"] - 1]
        cum = np.concatenate([[0], np.cumsum(gl)]); f = fwd(cum, starts, c["h"]) * sig[starts][: len(fwd(cum, starts, c["h"]))] * c["dir"]
        ps = path_stats(f, c["h"], COST, 1); return ps["sharpe"], ps["n"]
    drivers = ["d_rrp"] + (["d_nl_interp"] if "d_nl_interp" in d.columns else [])
    cells = grid(driver=drivers, bar=[0.5, 1.0, 1.5], h=[1, 2, 5, 10], dir=[1, -1], regime=["all"] + (sorted(d["regime"].unique()) if lab is not None else []))
    sw = run(cells, stat, dict(gld=gld), shift_null("gld", 250), n_null=N_NULL, seed=0, label="D2c gold's next sessions after a daily liquidity change (RRP same-day; weekly NL interpolated) — net Sharpe, dir +1 = buy gold when liquidity is added", meta=dict(tag="sweep", rows="bar", cols="h"))
    print(f"D2c: best {sw.best} {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}")
    _finish("daily", [sw], [f"{n:,} sessions from {d.index[0].date()} (the RRP facility's start); the daily driver is the overnight reverse-repo balance (published the same evening); `d_nl_interp` spreads the Wednesday balance-sheet change evenly over the week and is an approximation, not a tradeable series."])


# ================================================================================================ D8 factor combinations as a predictive index
def cmd_combo():
    from src.factor_attribution import factors, returns as fret
    r = fret("GLD"); r.index = pd.to_datetime(r.index); F = factors(r.index); F.index = pd.to_datetime(F.index)
    d = pd.concat([r.rename("y"), F], axis=1).dropna(); names = [c for c in d.columns if c != "y"]; n = len(d)
    feats = {}
    for k in names:
        for w in (1, 5, 20): feats[f"{k}_{w}"] = d[k].rolling(w).sum().to_numpy()
    X_all = pd.DataFrame(feats, index=d.index); y = d["y"].to_numpy(); cum = np.concatenate([[0], np.cumsum(y)])
    combos = [("all",)] + [c for k in (1, 2, 3) for c in itertools.combinations(names, k)]
    print(f"D8: {len(names)} factors -> {len(combos)} combinations; {n:,} sessions")
    def stat(dd, c):
        H = c["h"]; yy = np.asarray(dd["y"]); cm = np.concatenate([[0], np.cumsum(yy)]); tgt = cm[H:] - cm[:-H]            # next-H return starting tomorrow
        cols = [f"{k}_{w}" for k in (names if c["combo"] == ("all",) else c["combo"]) for w in (1, 5, 20)]
        X = X_all[cols].to_numpy(); X = np.column_stack([X, np.ones(n)])
        ok = np.all(np.isfinite(X), axis=1); ok[-H - 1:] = False; ii = np.where(ok)[0]; pnl = []
        for s in range(max(1000, ii[0] + 1000), len(ii), 250):
            tr = ii[max(0, s - c["train"]):s]; te = ii[s:s + 250]; tr = tr[tr + H + 1 < te[0]] if len(te) else tr
            if len(tr) < 500 or not len(te): continue
            Xt = X[tr]; b = np.linalg.solve(Xt.T @ Xt + c["ridge"] * np.eye(Xt.shape[1]), Xt.T @ tgt[tr + 1]); pred = X[te] @ b
            pnl.extend(((np.sign(pred) * tgt[te + 1]) - COST).tolist())
        pnl = np.array(pnl)
        if len(pnl) < 250 or pnl.std(ddof=1) == 0: return np.nan, len(pnl)
        return float(pnl.mean() / pnl.std(ddof=1) * np.sqrt(252 / H)), len(pnl)
    cells = grid(combo=combos, h=[1, 5, 20], train=[1000, 2000], ridge=[10.0, 100.0])
    sw = run(cells, stat, dict(y=y), shift_null("y", 250), n_null=max(50, N_NULL // 4), seed=0, label="D8 factor combinations → gold's next 1/5/20 sessions (walk-forward ridge, sign traded) — net Sharpe", meta=dict(tag="sweep", rows="h", cols="train"))
    top = sw.surface.sort_values("stat", ascending=False).head(12)
    extra = ["## The twelve strongest combinations", "", "| combination | h | train | ridge | net Sharpe | n |", "|---|---|---|---|---|---|"] + [f"| {'+'.join(r_['combo']) if r_['combo'] != ('all',) else 'all'} | {r_['h']} | {r_['train']} | {r_['ridge']} | {r_['stat']:+.2f} | {int(r_['n'])} |" for _, r_ in top.iterrows()]
    print(f"D8: best {sw.best} {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}")
    _finish("combo", [sw], [f"Features: each factor's trailing 1-, 5- and 20-session change; target: gold's return over the NEXT h sessions; ridge refit every 250 sessions on the trailing window; null: gold time-shifted (the factors keep their own structure). {len(cells):,} cells, {sw.n_null} null draws (fewer than usual: the grid is large)."], extra)


# ================================================================================================ D5b the oil → rates → gold chain
def cmd_oilchain():
    df = pd.read_csv(PROC / "oil_shocks.csv"); df["date"] = pd.to_datetime(df["date"]); g = df[df.asset == "GLD"].copy().reset_index(drop=True)
    m = macro(); r = returns(); idx = r.index
    hz = [h for h in ("f5", "f10", "f20", "f40", "f60") if h in g.columns]
    link = {}
    for ser in ("DGS2", "DFII10"):
        if m is None or ser not in m.columns: continue
        s = m[ser].reindex(idx).ffill()
        for H in (5, 10, 20):
            ch = []
            for d_ in g["date"]:
                pos = idx.searchsorted(d_); ch.append(float(s.iloc[pos + H] - s.iloc[pos]) * 100 if pos + H < len(s) else np.nan)
            g[f"{ser}_chg{H}"] = ch
            v = np.array(ch, float); v = v[np.isfinite(v)]
            link[(ser, H)] = dict(n=len(v), mean_bp=float(v.mean()), share_up=float((v > 0).mean()), t=float(v.mean() / v.std(ddof=1) * np.sqrt(len(v))) if len(v) > 2 else np.nan)
    rate_cols = [c for c in g.columns if "_chg" in c]
    def stat(dd, c):
        f = dd["g"]; m_ = np.ones(len(f), bool)
        if c["rates"] != "any":
            col = f"{c['series']}_chg{c['rate_h']}"
            if col not in f.columns: return np.nan, 0
            m_ &= (f[col] > 0).to_numpy() if c["rates"] == "up" else (f[col] <= 0).to_numpy()
        v = f.loc[m_, c["h"]].dropna().to_numpy(); ps = path_stats(v, int(c["h"][1:]), COST, c["sign"]); return ps["sharpe"], ps["n"]
    series = sorted({c.split("_chg")[0] for c in rate_cols}) or ["none"]
    cells = grid(h=hz, series=series, rate_h=[5, 10, 20], rates=["any", "up", "down"], sign=[1, -1])
    def null_gen(dd, rng):
        f = dd["g"].copy(); p = rng.permutation(len(f))
        for h in hz: f[h] = f[h].to_numpy()[p]
        return dict(g=f)
    sw = run(cells, stat, dict(g=g), null_gen, n_null=N_NULL, seed=0, label="D5b gold after an oil shock, conditioned on whether rates/real yields rose afterwards — net Sharpe (sign +1 long gold)", meta=dict(tag="sweep", rows="rates", cols="h"))
    L = ["## Link 1 — do rates rise after an oil shock?", "", "| series | horizon (sessions) | n | mean change (bp) | share up | t |", "|---|---|---|---|---|---|"] + [f"| {k[0]} | {k[1]} | {v['n']} | {v['mean_bp']:+.1f} | {v['share_up']:.0%} | {v['t']:+.2f} |" for k, v in link.items()]
    L += ["", "Link 2 (rates up → gold down) is the standing T9b/T-B result. Link 3 is the sweep above: gold after shocks where rates DID rise versus where they did not.", ""]
    print(f"D5b: best {sw.best} {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}"); print("link 1:", {f"{k[0]}@{k[1]}": round(v["t"], 2) for k, v in link.items()})
    _finish("oilchain", [sw], [f"{len(g)} oil shocks (GLD rows). The founder's chain, 5 Nov: oil up → inflation expectations → hawkish policy → higher real rates → gold down. Each link measured separately."], L)


# ================================================================================================ D5c the chain with tradeable timing
def cmd_oilchain_timed():
    df = pd.read_csv(PROC / "oil_shocks.csv"); df["date"] = pd.to_datetime(df["date"]); g = df[df.asset == "GLD"].copy().reset_index(drop=True)
    m = macro(); r = returns(); idx = r.index
    if m is None or "DFII10" not in m.columns: print("D5c: DFII10 not in macro_panel -- skipped"); return
    for ser in ("DFII10", "DGS2"):
        s = m[ser].reindex(idx).ffill(); ch = []
        for d_ in g["date"]:
            pos = idx.searchsorted(d_); ch.append(float(s.iloc[pos + 5] - s.iloc[pos]) * 100 if pos + 5 < len(s) else np.nan)
        g[f"{ser}_first5"] = ch
    for a, b in ((5, 20), (5, 40), (10, 20), (10, 40)):
        g[f"gold_{a}_{b}"] = g[f"f{b}"] - g[f"f{a}"]           # gold from session a to session b after the shock: entry after the rate move is known
    def stat(dd, c):
        f = dd["g"]; col = f"{c['series']}_first5"; m_ = (f[col] > 0).to_numpy() if c["rates"] == "up" else (f[col] <= 0).to_numpy() if c["rates"] == "down" else np.ones(len(f), bool)
        v = f.loc[m_, c["window"]].dropna().to_numpy(); a, b = [int(x) for x in c["window"].split("_")[1:]]; ps = path_stats(v, b - a, COST, c["sign"]); return ps["sharpe"], ps["n"]
    cells = grid(series=["DFII10", "DGS2"], rates=["any", "up", "down"], window=["gold_5_20", "gold_5_40", "gold_10_20", "gold_10_40"], sign=[1, -1])
    wins = [c for c in g.columns if c.startswith("gold_")]
    def null_gen(dd, rng):
        f = dd["g"].copy(); p = rng.permutation(len(f))
        for w in wins: f[w] = f[w].to_numpy()[p]
        return dict(g=f)
    sw = run(cells, stat, dict(g=g), null_gen, n_null=N_NULL, seed=0, label="D5c gold from session 6 (or 11) after an oil shock, conditioned on the rate move over the first 5 sessions — net Sharpe", meta=dict(tag="sweep", rows="rates", cols="window"))
    print(f"D5c: best {sw.best} {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}")
    _finish("oilchain_timed", [sw], [f"{len(g)} shocks; the rate condition uses only sessions 1–5 after the shock, the gold return starts after it (tradeable timing). Prior #105: inside the null."])


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["sudden", "regimes", "daily", "combo", "oilchain", "oilchain_timed", "all"]); a = ap.parse_args()
    DOCS.mkdir(exist_ok=True)
    todo = ["sudden", "regimes", "daily", "combo", "oilchain"] if a.cmd == "all" else [a.cmd]
    for c in todo:
        try:
            {"sudden": cmd_sudden, "regimes": cmd_regimes, "daily": cmd_daily, "combo": cmd_combo, "oilchain": cmd_oilchain, "oilchain_timed": cmd_oilchain_timed}[c]()
        except SystemExit:
            raise
        except Exception as e:
            print(f"{c}: did not run -- {type(e).__name__}: {e}")
            if a.cmd != "all": raise
