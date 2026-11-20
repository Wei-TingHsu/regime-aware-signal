"""selloff_count.py -- stage A of the sell-off study (TRACK 3.75): HOW MANY big sell-offs are there to learn from, under each way of defining one?
It only counts events and how they bunch on the same days. It does NOT look at what happened afterwards (that is fixed in stage B, before any outcome
is seen). Free daily prices from Yahoo; nothing paid.

    python -m src.selloff_count        # -> docs/selloff_counts.md
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd

INDEX = {"SPY": "S&P 500", "QQQ": "Nasdaq-100", "SOXX": "semiconductors (SOXX)", "SMH": "semiconductors (SMH)", "IWM": "small companies"}
SECTORS = {"XLK": "technology", "XLC": "communication", "XLY": "consumer discretionary", "XLP": "consumer staples", "XLE": "energy", "XLF": "financials", "XLV": "health care", "XLI": "industrials", "XLB": "materials", "XLRE": "real estate", "XLU": "utilities"}
CHAIN = ["AMD", "NVDA", "MU", "INTC", "AVGO", "SNDK", "SKHY", "ORCL", "TSM", "CRWD", "GOOG", "META", "AMZN", "MSFT"]
ONE_DAY = [3, 4, 5, 7, 10]; DRAWDOWN = [(5, 7), (5, 10), (10, 10), (10, 15), (20, 15), (20, 20)]      # one-day falls of X% or more; and falls of X% or more over N sessions (N, X)


def prices(tickers):
    import yfinance as yf
    out = {}
    for t in tickers:
        try:
            d = yf.download(t, start="1999-01-01", interval="1d", progress=False, auto_adjust=True); c = d["Close"]; c = c.iloc[:, 0] if isinstance(c, pd.DataFrame) else c; c = c.dropna()
            if len(c) > 250: out[t] = c
            else: print(f"  {t}: only {len(c)} days of prices -- left out")
        except Exception as e: print(f"  {t}: {type(e).__name__}: {str(e)[:80]}")
    return out


def events(c: pd.Series, n: int, x: float) -> pd.DatetimeIndex:
    """days on which the return over the last n sessions is -x% or worse, counted once per episode: a new event needs n sessions since the last one"""
    r = c.pct_change(n) * 100; hit = r.index[r <= -x]; keep = []; last = None; pos = {d: i for i, d in enumerate(c.index)}
    for d in hit:
        if last is None or pos[d] - pos[last] >= max(n, 1): keep.append(d); last = d
    return pd.DatetimeIndex(keep)


def main():
    groups = [("Indices", INDEX), ("Sectors", SECTORS), ("AI-chain stocks", {t: t for t in CHAIN})]; P = prices(list(INDEX) + list(SECTORS) + CHAIN)
    L = ["# Sell-off study, stage A: how many events are there to learn from?", "", "Counts only; nothing after the event day was looked at. Daily prices adjusted for splits and dividends, Yahoo. An episode is counted once: a new event needs as many sessions as the window since the last one.", ""]
    defs = [(1, x, f"one day, -{x}% or worse") for x in ONE_DAY] + [(n, x, f"{n} sessions, -{x}% or worse") for n, x in DRAWDOWN]; allev = {}
    for title, G in groups:
        L += [f"## {title}", "", "| | first day of prices | " + " | ".join(lab for _, _, lab in defs) + " |", "|---|---|" + "---|" * len(defs)]
        for t, name in G.items():
            if t not in P: L.append(f"| {name} | no prices | " + " | ".join("" for _ in defs) + " |"); continue
            row = []
            for n, x, lab in defs: e = events(P[t], n, x); allev.setdefault((title, lab), []).append(pd.Series(t, index=e)); row.append(str(len(e)))
            L.append(f"| {name} ({t}) | {P[t].index[0]:%Y-%m-%d} | " + " | ".join(row) + " |"); print(f"  {t:5} from {P[t].index[0]:%Y-%m-%d}: " + ", ".join(f"{lab}: {v}" for (_, _, lab), v in zip(defs, row)))
        L.append("")
    L += ["## How the events bunch together", "", "Many units fall on the same day in a crisis, so events are not all separate pieces of evidence. 'Separate days' is the honest count; 'share in the three busiest years' shows how much 2008, 2020 and similar years dominate.", "", "| group | definition | events | separate days | share of events in the three busiest years | busiest years |", "|---|---|---|---|---|---|"]
    for (title, lab), parts in allev.items():
        S = pd.concat(parts) if parts else pd.Series(dtype=object)
        if not len(S): continue
        yr = pd.Series(S.index.year).value_counts(); top = yr.head(3); L.append(f"| {title} | {lab} | {len(S)} | {S.index.nunique()} | {top.sum() / len(S):.0%} | {', '.join(f'{y} ({v})' for y, v in top.items())} |")
    print("\n".join(L[-(len(allev) + 2):])); Path("docs").mkdir(exist_ok=True); Path("docs/selloff_counts.md").write_text("\n".join(L) + "\n"); print("-> docs/selloff_counts.md")


if __name__ == "__main__": main()
