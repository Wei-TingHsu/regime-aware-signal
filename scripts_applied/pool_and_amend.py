"""23 Oct: (1) record factor-attribution T-A/T-B (priors #58, #59 wrong -> tally 53) and the GLD episode reading; amendment: --start peak,
BTC as a speculative-liquidity proxy, ETF-flow and CFTC proxies registered; (2) dynamic issuer pool from BEA contributions to GDP growth
(src/issuer_pool.py, TRACK 3.32), nightly 8-K fetch reads the pool file.
Run from the repo root:  python scripts_applied/pool_and_amend.py ; python -m src.issuer_pool build ; python -m src.factor_attribution episode GLD --start peak --end 2026-10-21 --price-start 5600"""
from pathlib import Path
import sys

# ---------------------------------------------------------------- 1a. records
p = Path("docs/prereg_factor_attribution.md"); s = p.read_text()
if "| 2026-10-23 | T-A |" in s: print("  prereg results: already")
else:
    s = s.rstrip("\n") + """
| 2026-10-23 | T-A | GLD median out-of-sample R² **0.177** over 235 blocks (bar 0.20) → **FAIL**. `docs/factor_attribution_tests.md` | **#58 wrong** (expected 0.25–0.40). Tally 52 |
| 2026-10-23 | T-B | Stable: dollar 100%, oil 90%, macro line 2 88%, macro line 1 83%. Unstable: hikes 66%, real yield 63%, VIX 59%, war (GPR) 54%. | **#59 wrong** (real, hikes expected stable; oil expected unstable). Tally 53 |
| 2026-10-23 | episode GLD 28 Jan → 21 Oct (first run, dates a guess) | Move −19% (not the −29% of 5,600 → 4,000: 28 Jan was not the peak; the war index fell −14% over the window — its spike was in March). With pre-episode sensitivities the named reasons explain ≈ $90 of a $1,200 fall; the prior uptrend (drift) would have added ≈ $1,700; ≈ $2,800 unexplained. Orderings agree (the war proxy barely moved). Reading: 2026 broke gold's 2024–25 sensitivities (rose with oil, despite rate rises); the unexplained part is where no proxy exists — positioning and forced selling. | diagnostic, not a verdict |
"""
    old = "| date | change | reason |\n|---|---|---|\n"
    s = s.replace(old, old + "| 2026-10-23 | `--start peak` finds the episode's own peak (max close in the prior 300 sessions); **new proxies**: BTC-USD (speculative liquidity, in the model now), "
                  "GLD shares outstanding (ETF flows) and CFTC net speculative gold positions (weekly) registered, fetchers next; silver deliberately excluded (gold's twin — would explain without naming a reason). "
                  "Tests re-run after the proxies land; the 23 Oct verdicts stand as the baseline. **Prior #61:** with flows and positioning, T-A rises to 0.20–0.25 and the 2026 episode's unexplained share falls below half. | "
                  "First-run reading: the fall is unexplained by standard factors; the founder's forced-selling hypothesis has no proxy in the model. |\n", 1)
    p.write_text(s); print("  prereg results + amendment: appended")
m = Path("docs/PROJECT_MASTER.md"); s = m.read_text()
if "tally 53" in s: print("  MASTER tally: already")
else:
    s = s.replace("#51 H3 dollar-shock count, all Claude's)", "#51 H3 dollar-shock count, #55 target-range calibration sign, #58–#59 factor attribution R² and sign stability, all Claude's)", 1)
    s = s.replace("tally 50 (#40", "tally 53 (#40", 1)
    s = s.replace("| registered 23 Oct before code; T-A/T-B run next | priors #58 PASS, #59 war/oil unstable, #60 T-C FAIL/INCONCLUSIVE |",
                  "| 23 Oct T-A/T-B run | **T-A FAIL 0.177** (#58 wrong); T-B dollar/oil/macro stable, real/hikes/VIX/war unstable (#59 wrong); flows + positioning proxies amended in (#61); T-C after |", 1)
    m.write_text(s); print("  MASTER: tally 53, row 47 result")

# ---------------------------------------------------------------- 1b. factor_attribution: --start peak, BTC proxy
f = Path("src/factor_attribution.py"); s = f.read_text()
if '"btc"' in s: print("  factor_attribution amendments: already")
else:
    s = s.replace('ORDER_DEFAULT = ["war", "hikes", "real", "dollar", "oil", "vix", "macro1", "macro2"]',
                  'ORDER_DEFAULT = ["war", "hikes", "real", "dollar", "oil", "vix", "btc", "macro1", "macro2"]', 1)
    s = s.replace('"macro2": "macro state, PCA line 2"}', '"macro2": "macro state, PCA line 2", "btc": "speculative liquidity (Bitcoin)"}', 1)
    old = '    pc = PROC / "macro_pca_scores.parquet"\n'
    new = '''    bp = PROC / "btc_daily.parquet"
    if not bp.exists():
        try:
            import yfinance as yf
            b = yf.Ticker("BTC-USD").history(period="max", interval="1d")["Close"]; b.index = pd.to_datetime(b.index).tz_localize(None).normalize(); b.to_frame("BTC").to_parquet(bp)
        except Exception: pass
    if bp.exists():
        b = pd.read_parquet(bp)["BTC"]; b.index = pd.to_datetime(b.index); F["btc"] = np.log(b.reindex(idx).ffill()).diff()
    pc = PROC / "macro_pca_scores.parquet"
'''
    s = s.replace(old, new, 1)
    old = "    s0, s1 = pd.Timestamp(start), pd.Timestamp(end)\n"
    new = '''    s1 = pd.Timestamp(end)
    if str(start) == "peak":                      # the episode's own peak: highest cumulative level in the 300 sessions before the end
        cum = r.loc[:s1].cumsum().iloc[-300:]; s0 = cum.idxmax(); start = s0.strftime("%Y-%m-%d"); print(f"  peak found: {start}")
    else: s0 = pd.Timestamp(start)
'''
    s = s.replace(old, new, 1)
    f.write_text(s); print("  factor_attribution: --start peak, BTC proxy")

# ---------------------------------------------------------------- 2. dynamic issuer pool
ip = Path("src/issuer_pool.py")
if ip.exists(): print("  issuer_pool.py: already")
else:
    ip.write_text(r'''"""
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


def bea_contributions(year: int) -> tuple[str, pd.DataFrame]:
    key = os.environ.get("BEA_API_KEY") or _env("BEA_API_KEY")
    url = (f"https://apps.bea.gov/api/data/?&UserID={key}&method=GetData&datasetname=NIPA&TableName=T10102&Frequency=Q&Year={year}&ResultFormat=JSON")
    js = json.loads(urllib.request.urlopen(url, timeout=60).read().decode())
    rows = js["BEAAPI"]["Results"]["Data"]
    df = pd.DataFrame(rows)[["LineNumber", "LineDescription", "TimePeriod", "DataValue"]]
    df["LineNumber"] = df.LineNumber.astype(int); df["DataValue"] = pd.to_numeric(df.DataValue.str.replace(",", ""), errors="coerce")
    q = sorted(df.TimePeriod.unique())[-1]; d = df[df.TimePeriod == q].set_index("LineNumber")
    return q, d


def _env(name):
    try:
        for ln in Path(".env").read_text().splitlines():
            if ln.startswith(name + "="): return ln.split("=", 1)[1].strip().strip('"').strip("'")
    except Exception: pass
    return ""


def universe() -> pd.DataFrame:
    """S&P 500 constituents with GICS sector (Wikipedia) and market value (Yahoo). Cached per quarter."""
    cache = DP / "issuer_universe.csv"
    if cache.exists() and (datetime.now() - datetime.fromtimestamp(cache.stat().st_mtime)).days < 80:
        return pd.read_csv(cache)
    t = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]
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
        q, d = bea_contributions(year)
    except Exception as e:
        q, d = bea_contributions(year - 1); print(f"  BEA {year} unavailable ({type(e).__name__}); using {q}")
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
''')
    print("  issuer_pool.py: written")

d = Path("daily_run.sh"); s = d.read_text()
if "issuer_pool_tickers.txt" in s: print("  daily_run pool: already")
else:
    import re
    new_line = ('POOL="$(cat processed/issuer_pool_tickers.txt 2>/dev/null || echo NVDA,TSM,ASML,MU,INTC,MSFT,ORCL,TSLA,LMT)"\n'
                'python -m src.fetch_sources edgar --tickers "$POOL" --limit 4 --sleep 0.5 || echo')
    s2, n = re.subn(r'python -m src\.fetch_sources edgar --tickers [A-Z,]+ --limit 4 --sleep 0\.5 \|\| echo', new_line, s, count=1)
    if n: d.write_text(s2); print("  daily_run pool: nightly 8-K fetch reads processed/issuer_pool_tickers.txt")
    else: print("  daily_run 8-K line not found -- edit by hand")

t = Path("docs/TRACK.md"); s = t.read_text()
anchor = "## 4. Potential upgrades — not registered, not costed\n"
if "### 3.32 Dynamic issuer pool" in s: print("  TRACK 3.32: already")
else:
    add = """### 3.32 Dynamic issuer pool — issuers chosen by what drives the economy (registered 23 Oct; built)

Founder's rule: adjust the earnings issuers round by round to the largest contributors to the economy (the top few covering 60–70%). Measured
form: BEA table 1.1.2 contributions to real GDP growth → fixed line-to-sector map → sectors ranked until ≥ 70% of the positive contributions
are covered → the four largest issuers by market value per sector (S&P 500 list, Yahoo market values), plus the ten largest index weights,
plus the nine original issuers; cap 35; rebuilt quarterly after the advance GDP release; every build logged in `docs/issuer_pool.md`, a changed
pool is a dated corpus amendment. Premise corrected at registration: the ~70% in the GDP release is consumption's share of the level, not AI;
AI investment is a large share of growth, which is what the rule ranks. Registered cell to test the idea rather than assume it: "releases of the
pool's issuers move SPY at 2 sessions" (prereg_report_scoreboard, corpus tag). `src/issuer_pool.py`; nightly fetch reads the pool file.

"""
    t.write_text(s.replace(anchor, add + anchor, 1)); print("  TRACK 3.32: done")
c = Path("docs/CURRENT_STATE_2026-08-23.md"); s = c.read_text()
if "### 18.35" in s: print("  CURRENT_STATE 18.35: already")
else:
    c.write_text(s.rstrip("\n") + """

### 18.35 Factor attribution first run; dynamic issuer pool (23 Oct)

Factor attribution (3.31) built and tested the same night: T-A out-of-sample R² 0.177 FAIL (#58 wrong), T-B dollar/oil/macro stable, real
yields/hikes/VIX/war unstable (#59 wrong), tally 53. The GLD 2026 episode, with pre-episode sensitivities: named reasons ≈ $90 of a $1,200
fall, prior uptrend +$1,700, unexplained ≈ $2,800 — 2026 broke gold's 2024–25 sensitivities; the unexplained part is where positioning and
forced selling live, for which the model had no proxy. Amendment: `--start peak`, Bitcoin as a speculative-liquidity proxy, ETF flows and CFTC
positioning registered (prior #61). Dynamic issuer pool (3.32) built from BEA contributions to growth; the nightly 8-K fetch reads it.
"""); print("  CURRENT_STATE 18.35: appended")
print("done -- python -m src.issuer_pool build ; python -m src.factor_attribution episode GLD --start peak --end 2026-10-21 --price-start 5600")
