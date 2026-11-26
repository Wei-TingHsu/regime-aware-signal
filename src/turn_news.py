"""turn_news.py -- test TN-1 (TRACK 3.141): the founder's assumption 'a trend turns because of news' (docs/POOL_PLAN.md, point 4).

A TURN = the day a trend of the fixed trend rule ends (src/trend_finder.py, K = 5 usual daily moves): the top of a rise or the bottom of a fall. The new trend starts
the session after. If news causes turns, the first sessions of the new trend should be days on which the market answers news far more often than ordinary days are.

News with a date that is on this laptop, free:
  the company's own results (8-K item 2.02) | the company's other 8-K filings | any 8-K of the company | a Fed decision day | a TrendForce release (chip companies only)
A filing made after 16:00 New York is answered the next session; that 'answer day' is what is compared with the turn.

Windows around the turn day (day 0 = the top or the bottom):
  the session after (day +1) | the turn day or the session after (0, +1) | from the session before to two after (-1 .. +2)

For each kind of news and window: the share of turns that have such news there, against the same share when every stock's turns are slid along its own calendar
(the number of turns and their spacing stay as they are). One cell passes when its chance is under 0.05 / 15.

    python -m src.turn_news run      # free, no download; needs the daily check's prices and 8-K list
"""
from __future__ import annotations
import argparse, re
from pathlib import Path
import numpy as np, pandas as pd

DOCS = Path("docs"); F8 = Path("data_provenance/selloff_live/filings8k.csv"); FED = Path("data_provenance/doc_reads"); TFR = Path("data_provenance/trendforce/releases.csv"); FROM = "2018-06-01"; MINSHIFT = 20
CHIPS = ["AMD", "AVGO", "INTC", "MU", "NVDA", "QCOM", "SNDK", "TSM", "TXN"]
WINDOWS = {"the session after the turn (+1)": (1, 1), "the turn day or the session after (0, +1)": (0, 1), "from the session before to two after (-1 .. +2)": (-1, 2)}
KINDS = ["the company's own results", "the company's other 8-K filings", "any 8-K of the company", "a Fed decision day", "a TrendForce release (chip companies)"]


def _answer_day(cal_values, ts, late_next=True):
    d = np.datetime64(pd.Timestamp(ts).normalize()); i = int(np.searchsorted(cal_values, d, side="left"))
    if late_next and i < len(cal_values) and cal_values[i] == d and pd.Timestamp(ts).hour >= 16: i += 1
    return i


def cmd_run():
    from src import trend_finder as TF
    if not F8.exists(): print(f"{F8} is missing: run the daily check first"); return
    R8 = pd.read_csv(F8, parse_dates=["accepted_ny"]); R8["results"] = R8.results.astype(str).str.lower().isin(["true", "1"])
    fed = sorted({pd.Timestamp(m.group(1)) for f in FED.glob("fomc_statement__*") for m in [re.search(r"__(\d{8})", f.name)] if m}) if FED.exists() else []
    tfd = sorted(pd.to_datetime(pd.read_csv(TFR).date, errors="coerce").dropna().unique()) if TFR.exists() else []
    S = {}; info = []
    for t in TF.POOL:
        d = TF._prices(t)
        if d is None or len(d) < 400: info.append(f"{t}: no prices"); continue
        d = d.copy(); d.index = pd.DatetimeIndex(d.index).tz_localize(None) if getattr(d.index, "tz", None) is not None else pd.DatetimeIndex(d.index); sw = TF.swings(d, TF.K_FIXED)
        cal = d.index[d.index >= FROM]; cv = cal.values; n = len(cal); pos = {x: i for i, x in enumerate(cal)}
        if n < 300: info.append(f"{t}: under 300 sessions since {FROM}"); continue
        top = np.zeros(n, bool); bot = np.zeros(n, bool)
        for x in sw:
            if x["side"] in ("up", "down") and not x["running"] and x["end"] in pos: (top if x["side"] == "up" else bot)[pos[x["end"]]] = True
        def flag(dates, late):
            f = np.zeros(n, bool)
            for ts in dates:
                i = _answer_day(cv, ts, late)
                if 0 <= i < n and pd.Timestamp(ts) >= cal[0] - pd.Timedelta(days=5): f[i] = True
            return f
        g = R8[R8.ticker == t]; has8 = len(g) > 0
        N = {KINDS[0]: flag(g[g.results].accepted_ny, True) if has8 else None, KINDS[1]: flag(g[~g.results].accepted_ny, True) if has8 else None, KINDS[2]: flag(g.accepted_ny, True) if has8 else None,
             KINDS[3]: flag(fed, False) if fed else None, KINDS[4]: flag(tfd, False) if (tfd and t in CHIPS) else None}
        S[t] = dict(n=n, turn=top | bot, top=top, bot=bot, N=N); info.append(f"{t}: {int((top | bot).sum())} turns" + ("" if has8 else " (no 8-K list)"))
    if not S: print("no stock could be used"); return
    def spread(f, a, b):      # news answered on day j counts for a turn on day i when j - i lies in [a, b]
        out = np.zeros(len(f), bool)
        for k in range(a, b + 1):
            out |= np.roll(f, -k) if k else f
        return out
    cells = {}; nmin = min(v["n"] for v in S.values()); shifts = list(range(MINSHIFT, nmin - MINSHIFT)); any_news = {t: {w: np.zeros(S[t]["n"], bool) for w in WINDOWS} for t in S}
    for kind in KINDS:
        for wl, (a, b) in WINDOWS.items():
            use = [(t, S[t]["turn"], spread(S[t]["N"][kind], a, b)) for t in S if S[t]["N"][kind] is not None]
            if not use: cells[(kind, wl)] = None; continue
            if kind in (KINDS[2], KINDS[3], KINDS[4]):
                for t, _, f in use: any_news[t][wl] |= f
            tot = sum(int(T.sum()) for _, T, _ in use); hit = sum(int((T & f).sum()) for _, T, f in use); base = sum(int(f.sum()) for _, _, f in use) / sum(len(f) for _, _, f in use)
            z = np.array([sum(int((np.roll(T, k) & f).sum()) for _, T, f in use) for k in shifts]); p = float((np.sum(z >= hit) + 1) / (len(z) + 1))
            sub = {}
            for nm in ("top", "bot"):
                tt = sum(int(S[t][nm].sum()) for t, _, _ in use); hh = sum(int((S[t][nm] & f).sum()) for t, _, f in use); sub[nm] = (hh, tt)
            cells[(kind, wl)] = dict(turns=tot, hit=hit, share=hit / tot if tot else np.nan, base=base, expected=float(z.mean()) / tot if tot else np.nan, chance=p, stocks=len(use), sub=sub)
    live = {k: v for k, v in cells.items() if v}; bar = 0.05 / len(live) if live else np.nan; allturn = sum(int(v["turn"].sum()) for v in S.values())
    L = ["# Test TN-1: do trends turn on news? (the founder's assumption, POOL_PLAN point 4)", "", f"Registered in TRACK 3.141 before running. {len(S)} pool stocks, sessions from {FROM}; {allturn} turns of the fixed trend rule (K = {TF.K_FIXED} usual daily moves). "
         f"News dates on file: 8-K filings of {R8[R8.ticker.isin(list(S))].ticker.nunique()} of these companies, {len(fed)} Fed decision days, {len(tfd)} TrendForce release days. "
         "'Share of turns' = the turns that have such news in the window. 'Ordinary' = the same share when each stock's turns are slid along its own calendar. "
         f"'Chance' = the share of the {len(shifts)} slid copies with at least as many. **PASSES** = chance under {bar:.4f} (0.05 / {len(live)} cells).", "",
         "| kind of news | window around the turn | turns | with such news | share of turns | ordinary | times the ordinary | chance | verdict | tops / bottoms with such news |", "|---|---|---|---|---|---|---|---|---|---|"]
    print(f"{len(S)} pool stocks, {allturn} turns since {FROM}; news on file: 8-K lists, {len(fed)} Fed decision days, {len(tfd)} TrendForce days; {len(shifts)} slid copies; a cell passes under {bar:.4f}")
    print("  share of turns with such news (ordinary; times) | chance | verdict | kind of news | window")
    for (kind, wl), v in cells.items():
        if not v: L.append(f"| {kind} | {wl} | | | | | | | no dates on file | |"); print(f"    no dates on file | {kind} | {wl}"); continue
        ok = v["chance"] < bar; times = v["share"] / v["expected"] if v["expected"] else np.nan; sb = v["sub"]
        L.append(f"| {kind} | {wl} | {v['turns']} | {v['hit']} | {v['share']:.1%} | {v['expected']:.1%} | {times:.2f} | {v['chance']:.4f} | {'**PASSES**' if ok else 'no'} | {sb['top'][0]} of {sb['top'][1]} / {sb['bot'][0]} of {sb['bot'][1]} |")
        print(f"    {v['share']:.1%} ({v['expected']:.1%}; {times:.2f}x) | {v['chance']:.4f} | {'PASSES' if ok else 'no'} | {kind} | {wl}")
    L += ["", "## How many turns have ANY dated news near them (any 8-K of the company, a Fed decision, a TrendForce release)", "", "| window | turns | with any dated news | share | ordinary |", "|---|---|---|---|---|"]
    print("  turns with ANY dated news near them (own 8-K, Fed decision, TrendForce):")
    for wl in WINDOWS:
        hit = sum(int((S[t]["turn"] & any_news[t][wl]).sum()) for t in S); base = sum(int(any_news[t][wl].sum()) for t in S) / sum(S[t]["n"] for t in S)
        L.append(f"| {wl} | {allturn} | {hit} | {hit / allturn:.1%} | {base:.1%} |"); print(f"    {wl}: {hit} of {allturn} = {hit / allturn:.1%} (ordinary days: {base:.1%})")
    L += ["", "Stocks: " + "; ".join(info), "", "What this cannot say: news without a date on file is not counted (press reports, analyst changes, product launches, news of OTHER companies -- a customer's or a rival's results); "
          "a turn is only known afterwards (the rule confirms it some sessions later), so this is about causes, not about a trade; a turn that has news near it need not be caused by it.", "Sources: SEC EDGAR (8-K lists), the Federal Reserve (statement dates), TrendForce press centre (release dates)."]
    DOCS.mkdir(exist_ok=True); (DOCS / "turn_news.md").write_text("\n".join(L) + "\n"); print("  " + "; ".join(info)); print("-> docs/turn_news.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run"]); ap.parse_args(); cmd_run()
