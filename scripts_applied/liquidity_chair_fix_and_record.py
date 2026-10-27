"""27 Oct, later. (1) T-L first run failed on units: FRED's WTREGEN (Treasury account) is in millions, WALCL in millions, RRP in billions — my code
took the account as billions, so net liquidity was negative everywhere and every week dropped. Fixed with a units guard; the first module versions are kept
in scripts_applied/superseded/. (2) T-L5 added before running — the founder's exact sentence: gold affected by a liquidity drain *after other asset classes
have had a huge sell-off*. (3) T-K0/T-K1/T-K2 results recorded (#77 wrong, #78 wrong, tally 64); T-K1' (surprise in volatility units) and the pooled-sigma
standard error for a few-statement chair registered before running. (4) MASTER Block 9, CURRENT_STATE 18.40, TRACK 3.35 status. (5) .gitignore for the
CFTC zips; the PDF the SPDR site served is renamed so it is not committed as a csv.
Run from the repo root:  python scripts_applied/liquidity_chair_fix_and_record.py
then:  python -m src.liquidity_link run ; python -m src.liquidity_link record ; python -m src.chair_power run ; python -m src.chair_power record"""
from pathlib import Path
import ast, shutil
from datetime import datetime

PROC, DOCS = Path("processed"), Path("docs")
TODAY = "2026-10-27"

# ---------------------------------------------------------------- 0. keep the first versions
sup = Path("scripts_applied/superseded"); sup.mkdir(parents=True, exist_ok=True)
for f, g in (("src/liquidity_link.py", "liquidity_link_v1_27oct_units_bug.py"), ("src/chair_power.py", "chair_power_v1_27oct.py")):
    if Path(f).exists() and not (sup / g).exists(): shutil.copy(f, sup / g); print(f"  kept {f} -> {sup / g}")

# ---------------------------------------------------------------- 1. src/liquidity_link.py v2
Path("src/liquidity_link.py").write_text(r'''"""T-L: is the liquidity-gold link constant through time? Weekly Fed net liquidity (WALCL - TGA - RRP, FRED) against GLD's weekly return.
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
'''); ast.parse(Path("src/liquidity_link.py").read_text()); print("  src/liquidity_link.py v2: units guard, T-L5, record")

# ---------------------------------------------------------------- 2. src/chair_power.py v2
Path("src/chair_power.py").write_text(r'''"""T-K0/T-K1/T-K1'/T-K2: the few-shot chair problem. Statement-day reaction of GLD (and TLT) to the 2-yr-yield surprise by chair; power of a per-chair
coefficient; chair x surprise interaction with a permutation null, in basis points (T-K1) and in units of the yield's own trailing volatility (T-K1');
empirical-Bayes posterior for the current chair with the pooled residual sigma for a few-statement chair.  docs/prereg_liquidity_and_chair.md section 3.
    python -m src.chair_power run ; python -m src.chair_power record"""
from __future__ import annotations
import json, re, sys
from datetime import datetime
from math import comb
from pathlib import Path
import numpy as np, pandas as pd

PROC, DOCS = Path("processed"), Path("docs")
CHAIRS = [("Bernanke", "2006-02-01", "2014-01-31"), ("Yellen", "2014-02-03", "2018-02-03"), ("Powell", "2018-02-05", "2026-05-15"), ("Warsh", "2026-05-22", "2099-12-31")]
MIN_N, NPERM, SEED, Z, VOLWIN = 20, 2000, 0, 1.96 + 0.84, 504   # alpha 5% two-sided, power 80%; trailing two years for the yield's volatility


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


def run():
    df = table(); n = len(df); a, b, se, e, _ = ols(df.s.to_numpy(), df.gld.to_numpy()); sigma = float(e.std(ddof=2)); var_s = float(df.s.var())
    dn = df.dropna(subset=["s_norm"]); _, bn, sen, en, _ = ols(dn.s_norm.to_numpy(), dn.gld.to_numpy())
    per = []
    for name, _, _ in CHAIRS:
        g = df[df.chair == name]; gn = g.dropna(subset=["s_norm"]); row = dict(chair=name, n=int(len(g)), mean_s=float(g.s.mean()) if len(g) else np.nan, sd_s=float(g.s.std()) if len(g) > 1 else np.nan, mean_gld=float(g.gld.mean()) if len(g) else np.nan,
                                                                             beta=np.nan, se=np.nan, sxx=np.nan, beta_norm=np.nan, se_norm=np.nan, mean_vol=float(g.vol.mean()) if len(g) else np.nan)
        if len(g) >= 3:
            _, bc, sec, _, sxx = ols(g.s.to_numpy(), g.gld.to_numpy()); row.update(beta=bc, se=sec, sxx=sxx, se_pooled=float(sigma / np.sqrt(sxx)) if sxx > 0 else np.nan)
        if len(gn) >= 3: _, bcn, secn, _, _ = ols(gn.s_norm.to_numpy(), gn.gld.to_numpy()); row.update(beta_norm=bcn, se_norm=secn)
        per.append(row)
    P = pd.DataFrame(per); big = P[P.n >= MIN_N]
    tau2 = float(max(0.0, big.beta.var(ddof=1) - (big.se ** 2).mean())) if len(big) >= 2 else 0.0
    need = {f"delta = beta/{k}": (Z ** 2) * sigma ** 2 / ((abs(b) / k) ** 2 * var_s) if b != 0 else np.nan for k in (2, 1)}
    sub = df[df.chair.isin(big.chair)].dropna(subset=["s_norm"]).reset_index(drop=True); lab = sub.chair.to_numpy(); rng = np.random.default_rng(SEED)
    F_obs, p_gld = perm_p(sub, "gld", lab, "s", rng); F_norm, p_norm = perm_p(sub, "gld", lab, "s_norm", rng)
    F_tlt, p_tlt = (perm_p(sub, "tlt", lab, "s", rng) if sub.tlt.notna().all() else (np.nan, np.nan))
    cur = P.iloc[-1]; post = None
    if np.isfinite(cur.get("se_pooled", np.nan)):
        sp = float(cur.se_pooled); w = tau2 / (tau2 + sp ** 2) if tau2 > 0 else 0.0; mean = b + w * (cur.beta - b); sd = (1 / tau2 + 1 / sp ** 2) ** -0.5 if tau2 > 0 else 0.0
        w_own = tau2 / (tau2 + cur.se ** 2) if (tau2 > 0 and np.isfinite(cur.se)) else 0.0
        post = dict(chair=cur.chair, n=int(cur.n), beta_hat=float(cur.beta), se_own=float(cur.se), se_pooled=sp, weight_on_own=float(w), weight_if_own_se=float(w_own), posterior_mean=float(mean), posterior_sd=float(sd),
                    explained_by_pooled_slope=float(b * cur.mean_s), mean_gld=float(cur.mean_gld))
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
          f"**T-K1′ chairs differ (per σ of the yield)?** F = {F_norm:.2f}; permutation p = **{p_norm:.3f}** → **{v1n}**.", ""]
    if post:
        L += [f"**T-K2 {post['chair']} so far ({post['n']} statements):** own slope {post['beta_hat'] * 100:+.4f}% per bp; standard error from the pooled residual σ {post['se_pooled'] * 100:.4f} (the own 1-dof se was {post['se_own'] * 100:.4f}); weight the data earns against the pooled prior **{post['weight_on_own']:.0%}** (it would have been {post['weight_if_own_se']:.0%} on the own se); posterior **{post['posterior_mean'] * 100:+.4f}% ± {post['posterior_sd'] * 100:.4f}** per bp. "
              f"His statement days averaged {post['mean_gld'] * 100:+.2f}% on gold; the pooled slope times his average surprise gives {post['explained_by_pooled_slope'] * 100:+.2f}% — " + ("most of it: gold fell on his days because the statements surprised hawkish, not because gold reacts to him differently." if abs(post['explained_by_pooled_slope']) > 0.5 * abs(post['mean_gld']) else "less than half of it."), ""]
    L += ["**T-K3 (not run):** smallest attainable exact-permutation p for n statements against the previous chair's last 8 — " + ", ".join(f"n = {k}: {v:.4f}" for k, v in min_p.items()) + "."]
    out = DOCS / "chair_power.md"; out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"-> {out}")
    J = dict(run=datetime.now().strftime("%Y-%m-%d %H:%M"), n=n, beta=b, se=se, beta_norm=bn, se_norm=sen, sigma=sigma, var_s=var_s, chairs=per, tau2=tau2, need=need,
             TK1=dict(F=F_obs, p=p_gld, F_tlt=F_tlt, p_tlt=p_tlt, verdict=v1), TK1n=dict(F=F_norm, p=p_norm, verdict=v1n), TK2=post, min_p=min_p)
    (PROC / "chair_power.json").write_text(json.dumps(J, indent=1, default=float))


def _bump_tally(text: str, note: str) -> str:
    m = re.search(r"tally (\d+) \(#40–#43 lever priors", text)
    if not m: return text
    k = int(m.group(1)) + 1; text = text.replace(m.group(0), f"tally {k} (#40–#43 lever priors", 1)
    anchor = "#78 chairs differ (p 0.016)"; return text.replace(anchor, anchor + ", " + note, 1) if anchor in text else text


def record():
    """Write T-K1' against prior #81, and the pooled-sigma posterior, into the register, the pre-registration and the state record."""
    J = json.loads((PROC / "chair_power.json").read_text()); k1n, post = J["TK1n"], J["TK2"]
    right81 = k1n["p"] > 0.05; pri = "**#81 right**" if right81 else "**#81 wrong** (chairs still differ in volatility units)"
    rows = {c["chair"]: c for c in J["chairs"]}; per_sigma = ", ".join(f"{c} {rows[c]['beta_norm'] * 100:+.2f}" for c in ("Bernanke", "Yellen", "Powell") if c in rows and np.isfinite(rows[c].get("beta_norm", np.nan)))
    res = (f"T-K1′: interaction F {k1n['F']:.2f}, permutation p {k1n['p']:.3f} → {k1n['verdict']}; β per σ of the yield — {per_sigma}% (per bp they were {rows['Bernanke']['beta'] * 100:+.3f}, {rows['Yellen']['beta'] * 100:+.3f}, {rows['Powell']['beta'] * 100:+.3f})"
           + (f". T-K2 with the pooled-σ se: {post['chair']} weight on own data {post['weight_on_own']:.0%} (was {post['weight_if_own_se']:.0%}), posterior {post['posterior_mean'] * 100:+.4f}% ± {post['posterior_sd'] * 100:.4f} per bp" if post else ""))
    p = DOCS / "prereg_liquidity_and_chair.md"; s = p.read_text()
    if "| T-K1′ and T-K2 (pooled σ) |" not in s: s = s.rstrip("\n") + f"\n| {datetime.now():%Y-%m-%d} | T-K1′ and T-K2 (pooled σ) | {res}. docs/chair_power.md | {pri} |\n"; p.write_text(s); print("  prereg: T-K1′ result row")
    m = DOCS / "PROJECT_MASTER.md"; s = m.read_text(); ph = "[T-K1′: registered, result to be written by `chair_power record`.]"
    if ph in s:
        s = s.replace(ph, f"{res} ({pri.replace('**', '')}).", 1)
        if not right81: s = _bump_tally(s, "#81 chairs in volatility units")
        m.write_text(s); print("  MASTER: T-K1′ written into row 52 and Block 9" + ("" if right81 else ", tally advanced"))
    cs = DOCS / "CURRENT_STATE_2026-08-23.md"; s = cs.read_text()
    if "T-K1′ result:" not in s: cs.write_text(s.rstrip("\n") + f"\n\nT-K1′ result ({datetime.now():%d %b}): {res}. {pri.replace('**', '')}.\n"); print("  CURRENT_STATE: T-K1′ line")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run": run()
    elif cmd == "record": record()
    elif cmd == "table": print(table().tail(12))
'''); ast.parse(Path("src/chair_power.py").read_text()); print("  src/chair_power.py v2: volatility units (T-K1′), pooled-σ se (T-K2), record")

# ---------------------------------------------------------------- 3. .gitignore; the PDF the SPDR site served
gi = Path(".gitignore"); s = gi.read_text() if gi.exists() else ""
if "data_provenance/flows/*.zip" not in s: gi.write_text(s.rstrip("\n") + "\n# CFTC weekly archives (re-fetchable, ~45 MB)\ndata_provenance/flows/*.zip\n"); print("  .gitignore: CFTC zips")
pdf = Path("data_provenance/flows/GLD_US_archive_EN.csv")
if pdf.exists() and pdf.read_bytes()[:5] == b"%PDF-": pdf.rename(pdf.with_name("GLD_US_archive_EN.served_as_pdf_20261027")); print("  GLD archive: the served PDF renamed (kept)")

# ---------------------------------------------------------------- 4. registration additions and the T-K v1 record
p = DOCS / "prereg_liquidity_and_chair.md"; s = p.read_text()
if "T-L5" in s: print("  prereg T-L5 / T-K1′: already")
else:
    s = s.replace("| sub-periods | β, t and n for 2004–08, 2009–14, 2015–19, 2020–21, 2022–26 | reported |\n",
        "| sub-periods | β, t and n for 2004–08, 2009–14, 2015–19, 2020–21, 2022–26 | reported |\n"
        "| **T-L5a after an equity sell-off** (the founder's sentence, 27 Oct, added before the first valid run) | β in weeks where SPY's trailing 20-session return at the week's start is ≤ −8%, vs all other weeks; difference in units of its standard error | reported; the registered verdict sits in T-L5b |\n"
        "| **T-L5b gold after the sell-off** | events = the first session on which SPY's 20-session log return crosses below −8% (one event per 40 sessions); gold's forward 5-, 10-, 20-session return; share negative vs the base rate (all sessions); random-date null, 1,000 draws of as many random start dates. Thresholds −5% and −10% run beside as the sweep (standing rule, 23 Oct) | registered cell −8% / 20 sessions: PASS if n ≥ 30, gap ≥ 10 points and p < 0.05 (the H-table standard); INCONCLUSIVE if n < 30; else FAIL |\n", 1)
    s = s.replace("The founder's reading (a logic that was absent\nbefore and present now) is the alternative; T-L2 and T-L3 are the tests that would support it.",
        "The founder's reading (a logic that was absent\nbefore and present now) is the alternative; T-L2 and T-L3 are the tests that would support it.\n\n"
        "**Prior #80 (Claude, T-L5, before running).** At −8% there are fewer than 30 non-overlapping events since 2004 → INCONCLUSIVE; at −5% (n ≥ 30) the share of\n"
        "negative 20-session gold returns is within 10 points of the base rate → FAIL. 2008 and March 2020 are the two famous dash-for-cash cases; across all\n"
        "sell-offs gold's forward return after an equity drawdown is not distinguishable from any other time. T-L5a: β after a sell-off not distinguishable from β in other weeks (|t| < 2).", 1)
    s = s.replace("| **T-K2 the current chair's posterior** |",
        "| **T-K1′ chairs differ in volatility units?** (added 27 Oct after T-K1, before running) | the same interaction test with the surprise divided by the 2-yr yield's trailing two-year daily volatility (bp per day), so a 2 bp move at the zero bound and a 10 bp move in 2023 are compared on the same scale | PASS if p < 0.05 on GLD. **Prior #81: FAIL (p > 0.05)** — the per-bp difference found in T-K1 is the yield era's scale, not the chair: per bp Bernanke −0.33, Yellen −0.14, Powell −0.10, but times each era's surprise sd (2.6, 5.7, 7.8 bp) the three come to about −0.8% per sd |\n"
        "| **T-K2 the current chair's posterior** |", 1)
    s = s.replace("| reported with the shrinkage weight; refreshed after each statement. No criterion — it is what the page shows instead of a per-chair estimate |",
        "| reported with the shrinkage weight; refreshed after each statement. No criterion — it is what the page shows instead of a per-chair estimate. **Amendment 27 Oct (after seeing the v1 run, before the v2 run):** for a chair with few statements the own residual has 1 degree of freedom and is not an estimate (Warsh's 3 points gave se 0.03 and a 92% weight); the se used in the weight is the pooled residual σ divided by √Σ(s − s̄)² over his statements. Both weights are reported |", 1)
    s = s.rstrip("\n") + f"""
| {TODAY} | Units error in the first T-L run: WTREGEN is in millions on FRED (taken as billions), net liquidity negative, every week dropped; `to_bn` guard (median > 50,000 → millions). First module kept in scripts_applied/superseded/ | a data error, not a prior; counted in the text, not the tally |
| {TODAY} | T-L5a/b added; T-K1′ added; T-K2 se from the pooled σ (texts above) | the founder's exact sentence; the chair–era confound seen in T-K1; a 1-dof se is not an estimate |

## 5. Results

| date | test | result | prior |
|---|---|---|---|
| {TODAY} | T-K0 power | 131 statement days 2011-01-26 → 2026-09-16; pooled β −0.1138% per bp (se 0.0141), residual σ 1.07% a day, surprise sd 6.7 bp. Meetings needed at α 5%, power 80%: **62** for a chair whose reaction is half the pooled one, **16** for a reaction that has vanished. A four-year term is 32 meetings. docs/chair_power.md | **#77 wrong** (I said > 100; the same-day reaction is twice what I assumed and the noise smaller) — the conclusion survives in a weaker form: a halving is not detectable within one term |
| {TODAY} | T-K1 chairs differ (per bp) | Bernanke −0.332 (25), Yellen −0.144 (32), Powell −0.096 (71) % per bp; interaction F 4.43, permutation p **0.016 → PASS**; between-chair τ 0.109% per bp. TLT cross-check F 0.36, p 0.61 — the bond market's reaction does not differ by chair. **Caveat:** each chair sits in one yield era (Bernanke's surprises sd 2.6 bp at the zero bound), so chair and era are confounded → T-K1′ | **#78 wrong** (I said FAIL) |
| {TODAY} | T-K2 Warsh (3 statements, v1) | own slope −0.142% per bp; the own 1-dof se (0.03) gave a 92% weight — not an estimate (amendment above). His three statement days: mean surprise +6.0 bp (hawkish), mean GLD day −0.82%; the pooled slope times +6.0 bp is −0.68%, i.e. most of the fall is the hawkish surprise, not a different reaction to him | no prior; the page quotes the pooled-σ posterior from the v2 run |
"""; p.write_text(s); print("  prereg: T-L5, T-K1′, T-K2 amendment, T-K v1 results (#77, #78 wrong)")

# ---------------------------------------------------------------- 5. MASTER: row 52 result, tally 64, Block 9; CURRENT_STATE 18.40; TRACK status
m = DOCS / "PROJECT_MASTER.md"; s = m.read_text()
old52 = "| registered 27 Oct, not run; priors #77 n > 100, #78 FAIL, #79 n = 4 does not separate | — |"
if old52 in s:
    s = s.replace(old52, "| 27 Oct, 131 statement days 2011–2026 | **T-K0: 62 meetings to detect a half-size chair reaction, 16 a vanished one (#77 wrong); T-K1 PASS p 0.016 per bp (#78 wrong), TLT p 0.61, chair confounded with yield era; T-K2 Warsh's 3 days −0.82% ≈ pooled slope × his +6 bp hawkish surprises.** [T-K1′: registered, result to be written by `chair_power record`.] T-K3 next |", 1)
    s = s.replace("tally 62 (#40–#43 lever priors", "tally 64 (#40–#43 lever priors", 1)
    s = s.replace("#61 flows and positioning (T-A 0.177 → 0.160, COT sign shares 52–61%)", "#61 flows and positioning (T-A 0.177 → 0.160, COT sign shares 52–61%), #77 chair power (62 meetings, not > 100), #78 chairs differ (p 0.016)", 1)
    print("  MASTER: row 52 result, tally 64")
else: print("  MASTER row 52: anchor not found or already written")
if "**Block 9 —" in s: print("  MASTER Block 9: already")
else:
    block = """**Block 9 — "Was 'gold is sold when liquidity drains' ever tested through time — and can the machine learn a new Fed chair from a few announcements?"**
*Idea.* The founder suspected a logic that was absent before and present now: gold sold off when liquidity drains after other asset classes have had a huge
sell-off. He also asked how the engine could learn a new chair's pattern from the few announcements a chair makes in his life, instead of waiting for a large n.
*Then.* The record showed the liquidity question had been asked once (P1, 11 Aug), pooled over the whole span and as the opposite claim (gold decouples), with a
NULL whose "dash-for-cash" line was the sign of a gap not distinguishable from zero; no test had asked whether the relationship changed through time or after an
equity sell-off. For the chair the answer splits in two: what a chair does is measured without noise and can be learned from few; how the market reacts to him is
measured through 1% a day of noise and cannot — so the engine should carry the pooled reaction, shrunk toward the chair, and test his style on content.
*Terms.* Fed net liquidity (balance sheet − Treasury account − reverse repo); rolling-window sign share; Quandt–Andrews sup-F for a break at an unknown date with
a circular block-bootstrap null; conditional β after an equity drawdown; random-date null for forward shares. Statistical power (meetings needed at α 5%, power
80%); chair × surprise interaction with a permutation null; the chair–era confound and normalising by the yield's own volatility; empirical-Bayes shrinkage
(between-chair variance τ², the weight a chair's own data earns); exact permutation over all arrangements for a few-shot style test.
*Findings.* Chair: on 131 statement days 2011–2026 gold moves −0.11% per basis point of same-day 2-year-yield surprise; detecting a chair whose reaction is half
that needs 62 meetings (about eight years), a vanished reaction 16 (#77 wrong — I had said more than 100). Bernanke, Yellen and Powell differ per basis point
(p 0.016, #78 wrong) but not on bonds (p 0.61), and each sits in one yield era — Bernanke's at the zero bound with 2.6 bp surprises — so the difference was
re-asked in volatility units: [T-K1′: registered, result to be written by `chair_power record`.] Warsh's three statement days averaged a +6 bp hawkish surprise and
−0.82% on gold; the pooled slope times +6 bp is −0.68%: gold fell on his days because his statements surprised hawkish, not because gold reacts to him
differently. Liquidity: [T-L: registered, result to be written by `liquidity_link record`.]

"""
    s = s.replace("\n## 3. What the machine does today", "\n" + block + "## 3. What the machine does today", 1); print("  MASTER: Block 9")
m.write_text(s)
cs = DOCS / "CURRENT_STATE_2026-08-23.md"; s = cs.read_text()
if "### 18.40" in s: print("  CURRENT_STATE 18.40: already")
else:
    cs.write_text(s.rstrip("\n") + """

### 18.40 The chair's reaction and the liquidity link, first numbers (27 Oct, night)

T-K ran on 131 FOMC statement days (2011–2026). Gold moves −0.11% per basis point of same-day 2-year-yield surprise (residual 1.07% a day). To detect a chair
whose reaction is half the pooled one takes 62 meetings — about eight years, two terms — and a vanished reaction 16; prior #77 (more than 100) wrong, the
conclusion holding in a weaker form: not within one term. Bernanke, Yellen and Powell differ per basis point (permutation p 0.016; #78 wrong) but not on
bonds (p 0.61), and each chair sits in one yield era, so the per-bp difference is confounded with the era's yield scale; T-K1′ in volatility units registered
and run next. Warsh's three statement days averaged a +6 bp hawkish surprise and −0.82% on gold, of which the pooled slope explains −0.68%. The first T-L run
failed on a units error (the Treasury account is in millions on FRED); fixed, with the founder's exact conditional — gold after other asset classes have had a
huge sell-off — added as T-L5 before the first valid run. Tally 64.
"""); print("  CURRENT_STATE 18.40: appended")
tr = DOCS / "TRACK.md"; s = tr.read_text()
if "units error in the first T-L run" in s: print("  TRACK 3.35 status: already")
else:
    tr.write_text(s.rstrip("\n") + "\n\nStatus 27 Oct night: T-K0–K2 run and recorded (#77, #78 wrong, tally 64); units error in the first T-L run fixed (WTREGEN is millions); T-L5 (after an equity sell-off) and T-K1′ (volatility units) added before running; `record` subcommands write the verdicts into the register. Open after this: T-K3 LLM rubric reads; the 16 Sep statement into the corpus; GLD flows by hand.\n"); print("  TRACK 3.35: status")
for f in ("src/flows.py", "src/liquidity_link.py", "src/chair_power.py", "src/factor_attribution.py", "src/why_moved.py", "src/context.py", "app.py"):
    ast.parse(Path(f).read_text())
print("  all modules parse")
print("done -- python -m src.liquidity_link run ; python -m src.liquidity_link record ; python -m src.chair_power run ; python -m src.chair_power record")
