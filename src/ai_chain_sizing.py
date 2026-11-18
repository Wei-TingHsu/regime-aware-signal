"""ai_chain_sizing.py -- three follow-ups to the design test (founder, 18 Nov), registered in TRACK 3.68 before running; priors #158-#161.

S  SIZE BY THE SCORE, shape learned by least squares.  "It might not be that score 0.1 = size 0.1 ... there might be a mathematical order."
   Trade: a company's results release, its own stock, entered 1 minute after the stamp, held 60 minutes (the cell where D1 found that larger scores
   earn more). r = the stock's return over the hold (bp), s = the reader's own-stock score (-1..+1). Four shapes, each fitted by least squares
   (choose the parameters that make the sum of squared errors, sum over releases of (r - prediction)^2, as small as possible):
       M0  sign       r = b * sign(s)                      every score the same size (the first test)
       M1  linear     r = b * s                            twice the score, twice the size
       M2  power      r = b * sign(s) * |s|^g              g < 1 flattens, g = 1 is linear, g > 1 puts the weight on strong scores
       M3  step       r = b * sign(s) * [ |s| >= h ]       trade only scores of size h or more, all at one size
   Position = the fitted shape, scaled so the average position size is 1. Judged OUT OF SAMPLE: for each year that has at least 60 earlier releases, the
   parameters are fitted on the releases BEFORE that year only and applied to that year's releases.

N  NETTING. One account per stock per afternoon. Signals = the stock's own results score, and the directions other companies' results releases give
   for it. After each signal the position is the SUM of the signals so far, limited to one unit long or short; it is held until 60 minutes after the
   last signal. Compared with the first test's way (every signal its own one-unit trade for 60 minutes).

C  COSTS with Interactive Brokers (IBKR Pro, Fixed): commission USD 0.005 per share, at least USD 1 per order, at most 1% of the trade; SEC fee on
   sales 0.0000206 x value (IBKR's pricing page, read 18 Nov 2026). Plus half the bid-ask spread on the way in and on the way out, MEASURED from
   Nasdaq's quotes at the entry and exit minutes of each past trade (Databento; `costs_plan` quotes the price first).

    python -m src.ai_chain_sizing size
    python -m src.ai_chain_sizing net
    python -m src.ai_chain_sizing costs_plan            # which quote data exists and what it costs. Downloads nothing.
    python -m src.ai_chain_sizing costs_fetch --max-usd 3
    python -m src.ai_chain_sizing costs_report --notional 10000
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
from src.ai_chain_test import build, entry, ret, LAST, _mentions, _load, US

DOCS = Path("docs"); QUOTES = Path("data_provenance/intraday/quotes"); G_GRID = np.round(np.arange(0.0, 4.01, 0.05), 2); H_GRID = np.round(np.arange(0.1, 0.95, 0.1), 2)


def _t(v): v = np.asarray(v, float); v = v[np.isfinite(v)]; return float(v.mean() / (v.std(ddof=1) / np.sqrt(len(v)))) if len(v) > 2 and v.std(ddof=1) > 0 else float("nan")


def _trades(k=1, x=60):
    F, B = build(); o = F["F2"]["obs"].reset_index(drop=True); s = pd.to_numeric(o["own_stock"], errors="coerce").fillna(0).to_numpy(float)
    r = np.array([ret(B, q.sym, entry(B, q.sym, q.date, int(q.t0), "ext", k), x, LAST["stock"]) for q in o.itertuples()], float); ok = np.isfinite(r) & (s != 0)
    return o[ok].reset_index(drop=True), s[ok], r[ok], F, B


# ------------------------------------------------------------------------------------------------ S: shapes fitted by least squares
def shape(name, s, par=None):
    a = np.abs(s); return {"M0": np.sign(s), "M1": s, "M2": np.sign(s) * a ** (par if par is not None else 1.0), "M3": np.sign(s) * (a >= (par if par is not None else 0.0))}[name]


def fit(name, s, r):
    """least squares: for a given shape x = shape(s), the best b is sum(x*r)/sum(x*x); for M2 and M3 the shape's own parameter is searched on a grid"""
    best = None
    for par in ([None] if name in ("M0", "M1") else (G_GRID if name == "M2" else H_GRID)):
        x = shape(name, s, par); den = float((x * x).sum())
        if den == 0: continue
        b = float((x * r).sum() / den); sse = float(((r - b * x) ** 2).sum())
        if best is None or sse < best["sse"]: best = dict(par=None if par is None else float(par), b=b, sse=sse)
    return best


def _perf(w, r):
    w = np.asarray(w, float); g = float(np.abs(w).sum()); return dict(per_unit=float((w * r).sum() / g) if g > 0 else float("nan"), t=_t(w * r), traded=int((w != 0).sum()))


def cmd_size():
    o, s, r, _, _ = _trades(); yr = o["date"].dt.year.to_numpy(); sst = float((r ** 2).sum()); out = dict(n=int(len(r))); names = {"M0": "sign (every score the same size)", "M1": "linear (size = score)", "M2": "power (size = |score|^g)", "M3": "step (trade only |score| >= h)"}
    L = ["# S: position size from the score, shape learned by least squares", "", f"Trade: results release -> own stock, enter 1 min after the SEC stamp, hold 60 min; {len(r)} releases, May 2018 to Nov 2026; returns in bp before cost. r = the stock's return, s = the own-stock score.", "",
         "## Fitted on all releases (in sample: this describes the past, it is not a test)", "", "| shape | equation | fitted | sum of squared errors, share of the total | per unit of position | t |", "|---|---|---|---|---|---|"]
    eq = {"M0": "r = b * sign(s)", "M1": "r = b * s", "M2": "r = b * sign(s) * |s|^g", "M3": "r = b * sign(s) * [|s| >= h]"}; print(f"S: {len(r)} trades")
    for k in names:
        f = fit(k, s, r); w = shape(k, s, f["par"]); pf = _perf(w, r); par = "" if f["par"] is None else (f", g = {f['par']:.2f}" if k == "M2" else f", h = {f['par']:.1f}"); out[k] = dict(fit=f, **pf)
        L.append(f"| {k} {names[k]} | {eq[k]} | b = {f['b']:+.1f} bp{par} | {f['sse'] / sst:.4f} | {pf['per_unit']:+.1f} bp | {pf['t']:+.2f} |"); print(f"   in sample  {k}: b {f['b']:+.1f}{par}; error share {f['sse'] / sst:.4f}; per unit {pf['per_unit']:+.1f} bp, t {pf['t']:+.2f}, traded {pf['traded']}")
    years = [int(y) for y in sorted(set(yr)) if (yr < y).sum() >= 60]; W = {k: np.full(len(r), np.nan) for k in names}; pars = {k: [] for k in names}
    for y in years:
        tr, te = yr < y, yr == y
        for k in names: f = fit(k, s[tr], r[tr]); W[k][te] = shape(k, s[te], f["par"]) * np.sign(f["b"]); pars[k].append((int(y), f["par"], round(f["b"], 1)))      # a negative fitted b would mean 'trade against the score'
    te = np.isfinite(W["M0"]); L += ["", f"## Out of sample ({years[0]}-{years[-1]}; parameters fitted only on earlier releases)" if years else "## Out of sample: not enough history", "", "| shape | per unit of position | t | releases traded | parameter fitted each year |", "|---|---|---|---|---|"]
    for k in names:
        pf = _perf(W[k][te], r[te]); out[k + "_oos"] = dict(**pf, pars=pars[k]); ps = "; ".join(f"{y}: {('g ' if k == 'M2' else 'h ') + format(p_, '.2f') if p_ is not None else 'b ' + format(b_, '+.0f')}" for y, p_, b_ in pars[k])
        L.append(f"| {k} {names[k]} | {pf['per_unit']:+.1f} bp | {pf['t']:+.2f} | {pf['traded']} of {int(te.sum())} | {ps} |"); print(f"   OUT of sample {k}: per unit {pf['per_unit']:+.1f} bp, t {pf['t']:+.2f}, traded {pf['traded']} of {int(te.sum())} | {ps}")
    L += ["", "Per unit of position = total gain divided by total position size, so shapes that trade fewer or smaller positions are compared fairly. The out-of-sample table is the one to believe: the shape's parameter was chosen without seeing that year's releases."]
    DOCS.mkdir(exist_ok=True); (DOCS / "ai_chain_sizing.md").write_text("\n".join(L) + "\n"); (DOCS / "ai_chain_sizing.json").write_text(json.dumps(out, indent=1, default=str)); print("-> docs/ai_chain_sizing.md")


# ------------------------------------------------------------------------------------------------ N: one account per stock per afternoon
def cmd_net():
    S, _ = _load(); F, B = build(); eq0 = pd.Timestamp("2018-05-01"); R = S[S.ticker.isin(US) & (S.date >= eq0) & (S.t0 >= 960)].copy(); R["own_stock"] = pd.to_numeric(R["own_stock"], errors="coerce").fillna(0)
    own = R[R.own_stock != 0][["sym", "date", "t0", "own_stock"]].rename(columns={"own_stock": "sig"}).assign(kind="own"); M = _mentions(R); men = M[["sym", "date", "t0", "direction"]].rename(columns={"direction": "sig"}).assign(kind="other") if len(M) else own.iloc[:0]
    A = pd.concat([own, men], ignore_index=True).sort_values(["sym", "date", "t0"]); rows = []; last = LAST["stock"]
    def seg(sym, d, a, b):
        pa, pb = B.p(sym, d, a), B.p(sym, d, b); return np.log(pb / pa) * 1e4 if np.isfinite(pa) and np.isfinite(pb) and pa > 0 else np.nan
    for (sym, d), g in A.groupby(["sym", "date"]):
        t = g.t0.to_numpy(int) + 1; sg = g.sig.to_numpy(float)
        if t[-1] + 60 > last or d not in B.d.get(sym, {}): continue
        un = [np.sign(x) * seg(sym, d, a, a + 60) for x, a in zip(sg, t)]; cuts = list(t) + [t[-1] + 60]; res = {}
        for name, vals in (("signs", np.sign(sg)), ("scores", sg)):
            pos = np.clip(np.cumsum(vals), -1, 1); res[name] = (sum(p * seg(sym, d, cuts[i], cuts[i + 1]) if cuts[i + 1] > cuts[i] else 0.0 for i, p in enumerate(pos)), float(np.max(np.abs(pos))))
        rows.append(dict(sym=sym, date=d, n=len(g), has_own=bool((g.kind == "own").any()), conflict=bool((sg > 0).any() and (sg < 0).any()), un=float(np.sum(un)), un_units=len(g), net_signs=res["signs"][0], net_signs_units=res["signs"][1], net_scores=res["scores"][0], net_scores_units=res["scores"][1]))
    T = pd.DataFrame(rows).replace([np.inf, -np.inf], np.nan).dropna(subset=["un", "net_signs", "net_scores"]); out = {}
    L = ["# N: netting -- one account per stock per afternoon", "", "Signals after 16:00 from results releases, May 2018 to Nov 2026: the stock's own results score, and the directions other companies' releases give for it. **Each signal alone** = the first test's way (one unit per signal, 60 minutes each). **Net of signs** / **net of scores** = one account: after each signal the position is the sum of the signs (or of the scores) so far, limited to one unit, held until 60 minutes after the last signal. Returns in bp before cost; 'per unit' = total gain divided by the units of capital used.", ""]
    for title, m in (("all stock-afternoons", np.ones(len(T), bool)), ("the stock itself reported", T.has_own.to_numpy()), ("only named by others", ~T.has_own.to_numpy()), ("two or more signals", (T.n >= 2).to_numpy()), ("signals pointing opposite ways", T.conflict.to_numpy())):
        g = T[m]
        if len(g) < 10: L += [f"## {title}: {len(g)} cases, too few", ""]; continue
        L += [f"## {title}: {len(g)} stock-afternoons", "", "| way | average per stock-afternoon | per unit of capital | t |", "|---|---|---|---|"]; print(f"N  {title}: {len(g)} stock-afternoons"); out[title] = dict(n=int(len(g)))
        for lab, col, u in (("each signal alone", "un", "un_units"), ("net of signs", "net_signs", "net_signs_units"), ("net of scores", "net_scores", "net_scores_units")):
            pu = float(g[col].sum() / g[u].sum()) if g[u].sum() > 0 else float("nan"); L.append(f"| {lab} | {g[col].mean():+.1f} bp | {pu:+.1f} bp | {_t(g[col]):+.2f} |"); out[title][lab] = dict(mean=float(g[col].mean()), per_unit=pu, t=_t(g[col])); print(f"     {lab:18} average {g[col].mean():+7.1f} bp | per unit {pu:+7.1f} bp | t {_t(g[col]):+.2f}")
        L.append("")
    DOCS.mkdir(exist_ok=True); (DOCS / "ai_chain_netting.md").write_text("\n".join(L) + "\n"); (DOCS / "ai_chain_netting.json").write_text(json.dumps(out, indent=1, default=str)); print("-> docs/ai_chain_netting.md")


# ------------------------------------------------------------------------------------------------ C: measured costs, IBKR
def _windows():
    o, s, r, _, _ = _trades(); W = []
    for i, q in enumerate(o.itertuples()):
        a = q.date + pd.Timedelta(minutes=int(q.t0) - 1); b = q.date + pd.Timedelta(minutes=int(q.t0) + 63); sym = "FB" if q.sym == "META" and q.date < pd.Timestamp("2022-06-09") else q.sym
        W.append(dict(i=i, sym=q.sym, raw=sym, date=q.date, t0=int(q.t0), start=a.tz_localize("America/New_York").tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%S"), end=b.tz_localize("America/New_York").tz_convert("UTC").strftime("%Y-%m-%dT%H:%M:%S"), key=f"{q.sym}_{q.date:%Y%m%d}", score=float(s[i]), ret=float(r[i])))
    return W


def _schema(c):
    have = [str(x) for x in c.metadata.list_schemas(dataset="XNAS.ITCH")]; return next((x for x in ("bbo-1m", "bbo-1s", "tbbo", "mbp-1") if x in have), None), have


def cmd_costs_plan(limit):
    from src.intraday_fetch import _client
    c = _client(); sch, have = _schema(c); print(f"Nasdaq quote data offered: {', '.join(have)}\nusing: {sch}")
    if sch is None: print("no quote schema is offered for this dataset -- tell Claude"); return
    W = _windows(); todo = [w for w in W if not (QUOTES / f"{w['key']}.parquet").exists()]; sample = todo if limit is None else todo[:: max(1, len(todo) // limit)][:limit]; usd = 0.0; bad = 0
    for w in sample:
        try: usd += float(c.metadata.get_cost(dataset="XNAS.ITCH", symbols=[w["raw"]], stype_in="raw_symbol", schema=sch, start=w["start"], end=w["end"]))
        except Exception as e: bad += 1; print(f"  {w['key']}: quote failed: {type(e).__name__}: {str(e)[:80]}") if bad <= 3 else None
    est = usd / max(1, len(sample) - bad) * len(todo); print(f"{len(W)} trades; {len(todo)} quote windows of 64 minutes still to download. Quoted for {len(sample) - bad} of them: US${usd:.4f} -> about US${est:.2f} for all. Nothing was downloaded.")


def cmd_costs_fetch(max_usd):
    from src.intraday_fetch import _client
    import warnings
    c = _client(); sch, _ = _schema(c); W = _windows(); QUOTES.mkdir(parents=True, exist_ok=True); spent = 0.0; n = 0
    for w in W:
        f = QUOTES / f"{w['key']}.parquet"
        if f.exists(): continue
        try:
            usd = float(c.metadata.get_cost(dataset="XNAS.ITCH", symbols=[w["raw"]], stype_in="raw_symbol", schema=sch, start=w["start"], end=w["end"]))
            if spent + usd > max_usd: print(f"  cap US${max_usd:.2f} reached after {n} windows; rerun with a higher --max-usd"); break
            with warnings.catch_warnings():
                warnings.simplefilter("ignore"); df = c.timeseries.get_range(dataset="XNAS.ITCH", symbols=[w["raw"]], stype_in="raw_symbol", schema=sch, start=w["start"], end=w["end"]).to_df()
            df.to_parquet(f); spent += usd; n += 1
            if n % 50 == 0: print(f"  {n} windows, about US${spent:.2f}")
        except Exception as e: print(f"  {w['key']}: {type(e).__name__}: {str(e)[:90]}")
    print(f"done: {n} windows downloaded, about US${spent:.2f} -> {QUOTES} (ignored folder; not uploaded)")


def _quote_at(df, when_utc):
    """last valid Nasdaq bid and ask at or before a moment"""
    ix = pd.to_datetime(df.index, utc=True); d = df[(ix <= when_utc) & (df["bid_px_00"] > 0) & (df["ask_px_00"] > df["bid_px_00"])]
    return (float(d["bid_px_00"].iloc[-1]), float(d["ask_px_00"].iloc[-1])) if len(d) else (np.nan, np.nan)


def cmd_costs_report(notional):
    rows = []
    for w in _windows():
        f = QUOTES / f"{w['key']}.parquet"
        if not f.exists(): continue
        df = pd.read_parquet(f)
        if "bid_px_00" not in df.columns or not len(df): continue
        t_in = (w["date"] + pd.Timedelta(minutes=w["t0"] + 1)).tz_localize("America/New_York").tz_convert("UTC"); t_out = t_in + pd.Timedelta(minutes=60); (b1, a1), (b2, a2) = _quote_at(df, t_in), _quote_at(df, t_out)
        if not all(np.isfinite([b1, a1, b2, a2])): continue
        m1, m2 = (a1 + b1) / 2, (a2 + b2) / 2; sp1, sp2 = (a1 - b1) / m1 * 1e4, (a2 - b2) / m2 * 1e4; sh = notional / m1; com = min(max(1.0, 0.005 * sh), 0.01 * notional); com_bp = 2 * com / notional * 1e4 + 0.0000206 * 1e4
        rows.append(dict(sym=w["sym"], date=w["date"], score=w["score"], gross=np.sign(w["score"]) * w["ret"], spread_in=sp1, spread_out=sp2, spread_cost=sp1 / 2 + sp2 / 2, commission=com_bp, cost=sp1 / 2 + sp2 / 2 + com_bp))
    T = pd.DataFrame(rows)
    if T.empty: print("no quote windows on disk yet -- run costs_fetch first"); return
    T["net"] = T["gross"] - T["cost"]; q = lambda x, p: float(np.nanpercentile(x, p)); strong = T[T.score.abs() >= 0.8]
    L = ["# C: measured trading cost of the results rule, Interactive Brokers", "", f"Trade: own stock, enter 1 min after the SEC stamp, hold 60 min; {len(T)} past trades with Nasdaq quotes at both ends. Cost of one round trip = half the bid-ask spread going in + half going out + IBKR Pro Fixed commission (USD 0.005 per share, at least USD 1, at most 1%, both orders) + SEC fee on the sale, for a trade of US${notional:,.0f}. In bp (1 bp = 0.01%).", "",
         "| | median | average | three in four trades below | nine in ten below |", "|---|---|---|---|---|"]
    for lab, col in (("spread when entering", "spread_in"), ("spread when leaving", "spread_out"), ("spread cost of the round trip", "spread_cost"), ("commission and fee", "commission"), ("TOTAL cost", "cost")): L.append(f"| {lab} | {q(T[col], 50):.1f} | {T[col].mean():.1f} | {q(T[col], 75):.1f} | {q(T[col], 90):.1f} |")
    L += ["", "| rule | trades | before cost | cost (average) | after cost | t after cost | right on, after cost |", "|---|---|---|---|---|---|---|", f"| every score, one unit | {len(T)} | {T.gross.mean():+.1f} bp | {T.cost.mean():.1f} bp | {T.net.mean():+.1f} bp | {_t(T.net):+.2f} | {(T.net > 0).mean():.0%} |"]
    if len(strong) >= 10: L.append(f"| only scores of 0.8 or more | {len(strong)} | {strong.gross.mean():+.1f} bp | {strong.cost.mean():.1f} bp | {strong.net.mean():+.1f} bp | {_t(strong.net):+.2f} | {(strong.net > 0).mean():.0%} |")
    L += ["", "Limits: these are Nasdaq's own best bid and ask; IBKR routes to the best of all exchanges, so the true spread is at most this. A quote shows the price for a small size; a large order moves the price further. Outside regular hours IBKR accepts limit orders only, so an order may not fill."]
    print("\n".join(L[4:])); DOCS.mkdir(exist_ok=True); (DOCS / "ai_chain_costs.md").write_text("\n".join(L) + "\n"); T.to_csv(DOCS / "ai_chain_costs.csv", index=False); print("-> docs/ai_chain_costs.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["size", "net", "costs_plan", "costs_fetch", "costs_report"]); ap.add_argument("--max-usd", type=float, default=3.0); ap.add_argument("--limit", type=int, default=40, help="costs_plan: how many windows to price before scaling up"); ap.add_argument("--notional", type=float, default=10000.0); a = ap.parse_args()
    {"size": cmd_size, "net": cmd_net, "costs_plan": lambda: cmd_costs_plan(a.limit), "costs_fetch": lambda: cmd_costs_fetch(a.max_usd), "costs_report": lambda: cmd_costs_report(a.notional)}[a.cmd]()
