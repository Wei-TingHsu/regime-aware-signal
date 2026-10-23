"""23 Oct evening: retracement rule capped at the coarse threshold (the f=50% freeze); extremes from highs/lows and day-sign from open/close as
grid variables (founder's two-step); records (T-J PASS, #71 wrong, tally 59; priors #72, #73). Run from the repo root:
  python scripts_applied/retrace_hl_setup.py ; python -m src.why_moved segmenter-test GLD | sed -n 5,8p ; python -m src.why_moved segmenter-test GLD | grep "zigzag\\|retrace" ;
  python -m src.why_moved run | grep -A3 "^## gold" | sed -n 3,4p"""
from pathlib import Path
import sys

wm = Path("src/why_moved.py"); s = wm.read_text()
if "def ohlc(" in s: print("  why_moved hl/cap: already")
else:
    old = s[s.index("def turning_points_retrace(r: pd.Series, f: float = 0.382, n: int = 5, c: float = 1.0):"):s.index("def two_scale(")]
    new = '''def ohlc(asset: str):
    """Open/High/Low/Close ratios to the close for the panel's assets (raw Yahoo cache, adjusted consistently); None where only closes exist."""
    p = Path("raw/yfinance") / f"{asset}.parquet"
    if not p.exists(): return None
    try:
        d = pd.read_parquet(p); d.index = pd.to_datetime(d.index)
        cols = {str(c).split("'")[1] if str(c).startswith("(") else str(c): c for c in d.columns}
        need = {k: cols[k] for k in ("Open", "High", "Low", "Close") if k in cols}
        if len(need) < 4: return None
        o = pd.DataFrame({k: d[v].astype(float) for k, v in need.items()}).dropna()
        return pd.DataFrame({"hi": o.High / o.Close, "lo": o.Low / o.Close, "oc": np.sign(o.Close - o.Open)}, index=o.index)
    except Exception:
        return None


def turning_points_retrace(r: pd.Series, f: float = 0.382, n: int = 5, c: float = 1.0, cap: bool = True, hl=None, daysign: str = "close"):
    """Founder's gradient test made operational: the sign of every back-gradient from today equals the sign of (today - that day), so 'all one sign'
    means today is the leg's extreme; a change of sign is a drawdown from the extreme. A turn is confirmed when that drawdown exceeds
    max(f x the leg's own move so far, c x monthly volatility) — capped at the coarse zigzag threshold (cap=True; without it a 50% retracement of a
    long trend is unreachable and the rule freezes) — and has persisted n sessions since the extreme (daysign='close') or n open-to-close days
    against the trend (daysign='oc'). hl: ratios High/Close, Low/Close (and the open-to-close sign) so extremes are the intraday ones.
    Returns tps, trend, extreme, px (closes), lags."""
    rr = r.fillna(0.0); px = np.exp(rr.cumsum().to_numpy()); lp = np.log(px)
    if hl is not None:
        h = hl.reindex(r.index); hi_r = h.hi.fillna(1.0).to_numpy(); lo_r = h.lo.fillna(1.0).to_numpy(); oc = h.oc.fillna(0.0).to_numpy()
    else:
        hi_r = lo_r = np.ones(len(px)); oc = np.sign(rr.to_numpy())
    pxh, pxl = np.log(px * hi_r), np.log(px * lo_r)                      # intraday extremes in log units (== closes when hl is None)
    sig = rr.rolling(20).std().bfill().fillna(rr.std()).to_numpy() * np.sqrt(20); coarse = np.maximum(FLOOR, MULT * sig)
    hi = lo = 0; trend = 0; start = 0; tps = []; lags = []; run_ = 0
    for i in range(1, len(px)):
        if trend >= 0 and pxh[i] > pxh[hi]: hi = i
        if trend <= 0 and pxl[i] < pxl[lo]: lo = i
        if daysign == "oc":
            against = (oc[i] < 0) if trend >= 0 else (oc[i] > 0); run_ = run_ + 1 if against else 0
        if trend >= 0:
            leg = pxh[hi] - pxl[start]; dd = pxh[hi] - lp[i]; thr = max(f * max(leg, 0.0), c * sig[i]); thr = min(thr, coarse[i]) if cap else thr
            persisted = (run_ >= n) if daysign == "oc" else (i - hi >= n)
            if dd >= thr and persisted:
                tps.append((hi, "peak")); lags.append(i - hi); trend = -1; start = hi; lo = i; run_ = 0; continue
        if trend <= 0:
            leg = pxh[start] - pxl[lo]; up = lp[i] - pxl[lo]; thr = max(f * max(leg, 0.0), c * sig[i]); thr = min(thr, coarse[i]) if cap else thr
            persisted = (run_ >= n) if daysign == "oc" else (i - lo >= n)
            if up >= thr and persisted:
                tps.append((lo, "trough")); lags.append(i - lo); trend = 1; start = lo; hi = i; run_ = 0
    return tps, trend, (hi if trend > 0 else lo), px, lags


'''
    s = s.replace(old, new, 1)
    # two_scale passes hl / daysign through
    s = s.replace("def two_scale(r: pd.Series, fine=None):", "def two_scale(r: pd.Series, fine=None, hl=None, daysign: str = \"close\"):", 1)
    s = s.replace("    tps_f, trend_f, ext_f, _, lags = turning_points_retrace(sub, *fine)", "    tps_f, trend_f, ext_f, _, lags = turning_points_retrace(sub, *fine, hl=hl, daysign=daysign)", 1)
    # segmenters per asset (hl cells need the asset's OHLC)
    old = "    r = returns(asset).dropna(); F = factors(r.index); idx = r.index\n    J = json.loads((PROC / \"factor_attribution.json\").read_text()) if (PROC / \"factor_attribution.json\").exists() else {}\n    bb = "
    new = ("    r = returns(asset).dropna(); F = factors(r.index); idx = r.index; HL = ohlc(asset)\n"
           "    SEGS = SEGMENTERS + ([(f\"retrace-hl f=38%, N={n}, c={c}\", (lambda n, c: (lambda rr_: turning_points_retrace(rr_, 0.382, n, c, True, HL, \"close\")))(n, c)) for n in (3, 5) for c in (0.5, 1.0)]\n"
           "                        + [(f\"retrace-hl-oc f=38%, N={n}, c={c}\", (lambda n, c: (lambda rr_: turning_points_retrace(rr_, 0.382, n, c, True, HL, \"oc\")))(n, c)) for n in (3, 5) for c in (0.5, 1.0)] if HL is not None else [])\n"
           "    J = json.loads((PROC / \"factor_attribution.json\").read_text()) if (PROC / \"factor_attribution.json\").exists() else {}\n    bb = ")
    assert old in s, "segmenter_test head anchor"; s = s.replace(old, new, 1)
    s = s.replace("    for name, fn in SEGMENTERS:\n        res = fn(r); tps, trend, ext, px = res[:4]; lags = res[4] if len(res) > 4 else None", "    for name, fn in SEGS:\n        res = fn(r); tps, trend, ext, px = res[:4]; lags = res[4] if len(res) > 4 else None", 1)
    # promotion json: parse hl / oc variants
    old = '''        import re as _re; mm = _re.match(r"retrace f=(\\d+)%, N=(\\d+), c=([\\d.]+)", fine_best.rule)
        (PROC / "fine_rule.json").write_text(json.dumps(dict(rule="retrace", f={25: 0.25, 38: 0.382, 50: 0.5}.get(int(mm.group(1)), int(mm.group(1)) / 100), n=int(mm.group(2)), c=float(mm.group(3)), promoted=datetime.now().strftime("%Y-%m-%d"),'''
    new = '''        import re as _re; mm = _re.match(r"retrace(-hl)?(-oc)? f=(\\d+)%, N=(\\d+), c=([\\d.]+)", fine_best.rule)
        (PROC / "fine_rule.json").write_text(json.dumps(dict(rule="retrace", hl=bool(mm.group(1)), daysign=("oc" if mm.group(2) else "close"), f={25: 0.25, 38: 0.382, 50: 0.5}.get(int(mm.group(3)), int(mm.group(3)) / 100), n=int(mm.group(4)), c=float(mm.group(5)), promoted=datetime.now().strftime("%Y-%m-%d"),'''
    assert old in s, "promotion json anchor"; s = s.replace(old, new, 1)
    s = s.replace('    fine_ok = df[(df.rule.str.startswith("retrace")) & (df.missed == 0) & (df.lag <= 10) & (df.r5 >= reg.r5 - 0.05) & (df.legs >= reg.legs)] if np.isfinite(reg.r5) else df.iloc[0:0]   # T-J fine scale: sees every turn, confirms fast, explains nearly as well',
                  '    fine_ok = df[(df.rule.str.startswith("retrace")) & (df.missed == 0) & (df.lag <= 10) & (df.r5 >= reg.r5 - 0.05) & (df.legs >= reg.legs)] if np.isfinite(reg.r5) else df.iloc[0:0]   # T-J fine scale: sees every turn, confirms fast, explains nearly as well', 1)
    # run(): hl / daysign from the promotion file
    old = '''            fj = json.loads(FINE.read_text()); ts = two_scale(r, (fj["f"], fj["n"], fj["c"]))'''
    new = '''            fj = json.loads(FINE.read_text()); ts = two_scale(r, (fj["f"], fj["n"], fj["c"]), hl=(ohlc(a) if fj.get("hl") else None), daysign=fj.get("daysign", "close"))'''
    assert old in s, "run two_scale anchor"; s = s.replace(old, new, 1)
    s = s.replace('                tps_hist = turning_points_retrace(r, fj["f"], fj["n"], fj["c"])[0]',
                  '                tps_hist = turning_points_retrace(r, fj["f"], fj["n"], fj["c"], True, (ohlc(a) if fj.get("hl") else None), fj.get("daysign", "close"))[0]', 1)
    s = s.replace('''                rule_label = (f"big picture by the zigzag; the current leg by the founder's retracement rule — a turn is confirmed when the price has given back "
                              f"{fj['f']:.0%} of the leg's own move (floor {fj['c']}× monthly volatility) and stayed there {fj['n']} sessions (promoted {fj['promoted']})")''',
                  '''                rule_label = (f"big picture by the zigzag; the current leg by the founder's retracement rule — a turn is confirmed when the price has given back "
                              f"{fj['f']:.0%} of the leg's own move (floor {fj['c']}× monthly volatility, never more than the zigzag's threshold) and "
                              f"{'stayed there ' + str(fj['n']) + ' sessions' if fj.get('daysign', 'close') == 'close' else str(fj['n']) + ' open-to-close days have gone against the trend'}"
                              f"{'; extremes taken from the high and low of the day' if fj.get('hl') else ''} (promoted {fj['promoted']})")''', 1)
    wm.write_text(s); print("  why_moved: cap at the coarse threshold, high/low extremes, open-to-close day sign, grid cells, promotion carries them")

# records
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "| 2026-10-23 | T-J (GLD) |" in s: print("  prereg T-J record: already")
else:
    s = s.replace("| date | change | reason |\n|---|---|---|\n", "| date | change | reason |\n|---|---|---|\n| 2026-10-23 (evening) | **Retracement rule capped** at the coarse zigzag threshold; **extremes source** {close, high/low} and **day-sign basis** {close-to-close, open-to-close} added as grid variables (the founder's two-step: open/close says whether the day rose or fell, high/low carries the gradient). | "
        "f = 50% found 9 legs since 2006: after a long trend 'give back half the leg' is unreachable and the rule freezes; the f = 38% / c = 1.0 cells each hid one 15% counter-move for the same reason. The fine scale may never demand more than the coarse one. **Prior #72:** with the cap the c = 1.0 cells reach 0 missed and keep ~74%. **Prior #73:** high/low extremes move turning points 0–2 sessions earlier and change the share by < 3 points. |\n", 1)
    s = s.rstrip("\n") + ("\n| 2026-10-23 | T-J (GLD) | **PASS — fine scale promoted: retrace f = 38%, N = 3, floor 0.5× vol**: 215 legs, 0 missed, lag 6 sessions, 70% explained (zigzag: 54 legs, 3 missed, 68%). f = 38% / c = 1.0 cells beat the zigzag outright (74–76%, 107–109 legs) but hide one 15% counter-move each; f = 50% froze (9 legs). "
        "Gold's current leg reads the same at both scales (down since 25 Aug); the fine base rate: typical fall −6% over 14 sessions, this one 241% of it. | **#71 wrong** (named the c = 1.0 cell: 1 missed, lag 12, share 76% not 62%). Tally 59 |\n")
    p.write_text(s); print("  prereg: T-J result, cap/hl amendment, #72–#73")
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "tally 59" in s: print("  MASTER: already")
else:
    s = s.replace("| registered 23 Oct evening before code; run same evening | prior #71 promoted at f = 38%, N = 5 |", "| 23 Oct evening | **PASS**: f = 38%, N = 3, floor 0.5× vol — 215 legs, 0 missed, lag 6, 70% (#71 wrong on the cell); capped and high/low variants registered (#72, #73) |", 1)
    s = s.replace("#70 persist-time share, all Claude's)", "#70 persist-time share, #71 retracement cell, all Claude's)", 1).replace("tally 58 (#40", "tally 59 (#40", 1)
    m.write_text(s); print("  MASTER: row 50 result, tally 59")
print("done -- python -m src.why_moved segmenter-test GLD")
