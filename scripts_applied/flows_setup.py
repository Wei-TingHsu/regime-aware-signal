"""23 Oct night: (1) T-G tie-break — longest patience among tied cells; (2) src/flows.py — ETF flows (SPDR Gold Trust daily archive) and CFTC positioning
(legacy futures-only COT: gold, silver, WTI), dated by when the public could know them; three new reasons in the factor model; nightly hook; records.
Run from the repo root:  python scripts_applied/flows_setup.py ; python -m src.flows update ; python -m src.flows show ;
  python -m src.factor_attribution tests GLD | sed -n 5,20p ; python -m src.factor_attribution episode GLD --start peak --end 2026-10-22 --price-start 5600 | sed -n 1,16p"""
from pathlib import Path
import sys, ast

# ---------------------------------------------------------------- 1. tie-break
wm = Path("src/why_moved.py"); s = wm.read_text()
old = '    real = sweep(F); df = pd.DataFrame([dict(window=c[0], patience=c[1], min_k=c[2], **v) for c, v in real.items()]).dropna(subset=["r5"])\n    best = df.loc[df.r5.idxmax()]; rng = np.random.default_rng(seed); mx = []'
new = ('    real = sweep(F); df = pd.DataFrame([dict(window=c[0], patience=c[1], min_k=c[2], **v) for c, v in real.items()]).dropna(subset=["r5"])\n'
       '    best = df.sort_values(["r5", "patience", "min_k"], ascending=[False, False, True]).iloc[0]   # tie-break (23 Oct): longest patience, then smallest min window\n'
       '    rng = np.random.default_rng(seed); mx = []')
if old in s: s = s.replace(old, new, 1); wm.write_text(s); print("  window_grid_rule: tie-break = longest patience")
else: print("  tie-break: already/absent")
ast.parse(Path("src/why_moved.py").read_text())

# ---------------------------------------------------------------- 2. flows.py
fl = Path("src/flows.py")
if fl.exists(): print("  flows.py: already")
else:
    fl.write_text(r'''"""
Flows and positioning (prereg_factor_attribution amendment #61, 23 Oct). Two free series, dated by when the public could know them:
  - ETF flows: SPDR Gold Trust daily archive (tonnes held / shares outstanding, 2004 ->); flow = daily log change of tonnes.
  - Positioning: CFTC Commitments of Traders, legacy futures-only, non-commercial (speculative) net position as a share of open interest for
    gold, silver and WTI; as-of Tuesday, published Friday -> the change is placed on the Friday (publication) session, zero on other days.
Writes processed/flows.parquet with columns gldflow, cot_gold, cot_silver, cot_oil (daily, aligned to sessions when read by factors()).

  python -m src.flows update        # fetch what is missing and rebuild
  python -m src.flows show
"""
from __future__ import annotations
import io, sys, zipfile, urllib.request
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

PROC, DP = Path("processed"), Path("data_provenance") / "flows"
OUT = PROC / "flows.parquet"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) regime-aware-signal academic research"}
GLD_URL = "https://www.spdrgoldshares.com/assets/dynamic/GLD/GLD_US_archive_EN.csv"
COT_YEAR = "https://www.cftc.gov/files/dea/history/deacot{y}.zip"
COT_HIST = "https://www.cftc.gov/files/dea/history/deacot1986_2016.zip"
MARKETS = {"cot_gold": ["GOLD - COMMODITY EXCHANGE"], "cot_silver": ["SILVER - COMMODITY EXCHANGE"],
           "cot_oil": ["CRUDE OIL, LIGHT SWEET - NEW YORK", "WTI-PHYSICAL - NEW YORK", "CRUDE OIL, LIGHT SWEET-WTI - ICE"]}


def _get(url, timeout=120):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read()


def gld_archive() -> pd.Series | None:
    """Tonnes in the Trust (preferred) or shares outstanding, daily. The archive's header rows vary; find the date column and a tonnes/shares column."""
    DP.mkdir(parents=True, exist_ok=True); f = DP / "GLD_US_archive_EN.csv"
    try:
        raw = _get(GLD_URL); f.write_bytes(raw)
    except Exception as e:
        print(f"  GLD archive fetch failed ({type(e).__name__}); using the file on disk if any")
        if not f.exists(): return None
    txt = f.read_text("utf-8", "ignore").splitlines()
    hdr = next((i for i, ln in enumerate(txt) if "Date" in ln and ("Tonnes" in ln or "Shares" in ln or "NAV" in ln)), None)
    if hdr is None: print("  GLD archive: header not recognised"); return None
    df = pd.read_csv(io.StringIO("\n".join(txt[hdr:])), engine="python", on_bad_lines="skip")
    dcol = next(c for c in df.columns if "Date" in str(c))
    tcol = next((c for c in df.columns if "Tonnes" in str(c)), None) or next((c for c in df.columns if "Shares" in str(c)), None)
    if tcol is None: print("  GLD archive: no tonnes/shares column"); return None
    d = pd.to_datetime(df[dcol], errors="coerce"); v = pd.to_numeric(df[tcol].astype(str).str.replace(",", ""), errors="coerce")
    s = pd.Series(v.to_numpy(), index=d).dropna(); s = s[~s.index.duplicated()].sort_index(); s.name = str(tcol); return s


def cot_frames(years) -> pd.DataFrame:
    """Legacy futures-only COT rows for the markets above, all years requested (annual zips; the 1986-2016 archive once)."""
    DP.mkdir(parents=True, exist_ok=True); frames = []
    srcs = [("hist", COT_HIST)] + [(str(y), COT_YEAR.format(y=y)) for y in years if y >= 2017]
    for tag, url in srcs:
        f = DP / f"deacot_{tag}.zip"
        if not f.exists() or tag == str(datetime.now().year):
            try: f.write_bytes(_get(url))
            except Exception as e: print(f"  COT {tag}: fetch failed ({type(e).__name__})");
        if not f.exists(): continue
        try:
            with zipfile.ZipFile(f) as z:
                name = next(n for n in z.namelist() if n.lower().endswith(".txt"))
                df = pd.read_csv(z.open(name), low_memory=False)
        except Exception as e:
            print(f"  COT {tag}: unreadable ({type(e).__name__})"); continue
        cols = {c.strip(): c for c in df.columns}
        mk = cols.get("Market and Exchange Names") or cols.get("Market_and_Exchange_Names")
        dt = cols.get("As of Date in Form YYYY-MM-DD") or cols.get("Report_Date_as_YYYY-MM-DD")
        oi = cols.get("Open Interest (All)") or cols.get("Open_Interest_All"); nl = cols.get("Noncommercial Positions-Long (All)") or cols.get("NonComm_Positions_Long_All")
        ns = cols.get("Noncommercial Positions-Short (All)") or cols.get("NonComm_Positions_Short_All")
        if not all([mk, dt, oi, nl, ns]): print(f"  COT {tag}: columns not recognised"); continue
        sub = df[[mk, dt, oi, nl, ns]].copy(); sub.columns = ["market", "date", "oi", "nc_long", "nc_short"]; sub["market"] = sub.market.astype(str).str.strip().str.upper()
        frames.append(sub)
    if not frames: return pd.DataFrame()
    allf = pd.concat(frames, ignore_index=True); allf["date"] = pd.to_datetime(allf.date, errors="coerce")
    for c in ("oi", "nc_long", "nc_short"): allf[c] = pd.to_numeric(allf[c], errors="coerce")
    return allf.dropna(subset=["date", "oi"]).drop_duplicates(subset=["market", "date"])


def cot_series(allf: pd.DataFrame) -> pd.DataFrame:
    """Net speculative position / open interest per market, as-of Tuesday; placed on the publication session (Friday, as_of + 3 days)."""
    out = {}
    for key, pats in MARKETS.items():
        m = allf[allf.market.apply(lambda x: any(x.startswith(p) for p in pats))]
        if m.empty: print(f"  COT: no rows for {key}"); continue
        m = m.sort_values(["date", "oi"]).drop_duplicates(subset=["date"], keep="last")   # largest open interest when several contracts match
        net = ((m.nc_long - m.nc_short) / m.oi).to_numpy(); pub = m.date + pd.Timedelta(days=3)
        out[key] = pd.Series(net, index=pub.to_numpy()).sort_index()
    return pd.DataFrame(out)


def update():
    PROC.mkdir(exist_ok=True); years = range(2017, datetime.now().year + 1); parts = {}
    g = gld_archive()
    if g is not None: parts["gldflow_level"] = g; print(f"  GLD archive: {g.name}, {g.index[0].date()} -> {g.index[-1].date()} ({len(g):,} days)")
    cot = cot_series(cot_frames(years)) if True else pd.DataFrame()
    for c in cot.columns: parts[c + "_level"] = cot[c]; print(f"  {c}: {cot[c].dropna().index[0].date()} -> {cot[c].dropna().index[-1].date()} ({cot[c].notna().sum():,} weeks)")
    if not parts: print("  nothing fetched"); return
    lv = pd.DataFrame(parts).sort_index(); lv.to_parquet(PROC / "flows_levels.parquet")
    # daily changes, each on its own dates (no gaps from the other series): flows = dlog tonnes; COT = change in net share on publication days
    pieces = []
    if g is not None: pieces.append(np.log(g[g > 0]).diff().rename("gldflow"))
    for c in cot.columns: pieces.append(cot[c].dropna().diff().rename(c))
    F = pd.concat(pieces, axis=1).sort_index()
    F.to_parquet(OUT); print(f"-> {OUT} ({len(F):,} rows, columns {list(F.columns)})")


def show():
    F = pd.read_parquet(OUT); print(F.dropna(how="all").tail(8).round(4)); print(F.describe().T[["count", "mean", "std"]].round(5))


if __name__ == "__main__":
    {"update": update, "show": show}[sys.argv[1] if len(sys.argv) > 1 else "update"]()
''')
    print("  flows.py: written")

# ---------------------------------------------------------------- 3. factors(): three new reasons
fa = Path("src/factor_attribution.py"); s = fa.read_text()
if '"gldflow"' in s: print("  factors: already")
else:
    s = s.replace('ORDER_DEFAULT = ["war", "hikes", "real", "dollar", "oil", "vix", "btc", "macro1", "macro2"]',
                  'ORDER_DEFAULT = ["war", "hikes", "real", "dollar", "oil", "vix", "btc", "gldflow", "cot_gold", "cot_silver", "cot_oil", "macro1", "macro2"]', 1)
    s = s.replace('"btc": "speculative liquidity (Bitcoin)"}', '"btc": "speculative liquidity (Bitcoin)", "gldflow": "gold ETF flows (tonnes held)", "cot_gold": "speculative positioning in gold (CFTC)", "cot_silver": "speculative positioning in silver (CFTC)", "cot_oil": "speculative positioning in oil (CFTC)"}', 1)
    old = '    pc = PROC / "macro_pca_scores.parquet"\n'
    new = '''    fp = PROC / "flows.parquet"
    if fp.exists():
        fl = pd.read_parquet(fp); fl.index = pd.to_datetime(fl.index); fl = fl.reindex(idx)      # a flow/positioning change lands on the session it became public; other sessions 0
        for c in ("gldflow", "cot_gold", "cot_silver", "cot_oil"):
            if c in fl.columns and fl[c].notna().sum() > 200: F[c] = fl[c].fillna(0.0)
    pc = PROC / "macro_pca_scores.parquet"
'''
    assert old in s, "factors anchor"; s = s.replace(old, new, 1); fa.write_text(s); print("  factors: gldflow, cot_gold, cot_silver, cot_oil")
ast.parse(Path("src/factor_attribution.py").read_text()); print("  factor_attribution parses")

d = Path("daily_run.sh"); s = d.read_text()
if "src.flows update" in s: print("  daily_run flows: already")
else:
    old = "python -m src.why_moved run > /dev/null"
    if old in s: d.write_text(s.replace(old, 'python -m src.flows update || echo "  flows update failed -- continuing"\n' + old, 1)); print("  daily_run: flows update before why_moved")
    else: print("  daily_run anchor not found -- add by hand before why_moved: python -m src.flows update")

p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "SPDR Gold Trust daily archive" in s: print("  prereg: already")
else:
    s = s.replace("| date | change | reason |\n|---|---|---|\n", "| date | change | reason |\n|---|---|---|\n| 2026-10-23 (night) | **Flows and positioning proxies in** (amendment #61 executed): gold ETF flows = daily log change of tonnes held, from the SPDR Gold Trust daily archive (2004 →); speculative positioning = CFTC legacy futures-only non-commercial net position ÷ open interest for gold, silver and WTI (1986 →), as-of Tuesday and placed on the Friday publication session (zero on other sessions). "
        "Three new reasons in the factor set (13 in all); T-A/T-B and the gold episode re-run. **T-G tie-break:** among cells tied on median share, the longest patience (then the smallest min window) — on gold's current leg patience 7 stopped at 4 sessions (43%) where 20–30 reaches the 23-session window (62%). | Gold's 2026 fall was ≈ 90% outside the standard factors; the founder's forced-selling hypothesis needs a series. Prior #61 stands: T-A 0.20–0.25, the episode's unexplained share below half. |\n", 1)
    p.write_text(s); print("  prereg: flows amendment executed, tie-break")
print("done -- python -m src.flows update ; python -m src.flows show ; python -m src.factor_attribution tests GLD")
