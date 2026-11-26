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
import argparse, json, logging, os, shutil, time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd

LIVE = Path("data_provenance/selloff_live"); STUDY = Path("data_provenance/selloff"); RULES = Path("docs/selloff_rules.json"); FWD = Path("data_provenance/live/selloff_rules_forward.csv"); CARD = Path("processed/selloff_rules_card.json")
START = pd.Timestamp("2026-11-24"); VERDICT_AT = 30; NY = ZoneInfo("America/New_York"); GROUP_DEF = ("stocks", "1 session, -5% or worse"); FRED_IDS = ["USEPUINDXD", "STLFSI4"]
COLS = ["code", "ticker", "day", "move_pct", "side", "exit_sessions", "entry_day", "exit_day", "alone_bp", "against_spx_bp", "stock_move_bp", "spx_move_bp", "way", "way_usd", "size_A", "size_B", "size_C", "size_D", "usd_A", "usd_B", "usd_C", "usd_D"]
# Founder, 26 Nov 2026 (TRACK 3.132): when signals overlap, all four ways are kept side by side. A = one position per stock; B = limits on the whole account (at most US$35,000 sold short in all,
# at most US$70,000 in all positions together; a new signal gets what is left); C = A and B; D = no rule, every signal at its full size. The page shows SHOWN.
WAYS = {"A": "one position per stock", "B": "limits on the whole account", "C": "one position per stock AND limits on the whole account", "D": "no rule: every signal at full size"}
SHOWN = "C"; CAP_ALL, CAP_SHORT, MIN_TRADE = 70_000.0, 35_000.0, 5_000.0
# NYSE Group's holiday calendar (press release 'NYSE Group Announces 2026, 2027 and 2028 Holiday and Early Closings Calendar', read 25 Nov 2026). Extend before 2028.
HOLIDAYS = {pd.Timestamp(x) for x in ["2026-11-26", "2026-12-25", "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31", "2027-06-18", "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24"]}
EARLY = {pd.Timestamp(x) for x in ["2026-11-27", "2026-12-24", "2027-11-26"]}      # the market closes at 13:00 New York time
SHORT_MONEY = 35_000.0      # founder, 25 Nov 2026 (TRACK 3.121): the inverse fund where one exists; where none exists the stock is sold short with US$35,000, half the account
HS = {"stock": 3.6 + 0.6, "fund1": 7.8 + 5.2, "fund2": 11.4 + 6.6, "spy": 4.0}      # half the bid-ask gap in and out, basis points (measured, TRACK 3.114; the S&P 500 fund: the allowance)


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
    logging.getLogger("yfinance").setLevel(logging.CRITICAL)      # Yahoo's own message for a refused request is 'possibly delisted' -- misleading; this code reports refusals itself
    def save(t, d):
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        d = d[["Open", "High", "Low", "Close", "Volume"]].dropna(subset=["Close"]); d.columns = ["open", "high", "low", "close", "volume"]; d.index = pd.DatetimeIndex(d.index).tz_localize(None)
        if len(d) and d.index[-1].date() == now.date() and now.hour * 60 + now.minute < 16 * 60 + 10: d = d.iloc[:-1]      # today's bar is not finished: left out
        if len(d) < 300: return False
        d.to_parquet(SS.PX / f"{t.replace('^', '_')}.parquet"); return True
    try: D = yf.download(ticks, start="1998-01-01", interval="1d", progress=False, auto_adjust=True, group_by="ticker", threads=True)
    except Exception: D = None
    for t in ticks:
        try: ok = D is not None and save(t, D[t].copy())
        except Exception: ok = False
        n += ok; bad += [] if ok else [t]
    for wait in (20, 40, 60):      # Yahoo refuses requests when many come at once; the refused names are asked again one by one, slowly
        if not bad: break
        print(f"  Yahoo did not answer for {len(bad)} of {len(ticks)} securities (too many requests at once -- they are NOT delisted); waiting {wait} seconds and asking again ..."); time.sleep(wait); still = []
        for t in bad:
            try: ok = save(t, yf.download(t, start="1998-01-01", interval="1d", progress=False, auto_adjust=True)); time.sleep(1.0)
            except Exception: ok = False
            n += ok; still += [] if ok else [t]
        bad = still
    print(f"  prices: {n} of {len(ticks)} securities; without prices: {bad or 'none'}")
    if bad: print(f"  WARNING: {len(bad)} securities have NO fresh price ({', '.join(bad)}). The check below uses their older prices: a match or a miss today may be wrong. Run the daily check again in 30 minutes.")
    _prices.bad = bad; return n


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
    """the next k sessions after `day`: weekdays that are not NYSE holidays (HOLIDAYS, 2026-2027)"""
    out = []; d = day
    while len(out) < k:
        d = d + pd.Timedelta(days=1)
        if d.weekday() < 5 and d.normalize() not in HOLIDAYS: out.append(d)
    return out


def _way(ticker: str, hedged: bool, scale: float = 1.0, why: str = "") -> dict:
    """the founder's way to trade a match (TRACK 3.121): buy the inverse single-stock fund with cash where one exists (the 1x fund first); where none exists, sell the stock short with US$35,000.
    Where the rule also buys the S&P 500 fund, the same exposure is bought of it; with a fund the US$70,000 cash is split so that nothing is borrowed."""
    A = 70_000.0; f = None
    if scale <= 0: return dict(kind="none", money=0.0, spy=0.0, text=f"NO TRADE: {why}", short_text="no trade")
    try:
        C = pd.read_csv(STUDY / "funds_check.csv"); C = C[C.ok.astype(bool) & (C.stated < 0) & (C.stock == ticker)]
        if len(C): c = C.assign(k=(C.stated + 1).abs()).sort_values("k").iloc[0]; f = (str(c.fund), abs(float(c.stated)))
    except Exception: pass
    less = f" (reduced: {why})" if scale < 1 and why else ""
    if f is None:
        sm = SHORT_MONEY * scale
        return dict(kind="short", money=sm, spy=sm if hedged else 0.0, text=f"sell {ticker} short with US${sm:,.0f} (it has no inverse fund)" + (f" and buy the S&P 500 fund with US${sm:,.0f}" if hedged else "") + less, short_text=f"sell {ticker} short, US${sm:,.0f}")
    fund, k = f; m = (A / k if not hedged else A / (1 + k)) * scale
    return dict(kind="fund", fund=fund, mult=k, money=m, spy=k * m if hedged else 0.0, text=f"buy the inverse fund {fund} ({k:g}x) with US${m:,.0f}" + (f" and the S&P 500 fund with US${k * m:,.0f}" if hedged else "") + "; no short sale, nothing borrowed" + less, short_text=f"buy {fund}, US${m:,.0f}")


def _plan(F: pd.DataFrame, hedged_of: dict) -> dict:
    """for every match and each of the four ways: the share of its full size that is traded (0 = no trade) and why. Matches are taken in the order of their entry
    (the open after the sell-off), then by stock name; a position is open from its entry to its exit."""
    rows = []
    for k, r in F.iterrows():
        ns = _next_sessions(pd.Timestamp(r.day), int(r.exit_sessions)); ent = ns[0] + pd.Timedelta(hours=9, minutes=30); ex = ns[-1] + pd.Timedelta(hours=13 if ns[-1].normalize() in EARLY else 16); w = _way(r.ticker, hedged_of.get(r.code, False))
        rows.append(dict(k=k, ticker=r.ticker, ent=ent, ex=ex, kind=w["kind"], money=w["money"], spy=w["spy"]))
    rows.sort(key=lambda x: (x["ent"], x["ticker"], x["k"])); out = {x["k"]: {} for x in rows}
    for v in WAYS:
        held = []      # positions taken under this way: (ticker, kind, money, spy, exit)
        for x in rows:
            op = [h for h in held if h[4] > x["ent"]]; scale = 1.0; why = ""
            if v in ("A", "C") and any(h[0] == x["ticker"] for h in op): scale, why = 0.0, f"a position in {x['ticker']} is still open"
            if scale > 0 and v in ("B", "C"):
                used = sum(h[2] + h[3] for h in op); short = sum(h[2] for h in op if h[1] == "short"); room = (CAP_ALL - used) / (x["money"] + x["spy"]); why_b = f"the account already holds US${used:,.0f} of its US${CAP_ALL:,.0f}"
                if x["kind"] == "short" and (CAP_SHORT - short) / x["money"] < room: room = (CAP_SHORT - short) / x["money"]; why_b = f"US${short:,.0f} is already sold short, the limit is US${CAP_SHORT:,.0f}"
                if room < 1: scale, why = max(0.0, room), why_b
                if scale * x["money"] < MIN_TRADE: scale = 0.0
            if scale > 0: held.append((x["ticker"], x["kind"], x["money"] * scale, x["spy"] * scale, x["ex"]))
            out[x["k"]][v] = (scale, why, x["money"] * scale)
    return out



def _way_usd(w: dict, pin, pout, sin, sout, d_in, d_out, nights, RC):
    """the result of one finished trade done the founder's way, in US dollars after cost; None when the fund's prices cannot be had"""
    if w["kind"] == "short":
        fee, amt = RC.round_trip(pin, pout, w["money"], short=True); usd = -amt * (pout / pin - 1) - fee - HS["stock"] / 1e4 * amt - RC.short_carry(amt, nights)
    else:
        try:
            import yfinance as yf
            d = yf.download(w["fund"], start=f"{d_in - pd.Timedelta(days=7):%Y-%m-%d}", interval="1d", progress=False, auto_adjust=True)
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            d.index = pd.DatetimeIndex(d.index).tz_localize(None); fin, fout = float(d.Open.loc[d_in]), float(d.Close.loc[d_out])
        except Exception: return None
        fee, amt = RC.round_trip(fin, fout, w["money"], short=False); usd = amt * (fout / fin - 1) - fee - HS["fund1" if w["mult"] < 1.75 else "fund2"] / 1e4 * amt
    if w["spy"]: fee2, a2 = RC.round_trip(sin, sout, w["spy"], short=False); usd += a2 * (sout / sin - 1) - fee2 - HS["spy"] / 1e4 * a2
    return float(usd)


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
    F["day"] = pd.to_datetime(F["day"]); F[["entry_day", "exit_day", "way"]] = F[["entry_day", "exit_day", "way"]].astype(object); hedged_of = {r["code"]: not r["passed_alone"] for r in R}
    plan = _plan(F, hedged_of)
    for k, r in F.iterrows():
        for v in WAYS: F.at[k, f"size_{v}"] = round(plan[k][v][2], 0)
        F.at[k, "way"] = _way(r.ticker, hedged_of.get(r.code, False), plan[k][SHOWN][0], plan[k][SHOWN][1])["text"]
    for k, r in F.iterrows():      # what followed: sold at the next open, closed at the rule's exit, the founder's real cost
        d = P.get(r.ticker)
        if d is None or r.day not in d.index or r.day not in spy.index or (pd.notna(r.alone_bp) and pd.notna(r.usd_D)): continue
        i = d.index.get_loc(r.day); j = spy.index.get_loc(r.day); h = int(r.exit_sessions)
        if i + h >= len(d) or j + h >= len(spy): continue
        sign = -1.0 if r.side == "SELL" else 1.0; pin, pout = float(d.open.iloc[i + 1]), float(d.close.iloc[i + h]); sin, sout = float(spy.open.iloc[j + 1]), float(spy.close.iloc[j + h]); nights = (d.index[i + h] - d.index[i + 1]).days; A = RC.ACCOUNT; SSb = RC.SPREAD_BP["stock"] / 1e4
        fee, amt = RC.round_trip(pin, pout, A, short=sign < 0); alone = sign * amt * (pout / pin - 1) - fee - 2 * SSb * amt - (RC.short_carry(amt, nights) if sign < 0 else 0.0)
        fee2, amt2 = RC.round_trip(sin, sout, A, short=sign > 0); hedge = -sign * amt2 * (sout / sin - 1) - fee2 - 2 * SSb * amt2 - (RC.short_carry(amt2, nights) if sign > 0 else 0.0)
        wu = _way_usd(_way(r.ticker, hedged_of.get(r.code, False)), pin, pout, sin, sout, d.index[i + 1], d.index[i + h], nights, RC); F.at[k, "way_usd"] = np.nan if wu is None else round(wu * plan[k][SHOWN][0], 0)
        for v in WAYS: F.at[k, f"usd_{v}"] = np.nan if wu is None else round(wu * plan[k][v][0], 0)      # a smaller position: the same result in proportion (the fixed fee of about US$2 is ignored)
        F.at[k, "entry_day"] = f"{d.index[i + 1]:%Y-%m-%d}"; F.at[k, "exit_day"] = f"{d.index[i + h]:%Y-%m-%d}"; F.at[k, "alone_bp"] = round(alone / A * 1e4, 1); F.at[k, "against_spx_bp"] = round((alone + hedge) / A * 1e4, 1); F.at[k, "stock_move_bp"] = round((pout / pin - 1) * 1e4, 1); F.at[k, "spx_move_bp"] = round((sout / sin - 1) * 1e4, 1)
    F = F[COLS].sort_values(["day", "code", "ticker"]).reset_index(drop=True); FWD.parent.mkdir(parents=True, exist_ok=True); tmp = FWD.with_suffix(".tmp"); F.to_csv(tmp, index=False); os.replace(tmp, FWD)
    # ---- the tally, per rule: each day counts once
    tally = {}; L = ["# Sell-off rules SS-2a, SS-2b, SS-2c: the forward record", "", f"Registered in TRACK 3.110 (24 Nov 2026) before any case. Every sell-off of 5% or more of the list from {start:%d %b %Y} is tested against the rules as frozen in `docs/selloff_rules.json`. A match is sold at the next open and closed at the rule's exit; "
         f"cost: the founder's fees, 2 basis points of spread per order, 4.8% a year on the short position; account US${70000:,}. Each day counts once per rule. **Verdict per rule at {VERDICT_AT} separate days.** The two bp columns are the registered measure (the stock sold short with the whole account). **'The founder's way' (decided 25 Nov 2026, TRACK 3.121) is how a match is really traded: the inverse fund bought with cash where one exists, otherwise the stock sold short with US$35,000; its result is in US dollars after cost.** The history numbers are flattered (the rules were chosen on those years); this record is the first clean evidence.", "",
         "| rule | trade that passed the test | history 2018-2026, per day with a trade | days so far with a known result | average so far, the stock alone | against the S&P 500 | waiting for their sessions |", "|---|---|---|---|---|---|---|"]
    for r in R:
        G = F[F.code == r["code"]]; K = G[G.alone_bp.notna()]; bd = K.groupby("day")[["alone_bp", "against_spx_bp"]].mean(); main = "against_spx" if not r["passed_alone"] else "alone"
        tally[r["code"]] = dict(days=int(len(bd)), alone=float(bd.alone_bp.mean()) if len(bd) else None, against_spx=float(bd.against_spx_bp.mean()) if len(bd) else None, waiting=int(G.alone_bp.isna().sum()), main=main)
        L.append(f"| {r['code']} | {'sell the stock' if r['passed_alone'] else 'sell the stock and buy the S&P 500 fund'}; exit +{r['exit']} | {r['history']['alone_bp' if r['passed_alone'] else 'against_spx_bp']:+.0f} bp ({r['history']['days']} days) | {len(bd)} of {VERDICT_AT} | {'' if not len(bd) else format(bd.alone_bp.mean(), '+.0f') + ' bp'} | {'' if not len(bd) else format(bd.against_spx_bp.mean(), '+.0f') + ' bp'} | {int(G.alone_bp.isna().sum())} |")
    f0 = lambda x: "" if pd.isna(x) else f"{x:+.0f}"
    L += ["", "| sell-off day | rule | stock | move that day % | sold at the open of | closed at the close of | the stock alone, bp after cost | against the S&P 500, bp after cost | the founder's way | its result, US$ |", "|---|---|---|---|---|---|---|---|---|---|"] + [f"| {x.day:%Y-%m-%d} | {x.code} | {x.ticker} | {f0(x.move_pct) if pd.isna(x.move_pct) else format(x.move_pct, '+.1f')} | {x.entry_day if isinstance(x.entry_day, str) else ''} | {x.exit_day if isinstance(x.exit_day, str) else ''} | {f0(x.alone_bp)} | {f0(x.against_spx_bp)} | {x.way if isinstance(x.way, str) else ''} | {'' if pd.isna(x.way_usd) else format(x.way_usd, '+,.0f')} |" for x in F.sort_values("day", ascending=False).itertuples()]
    if not len(F): L.append("| (no match yet) | | | | | | | | | |")
    if missing: L += ["", "Not checkable at the last run (an input was missing for the new days): " + "; ".join(f"{k}: {', '.join(sorted(set(v)))[:120]}" for k, v in missing.items()) + "."]
    stale = list(getattr(_prices, "bad", []) or [])
    if stale: L += ["", f"**Warning, last run:** Yahoo gave no fresh price for {', '.join(stale)}; a match or a miss of that run may be wrong until the check is run again."]
    m0 = lambda x: "" if pd.isna(x) else ("no trade" if x == 0 else f"{x:,.0f}"); u0 = lambda x: "" if pd.isna(x) else f"{x:+,.0f}"
    L += ["", "## When signals overlap: the four ways side by side (founder, 26 Nov 2026)", "", "; ".join(f"**{v}** = {t}" for v, t in WAYS.items()) + f". Limits of B and C: at most US${CAP_SHORT:,.0f} sold short in all, at most US${CAP_ALL:,.0f} in all positions together; a signal that would get under US${MIN_TRADE:,.0f} is not traded. "
          f"Sizes are the money in the fund or the short sale; results in US dollars after cost. **The page shows way {SHOWN}.**", "", "| sell-off day | rule | stock | size A | size B | size C | size D | result A | result B | result C | result D |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    L += [f"| {x.day:%Y-%m-%d} | {x.code} | {x.ticker} | {m0(x.size_A)} | {m0(x.size_B)} | {m0(x.size_C)} | {m0(x.size_D)} | {u0(x.usd_A)} | {u0(x.usd_B)} | {u0(x.usd_C)} | {u0(x.usd_D)} |" for x in F.sort_values("day", ascending=False).itertuples()]
    K = F[F.usd_D.notna()]
    if len(K): L.append("| **total of the finished trades** | | | | | | | " + " | ".join(f"**{K[f'usd_{v}'].sum():+,.0f}**" for v in WAYS) + " |")
    Path("docs").mkdir(exist_ok=True); Path("docs/selloff_rules_forward.md").write_text("\n".join(L) + "\n")
    # ---- what the block shows
    plan2 = _plan(F, hedged_of); shown = {(x.code, x.ticker, pd.Timestamp(x.day)): _way(x.ticker, hedged_of.get(x.code, False), plan2[k][SHOWN][0], plan2[k][SHOWN][1]) for k, x in F.iterrows()}
    sigs = []
    for r in R:
        for q in np.flatnonzero(r["_mask"] & new):
            b = B.iloc[q]; ns = _next_sessions(b.day, int(r["exit"])); ent = datetime.combine(ns[0].date(), datetime.min.time(), NY).replace(hour=9, minute=30); ex = datetime.combine(ns[-1].date(), datetime.min.time(), NY).replace(hour=13 if ns[-1].normalize() in EARLY else 16)
            if now <= ex + timedelta(hours=24): sigs.append(dict(code=r["code"], ticker=b.ticker, day=f"{b.day:%Y-%m-%d}", move_pct=round(float(b["last day's move %"]), 1) if "last day's move %" in B.columns else None, side=r["side"], hedged=not r["passed_alone"], way=shown.get((r["code"], b.ticker, pd.Timestamp(b.day)), _way(b.ticker, not r["passed_alone"]))["text"], way_short=shown.get((r["code"], b.ticker, pd.Timestamp(b.day)), _way(b.ticker, not r["passed_alone"]))["short_text"], entry_at=ent.isoformat(), exit_at=ex.isoformat(), exit_sessions=int(r["exit"]),
                                                             history_bp=r["history"]["alone_bp" if r["passed_alone"] else "against_spx_bp"], history_days=r["history"]["days"]))
    falls = B[(B.day == last)]; card = dict(checked=datetime.now(NY).isoformat(), last_close=f"{last:%Y-%m-%d}", falls_last_close=[dict(ticker=x.ticker, move_pct=round(float(x["last day's move %"]), 1)) for _, x in falls.iterrows()] if "last day's move %" in B.columns else [], signals=sigs, tally=tally,
                                              rules=[dict(code=r["code"], when=r["when"], exit=r["exit"], hedged=not r["passed_alone"], history_bp=r["history"]["alone_bp" if r["passed_alone"] else "against_spx_bp"], history_days=r["history"]["days"], per_year=r["history"]["per_year"]) for r in R], not_checkable=missing, stale=stale)
    CARD.parent.mkdir(parents=True, exist_ok=True); tmp = CARD.with_suffix(".tmp"); tmp.write_text(json.dumps(card, indent=1, default=float)); os.replace(tmp, CARD)
    print(f"  last finished session {last:%Y-%m-%d}: {len(falls)} sell-offs of 5% or more in the list" + (f" ({', '.join(falls.ticker)})" if len(falls) else "") + f"; matches of a rule since {start:%d %b}: {len(F)} ({len(rows)} new now)")
    for x in F[F.day >= last - pd.Timedelta(days=7)].itertuples(): print(f"  MATCH {x.code}: {x.ticker} closed {x.move_pct:+.1f}% on {x.day:%Y-%m-%d} -> way {SHOWN} (on the page): {x.way}" + ("" if pd.isna(x.way_usd) else f"; result US${x.way_usd:+,.0f}") + " | sizes A/B/C/D: " + "/".join("no trade" if getattr(x, f"size_{v}") == 0 else f"{getattr(x, f'size_{v}'):,.0f}" for v in WAYS))
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


def _other_calls(ticker: str, side: str, exit_sessions: int) -> str:
    """Founder, 26 Nov 2026 (TRACK 3.132): when another part of the product says the opposite about the same stock, the block must say so and explain it.
    The market-condition models (processed/forward_ledger.csv) list assets to hold for 5 to 20 sessions; a sell-off rule is about the 2 or 3 sessions after a severe fall."""
    try:
        T = pd.read_csv("processed/forward_ledger.csv", dtype=str); T = T[T.status.fillna("") == "pending"]; T = T[pd.to_datetime(T.entry_date, errors="coerce") >= pd.Timestamp.now().normalize() - pd.Timedelta(days=30)]
    except Exception: return ""
    opp = "longs" if side == "SELL" else "shorts"; same = "shorts" if side == "SELL" else "longs"; hit = []; agree = []
    for r in T.itertuples():
        if ticker in str(getattr(r, opp, "")).split("|"): hit.append((r.signal_date, int(float(r.horizon))))
        if ticker in str(getattr(r, same, "")).split("|"): agree.append((r.signal_date, int(float(r.horizon))))
    if not hit: return ""
    hs = sorted({h for _, h in hit}); word = "BUY" if side == "SELL" else "SELL"; mine = "sells" if side == "SELL" else "buys"
    return (f"<p><b>Opposite call elsewhere in this product:</b> {len(hit)} market-condition model{'s' if len(hit) > 1 else ''} (signal of {max(d for d, _ in hit)}) list{'' if len(hit) > 1 else 's'} <b>{ticker}</b> among {'their' if len(hit) > 1 else 'its'} {word} names, to be held {', '.join(str(h) for h in hs)} sessions. "
            f"This rule {mine} it for {exit_sessions} sessions. They answer different questions: the models rank assets over weeks from the market condition; this rule is only about the first sessions after a severe fall. "
            "Both can be right at once (down for two days, up over three weeks) and both can be wrong: neither has finished its forward test." + (f" {len(agree)} model{'s' if len(agree) > 1 else ''} list{'' if len(agree) > 1 else 's'} it on the same side as this rule." if agree else "") + "</p>")


# ------------------------------------------------------------------ the block on the page
def card_html() -> str:
    from src.selloff_forward import CARD_CSS
    css = CARD_CSS + "<style>.sso-red{outline:1px solid #C0392B;background:linear-gradient(135deg,rgba(255,236,233,.97),rgba(255,222,217,.92))}.sso-yel{outline:1px solid #B7791F;background:linear-gradient(135deg,rgba(255,249,235,.97),rgba(255,241,214,.92))}.sso-grn{outline:1px solid #178A4C;background:linear-gradient(135deg,rgba(236,248,241,.97),rgba(222,243,231,.92))}</style>"
    if not CARD.exists(): return css + "<div class='sso-wrap'><details class='sso'><summary><span class='sso-t'>Severe Sell-off</span><span class='sso-s sso-m'>Not checked yet: run the daily check once.</span></summary></details></div>"
    try: C = json.loads(CARD.read_text())
    except Exception: return ""
    now = datetime.now(NY); S = [dict(s, stage=_stage(s, now)) for s in C.get("signals", [])]; S = [s for s in S if s["stage"]]; order = {"red": 0, "yellow": 1, "green": 2}; S.sort(key=lambda s: (order[s["stage"]], s.get("way_short") == "no trade")); chk = datetime.fromisoformat(C["checked"]); old = (now - chk).total_seconds() > 30 * 3600
    word = {"red": "TRADE NOW", "yellow": "best entry time passed", "green": "trading time over"}; cls = {"red": "sso-red", "yellow": "sso-yel", "green": "sso-grn"}.get(S[0]["stage"], "") if S else ""
    if S: status = "<b>" + ", ".join(f"{s['ticker']} {s['move_pct']:+.1f}%" for s in S[:3]) + (f" +{len(S) - 3}" if len(S) > 3 else "") + "</b><br>" + (f"<b>{word[S[0]['stage']]}</b> · {S[0]['code']}: {S[0].get('way_short', 'sell at the next open')}" if S[0].get("way_short") != "no trade" else f"{S[0]['code']} met, <b>no trade</b> (overlap rule {SHOWN})")
    else: fl = C.get("falls_last_close", []); status = ("No rule met at the last close." if not fl else f"{len(fl)} fell 5%+ at the last close; no rule met.") + (f"<br><span class='sso-m'>checked {chk:%d %b %H:%M} New York</span>" if not old else "")
    if old: status += "<br><span class='sso-m'><b>Not checked since " + f"{chk:%d %b %H:%M}" + " New York — run the daily check.</b></span>"
    d = []
    for s in S:
        ent = datetime.fromisoformat(s["entry_at"]); ex = datetime.fromisoformat(s["exit_at"]); d.append(f"<p><b>{s['ticker']}</b> closed {s['move_pct']:+.1f}% on {s['day']} and meets <b>{s['code']}</b> — " + (f"<b>{s['way']}</b> (overlap rule {SHOWN}; entry would have been the open of {ent:%a %d %b})" if str(s.get("way", "")).startswith("NO TRADE") else f"<b>{word[s['stage']]}</b>. Trade: " + (s["way"] if s.get("way") else "sell the stock" + (" and buy the S&P 500 fund" if s["hedged"] else "")) + f" at the open of {ent:%a %d %b}; close it at the close of {ex:%a %d %b}" + (" (the market closes at 13:00 New York that day)" if ex.hour == 13 else "")) + f". History 2018–2026: {s['history_bp']:+.0f} basis points per day with a trade, after cost ({s['history_days']} days).</p>" + _other_calls(s["ticker"], s.get("side", "SELL"), int(s.get("exit_sessions", 2))))
    for r in C.get("rules", []):
        tl = (C.get("tally") or {}).get(r["code"], {}); d.append(f"<p><b>{r['code']}</b> — a stock of the list closes 5% or more down AND {' AND '.join(r['when'])}. Exit: the close {r['exit']} sessions after. History: {r['history_bp']:+.0f} bp after cost, about {r['per_year']:.0f} days a year. Forward record: {tl.get('days', 0)} of {VERDICT_AT} days" + (f", average {tl[tl['main']]:+.0f} bp" if tl.get("days") else "") + ".</p>")
    if C.get("stale"): d.append("<p><b>Warning:</b> at the last check Yahoo gave no fresh price for " + ", ".join(C["stale"]) + "; run the daily check again.</p>")
    if C.get("not_checkable"): d.append("<p><b>Not checkable at the last run:</b> " + ", ".join(C["not_checkable"]) + " (an input was missing).</p>")
    d.append(f"<p class='sso-m'>Overlapping signals follow way {SHOWN}: {WAYS[SHOWN]} (at most US${CAP_SHORT:,.0f} sold short in all, US${CAP_ALL:,.0f} in all positions). The other three ways are recorded beside it in the forward record.</p>")
    d.append("<p class='sso-m'>Rules passed a test on 2005–2026 with the real trading cost; those numbers are flattered because the rules were chosen on the same years. The verdict comes from the forward record at 30 days each. Colours: red = trade now · yellow = best entry passed · green = over.</p>")
    d.append(f"<p class='sso-m'>Last finished session {C.get('last_close')} · checked {chk:%d %b %H:%M} New York · daily prices from Yahoo, filings from the SEC, indices from FRED</p>")
    return css + f"<div class='sso-wrap'><details class='sso {cls}'><summary><span class='sso-t'>Severe Sell-off</span><span class='sso-more'>details ▾</span><span class='sso-s'>{status}</span></summary><div class='sso-d'>{''.join(d)}</div></details></div>"


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["daily", "check"]); a = ap.parse_args()
    cmd_daily() if a.cmd == "daily" else check()
