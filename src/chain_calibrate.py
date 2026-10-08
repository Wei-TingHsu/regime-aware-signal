"""
Calibrate the oil-shock chain criterion against the two wars BEFORE it is used.

Founder's requirement (8 Oct): the rule must fire inside both the Ukraine (24 Feb 2022) and
Iran (28 Feb 2026) windows and not outside them. This script:
  1. prints the first 15 sessions of each war: oil z, 5-session DGS2 change, 5-session DXY change
  2. runs the registered rule (v0) and candidate rules v1-v3 over 2006-2026
  3. scores each: fires inside war windows (recall), alert runs outside (false alarms), with dates

It writes docs/chain_calibration.md. It changes nothing else. Run from the repo root.
"""
from __future__ import annotations
import os
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

LAMBDA = 0.94
WARS = {"Ukraine": ("2022-02-24", "2022-03-31"), "Iran": ("2026-02-28", "2026-03-31")}
PROC = Path("processed")


def ewma_sigma(r): return np.sqrt(r.fillna(0).pow(2).ewm(alpha=1 - LAMBDA, adjust=False).mean().shift(1))


def load_macro(idx):
    out = {}
    for key in ("DGS2", "DTWEXBGS", "DGS10", "T10Y2Y"):
        s = None
        try:
            from src.data_io import cached_fetch
            d = cached_fetch(source="fred", key=key, fetch_fn=lambda: (_ for _ in ()).throw(RuntimeError()), force_refresh=False)
            s = d.iloc[:, 0] if isinstance(d, pd.DataFrame) else d
        except Exception:
            try:
                from dotenv import load_dotenv; load_dotenv()
                from fredapi import Fred; s = Fred(api_key=os.environ["FRED_API_KEY"]).get_series(key)
            except Exception:
                s = None
        if s is not None:
            s = pd.to_numeric(s, errors="coerce"); s.index = pd.to_datetime(s.index); out[key] = s.reindex(idx).ffill()
    return out


def runs(mask: pd.Series):
    starts = mask & ~mask.shift(1, fill_value=False)
    return list(starts[starts].index)


def score(mask: pd.Series, name: str, L: list):
    rs = runs(mask)
    inside = {w: [d for d in rs if pd.Timestamp(a) <= d <= pd.Timestamp(b)] for w, (a, b) in WARS.items()}
    outside = [d for d in rs if not any(pd.Timestamp(a) <= d <= pd.Timestamp(b) for a, b in WARS.values())]
    L += [f"### {name}", "",
          f"- Ukraine window: {'**fires** on ' + ', '.join(d.strftime('%Y-%m-%d') for d in inside['Ukraine']) if inside['Ukraine'] else '**does not fire**'}",
          f"- Iran window: {'**fires** on ' + ', '.join(d.strftime('%Y-%m-%d') for d in inside['Iran']) if inside['Iran'] else '**does not fire**'}",
          f"- Alert runs outside both windows: **{len(outside)}** — " + (", ".join(d.strftime('%Y-%m-%d') for d in outside) if outside else "none"), ""]
    return bool(inside["Ukraine"]) and bool(inside["Iran"]), len(outside)


def main():
    rets = pd.read_parquet(PROC / "asset_returns.parquet"); rets.index = pd.to_datetime(rets.index)
    rets = rets.loc["2006-01-01":]
    z = {a: rets[a] / ewma_sigma(rets[a]) for a in ("USO", "GLD", "SPY", "TLT", "UUP")}
    m = load_macro(rets.index); dgs2, dxy = m["DGS2"], m["DTWEXBGS"]
    L = ["# Oil-shock chain — calibration against the two wars", "",
         f"*Run {datetime.now():%Y-%m-%d %H:%M}. Requirement: fire inside both war windows (first ~5 weeks), not outside. "
         "Rules are scored on 2006–2026; nothing here changes the registered rule until an amendment is written.*", ""]
    # 1. what the wars looked like
    for w, (a, b) in WARS.items():
        L += [f"## {w}: first 15 sessions from {a}", "", "| session | oil ret | oil z | 5-session oil | DGS2 5d (bp) | DXY 5d | gold ret | gold z |", "|---|---|---|---|---|---|---|---|"]
        seg = rets.loc[a:].index[:15]
        for d in seg:
            i = rets.index.get_loc(d)
            o5 = float(rets["USO"].iloc[max(0, i - 4):i + 1].sum()); d2 = float((dgs2.iloc[i] - dgs2.iloc[i - 5]) * 100); dx = float(dxy.iloc[i] / dxy.iloc[i - 5] - 1)
            L.append(f"| {d:%Y-%m-%d} | {rets['USO'].iloc[i]:+.2%} | {z['USO'].iloc[i]:+.1f} | {o5:+.1%} | {d2:+.0f} | {dx:+.2%} | {rets['GLD'].iloc[i]:+.2%} | {z['GLD'].iloc[i]:+.1f} |")
        L.append("")
    # 2. rules
    L += ["## Rules scored", ""]
    results = {}
    big_up = z["USO"] > 2
    # v0: registered rule — oil z>2 within 5 sessions AND DGS2 +10bp over 5 AND DXY up over 5
    v0 = big_up.rolling(5, min_periods=1).max().astype(bool) & ((dgs2 - dgs2.shift(5)) * 100 >= 10) & (dxy > dxy.shift(5))
    results["v0 (registered): oil z>2 in 5s & DGS2 ≥+10bp/5s & DXY up/5s"] = score(v0, "v0 (registered)", L)
    # v1: oil shock must be LARGE and SUSTAINED — 5-session oil return > +8% — plus DGS2 and DXY both up over 10 sessions
    o5 = rets["USO"].rolling(5).sum()
    v1 = (o5 > 0.08) & ((dgs2 - dgs2.shift(10)) * 100 >= 10) & (dxy > dxy.shift(10))
    results["v1: 5s oil > +8% & DGS2 ≥+10bp/10s & DXY up/10s"] = score(v1, "v1: sustained oil shock (+8% in 5 sessions), rates and dollar up over 10", L)
    # v2: v1 plus oil's level is at a 60-session high (a shock, not a bounce)
    hi60 = rets["USO"].cumsum(); at_high = hi60 >= hi60.rolling(60).max()
    v2 = v1 & at_high
    results["v2: v1 & oil at 60-session high"] = score(v2, "v2: v1 plus oil at a 60-session high", L)
    # v3: v2 plus gold NOT confirming as haven — gold 5s return < oil 5s return/4 (the haven leg fails)
    g5 = rets["GLD"].rolling(5).sum()
    v3 = v2 & (g5 < o5 / 4)
    results["v3: v2 & gold lagging oil (haven leg absent)"] = score(v3, "v3: v2 plus gold lagging oil by 4:1 (the haven leg is absent)", L)
    L += ["## Summary", "", "| rule | fires in both wars | false alarms outside | meets requirement |", "|---|---|---|---|"]
    for k, (both, fa) in results.items():
        L.append(f"| {k} | {'yes' if both else 'NO'} | {fa} | {'**yes**' if (both and fa == 0) else 'no'} |")
    L += ["", "A rule meets the requirement only with both wars inside and zero alert runs outside. If none does, the next candidates are "
          "listed by hand from the false-alarm dates above (what were they? 2008 oil spike, 2015 China devaluation, 2016 election, 2023 Hamas attack...) "
          "— each is either a legitimate oil→rates→dollar episode the founder wants flagged, or a reason to tighten."]
    out = Path("docs/chain_calibration.md"); out.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"\n  -> {out}")


if __name__ == "__main__":
    main()
