"""selloff_live.py -- the DAILY CHECK of the frozen sell-off rules SS-2a, SS-2b, SS-2c (TRACK 3.110), their forward record, and the Severe Sell-off block.

One command, once a day after the New York close:
    python -m src.selloff_live daily
What it does, in order:
  1. downloads today's prices for the list (Yahoo, free) into a SEPARATE folder, data_provenance/selloff_live -- the study's own data
     (data_provenance/selloff) is never touched, so every recorded result can still be reproduced;
  2. downloads the list of 8-K filings (SEC, free) and the two index series rule SS-2b needs (FRED, free, with the project's FRED key);
  3. rebuilds the sell-off events and their tables with the study's own code, pointed at the separate folder;
  4. tests every sell-off of 5% or more against the rules exactly as frozen in docs/selloff_rules.json;
  5. records each match, and fills in what followed once the sessions exist: sold at the next open, closed at the rule's exit, the founder's real cost;
  6. writes the forward record (docs/selloff_rules_forward.md) and what the block on the page shows.
Needs SEC_CONTACT and FRED_API_KEY set in the window. No cost. About 5 to 10 minutes.
"""
from __future__ import annotations
import argparse, json, os, shutil
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd

LIVE = Path("data_provenance/selloff_live"); STUDY = Path("data_provenance/selloff"); RULES = Path("docs/selloff_rules.json"); FWD = Path("data_provenance/live/selloff_rules_forward.csv"); CARD = Path("processed/selloff_rules_card.json")
START = pd.Timestamp("2026-11-24"); VERDICT_AT = 30; NY = ZoneInfo("America/New_York"); GROUP_DEF = ("stocks", "1 session, -5% or worse"); FRED_IDS = ["USEPUINDXD", "STLFSI4"]
COLS = ["code", "ticker", "day", "move_pct", "side", "exit_sessions", "entry_day", "exit_day", "alone_bp", "against_spx_bp", "stock_move_bp", "spx_move_bp"]


def _redirect():
    """point the study's own code at the separate live folder (this process only)"""
    import src.selloff_study as SS
    SS.ROOT = LIVE; SS.PX = LIVE / "prices"; SS.DOCS = LIVE / "docs"
    import src.selloff_inputs as SI
    if SI.ROOT != LIVE: raise SystemExit("the inputs module was loaded before the redirect -- tell Claude")
    return SS, SI


def _prices(SS, now):
    import yfinance as yf
    SS.PX.mkdir(parents=True, exist_ok=True); ticks = SS._stocks() + SS.INDEX + SS.SECTORS + ["^VIX"]; n = 0; bad = []
    D = yf.download(ticks, start="1998-01-01", interval="1d", progress=False, auto_adjust=True, group_by="ticker", threads=True)
    for t in ticks:
        try:
            d = D[t][["Open", "High", "Low", "Close", "Volume"]].dropna(subset=["Close"]); d.columns = ["open", "high", "low", "close", "volume"]; d.index = pd.DatetimeIndex(d.index).tz_localize(None)
            if len(d) and d.index[-1].date() == now.date() and now.hour * 60 + now.minute < 16 * 60 + 10: d = d.iloc[:-1]      # today's bar is not finished: left out
            if len(d) < 300: bad.append(t); continue
            d.to_parquet(SS.PX / f"{t.replace('^', '_')}.parquet"); n += 1
        except Exception: bad.append(t)
    print(f"  prices: {n} of {len(ticks)} securities; without prices: {bad or 'none'}"); return n


def _fred():
    ex = LIVE / "extra"; ex.mkdir(parents=True, exist_ok=True)
    if not os.environ.get("FRED_API_KEY"): print("  FRED_API_KEY is not set: the two index series were NOT refreshed -- rule SS-2b cannot be checked today"); return False
    try:
        from fredapi import Fred
        fr = Fred(api_key=os.environ["FRED_API_KEY"])
        for k in FRED_IDS: x = fr.get_series(k).dropna(); x.index = pd.to_datetime(x.index); x.to_frame("value").to_parquet(ex / f"fred_{k}.parquet")
        print(f"  FRED: {', '.join(FRED_IDS)} refreshed"); return True
    except Exception as e: print(f"  FRED failed ({type(e).__name__}): rule SS-2b cannot be checked today"); return False


def _sec_copy():
    """the reported financials (for 'size rank in the list') are taken from the study's folder as they are; they change once a quarter"""
    if not (LIVE / "sec").exists() and (STUDY / "sec").exists(): shutil.copytree(STUDY / "sec", LIVE / "sec"); print("  reported financials copied from the study's folder (first run)")


def _stage(sig: dict, now) -> str:
    """the page's one colour rule (TRACK 3.102): red = trade now (from the close of the sell-off day until 5 minutes after the entry at the next open); yellow = the rule's time is running, best entry passed; green = over, kept 24 hours"""
    ent = datetime.fromisoformat(sig["entry_at"]); ex = datetime.fromisoformat(sig["exit_at"])
    if now <= ent + timedelta(minutes=5): return "red"
    if now <= ex: return "yellow"
    return "green" if now <= ex + timedelta(hours=24) else ""


def _next_sessions(day: pd.Timestamp, k: int) -> list:
    """the next k weekdays after `day` (public holidays are not known to this code; on a holiday the entry is the session after)"""
    out = []; d = day
    while len(out) < k:
        d = d + pd.Timedelta(days=1)
        if d.weekday() < 5: out.append(d)
    return out


def check(SS=None, start=START, now=None):
    """steps 4 to 6: the frozen rules against the tables in the live folder. Returns the card."""
    from src.selloff_rules import apply_condition
    from src import real_cost as RC
    if SS is None: SS, _ = _redirect()
    now = now or datetime.now(NY); R = json.loads(RULES.read_text())["rules"]; E = pd.read_csv(SS.ROOT / "events.csv", parse_dates=["day"]); E["event_id"] = E.index; P = SS._px(); spy = P["SPY"]
    B = E[(E.unit == GROUP_DEF[0]) & (E.definition == GROUP_DEF[1])].sort_values("day").reset_index(drop=True); tb = SS.ROOT / "tables"
    tabs = {}
    for tn in sorted({c["table"] for r in R for c in r["conditions"]}):
        f = tb / f"{tn}.csv"; tabs[tn] = pd.read_csv(f).drop_duplicates("event_id").set_index("event_id").reindex(B.event_id.to_numpy()) if f.exists() else pd.DataFrame(index=B.event_id.to_numpy())
    new = (B.day >= start).to_numpy(); last = spy.index[-1]; F = pd.read_csv(FWD, parse_dates=["day"]) if FWD.exists() else pd.DataFrame(columns=COLS); have = {(r.code, r.ticker, r.day) for r in F.itertuples()}; rows = []; missing = {}
    for r in R:
        need = [c for c in r["conditions"]]; m = np.ones(len(B), bool)
        for c in need:
            cols = c["columns"] if c["kind"] == "group" else [c["column"]]; T = tabs[c["table"]]; lack = [x for x in cols if x not in T.columns or T.loc[B.event_id[new].to_numpy(), x].isna().all()] if new.any() else []
            if lack: missing[r["code"]] = missing.get(r["code"], []) + lack
            m &= apply_condition(c, T)
        r["_mask"] = m
        for q in np.flatnonzero(m & new):
            b = B.iloc[q]
            if (r["code"], b.ticker, b.day) not in have: rows.append(dict(code=r["code"], ticker=b.ticker, day=b.day, move_pct=round(float(b["last day's move %"]), 2) if "last day's move %" in B.columns else np.nan, side=r["side"], exit_sessions=r["exit"]))
    if rows: F = pd.concat([F, pd.DataFrame(rows)], ignore_index=True)
    for c in COLS:
        if c not in F.columns: F[c] = np.nan
    F["day"] = pd.to_datetime(F["day"]); F[["entry_day", "exit_day"]] = F[["entry_day", "exit_day"]].astype(object)
    for k, r in F.iterrows():      # what followed: sold at the next open, closed at the rule's exit, the founder's real cost
        d = P.get(r.ticker)
        if d is None or r.day not in d.index or r.day not in spy.index or pd.notna(r.alone_bp): continue
        i = d.index.get_loc(r.day); j = spy.index.get_loc(r.day); h = int(r.exit_sessions)
        if i + h >= len(d) or j + h >= len(spy): continue
        sign = -1.0 if r.side == "SELL" else 1.0; pin, pout = float(d.open.iloc[i + 1]), float(d.close.iloc[i + h]); sin, sout = float(spy.open.iloc[j + 1]), float(spy.close.iloc[j + h]); nights = (d.index[i + h] - d.index[i + 1]).days; A = RC.ACCOUNT; SSb = RC.SPREAD_BP["stock"] / 1e4
        fee, amt = RC.round_trip(pin, pout, A, short=sign < 0); alone = sign * amt * (pout / pin - 1) - fee - 2 * SSb * amt - (RC.short_carry(amt, nights) if sign < 0 else 0.0)
        fee2, amt2 = RC.round_trip(sin, sout, A, short=sign > 0); hedge = -sign * amt2 * (sout / sin - 1) - fee2 - 2 * SSb * amt2 - (RC.short_carry(amt2, nights) if sign > 0 else 0.0)
        F.at[k, "entry_day"] = f"{d.index[i + 1]:%Y-%m-%d}"; F.at[k, "exit_day"] = f"{d.index[i + h]:%Y-%m-%d}"; F.at[k, "alone_bp"] = round(alone / A * 1e4, 1); F.at[k, "against_spx_bp"] = round((alone + hedge) / A * 1e4, 1); F.at[k, "stock_move_bp"] = round((pout / pin - 1) * 1e4, 1); F.at[k, "spx_move_bp"] = round((sout / sin - 1) * 1e4, 1)
    F = F[COLS].sort_values(["day", "code", "ticker"]).reset_index(drop=True); FWD.parent.mkdir(parents=True, exist_ok=True); tmp = FWD.with_suffix(".tmp"); F.to_csv(tmp, index=False); os.replace(tmp, FWD)
    # ---- the tally, per rule: each day counts once
    tally = {}; L = ["# Sell-off rules SS-2a, SS-2b, SS-2c: the forward record", "", f"Registered in TRACK 3.110 (24 Nov 2026) before any case. Every sell-off of 5% or more of the list from {start:%d %b %Y} is tested against the rules as frozen in `docs/selloff_rules.json`. A match is sold at the next open and closed at the rule's exit; "
         f"cost: the founder's fees, 2 basis points of spread per order, 4.8% a year on the short position; account US${70000:,}. Each day counts once per rule. **Verdict per rule at {VERDICT_AT} separate days.** The history numbers are flattered (the rules were chosen on those years); this record is the first clean evidence.", "",
         "| rule | trade that passed the test | history 2018-2026, per day with a trade | days so far with a known result | average so far, the stock alone | against the S&P 500 | waiting for their sessions |", "|---|---|---|---|---|---|---|"]
    for r in R:
        G = F[F.code == r["code"]]; K = G[G.alone_bp.notna()]; bd = K.groupby("day")[["alone_bp", "against_spx_bp"]].mean(); main = "against_spx" if not r["passed_alone"] else "alone"
        tally[r["code"]] = dict(days=int(len(bd)), alone=float(bd.alone_bp.mean()) if len(bd) else None, against_spx=float(bd.against_spx_bp.mean()) if len(bd) else None, waiting=int(G.alone_bp.isna().sum()), main=main)
        L.append(f"| {r['code']} | {'sell the stock' if r['passed_alone'] else 'sell the stock and buy the S&P 500 fund'}; exit +{r['exit']} | {r['history']['alone_bp' if r['passed_alone'] else 'against_spx_bp']:+.0f} bp ({r['history']['days']} days) | {len(bd)} of {VERDICT_AT} | {'' if not len(bd) else format(bd.alone_bp.mean(), '+.0f') + ' bp'} | {'' if not len(bd) else format(bd.against_spx_bp.mean(), '+.0f') + ' bp'} | {int(G.alone_bp.isna().sum())} |")
    f0 = lambda x: "" if pd.isna(x) else f"{x:+.0f}"
    L += ["", "| sell-off day | rule | stock | move that day % | sold at the open of | closed at the close of | the stock alone, bp after cost | against the S&P 500, bp after cost |", "|---|---|---|---|---|---|---|---|"] + [f"| {x.day:%Y-%m-%d} | {x.code} | {x.ticker} | {f0(x.move_pct) if pd.isna(x.move_pct) else format(x.move_pct, '+.1f')} | {x.entry_day if isinstance(x.entry_day, str) else ''} | {x.exit_day if isinstance(x.exit_day, str) else ''} | {f0(x.alone_bp)} | {f0(x.against_spx_bp)} |" for x in F.sort_values("day", ascending=False).itertuples()]
    if not len(F): L.append("| (no match yet) | | | | | | | |")
    if missing: L += ["", "Not checkable at the last run (an input was missing for the new days): " + "; ".join(f"{k}: {', '.join(sorted(set(v)))[:120]}" for k, v in missing.items()) + "."]
    Path("docs").mkdir(exist_ok=True); Path("docs/selloff_rules_forward.md").write_text("\n".join(L) + "\n")
    # ---- what the block shows
    sigs = []
    for r in R:
        for q in np.flatnonzero(r["_mask"] & new):
            b = B.iloc[q]; ns = _next_sessions(b.day, int(r["exit"])); ent = datetime.combine(ns[0].date(), datetime.min.time(), NY).replace(hour=9, minute=30); ex = datetime.combine(ns[-1].date(), datetime.min.time(), NY).replace(hour=16)
            if now <= ex + timedelta(hours=24): sigs.append(dict(code=r["code"], ticker=b.ticker, day=f"{b.day:%Y-%m-%d}", move_pct=round(float(b["last day's move %"]), 1) if "last day's move %" in B.columns else None, side=r["side"], hedged=not r["passed_alone"], entry_at=ent.isoformat(), exit_at=ex.isoformat(), exit_sessions=int(r["exit"]),
                                                             history_bp=r["history"]["alone_bp" if r["passed_alone"] else "against_spx_bp"], history_days=r["history"]["days"]))
    falls = B[(B.day == last)]; card = dict(checked=datetime.now(NY).isoformat(), last_close=f"{last:%Y-%m-%d}", falls_last_close=[dict(ticker=x.ticker, move_pct=round(float(x["last day's move %"]), 1)) for _, x in falls.iterrows()] if "last day's move %" in B.columns else [], signals=sigs, tally=tally,
                                              rules=[dict(code=r["code"], when=r["when"], exit=r["exit"], hedged=not r["passed_alone"], history_bp=r["history"]["alone_bp" if r["passed_alone"] else "against_spx_bp"], history_days=r["history"]["days"], per_year=r["history"]["per_year"]) for r in R], not_checkable=missing)
    CARD.parent.mkdir(parents=True, exist_ok=True); tmp = CARD.with_suffix(".tmp"); tmp.write_text(json.dumps(card, indent=1, default=float)); os.replace(tmp, CARD)
    print(f"  last finished session {last:%Y-%m-%d}: {len(falls)} sell-offs of 5% or more in the list" + (f" ({', '.join(falls.ticker)})" if len(falls) else "") + f"; matches of a rule since {start:%d %b}: {len(F)} ({len(rows)} new now)")
    for r in R: tl = tally[r["code"]]; print(f"  {r['code']}: {tl['days']} of {VERDICT_AT} days with a known result" + (f", average {tl[tl['main']]:+.0f} bp after cost" if tl["days"] else "") + f"; {tl['waiting']} waiting" + (f"; NOT CHECKABLE today: {', '.join(sorted(set(missing[r['code']])))[:90]}" if r["code"] in missing else ""))
    print("-> docs/selloff_rules_forward.md, data_provenance/live/selloff_rules_forward.csv"); return card


def cmd_daily():
    if not os.environ.get("SEC_CONTACT"): raise SystemExit("SEC_CONTACT is not set (the SEC asks every script to say who is calling)")
    if not RULES.exists(): raise SystemExit("docs/selloff_rules.json is missing: run `python -m src.selloff_rules freeze` first")
    SS, SI = _redirect(); now = datetime.now(NY); LIVE.mkdir(parents=True, exist_ok=True); print(f"Daily check of the sell-off rules, {now:%Y-%m-%d %H:%M} New York. The study's data is not touched; everything goes to {LIVE}.")
    if not _prices(SS, now): raise SystemExit("no prices downloaded (network?) -- nothing changed")
    SS.cmd_filings(); _sec_copy(); _fred(); SS.cmd_build(); SI.cmd_tables(); check(SS, now=now)
    try:
        from src import selloff_forward as F1; F1.scan(quiet=True)      # the plain rule SS-1 keeps its own forward record, as registered in 3.101
    except Exception: pass


# ------------------------------------------------------------------ the block on the page
def card_html() -> str:
    from src.selloff_forward import CARD_CSS
    css = CARD_CSS + "<style>.sso-red{outline:1px solid #C0392B;background:linear-gradient(135deg,rgba(255,236,233,.97),rgba(255,222,217,.92))}.sso-yel{outline:1px solid #B7791F;background:linear-gradient(135deg,rgba(255,249,235,.97),rgba(255,241,214,.92))}.sso-grn{outline:1px solid #178A4C;background:linear-gradient(135deg,rgba(236,248,241,.97),rgba(222,243,231,.92))}</style>"
    if not CARD.exists(): return css + "<div class='sso-wrap'><details class='sso'><summary><span class='sso-t'>Severe Sell-off</span><span class='sso-s sso-m'>Not checked yet: run the daily check once.</span></summary></details></div>"
    try: C = json.loads(CARD.read_text())
    except Exception: return ""
    now = datetime.now(NY); S = [dict(s, stage=_stage(s, now)) for s in C.get("signals", [])]; S = [s for s in S if s["stage"]]; order = {"red": 0, "yellow": 1, "green": 2}; S.sort(key=lambda s: order[s["stage"]]); chk = datetime.fromisoformat(C["checked"]); old = (now - chk).total_seconds() > 30 * 3600
    word = {"red": "TRADE NOW", "yellow": "best entry time passed", "green": "trading time over"}; cls = {"red": "sso-red", "yellow": "sso-yel", "green": "sso-grn"}.get(S[0]["stage"], "") if S else ""
    if S: status = "<b>" + ", ".join(f"{s['ticker']} {s['move_pct']:+.1f}%" for s in S[:3]) + (f" +{len(S) - 3}" if len(S) > 3 else "") + f"</b><br><b>{word[S[0]['stage']]}</b> · {S[0]['code']}: sell at the next open"
    else: fl = C.get("falls_last_close", []); status = ("No rule met at the last close." if not fl else f"{len(fl)} fell 5%+ at the last close; no rule met.") + (f"<br><span class='sso-m'>checked {chk:%d %b %H:%M} New York</span>" if not old else "")
    if old: status += "<br><span class='sso-m'><b>Not checked since " + f"{chk:%d %b %H:%M}" + " New York — run the daily check.</b></span>"
    d = []
    for s in S:
        ent = datetime.fromisoformat(s["entry_at"]); ex = datetime.fromisoformat(s["exit_at"]); d.append(f"<p><b>{s['ticker']}</b> closed {s['move_pct']:+.1f}% on {s['day']} and meets <b>{s['code']}</b> — <b>{word[s['stage']]}</b>. Trade: sell the stock" + (" and buy the S&P 500 fund" if s["hedged"] else "") + f" at the open of {ent:%a %d %b}; close it at the close of {ex:%a %d %b}. History 2018–2026: {s['history_bp']:+.0f} basis points per day with a trade, after cost ({s['history_days']} days).</p>")
    for r in C.get("rules", []):
        tl = (C.get("tally") or {}).get(r["code"], {}); d.append(f"<p><b>{r['code']}</b> — a stock of the list closes 5% or more down AND {' AND '.join(r['when'])}. Exit: the close {r['exit']} sessions after. History: {r['history_bp']:+.0f} bp after cost, about {r['per_year']:.0f} days a year. Forward record: {tl.get('days', 0)} of {VERDICT_AT} days" + (f", average {tl[tl['main']]:+.0f} bp" if tl.get("days") else "") + ".</p>")
    if C.get("not_checkable"): d.append("<p><b>Not checkable at the last run:</b> " + ", ".join(C["not_checkable"]) + " (an input was missing).</p>")
    d.append("<p class='sso-m'>Rules passed a test on 2005–2026 with the real trading cost; those numbers are flattered because the rules were chosen on the same years. The verdict comes from the forward record at 30 days each. Colours: red = trade now · yellow = best entry passed · green = over.</p>")
    d.append(f"<p class='sso-m'>Last finished session {C.get('last_close')} · checked {chk:%d %b %H:%M} New York · daily prices from Yahoo, filings from the SEC, indices from FRED</p>")
    return css + f"<div class='sso-wrap'><details class='sso {cls}'><summary><span class='sso-t'>Severe Sell-off</span><span class='sso-more'>details ▾</span><span class='sso-s'>{status}</span></summary><div class='sso-d'>{''.join(d)}</div></details></div>"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["daily", "check"]); a = ap.parse_args()
    cmd_daily() if a.cmd == "daily" else check()
