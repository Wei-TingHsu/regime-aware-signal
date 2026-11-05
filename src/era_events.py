"""era_events.py -- event tables by era from the event files already on disk (prereg_subperiod_audit.md, group B, item B7).

  python -m src.era_events oil        # processed/oil_shocks.csv (T13 A3a: the path after an oil shock) by era and by pool: n, median
                                      # and share-positive of f5..f90 per asset; rows with n < 30 are measured, not judged
Output docs/era_events_oil.md (+ .json). Nothing here writes the register.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROC, DOCS = Path("processed"), Path("docs")
ERAS = [("1995-03", "1995-01-01", "2003-12-31"), ("2004-08", "2004-01-01", "2008-12-31"), ("2009-14", "2009-01-01", "2014-12-31"),
        ("2015-19", "2015-01-01", "2019-12-31"), ("2020-21", "2020-01-01", "2021-12-31"), ("2022-26", "2022-01-01", "2026-12-31")]
HORIZONS = ["f5", "f10", "f20", "f40", "f60", "f90"]


def era_of(d) -> str:
    for name, a, b in ERAS:
        if pd.Timestamp(a) <= d <= pd.Timestamp(b): return name
    return "other"


def cmd_oil():
    df = pd.read_csv(PROC / "oil_shocks.csv"); df["date"] = pd.to_datetime(df["date"]); df["era"] = df["date"].map(era_of)
    hz = [h for h in HORIZONS if h in df.columns]
    rows = []
    for (pool, asset, era), g in df.groupby(["pool", "asset", "era"]):
        row = dict(pool=pool, asset=asset, era=era, n=len(g))
        for h in hz:
            v = g[h].dropna(); row[f"{h}_med"] = float(v.median()) if len(v) else np.nan; row[f"{h}_pos"] = float((v > 0).mean()) if len(v) else np.nan
        rows.append(row)
    for (pool, asset), g in df.groupby(["pool", "asset"]):
        row = dict(pool=pool, asset=asset, era="all", n=len(g))
        for h in hz:
            v = g[h].dropna(); row[f"{h}_med"] = float(v.median()) if len(v) else np.nan; row[f"{h}_pos"] = float((v > 0).mean()) if len(v) else np.nan
        rows.append(row)
    tab = pd.DataFrame(rows).sort_values(["pool", "asset", "era"])
    out = DOCS / "era_events_oil.md"
    L = ["# Oil shocks by era (T13 A3a, processed/oil_shocks.csv)", "", "Median forward return and share positive after each shock, by pool, asset and era. n < 30: measured, not a verdict.", ""]
    for pool, gp in tab.groupby("pool"):
        L += [f"## pool {pool}", "", "| asset | era | n | " + " | ".join(f"{h} med / pos" for h in hz) + " |", "|---|---|---|" + "---|" * len(hz)]
        for _, r_ in gp.iterrows():
            L.append(f"| {r_['asset']} | {r_['era']} | {r_['n']} | " + " | ".join((f"{r_[f'{h}_med'] * 100:+.1f}% / {r_[f'{h}_pos']:.0%}" if np.isfinite(r_[f'{h}_med']) else "·") for h in hz) + " |")
        L.append("")
    out.write_text("\n".join(L) + "\n"); out.with_suffix(".json").write_text(json.dumps(json.loads(tab.to_json(orient="records")), indent=1))
    print(tab[tab.asset.isin(["GLD", "SPY"])][["pool", "asset", "era", "n"] + [f"{h}_med" for h in hz[:3]]].to_string(index=False)); print(f"-> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["oil"]); a = ap.parse_args()
    DOCS.mkdir(exist_ok=True)
    if a.cmd == "oil": cmd_oil()
