"""
Dynamic issuer pool (TRACK 3.32). Founder's rule, 23 Oct: choose the earnings issuers each quarter from whatever is driving the economy.
Measured form: BEA NIPA table 1.1.2 (contributions to percent change in real GDP, quarterly) -> fixed line-to-sector map -> sectors ranked by
their share of the positive contributions until >= 70% is covered -> the largest issuers by market value in those sectors (S&P 500 list from
Wikipedia, market values from Yahoo), plus the ten largest index weights always, plus the nine original issuers for continuity. Cap 35.
Every build is logged; a changed pool is a dated corpus amendment (prereg_report_scoreboard).
Note the premise corrected on registration: the ~70% figure in the GDP release is personal consumption's share of the LEVEL of GDP; AI-related
investment is a few percent of the level but a large share of recent GROWTH -- the rule therefore ranks by contributions to growth.

  python -m src.issuer_pool build [--year 2026] [--cover 0.70] [--per-sector 4]
  python -m src.issuer_pool show
"""
from __future__ import annotations
import json, os, sys, urllib.request
from datetime import datetime
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
PROC, DOCS, DP = Path("processed"), Path("docs"), Path("data_provenance")
ORIGINAL = ["NVDA", "TSM", "ASML", "MU", "INTC", "MSFT", "ORCL", "TSLA", "LMT"]
# NIPA 1.1.2 line numbers -> GICS sectors (weights sum to 1 per line). Fixed at registration; changes are dated amendments.
LINE_MAP = {
    4:  ("Durable goods",            {"Consumer Discretionary": .7, "Information Technology": .3}),
    5:  ("Nondurable goods",         {"Consumer Staples": .7, "Energy": .3}),
    6:  ("Services",                 {"Health Care": .3, "Financials": .2, "Communication Services": .2, "Consumer Discretionary": .2, "Utilities": .1}),
    10: ("Structures",               {"Industrials": .4, "Real Estate": .3, "Energy": .3}),
    11: ("Equipment",                {"Information Technology": .7, "Industrials": .3}),
    12: ("Intellectual property",    {"Information Technology": .6, "Communication Services": .2, "Health Care": .2}),
    13: ("Residential",              {"Consumer Discretionary": .6, "Materials": .2, "Financials": .2}),
    14: ("Change in inventories",    {"Industrials": .5, "Consumer Discretionary": .5}),
    16: ("Exports",                  {"Industrials": .4, "Energy": .3, "Information Technology": .3}),
    24: ("National defense",         {"Industrials": 1.0}),
    25: ("Federal nondefense",       {"Health Care": .3, "Industrials": .4, "Utilities": .3}),
    26: ("State and local",          {"Health Care": .3, "Industrials": .4, "Utilities": .3}),
}


FRED_IDS = {4: "DDURRY2Q224SBEA", 5: "DNDGRY2Q224SBEA", 6: "DSERRY2Q224SBEA", 10: "A009RY2Q224SBEA", 11: "Y033RY2Q224SBEA", 12: "Y001RY2Q224SBEA",
            13: "A011RY2Q224SBEA", 14: "A014RY2Q224SBEA", 16: "A020RY2Q224SBEA", 24: "A824RY2Q224SBEA", 25: "A825RY2Q224SBEA", 26: "A829RY2Q224SBEA"}


def fred_contributions() -> tuple[str, pd.DataFrame]:
    """NIPA 1.1.2 contributions to percent change in real GDP, from FRED (same BEA numbers; FRED key already on file)."""
    from fredapi import Fred
    key = os.environ.get("FRED_API_KEY") or _env("FRED_API_KEY")
    if not key: raise RuntimeError("FRED_API_KEY missing")
    fred = Fred(api_key=key); rows = []; missing = []
    for ln, sid in FRED_IDS.items():
        try:
            ser = fred.get_series(sid).dropna(); rows.append(dict(LineNumber=ln, LineDescription=LINE_MAP[ln][0], TimePeriod=f"{ser.index[-1].year}Q{(ser.index[-1].month - 1) // 3 + 1}", DataValue=float(ser.iloc[-1])))
        except Exception as e:
            missing.append(f"{sid} ({type(e).__name__})")
    if not rows: raise RuntimeError("FRED returned nothing: " + "; ".join(missing))
    if missing: print(f"  FRED series not found: {', '.join(missing)}")
    df = pd.DataFrame(rows); q = df.TimePeriod.mode().iloc[0]
    return q, df[df.TimePeriod == q].set_index("LineNumber")


def bea_contributions(year: int) -> tuple[str, pd.DataFrame]:
    key = next((v for v in (os.environ.get(n) or _env(n) for n in ("BEA_API_KEY", "BEA_KEY", "BEA_USERID", "BEA_USER_ID", "BEAKEY")) if v), "")
    if not key: raise RuntimeError(f"no BEA key under BEA_API_KEY/BEA_KEY/BEA_USERID/BEA_USER_ID/BEAKEY; names present in .env: {_env_names()}")
    url = (f"https://apps.bea.gov/api/data/?&UserID={key}&method=GetData&datasetname=NIPA&TableName=T10102&Frequency=Q&Year={year}&ResultFormat=JSON")
    js = json.loads(urllib.request.urlopen(url, timeout=60).read().decode())
    res = js.get("BEAAPI", {}).get("Results", {})
    if "Data" not in res: raise RuntimeError("BEA said: " + json.dumps(res or js)[:300])
    rows = res["Data"]
    df = pd.DataFrame(rows)[["LineNumber", "LineDescription", "TimePeriod", "DataValue"]]
    df["LineNumber"] = df.LineNumber.astype(int); df["DataValue"] = pd.to_numeric(df.DataValue.str.replace(",", ""), errors="coerce")
    q = sorted(df.TimePeriod.unique())[-1]; d = df[df.TimePeriod == q].set_index("LineNumber")
    return q, d


def _env(name):
    try:
        for ln in Path(".env").read_text().splitlines():
            ln = ln.strip().removeprefix("export ").strip()
            if "=" in ln and ln.split("=", 1)[0].strip() == name: return ln.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception: pass
    return ""


def _env_names():
    try: return sorted({ln.strip().removeprefix("export ").split("=", 1)[0].strip() for ln in Path(".env").read_text().splitlines() if "=" in ln and not ln.strip().startswith("#")})
    except Exception: return []


def universe() -> pd.DataFrame:
    """S&P 500 constituents with GICS sector (Wikipedia) and market value (Yahoo). Cached per quarter."""
    cache = DP / "issuer_universe.csv"
    if cache.exists() and (datetime.now() - datetime.fromtimestamp(cache.stat().st_mtime)).days < 80:
        return pd.read_csv(cache)
    wiki_html = urllib.request.urlopen(urllib.request.Request("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies", headers={"User-Agent": "Mozilla/5.0 regime-aware-signal research"}), timeout=60).read().decode("utf-8", "ignore")
    import io; t = pd.read_html(io.StringIO(wiki_html))[0]
    u = t.rename(columns={"Symbol": "ticker", "GICS Sector": "sector", "Security": "name"})[["ticker", "name", "sector"]]
    u["ticker"] = u.ticker.str.replace(".", "-", regex=False)
    import yfinance as yf
    caps = []
    for tk in u.ticker:
        try:
            fi = yf.Ticker(tk).fast_info; caps.append(float(getattr(fi, "market_cap", None) or fi["marketCap"]))
        except Exception: caps.append(float("nan"))
    u["mcap"] = caps; u.to_csv(cache, index=False); return u


def build(year=None, cover=0.70, per_sector=4, cap=35):
    year = year or datetime.now().year
    try:
        q, d = fred_contributions(); print(f"  contributions from FRED, latest quarter {q}")
    except Exception as e:
        print(f"  FRED route failed: {e}; trying BEA")
        q, d = bea_contributions(year)
    sec = {}
    for ln, (label, wmap) in LINE_MAP.items():
        v = float(d.loc[ln, "DataValue"]) if ln in d.index else 0.0
        if v <= 0: continue
        for s_, w in wmap.items(): sec[s_] = sec.get(s_, 0.0) + v * w
    tot = sum(sec.values()); ranked = sorted(sec.items(), key=lambda x: -x[1]); chosen, cum = [], 0.0
    for s_, v in ranked:
        chosen.append(s_); cum += v
        if cum / tot >= cover: break
    u = universe().dropna(subset=["mcap"]).sort_values("mcap", ascending=False)
    top10 = list(u.ticker.head(10)); by_sector = {s_: list(u[u.sector == s_].ticker.head(per_sector)) for s_ in chosen}
    pool = []
    for tk in ORIGINAL + top10 + [t for s_ in chosen for t in by_sector[s_]]:
        if tk not in pool: pool.append(tk)
    pool = pool[:cap]
    rec = {"built": datetime.now().strftime("%Y-%m-%d %H:%M"), "quarter": q, "cover": cover, "sector_scores": dict(ranked), "chosen_sectors": chosen,
           "top10": top10, "by_sector": by_sector, "pool": pool}
    (PROC / "issuer_pool.json").write_text(json.dumps(rec, indent=1)); (PROC / "issuer_pool_tickers.txt").write_text(",".join(pool) + "\n")
    L = [f"# Issuer pool — built {rec['built']} from BEA contributions to real GDP growth, {q}", "",
         f"*Rule (TRACK 3.32): sectors ranked by their mapped share of the positive contributions to last quarter's growth, taken until ≥ {cover:.0%} is covered; "
         f"the {per_sector} largest issuers by market value in each; plus the ten largest index weights always; plus the nine original issuers. Cap {cap}. "
         "Line-to-sector map fixed in src/issuer_pool.py; a changed pool is a dated corpus amendment.*", "",
         "| sector | mapped contribution (pp of growth) | share | chosen |", "|---|---|---|---|"]
    for s_, v in ranked: L.append(f"| {s_} | {v:+.2f} | {v / tot:.0%} | {'yes' if s_ in chosen else ''} |")
    L += ["", f"**Pool ({len(pool)}):** " + ", ".join(pool), "", f"Top-10 index weights: {', '.join(top10)}", "",
          "Premise note: the ~70% figure in the GDP release is personal consumption's share of the level of GDP; AI-related investment is a few percent of the "
          "level and a large share of recent growth, which is why the rule ranks contributions to growth, not levels."]
    hist = DOCS / "issuer_pool.md"; prev = hist.read_text() if hist.exists() else ""
    hist.write_text("\n".join(L) + "\n\n---\n\n" + prev); print("\n".join(L)); print(f"-> docs/issuer_pool.md, processed/issuer_pool_tickers.txt")


def show():
    j = json.loads((PROC / "issuer_pool.json").read_text()); print(f"{j['quarter']}: {', '.join(j['pool'])}")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build"); b.add_argument("--year", type=int, default=None); b.add_argument("--cover", type=float, default=0.70); b.add_argument("--per-sector", type=int, default=4)
    sub.add_parser("show"); a = ap.parse_args()
    build(a.year, a.cover, a.per_sector) if a.cmd == "build" else show()
