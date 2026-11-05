"""deeper.py -- the deeper tests of 5 Nov (docs/prereg_deeper_signals.md): seven candidate patterns taken from "measured" to
"could this be a weak trading signal", all through one recipe and one engine (src.sweep).

The recipe, stated once: (1) the entry condition becomes a grid; (2) confirmation filters are axes too; (3) every cell is scored on
the whole path after costs -- net Sharpe (mean forward return minus the round-trip cost, over its standard deviation, annualised by
horizon), with hit-rate, mean, worst and asymmetry carried beside; (4) the best cell is judged against the best cell the same search
finds on time-shifted data (p_family); (5) a survivor is registered and logged forward from that day (`forward`), and only a forward
log that itself clears its bar makes a signal.

  python -m src.deeper selloff     # D1 gold after an S&P drawdown: threshold x look-back x horizon x delay x filters (gold's own drawdown,
                                   #    dollar move, rate move during the sell-off, liquidity state); both directions
  python -m src.deeper liquidity   # D2 the liquidity link as an on/off meta-signal: trade gold on weekly liquidity changes only when the
                                   #    trailing link is 'on' (rolling t above a bar); grid: window x bar x horizon; publication lag kept
  python -m src.deeper corr        # D3 gold-equity correlation regime: predict next-month GLD-SPY correlation from state and recent realised
                                   #    correlation; scored by hedge error (a sizing input, not a direction call)
  python -m src.deeper fomc        # D4 Fed-day drift: statement-day and next-day GLD from the 2-yr surprise, the T-K3 rubric dimensions and the
                                   #    volatility state; grid over horizon x feature set x state
  python -m src.deeper oil         # D5 gold after oil shocks (processed/oil_shocks.csv): shock-size bins x horizon x regime
  python -m src.deeper cot         # D6 speculative positioning extremes (processed/*cot*): z-score bar x window x horizon x asset
  python -m src.deeper calls       # D7 the report's calls as a walk-forward learner (tier, specificity, agreement, ESS, regime, source, era)
  python -m src.deeper forward     # evaluate the registered survivor cells on the latest data; append pending rows to processed/forward_signals.csv
  python -m src.deeper all

Every run writes docs/deeper_<test>.md (+ _sweep.md, .json). Nothing here writes the register; the results rows are filled from the files.
"""
from __future__ import annotations

import argparse
import glob
import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

from src.sweep import grid, run, write_md, shift_null

PROC, DOCS = Path("processed"), Path("docs")
COST = 0.0010                     # round trip, GLD/SLV/USO-sized ETFs: 10 bp -- a grid axis in D1
MIN_N = 30
ERAS = [("2004-08", "2004-01-01", "2008-12-31"), ("2009-14", "2009-01-01", "2014-12-31"), ("2015-19", "2015-01-01", "2019-12-31"),
        ("2020-21", "2020-01-01", "2021-12-31"), ("2022-26", "2022-01-01", "2026-12-31")]
N_NULL = 200


def era_of(d) -> str:
    for name, a, b in ERAS:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b): return name
    return "other"


def returns() -> pd.DataFrame:
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    if getattr(r.index, "tz", None) is not None: r.index = r.index.tz_localize(None)
    return r.sort_index()


def macro() -> pd.DataFrame | None:
    p = PROC / "macro_panel.parquet"
    if not p.exists(): return None
    m = pd.read_parquet(p); m.index = pd.to_datetime(m.index); return m.sort_index()


def path_stats(f: np.ndarray, h: int, cost: float = COST, sign: int = 1) -> dict:
    """f: forward log returns of the traded asset over h sessions after each entry; sign +1 long, -1 short."""
    x = sign * f - cost; n = len(x)
    if n < MIN_N or x.std(ddof=1) == 0: return dict(n=n, sharpe=np.nan, hit=np.nan, mean=np.nan, worst=np.nan, asym=np.nan)
    hit = (x > 0).mean(); g = x[x > 0].mean() if (x > 0).any() else np.nan; l = -x[x <= 0].mean() if (x <= 0).any() else np.nan
    return dict(n=n, sharpe=float(x.mean() / x.std(ddof=1) * np.sqrt(252 / h)), hit=float(hit), mean=float(x.mean()), worst=float(x.min()),
                asym=float(g / l) if (np.isfinite(g) and np.isfinite(l) and l > 0) else np.nan)


def fwd(cum: np.ndarray, starts: np.ndarray, h: int) -> np.ndarray:
    starts = starts[starts + h < len(cum)]; return cum[starts + h] - cum[starts]


def _md_table(rows: list[dict], cols: list[str], fmt: dict) -> list[str]:
    L = ["| " + " | ".join(cols) + " |", "|---|" * len(cols)]
    for r in rows: L.append("| " + " | ".join((fmt.get(c, "{}").format(r[c]) if not (isinstance(r[c], float) and not np.isfinite(r[c])) else "·") for c in cols) + " |")
    return L


def _finish(name: str, sw_list: list, head: list[str], extra: list[str] | None = None):
    out = DOCS / f"deeper_{name}.md"
    L = [f"# Deeper test {name} — {datetime.now():%Y-%m-%d %H:%M}", ""] + head + [""]
    for sw in sw_list:
        b = sw.surface.loc[sw.surface["stat"].idxmax()] if sw.surface["stat"].notna().any() else None
        L += [f"## {sw.label}", "",
              f"Best cell `{sw.best}`: net Sharpe {sw.best_stat:+.2f} on n = {int(b['n']) if b is not None else 0}; best-of-search null 95th percentile {sw.q95:+.2f}; **p_family = {sw.p_family:.3f}**; survivors {len(sw.survivors)}.", ""]
        if sw.survivors:
            L += ["Survivors: " + "; ".join(str({k: v for k, v in c.items() if k != 'stat'}) + f" {c['stat']:+.2f}" for c in sw.survivors[:10]), ""]
        write_md(sw, DOCS / f"deeper_{name}_{sw.meta.get('tag', 'sweep')}.md", axis_rows=sw.meta.get("rows"), axis_cols=sw.meta.get("cols"), fmt="{:+.2f}")
    if extra: L += extra
    L += ["", "A survivor here is a candidate for the forward log, not a signal: the registered rule is written by dated amendment and judged on data it has never seen."]
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(json.dumps([sw.to_json() for sw in sw_list], indent=1, default=float))
    print(f"-> {out}")


# ================================================================================================ D1 gold after an S&P drawdown
def _crossings(dd: np.ndarray, thr: float, cool: int, lo: int) -> np.ndarray:
    hit = np.where((dd[1:] <= thr) & (dd[:-1] > thr))[0] + 1; ev = []; last = -10 ** 9
    for i in hit:
        if i >= lo and i - last >= cool: ev.append(i); last = i
    return np.array(ev, int)


def cmd_selloff():
    r = returns(); m = macro()
    spy, gld = r["SPY"], r["GLD"]; ok = spy.notna() & gld.notna(); d = pd.DataFrame(dict(spy=spy[ok], gld=gld[ok])); idx = d.index; n = len(d)
    uup = r["UUP"].reindex(idx).to_numpy() if "UUP" in r.columns else np.full(n, np.nan)
    dgs = (m["DGS2"].reindex(idx).ffill().diff().to_numpy() if (m is not None and "DGS2" in m.columns) else np.full(n, np.nan))
    stress = np.zeros(n)
    if (PROC / "liquidity_states.parquet").exists():
        s_ = pd.read_parquet(PROC / "liquidity_states.parquet"); s_.index = pd.to_datetime(s_.index); stress = s_[s_.columns[0]].reindex(idx).ffill().fillna(0).astype(float).to_numpy()
    spy_v, gld_v = d["spy"].to_numpy(), d["gld"].to_numpy(); era = np.array([era_of(t) for t in idx])
    cum_u = np.concatenate([[0], np.cumsum(np.nan_to_num(uup))]); cum_r = np.concatenate([[0], np.cumsum(np.nan_to_num(dgs))])
    have_u, have_r = bool(np.isfinite(uup).any()), bool(np.isfinite(dgs).any())
    DD = {look: pd.Series(spy_v).rolling(look).sum().to_numpy() for look in (10, 20, 40)}
    EV = {}
    def ev_for(look, thr):
        key = (look, thr)
        if key not in EV: EV[key] = _crossings(DD[look], thr, 2 * look, look)
        return EV[key]

    def stat_factory(sign):
        def stat(dd, c):
            g = np.asarray(dd["gld"]); cum = np.concatenate([[0], np.cumsum(g)])
            ev = ev_for(c["look"], c["thr"]) + c["delay"]; ev = ev[(ev > c["look"]) & (ev < n - c["h"] - 1)]
            lo = np.maximum(ev - c["look"], 0); f = c["filter"]
            if f == "gold_down": ev = ev[(cum[ev] - cum[lo]) < 0]
            elif f == "gold_up": ev = ev[(cum[ev] - cum[lo]) >= 0]
            elif f == "dollar_up": ev = ev[(cum_u[ev] - cum_u[lo]) > 0]
            elif f == "dollar_down": ev = ev[(cum_u[ev] - cum_u[lo]) <= 0]
            elif f == "rates_down": ev = ev[(cum_r[ev] - cum_r[lo]) < 0]
            elif f == "rates_up": ev = ev[(cum_r[ev] - cum_r[lo]) >= 0]
            elif f == "stress": ev = ev[stress[ev] == 1]
            elif f == "abundant": ev = ev[stress[ev] != 1]
            elif f.startswith("era="): ev = ev[era[ev] == f[4:]]
            fw = fwd(cum, ev, c["h"]); ps = path_stats(fw, c["h"], c["cost"], sign); return ps["sharpe"], ps["n"]
        return stat
    filters = ["none", "gold_down", "gold_up"] + (["dollar_up", "dollar_down"] if have_u else []) + (["rates_down", "rates_up"] if have_r else []) + ["stress", "abundant"] + [f"era={e[0]}" for e in ERAS]
    cells = grid(thr=[-0.04, -0.05, -0.06, -0.07, -0.08, -0.10], look=[10, 20, 40], h=[5, 10, 15, 20, 30], delay=[0, 1, 3], filter=filters, cost=[COST])
    sws = []
    for name, sign in (("long gold after the drawdown", +1), ("short gold after the drawdown", -1)):
        sw = run(cells, stat_factory(sign), dict(gld=gld_v), shift_null("gld", 250), n_null=N_NULL, seed=0, label=f"D1 {name} — net Sharpe", meta=dict(tag="long" if sign > 0 else "short", rows="thr", cols="h"))
        sws.append(sw); print(f"D1 {name}: best {sw.best} Sharpe {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}, survivors {len(sw.survivors)}")
    cum_g = np.concatenate([[0], np.cumsum(gld_v)]); ev = ev_for(20, -0.06); ps = path_stats(fwd(cum_g, ev[ev < n - 16], 15), 15)
    extra = ["## The 5 Nov survivor on the path (−6% / look 20 / 15 sessions, long gold, 10 bp cost)", "",
             (f"n {ps['n']}, hit {ps['hit']:.0%}, mean {ps['mean'] * 100:+.2f}% per trade, net Sharpe {ps['sharpe']:+.2f}, worst {ps['worst'] * 100:+.1f}%, asymmetry {ps['asym']:.2f}." if ps["n"] >= MIN_N else f"n {ps['n']} (under {MIN_N}).")]
    _finish("selloff", sws, [f"{n:,} sessions {idx[0].date()} → {idx[-1].date()}; {len(cells):,} cells (one filter at a time, plus eras); cost {COST * 1e4:.0f} bp round trip; cells under {MIN_N} events are ·."], extra)


# ================================================================================================ D2 liquidity on/off
def cmd_liquidity():
    from src.liquidity_link import weekly_pair
    df, nl, r = weekly_pair("GLD"); x, y = df["x"].to_numpy(), df["y"].to_numpy(); dates = df.index; n = len(x)

    def rolling_t(xx, yy, W):
        t = np.full(len(xx), np.nan)
        for i in range(W, len(xx)):
            a, b = xx[i - W:i], yy[i - W:i]; am, bm = a.mean(), b.mean(); sxx = ((a - am) ** 2).sum()
            if sxx <= 0: continue
            beta = ((a - am) * (b - bm)).sum() / sxx; e = b - bm - beta * (a - am); se = np.sqrt((e @ e) / (W - 2) / sxx); t[i] = beta / se if se > 0 else np.nan
        return t

    def stat(dd, c):
        xx, yy = np.asarray(dd["x"]), np.asarray(dd["y"]); t = rolling_t(xx, yy, c["W"])
        # position next week = sign of this week's liquidity change (known Thursday, GLD traded Thu->Wed of the next week: shift 1), only when 'on'
        on = (t > c["bar"]) if c["mode"] == "on" else (t <= c["bar"]) if c["mode"] == "off" else np.ones(n, bool)
        pos = np.sign(xx) * on; pnl = pos[:-1] * yy[1:] - COST * (np.abs(np.diff(pos)) > 0)[: n - 1] * 0.5
        pnl = pnl[np.isfinite(pnl) & (np.abs(pos[:-1]) > 0)]
        if len(pnl) < 52 or pnl.std(ddof=1) == 0: return np.nan, len(pnl)
        return float(pnl.mean() / pnl.std(ddof=1) * np.sqrt(52)), len(pnl)
    cells = grid(W=[52, 78, 104, 156], bar=[1.0, 1.5, 2.0, 2.5], mode=["on", "off", "always"])
    sw = run(cells, stat, dict(x=x, y=y), shift_null("x", 52), n_null=N_NULL, seed=0, label="D2 gold on weekly liquidity change, traded only when the trailing link is 'on' — annualised net Sharpe", meta=dict(tag="sweep", rows="W", cols="bar"))
    print(f"D2: best {sw.best} Sharpe {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}")
    _finish("liquidity", [sw], [f"{n} weeks {dates[0].date()} → {dates[-1].date()}; position = sign of this week's Δlog net liquidity, held Thursday→Wednesday of the following week; 'on' = trailing W-week t-statistic above the bar; 'always' is the unconditional rule for comparison."])


# ================================================================================================ D3 correlation regime
def cmd_corr():
    r = returns(); d = pd.DataFrame(dict(gld=r["GLD"], spy=r["SPY"])).dropna(); idx = d.index
    st = None
    if (PROC / "liquidity_states.parquet").exists():
        s = pd.read_parquet(PROC / "liquidity_states.parquet"); s.index = pd.to_datetime(s.index); st = s[s.columns[0]].reindex(idx).ffill().astype(float).to_numpy()
    g, sp = d["gld"].to_numpy(), d["spy"].to_numpy(); n = len(d)
    def realised(win):
        return pd.Series(g).rolling(win).corr(pd.Series(sp)).to_numpy()
    fut = {}
    for H in (20, 40, 60):
        c = pd.Series(g).rolling(H).corr(pd.Series(sp)).to_numpy(); fut[H] = np.concatenate([c[H:], np.full(H, np.nan)])     # correlation over the NEXT H sessions
    def stat(dd, c):
        y = np.asarray(dd[f"fut{c['H']}"]); x = realised(c["win"]); feats = [x]
        if c["state"] and st is not None: feats.append(st)
        X = np.column_stack(feats + [np.ones(n)]); ok = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
        # walk-forward: fit on the first 60% of the sample, score hedge error on the rest; baseline = long-run mean correlation
        k = int(ok.sum() * 0.6); ii = np.where(ok)[0]; tr, te = ii[:k], ii[k:]
        if len(te) < 250: return np.nan, len(te)
        b, *_ = np.linalg.lstsq(X[tr], y[tr], rcond=None); pred = X[te] @ b
        err_model = np.mean((y[te] - pred) ** 2); err_base = np.mean((y[te] - y[tr].mean()) ** 2)
        return float(1 - err_model / err_base), len(te)          # skill: share of the baseline's squared error removed
    cells = grid(win=[20, 40, 60, 120], H=[20, 40, 60], state=[False, True])
    data = dict(g=g, **{f"fut{H}": v for H, v in fut.items()})
    def null_gen(dd, rng):
        out = dict(dd); s_ = int(rng.integers(250, n - 250))
        for H in (20, 40, 60): out[f"fut{H}"] = np.roll(dd[f"fut{H}"], s_)
        return out
    sw = run(cells, stat, data, null_gen, n_null=N_NULL, seed=0, label="D3 next-period GLD–SPY correlation from realised correlation (+ stress state): out-of-sample skill vs the long-run mean", meta=dict(tag="sweep", rows="win", cols="H"))
    print(f"D3: best {sw.best} skill {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}")
    _finish("corr", [sw], [f"{n:,} sessions; skill = 1 − (model squared error / baseline squared error) on the last 40% of the sample; a sizing input for the equity hedge, not a direction call."])


# ================================================================================================ D4 Fed-day drift
def cmd_fomc():
    from src.chair_power import table
    t = table().dropna(subset=["s", "gld"]).copy(); r = returns(); g = r["GLD"]
    nxt = []; two = []
    for d in t["date"]:
        pos = g.index.searchsorted(d)
        nxt.append(g.iloc[pos + 1] if pos + 1 < len(g) else np.nan); two.append(g.iloc[pos + 1:pos + 3].sum() if pos + 3 <= len(g) else np.nan)
    t["gld_next"] = nxt; t["gld_2"] = two
    rub = {}
    for f in glob.glob("data_provenance/doc_reads_style/fomc_statement__*__style-v1-*.json"):
        j = json.loads(Path(f).read_text()); rub[j["date"]] = j
    for k in ("hawk_dove", "inflation_vs_labour", "hedging_density", "guidance_strength", "novelty_vs_prev"):
        t[k] = [float(rub.get(str(d.date()), {}).get(k, np.nan) or np.nan) for d in t["date"]]
    t["volstate"] = (t["vol"] > t["vol"].median()).astype(float)
    def stat(dd, c):
        y = np.asarray(dd[c["target"]]); feats = {"surprise": ["s_norm"], "rubric": ["hawk_dove", "inflation_vs_labour", "hedging_density"], "both": ["s_norm", "hawk_dove", "inflation_vs_labour", "hedging_density"]}[c["features"]]
        X = t[feats].to_numpy(float); ok = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
        if c["state"] != "all": ok &= (t["volstate"].to_numpy() == (1.0 if c["state"] == "highvol" else 0.0))
        ii = np.where(ok)[0]
        if len(ii) < 40: return np.nan, len(ii)
        # leave-one-out linear prediction, sign of prediction traded, costed
        X1 = np.column_stack([X[ii], np.ones(len(ii))]); yy = y[ii]; pnl = []
        for k in range(len(ii)):
            m = np.ones(len(ii), bool); m[k] = False; b, *_ = np.linalg.lstsq(X1[m], yy[m], rcond=None); pnl.append(np.sign(X1[k] @ b) * yy[k] - COST)
        pnl = np.array(pnl); return float(pnl.mean() / pnl.std(ddof=1) * np.sqrt(8)), len(ii)
    cells = grid(target=["gld", "gld_next", "gld_2"], features=["surprise", "rubric", "both"], state=["all", "highvol", "lowvol"])
    def null_gen(dd, rng):
        out = dict(dd); p = rng.permutation(len(t))
        for k in ("gld", "gld_next", "gld_2"): out[k] = np.asarray(dd[k])[p]
        return out
    sw = run(cells, stat, dict(gld=t["gld"].to_numpy(), gld_next=t["gld_next"].to_numpy(float), gld_2=t["gld_2"].to_numpy(float)), null_gen, n_null=N_NULL, seed=0,
             label="D4 Fed-day gold from the surprise and the statement's rubric — leave-one-out, per-meeting Sharpe", meta=dict(tag="sweep", rows="target", cols="features"))
    print(f"D4: best {sw.best} Sharpe {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}")
    _finish("fomc", [sw], [f"{len(t)} statements; targets: statement day, next day, next two days; features: the 2-yr surprise per σ, the T-K3 rubric (hawk/dove, inflation emphasis, hedging), or both; state = the yield's trailing volatility above/below its median. The statement-day target is tradeable only from 2 pm (the live reader); the others from the close."])


# ================================================================================================ D5 oil shocks
def cmd_oil():
    df = pd.read_csv(PROC / "oil_shocks.csv"); df["date"] = pd.to_datetime(df["date"]); df = df[df.asset == "GLD"].copy().reset_index(drop=True)
    hz = [h for h in ("f5", "f10", "f20", "f40", "f60", "f90") if h in df.columns]
    era = df["date"].map(era_of).to_numpy(); pool = df["pool"].astype(str).to_numpy(); regime = df["regime"].astype(str).to_numpy()
    size = pd.cut(df["oil5"], [0, 0.08, 0.12, 1], labels=["5-8%", "8-12%", ">12%"]).astype(str).to_numpy()
    F = {h: df[h].to_numpy(float) for h in hz}
    splits = ["all"] + [f"regime={x}" for x in sorted(set(regime))] + [f"era={e[0]}" for e in ERAS]
    def stat(dd, c):
        m = np.ones(len(df), bool)
        if c["pool"] != "all": m &= pool == c["pool"]
        if c["size"] != "all": m &= size == c["size"]
        if c["split"] != "all":
            k, v = c["split"].split("="); m &= (regime == v) if k == "regime" else (era == v)
        v = dd[c["h"]][m]; v = v[np.isfinite(v)]; hh = int(c["h"][1:]); ps = path_stats(v, hh, COST, c["sign"]); return ps["sharpe"], ps["n"]
    cells = grid(h=hz, pool=["all"] + sorted(set(pool)), size=["all", "5-8%", "8-12%", ">12%"], split=splits, sign=[1, -1])
    def null_gen(dd, rng):
        p = rng.permutation(len(df)); return {h: dd[h][p] for h in hz}      # forward paths detached from the shock's attributes
    sw = run(cells, stat, F, null_gen, n_null=N_NULL, seed=0, label="D5 gold after an oil shock — net Sharpe by horizon, pool, shock size, regime or era, direction", meta=dict(tag="sweep", rows="size", cols="h"))
    print(f"D5: best {sw.best} Sharpe {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}")
    _finish("oil", [sw], [f"{len(df)} shock rows (GLD) from processed/oil_shocks.csv; {len(cells):,} cells; the null detaches each shock's forward path from its attributes."])


# ================================================================================================ D6 COT positioning
def cmd_cot():
    files = sorted(glob.glob(str(PROC / "*cot*")) + glob.glob(str(PROC / "*positioning*")))
    if not files: print("D6: no COT file under processed/ (looked for *cot*, *positioning*) -- skipped"); return
    p = Path(files[0]); cot = pd.read_parquet(p) if p.suffix == ".parquet" else pd.read_csv(p, index_col=0, parse_dates=True); cot.index = pd.to_datetime(cot.index)
    r = returns(); assets = {"GLD": [c for c in cot.columns if "gold" in c.lower()], "SLV": [c for c in cot.columns if "silver" in c.lower()], "USO": [c for c in cot.columns if "oil" in c.lower() or "wti" in c.lower()]}
    assets = {a: cs[0] for a, cs in assets.items() if cs and a in r.columns}
    if not assets: print(f"D6: no gold/silver/oil column recognised in {p.name}: {list(cot.columns)[:8]} -- skipped"); return
    print(f"D6: using {p.name}, columns {assets}")
    def stat(dd, c):
        a = c["asset"]; s = cot[assets[a]].dropna(); z = (s - s.rolling(c["win"]).mean()) / s.rolling(c["win"]).std()
        g = dd[a]; cum = np.concatenate([[0], np.cumsum(np.nan_to_num(g.to_numpy()))]); idx = g.index
        ext = z[z.abs() > c["bar"]]; starts = idx.searchsorted(ext.index + pd.Timedelta(days=3))        # published Friday: enter the next session
        starts = starts[starts < len(idx) - c["h"]]; signs = -np.sign(ext.to_numpy())[: len(starts)] * c["dir"]   # dir +1 = fade the crowd, -1 = follow
        f = fwd(cum, starts, c["h"]) * signs[: len(fwd(cum, starts, c["h"]))]; ps = path_stats(f, c["h"], COST, 1); return ps["sharpe"], ps["n"]
    cells = grid(asset=list(assets), win=[52, 104, 156], bar=[1.0, 1.5, 2.0], h=[5, 10, 20, 40], dir=[1, -1])
    data = {a: r[a].dropna() for a in assets}
    def null_gen(dd, rng):
        out = {}
        for a, g in dd.items(): s_ = int(rng.integers(250, len(g) - 250)); out[a] = pd.Series(np.roll(g.to_numpy(), s_), index=g.index)
        return out
    sw = run(cells, stat, data, null_gen, n_null=N_NULL, seed=0, label="D6 speculative positioning extremes — fade (+1) or follow (−1) the crowd; net Sharpe", meta=dict(tag="sweep", rows="bar", cols="h"))
    print(f"D6: best {sw.best} Sharpe {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}")
    _finish("cot", [sw], [f"Positioning from {p.name}; z-score of the net speculative position over a trailing window; entries the session after publication."])


# ================================================================================================ D7 the report's calls as a learner
def cmd_calls(csv: str):
    df = pd.read_csv(csv); df["date"] = pd.to_datetime(df["date"]); df = df[(df.h == 2) & (df.kind == "call")].dropna(subset=["call", "ret_primary"]).sort_values("date").reset_index(drop=True)
    df["era"] = df["date"].map(era_of); y = (df["call"] * df["ret_primary"]).to_numpy()          # the call's own signed return
    num = [c for c in ("ess", "w", "n_docs", "agreement", "net_view") if c in df.columns]
    for c in num: df[c] = pd.to_numeric(df[c], errors="coerce")
    cat = [c for c in ("tier", "regime", "dominant_source", "asset") if c in df.columns]
    X = pd.get_dummies(df[num + cat].astype({c: str for c in cat}), dummy_na=True).astype(float).fillna(0.0); X["const"] = 1.0
    def stat(dd, c):
        yy = np.asarray(dd["y"]); n = len(yy); k0 = int(n * 0.5); pnl = []
        step = 250
        for s in range(k0, n, step):
            tr = np.arange(max(0, s - c["train"]), s); te = np.arange(s, min(s + step, n))
            Xt = X.iloc[tr].to_numpy(); lam = c["ridge"] * np.eye(Xt.shape[1]); b = np.linalg.solve(Xt.T @ Xt + lam, Xt.T @ yy[tr])
            pred = X.iloc[te].to_numpy() @ b
            take = pred > np.quantile(pred, c["q"]) if c["q"] > 0 else pred > 0
            pnl.extend((yy[te][take] - COST).tolist())
        pnl = np.array(pnl)
        if len(pnl) < 100 or pnl.std(ddof=1) == 0: return np.nan, len(pnl)
        return float(pnl.mean() / pnl.std(ddof=1) * np.sqrt(126)), len(pnl)
    cells = grid(train=[500, 1000, 2000], ridge=[1.0, 10.0, 100.0], q=[0.0, 0.5, 0.75])
    def null_gen(dd, rng): return dict(y=np.asarray(dd["y"])[rng.permutation(len(dd["y"]))])
    base = path_stats(y, 2, COST); sw = run(cells, stat, dict(y=y), null_gen, n_null=N_NULL, seed=0, label="D7 keep only the calls a walk-forward ridge expects to pay — net Sharpe of the kept calls", meta=dict(tag="sweep", rows="train", cols="ridge"))
    print(f"D7: all calls net Sharpe {base['sharpe']:+.2f} (n {base['n']}); best {sw.best} {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}")
    _finish("calls", [sw], [f"{len(df):,} calls (h 2) from {Path(csv).name}; features {num + cat}; target = the call's own signed 2-session return; learner refit every 250 calls on the trailing window; `q` keeps the top share by predicted return (0 = all with positive prediction). Baseline: every call, net Sharpe {base['sharpe']:+.2f}."])


# ================================================================================================ forward log
REGISTERED = [dict(name="D1-5nov", rule="long GLD 15 sessions after SPY's 20-session return first crosses −6% (one entry per 40 sessions)", thr=-0.06, look=20, h=15, cool=40)]


def cmd_forward():
    r = returns(); spy, gld = r["SPY"].dropna(), r["GLD"]; p = PROC / "forward_signals.csv"
    log = pd.read_csv(p, parse_dates=["entry"]) if p.exists() else pd.DataFrame(columns=["name", "entry", "exit_due", "h", "status", "ret", "logged_at"])
    today = spy.index[-1]; rows = []
    for R in REGISTERED:
        dd = spy.rolling(R["look"]).sum()
        if len(dd) < 2 or not (dd.iloc[-1] <= R["thr"] and dd.iloc[-2] > R["thr"]): continue
        recent = log[(log["name"] == R["name"]) & (log["entry"] > today - pd.Timedelta(days=R["cool"] * 1.5))]
        if len(recent): continue
        rows.append(dict(name=R["name"], entry=today, exit_due=today + pd.tseries.offsets.BDay(R["h"]), h=R["h"], status="pending", ret=np.nan, logged_at=datetime.now().strftime("%Y-%m-%d %H:%M")))
    if rows: log = pd.concat([log, pd.DataFrame(rows)], ignore_index=True); print(f"forward: {len(rows)} new entr{'y' if len(rows) == 1 else 'ies'} logged for {today.date()}")
    for i, row in log[log["status"] == "pending"].iterrows():
        pos = gld.index.searchsorted(row["entry"])
        if pos + row["h"] < len(gld):
            log.loc[i, "ret"] = float(gld.iloc[pos + 1:pos + 1 + int(row["h"])].sum()); log.loc[i, "status"] = "matured"
    log.to_csv(p, index=False)
    m = log[log.status == "matured"]
    print(f"forward log: {len(log)} rows, {len(m)} matured" + (f"; matured mean {m['ret'].mean() * 100:+.2f}%, hit {(m['ret'] > 0).mean():.0%}" if len(m) else "") + f" -> {p}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["selloff", "liquidity", "corr", "fomc", "oil", "cot", "calls", "forward", "all"])
    ap.add_argument("--csv", default="processed/report_backfill_97d9bf07dd2c_n5793.csv"); a = ap.parse_args()
    DOCS.mkdir(exist_ok=True)
    todo = ["selloff", "liquidity", "corr", "fomc", "oil", "cot", "calls"] if a.cmd == "all" else [a.cmd]
    for c in todo:
        try:
            {"selloff": cmd_selloff, "liquidity": cmd_liquidity, "corr": cmd_corr, "fomc": cmd_fomc, "oil": cmd_oil, "cot": cmd_cot, "calls": lambda: cmd_calls(a.csv), "forward": cmd_forward}[c]()
        except SystemExit:
            raise
        except Exception as e:
            print(f"{c}: did not run -- {type(e).__name__}: {e}")
            if a.cmd != "all": raise
