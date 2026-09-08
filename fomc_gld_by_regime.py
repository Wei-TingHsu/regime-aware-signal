"""
fomc_gld_by_regime.py -- where did the FOMC->GLD effect live?  DESCRIPTIVE ONLY.

WHAT THIS IS NOT
    Not a test. No p-value is computed and none may be quoted from it. The
    FOMC->GLD cell met its criterion pooled, then FAILED its temporal split at
    4.62x on 2026-08-28 and is retired. Splitting the same 131 events four ways
    by regime and reporting which quarter looks best is the garden of forking
    paths: with ~33 events per regime, one of four will look good by chance.

    What this file does is GENERATE A HYPOTHESIS for forward registration:
    "FOMC->GLD works in condition X." That hypothesis is then tested only on
    FOMC meetings that have not yet happened -- there is no held-out data,
    every one of the 131 was used. At eight meetings a year, a verdict is
    roughly two years away. The registration is free and it compounds either
    way.

WHAT IT REPRODUCES
    macro_event_test.py's NEXT_h window: close(N+h)/close(N)-1 from the close
    of the decision day, h in {2, 3}. Uses the project's own GLD returns rather
    than a fresh yfinance pull, so the numbers match fomc_gld_split_cost.py.

Run:  python fomc_gld_by_regime.py
"""
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from src.analog_event import load_data, regime_labels_expanding
from src.data_io import load_config, PROCESSED_DIR

REPO = PROCESSED_DIR.parent
OUT = REPO / "docs" / "fomc_gld_by_regime.md"
DATES = PROCESSED_DIR / "fomc_decisions.csv"
HS = (2, 3)


def main():
    cfg = load_config()
    scores, rets = load_data()
    idx = pd.DatetimeIndex(scores.index)
    lab = pd.Series(regime_labels_expanding(scores, cfg), index=idx)
    prof = {}
    p = PROCESSED_DIR / "regime_profile.json"
    if p.exists():
        import json
        prof = {int(k): v["label"] for k, v in
                json.loads(p.read_text())["regimes"].items()}

    dts = pd.read_csv(DATES)
    col = next(c for c in dts.columns if "date" in c.lower())
    ev = pd.DatetimeIndex(pd.to_datetime(dts[col])).sort_values()

    close = (1 + rets["GLD"].fillna(0)).cumprod().values
    rows = []
    for d in ev:
        hit = idx[idx >= d]
        if not len(hit) or (hit[0] - d) > pd.Timedelta("5D"):
            continue
        i = idx.get_loc(hit[0])
        if i < 252 or i + max(HS) >= len(idx) or lab.iloc[i] < 0:
            continue
        r = dict(date=hit[0].date(), regime=int(lab.iloc[i]),
                 half="EARLY" if hit[0] < pd.Timestamp("2019-03-20") else "LATE")
        for h in HS:
            r[f"next_{h}"] = close[i + h] / close[i] - 1
        rows.append(r)
    df = pd.DataFrame(rows)

    print("=" * 74)
    print("FOMC -> GLD by regime.  DESCRIPTIVE. No test. No p-value.")
    print("=" * 74)
    print(f"  {len(df)} events, {df.date.min()} -> {df.date.max()}")
    print(f"  pooled: h=2 {df.next_2.mean()*100:+.3f}%   h=3 "
          f"{df.next_3.mean()*100:+.3f}%   (retired at split ratio 4.62x)\n")

    print(f"  {'regime':<8}{'label':<44}{'n':>4}  {'h=2':>8}  {'h=3':>8}")
    for r, g in df.groupby("regime"):
        print(f"  {r:<8}{prof.get(r, ''):<44}{len(g):>4}  "
              f"{g.next_2.mean()*100:+7.3f}%  {g.next_3.mean()*100:+7.3f}%")

    print(f"\n  by regime x half -- shows whether 'regime' and 'time' are the "
          f"same thing here:")
    ct = df.groupby(["regime", "half"]).size().unstack(fill_value=0)
    print(ct.to_string())

    print("\n  READING")
    print("  If one regime carries the effect AND that regime is almost entirely")
    print("  EARLY, then 'works in regime X' and 'worked before 2019' are the same")
    print("  claim, and the split already rejected it. If a regime carries the")
    print("  effect across BOTH halves, that is a hypothesis worth registering")
    print("  forward. Either way nothing here is evidence -- it was found by")
    print("  looking, not by testing.")

    ts = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %z")
    L = ["# FOMC → GLD by regime — descriptive, not a test", "", f"*{ts}.*", "",
         "**No p-value is reported and none may be quoted.** The cell is "
         "retired (split FAIL 4.62×). Splitting 131 events four ways and "
         "picking the best quarter is the garden of forking paths. This table "
         "generates a hypothesis for *forward* registration only.", "",
         "| regime | label | n | h=2 | h=3 |", "|---|---|---|---|---|"]
    for r, g in df.groupby("regime"):
        L.append(f"| {r} | {prof.get(r, '')} | {len(g)} | "
                 f"{g.next_2.mean()*100:+.3f}% | {g.next_3.mean()*100:+.3f}% |")
    L += ["", "Regime × half:", "", "```", ct.to_string(), "```", ""]
    OUT.write_text("\n".join(L) + "\n")
    print(f"\n  -> {OUT}")


if __name__ == "__main__":
    main()
