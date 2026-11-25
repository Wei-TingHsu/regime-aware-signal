"""trend_finder.py -- step 1 of the addition and subtraction pool (docs/POOL_PLAN.md, points 1-3): find the fast trends a person sees on the daily chart,
WITHOUT choosing a length, and draw them so the founder can mark which ones his eye agrees with.

The rule (Part 2 of the plan, Claude's proposal). For every stretch of 5 to 60 sessions ending on a day:
    strength = (change of the price over the stretch, in log terms) / (the stock's usual daily move x the square root of the number of sessions)
'Usual daily move' = the spread of its daily moves over the 250 sessions BEFORE the stretch begins. The square root is how far a price drifts by chance in
that many sessions, so the strength says how many 'chance drifts' the move is -- a 9-session move and a 40-session move are judged on the same scale.
A day belongs to a trend when it lies inside any stretch whose strength is beyond the cut. Days that belong together form one trend; it is then drawn from
its lowest to its highest price (an uptrend) or highest to lowest (a downtrend), as the eye would.
Three cuts are drawn at once (1.6 weak, 2.0 middle, 2.6 strong): the founder's marks decide which one is 'what the eye sees'. Nothing here uses news.

    python -m src.trend_finder run     # free, no download -> docs/trends/*.png, docs/trends/index.md, docs/trends/trends.csv
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np, pandas as pd

POOL = ["AAPL", "AMD", "AMZN", "AVGO", "CRWD", "CSCO", "EMR", "GE", "GOOG", "IBM", "INTC", "META", "MSFT", "MU", "NVDA", "ORCL", "QCOM", "SNDK", "TSM", "TXN"]      # the 20 companies with profiles (founder, 24 Nov)
OUT = Path("docs/trends"); NMIN, NMAX, USUAL = 5, 60, 250; CUTS = {"weak": 1.6, "middle": 2.0, "strong": 2.6}; SHOW = 620; TURN = 3.0
EXAMPLES = [("NVDA", "2026-10-06", "2026-11-20", "down"), ("AMD", "2026-04-04", "2026-05-11", "up")]      # the founder's two examples (docs/POOL_PLAN.md, point 1)


def _prices(t: str):
    for root in ("data_provenance/selloff_live/prices", "data_provenance/selloff/prices"):
        f = Path(root) / f"{t}.parquet"
        if f.exists(): return pd.read_parquet(f)
    return None


def find(d: pd.DataFrame) -> tuple[list, pd.DataFrame]:
    c = d.close.astype(float); lp = np.log(c.to_numpy()); r = np.diff(lp, prepend=np.nan); n_all = len(lp); usual = pd.Series(r).rolling(USUAL, min_periods=120).std().to_numpy()
    up = np.zeros(n_all); dn = np.zeros(n_all); seen_up = np.zeros(n_all); seen_dn = np.zeros(n_all)      # the largest strength of any stretch that covers the day / that ENDS on the day
    for n in range(NMIN, NMAX + 1):
        z = np.full(n_all, np.nan); z[n:] = (lp[n:] - lp[:-n]) / (usual[:-n] * np.sqrt(n))      # usual move as known when the stretch began
        for t in np.flatnonzero(np.isfinite(z)):
            if z[t] > 0: up[t - n + 1:t + 1] = np.maximum(up[t - n + 1:t + 1], z[t]); seen_up[t] = max(seen_up[t], z[t])
            else: dn[t - n + 1:t + 1] = np.maximum(dn[t - n + 1:t + 1], -z[t]); seen_dn[t] = max(seen_dn[t], -z[t])
    out = []; lo = CUTS["weak"]
    for sign, cover, seen in ((1, up, seen_up), (-1, dn, seen_dn)):
        on = cover >= lo; i = 0
        while i < n_all:
            if not on[i]: i += 1; continue
            j = i
            while j + 1 < n_all and on[j + 1]: j += 1
            a = max(0, i - 1); seg = lp[a:j + 1]      # the day before the first covered day is where the first stretch started
            if sign > 0: s = a + int(np.argmin(seg)); e = s + int(np.argmax(lp[s:j + 1]))
            else: s = a + int(np.argmax(seg)); e = s + int(np.argmin(lp[s:j + 1]))
            if e - s >= 3:
                peak = float(cover[i:j + 1].max()); first = next((k for k in range(s, j + 1) if seen[k] >= lo), None); path = float(np.nansum(np.abs(r[s + 1:e + 1])))
                out.append(dict(side="up" if sign > 0 else "down", start=d.index[s], end=d.index[e], sessions=int(e - s), move_pct=float((np.exp(lp[e] - lp[s]) - 1) * 100), strength=peak, tier="strong" if peak >= CUTS["strong"] else "middle" if peak >= CUTS["middle"] else "weak",
                                first_seen=d.index[first] if first is not None else pd.NaT, straight=float(abs(lp[e] - lp[s]) / path) if path > 0 else np.nan, i0=s, i1=e))
            i = j + 1
    out.sort(key=lambda x: x["start"])
    # turning points: a crest or trough is confirmed when the price has come back by TURN usual daily moves
    turns = []; direction = 0; hi = lo = None
    for k in range(n_all):
        u = usual[k]
        if not np.isfinite(u): continue
        if hi is None: hi = lo = k; continue
        thr = TURN * u
        if direction >= 0:      # rising (or not yet known): the highest point so far is a crest once the price is TURN usual moves below it
            if lp[k] > lp[hi]: hi = k
            elif lp[hi] - lp[k] >= thr: turns.append((hi, "crest")); direction = -1; lo = k; continue
        if direction <= 0:
            if lp[k] < lp[lo]: lo = k
            elif lp[k] - lp[lo] >= thr: turns.append((lo, "trough")); direction = 1; hi = k
    T = pd.DataFrame([dict(day=d.index[k], kind=kind, price=float(c.iloc[k])) for k, kind in turns])
    return out, T


def _chart(t, d, trends, T, f):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    x = d.iloc[-SHOW:]; fig, ax = plt.subplots(figsize=(15, 4.6), dpi=110); ax.plot(x.index, x.close, color="#14171F", lw=1.1); shade = {"weak": 0.10, "middle": 0.22, "strong": 0.36}; k = 0
    for tr in trends:
        if tr["end"] < x.index[0]: continue
        k += 1; tr["no"] = k; col = "#178A4C" if tr["side"] == "up" else "#C0392B"; a, b = max(tr["start"], x.index[0]), tr["end"]; ax.axvspan(a, b, color=col, alpha=shade[tr["tier"]], lw=0)
        y = float(x.close.loc[a:b].max()) if tr["side"] == "up" else float(x.close.loc[a:b].min()); ax.annotate(f"{k}", (a + (b - a) / 2, y), textcoords="offset points", xytext=(0, 7 if tr["side"] == "up" else -13), ha="center", fontsize=9, color=col, fontweight="bold")
    if len(T):
        tt = T[T.day >= x.index[0]]; ax.scatter(tt.day, tt.price, s=9, color="#5F6672", zorder=3)
    ax.set_title(f"{t}: fast trends found without a fixed length (light = weak, 1.6; medium = 2.0; dark = strong, 2.6). Green up, red down. Dots: crests and troughs.", fontsize=10, loc="left"); ax.grid(alpha=0.25); ax.margins(x=0.01); fig.tight_layout(); fig.savefig(f); plt.close(fig)


def cmd_run(tickers=None):
    OUT.mkdir(parents=True, exist_ok=True); rows = []; L = ["# Fast trends found without a fixed length: for the founder to mark", "", "Step 1 of the addition and subtraction pool (`docs/POOL_PLAN.md`). No news is used here. For each stock: the chart of about the last two and a half years, each trend with a number, and the list under it. "
         "**To mark: say which numbers your eye does NOT accept as a trend, and where a trend you see is missing** (for example 'NVDA: 3 no; missing an uptrend in March'). 'Strength' = the move divided by how far the price drifts by chance in that many sessions; 'straightness' = the net move divided by the sum of all daily moves (1 = a straight line). "
         "'First seen' = the first day on which the trend could have been recognised with the prices known that day.", ""]; missing = []
    for t in (tickers or POOL):
        d = _prices(t)
        if d is None or len(d) < 400: missing.append(t); continue
        trends, T = find(d); _chart(t, d, trends, T, OUT / f"{t}.png"); shown = [tr for tr in trends if "no" in tr]
        L += [f"## {t}", "", f"![{t}]({t}.png)", "", "| no. | direction | from | to | sessions | move | strength (tier) | straightness | first seen |", "|---|---|---|---|---|---|---|---|---|"]
        for tr in shown:
            L.append(f"| {tr['no']} | {tr['side']} | {tr['start']:%Y-%m-%d} | {tr['end']:%Y-%m-%d} | {tr['sessions']} | {tr['move_pct']:+.0f}% | {tr['strength']:.1f} ({tr['tier']}) | {tr['straight']:.2f} | {'' if pd.isna(tr['first_seen']) else format(tr['first_seen'], '%Y-%m-%d')} |")
            rows.append(dict(ticker=t, no=tr["no"], side=tr["side"], start=f"{tr['start']:%Y-%m-%d}", end=f"{tr['end']:%Y-%m-%d}", sessions=tr["sessions"], move_pct=round(tr["move_pct"], 1), strength=round(tr["strength"], 2), tier=tr["tier"], straightness=round(tr["straight"], 2), first_seen="" if pd.isna(tr["first_seen"]) else f"{tr['first_seen']:%Y-%m-%d}", founder_mark=""))
        L.append("")
        n = {k: sum(tr["tier"] == k for tr in shown) for k in CUTS}; print(f"  {t}: {len(shown)} trends on the chart (strong {n['strong']}, middle {n['middle']}, weak {n['weak']}); last price day {d.index[-1]:%Y-%m-%d}")
    R = pd.DataFrame(rows); R.to_csv(OUT / "trends.csv", index=False)
    # the founder's two examples: are they found, and where does the rule put their ends?
    L += ["## The founder's two examples", ""]
    for t, a, b, side in EXAMPLES:
        g = R[(R.ticker == t) & (R.side == side) & (R.start <= b) & (R.end >= a)] if len(R) else R
        if len(g): x = g.sort_values("strength", ascending=False).iloc[0]; msg = f"{t} {side} {a} to {b}: FOUND as trend {x.no} -- {x.start} to {x['end']}, {x.sessions} sessions, {x.move_pct:+.0f}%, strength {x.strength} ({x.tier}), first seen {x.first_seen}" + (f"; {len(g) - 1} more trend(s) overlap the same dates" if len(g) > 1 else "")
        else: msg = f"{t} {side} {a} to {b}: NOT found at any cut" + ("" if t in (tickers or POOL) and t not in missing else " (no prices for this stock)")
        L.append("- " + msg); print("  example: " + msg)
    if missing: L += ["", f"No prices on disk for: {', '.join(missing)}."]; print(f"  no prices for: {missing}")
    (OUT / "index.md").write_text("\n".join(L) + "\n"); print(f"{len(R)} trends drawn for {R.ticker.nunique() if len(R) else 0} stocks -> docs/trends/index.md (the charts are the .png files beside it), docs/trends/trends.csv")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run"]); ap.add_argument("--tickers", default=None); a = ap.parse_args(); cmd_run(a.tickers.split(",") if a.tickers else None)
