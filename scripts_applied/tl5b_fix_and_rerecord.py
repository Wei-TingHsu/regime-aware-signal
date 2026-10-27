"""27 Oct, 23:50. A data error in T-L5b: the panel starts in 1995 and GLD in Nov 2004, so equity sell-offs before GLD existed (21 of 64 at -5%, 10 of 30 at -8%,
7 of 23 at -10%) were counted as zero gold returns — the medians printed as exactly 0.00% exposed it; the random-date null drew from the same pre-GLD dates.
Fix: events and the null's date pool restricted to GLD's history; the re-run replaces the written records (record() now replaces rows instead of skipping);
#80 is re-judged clause by clause. Also T-K2 in volatility units — the scale on which chairs are exchangeable (T-K1' FAIL) — so the page's chair posterior
does not borrow a between-chair variance that was the yield era's scale. Module v2 files kept in scripts_applied/superseded/.
Run from the repo root:  python scripts_applied/tl5b_fix_and_rerecord.py
then:  python -m src.liquidity_link run ; python -m src.liquidity_link record ; python -m src.chair_power run ; python -m src.chair_power record"""
from pathlib import Path
import ast, re, shutil

DOCS = Path("docs"); TODAY = "2026-10-27"
print("  tl5b_fix_and_rerecord: applying (the earlier attempt at 23:57 ran without this file -- commit 6b1e44a's message described a fix that had not run)")
sup = Path("scripts_applied/superseded"); sup.mkdir(parents=True, exist_ok=True)
# the 23:57 re-run of the v2 modules appended duplicate result lines to CURRENT_STATE (its guard looked for "T-L result:" but the lines read "T-L result (27 Oct)"): keep the first of each, the v3 record() then replaces it
cs = DOCS / "CURRENT_STATE_2026-08-23.md"; s = cs.read_text(); out, seen, dropped = [], set(), 0
for ln in s.split("\n"):
    key = next((k for k in ("T-L result (", "T-K1′ result (") if ln.startswith(k)), None)
    if key and key in seen: dropped += 1; continue
    if key: seen.add(key)
    out.append(ln)
if dropped: cs.write_text(re.sub(r"\n{3,}", "\n\n", "\n".join(out))); print(f"  CURRENT_STATE: {dropped} duplicated result line(s) from the 23:57 run removed (exact repeats of the line kept)")
for f, g in (("src/liquidity_link.py", "liquidity_link_v2_27oct_preGLD_events.py"), ("src/chair_power.py", "chair_power_v2_27oct.py")):
    if Path(f).exists() and not (sup / g).exists(): shutil.copy(f, sup / g); print(f"  kept {f} -> {sup / g}")

# ---------------------------------------------------------------- 1. src/liquidity_link.py v3
Path("src/liquidity_link.py").write_text(r'''"""T-L: is the liquidity-gold link constant through time? Weekly Fed net liquidity (WALCL - TGA - RRP, FRED) against GLD's weekly return.
T-L1 stability (sign share across 104-week windows); T-L2 change-point (sup-F, block-bootstrap null); T-L3 recent vs history; T-L4 by the P1 liquidity
state; T-L5 after an equity sell-off (the founder's sentence): conditional beta, and gold's forward return after SPY's 20-session drawdown crosses a
threshold, against the base rate with a random-date null -- events and null dates restricted to GLD's history (v3).  docs/prereg_liquidity_and_chair.md section 2.
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


def gold_range(r: pd.DataFrame):
    """SPY's sessions with GLD's valid history: (spy, gld on spy's index, first valid index, last valid index)."""
    spy = r["SPY"].dropna(); g = r["GLD"].reindex(spy.index); v = g.notna().to_numpy(); i0 = int(np.argmax(v)); i1 = len(v) - 1 - int(np.argmax(v[::-1])); return spy, g, i0, i1


def sell_off_events(r: pd.DataFrame, thr: float):
    """First session on which SPY's 20-session log return crosses below thr, one event per COOL sessions, only where GLD exists for the full forward window (v3)."""
    spy, g, i0, i1 = gold_range(r); dd = spy.rolling(LOOK).sum().to_numpy(); ev = []; last = -10 ** 9
    for i in range(max(LOOK, i0), i1 - max(HORIZONS)):
        if dd[i] <= thr and dd[i - 1] > thr and i - last >= COOL: ev.append(i); last = i
    return ev, g, i0, i1


def event_test(r: pd.DataFrame, thr: float, rng) -> tuple[list, dict]:
    ev, g, i0, i1 = sell_off_events(r, thr); gv = g.to_numpy(); out = {}
    def fwd(starts, h): return np.array([np.nansum(gv[i + 1:i + 1 + h]) for i in starts])
    for h in HORIZONS:
        f = fwd(ev, h); n = len(f); share = float((f < 0).mean()) if n else np.nan
        allv = g.rolling(h).sum().shift(-h).dropna(); base = float((allv < 0).mean()); gap = (share - base) * 100 if n else np.nan
        pool = np.arange(max(LOOK, i0), i1 - h); nulls = np.array([(fwd(rng.choice(pool, n, replace=False), h) < 0).mean() for _ in range(NNULL)]) if n else np.array([])
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
    _, b1, se1, _ = ols(X[:j], Y[:j]); _, b2, se2, _ = ols(X[j:], Y[j:]); sdx1, sdx2 = float(X[:j].std()), float(X[j:].std())
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
    rng = np.random.default_rng(SEED); after = None; events = {}
    if "dd" in df.columns:
        m_a = (df["dd"] <= SELL[SELL_REG]).to_numpy(); m_o = ~m_a
        if m_a.sum() >= 20: _, ba5, sea5, _ = ols(X[m_a], Y[m_a]); _, bo5, seo5, _ = ols(X[m_o], Y[m_o]); after = dict(thr=SELL_REG, n_after=int(m_a.sum()), beta_after=ba5, t_after=ba5 / sea5, n_other=int(m_o.sum()), beta_other=bo5, t_other=bo5 / seo5, diff_t=(ba5 - bo5) / float(np.sqrt(sea5 ** 2 + seo5 ** 2)))
        else: after = dict(thr=SELL_REG, n_after=int(m_a.sum()), note="fewer than 20 weeks after a sell-off")
        _, _, i0, i1 = gold_range(r); gstart, gend = r["SPY"].dropna().index[i0].date(), r["SPY"].dropna().index[i1].date()
        for lab, thr in SELL.items():
            ev, out = event_test(r, thr, rng); events[lab] = dict(n_events=len(ev), by_h={str(h): v for h, v in out.items()})
    v1 = "STABLE" if share >= STABLE else "UNSTABLE"; v2 = "BREAK" if p_break < 0.05 else "no break"
    reg = events.get(SELL_REG, {}).get("by_h", {}).get("20"); v5 = reg["verdict"] if reg else "not run"
    L = [f"# T-L — the liquidity–gold link through time ({asset})", "",
         f"*{datetime.now():%Y-%m-%d %H:%M}. {n} weeks, {dates[0].date()} → {dates[-1].date()}; x = weekly Δlog(Fed assets − TGA − RRP), y = {asset} weekly log return, Thursday-to-Wednesday; contemporaneous, not a trading signal. Net liquidity now {nl['NL'].iloc[-1]:,.0f} bn ({nl.index[-1].date()}). prereg_liquidity_and_chair §2.*", "",
         f"**Pooled:** β = {b:+.3f} (t {t_pool:+.2f}) — a 1% weekly rise in net liquidity goes with {b:+.3f}% on {asset} the same week.", "",
         f"**T-L1 stability:** {len(W)} windows of {WIN} weeks; majority sign {maj}, share {share:.0%} → **{v1}** (bar {STABLE:.0%}).", "",
         f"**T-L2 change-point:** sup-F {F_obs:.2f} at {bdate.date()}; bootstrap null median {np.median(null):.2f}, 95th {np.percentile(null, 95):.2f}; **p = {p_break:.3f} → {v2}**. β before {b1:+.3f} (t {b1 / se1:+.2f}), after {b2:+.3f} (t {b2 / se2:+.2f}); weekly sd of Δlog net liquidity before {sdx1:.2%}, after {sdx2:.2%}.", "",
         f"**T-L3 recent-only:** last {WIN} weeks β = {b_last:+.3f} (t {b_last / se_last:+.2f}); earlier windows' 5–95% range {lo5:+.3f} to {hi95:+.3f} → " + ("**recent is different** (outside the range)" if recent_diff else "inside the range — nothing new"), ""]
    if cond and "beta_stress" in cond: L += [f"**T-L4 conditional (P1 state '{cond['col']}'):** stress weeks β = {cond['beta_stress']:+.3f} (t {cond['t_stress']:+.2f}, n {cond['n_stress']}); abundant weeks β = {cond['beta_abundant']:+.3f} (t {cond['t_abundant']:+.2f}, n {cond['n_abundant']}).", ""]
    elif cond: L += [f"T-L4: {cond['note']}", ""]
    if after and "beta_after" in after:
        L += [f"**T-L5a after an equity sell-off (SPY's trailing 20 sessions ≤ {SELL_REG} at the week's start):** β = {after['beta_after']:+.3f} (t {after['t_after']:+.2f}, n {after['n_after']} weeks) vs other weeks {after['beta_other']:+.3f} (t {after['t_other']:+.2f}, n {after['n_other']}); difference t = {after['diff_t']:+.2f}.", ""]
    elif after: L += [f"T-L5a: {after['note']} (n {after['n_after']})", ""]
    if events:
        L += [f"**T-L5b gold after SPY's 20-session drawdown first crosses the threshold (events and the random-date null within GLD's history {gstart} → {gend}; one event per {COOL} sessions; share of forward returns negative vs the base rate; {NNULL:,} null draws). Registered cell: {SELL_REG}, 20 sessions → {v5}.**", "",
              "| threshold | events | horizon | share negative | base rate | gap (pts) | median | p (share negative ≥ observed) | verdict |", "|---|---|---|---|---|---|---|---|---|"]
        for lab, ev in events.items():
            for h, v in ev["by_h"].items(): L.append(f"| {lab} | {ev['n_events']} | {h} | {v['share_neg']:.0%} | {v['base_neg']:.0%} | {v['gap_pts']:+.0f} | {v['median']:+.2%} | {v['p']:.3f} | {v['verdict']} |" if v["n"] else f"| {lab} | 0 | {h} | — | — | — | — | — | no events |")
        L.append("")
    k = len(L); L += ["| period | n weeks | β | t |", "|---|---|---|---|"] + [f"| {q['period']} | {q['n']} | {q['beta']:+.3f} | {q['t']:+.2f} |" for q in per]
    L += ["", "| window start | end | β | t |", "|---|---|---|---|"] + [f"| {q.start.date()} | {q.end.date()} | {q.beta:+.3f} | {q.t:+.2f} |" for q in W.itertuples()]
    out = DOCS / f"liquidity_link_{asset}.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L[:k])); print(f"-> {out}")
    J = json.loads((PROC / "liquidity_link.json").read_text()) if (PROC / "liquidity_link.json").exists() else {}
    J[asset] = dict(run=datetime.now().strftime("%Y-%m-%d %H:%M"), n=n, start=str(dates[0].date()), end=str(dates[-1].date()), beta=b, t=t_pool, TL1=dict(windows=len(W), share=share, majority=maj, verdict=v1),
                    TL2=dict(supF=F_obs, date=str(bdate.date()), p=p_break, beta_before=b1, beta_after=b2, sdx_before=sdx1, sdx_after=sdx2, verdict=v2), TL3=dict(beta_last=b_last, lo5=lo5, hi95=hi95, recent_is_different=recent_diff),
                    TL4=cond, TL5a=after, TL5b=events, TL5_verdict=v5, periods=per,
                    nl_latest=dict(date=str(nl.index[-1].date()), NL_bn=float(nl["NL"].iloc[-1]), walcl_bn=float(nl["walcl"].iloc[-1]), tga_bn=float(nl["tga"].iloc[-1]), rrp_bn=float(nl["rrp"].iloc[-1])))
    (PROC / "liquidity_link.json").write_text(json.dumps(J, indent=1, default=float))


def _bump_tally(text: str, note: str) -> str:
    """Advance the wrong-prior tally once for `note` (idempotent: no second bump if the note is already on the line)."""
    if note in text: return text
    m = re.search(r"tally (\d+) \(#40–#43 lever priors", text)
    if not m: return text
    k = int(m.group(1)) + 1; text = text.replace(m.group(0), f"tally {k} (#40–#43 lever priors", 1)
    anchor = "#78 chairs differ (p 0.016)"; return text.replace(anchor, anchor + ", " + note, 1) if anchor in text else text


def _replace_line(text: str, pattern: str, new: str) -> tuple[str, bool]:
    m = re.search(pattern, text, flags=re.M); return (text[:m.start()] + new + text[m.end():], True) if m else (text, False)


def record(asset: str = "GLD"):
    """Write T-L's verdicts against priors #76 and #80 into the register, the pre-registration and the state record; replaces rows written earlier."""
    J = json.loads((PROC / "liquidity_link.json").read_text())[asset]; t1, t2, t3 = J["TL1"], J["TL2"], J["TL3"]; b5 = J.get("TL5b", {}); a5 = J.get("TL5a") or {}
    c8 = b5.get("-8%", {}).get("by_h", {}).get("20"); c5 = b5.get("-5%", {}).get("by_h", {}).get("20")
    clauses76 = dict(pooled_small_positive=(J["beta"] > 0 and abs(J["t"]) < 3), unstable=(t1["verdict"] == "UNSTABLE"), no_break=(t2["verdict"] == "no break"), nothing_new=(not t3["recent_is_different"]))
    clauses80 = {"-8% inconclusive (n < 30)": bool(c8 and c8["n"] < 30), "-5% within 10 points of base": bool(c5 and abs(c5["gap_pts"]) < 10), "T-L5a |t| < 2": bool("diff_t" in a5 and abs(a5["diff_t"]) < 2)}
    right76, right80 = all(clauses76.values()), all(clauses80.values()); miss76 = [k for k, v in clauses76.items() if not v]; miss80 = [k for k, v in clauses80.items() if not v]
    pri = ("**#76 right**" if right76 else f"**#76 wrong** ({', '.join(miss76)} did not hold)") + "; " + ("**#80 right**" if right80 else f"**#80 wrong** ({', '.join(miss80)} did not hold)")
    brk = (f"T-L2 sup-F {t2['supF']:.2f} at {t2['date']}, p {t2['p']:.3f} → {t2['verdict']} (β {t2['beta_before']:+.3f} → {t2['beta_after']:+.3f}"
           + (f"; the link was stronger before the break, when net liquidity barely moved week to week — sd {t2.get('sdx_before', float('nan')):.2%} → {t2.get('sdx_after', float('nan')):.2%} after — the opposite of 'absent before, present now'" if (t2["verdict"] == "BREAK" and abs(t2["beta_before"]) > abs(t2["beta_after"])) else "") + ")")
    res = (f"{J['n']} weeks {J['start']} → {J['end']}: pooled β {J['beta']:+.3f} (t {J['t']:+.2f}); T-L1 {t1['share']:.0%} of windows share the majority sign ({t1['majority']}) → {t1['verdict']}; {brk}; "
           f"T-L3 last two years β {t3['beta_last']:+.3f} vs the earlier range {t3['lo5']:+.3f}..{t3['hi95']:+.3f} → " + ("recent is different" if t3["recent_is_different"] else "nothing new"))
    c4 = J.get("TL4") or {}
    if "beta_stress" in c4: res += f"; T-L4 stress weeks β {c4['beta_stress']:+.3f} (t {c4['t_stress']:+.2f}, n {c4['n_stress']}) vs abundant {c4['beta_abundant']:+.3f} (t {c4['t_abundant']:+.2f}, n {c4['n_abundant']})"
    if "beta_after" in a5: res += f"; T-L5a β after a sell-off {a5['beta_after']:+.3f} (n {a5['n_after']} weeks) vs other weeks {a5['beta_other']:+.3f}, difference t {a5['diff_t']:+.2f}"
    if c8: res += f"; T-L5b (−8%, 20 sessions, events within GLD's history): {c8['n']} events, {c8['share_neg']:.0%} negative vs base {c8['base_neg']:.0%} (gap {c8['gap_pts']:+.0f} pts, p {c8['p']:.3f}) → {c8['verdict']}"
    if c5: res += f"; at −5%: {c5['n']} events, {c5['share_neg']:.0%} vs {c5['base_neg']:.0%} (gap {c5['gap_pts']:+.0f}, p {c5['p']:.3f}) → {c5['verdict']}"
    short = f"**T-L1 {t1['verdict']} ({t1['share']:.0%}), T-L2 {t2['verdict']} (p {t2['p']:.3f}, {t2['date']}), T-L3 " + ("recent differs" if t3["recent_is_different"] else "nothing new") + (f", T-L5b {c8['verdict']}" if c8 else "") + "**"
    stamp = datetime.now().strftime("%Y-%m-%d")
    p = DOCS / "prereg_liquidity_and_chair.md"; s = p.read_text(); row = f"| {stamp} | T-L ({asset}) | {res}. docs/liquidity_link_{asset}.md | {pri} |"
    s, done = _replace_line(s, r"^\| \d{4}-\d{2}-\d{2} \| T-L \(" + re.escape(asset) + r"\) \|.*$", row)
    if not done: s = s.rstrip("\n") + "\n" + row + "\n"
    p.write_text(s); print("  prereg: T-L result row " + ("replaced" if done else "added"))
    m = DOCS / "PROJECT_MASTER.md"; s = m.read_text(); lines = s.split("\n"); hit = False
    for i, ln in enumerate(lines):
        if ln.startswith("| 51 |"):
            cells = ln.strip().strip("|").split(" | ")
            if len(cells) >= 4: lines[i] = f"| 51 | {cells[1].strip()} | 27 Oct, {J['n']} weeks (T-L5b events within GLD's history) | {short} — {pri} |"; hit = True
    s = "\n".join(lines)
    s = re.sub(r"Liquidity: T-L: .*?(?=\n\n)", lambda _: f"Liquidity: T-L: {res} ({pri.replace('**', '')}).", s, count=1, flags=re.S)
    s = s.replace("[T-L: registered, result to be written by `liquidity_link record`.]", f"T-L: {res} ({pri.replace('**', '')}).", 1)
    if not right76: s = _bump_tally(s, "#76 liquidity link")
    if not right80: s = _bump_tally(s, "#80 gold after equity sell-offs")
    m.write_text(s); print("  MASTER: row 51 " + ("rewritten" if hit else "not found") + ", Block 9 updated")
    cs = DOCS / "CURRENT_STATE_2026-08-23.md"; s = cs.read_text(); line = f"T-L result ({datetime.now():%d %b}): {res}. {pri.replace('**', '')}."
    s, done = _replace_line(s, r"^T-L result \(.*$", line)
    if not done: s = s.rstrip("\n") + "\n\n" + line + "\n"
    cs.write_text(s); print("  CURRENT_STATE: T-L line " + ("replaced" if done else "added"))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run": run(sys.argv[2] if len(sys.argv) > 2 else "GLD")
    elif cmd == "record": record(sys.argv[2] if len(sys.argv) > 2 else "GLD")
    elif cmd == "levels":
        nl = net_liquidity(); print(nl.tail(8).round(0)) if nl is not None else print("  none")
'''); ast.parse(Path("src/liquidity_link.py").read_text()); print("  src/liquidity_link.py v3: events and null within GLD's history; record() replaces rows; #80 by clause")

# ---------------------------------------------------------------- 2. src/chair_power.py v3
Path("src/chair_power.py").write_text(r'''"""T-K0/T-K1/T-K1'/T-K2: the few-shot chair problem. Statement-day reaction of GLD (and TLT) to the 2-yr-yield surprise by chair; power of a per-chair
coefficient; chair x surprise interaction with a permutation null, in basis points (T-K1) and in units of the yield's own trailing volatility (T-K1');
empirical-Bayes posterior for the current chair, per bp and (v3) in volatility units -- the scale on which chairs are exchangeable.
docs/prereg_liquidity_and_chair.md section 3.    python -m src.chair_power run ; python -m src.chair_power record"""
from __future__ import annotations
import json, re, sys
from datetime import datetime
from math import comb
from pathlib import Path
import numpy as np, pandas as pd

PROC, DOCS = Path("processed"), Path("docs")
CHAIRS = [("Bernanke", "2006-02-01", "2014-01-31"), ("Yellen", "2014-02-03", "2018-02-03"), ("Powell", "2018-02-05", "2026-05-15"), ("Warsh", "2026-05-22", "2099-12-31")]
MIN_N, NPERM, SEED, Z, VOLWIN = 20, 2000, 0, 1.96 + 0.84, 504


def chair_of(d: pd.Timestamp) -> str:
    for name, a, b in CHAIRS:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b): return name
    return "other"


def table() -> pd.DataFrame:
    dates = pd.to_datetime(pd.read_csv(PROC / "fomc_decisions.csv")["date"]); dates = dates[dates <= pd.Timestamp.today().normalize()]
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    m = pd.read_parquet(PROC / "macro_panel.parquet"); m.index = pd.to_datetime(m.index); ds = m["DGS2"].dropna().diff() * 100
    vol = ds.rolling(VOLWIN, min_periods=250).std().shift(1); s = ds.reindex(r.index); v = vol.reindex(r.index).ffill()
    rows = [dict(date=d, chair=chair_of(d), s=s.get(d, np.nan), vol=v.get(d, np.nan), gld=r["GLD"].get(d, np.nan), tlt=(r["TLT"].get(d, np.nan) if "TLT" in r.columns else np.nan)) for d in dates]
    df = pd.DataFrame(rows).dropna(subset=["s", "gld"]); df["s_norm"] = df["s"] / df["vol"]; return df


def ols(x, y):
    n = len(x); xm, ym = x.mean(), y.mean(); sxx = ((x - xm) ** 2).sum(); b = ((x - xm) * (y - ym)).sum() / sxx if sxx > 0 else np.nan; a = ym - b * xm
    e = y - a - b * x; s2 = (e @ e) / max(n - 2, 1); return float(a), float(b), float(np.sqrt(s2 / sxx)) if sxx > 0 else np.nan, e, float(sxx)


def interaction_F(df: pd.DataFrame, col: str, labels: np.ndarray, xcol: str = "s") -> float:
    y = df[col].to_numpy(); s = df[xcol].to_numpy(); groups = sorted(set(labels)); n = len(y)
    D = np.column_stack([(labels == g).astype(float) for g in groups]); Xr = np.column_stack([D, s]); Xf = np.column_stack([D, D * s[:, None]])
    def rss(X): c, *_ = np.linalg.lstsq(X, y, rcond=None); e = y - X @ c; return float(e @ e)
    rf, rr = rss(Xf), rss(Xr); kf, kr = Xf.shape[1], Xr.shape[1]; return ((rr - rf) / (kf - kr)) / (rf / max(n - kf, 1))


def perm_p(sub, col, lab, xcol, rng):
    F = interaction_F(sub, col, lab, xcol); null = np.array([interaction_F(sub, col, rng.permutation(lab), xcol) for _ in range(NPERM)]); return F, float((null >= F).mean())


def posterior(b_pool: float, b_own: float, se_pooled: float, tau2: float) -> tuple[float, float, float]:
    w = tau2 / (tau2 + se_pooled ** 2) if tau2 > 0 else 0.0; mean = b_pool + w * (b_own - b_pool); sd = (1 / tau2 + 1 / se_pooled ** 2) ** -0.5 if tau2 > 0 else 0.0; return float(w), float(mean), float(sd)


def run():
    df = table(); n = len(df); a, b, se, e, _ = ols(df.s.to_numpy(), df.gld.to_numpy()); sigma = float(e.std(ddof=2)); var_s = float(df.s.var())
    dn = df.dropna(subset=["s_norm"]); _, bn, sen, en, _ = ols(dn.s_norm.to_numpy(), dn.gld.to_numpy()); sigma_n = float(en.std(ddof=2))
    per = []
    for name, _, _ in CHAIRS:
        g = df[df.chair == name]; gn = g.dropna(subset=["s_norm"])
        row = dict(chair=name, n=int(len(g)), mean_s=float(g.s.mean()) if len(g) else np.nan, sd_s=float(g.s.std()) if len(g) > 1 else np.nan, mean_gld=float(g.gld.mean()) if len(g) else np.nan,
                   beta=np.nan, se=np.nan, sxx=np.nan, se_pooled=np.nan, beta_norm=np.nan, se_norm=np.nan, sxx_norm=np.nan, se_norm_pooled=np.nan, mean_vol=float(g.vol.mean()) if len(g) else np.nan)
        if len(g) >= 3:
            _, bc, sec, _, sxx = ols(g.s.to_numpy(), g.gld.to_numpy()); row.update(beta=bc, se=sec, sxx=sxx, se_pooled=float(sigma / np.sqrt(sxx)) if sxx > 0 else np.nan)
        if len(gn) >= 3:
            _, bcn, secn, _, sxxn = ols(gn.s_norm.to_numpy(), gn.gld.to_numpy()); row.update(beta_norm=bcn, se_norm=secn, sxx_norm=sxxn, se_norm_pooled=float(sigma_n / np.sqrt(sxxn)) if sxxn > 0 else np.nan)
        per.append(row)
    P = pd.DataFrame(per); big = P[P.n >= MIN_N]
    tau2 = float(max(0.0, big.beta.var(ddof=1) - (big.se ** 2).mean())) if len(big) >= 2 else 0.0
    bigN = big[big.beta_norm.notna()]; tau2n = float(max(0.0, bigN.beta_norm.var(ddof=1) - (bigN.se_norm ** 2).mean())) if len(bigN) >= 2 else 0.0
    need = {f"delta = beta/{k}": (Z ** 2) * sigma ** 2 / ((abs(b) / k) ** 2 * var_s) if b != 0 else np.nan for k in (2, 1)}
    sub = df[df.chair.isin(big.chair)].dropna(subset=["s_norm"]).reset_index(drop=True); lab = sub.chair.to_numpy(); rng = np.random.default_rng(SEED)
    F_obs, p_gld = perm_p(sub, "gld", lab, "s", rng); F_norm, p_norm = perm_p(sub, "gld", lab, "s_norm", rng)
    F_tlt, p_tlt = (perm_p(sub, "tlt", lab, "s", rng) if sub.tlt.notna().all() else (np.nan, np.nan))
    cur = P.iloc[-1]; post = None
    if np.isfinite(cur.se_pooled):
        w, mean, sd = posterior(b, cur.beta, cur.se_pooled, tau2); w_own = tau2 / (tau2 + cur.se ** 2) if (tau2 > 0 and np.isfinite(cur.se)) else 0.0
        post = dict(chair=cur.chair, n=int(cur.n), beta_hat=float(cur.beta), se_own=float(cur.se), se_pooled=float(cur.se_pooled), weight_on_own=w, weight_if_own_se=float(w_own), posterior_mean=mean, posterior_sd=sd,
                    explained_by_pooled_slope=float(b * cur.mean_s), mean_gld=float(cur.mean_gld))
        if np.isfinite(cur.se_norm_pooled):
            wn, mn, sdn = posterior(bn, cur.beta_norm, cur.se_norm_pooled, tau2n); vol_now = float(cur.mean_vol)
            post.update(sigma_units=dict(beta_hat=float(cur.beta_norm), se_pooled=float(cur.se_norm_pooled), tau=float(np.sqrt(tau2n)), weight_on_own=wn, posterior_mean=mn, posterior_sd=sdn, vol_now_bp=vol_now,
                                         posterior_per_bp=(mn / vol_now if vol_now > 0 else np.nan), posterior_sd_per_bp=(sdn / vol_now if vol_now > 0 else np.nan)))
    min_p = {k: 1 / comb(k + 8, k) for k in (3, 4, 5, 6, 8)}
    v1 = "PASS — chairs differ per bp" if p_gld < 0.05 else "FAIL — no detectable chair difference"; v1n = "PASS — chairs still differ in volatility units" if p_norm < 0.05 else "FAIL — no chair difference once the surprise is in volatility units"
    L = [f"# T-K — the few-shot chair problem (GLD on the 2-yr surprise, statement days)", "",
         f"*{datetime.now():%Y-%m-%d %H:%M}. {n} statement days {df.date.min().date()} → {df.date.max().date()}; s = ΔDGS2 bp on the day, s/σ = the same in units of the yield's trailing two-year daily volatility; y = GLD log return on the day (%). prereg_liquidity_and_chair §3.*", "",
         f"**Pooled:** β = {b * 100:+.4f}% per bp (se {se * 100:.4f}); in volatility units β = {bn * 100:+.3f}% per σ (se {sen * 100:.3f}); residual σ = {sigma * 100:.2f}% a day; sd of the surprise {np.sqrt(var_s):.1f} bp.", "",
         "| chair | statements | mean surprise (bp) | sd (bp) | yield vol (bp/day) | mean GLD day (%) | β (% per bp) | se (own) | β (% per σ) | se |", "|---|---|---|---|---|---|---|---|---|---|"]
    for q in P.itertuples():
        f = lambda v, fmt: (fmt % v) if np.isfinite(v) else "—"
        L.append(f"| {q.chair} | {q.n} | {f(q.mean_s, '%+.1f')} | {f(q.sd_s, '%.1f')} | {f(q.mean_vol, '%.1f')} | {f(q.mean_gld * 100, '%+.2f')} | {f(q.beta * 100, '%+.4f')} | {f(q.se * 100, '%.4f')} | {f(q.beta_norm * 100, '%+.3f')} | {f(q.se_norm * 100, '%.3f')} |")
    L += ["", "**T-K0 power:** meetings needed to detect a chair-specific difference at α 5%, power 80% — " + "; ".join(f"{k}: **{v:,.0f}**" for k, v in need.items()) + ". A tenure is 8 meetings a year; a four-year term 32.", "",
          f"**T-K1 chairs differ (per bp)?** F = {F_obs:.2f} among {', '.join(big.chair)}; permutation p = **{p_gld:.3f}** → **{v1}**; between-chair τ = {np.sqrt(tau2) * 100:.4f}% per bp" + (f"; TLT cross-check F = {F_tlt:.2f}, p = {p_tlt:.3f}" if np.isfinite(p_tlt) else "") + ".", "",
          f"**T-K1′ chairs differ (per σ of the yield)?** F = {F_norm:.2f}; permutation p = **{p_norm:.3f}** → **{v1n}**; between-chair τ in these units {np.sqrt(tau2n) * 100:.3f}% per σ.", ""]
    if post:
        L += [f"**T-K2 {post['chair']} so far ({post['n']} statements), per bp:** own slope {post['beta_hat'] * 100:+.4f}% per bp; standard error from the pooled residual σ {post['se_pooled'] * 100:.4f} (the own 1-dof se was {post['se_own'] * 100:.4f}); weight on own data **{post['weight_on_own']:.0%}** (would be {post['weight_if_own_se']:.0%} on the own se); posterior {post['posterior_mean'] * 100:+.4f}% ± {post['posterior_sd'] * 100:.4f} per bp. "
              f"His statement days averaged {post['mean_gld'] * 100:+.2f}% on gold; the pooled slope times his average surprise gives {post['explained_by_pooled_slope'] * 100:+.2f}% — " + ("most of it: gold fell on his days because the statements surprised hawkish, not because gold reacts to him differently." if abs(post['explained_by_pooled_slope']) > 0.5 * abs(post['mean_gld']) else "less than half of it."), ""]
        su = post.get("sigma_units")
        if su: L += [f"**T-K2σ in volatility units (the scale on which chairs are exchangeable, T-K1′):** own {su['beta_hat'] * 100:+.3f}% per σ, pooled-σ se {su['se_pooled'] * 100:.3f}, between-chair τ {su['tau'] * 100:.3f}; weight on own data **{su['weight_on_own']:.0%}**; posterior **{su['posterior_mean'] * 100:+.3f}% ± {su['posterior_sd'] * 100:.3f} per σ**, i.e. about {su['posterior_per_bp'] * 100:+.4f}% ± {su['posterior_sd_per_bp'] * 100:.4f} per bp at today's yield volatility ({su['vol_now_bp']:.1f} bp a day). **The page quotes this one.**", ""]
    L += ["**T-K3 (not run):** smallest attainable exact-permutation p for n statements against the previous chair's last 8 — " + ", ".join(f"n = {k}: {v:.4f}" for k, v in min_p.items()) + "."]
    out = DOCS / "chair_power.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")
    J = dict(run=datetime.now().strftime("%Y-%m-%d %H:%M"), n=n, beta=b, se=se, beta_norm=bn, se_norm=sen, sigma=sigma, sigma_norm=sigma_n, var_s=var_s, chairs=per, tau2=tau2, tau2_norm=tau2n, need=need,
             TK1=dict(F=F_obs, p=p_gld, F_tlt=F_tlt, p_tlt=p_tlt, verdict=v1), TK1n=dict(F=F_norm, p=p_norm, verdict=v1n), TK2=post, min_p=min_p)
    (PROC / "chair_power.json").write_text(json.dumps(J, indent=1, default=float))


def _bump_tally(text: str, note: str) -> str:
    if note in text: return text
    m = re.search(r"tally (\d+) \(#40–#43 lever priors", text)
    if not m: return text
    k = int(m.group(1)) + 1; text = text.replace(m.group(0), f"tally {k} (#40–#43 lever priors", 1)
    anchor = "#78 chairs differ (p 0.016)"; return text.replace(anchor, anchor + ", " + note, 1) if anchor in text else text


def _replace_line(text: str, pattern: str, new: str) -> tuple[str, bool]:
    m = re.search(pattern, text, flags=re.M); return (text[:m.start()] + new + text[m.end():], True) if m else (text, False)


def record():
    """Write T-K1' against prior #81 and the posteriors into the register, the pre-registration and the state record; replaces rows written earlier."""
    J = json.loads((PROC / "chair_power.json").read_text()); k1n, post = J["TK1n"], J["TK2"]
    right81 = k1n["p"] > 0.05; pri = "**#81 right**" if right81 else "**#81 wrong** (chairs still differ in volatility units)"
    rows = {c["chair"]: c for c in J["chairs"]}; per_sigma = ", ".join(f"{c} {rows[c]['beta_norm'] * 100:+.2f}" for c in ("Bernanke", "Yellen", "Powell") if c in rows and np.isfinite(rows[c].get("beta_norm", np.nan)))
    res = (f"T-K1′: interaction F {k1n['F']:.2f}, permutation p {k1n['p']:.3f} → {k1n['verdict']}; β per σ of the yield — {per_sigma}% (per bp they were {rows['Bernanke']['beta'] * 100:+.3f}, {rows['Yellen']['beta'] * 100:+.3f}, {rows['Powell']['beta'] * 100:+.3f})")
    if post:
        res += f". T-K2 per bp with the pooled-σ se: {post['chair']} weight on own data {post['weight_on_own']:.0%} (was {post['weight_if_own_se']:.0%}), posterior {post['posterior_mean'] * 100:+.4f}% ± {post['posterior_sd'] * 100:.4f} per bp"
        su = post.get("sigma_units")
        if su: res += (f". T-K2σ in volatility units, the scale on which chairs are exchangeable: weight on own data {su['weight_on_own']:.0%}, posterior {su['posterior_mean'] * 100:+.3f}% ± {su['posterior_sd'] * 100:.3f} per σ "
                       f"(≈ {su['posterior_per_bp'] * 100:+.4f}% per bp at today's {su['vol_now_bp']:.1f} bp/day) — the page quotes this one")
    stamp = datetime.now().strftime("%Y-%m-%d")
    p = DOCS / "prereg_liquidity_and_chair.md"; s = p.read_text(); row = f"| {stamp} | T-K1′ and T-K2 (pooled σ, volatility units) | {res}. docs/chair_power.md | {pri} |"
    s, done = _replace_line(s, r"^\| \d{4}-\d{2}-\d{2} \| T-K1′ and T-K2 \(pooled σ.*$", row)
    if not done: s = s.rstrip("\n") + "\n" + row + "\n"
    p.write_text(s); print("  prereg: T-K1′ row " + ("replaced" if done else "added"))
    m = DOCS / "PROJECT_MASTER.md"; s = m.read_text(); txt = f"{res} ({pri.replace('**', '')})."
    lines = s.split("\n")
    for i, ln in enumerate(lines):      # row 52: line-wise, so the replacement can never run across other rows or sections
        if ln.startswith("| 52 |"): lines[i] = re.sub(r"T-K1′: interaction F .*? T-K3 next \|", lambda _: txt + " T-K3 next |", ln, count=1)
    s2 = "\n".join(lines).replace("[T-K1′: registered, result to be written by `chair_power record`.]", txt, 1)
    mb = re.search(r"re-asked in volatility units: (.*?) Warsh's three statement days", s2, flags=re.S)   # Block 9: one paragraph; refuse a match that crosses a blank line
    if mb and "\n\n" not in mb.group(1): s2 = s2[:mb.start()] + "re-asked in volatility units: " + txt + " Warsh's three statement days" + s2[mb.end():]
    if not right81: s2 = _bump_tally(s2, "#81 chairs in volatility units")
    m.write_text(s2); print("  MASTER: row 52 and Block 9 " + ("updated" if s2 != s else "unchanged (anchors not found)"))
    cs = DOCS / "CURRENT_STATE_2026-08-23.md"; s = cs.read_text(); line = f"T-K1′ result ({datetime.now():%d %b}): {res}. {pri.replace('**', '')}."
    s, done = _replace_line(s, r"^T-K1′ result \(.*$", line)
    if not done: s = s.rstrip("\n") + "\n\n" + line + "\n"
    cs.write_text(s); print("  CURRENT_STATE: T-K1′ line " + ("replaced" if done else "added"))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run": run()
    elif cmd == "record": record()
    elif cmd == "table": print(table().tail(12))
'''); ast.parse(Path("src/chair_power.py").read_text()); print("  src/chair_power.py v3: T-K2 in volatility units; record() replaces rows")

# ---------------------------------------------------------------- 3. amendments
p = DOCS / "prereg_liquidity_and_chair.md"; s = p.read_text()
if "events before GLD existed" in s: print("  prereg amendments: already")
else:
    rows = (f"| {TODAY} (23:50) | **Data error in T-L5b, after the first valid run:** the price panel starts in 1995 and GLD in Nov 2004; equity sell-offs before GLD existed (21 of 64 at −5%, 10 of 30 at −8%, 7 of 23 at −10%) were counted as zero gold returns, and the random-date null drew from the same dates. The medians printing as exactly 0.00% exposed it. Events and the null's date pool are restricted to GLD's history; the rows written to the register are replaced by the re-run; **#80 re-judged clause by clause** (−8% INCONCLUSIVE with n < 30; −5% within 10 points; T-L5a |t| < 2). The first T-L5b numbers are void and not quoted. | a data error, not a prior; counted in the text |\n"
            f"| {TODAY} (23:50) | **T-K2 in volatility units (T-K2σ).** T-K1′ found no chair difference once the surprise is in units of the yield's own volatility, so that is the scale on which chairs are exchangeable; the between-chair variance per bp (τ 0.109% per bp) was the yield era's scale and must not lend a few-statement chair a 65% weight. The page's chair posterior is computed per σ (τ_σ from Bernanke/Yellen/Powell, the chair's se from the pooled residual σ) and translated to per bp at today's yield volatility. Expectation, not a prior: the weight on Warsh's own three statements falls well below the 65% found per bp. | consistency between T-K1′ and the quantity shown |\n")
    rows += (f"| {TODAY} (23:57) | **Record note.** Commit 6b1e44a carries the message of this fix, but the fix had not run: the script was not yet on disk, so the v2 modules re-ran unchanged, the contaminated T-L5b rows stayed, and two result lines were duplicated in CURRENT_STATE (removed here as exact repeats). History is not rewritten; the next commit applies the fix and says so. | an honest ledger |\n")
    s = s.replace("\n## 5. Results\n", "\n" + rows + "\n## 5. Results\n", 1); p.write_text(s); print("  prereg: three amendments (data error; T-K2σ; record note on 6b1e44a)")
tr = DOCS / "TRACK.md"; s = tr.read_text()
if "T-L5b events before GLD" in s: print("  TRACK: already")
else: tr.write_text(s.rstrip("\n") + "\n\n27 Oct 23:50: T-L5b events before GLD existed (1995–2004) had been counted as zero gold returns — fixed, re-run, records replaced, #80 re-judged; T-K2σ (chair posterior in volatility units) added. Commit after the re-run closes the night.\n"); print("  TRACK: status line")
for f in ("src/liquidity_link.py", "src/chair_power.py", "src/flows.py", "src/factor_attribution.py", "src/why_moved.py", "src/context.py", "app.py"):
    ast.parse(Path(f).read_text())
print("  all modules parse")
print("done -- python -m src.liquidity_link run ; python -m src.liquidity_link record ; python -m src.chair_power run ; python -m src.chair_power record")
