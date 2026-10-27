"""T-L: is the liquidity-gold link constant through time? Weekly Fed net liquidity (WALCL - TGA - RRP, FRED) against GLD's weekly return.
T-L1 stability (sign share across 104-week windows); T-L2 change-point (sup-F, block-bootstrap null); T-L3 recent vs history; T-L4 by the P1 liquidity
state; T-L5 after an equity sell-off (the founder's sentence): conditional beta, and gold's forward return after SPY's 20-session drawdown crosses a
threshold, against the base rate with a random-date null.  docs/prereg_liquidity_and_chair.md section 2.
    python -m src.liquidity_link run ; python -m src.liquidity_link record"""
from __future__ import annotations
import json, os, re, sys, urllib.request, urllib.parse
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd

PROC, DOCS, DP = Path("processed"), Path("docs"), Path("data_provenance") / "liquidity"
FRED = "https://api.stlouisfed.org/fred/series/observations"
WIN, STEP, TRIM, BLOCK, NDRAW, SEED, STABLE = 104, 13, 0.15, 13, 500, 0, 0.80
PERIODS = [("2004-08", 2004, 2008), ("2009-14", 2009, 2014), ("2015-19", 2015, 2019), ("2020-21", 2020, 2021), ("2022-26", 2022, 2026)]
SELL = {"-5%": -0.05, "-8%": -0.08, "-10%": -0.10}; SELL_REG = "-8%"; LOOK, COOL, HORIZONS, NNULL = 20, 40, (5, 10, 20), 1000


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


def to_bn(s: pd.Series) -> tuple[pd.Series, str]:
    """FRED mixes units: WALCL and WTREGEN are millions, RRPONTSYD billions. A median above 50,000 is taken as millions (27 Oct units error)."""
    return (s / 1000.0, "millions -> bn") if s.abs().median() > 50_000 else (s, "bn")


def net_liquidity() -> pd.DataFrame | None:
    parts = {}
    for sid in ("WALCL", "WTREGEN", "RRPONTSYD"):
        s = fred(sid)
        if s is None:
            if sid == "RRPONTSYD": print("  RRPONTSYD missing; reverse repo taken as zero"); continue
            return None
        s, u = to_bn(s); parts[sid] = s; print(f"  {sid}: {u}; last {s.index[-1].date()} = {s.iloc[-1]:,.0f} bn")
    nl = parts["WALCL"].to_frame("walcl").join(parts["WTREGEN"].rename("tga"), how="inner")
    rr = parts.get("RRPONTSYD"); nl["rrp"] = rr.reindex(nl.index, method="ffill").fillna(0.0) if rr is not None else 0.0
    nl["NL"] = nl["walcl"] - nl["tga"] - nl["rrp"]; return nl


def weekly_pair(asset: str = "GLD"):
    nl = net_liquidity()
    if nl is None: raise SystemExit("  no net-liquidity series (FRED key or network)")
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    if getattr(r.index, "tz", None) is not None: r.index = r.index.tz_localize(None)
    y = r[asset].resample("W-WED").sum(min_count=1)
    dd = r["SPY"].rolling(LOOK).sum().resample("W-WED").last().shift(1).rename("dd") if "SPY" in r.columns else None   # SPY's trailing 20-session log return as of the previous Wednesday
    x = np.log(nl["NL"].where(nl["NL"] > 0)).diff()
    df = pd.concat([x.rename("x"), y.rename("y")] + ([dd] if dd is not None else []), axis=1, sort=True).dropna(subset=["x", "y"]); df = df[df.index >= "2004-11-24"]
    if len(df) < WIN:
        print(f"  too few overlapping weeks ({len(df)}): NL weeks {int(nl['NL'].notna().sum())}, NL <= 0 in {int((nl['NL'] <= 0).sum())}; NL {nl.index[0].date()} -> {nl.index[-1].date()}; {asset} weeks {int(y.notna().sum())}, {y.index[0].date()} -> {y.index[-1].date()}")
        raise SystemExit(1)
    return df, nl, r


def ols(x: np.ndarray, y: np.ndarray):
    n = len(x); xm, ym = x.mean(), y.mean(); sxx = ((x - xm) ** 2).sum(); b = ((x - xm) * (y - ym)).sum() / sxx if sxx > 0 else np.nan; a = ym - b * xm
    e = y - a - b * x; s2 = (e @ e) / max(n - 2, 1); se = float(np.sqrt(s2 / sxx)) if sxx > 0 else np.nan; return float(a), float(b), se, e


def _rss_prefix(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    cx, cy, cxx, cxy, cyy = [np.concatenate([[0.0], np.cumsum(v)]) for v in (x, y, x * x, x * y, y * y)]
    i = np.arange(len(x) + 1, dtype=float)
    with np.errstate(invalid="ignore", divide="ignore"):
        sxx = cxx - cx * cx / i; sxy = cxy - cx * cy / i; syy = cyy - cy * cy / i; rss = syy - sxy * sxy / sxx
    rss[:2] = np.nan; return rss


def sup_f(x: np.ndarray, y: np.ndarray, trim: float = TRIM) -> tuple[float, int]:
    """Quandt-Andrews sup-F for one break in (alpha, beta). Returns (sup F, index of the first point of the second segment)."""
    n = len(x); k = 2; R1 = _rss_prefix(x, y); R2 = _rss_prefix(x[::-1], y[::-1])[::-1]
    rss0 = R1[n]; lo, hi = int(np.floor(n * trim)), int(np.ceil(n * (1 - trim))); idx = np.arange(lo, hi)
    F = ((rss0 - R1[idx] - R2[idx]) / k) / ((R1[idx] + R2[idx]) / (n - 2 * k)); j = int(np.nanargmax(F)); return float(F[j]), int(idx[j])


def block_bootstrap_p(x, y, F_obs, n_draw=NDRAW, block=BLOCK, seed=SEED):
    a, b, _, e = ols(x, y); n = len(x); rng = np.random.default_rng(seed); out = np.empty(n_draw); nb = int(np.ceil(n / block))
    for d in range(n_draw):
        starts = rng.integers(0, n, nb); idx = (starts[:, None] + np.arange(block)[None, :]).ravel()[:n] % n
        out[d] = sup_f(x, a + b * x + e[idx])[0]
    return float((out >= F_obs).mean()), out


def sell_off_events(r: pd.DataFrame, thr: float):
    spy = r["SPY"].dropna(); g = r["GLD"].reindex(spy.index); dd = spy.rolling(LOOK).sum().to_numpy(); ev = []; last = -10 ** 9
    for i in range(LOOK, len(spy) - max(HORIZONS) - 1):
        if dd[i] <= thr and dd[i - 1] > thr and i - last >= COOL: ev.append(i); last = i
    return ev, g


def event_test(r: pd.DataFrame, thr: float, rng) -> tuple[list, dict]:
    ev, g = sell_off_events(r, thr); gv = g.to_numpy(); out = {}
    def fwd(starts, h): return np.array([np.nansum(gv[i + 1:i + 1 + h]) for i in starts])
    for h in HORIZONS:
        f = fwd(ev, h); n = len(f); share = float((f < 0).mean()) if n else np.nan
        allv = g.rolling(h).sum().shift(-h).dropna(); base = float((allv < 0).mean()); gap = (share - base) * 100 if n else np.nan
        pool = np.arange(LOOK, len(gv) - h - 1); nulls = np.array([(fwd(rng.choice(pool, n, replace=False), h) < 0).mean() for _ in range(NNULL)]) if n else np.array([])
        p = float((nulls >= share).mean()) if n else np.nan
        verdict = "INCONCLUSIVE (n < 30)" if n < 30 else ("PASS" if (gap >= 10 and p < 0.05) else "FAIL")
        out[h] = dict(n=n, share_neg=share, base_neg=base, gap_pts=gap, p=p, median=float(np.median(f)) if n else np.nan, verdict=verdict)
    return ev, out


def run(asset: str = "GLD"):
    df, nl, r = weekly_pair(asset); X, Y = df["x"].to_numpy(), df["y"].to_numpy(); n = len(X); dates = df.index
    a, b, se, e = ols(X, Y); t_pool = b / se
    rows = []
    for s0 in range(0, n - WIN + 1, STEP):
        _, bw, sew, _ = ols(X[s0:s0 + WIN], Y[s0:s0 + WIN]); rows.append(dict(start=dates[s0], end=dates[s0 + WIN - 1], beta=bw, t=bw / sew))
    W = pd.DataFrame(rows); pos = float((W.beta > 0).mean()); share = max(pos, 1 - pos); maj = "+" if pos >= 0.5 else "-"
    F_obs, j = sup_f(X, Y); p_break, null = block_bootstrap_p(X, Y, F_obs); bdate = dates[j]
    _, b1, se1, _ = ols(X[:j], Y[:j]); _, b2, se2, _ = ols(X[j:], Y[j:])
    _, b_last, se_last, _ = ols(X[-WIN:], Y[-WIN:]); earlier = W[W.end < dates[-WIN]].beta
    lo5, hi95 = (float(np.percentile(earlier, 5)), float(np.percentile(earlier, 95))) if len(earlier) >= 5 else (np.nan, np.nan)
    recent_diff = bool(len(earlier) >= 5 and (b_last < lo5 or b_last > hi95))
    per = []
    for lab, y0, y1 in PERIODS:
        m = (dates.year >= y0) & (dates.year <= y1)
        if m.sum() >= 30: _, bp, sep, _ = ols(X[m], Y[m]); per.append(dict(period=lab, n=int(m.sum()), beta=bp, t=bp / sep))
    cond = None; fs = PROC / "liquidity_states.parquet"
    if fs.exists():
        try:
            L = pd.read_parquet(fs); L.index = pd.to_datetime(L.index); col = next((c for c in L.columns if "stress" in c.lower()), None)
            if col is not None:
                st = L[col].astype(float).resample("W-WED").mean().reindex(dates); m1 = (st > 0.5).to_numpy(); m0 = (st <= 0.5).to_numpy()
                if m1.sum() >= 30 and m0.sum() >= 30:
                    _, bs, ses, _ = ols(X[m1], Y[m1]); _, ba, sea, _ = ols(X[m0], Y[m0]); cond = dict(col=col, n_stress=int(m1.sum()), beta_stress=bs, t_stress=bs / ses, n_abundant=int(m0.sum()), beta_abundant=ba, t_abundant=ba / sea)
            else: cond = dict(note=f"no stress column in liquidity_states.parquet (columns {list(L.columns)[:6]})")
        except Exception as ex: cond = dict(note=f"liquidity_states.parquet not usable ({type(ex).__name__})")
    # T-L5 — after an equity sell-off
    rng = np.random.default_rng(SEED); after = None; events = {}
    if "dd" in df.columns:
        m_a = (df["dd"] <= SELL[SELL_REG]).to_numpy(); m_o = ~m_a
        if m_a.sum() >= 20: _, ba5, sea5, _ = ols(X[m_a], Y[m_a]); _, bo5, seo5, _ = ols(X[m_o], Y[m_o]); after = dict(thr=SELL_REG, n_after=int(m_a.sum()), beta_after=ba5, t_after=ba5 / sea5, n_other=int(m_o.sum()), beta_other=bo5, t_other=bo5 / seo5, diff_t=(ba5 - bo5) / float(np.sqrt(sea5 ** 2 + seo5 ** 2)))
        else: after = dict(thr=SELL_REG, n_after=int(m_a.sum()), note="fewer than 20 weeks after a sell-off")
        for lab, thr in SELL.items():
            ev, out = event_test(r, thr, rng); events[lab] = dict(n_events=len(ev), by_h={str(h): v for h, v in out.items()})
    v1 = "STABLE" if share >= STABLE else "UNSTABLE"; v2 = "BREAK" if p_break < 0.05 else "no break"
    reg = events.get(SELL_REG, {}).get("by_h", {}).get("20"); v5 = reg["verdict"] if reg else "not run"
    L = [f"# T-L — the liquidity–gold link through time ({asset})", "",
         f"*{datetime.now():%Y-%m-%d %H:%M}. {n} weeks, {dates[0].date()} → {dates[-1].date()}; x = weekly Δlog(Fed assets − TGA − RRP), y = {asset} weekly log return, Thursday-to-Wednesday; contemporaneous, not a trading signal. Net liquidity now {nl['NL'].iloc[-1]:,.0f} bn ({nl.index[-1].date()}). prereg_liquidity_and_chair §2.*", "",
         f"**Pooled:** β = {b:+.3f} (t {t_pool:+.2f}) — a 1% weekly rise in net liquidity goes with {b:+.3f}% on {asset} the same week.", "",
         f"**T-L1 stability:** {len(W)} windows of {WIN} weeks; majority sign {maj}, share {share:.0%} → **{v1}** (bar {STABLE:.0%}).", "",
         f"**T-L2 change-point:** sup-F {F_obs:.2f} at {bdate.date()}; bootstrap null median {np.median(null):.2f}, 95th {np.percentile(null, 95):.2f}; **p = {p_break:.3f} → {v2}**. β before {b1:+.3f} (t {b1 / se1:+.2f}), after {b2:+.3f} (t {b2 / se2:+.2f}).", "",
         f"**T-L3 recent-only:** last {WIN} weeks β = {b_last:+.3f} (t {b_last / se_last:+.2f}); earlier windows' 5–95% range {lo5:+.3f} to {hi95:+.3f} → " + ("**recent is different** (outside the range)" if recent_diff else "inside the range — nothing new"), ""]
    if cond and "beta_stress" in cond: L += [f"**T-L4 conditional (P1 state '{cond['col']}'):** stress weeks β = {cond['beta_stress']:+.3f} (t {cond['t_stress']:+.2f}, n {cond['n_stress']}); abundant weeks β = {cond['beta_abundant']:+.3f} (t {cond['t_abundant']:+.2f}, n {cond['n_abundant']}).", ""]
    elif cond: L += [f"T-L4: {cond['note']}", ""]
    if after and "beta_after" in after:
        L += [f"**T-L5a after an equity sell-off (SPY's trailing 20 sessions ≤ {SELL_REG} at the week's start):** β = {after['beta_after']:+.3f} (t {after['t_after']:+.2f}, n {after['n_after']} weeks) vs other weeks {after['beta_other']:+.3f} (t {after['t_other']:+.2f}, n {after['n_other']}); difference t = {after['diff_t']:+.2f}.", ""]
    elif after: L += [f"T-L5a: {after['note']} (n {after['n_after']})", ""]
    if events:
        L += [f"**T-L5b gold after SPY's 20-session drawdown first crosses the threshold (one event per {COOL} sessions; share of forward returns negative vs the base rate; random-date null, {NNULL:,} draws). Registered cell: {SELL_REG}, 20 sessions → {v5}.**", "",
              "| threshold | events | horizon | share negative | base rate | gap (pts) | median | p | verdict |", "|---|---|---|---|---|---|---|---|---|"]
        for lab, ev in events.items():
            for h, v in ev["by_h"].items(): L.append(f"| {lab} | {ev['n_events']} | {h} | {v['share_neg']:.0%} | {v['base_neg']:.0%} | {v['gap_pts']:+.0f} | {v['median']:+.2%} | {v['p']:.3f} | {v['verdict']} |" if v["n"] else f"| {lab} | 0 | {h} | — | — | — | — | — | no events |")
        L.append("")
    L += ["| period | n weeks | β | t |", "|---|---|---|---|"] + [f"| {q['period']} | {q['n']} | {q['beta']:+.3f} | {q['t']:+.2f} |" for q in per]
    L += ["", "| window start | end | β | t |", "|---|---|---|---|"] + [f"| {q.start.date()} | {q.end.date()} | {q.beta:+.3f} | {q.t:+.2f} |" for q in W.itertuples()]
    out = DOCS / f"liquidity_link_{asset}.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L[:26])); print(f"-> {out}")
    J = json.loads((PROC / "liquidity_link.json").read_text()) if (PROC / "liquidity_link.json").exists() else {}
    J[asset] = dict(run=datetime.now().strftime("%Y-%m-%d %H:%M"), n=n, start=str(dates[0].date()), end=str(dates[-1].date()), beta=b, t=t_pool, TL1=dict(windows=len(W), share=share, majority=maj, verdict=v1),
                    TL2=dict(supF=F_obs, date=str(bdate.date()), p=p_break, beta_before=b1, beta_after=b2, verdict=v2), TL3=dict(beta_last=b_last, lo5=lo5, hi95=hi95, recent_is_different=recent_diff),
                    TL4=cond, TL5a=after, TL5b=events, TL5_verdict=v5, periods=per,
                    nl_latest=dict(date=str(nl.index[-1].date()), NL_bn=float(nl["NL"].iloc[-1]), walcl_bn=float(nl["walcl"].iloc[-1]), tga_bn=float(nl["tga"].iloc[-1]), rrp_bn=float(nl["rrp"].iloc[-1])))
    (PROC / "liquidity_link.json").write_text(json.dumps(J, indent=1, default=float))


def _bump_tally(text: str, note: str) -> str:
    m = re.search(r"tally (\d+) \(#40–#43 lever priors", text)
    if not m: return text
    k = int(m.group(1)) + 1; text = text.replace(m.group(0), f"tally {k} (#40–#43 lever priors", 1)
    anchor = "#78 chairs differ (p 0.016)"; return text.replace(anchor, anchor + ", " + note, 1) if anchor in text else text


def record(asset: str = "GLD"):
    """Write T-L's verdicts against prior #76 into the register, the pre-registration and the state record."""
    J = json.loads((PROC / "liquidity_link.json").read_text())[asset]; t1, t2, t3, t5 = J["TL1"], J["TL2"], J["TL3"], J.get("TL5b", {}).get(SELL_REG, {}).get("by_h", {}).get("20")
    clauses = dict(pooled_small_positive=(J["beta"] > 0 and abs(J["t"]) < 3), unstable=(t1["verdict"] == "UNSTABLE"), no_break=(t2["verdict"] == "no break"), nothing_new=(not t3["recent_is_different"]))
    right76 = all(clauses.values()); missed = [k for k, v in clauses.items() if not v]
    right80 = bool(t5 and t5["verdict"] != "PASS")
    pri = ("**#76 right**" if right76 else f"**#76 wrong** ({', '.join(missed)} did not hold)") + "; " + ("**#80 right**" if right80 else "**#80 wrong** (gold is sold after an equity sell-off more often than the base rate)")
    res = (f"{J['n']} weeks {J['start']} → {J['end']}: pooled β {J['beta']:+.3f} (t {J['t']:+.2f}); T-L1 {t1['share']:.0%} windows share the majority sign ({t1['majority']}) → {t1['verdict']}; "
           f"T-L2 sup-F {t2['supF']:.2f} at {t2['date']}, p {t2['p']:.3f} → {t2['verdict']} (β {t2['beta_before']:+.3f} → {t2['beta_after']:+.3f}); T-L3 last two years β {t3['beta_last']:+.3f} vs range {t3['lo5']:+.3f}..{t3['hi95']:+.3f} → "
           + ("recent is different" if t3["recent_is_different"] else "nothing new") + (f"; T-L5b ({SELL_REG}, 20 sessions): {t5['n']} events, {t5['share_neg']:.0%} negative vs base {t5['base_neg']:.0%} (gap {t5['gap_pts']:+.0f} pts, p {t5['p']:.3f}) → {t5['verdict']}" if t5 else ""))
    a5 = J.get("TL5a") or {}
    if "beta_after" in a5: res += f"; T-L5a β after a sell-off {a5['beta_after']:+.3f} (n {a5['n_after']}) vs other weeks {a5['beta_other']:+.3f}, difference t {a5['diff_t']:+.2f}"
    p = DOCS / "prereg_liquidity_and_chair.md"; s = p.read_text()
    if f"| {datetime.now():%Y-%m-%d} | T-L ({asset}) |" not in s:
        s = s.rstrip("\n") + f"\n| {datetime.now():%Y-%m-%d} | T-L ({asset}) | {res}. docs/liquidity_link_{asset}.md | {pri} |\n"; p.write_text(s); print("  prereg: T-L result row")
    m = DOCS / "PROJECT_MASTER.md"; s = m.read_text(); old = "| registered 27 Oct, not run; prior #76: unstable, no break, nothing new | — |"
    if old in s:
        s = s.replace(old, f"| 27 Oct, {J['n']} weeks | **T-L1 {t1['verdict']} ({t1['share']:.0%}), T-L2 {t2['verdict']} (p {t2['p']:.2f}), T-L3 " + ("recent differs" if t3["recent_is_different"] else "nothing new") + (f", T-L5b {t5['verdict']}" if t5 else "") + f"** — {pri} |", 1)
        if not right76: s = _bump_tally(s, "#76 liquidity link")
        if not right80: s = _bump_tally(s, "#80 gold after equity sell-offs")
        ph = "[T-L: registered, result to be written by `liquidity_link record`.]"
        if ph in s: s = s.replace(ph, f"T-L: {res} ({pri.replace('**', '')}).", 1)
        m.write_text(s); print("  MASTER: row 51 result" + ("" if right76 else ", tally advanced"))
    cs = DOCS / "CURRENT_STATE_2026-08-23.md"; s = cs.read_text()
    if "T-L result:" not in s: cs.write_text(s.rstrip("\n") + f"\n\nT-L result ({datetime.now():%d %b}): {res}. {pri.replace('**', '')}.\n"); print("  CURRENT_STATE: T-L line")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run": run(sys.argv[2] if len(sys.argv) > 2 else "GLD")
    elif cmd == "record": record(sys.argv[2] if len(sys.argv) > 2 else "GLD")
    elif cmd == "levels":
        nl = net_liquidity(); print(nl.tail(8).round(0)) if nl is not None else print("  none")
