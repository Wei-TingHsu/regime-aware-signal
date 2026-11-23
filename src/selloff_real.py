"""selloff_real.py -- test SO-T2 (registered in TRACK 3.104 before it runs): the strong sell-off patterns again, with the founder's REAL cost and
account size, and traded through the stock's LEVERAGED / INVERSE single-stock funds.

Founder, 22 Nov 2026: (1) replace the round cost of 30 basis points by my broker's real fees (src/real_cost.py), on an account kept at US$70,000;
(2) test the same trades made with the stock's 2x long / short exchange-traded funds instead of the stock, for the stocks that have one.

PART 1 -- real cost. The 24 candidate patterns of the machine search, the same sell-offs and the same trade as SO-T (enter at the next open, exit at
the close of the pattern's own horizon), but: each day's US$70,000 is split equally over that day's signals; whole shares at the real share price of
that day; fees of the fee board on every order; plus an allowance for the spread (2 basis points per order for shares -- an assumption).
Two versions side by side: the stock ALONE, and the stock AGAINST the S&P 500 fund (a second pair of orders of the same size).
PART 2 -- the funds. For every signal whose stock had a suitable fund trading that day (expected lower -> BUY the inverse fund, 2x if there is one,
else 1x; expected higher -> BUY the 2x long fund): the same US$70,000 in the fund, real fund prices, fees, 10 basis points per order for the spread,
beside the stock trade on exactly the same signals. A fund is used only if its measured daily move against the stock matches what its issuer states.

    python -m src.selloff_real fetch     # free download (Yahoo): real share prices with splits undone, and the funds' prices -> data_provenance/selloff/realpx, docs/selloff_funds.md
    python -m src.selloff_real run       # no download -> docs/selloff_real.md, .json
"""
from __future__ import annotations
import argparse, json, re, time
import numpy as np, pandas as pd
from src import selloff_search as S
from src import real_cost as RC
from src.selloff_study import ROOT, DOCS, _px, _stocks

RP = ROOT / "realpx"; EXITS = [1, 2, 3, 5]; NBOOT = 5000; GROUP = "stocks, one day -5% or worse"; CHECK = ROOT / "funds_check.csv"
# Single-stock funds, from the issuers' own lists read on 22 Nov 2026 (Direxion 'Single Stock ETFs List'; GraniteShares product guide; REX Shares 'T-REX leveraged ETFs').
# (fund, what the issuer states it does each day against the stock, issuer). Tradr's two funds are from memory, unverified -- the data check below decides.
FUNDS = {
    "AAPL": [("AAPU", 2, "Direxion"), ("AAPB", 2, "GraniteShares"), ("AAPX", 2, "T-REX"), ("AAPD", -1, "Direxion")],
    "ADBE": [("ADBU", 2, "Direxion")], "AMD": [("AMUU", 2, "Direxion"), ("AMDL", 2, "GraniteShares"), ("AMDD", -1, "Direxion")],
    "AMZN": [("AMZU", 2, "Direxion"), ("AMZZ", 2, "GraniteShares"), ("AMZD", -1, "Direxion")], "AVGO": [("AVL", 2, "Direxion"), ("AVGU", 2, "GraniteShares"), ("AVS", -1, "Direxion")],
    "BA": [("BOEU", 2, "Direxion")], "BRK-B": [("BRKU", 2, "Direxion")], "CSCO": [("CSCL", 2, "Direxion"), ("CSCS", -1, "Direxion")], "CRWD": [("CRWL", 2, "GraniteShares")], "LLY": [("ELIL", 2, "Direxion")],
    "GOOGL": [("GGLL", 2, "Direxion"), ("GGLS", -1, "Direxion"), ("GOU", 2, "GraniteShares"), ("GOOX", 2, "T-REX")], "GOOG": [("GOU", 2, "GraniteShares"), ("GOOX", 2, "T-REX"), ("GGLL", 2, "Direxion"), ("GGLS", -1, "Direxion")],
    "INTC": [("LINT", 2, "Direxion"), ("INTW", 2, "GraniteShares")], "LMT": [("LMTL", 2, "Direxion")], "META": [("METU", 2, "Direxion"), ("FBL", 2, "GraniteShares"), ("METD", -1, "Direxion")],
    "MSFT": [("MSFU", 2, "Direxion"), ("MSFL", 2, "GraniteShares"), ("MSFX", 2, "T-REX"), ("MSFD", -1, "Direxion")], "MU": [("MUU", 2, "Direxion"), ("MULL", 2, "GraniteShares"), ("MUD", -1, "Direxion")],
    "NFLX": [("NFXL", 2, "Direxion"), ("NFLU", 2, "T-REX"), ("NFXS", -1, "Direxion")], "NVDA": [("NVDL", 2, "GraniteShares"), ("NVDU", 2, "Direxion"), ("NVDX", 2, "T-REX"), ("NVD", -2, "GraniteShares"), ("NVDQ", -2, "T-REX"), ("NVDD", -1, "Direxion"), ("NVDS", -1.5, "Tradr (unverified)")],
    "ORCL": [("ORCU", 2, "Direxion"), ("ORCS", -1, "Direxion")], "PLTR": [("PLTU", 2, "Direxion"), ("PLTD", -1, "Direxion")], "PYPL": [("PYPU", 2, "Direxion")], "QCOM": [("QCMU", 2, "Direxion"), ("QCML", 2, "GraniteShares"), ("QCMD", -1, "Direxion")],
    "TSLA": [("TSLL", 2, "Direxion"), ("TSLR", 2, "GraniteShares"), ("TSLT", 2, "T-REX"), ("TSDD", -2, "GraniteShares"), ("TSLZ", -2, "T-REX"), ("TSLQ", -2, "Tradr (unverified)"), ("TSLS", -1, "Direxion")],
    "TSM": [("TSMX", 2, "Direxion"), ("TSMU", 2, "GraniteShares"), ("TSMZ", -1, "Direxion")], "TXN": [("TXNU", 2, "Direxion")], "UNH": [("UNHU", 2, "Direxion")], "XOM": [("XOMX", 2, "Direxion")], "SNDK": [("SNDU", 2, "T-REX")],
}


def _store(t: str, d: pd.DataFrame):
    """d: Yahoo's daily table with auto_adjust=False (Open, Close, Adj Close, Stock Splits). Saves the adjusted open and close (for returns) and the REAL prices of the day
    (splits undone -- Yahoo's 'Close' is already divided by later splits), which the fee per share needs."""
    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
    d = d.dropna(subset=["Close"]); d.index = pd.DatetimeIndex(d.index).tz_localize(None)
    if len(d) < 5: return False
    sp = d["Stock Splits"].replace(0, 1.0).fillna(1.0) if "Stock Splits" in d.columns else pd.Series(1.0, index=d.index); later = sp[::-1].cumprod()[::-1].shift(-1).fillna(1.0)      # the product of the splits AFTER each day
    adj = (d["Adj Close"] / d["Close"]) if "Adj Close" in d.columns else 1.0
    out = pd.DataFrame(dict(open=d["Open"] * adj, close=d["Close"] * adj, raw_open=d["Open"] * later, raw_close=d["Close"] * later)); RP.mkdir(parents=True, exist_ok=True); out.to_parquet(RP / f"{t}.parquet"); return True


def cmd_fetch():
    import yfinance as yf
    stocks = _stocks(); funds = sorted({f for t in stocks for f, _, _ in FUNDS.get(t, [])}); ticks = stocks + ["SPY"] + funds; n = 0; bad = []
    for t in ticks:
        if (RP / f"{t}.parquet").exists() and time.time() - (RP / f"{t}.parquet").stat().st_mtime < 20 * 3600: continue
        try:
            d = yf.download(t, start="1998-01-01", interval="1d", auto_adjust=False, actions=True, progress=False)
            if d is None or not len(d) or not _store(t, d): bad.append(t); continue
            n += 1
        except Exception: bad.append(t)
    print(f"  {len(ticks)} securities ({len(stocks)} stocks, the S&P 500 fund, {len(funds)} single-stock funds); {n} downloaded now; without prices: {bad or 'none'}. No cost. -> {RP}")
    _check(stocks)


def _check(stocks):
    """every fund against its stock: does it move as its issuer states?"""
    rows = []
    for t in stocks:
        for f, mult, issuer in FUNDS.get(t, []):
            if not (RP / f"{f}.parquet").exists() or not (RP / f"{t}.parquet").exists(): rows.append(dict(stock=t, fund=f, issuer=issuer, stated=mult, measured=np.nan, first_day="", sessions=0, ok=False, why="no prices")); continue
            a = pd.read_parquet(RP / f"{f}.parquet").close.pct_change(); b = pd.read_parquet(RP / f"{t}.parquet").close.pct_change(); X = pd.concat([a, b], axis=1, keys=["f", "s"]).dropna()
            if len(X) < 20: rows.append(dict(stock=t, fund=f, issuer=issuer, stated=mult, measured=np.nan, first_day=f"{X.index.min():%Y-%m-%d}" if len(X) else "", sessions=len(X), ok=False, why="under 20 sessions")); continue
            slope = float(np.cov(X.f, X.s)[0, 1] / X.s.var()); good = abs(slope - mult) <= 0.35; rows.append(dict(stock=t, fund=f, issuer=issuer, stated=mult, measured=round(slope, 2), first_day=f"{X.index.min():%Y-%m-%d}", sessions=len(X), ok=bool(good), why="" if good else "does not move as stated"))
    C = pd.DataFrame(rows); C.to_csv(CHECK, index=False); ok = C[C.ok] if len(C) else C
    L = ["# Single-stock leveraged and inverse funds for the stocks of the list", "", "Funds named on the issuers' own lists (Direxion, GraniteShares, REX Shares T-REX; read 22 Nov 2026; two Tradr funds from memory, marked unverified). "
         "'Measured' = how much the fund moved per 1% move of the stock on the same day, over its whole life (Yahoo daily prices). A fund is used by the test only if measured is within 0.35 of what the issuer states.", "",
         f"**{len(stocks)} stocks in the list; {ok.stock.nunique() if len(ok) else 0} have at least one usable fund; {ok[ok.stated > 0].stock.nunique() if len(ok) else 0} have a 2x LONG fund; {ok[ok.stated < 0].stock.nunique() if len(ok) else 0} have an INVERSE fund; {ok[ok.stated <= -1.5].stock.nunique() if len(ok) else 0} have an inverse fund of 1.5x or 2x.**", "",
         "| stock | fund | issuer | issuer states (daily) | measured | first day with prices | sessions | used |", "|---|---|---|---|---|---|---|---|"]
    L += [f"| {r.stock} | {r.fund} | {r.issuer} | {r.stated:+g}x | {'' if pd.isna(r.measured) else f'{r.measured:+.2f}x'} | {r.first_day} | {r.sessions} | {'yes' if r.ok else 'NO: ' + r.why} |" for r in C.itertuples()]
    none = [t for t in stocks if t not in set(C.stock)] if len(C) else stocks; L += ["", f"Stocks of the list with no fund on those lists ({len(none)}): {', '.join(none)}."]
    DOCS.mkdir(exist_ok=True); (DOCS / "selloff_funds.md").write_text("\n".join(L) + "\n"); print(L[4].replace("**", "  "))
    if len(ok): print("  inverse funds usable: " + ", ".join(f"{r.stock}: {r.fund} ({r.measured:+.2f}x, from {r.first_day})" for r in ok[ok.stated < 0].itertuples()))
    if len(C[~C.ok]): print("  NOT usable: " + ", ".join(f"{r.fund} ({r.why})" for r in C[~C.ok].itertuples()))
    print("-> docs/selloff_funds.md")


def _boot(day_vals: pd.Series, rng) -> float:
    m = day_vals.index.year * 12 + day_vals.index.month; g = day_vals.groupby(m); sums = g.sum().to_numpy(); cnt = g.size().to_numpy(); k = len(sums)
    if k < 6: return float("nan")
    pick = rng.integers(0, k, size=(NBOOT, k)); return float(((sums[pick].sum(1) / cnt[pick].sum(1)) <= 0).mean())


def cmd_run(everything=False):
    J = json.loads((DOCS / "selloff_search.json").read_text())[GROUP]; pats = [p for p in J["patterns"] if everything or p.get("candidate")]
    if not pats: raise SystemExit("no candidate pattern in docs/selloff_search.json")
    if not CHECK.exists(): raise SystemExit("run `python -m src.selloff_real fetch` first")
    E = pd.read_csv(ROOT / "events.csv", parse_dates=["day"]); E["event_id"] = E.index; P = _px(); unit, dfn = S.BASES[GROUP]; rng = np.random.default_rng(S.SEED)
    B = E[(E.unit == unit) & (E.definition == dfn)].sort_values("day").reset_index(drop=True); Y, _, _ = S._outcomes(B, P); ok = np.isfinite(Y).all(axis=1); B = B[ok].reset_index(drop=True)
    disc = (B.day < S.SPLIT).to_numpy(); items = S._items(B, disc, rng); by_label = {it[2]: it[3] for it in items}; n = len(B); spy = P["SPY"]
    R = {f.stem: pd.read_parquet(f) for f in RP.glob("*.parquet")}; C = pd.read_csv(CHECK); C = C[C.ok]; fmap = {t: [(r.fund, float(r.stated)) for r in g.itertuples()] for t, g in C.groupby("stock")}
    # ---- per sell-off and exit: the stock's and the S&P fund's return from the next open, and the REAL prices of the two days (for the number of shares)
    ret = {h: np.full(n, np.nan) for h in EXITS}; rspy = {h: np.full(n, np.nan) for h in EXITS}; pin = np.full(n, np.nan); pout = {h: np.full(n, np.nan) for h in EXITS}; sin = np.full(n, np.nan); sout = {h: np.full(n, np.nan) for h in EXITS}; d_in = [None] * n; d_out = {h: [None] * n for h in EXITS}; noraw = 0
    for q, r in enumerate(B.itertuples()):
        d = P[r.ticker]; c, o = d.close, d.open; i = int(r.i); js = spy.index.get_loc(r.day); rw = R.get(r.ticker); rs = R.get("SPY"); d_in[q] = c.index[i + 1]
        pin[q] = float(rw.raw_open.get(d_in[q], np.nan)) if rw is not None else np.nan; sin[q] = float(rs.raw_open.get(spy.index[js + 1], np.nan)) if rs is not None else np.nan
        if not pin[q] > 0: pin[q] = float(o.iloc[i + 1]); noraw += 1
        if not sin[q] > 0: sin[q] = float(spy.open.iloc[js + 1])
        for h in EXITS:
            ret[h][q] = c.iloc[i + h] / o.iloc[i + 1] - 1; rspy[h][q] = spy.close.iloc[js + h] / spy.open.iloc[js + 1] - 1; d_out[h][q] = c.index[i + h]; pout[h][q] = pin[q] * (1 + ret[h][q]); sout[h][q] = sin[q] * (1 + rspy[h][q])
    # TRACK 3.108: a fund's price on Yahoo can be plainly wrong around a split (MUD, 3 Mar 2026: 381.6 -> 37.8 in two sessions while the stock moved +0.9%). A day is marked BAD for a fund when its
    # close-to-close move differs from (its multiple x the stock's move) by more than 30 percentage points -- no real fund does that -- and a trade that touches a bad day is left out, for the fund AND for the comparison.
    BAD = {}
    for c in C.itertuples():
        Fd, Sd = R.get(c.fund), R.get(c.stock)
        if Fd is None or Sd is None: continue
        X = pd.concat([Fd.close.pct_change(), Sd.close.pct_change()], axis=1, keys=["f", "s"], sort=True).dropna(); BAD[c.fund] = set(X.index[(X.f - float(c.stated) * X.s).abs() > 0.30])
    nbad = sum(len(v) for v in BAD.values())
    def funds_for(q, h, sign):
        """every usable fund to BUY for this signal (inverse when the stock is expected lower, long when expected higher) with prices on both days: (fund, multiple, its return, its real price at entry); strongest first"""
        out = []
        for f, mult in sorted([x for x in fmap.get(B.ticker.iat[q], []) if (x[1] < 0) == (sign < 0)], key=lambda x: -abs(x[1])):
            F = R.get(f)
            if F is not None and d_in[q] in F.index and d_out[h][q] in F.index and not any(d_in[q] <= x <= d_out[h][q] for x in BAD.get(f, ())):
                a, b = float(F.open.loc[d_in[q]]), float(F.close.loc[d_out[h][q]]); ra = float(F.raw_open.loc[d_in[q]])
                if a > 0 and b > 0 and ra > 0: out.append((f, mult, b / a - 1, ra))
        return out
    def fund_for(q, h, sign): x = funds_for(q, h, sign); return x[0] if x else None
    def cheapest(mask, sign, h):
        """founder, 22 Nov: for the SAME exposure, take whichever way of trading costs least on that day. Ways: the stock itself (sold short when it is expected lower), or a fund
        bought with (exposure / the fund's multiple) -- half the money in a 2x fund gives the same exposure. Cost of a way = fees + the spread allowance + (for a short sale) the
        nightly charge. The fund's own running cost and daily reset are not a cost we pay separately: they are inside the fund's price and so inside the result."""
        idx = np.flatnonzero(mask); out = {}; used = {"stock": 0, "1x fund": 0, "2x fund": 0}; cost = {"stock": [], "1x fund": [], "2x fund": []}
        for day, qs in pd.Series(idx).groupby(B.day.to_numpy()[idx]) if len(idx) else []:
            qs = qs.to_numpy(); each = A / len(qs); pnl = 0.0
            for q in qs:
                nights = (d_out[h][q] - d_in[q]).days; fee, amt = RC.round_trip(pin[q], pout[h][q], each, short=sign < 0); c0 = fee + 2 * SS * amt + (RC.short_carry(amt, nights) if sign < 0 else 0.0); ways = [("stock", c0, sign * amt * ret[h][q] - c0)]; cost["stock"].append(c0 / each * 1e4)
                for f, mult, fr, ra in funds_for(q, h, sign):
                    fee, amt = RC.round_trip(ra, ra * (1 + fr), each / abs(mult), short=False); c = fee + 2 * SE * amt; k = "2x fund" if abs(mult) >= 1.5 else "1x fund"; ways.append((k, c, amt * fr - c)); cost[k].append(c / each * 1e4)
                w = min(ways, key=lambda x: x[1]); used[w[0]] += 1; pnl += w[2]
            out[pd.Timestamp(day)] = pnl / A * 1e4
        return pd.Series(out, dtype=float).sort_index(), used, {k: (float(np.mean(v)) if v else float("nan"), len(v)) for k, v in cost.items()}
    A = RC.ACCOUNT; SS, SE = RC.SPREAD_BP["stock"] / 1e4, RC.SPREAD_BP["etf"] / 1e4

    def days(mask, sign, h, kind):
        """one number per day, in basis points of the US$70,000 account, after fees and the spread allowance. kind: 'alone' / 'hedged' / 'fund' / 'alone_f' (the stock, on the signals that have a fund)."""
        idx = np.flatnonzero(mask)
        if kind in ("fund", "alone_f"): pick = {q: fund_for(q, h, sign) for q in idx}; idx = np.array([q for q in idx if pick[q] is not None], dtype=int)
        out = {}; mult_seen = []
        for day, qs in pd.Series(idx).groupby(B.day.to_numpy()[idx]) if len(idx) else []:
            qs = qs.to_numpy(); each = A / len(qs); pnl = 0.0
            for q in qs:
                if kind == "fund":
                    f, mult, fr, ra = pick[q]; fee, amt = RC.round_trip(ra, ra * (1 + fr), each, short=False); pnl += amt * fr - fee - 2 * SE * amt; mult_seen.append(mult)
                else:
                    nights = (d_out[h][q] - d_in[q]).days; fee, amt = RC.round_trip(pin[q], pout[h][q], each, short=sign < 0); pnl += sign * amt * ret[h][q] - fee - 2 * SS * amt - (RC.short_carry(amt, nights) if sign < 0 else 0.0)
                    if kind == "hedged": fee2, amt2 = RC.round_trip(sin[q], sout[h][q], each, short=sign > 0); pnl += -sign * amt2 * rspy[h][q] - fee2 - 2 * SS * amt2 - (RC.short_carry(amt2, nights) if sign > 0 else 0.0)
            out[pd.Timestamp(day)] = pnl / A * 1e4
        return pd.Series(out, dtype=float).sort_index(), mult_seen

    brng = np.random.default_rng(20261123); K = len(pats); bar = 0.05 / K; rows = []; years_new = max(1e-9, (B.day.max() - S.SPLIT).days / 365.25); f0 = lambda x: "n/a" if x != x else f"{x:+.0f}"
    def stat(s): return dict(days=int(len(s)), bp=float(s.mean()) if len(s) else float("nan"), win=float((s > 0).mean()) if len(s) else float("nan"))
    for p in pats:
        if any(w not in by_label for w in p["when"]): continue
        m = np.logical_and.reduce([by_label[w] for w in p["when"]]); sign = -1.0 if p["confirm_rate"] < p["confirm_all"] else 1.0; mt = re.search(r"(\d+) session", p["outcome"]); h0 = min(EXITS, key=lambda x: abs(x - (int(mt.group(1)) if mt else 2)))
        row = dict(when=p["when"], side="SELL" if sign < 0 else "BUY", exit=h0)
        for kind in ("hedged", "alone"):
            so, _ = days(m & disc, sign, h0, kind); sn, _ = days(m & ~disc, sign, h0, kind); a, b = stat(so), stat(sn); b["p"] = _boot(sn, brng) if len(sn) else float("nan"); b["usd_trade"] = b["bp"] / 1e4 * A; b["usd_year"] = b["usd_trade"] * b["days"] / years_new; b["per_year"] = b["days"] / years_new
            row[kind] = dict(old=a, new=b, passes=bool(a["bp"] > 0 and b["bp"] > 0 and b["p"] == b["p"] and b["p"] < bar), exits={h: float(days(m & ~disc, sign, h, kind)[0].mean()) for h in EXITS})
        co, _, _ = cheapest(m & disc, sign, h0); cn, used, _ = cheapest(m & ~disc, sign, h0); a, b = stat(co), stat(cn); b["p"] = _boot(cn, brng) if len(cn) else float("nan"); b["usd_year"] = b["bp"] / 1e4 * A * b["days"] / years_new
        row["cheap"] = dict(old=a, new=b, used=used, passes=bool(a["bp"] > 0 and b["bp"] > 0 and b["p"] == b["p"] and b["p"] < bar))
        sf, mults = days(m, sign, h0, "fund"); sa, _ = days(m, sign, h0, "alone_f"); row["fund"] = dict(stat(sf), stock_same_signals=float(sa.mean()) if len(sa) else float("nan"), first=f"{sf.index.min():%Y-%m}" if len(sf) else "", two_x=int(sum(abs(x) >= 1.5 for x in mults)), one_x=int(sum(abs(x) < 1.5 for x in mults))); rows.append(row)
    # ---- the funds on larger sets (the patterns are rare and the funds are young)
    sell = [np.logical_and.reduce([by_label[w] for w in p["when"]]) for p in pats if p["confirm_rate"] < p["confirm_all"] and all(w in by_label for w in p["when"])]; union = np.logical_or.reduce(sell) if sell else np.zeros(n, bool); pools = []
    for name, m in (("a sell-off that is in ANY of the candidate patterns (stock expected lower)", union), ("EVERY one-day sell-off of 5% or more (for reference: no pattern required)", np.ones(n, bool))):
        for h in EXITS:
            sf, mults = days(m, -1.0, h, "fund"); sa, _ = days(m, -1.0, h, "alone_f"); two = [abs(x) >= 1.5 for x in mults]
            pools.append(dict(set=name, exit=h, days=int(len(sf)), fund_bp=float(sf.mean()) if len(sf) else float("nan"), fund_win=float((sf > 0).mean()) if len(sf) else float("nan"), stock_bp=float(sa.mean()) if len(sa) else float("nan"), signals=len(mults), two_x=int(sum(two)), first=f"{sf.index.min():%Y-%m}" if len(sf) else ""))
    _, used_all, cost_all = cheapest(np.ones(n, bool) & ~disc, -1.0, 2)      # what each way costs, on every sell-off of 2018-2026 traded as a SELL with exit +2
    # ---- write
    rows.sort(key=lambda r: -(r["hedged"]["new"]["bp"] if r["hedged"]["new"]["bp"] == r["hedged"]["new"]["bp"] else -1e9)); nh = sum(r["hedged"]["passes"] for r in rows); na = sum(r["alone"]["passes"] for r in rows)
    L = ["# Sell-off study, test SO-T2: the strong patterns with the founder's real cost, US$70,000, and the single-stock funds", "", f"Registered in TRACK 3.104 before running. Account kept at US${A:,.0f}: each day's US${A:,.0f} is split equally over that day's signals, whole shares at the real share price. "
         f"Cost per order: the broker's fee board (platform US$0.99, settlement US$0.003 a share up to 1%, SEC fee on sells, audit-trail fee, 9% tax on the fees) **plus an allowance for the spread of {RC.SPREAD_BP['stock']:.0f} basis points per order for shares and {RC.SPREAD_BP['etf']:.0f} for funds (assumptions, not measured)**. "
         f"Every SHORT position is charged {RC.MARGIN_RATE:.1%} a year for the nights it is held -- the broker's rate for borrowed US dollars, used as a stand-in for the share-borrowing fee, which is not on the fee board. Buying a fund with the account's own money borrows nothing. All results are in basis points of the US$70,000 account per day with a trade (100 basis points = 1% = US$700). "
         f"**PASSES** = the average is above zero in 2005-2017 and in 2018-2026, and in 2018-2026 the chance that it is zero or less is under {bar:.4f} (0.05 / {K} patterns; calendar months redrawn {NBOOT} times). The patterns were chosen on these same years: a pass only admits a pattern to a forward record.", "",
         "## Part 1. The stock itself, real cost", "", "| when ALL of these hold | trade; exit | AGAINST the S&P 500 fund: 2005-2017 (days) | 2018-2026 (days; share of days with a gain; chance of zero or less) | US$ per trade; trades a year; US$ a year | verdict | the stock ALONE: 2005-2017 | 2018-2026 (chance) | US$ a year | verdict |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        h, a = r["hedged"], r["alone"]; L.append(f"| {' AND '.join(r['when'])} | {r['side']}; +{r['exit']} | {f0(h['old']['bp'])} ({h['old']['days']}) | {f0(h['new']['bp'])} ({h['new']['days']}; {h['new']['win']:.0%}; {h['new']['p']:.4f}) | {h['new']['usd_trade']:+,.0f}; {h['new']['per_year']:.1f}; {h['new']['usd_year']:+,.0f} | {'**PASSES**' if h['passes'] else 'fails'} | {f0(a['old']['bp'])} | {f0(a['new']['bp'])} ({a['new']['p']:.4f}) | {a['new']['usd_year']:+,.0f} | {'**PASSES**' if a['passes'] else 'fails'} |")
    L += ["", f"**Against the S&P 500 fund: {nh} of {len(rows)} pass. The stock alone: {na} of {len(rows)} pass.** (With the round cost of 30 basis points, SO-T: 1 of 24.)" + (f" For {noraw} sell-offs the real share price was not on disk and the adjusted price was used for the number of shares." if noraw else ""), "",
          "## Part 2. The same signals through the single-stock funds", "", "Only signals whose stock had a usable fund trading on both days (docs/selloff_funds.md). 'The stock on the same signals' = the stock alone, on exactly those signals, so the two columns can be compared.", "",
          "| pattern | exit | days with a fund (since) | the FUND: basis points a day (share of days with a gain) | the stock on the same signals | signals through a 1.5x-2x fund / a 1x fund |", "|---|---|---|---|---|---|"]
    for r in rows:
        f = r["fund"]; L.append(f"| {' AND '.join(r['when'])} | +{r['exit']} | {f['days']} ({f['first'] or '-'}) | {f0(f['bp'])} ({'n/a' if f['win'] != f['win'] else format(f['win'], '.0%')}) | {f0(f['stock_same_signals'])} | {f['two_x']} / {f['one_x']} |")
    L += ["", "| larger set | exit | days with a fund (since) | the FUND, basis points a day (share with a gain) | the stock on the same signals | signals (of which 1.5x-2x funds) |", "|---|---|---|---|---|---|"]
    L += [f"| {x['set']} | +{x['exit']} | {x['days']} ({x['first'] or '-'}) | {f0(x['fund_bp'])} ({'n/a' if x['fund_win'] != x['fund_win'] else format(x['fund_win'], '.0%')}) | {f0(x['stock_bp'])} | {x['signals']} ({x['two_x']}) |" for x in pools]
    nc = sum(r["cheap"]["passes"] for r in rows)
    L += ["", "## Part 3. Which way is cheaper for the same exposure, and the result when the cheapest way is always taken", "", "Same exposure of US$70,000 a day: the stock itself (sold short when it is expected lower), or a 1x fund bought with the same money, or a 2x fund bought with HALF the money. "
          f"Cost = fees + spread allowance ({RC.SPREAD_BP['stock']:.0f} basis points per order for shares, {RC.SPREAD_BP['etf']:.0f} for funds -- assumptions) + for a short sale {RC.MARGIN_RATE:.1%} a year for the nights held (stand-in). Measured on every sell-off of 2018-2026, traded as a SELL, exit two sessions after:", "",
          "| way | average cost, basis points of the exposure | signals where this way existed | times it was the cheapest |", "|---|---|---|---|"]
    L += [f"| {k} | {cost_all[k][0]:.1f} | {cost_all[k][1]} | {used_all[k]} |" if cost_all[k][1] else f"| {k} | n/a | 0 | 0 |" for k in ("stock", "1x fund", "2x fund")]
    L += ["", "| pattern | exit | cheapest way always taken: 2005-2017 | 2018-2026 (days; chance of zero or less) | US$ a year | ways used 2018-2026: stock / 1x fund / 2x fund | verdict |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        c = r["cheap"]; L.append(f"| {' AND '.join(r['when'])} | +{r['exit']} | {f0(c['old']['bp'])} | {f0(c['new']['bp'])} ({c['new']['days']}; {c['new']['p']:.4f}) | {c['new']['usd_year']:+,.0f} | {c['used']['stock']} / {c['used']['1x fund']} / {c['used']['2x fund']} | {'**PASSES**' if c['passes'] else 'fails'} |")
    L += ["", f"**Cheapest way always taken: {nc} of {len(rows)} pass.** The order of the three ways depends on the two spread allowances, which are assumptions: if the funds' real spread is under about half of the allowance, the 2x fund becomes the cheapest way."]
    L += ["", f"Fund-days left out because the price on Yahoo is plainly wrong (the fund's move differs from its multiple x the stock's move by more than 30 percentage points): {nbad} -- " + (", ".join(f"{f} {', '.join(sorted(f'{x:%Y-%m-%d}' for x in v))}" for f, v in BAD.items() if v) or "none") + "."]
    L += ["", "Under 30 days with a fund: too few to say whether the fund version is better -- the single-stock funds only exist since 2022, most since 2024."]
    DOCS.mkdir(exist_ok=True); (DOCS / "selloff_real.md").write_text("\n".join(L) + "\n"); (DOCS / "selloff_real.json").write_text(json.dumps(dict(account=A, spread_bp=RC.SPREAD_BP, bar=bar, patterns=rows, pools=pools, way_cost_bp=cost_all, way_used=used_all), indent=1, default=float))
    print(f"PART 1 -- the stock, real cost (fees + {RC.SPREAD_BP['stock']:.0f} bp spread per order + {RC.MARGIN_RATE:.1%} a year on short positions), US${A:,.0f}; bar p < {bar:.4f}; numbers in basis points of the account per trading day")
    print("  AGAINST the S&P 500: 2005-17 | 2018-26 (days; chance) | US$/trade; trades/yr; US$/yr | verdict || ALONE: 2005-17 | 2018-26 (chance) | US$/yr | verdict || exit | trade | pattern")
    for r in rows:
        h, a = r["hedged"], r["alone"]; print(f"  {f0(h['old']['bp']):>5} | {f0(h['new']['bp']):>5} ({h['new']['days']:>3}; {h['new']['p']:.4f}) | {h['new']['usd_trade']:>+7,.0f}; {h['new']['per_year']:>4.1f}; {h['new']['usd_year']:>+8,.0f} | {'PASSES' if h['passes'] else 'fails '} || {f0(a['old']['bp']):>5} | {f0(a['new']['bp']):>5} ({a['new']['p']:.4f}) | {a['new']['usd_year']:>+8,.0f} | {'PASSES' if a['passes'] else 'fails '} || +{r['exit']} | {r['side']:<4} | {' AND '.join(r['when'])[:120]}")
    print(f"=> against the S&P 500: {nh} of {len(rows)} pass; the stock alone: {na} of {len(rows)} pass")
    print(f"PART 2 -- the same signals through single-stock funds (fees + {RC.SPREAD_BP['etf']:.0f} bp spread per order); {nbad} fund-days with a plainly wrong price left out: " + (", ".join(f"{f} {min(v):%Y-%m-%d}" + (f" (+{len(v) - 1})" if len(v) > 1 else "") for f, v in BAD.items() if v) or "none"))
    print("  days with a fund (since) | FUND bp/day (share with a gain) | the stock on the same signals | 1.5x-2x / 1x signals | exit | pattern")
    for r in rows:
        f = r["fund"]; print(f"  {f['days']:>3} ({f['first'] or '   -   '}) | {f0(f['bp']):>5} ({'n/a' if f['win'] != f['win'] else format(f['win'], '.0%'):>4}) | {f0(f['stock_same_signals']):>5} | {f['two_x']:>2} / {f['one_x']:>2} | +{r['exit']} | {' AND '.join(r['when'])[:110]}")
    for x in pools: print(f"  {x['days']:>3} ({x['first'] or '   -   '}) | {f0(x['fund_bp']):>5} ({'n/a' if x['fund_win'] != x['fund_win'] else format(x['fund_win'], '.0%'):>4}) | {f0(x['stock_bp']):>5} | {x['two_x']:>2} of {x['signals']:>3} signals 1.5x-2x | +{x['exit']} | {x['set']}")
    print("PART 3 -- which way is cheaper for the SAME exposure (every sell-off of 2018-2026 as a SELL, exit +2): average cost in basis points of the exposure")
    for k in ("stock", "1x fund", "2x fund"): print(f"  {k:<8}: " + (f"{cost_all[k][0]:>5.1f} bp on {cost_all[k][1]} signals; the cheapest way {used_all[k]} times" if cost_all[k][1] else "no signal had one"))
    print("  cheapest way always taken: 2005-17 | 2018-26 (days; chance) | US$/yr | stock / 1x / 2x used | verdict | exit | pattern")
    for r in rows:
        c = r["cheap"]; print(f"  {f0(c['old']['bp']):>5} | {f0(c['new']['bp']):>5} ({c['new']['days']:>3}; {c['new']['p']:.4f}) | {c['new']['usd_year']:>+8,.0f} | {c['used']['stock']:>3} / {c['used']['1x fund']:>2} / {c['used']['2x fund']:>2} | {'PASSES' if c['passes'] else 'fails '} | +{r['exit']} | {' AND '.join(r['when'])[:110]}")
    print(f"=> cheapest way always taken: {nc} of {len(rows)} pass")
    print("-> docs/selloff_real.md")


def cmd_audit(top: int = 25):
    """Free check of the doubt recorded in TRACK 3.106: the funds did about 150 basis points worse than their stocks on the same signals. For every one-day sell-off of
    5% whose stock had an inverse fund (traded as a SELL, next open -> close two sessions after) it compares what the fund DID with what it SHOULD have done (its multiple x
    the stock's move over the same span) and prints the largest differences with the fund's prices on the two days, so a bad price or a split can be seen by eye."""
    E = pd.read_csv(ROOT / "events.csv", parse_dates=["day"]); P = _px(); unit, dfn = S.BASES[GROUP]; B = E[(E.unit == unit) & (E.definition == dfn)].sort_values("day").reset_index(drop=True)
    R = {f.stem: pd.read_parquet(f) for f in RP.glob("*.parquet")}; C = pd.read_csv(CHECK); C = C[C.ok & (C.stated < 0)]; rows = []
    for r in B.itertuples():
        d = P[r.ticker]; i = int(r.i)
        if i + 2 >= len(d): continue
        din, dout = d.index[i + 1], d.index[i + 2]; sr = float(d.close.iloc[i + 2] / d.open.iloc[i + 1] - 1)
        for c in C[C.stock == r.ticker].itertuples():
            F = R.get(c.fund)
            if F is None or din not in F.index or dout not in F.index: continue
            fr = float(F.close.loc[dout] / F.open.loc[din] - 1); prev = F.close.shift(1).get(din, np.nan); rows.append(dict(day=f"{r.day:%Y-%m-%d}", stock=r.ticker, fund=c.fund, mult=float(c.stated), stock_move=sr * 100, fund_should=c.stated * sr * 100, fund_did=fr * 100,
                        fund_prev_close=float(prev), fund_open=float(F.open.loc[din]), fund_close2=float(F.close.loc[dout]), open_gap=float(F.open.loc[din] / prev - 1) * 100 if prev == prev and prev > 0 else np.nan, stock_gap=float(d.open.iloc[i + 1] / d.close.iloc[i] - 1) * 100))
    A = pd.DataFrame(rows)
    if not len(A): print("no signal with an inverse fund found"); return
    A["diff"] = A.fund_did - A.fund_should; A["gap_should"] = A.mult * A.stock_gap; A["gap_diff"] = A.open_gap - A.gap_should
    print(f"{len(A)} fund trades on one-day sell-offs (inverse funds, next open -> close +2). In per cent of the money put in:")
    print(f"  the stock moved {A.stock_move.mean():+.2f} on average; the funds SHOULD have made {A.fund_should.mean():+.2f}; they DID make {A.fund_did.mean():+.2f}; difference {A['diff'].mean():+.2f} (middle value {A['diff'].median():+.2f})")
    print(f"  trades where did and should differ by more than 3 points: {int((A['diff'].abs() > 3).sum())}; by more than 10 points: {int((A['diff'].abs() > 10).sum())}. Without those over 3 points the average difference is {A[A['diff'].abs() <= 3]['diff'].mean():+.2f}")
    print(f"  the fund's OPENING price against its stock's opening move (should be multiple x the stock's overnight move): average difference {A.gap_diff.mean():+.2f} points; over 3 points apart in {int((A.gap_diff.abs() > 3).sum())} trades")
    print("  by fund: " + ", ".join(f"{f} {g['diff'].mean():+.2f} ({len(g)})" for f, g in A.groupby("fund")))
    print(f"  the {top} largest differences:"); print("  day        stock fund   x   stock%  should%   did%   diff | fund: prev close -> open -> close+2 | its open against the stock's overnight move")
    for r in A.reindex(A["diff"].abs().sort_values(ascending=False).index).head(top).itertuples(): print(f"  {r.day} {r.stock:<5} {r.fund:<5} {r.mult:+.0f} {r.stock_move:+7.2f} {r.fund_should:+8.2f} {r.fund_did:+7.2f} {r.diff:+7.2f} | {r.fund_prev_close:9.3f} -> {r.fund_open:9.3f} -> {r.fund_close2:9.3f} | {r.open_gap:+6.2f} against {r.gap_should:+6.2f}")
    A.to_csv(DOCS / "selloff_funds_audit.csv", index=False); print("-> docs/selloff_funds_audit.csv")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["fetch", "run", "audit"]); ap.add_argument("--everything", action="store_true", help="also confirmed patterns that are not candidates (for checking the code)"); a = ap.parse_args(); cmd_fetch() if a.cmd == "fetch" else cmd_audit() if a.cmd == "audit" else cmd_run(a.everything)
