"""T-L: is the liquidity-gold link constant through time? Weekly Fed net liquidity (WALCL - TGA - RRP, FRED) against GLD's weekly return.
Stability (sign share across 104-week windows), change-point (sup-F, block-bootstrap null), recent-vs-history, conditional on the P1 liquidity state.
docs/prereg_liquidity_and_chair.md section 2.   python -m src.liquidity_link run"""
from __future__ import annotations
import json, os, sys, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd

PROC, DOCS, DP = Path("processed"), Path("docs"), Path("data_provenance") / "liquidity"
FRED = "https://api.stlouisfed.org/fred/series/observations"
WIN, STEP, TRIM, BLOCK, NDRAW, SEED, STABLE = 104, 13, 0.15, 13, 500, 0, 0.80
PERIODS = [("2004-08", 2004, 2008), ("2009-14", 2009, 2014), ("2015-19", 2015, 2019), ("2020-21", 2020, 2021), ("2022-26", 2022, 2026)]


def fred_key() -> str:
    env = Path(".env")
    if env.exists():
        for ln in env.read_text().splitlines():
            if ln.startswith("FRED_API_KEY="): return ln.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("FRED_API_KEY", "")


def fred(sid: str, start: str = "2000-01-01", refresh: bool = True) -> pd.Series | None:
    """One FRED series, cached as data_provenance/liquidity/<id>.csv (the file on disk is the record)."""
    DP.mkdir(parents=True, exist_ok=True); f = DP / f"{sid}.csv"
    if refresh or not f.exists():
        try:
            q = urllib.parse.urlencode(dict(series_id=sid, api_key=fred_key(), file_type="json", observation_start=start))
            j = json.loads(urllib.request.urlopen(f"{FRED}?{q}", timeout=60).read())
            pd.DataFrame(j["observations"])[["date", "value"]].to_csv(f, index=False)
        except Exception as e:
            print(f"  FRED {sid}: fetch failed ({type(e).__name__}: {e})" + ("; using the cached file" if f.exists() else ""))
            if not f.exists(): return None
    df = pd.read_csv(f); s = pd.Series(pd.to_numeric(df["value"], errors="coerce").to_numpy(), index=pd.to_datetime(df["date"])).dropna(); s.name = sid
    return s


def net_liquidity() -> pd.DataFrame | None:
    w, t, r = fred("WALCL"), fred("WTREGEN"), fred("RRPONTSYD")
    if w is None or t is None: return None
    nl = (w / 1000.0).to_frame("walcl").join(t.rename("tga"), how="inner")
    nl["rrp"] = (r.reindex(nl.index, method="ffill") if r is not None else 0.0); nl["rrp"] = nl["rrp"].fillna(0.0)
    nl["NL"] = nl["walcl"] - nl["tga"] - nl["rrp"]; return nl


def weekly_pair(asset: str = "GLD") -> tuple[pd.Series, pd.Series, pd.DataFrame]:
    nl = net_liquidity()
    if nl is None: raise SystemExit("  no net-liquidity series (FRED key or network)")
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index); y = r[asset].resample("W-WED").sum(min_count=1)
    x = np.log(nl["NL"]).diff(); x.index = pd.to_datetime(x.index)
    df = pd.concat([x.rename("x"), y.rename("y")], axis=1).dropna(); df = df[df.index >= "2004-11-24"]
    return df["x"], df["y"], nl


def ols(x: np.ndarray, y: np.ndarray):
    n = len(x); xm, ym = x.mean(), y.mean(); sxx = ((x - xm) ** 2).sum(); b = ((x - xm) * (y - ym)).sum() / sxx; a = ym - b * xm
    e = y - a - b * x; s2 = (e @ e) / max(n - 2, 1); se = float(np.sqrt(s2 / sxx)); return float(a), float(b), se, e


def _rss_prefix(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """RSS of the simple regression on the first i points, i = 0..n (NaN where i < 2)."""
    cx, cy, cxx, cxy, cyy = [np.concatenate([[0.0], np.cumsum(v)]) for v in (x, y, x * x, x * y, y * y)]
    i = np.arange(len(x) + 1, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        sxx = cxx - cx * cx / i; sxy = cxy - cx * cy / i; syy = cyy - cy * cy / i; rss = syy - sxy * sxy / sxx
    rss[:2] = np.nan; return rss


def sup_f(x: np.ndarray, y: np.ndarray, trim: float = TRIM) -> tuple[float, int]:
    """Quandt-Andrews sup-F for one break in (alpha, beta), trimming `trim` at both ends. Returns (sup F, break index = first point of the second segment)."""
    n = len(x); k = 2; R1 = _rss_prefix(x, y); R2 = _rss_prefix(x[::-1], y[::-1])[::-1]   # R2[i] = RSS of points i..n-1
    rss0 = R1[n]; lo, hi = int(np.floor(n * trim)), int(np.ceil(n * (1 - trim))); idx = np.arange(lo, hi)
    F = ((rss0 - R1[idx] - R2[idx]) / k) / ((R1[idx] + R2[idx]) / (n - 2 * k)); j = int(np.nanargmax(F)); return float(F[j]), int(idx[j])


def block_bootstrap_p(x: np.ndarray, y: np.ndarray, F_obs: float, n_draw: int = NDRAW, block: int = BLOCK, seed: int = SEED) -> tuple[float, np.ndarray]:
    """Null of a constant (alpha, beta): regenerate y from the pooled fit with circular block-bootstrapped residuals; sup-F each draw."""
    a, b, _, e = ols(x, y); n = len(x); rng = np.random.default_rng(seed); out = np.empty(n_draw); nb = int(np.ceil(n / block))
    for d in range(n_draw):
        starts = rng.integers(0, n, nb); idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n] % n
        out[d] = sup_f(x, a + b * x + e[idx])[0]
    return float((out >= F_obs).mean()), out


def run(asset: str = "GLD"):
    x, y, nl = weekly_pair(asset); X, Y = x.to_numpy(), y.to_numpy(); n = len(X); dates = x.index
    a, b, se, e = ols(X, Y); t_pool = b / se
    # T-L1 stability
    rows = []
    for s0 in range(0, n - WIN + 1, STEP):
        _, bw, sew, _ = ols(X[s0:s0 + WIN], Y[s0:s0 + WIN]); rows.append(dict(start=dates[s0], end=dates[s0 + WIN - 1], beta=bw, t=bw / sew))
    W = pd.DataFrame(rows); pos = float((W.beta > 0).mean()); share = max(pos, 1 - pos); maj = "+" if pos >= 0.5 else "-"
    # T-L2 change-point
    F_obs, j = sup_f(X, Y); p_break, null = block_bootstrap_p(X, Y, F_obs); bdate = dates[j]
    _, b1, se1, _ = ols(X[:j], Y[:j]); _, b2, se2, _ = ols(X[j:], Y[j:])
    # T-L3 recent vs history
    _, b_last, se_last, _ = ols(X[-WIN:], Y[-WIN:]); earlier = W[W.end < dates[-WIN]].beta; lo5, hi95 = (np.percentile(earlier, 5), np.percentile(earlier, 95)) if len(earlier) >= 5 else (np.nan, np.nan)
    recent_diff = bool(len(earlier) >= 5 and (b_last < lo5 or b_last > hi95))
    # sub-periods
    per = []
    for lab, y0, y1 in PERIODS:
        m = (dates.year >= y0) & (dates.year <= y1)
        if m.sum() >= 30: _, bp, sep, _ = ols(X[m], Y[m]); per.append(dict(period=lab, n=int(m.sum()), beta=bp, t=bp / sep))
    # T-L4 conditional on the P1 liquidity state
    cond = None; fs = PROC / "liquidity_states.parquet"
    if fs.exists():
        try:
            L = pd.read_parquet(fs); L.index = pd.to_datetime(L.index)
            col = next((c for c in L.columns if "stress" in c.lower()), None)
            if col is not None:
                st = L[col].astype(float).resample("W-WED").mean().reindex(dates); m1 = (st > 0.5).to_numpy(); m0 = (st <= 0.5).to_numpy()
                if m1.sum() >= 30 and m0.sum() >= 30:
                    _, bs, ses, _ = ols(X[m1], Y[m1]); _, ba, sea, _ = ols(X[m0], Y[m0]); cond = dict(col=col, n_stress=int(m1.sum()), beta_stress=bs, t_stress=bs / ses, n_abundant=int(m0.sum()), beta_abundant=ba, t_abundant=ba / sea)
            else: cond = dict(note=f"no stress column in liquidity_states.parquet (columns {list(L.columns)[:6]})")
        except Exception as ex: cond = dict(note=f"liquidity_states.parquet not usable ({type(ex).__name__})")
    v1 = "STABLE" if share >= STABLE else "UNSTABLE"; v2 = "BREAK" if p_break < 0.05 else "no break"
    L = [f"# T-L — the liquidity–gold link through time ({asset})", "",
         f"*{datetime.now():%Y-%m-%d %H:%M}. {n} weeks, {dates[0].date()} → {dates[-1].date()}; x = weekly Δlog(Fed assets − TGA − RRP), y = {asset} weekly log return, Thursday-to-Wednesday; contemporaneous, not a trading signal. prereg_liquidity_and_chair §2.*", "",
         f"**Pooled:** β = {b:+.3f} (t {t_pool:+.2f}) — a 1% weekly rise in net liquidity goes with {b:+.3f}% on {asset} the same week.", "",
         f"**T-L1 stability:** {len(W)} windows of {WIN} weeks; majority sign {maj}, share {share:.0%} → **{v1}** (bar {STABLE:.0%}).", "",
         f"**T-L2 change-point:** sup-F {F_obs:.2f} at {bdate.date()}; bootstrap null median {np.median(null):.2f}, 95th {np.percentile(null, 95):.2f}; **p = {p_break:.3f} → {v2}**. β before {b1:+.3f} (t {b1 / se1:+.2f}), after {b2:+.3f} (t {b2 / se2:+.2f}).", "",
         f"**T-L3 recent-only:** last {WIN} weeks β = {b_last:+.3f} (t {b_last / se_last:+.2f}); earlier windows' 5–95% range {lo5:+.3f} to {hi95:+.3f} → " + ("**recent is different** (outside the range)" if recent_diff else "inside the range — nothing new"), ""]
    if cond and "beta_stress" in cond:
        L += [f"**T-L4 conditional (P1 state '{cond['col']}'):** stress weeks β = {cond['beta_stress']:+.3f} (t {cond['t_stress']:+.2f}, n {cond['n_stress']}); abundant weeks β = {cond['beta_abundant']:+.3f} (t {cond['t_abundant']:+.2f}, n {cond['n_abundant']}).", ""]
    elif cond: L += [f"T-L4: {cond['note']}", ""]
    L += ["| period | n weeks | β | t |", "|---|---|---|---|"] + [f"| {q['period']} | {q['n']} | {q['beta']:+.3f} | {q['t']:+.2f} |" for q in per]
    L += ["", "| window start | end | β | t |", "|---|---|---|---|"] + [f"| {q.start.date()} | {q.end.date()} | {q.beta:+.3f} | {q.t:+.2f} |" for q in W.itertuples()]
    out = DOCS / f"liquidity_link_{asset}.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L[:14])); print(f"-> {out}")
    J = json.loads((PROC / "liquidity_link.json").read_text()) if (PROC / "liquidity_link.json").exists() else {}
    J[asset] = dict(run=datetime.now().strftime("%Y-%m-%d %H:%M"), n=n, start=str(dates[0].date()), end=str(dates[-1].date()), beta=b, t=t_pool, TL1=dict(windows=len(W), share=share, majority=maj, verdict=v1),
                    TL2=dict(supF=F_obs, date=str(bdate.date()), p=p_break, beta_before=b1, beta_after=b2, verdict=v2), TL3=dict(beta_last=b_last, lo5=float(lo5), hi95=float(hi95), recent_is_different=recent_diff),
                    TL4=cond, periods=per, nl_latest=dict(date=str(nl.index[-1].date()), NL_bn=float(nl["NL"].iloc[-1]), walcl_bn=float(nl["walcl"].iloc[-1]), tga_bn=float(nl["tga"].iloc[-1]), rrp_bn=float(nl["rrp"].iloc[-1])))
    (PROC / "liquidity_link.json").write_text(json.dumps(J, indent=1, default=float))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run": run(sys.argv[2] if len(sys.argv) > 2 else "GLD")
    elif cmd == "levels":
        nl = net_liquidity(); print(nl.tail(8).round(0)) if nl is not None else print("  none")
