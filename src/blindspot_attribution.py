"""
T13 A1 attribution: are the big-move days the engine is blind on / wrong on the scheduled data-print days?

Release dates come from ALFRED vintage dates (the date each number was first published), via fredapi
with FRED_API_KEY. Series: PAYEMS (Employment Situation), CPIAUCSL (CPI), ICSA (weekly claims),
GDP (BEA advance/second/third), PCEPI (PCE), RSAFS (retail sales). FOMC statement dates from
processed/fomc_decisions.csv.

Writes docs/blindspot_attribution.md:  state (A/B/C) x day-type (FOMC / data print / neither), per market.
"""
from __future__ import annotations
import json, os
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd

LAMBDA, BIG = 0.94, 2.0
ASSETS = ["SPY", "TLT", "GLD", "UUP", "USO"]
SERIES = {"PAYEMS": "NFP", "CPIAUCSL": "CPI", "ICSA": "claims", "GDP": "GDP", "PCEPI": "PCE", "RSAFS": "retail"}


def ewma_sigma(r): return np.sqrt(r.fillna(0).pow(2).ewm(alpha=1 - LAMBDA, adjust=False).mean().shift(1))


def dir_of(doc, a):
    d = doc.get("direction") or {}; v = d.get(a)
    if v is None: v = d.get({"SPY": "equity", "TLT": "duration", "GLD": "gold", "UUP": "dollar", "USO": "oil"}[a])
    return float(v or 0.0)


def release_dates() -> dict:
    from dotenv import load_dotenv; load_dotenv()
    from fredapi import Fred
    fred = Fred(api_key=os.environ["FRED_API_KEY"])
    out = {}
    cache = Path("processed/release_dates_alfred.json")
    if cache.exists() and all(k in json.loads(cache.read_text()) and json.loads(cache.read_text())[k] for k in SERIES.values()):
        return {k: set(pd.to_datetime(v)) for k, v in json.loads(cache.read_text()).items()}
    import time
    for sid, name in SERIES.items():
        vd = None
        for attempt, wait in enumerate((0, 3, 8, 15)):        # 8 Oct: NFP and CPI failed once on a URLError; retry before giving up
            time.sleep(wait)
            try:
                vd = fred.get_series_vintage_dates(sid); break
            except Exception as e:
                err = e
                try:                                            # second route: realtime_start of every observation = first publication
                    ar = fred.get_series_all_releases(sid); vd = sorted(set(pd.to_datetime(ar["realtime_start"]))); break
                except Exception as e2:
                    err = e2
        if vd is None:
            raise SystemExit(f"{name}: release dates unavailable after 4 attempts ({type(err).__name__}: {err}). "
                             "Refusing to write a table with a calendar missing -- rerun when FRED answers.")
        out[name] = sorted(set(pd.Timestamp(x).strftime("%Y-%m-%d") for x in vd))
        print(f"  {name:7} {len(out[name])} release dates {out[name][0]} -> {out[name][-1]}")
    # weekly claims vintages begin 2009-05; before that the release is every Thursday (holiday shifts ignored, marked 'rule')
    first_claims = pd.Timestamp(out["claims"][0]) if out.get("claims") else pd.Timestamp("2009-05-28")
    thursdays = pd.date_range("2006-01-05", first_claims - pd.Timedelta(days=1), freq="W-THU")
    out["claims"] = sorted(set(out["claims"]) | set(d.strftime("%Y-%m-%d") for d in thursdays))
    cache.write_text(json.dumps(out)); return {k: set(pd.to_datetime(v)) for k, v in out.items()}


def main():
    rets = pd.read_parquet("processed/asset_returns.parquet"); rets.index = pd.to_datetime(rets.index)
    z = {a: rets[a] / ewma_sigma(rets[a]) for a in ASSETS}
    rel = release_dates()
    fomc = set(pd.to_datetime(pd.read_csv("processed/fomc_decisions.csv").iloc[:, 0], errors="coerce").dropna())
    bf = sorted([d for d in Path("outputs/reports_backfill").glob("*/") if "altinstr" not in d.name], key=lambda p: p.stat().st_mtime)
    rep_dir = bf[-1]
    def day_type(d):
        if d in fomc: return "FOMC"
        hits = [n for n, s in rel.items() if d in s]
        return "print:" + "+".join(hits) if hits else "neither"
    L = ["# T13 A1 attribution — big-move days by state and day type", "",
         f"*Run {datetime.now():%Y-%m-%d %H:%M}. Release dates from ALFRED vintage dates ({', '.join(SERIES.values())}); FOMC from the decisions file; "
         f"reports from `{rep_dir.name}`. Big move = |z| > {BIG}. Document days only (the engine wrote a report).*", ""]
    allrows = []
    for a in ASSETS:
        rows = []
        for d, zz in z[a].items():
            if not np.isfinite(zz) or abs(zz) <= BIG: continue
            f = rep_dir / f"{d:%Y%m%d}.json"
            if not f.exists(): continue
            R = json.loads(f.read_text())
            docs = [x for x in R.get("documents", []) if abs(dir_of(x, a)) > 0.05]
            net = R["assets"][a].get("net_view")
            st = "A" if not docs else ("B" if (net is not None and np.sign(net) == -np.sign(zz)) else "C")
            rows.append(dict(asset=a, date=d, state=st, dtype=day_type(d).split(":")[0], detail=day_type(d), z=zz))
        allrows += rows
        df = pd.DataFrame(rows)
        if df.empty: continue
        tab = pd.crosstab(df["state"], df["dtype"]).reindex(index=["A", "B", "C"], columns=["FOMC", "print", "neither"], fill_value=0)
        L += [f"## {a} — {len(df)} big-move document days", "", "| state | FOMC day | data-print day | neither |", "|---|---|---|---|"]
        for stt, lab in (("A", "A blind"), ("B", "B wrong"), ("C", "C seen")):
            L.append(f"| {lab} | {tab.loc[stt, 'FOMC']} | {tab.loc[stt, 'print']} | {tab.loc[stt, 'neither']} |")
        L.append("")
    df = pd.DataFrame(allrows)
    share_print = (df["dtype"] == "print").mean(); share_fomc = (df["dtype"] == "FOMC").mean()
    b = df[df.state == "B"]
    L += ["## Reading", "",
          f"- Across all five markets, **{share_print:.0%}** of big-move document days are scheduled data-print days and **{share_fomc:.0%}** are FOMC days; "
          f"**{1 - share_print - share_fomc:.0%}** are neither (the move came from something outside both calendars).",
          f"- Of the **B (wrong)** days, {(b['dtype'] == 'print').mean():.0%} are print days — the document present was not the driver (misattribution, fixed by coverage), "
          f"{(b['dtype'] == 'FOMC').mean():.0%} are FOMC days — the reader scored the level, not the surprise (fixed by expectations), "
          f"and {(b['dtype'] == 'neither').mean():.0%} are neither (candidates for a genuine misread, or an uncovered driver).",
          "", "Print-day detail (which releases) is in the per-day table below for the B days.", "",
          "| asset | date | z | detail |", "|---|---|---|---|"]
    for _, r in b.sort_values("date").iterrows():
        L.append(f"| {r.asset} | {r.date:%Y-%m-%d} | {r.z:+.1f} | {r.detail} |")
    out = Path("docs/blindspot_attribution.md"); out.write_text("\n".join(L) + "\n"); print("\n".join(L[:60])); print(f"\n  -> {out}")


if __name__ == "__main__":
    main()
