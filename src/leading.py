"""leading.py -- test LI-1 (registered in TRACK 3.118 before it runs): which market LEADS semiconductor shares, and in which market condition?

Founder, 25 Nov 2026: chip shares fell before the open on 24 and 25 Nov as the credit default swap spreads of the AI borrowers widened (Reuters, 24 Nov:
'AI credit default swap spreads widen on unease over cash flow'). He does not believe that spread is the leader: 'there should be other markets that
decide when to widen this spread'. Find that market and test whether it leads semiconductor shares, under the main page's market conditions.

What can be tested for free. The spreads of single AI borrowers (Oracle, CoreWeave) are sold data and are NOT in this test. Candidates for what moves first:
credit markets as a whole, the lenders, the funding market, volatility in bonds and shares, and the largest AI borrower's own share.
The test, for every candidate X, look-back L (1 or 5 sessions) and look-ahead H (1 or 5 sessions):
    does the change of X over the last L sessions tell the move of the semiconductor fund over the NEXT H sessions?
measured as the link (correlation) between the two, and compared with 5,000 copies in which X is slid along the calendar by a random distance of at least
60 sessions -- which keeps each series' own rhythm and breaks only the link in time. A candidate LEADS when its link is stronger than in all but a
share of the copies under the limit (0.05 divided by the number of tests). The same is measured the other way round (do chip shares lead X?), and
inside each of the main page's four market conditions.

    python -m src.leading fetch     # free: Yahoo and FRED (FRED_API_KEY) -> data_provenance/leading
    python -m src.leading run       # no download -> docs/leading_indicator.md
"""
from __future__ import annotations
import argparse, json, os
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path("data_provenance/leading"); DOCS = Path("docs"); TARGET = "SOXX"; LS, HS = [1, 5], [1, 5]; NSHIFT = 5000; MINSHIFT = 60; START = "2007-07-01"
YAHOO = {"HYG": "high-yield bond fund", "LQD": "investment-grade bond fund", "IEF": "7-10 year Treasury fund", "BKLN": "bank-loan fund", "BIZD": "private-credit lenders (BDC fund)", "KRE": "regional banks", "XLF": "financial shares",
         "^VIX": "share volatility (VIX)", "^MOVE": "bond volatility (MOVE)", "ORCL": "Oracle shares", "SPY": "S&P 500 fund", "SOXX": "semiconductor fund", "SMH": "semiconductor fund (second)", "QQQ": "Nasdaq-100 fund"}
FRED = {"BAMLH0A0HYM2": "high-yield credit spread", "BAMLC0A0CM": "investment-grade credit spread", "BAMLH0A3HYC": "CCC credit spread", "BAMLC0A4CBBB": "BBB credit spread", "SOFR": "overnight funding rate (SOFR)", "IORB": "rate the Fed pays on reserves", "DGS10": "10-year yield", "DGS2": "2-year yield"}
# candidate -> (how it is built, what a RISE of it means). 'lag' = sessions until the day's value is public (FRED series appear the next morning).
CANDS = {
    "high-yield bonds against Treasuries (HYG / IEF)": dict(kind="ratio", a="HYG", b="IEF", lag=0, rise="credit calmer"),
    "investment-grade bonds against Treasuries (LQD / IEF)": dict(kind="ratio", a="LQD", b="IEF", lag=0, rise="credit calmer"),
    "bank loans (BKLN)": dict(kind="price", a="BKLN", lag=0, rise="credit calmer"),
    "private-credit lenders against the market (BIZD / SPY)": dict(kind="ratio", a="BIZD", b="SPY", lag=0, rise="lenders stronger"),
    "regional banks against the market (KRE / SPY)": dict(kind="ratio", a="KRE", b="SPY", lag=0, rise="banks stronger"),
    "share volatility (VIX)": dict(kind="price", a="^VIX", lag=0, rise="more fear"),
    "bond volatility (MOVE)": dict(kind="price", a="^MOVE", lag=0, rise="more fear in bonds"),
    "Oracle against the market (ORCL / SPY)": dict(kind="ratio", a="ORCL", b="SPY", lag=0, rise="the largest AI borrower stronger"),
    "high-yield credit spread (FRED)": dict(kind="level", a="BAMLH0A0HYM2", lag=1, rise="credit tighter"),
    "investment-grade credit spread (FRED)": dict(kind="level", a="BAMLC0A0CM", lag=1, rise="credit tighter"),
    "CCC credit spread (FRED)": dict(kind="level", a="BAMLH0A3HYC", lag=1, rise="weakest borrowers tighter"),
    "BBB credit spread (FRED)": dict(kind="level", a="BAMLC0A4CBBB", lag=1, rise="credit tighter"),
    "funding stress (SOFR minus the rate on reserves)": dict(kind="diff", a="SOFR", b="IORB", lag=1, rise="cash dearer"),
    "10-year minus 2-year yield": dict(kind="diff", a="DGS10", b="DGS2", lag=1, rise="curve steeper"),
}


def cmd_fetch():
    import yfinance as yf
    ROOT.mkdir(parents=True, exist_ok=True); bad = []
    D = yf.download(list(YAHOO), start="2005-01-01", interval="1d", auto_adjust=True, progress=False, group_by="ticker", threads=True)
    for t in YAHOO:
        try:
            x = D[t]["Close"].dropna(); x.index = pd.DatetimeIndex(x.index).tz_localize(None)
            if len(x) < 250: bad.append(t); continue
            x.to_frame("value").to_parquet(ROOT / f"y_{t.replace('^', '_')}.parquet")
        except Exception: bad.append(t)
    print(f"  Yahoo: {len(YAHOO) - len(bad)} of {len(YAHOO)} series; without data: {bad or 'none'}")
    if not os.environ.get("FRED_API_KEY"): print("  FRED_API_KEY is not set: the FRED candidates are left out"); return
    from fredapi import Fred
    fr = Fred(api_key=os.environ["FRED_API_KEY"]); badf = []
    for k in FRED:
        try: x = fr.get_series(k).dropna(); x.index = pd.to_datetime(x.index); x.to_frame("value").to_parquet(ROOT / f"f_{k}.parquet")
        except Exception: badf.append(k)
    print(f"  FRED: {len(FRED) - len(badf)} of {len(FRED)} series; failed: {badf or 'none'}. No cost. -> {ROOT}")


def _series(k):
    f = ROOT / (f"y_{k.replace('^', '_')}.parquet" if k in YAHOO else f"f_{k}.parquet"); return pd.read_parquet(f)["value"] if f.exists() else None


def _conditions(idx):
    """the main page's four market conditions, by the same call app.py makes (as in src/selloff_forward.py)"""
    try:
        import asset_extension as AE
        cfg = AE.load_config(); sc, _ = AE.load_data(); lab = pd.Series(np.asarray(AE.regime_labels_expanding(sc, cfg)), index=pd.DatetimeIndex(sc.index)); lab = lab[~lab.index.duplicated()].sort_index()
        prof = json.loads(Path("processed/regime_profile.json").read_text()).get("regimes", {}); names = {int(k): v.get("label", f"condition {int(k) + 1}") for k, v in prof.items()}
        return lab.reindex(lab.index.union(idx)).ffill().reindex(idx), names
    except Exception as e: print(f"  (the main page's market conditions could not be loaded: {type(e).__name__}: {str(e)[:100]})"); return None, {}


def _link(x, y, rng, n_shift):
    """correlation of x (known today) with y (what follows), and the share of calendar-slid copies of x with a link at least as strong"""
    ok = np.isfinite(x) & np.isfinite(y)
    if ok.sum() < 250: return np.nan, np.nan, int(ok.sum())
    xs = np.where(ok, x, np.nan); c = np.corrcoef(x[ok], y[ok])[0, 1]; n = len(x); hits = 0; done = 0
    for _ in range(n_shift):
        z = np.roll(xs, int(rng.integers(MINSHIFT, n - MINSHIFT))); k = np.isfinite(z) & np.isfinite(y)
        if k.sum() < 200: continue
        done += 1; hits += abs(np.corrcoef(z[k], y[k])[0, 1]) >= abs(c)
    return float(c), float((hits + 1) / (done + 1)), int(ok.sum())


def cmd_run(n_shift=NSHIFT):
    tgt = _series(TARGET); spy = _series("SPY")
    if tgt is None or spy is None: raise SystemExit("run `python -m src.leading fetch` first")
    idx = tgt.loc[START:].index; lt = np.log(tgt.reindex(idx)); ls = np.log(spy.reindex(idx)); rng = np.random.default_rng(20261125); rows = []; cond, names = _conditions(idx)
    X = {}
    for name, c in CANDS.items():
        a = _series(c["a"]); b = _series(c.get("b")) if c.get("b") else None
        if a is None or (c.get("b") and b is None): continue
        a = a.reindex(idx).ffill(limit=3); v = np.log(a) if c["kind"] == "price" else np.log(a) - np.log(b.reindex(idx).ffill(limit=3)) if c["kind"] == "ratio" else a if c["kind"] == "level" else a - b.reindex(idx).ffill(limit=3)
        X[name] = v.shift(c["lag"])      # only what was public by the close of the day
    tests = len(X) * len(LS) * len(HS); bar = 0.05 / max(1, tests)
    for name, v in X.items():
        for L in LS:
            dx = (v - v.shift(L)).to_numpy(float)
            for H in HS:
                fy = (lt.shift(-H) - lt).to_numpy(float); fyr = fy - (ls.shift(-H) - ls).to_numpy(float); c, p, n = _link(dx, fy, rng, n_shift); c2, p2, _ = _link(dx, fyr, rng, n_shift)
                back = (lt - lt.shift(L)).to_numpy(float); fx = (v.shift(-H) - v).to_numpy(float); cb, pb, _ = _link(back, fx, rng, max(500, n_shift // 5))      # the other way round: do chip shares lead the candidate?
                row = dict(candidate=name, rise=CANDS[name]["rise"], L=L, H=H, n=n, link=c, p=p, link_vs_spx=c2, p_vs_spx=p2, reverse_link=cb, reverse_p=pb, leads=bool(p == p and p < bar))
                if cond is not None:
                    for k, nm in names.items():
                        m = (cond == k).to_numpy(); ck, pk, nk = _link(np.where(m, dx, np.nan), fy, rng, max(500, n_shift // 5)); row[f"cond::{nm}"] = (ck, pk, nk)
                rows.append(row)
    R = pd.DataFrame(rows); f3 = lambda x: "n/a" if x != x else f"{x:+.3f}"; f4 = lambda x: "n/a" if x != x else f"{x:.4f}"
    L_ = ["# Test LI-1: which market leads semiconductor shares, and in which market condition?", "", f"Registered in TRACK 3.118 before running. Target: the semiconductor fund {TARGET}, {idx[0]:%Y} to {idx[-1]:%Y-%m-%d}. For each candidate: the link between its change over the last L sessions and the fund's move over the NEXT H sessions. "
          f"'Link' is a correlation: 0 = no link, +1 or -1 = a perfect one; the sign says whether the fund follows a rise of the candidate upward (+) or downward (-). 'Chance' = the share of {n_shift:,} copies, with the candidate slid along the calendar, that show a link at least as strong. "
          f"**LEADS** = chance under {bar:.5f} (0.05 / {tests} tests). 'The other way round' = the fund's move over the last L sessions against the candidate's change over the next H: do chip shares lead it? Single AI borrowers' credit default swap spreads are sold data and are not here.", "",
          "| candidate (what a rise means) | look-back L | look-ahead H | link (chance) | link with the fund measured against the S&P 500 (chance) | the other way round: chip shares first (chance) | days | verdict |", "|---|---|---|---|---|---|---|---|"]
    for r in R.sort_values("p").itertuples():
        L_.append(f"| {r.candidate} ({r.rise}) | {r.L} | {r.H} | {f3(r.link)} ({f4(r.p)}) | {f3(r.link_vs_spx)} ({f4(r.p_vs_spx)}) | {f3(r.reverse_link)} ({f4(r.reverse_p)}) | {r.n} | {'**LEADS**' if r.leads else 'no'} |")
    lead = R[R.leads]; L_ += ["", f"**{lead.candidate.nunique()} of {R.candidate.nunique()} candidates lead in at least one of the four (L, H) pairs; {len(lead)} of {len(R)} tests are under the limit.**"]
    if cond is not None and len(R):
        cc = [c for c in R.columns if c.startswith("cond::")]; L_ += ["", "## By the main page's market condition", "", "The same link inside each condition (days of that condition only), for the strongest (L, H) pair of each candidate. Fewer days, so chance is counted on fewer copies; read the SIZE of the link across conditions.", "",
              "| candidate | L, H | all days | " + " | ".join(c.split("::")[1] for c in cc) + " | strongest in |", "|---|---|---|" + "---|" * (len(cc) + 1)]
        for name, g in R.groupby("candidate", sort=False):
            r = g.sort_values("p").iloc[0]; vals = {c.split("::")[1]: r[c] for c in cc}; best = max(vals, key=lambda k: abs(vals[k][0]) if vals[k][0] == vals[k][0] else -1)
            L_.append(f"| {name} | {r.L}, {r.H} | {f3(r.link)} ({f4(r.p)}) | " + " | ".join(f"{f3(v[0])} ({f4(v[1])}; {v[2]} days)" for v in vals.values()) + f" | {best} |")
    L_ += ["", "How to read a 'LEADS': it says the link is too strong to be chance, not that it is large. A link of 0.05 explains a quarter of one per cent of the fund's moves. Whether it can be traded is a separate test (entry at the next open, the real cost)."]
    DOCS.mkdir(exist_ok=True); (DOCS / "leading_indicator.md").write_text("\n".join(L_) + "\n"); R.drop(columns=[c for c in R.columns if c.startswith("cond::")]).to_csv(DOCS / "leading_indicator.csv", index=False)
    print(f"{R.candidate.nunique()} candidates x {len(LS)} look-backs x {len(HS)} look-aheads = {len(R)} tests; limit: chance under {bar:.5f}; {n_shift:,} calendar-slid copies each")
    print("  link (chance) | against the S&P 500 | the other way round (chip shares first) | L | H | verdict | candidate")
    for r in R.sort_values("p").head(20).itertuples(): print(f"  {f3(r.link)} ({f4(r.p)}) | {f3(r.link_vs_spx)} ({f4(r.p_vs_spx)}) | {f3(r.reverse_link)} ({f4(r.reverse_p)}) | {r.L} | {r.H} | {'LEADS' if r.leads else 'no   '} | {r.candidate} ({r.rise})")
    print(f"=> {lead.candidate.nunique()} of {R.candidate.nunique()} candidates lead in at least one pair. -> docs/leading_indicator.md")
    if cond is not None: print("\n".join(L_[L_.index("## By the main page's market condition") + 4:-2]))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["fetch", "run"]); ap.add_argument("--shifts", type=int, default=NSHIFT); a = ap.parse_args(); cmd_fetch() if a.cmd == "fetch" else cmd_run(a.shifts)
