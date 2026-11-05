"""era_liquidity.py -- the liquidity-gold family by era and by grid (prereg_subperiod_audit.md, group B, items B1-B3).

  python -m src.era_liquidity liquidity      # T-L6: slope, R2, liquidity volatility per era; sequential sup-F for up to 3 breaks with the
                                             # block-bootstrap null; the registered watershed dates checked; sweep over the recent-window length
  python -m src.era_liquidity p1             # P1 by era: the stress-minus-abundant gap in GLD-SPY rolling correlation per era and in rolling
                                             # 2-year windows; sweep over era x correlation window x state lag against a block-permutation null
  python -m src.era_liquidity selloff        # T-L5b as a grid: threshold {-4..-10%} x horizon {5,7,10,13,15,20,30} x look-back {10,20,40} x era,
                                             # both directions (gold sold / gold bought), judged against the best-of-sweep null (GLD time-shifted)
  python -m src.era_liquidity all

Inputs: src.liquidity_link.weekly_pair (net liquidity from FRED, GLD weekly), processed/asset_returns.parquet, processed/liquidity_states.parquet.
Outputs: docs/era_liquidity_<part>.md (+ .json). Nothing here writes the register.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.sweep import grid, run, write_md, shift_null

PROC, DOCS = Path("processed"), Path("docs")
ERAS = [("2004-08", "2004-01-01", "2008-12-31"), ("2009-14", "2009-01-01", "2014-12-31"), ("2015-19", "2015-01-01", "2019-12-31"),
        ("2020-21", "2020-01-01", "2021-12-31"), ("2022-26", "2022-01-01", "2026-12-31")]
WATERSHEDS = {"2020-03-15 pandemic flood": "2020-03-15", "2022-02-24 reserve freeze": "2022-02-24", "2022-03-16 first hike": "2022-03-16"}
TRIM, MIN_SEG, NDRAW, BLOCK, SEED = 0.15, 104, 500, 13, 0


def era_of(d) -> str:
    for name, a, b in ERAS:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b):
            return name
    return "other"


def ols(x, y):
    x, y = np.asarray(x, float), np.asarray(y, float); n = len(x)
    if n < 8: return dict(n=n, beta=np.nan, t=np.nan, r2=np.nan, sd_x=np.nan)
    xm, ym = x.mean(), y.mean(); sxx = ((x - xm) ** 2).sum(); b = ((x - xm) * (y - ym)).sum() / sxx if sxx > 0 else np.nan; a = ym - b * xm
    e = y - a - b * x; s2 = (e @ e) / max(n - 2, 1); se = np.sqrt(s2 / sxx) if sxx > 0 else np.nan
    r2 = 1 - (e @ e) / (((y - ym) ** 2).sum() or np.nan)
    return dict(n=int(n), beta=float(b), t=float(b / se) if se and np.isfinite(se) and se > 0 else np.nan, r2=float(r2), sd_x=float(x.std(ddof=1)))


# ---------------------------------------------------------------------------------------------------------------- T-L6
def _rss_prefix(x, y):
    """RSS of the OLS fit on the first k points, for every k, in one pass (and reversed for the suffix)."""
    n = len(x); out = np.full(n + 1, np.nan)
    sx = sy = sxx = syy = sxy = 0.0
    for k in range(1, n + 1):
        xi, yi = x[k - 1], y[k - 1]; sx += xi; sy += yi; sxx += xi * xi; syy += yi * yi; sxy += xi * yi
        if k >= 2:
            vx = sxx - sx * sx / k; vy = syy - sy * sy / k; cxy = sxy - sx * sy / k
            out[k] = vy - (cxy * cxy / vx if vx > 0 else 0.0)
    return out


def sup_f(x, y, trim=TRIM):
    n = len(x); pre = _rss_prefix(x, y); suf = _rss_prefix(x[::-1], y[::-1])[::-1]
    rss0 = pre[n]; best, kb = -np.inf, None
    for k in range(int(n * trim), int(n * (1 - trim))):
        rss1 = pre[k] + suf[k]
        if not np.isfinite(rss1) or rss1 <= 0: continue
        F = ((rss0 - rss1) / 2) / (rss1 / (n - 4))
        if F > best: best, kb = F, k
    return float(best), kb


def boot_p(x, y, F_obs, rng, n_draw=NDRAW, block=BLOCK):
    """Null: the constant-slope model; circular block bootstrap of its residuals; the sup-F recomputed on each pseudo-series."""
    a, b = np.polyfit(x, y, 1)[::-1]; e = y - a - b * x; n = len(x); cnt = 0
    for _ in range(n_draw):
        idx = np.concatenate([np.arange(s, s + block) % n for s in rng.integers(0, n, size=n // block + 1)])[:n]
        F, _ = sup_f(x, a + b * x + e[idx]); cnt += F >= F_obs
    return cnt / n_draw


def sequential_breaks(x, y, dates, rng, max_breaks=3):
    """Bai (1997) sequential procedure: find the break on the whole sample; if it clears p < 0.05, split and test each segment; stop at
    max_breaks or when no segment of >= MIN_SEG weeks yields a break at p < 0.05."""
    segs = [(0, len(x))]; found = []
    while len(found) < max_breaks:
        cands = []
        for (lo, hi) in segs:
            if hi - lo < 2 * MIN_SEG: continue
            F, k = sup_f(x[lo:hi], y[lo:hi])
            if k is None: continue
            p = boot_p(x[lo:hi], y[lo:hi], F, rng)
            cands.append((p, -F, lo, hi, lo + k))
        cands = [c for c in cands if c[0] < 0.05]
        if not cands: break
        p, negF, lo, hi, kb = sorted(cands)[0]
        found.append(dict(date=str(dates[kb].date()), F=float(-negF), p=float(p), segment=(str(dates[lo].date()), str(dates[hi - 1].date())),
                          beta_before=ols(x[lo:kb], y[lo:kb])["beta"], beta_after=ols(x[kb:hi], y[kb:hi])["beta"]))
        segs = [s for s in segs if s != (lo, hi)] + [(lo, kb), (kb, hi)]
    return found


def cmd_liquidity():
    from src.liquidity_link import weekly_pair
    df, nl, r = weekly_pair("GLD"); df = df.copy(); df["era"] = [era_of(d) for d in df.index]
    x, y = df["x"].to_numpy(), df["y"].to_numpy(); dates = df.index
    rows = [dict(era="all", **ols(x, y))] + [dict(era=e, **ols(df.loc[df.era == e, "x"], df.loc[df.era == e, "y"])) for e in [e[0] for e in ERAS] if (df.era == e).any()]
    tab = pd.DataFrame(rows); tab["beta_x_sd"] = tab["beta"] * tab["sd_x"] * 100        # weekly gold move per 1-sd liquidity week, in %
    rng = np.random.default_rng(SEED)
    breaks = sequential_breaks(x, y, dates, rng)
    near = []
    for name, d in WATERSHEDS.items():
        for b in breaks:
            if abs((pd.Timestamp(b["date"]) - pd.Timestamp(d)).days) <= 26 * 7:
                near.append(f"{name} ↔ break {b['date']} (p {b['p']:.3f})")
    # sweep: the recent window length W, statistic = slope on the last W weeks in units of the earlier windows' spread -> is 'recent' different?
    cells = grid(W=[52, 78, 104, 130, 156, 208, 260, 312])
    def stat(d, c):
        W = c["W"]; xx, yy = np.asarray(d["x"]), np.asarray(d["y"])
        if len(xx) < 2 * W: return np.nan, 0
        b_recent = ols(xx[-W:], yy[-W:])["beta"]
        earlier = [ols(xx[i:i + W], yy[i:i + W])["beta"] for i in range(0, len(xx) - W, 13)]
        earlier = np.array([v for v in earlier if np.isfinite(v)])
        if len(earlier) < 5: return np.nan, W
        return float((b_recent - earlier.mean()) / (earlier.std(ddof=1) or np.nan)), W
    sw = run(cells, stat, dict(x=df["x"], y=df["y"]), shift_null("x", 52), n_null=300, seed=SEED, label="T-L6 recent window: slope of the last W weeks vs earlier windows (z)")
    out = DOCS / "era_liquidity_liquidity.md"
    L = [f"# T-L6 — the liquidity–gold link by era and by break ({df.index[0].date()} → {df.index[-1].date()}, {len(df)} weeks)", "",
         "Weekly GLD log return on weekly Δlog net liquidity (Fed assets − TGA − RRP), contemporaneous. `beta_x_sd` = gold's weekly move, in %, for a one-standard-deviation liquidity week of that era — the 'driver' and the 'habit' read together: a habit that changed shows in `beta`; a driver that started moving shows in `sd_x` and `r2` with `beta` flat.", "",
         "| era | n weeks | β | t | R² | sd(Δlog NL) % | β × sd (% gold / 1-sd week) |", "|---|---|---|---|---|---|---|"]
    for _, r_ in tab.iterrows():
        L.append(f"| {r_['era']} | {r_['n']} | {r_['beta']:+.3f} | {r_['t']:+.2f} | {r_['r2']:.3f} | {r_['sd_x'] * 100:.2f} | {r_['beta_x_sd']:+.3f} |")
    L += ["", f"## Sequential sup-F (Bai 1997), up to 3 breaks, {TRIM:.0%} trimming, segments ≥ {MIN_SEG} weeks, block-bootstrap null ({NDRAW} draws, block {BLOCK})", ""]
    if breaks:
        L += ["| break | sup-F | p | segment searched | β before | β after |", "|---|---|---|---|---|---|"]
        for b in breaks: L.append(f"| {b['date']} | {b['F']:.2f} | {b['p']:.3f} | {b['segment'][0]} → {b['segment'][1]} | {b['beta_before']:+.3f} | {b['beta_after']:+.3f} |")
    else:
        L.append("No break clears p < 0.05 on the whole sample.")
    L += ["", "Registered watershed dates (±26 weeks): " + ("; ".join(near) if near else "none of 2020-03-15, 2022-02-24, 2022-03-16 is within 26 weeks of a break found"), "",
          f"## Sweep — is the recent window different? best W = {sw.best['W']} weeks, z = {sw.best_stat:+.2f}; best-of-sweep null q95 {sw.q95:+.2f}; p_family {sw.p_family:.3f}", ""]
    out.write_text("\n".join(L) + "\n"); write_md(sw, DOCS / "era_liquidity_liquidity_sweep.md", fmt="{:+.2f}")
    out.with_suffix(".json").write_text(json.dumps(dict(eras=json.loads(tab.to_json(orient="records")), breaks=breaks, watershed_matches=near, sweep=sw.to_json()), indent=1, default=float))
    print(tab.to_string(index=False)); print("breaks:", breaks or "none"); print("watersheds:", near or "none"); print(f"recent-window sweep: best W {sw.best['W']}, z {sw.best_stat:+.2f}, q95 {sw.q95:+.2f}, p_family {sw.p_family:.3f}"); print(f"-> {out}")


# ---------------------------------------------------------------------------------------------------------------- P1
def _states() -> pd.Series:
    st = pd.read_parquet(PROC / "liquidity_states.parquet"); st.index = pd.to_datetime(st.index)
    if getattr(st.index, "tz", None) is not None: st.index = st.index.tz_localize(None)
    col = None
    for c in st.columns:
        if str(c).lower() in ("state", "stress", "liquidity_state", "regime", "label"): col = c; break
    if col is None:
        for c in st.columns:
            v = pd.Series(st[c]).dropna().unique()
            if len(v) <= 3 and set(np.asarray(v).astype(str)) <= {"0", "1", "0.0", "1.0", "True", "False", "stress", "abundant"}: col = c; break
    if col is None: raise SystemExit(f"liquidity_states.parquet: no state column recognised among {list(st.columns)} -- name it in _states()")
    s = st[col]
    if s.dtype == object: s = s.astype(str).str.lower().map({"stress": 1, "abundant": 0, "true": 1, "false": 0, "1": 1, "0": 0, "1.0": 1, "0.0": 0})
    return s.astype(float).rename("stress")


def cmd_p1():
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    if getattr(r.index, "tz", None) is not None: r.index = r.index.tz_localize(None)
    s = _states().reindex(r.index).ffill()
    d = pd.DataFrame(dict(gld=r["GLD"], spy=r["SPY"], stress=s)).dropna(); d["era"] = [era_of(i) for i in d.index]
    def gap(frame, win, lag):
        c = frame["gld"].rolling(win).corr(frame["spy"]); st_ = frame["stress"].shift(lag)
        m = c.notna() & st_.notna()
        if m.sum() < 250 or st_[m].sum() < 20 or (1 - st_[m]).sum() < 20: return np.nan, int(m.sum())
        return float(c[m & (st_ == 1)].mean() - c[m & (st_ == 0)].mean()), int(m.sum())
    rows = [dict(era="all", **dict(zip(("gap", "n"), gap(d, 20, 0))))] + [dict(era=e, **dict(zip(("gap", "n"), gap(d[d.era == e], 20, 0)))) for e in [e[0] for e in ERAS] if (d.era == e).any()]
    tab = pd.DataFrame(rows)
    roll = []
    for start in pd.date_range(d.index[0], d.index[-1] - pd.Timedelta(days=730), freq="13W"):
        sub = d[(d.index >= start) & (d.index < start + pd.Timedelta(days=730))]; g, n = gap(sub, 20, 0); roll.append(dict(start=str(start.date()), gap=g, n=n))
    roll = pd.DataFrame(roll)
    cells = grid(era=[e[0] for e in ERAS if (d.era == e[0]).any()] + ["all"], win=[10, 20, 40, 60], lag=[0, 5, 10])
    def stat(dd, c):
        frame = pd.DataFrame(dict(gld=dd["gld"], spy=dd["spy"], stress=dd["stress"]), index=d.index); frame["era"] = d["era"].to_numpy()
        if c["era"] != "all": frame = frame[frame.era == c["era"]]
        g, n = gap(frame, c["win"], c["lag"]); return (abs(g) if np.isfinite(g) else np.nan), n
    def null_gen(dd, rng):
        x = np.asarray(dd["stress"]); n = len(x); b = 60; starts = np.arange(0, n, b); order = rng.permutation(len(starts))
        idx = np.concatenate([np.arange(starts[j], min(starts[j] + b, n)) for j in order]); out = dict(dd); out["stress"] = x[idx]; return out
    sw = run(cells, stat, dict(gld=d["gld"].to_numpy(), spy=d["spy"].to_numpy(), stress=d["stress"].to_numpy()), null_gen, n_null=200, seed=SEED, label="P1 by era x correlation window x state lag (|stress − abundant| gap)")
    out = DOCS / "era_liquidity_p1.md"
    L = ["# P1 — gold's co-movement with equities in liquidity stress, by era", "",
         "Gap = mean 20-session GLD–SPY correlation in stress sessions − in abundant sessions (P1's statistic, 11 Aug: pooled +0.017, p 0.44). A positive gap = gold co-moves MORE in stress (the dash-for-cash reading); the safe-haven claim needs a negative one.", "",
         "| era | n sessions | gap |", "|---|---|---|"] + [f"| {r_['era']} | {r_['n']} | {r_['gap']:+.3f} |" if np.isfinite(r_['gap']) else f"| {r_['era']} | {r_['n']} | · (too few stress or abundant sessions) |" for _, r_ in tab.iterrows()]
    L += ["", "## Rolling two-year windows (stepped 13 weeks)", "", "| window start | n | gap |", "|---|---|---|"] + [f"| {r_['start']} | {r_['n']} | {r_['gap']:+.3f} |" if np.isfinite(r_["gap"]) else f"| {r_['start']} | {r_['n']} | · |" for _, r_ in roll.iterrows()]
    L += ["", f"## Sweep — |gap| over era × window × lag: best `{sw.best}` = {sw.best_stat:.3f}; best-of-sweep null q95 {sw.q95:.3f}; p_family {sw.p_family:.3f}", ""]
    out.write_text("\n".join(L) + "\n"); write_md(sw, DOCS / "era_liquidity_p1_sweep.md", axis_rows="era", axis_cols="win", fmt="{:.3f}")
    out.with_suffix(".json").write_text(json.dumps(dict(eras=json.loads(tab.to_json(orient="records")), rolling=json.loads(roll.to_json(orient="records")), sweep=sw.to_json()), indent=1, default=float))
    print(tab.to_string(index=False)); print(f"sweep: best {sw.best} |gap| {sw.best_stat:.3f}, q95 {sw.q95:.3f}, p_family {sw.p_family:.3f}"); print(f"-> {out}")


# ---------------------------------------------------------------------------------------------------------------- T-L5b grid
def _events(spy: np.ndarray, thr: float, look: int, cool: int, lo: int, hi: int) -> np.ndarray:
    dd = pd.Series(spy).rolling(look).sum().to_numpy(); ev = []; last = -10 ** 9
    for i in range(max(look, lo), hi):
        if dd[i] <= thr and dd[i - 1] > thr and i - last >= cool: ev.append(i); last = i
    return np.array(ev, int)


def cmd_selloff():
    from src.liquidity_link import gold_range
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    if getattr(r.index, "tz", None) is not None: r.index = r.index.tz_localize(None)
    spy, g, i0, i1 = gold_range(r); spy_v, gld_v = spy.to_numpy(), g.to_numpy(); dates = spy.index
    era_idx = np.array([era_of(d) for d in dates])
    cum = np.nancumsum(np.nan_to_num(gld_v));
    def fwd(starts, h): return cum[starts + h] - cum[starts]
    base_cache = {}
    def stat_factory(sign):
        def stat(d, c):
            gv = np.asarray(d["gld"]); cm = np.cumsum(np.nan_to_num(gv))
            thr, h, look, era = c["thr"], c["h"], c["look"], c["era"]
            ev = _events(spy_v, thr, look, 2 * look, i0, i1 - h)
            if era != "all": ev = ev[era_idx[ev] == era]
            if len(ev) < 30: return np.nan, len(ev)
            f = cm[ev + h] - cm[ev]; share = (f < 0).mean()
            allf = cm[h:] - cm[:-h]; m = np.ones(len(allf), bool); m[:i0] = False; m[i1 - h:] = False
            if era != "all": m &= (era_idx[:len(allf)] == era)
            base = (allf[m] < 0).mean() if m.sum() else np.nan
            return float(sign * (share - base) * 100), len(ev)
        return stat
    cells = grid(thr=[-0.04, -0.05, -0.06, -0.07, -0.08, -0.09, -0.10], h=[5, 7, 10, 13, 15, 20, 30], look=[10, 20, 40], era=["all"] + [e[0] for e in ERAS if (era_idx == e[0]).any()])
    data = dict(gld=gld_v)
    res = {}
    for name, sign in (("gold sold (share negative above base)", +1), ("gold bought (share negative below base)", -1)):
        res[name] = run(cells, stat_factory(sign), data, shift_null("gld", 250), n_null=200, seed=SEED, label=f"T-L5b grid — {name}", min_cells_valid=1)
        write_md(res[name], DOCS / f"era_liquidity_selloff_{'sold' if sign > 0 else 'bought'}.md", axis_rows="thr", axis_cols="h", fmt="{:+.1f}",
                 note="Statistic: share of negative forward GLD returns after an SPY sell-off minus the base rate, in points (cells with ≥ 30 events; others ·). Eras and look-backs as sections.")
        print(f"{name}: best {res[name].best} gap {res[name].best_stat:+.1f} pts (n {int(res[name].surface.loc[res[name].surface['stat'].idxmax(), 'n'])}); null q95 {res[name].q95:+.1f}; p_family {res[name].p_family:.3f}; survivors {len(res[name].survivors)}")
    (DOCS / "era_liquidity_selloff.json").write_text(json.dumps({k: v.to_json() for k, v in res.items()}, indent=1, default=float))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["liquidity", "p1", "selloff", "all"]); a = ap.parse_args()
    DOCS.mkdir(exist_ok=True)
    if a.cmd in ("liquidity", "all"): cmd_liquidity()
    if a.cmd in ("p1", "all"): cmd_p1()
    if a.cmd in ("selloff", "all"): cmd_selloff()
