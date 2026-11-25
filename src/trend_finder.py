"""trend_finder.py -- step 1 of the addition and subtraction pool (docs/POOL_PLAN.md, points 1-3): find the trends a person sees on the daily chart,
WITHOUT choosing a length, and draw them so the founder can mark them.

THIRD VERSION (25 Nov 2026), built from the founder's marks on AAPL, AMD, NVDA, SNDK, TSM (TRACK 3.115). What the marks say: his eye reads the chart as
SWINGS between major crests and troughs. Every swing is a trend, fast or slow, short or long (5 sessions or 170); a small move against the swing is not
a trend of its own, it belongs to the swing; a trend starts at a trough and ends at a crest (or the reverse). The first version looked for 'unusually
strong stretches', so it missed the slower swings and counted small counter-moves.

The rule now. Walk through the days. The highest price since the last trough is a CREST as soon as the price has fallen back from it by K times the
stock's usual daily move (the spread of its daily moves over the last 250 sessions); the same, mirrored, for a TROUGH. A trend is the swing from one
turn to the next. K is the only number. It is not chosen by Claude: the run tries K = 4 to 10 and takes the one that reproduces most of the founder's marks.
For each swing the 'strength' of the old rule is still shown (the move divided by how far the price drifts by chance in that many sessions): it says
whether the swing is fast or slow. 'First seen' = the day the swing could have been recognised with the prices known that day (the day its starting
turn was confirmed).

    python -m src.trend_finder run     # free, no download -> docs/trends/*.png, docs/trends/index.md, docs/trends/trends.csv
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np, pandas as pd

POOL = ["AAPL", "AMD", "AMZN", "AVGO", "CRWD", "CSCO", "EMR", "GE", "GOOG", "IBM", "INTC", "META", "MSFT", "MU", "NVDA", "ORCL", "QCOM", "SNDK", "TSM", "TXN"]      # the 20 companies with profiles (founder, 24 Nov)
OUT = Path("docs/trends"); USUAL = 250; KS = [4, 5, 6, 7, 8, 9, 10]; SHOW = 620; FAST = {"slow": 0.0, "medium": 1.6, "fast": 2.6}; TOL = 9
# The founder's marks of 25 Nov on the first charts, as swings that must exist: (stock, direction, start, end or None). Dates are those of the first version's table; a swing counts as found within 9 calendar days at each end.
MARKS = [("AAPL", "down", "2025-10-29", "2026-01-20"), ("AAPL", "down", "2026-02-06", "2026-03-30"), ("AAPL", "up", "2026-08-12", "2026-11-13"), ("AAPL", "down", "2026-07-28", "2026-08-12"), ("AAPL", "down", "2024-12-26", "2025-04-08"),
         ("NVDA", "down", "2026-10-06", "2026-11-20"), ("NVDA", "up", "2026-03-30", "2026-05-14"), ("NVDA", "down", "2025-10-29", None),
         ("TSM", "down", "2024-10-17", "2024-11-27"), ("TSM", "up", "2024-11-27", "2025-01-23"), ("TSM", "up", "2026-03-30", "2026-06-30"), ("TSM", "down", "2025-01-23", "2025-04-08"), ("TSM", "down", "2026-10-05", "2026-11-20"),
         ("AMD", "up", "2026-03-03", "2026-06-30"), ("AMD", "down", "2026-01-23", "2026-03-03"), ("AMD", "down", "2026-06-30", "2026-07-29"), ("AMD", "up", "2026-09-03", "2026-10-06"), ("AMD", "down", "2026-10-06", "2026-11-05")]
EXAMPLES = [("NVDA", "2026-10-06", "2026-11-20", "down"), ("AMD", "2026-04-04", "2026-05-11", "up")]      # the founder's two first examples (docs/POOL_PLAN.md, point 1)


def _prices(t: str):
    for root in ("data_provenance/selloff_live/prices", "data_provenance/selloff/prices"):
        f = Path(root) / f"{t}.parquet"
        if f.exists(): return pd.read_parquet(f)
    return None


def swings(d: pd.DataFrame, K: float) -> list:
    lp = np.log(d.close.to_numpy(float)); r = np.diff(lp, prepend=np.nan); n = len(lp); usual = pd.Series(r).rolling(USUAL, min_periods=120).std().to_numpy(); turns = []; direction = 0; hi = lo = None
    for k in range(n):
        u = usual[k]
        if not np.isfinite(u): continue
        if hi is None: hi = lo = k; continue
        thr = K * u
        if direction >= 0:      # rising, or not yet known: the highest point so far becomes a crest once the price is K usual moves below it
            if lp[k] > lp[hi]: hi = k
            elif lp[hi] - lp[k] >= thr: turns.append((hi, "crest", k)); direction = -1; lo = k; continue
        if direction <= 0:
            if lp[k] < lp[lo]: lo = k
            elif lp[k] - lp[lo] >= thr: turns.append((lo, "trough", k)); direction = 1; hi = k
    if turns:      # the swing still running: from the last confirmed turn to the furthest price since
        last, kind, _ = turns[-1]; ext = last + (int(np.argmin(lp[last:])) if kind == "crest" else int(np.argmax(lp[last:])))
        if ext > last: turns.append((ext, "trough" if kind == "crest" else "crest", None))
    out = []
    for (s, k0, conf), (e, k1, conf1) in zip(turns[:-1], turns[1:]):
        m = e - s; st = abs(lp[e] - lp[s]) / (usual[s] * np.sqrt(m)) if m > 0 and np.isfinite(usual[s]) else np.nan; path = float(np.nansum(np.abs(r[s + 1:e + 1])))
        out.append(dict(side="up" if k0 == "trough" else "down", start=d.index[s], end=d.index[e], sessions=int(m), move_pct=float((np.exp(lp[e] - lp[s]) - 1) * 100), strength=float(st), speed="fast" if st >= FAST["fast"] else "medium" if st >= FAST["medium"] else "slow",
                        first_seen=d.index[conf] if conf is not None else pd.NaT, straight=float(abs(lp[e] - lp[s]) / path) if path > 0 else np.nan, running=conf1 is None, in_usual_moves=float(abs(lp[e] - lp[s]) / usual[s]) if np.isfinite(usual[s]) else np.nan))
    return out


def _hit(sw, side, a, b):
    A = pd.Timestamp(a); B = pd.Timestamp(b) if b else None
    return any(x["side"] == side and abs((x["start"] - A).days) <= TOL and (B is None or abs((x["end"] - B).days) <= TOL) for x in sw)


def _chart(t, d, sw, K, f):
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    x = d.iloc[-SHOW:]; fig, ax = plt.subplots(figsize=(15, 4.8), dpi=110); ax.plot(x.index, x.close, color="#14171F", lw=1.1); shade = {"slow": 0.08, "medium": 0.18, "fast": 0.32}; k = 0; ymax = float(x.close.max()); ymin = float(x.close.min())
    for tr in sw:
        if tr["end"] <= x.index[0]: continue
        k += 1; tr["no"] = k; col = "#178A4C" if tr["side"] == "up" else "#C0392B"; a, b = max(tr["start"], x.index[0]), tr["end"]; ax.axvspan(a, b, color=col, alpha=shade[tr["speed"]], lw=0)
        ax.annotate(f"{k}", (a + (b - a) / 2, ymin + (ymax - ymin) * (0.03 if tr["side"] == "up" else 0.94)), ha="center", fontsize=9, color=col, fontweight="bold")
        ax.scatter([b], [float(x.close.loc[b])], s=14, color="#14171F", zorder=3)
    ax.set_title(f"{t}: every swing between a trough and a crest is one trend (K = {K}). Green up, red down; darker = faster. Dots: the crests and troughs.", fontsize=10, loc="left"); ax.grid(alpha=0.25); ax.margins(x=0.01); fig.tight_layout(); fig.savefig(f); plt.close(fig)


def cmd_run(tickers=None, K=None):
    OUT.mkdir(parents=True, exist_ok=True); P = {t: _prices(t) for t in (tickers or POOL)}; missing = [t for t, d in P.items() if d is None or len(d) < 400]; P = {t: d for t, d in P.items() if t not in missing}
    # ---- which K reproduces the founder's marks best
    marks = [m for m in MARKS if m[0] in P]; score = {}
    for k in KS:
        S = {t: swings(d, k) for t, d in P.items()}; score[k] = (sum(_hit(S[t], side, a, b) for t, side, a, b in marks), float(np.mean([sum(x["end"] > d.index[max(0, len(d) - SHOW)] for x in S[t]) for t, d in P.items()])))
    if K is None: K = max(KS, key=lambda k: (score[k][0], -abs(k - 7))) if marks else 7
    print(f"  the founder's marks ({len(marks)} swings that must exist) reproduced, by K: " + ", ".join(f"K={k}: {score[k][0]} ({score[k][1]:.0f} trends a stock)" for k in KS) + f" -> K = {K} is drawn")
    rows = []; L = ["# The trends on the daily chart: every swing between a trough and a crest (third version, from the founder's marks)", "", f"Step 1 of the addition and subtraction pool (`docs/POOL_PLAN.md`). No news is used. A crest is marked when the price has fallen back from it by K usual daily moves of the stock, a trough the same way upward; a trend is the swing from one turn to the next. "
         f"**K = {K}**, the value that reproduces most of the founder's marks of 25 Nov ({score[K][0]} of {len(marks)}): " + ", ".join(f"K={k}: {score[k][0]}" for k in KS) + ". 'Strength' = the move divided by how far the price drifts by chance in that many sessions (fast swings are darker); 'size' = the move in usual daily moves; "
         "'first seen' = the day the swing could have been recognised with the prices known that day. The last swing of each stock is still running. **To mark: which numbers are wrong, and what is missing.**", ""]
    for t, d in P.items():
        sw = swings(d, K); _chart(t, d, sw, K, OUT / f"{t}.png"); shown = [x for x in sw if "no" in x]
        L += [f"## {t}", "", f"![{t}]({t}.png)", "", "| no. | direction | from | to | sessions | move | size, usual daily moves | strength (speed) | straightness | first seen |", "|---|---|---|---|---|---|---|---|---|---|"]
        for x in shown:
            L.append(f"| {x['no']} | {x['side']} | {x['start']:%Y-%m-%d} | {x['end']:%Y-%m-%d}{' (running)' if x['running'] else ''} | {x['sessions']} | {x['move_pct']:+.0f}% | {x['in_usual_moves']:.0f} | {x['strength']:.1f} ({x['speed']}) | {x['straight']:.2f} | {'' if pd.isna(x['first_seen']) else format(x['first_seen'], '%Y-%m-%d')} |")
            rows.append(dict(ticker=t, no=x["no"], side=x["side"], start=f"{x['start']:%Y-%m-%d}", end=f"{x['end']:%Y-%m-%d}", running=x["running"], sessions=x["sessions"], move_pct=round(x["move_pct"], 1), size_usual_moves=round(x["in_usual_moves"], 1), strength=round(x["strength"], 2), speed=x["speed"], straightness=round(x["straight"], 2), first_seen="" if pd.isna(x["first_seen"]) else f"{x['first_seen']:%Y-%m-%d}", founder_mark=""))
        L.append(""); print(f"  {t}: {len(shown)} trends on the chart; last price day {d.index[-1]:%Y-%m-%d}")
    R = pd.DataFrame(rows); R.to_csv(OUT / "trends.csv", index=False)
    L += ["## The founder's marks of 25 Nov, checked one by one", ""]
    for t, side, a, b in marks:
        ok = _hit(swings(P[t], K), side, a, b); msg = f"{t} {side} from about {a}" + (f" to about {b}" if b else "") + (": found" if ok else ": NOT found"); L.append("- " + msg); print("  mark: " + msg)
    for t, a, b, side in EXAMPLES:
        if t not in P: continue
        g = R[(R.ticker == t) & (R.side == side) & (R.start <= b) & (R.end >= a)]; msg = f"first example, {t} {side} {a} to {b}: " + ("; ".join(f"trend {x.no}, {x.start} to {x.end}, {x.sessions} sessions, {x.move_pct:+.0f}%" for x in g.itertuples()) if len(g) else "NOT found"); L.append("- " + msg); print("  " + msg)
    if missing: L += ["", f"No prices on disk for: {', '.join(missing)}."]; print(f"  no prices for: {missing}")
    (OUT / "index.md").write_text("\n".join(L) + "\n"); print(f"{len(R)} trends drawn for {len(P)} stocks with K = {K} -> docs/trends/index.md (the charts are the .png files beside it), docs/trends/trends.csv")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run"]); ap.add_argument("--tickers", default=None); ap.add_argument("--k", type=float, default=None); a = ap.parse_args(); cmd_run(a.tickers.split(",") if a.tickers else None, a.k)
