"""ai_chain_test.py -- the AI-chain news test (registered in docs/prereg_ai_chain.md before running; priors #145-#152).

Question (founder, 12-15 Nov): when one of the fourteen AI-chain companies publishes (1) its results or (2) another material event, does the SCORE Claude
gave the text tell the direction prices take in the minutes and hours AFTER the text is public -- for the Nasdaq-100 future, for the company's own
stock, and for the other companies the reader named as affected?

Scores: processed/ai_earnings_scores.csv (reader ai-earn-v3) and processed/ai_events_scores.csv (reader ai-event-v2); made from the texts alone.
Prices: the Nasdaq-100 / S&P 500 futures' session cache (08:00-16:59 New York, from June 2010) and each stock's 1-minute bars (04:00-20:00, from May 2018).
Clock: the SEC's acceptance stamp, New York time. Price at minute m = last trade before m, at most 5 minutes old; returns in basis points (1 bp = 0.01%).

    python -m src.ai_chain_test coverage     # how many events have prices, family by family (no returns shown)
    python -m src.ai_chain_test run          # the seven families -> docs/ai_chain_test.md, .json
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path("data_provenance/intraday"); CACHE = ROOT / "_cache"; EQ = ROOT / "eq"; PROC, DOCS = Path("processed"), Path("docs")
US = ["AMD", "NVDA", "MU", "INTC", "AVGO", "SNDK", "ORCL", "CRWD", "GOOG", "META", "AMZN", "MSFT"]; FOREIGN = ["TSM", "SKHY"]        # foreign filers: the SEC stamp can be hours after the release in Asia
NAMES = {"GOOGL": "GOOG", "ALPHABET": "GOOG", "GOOGLE": "GOOG", "FB": "META", "FACEBOOK": "META", "SANDISK": "SNDK", "SK HYNIX": "SKHY", "HYNIX": "SKHY", "TSMC": "TSM", "NVIDIA": "NVDA", "MICRON": "MU", "INTEL": "INTC",
         "BROADCOM": "AVGO", "ORACLE": "ORCL", "CROWDSTRIKE": "CRWD", "AMAZON": "AMZN", "MICROSOFT": "MSFT"}
OPEN5, CLOSE, TOL, N_NULL, MIN_N, SEED = 575, 960, 5, 2000, 30, 20261115       # 09:35 (five minutes after the open, so the opening print is over), 16:00
BAR = 0.05 / 7                                                                 # seven families
COST = {"future": 2.0, "stock": 10.0}                                          # bp per round trip: the future as in v3e; stocks outside regular hours trade wider -- 10 bp is an assumption, stated
LAST = {"future": 1019, "stock": 1199}                                         # 16:59 (futures stop at 17:00); 19:59
SPLIT = 5000.0                                                                 # a |move| above 50% between two points is a share split in unadjusted prices -> dropped
SIG1 = ["own_stock", "results_vs_prior_guidance", "guidance_change", "fcf_trend", "market", "ai_demand"]


# ------------------------------------------------------------------------------------------------ prices
class Book:
    def __init__(self): self.d, self.days = {}, {}

    def add(self, sym, M):
        self.d[sym] = {k: (g["minute"].to_numpy(), g["close"].to_numpy()) for k, g in M.groupby("date", sort=True)}; self.days[sym] = np.array(sorted(self.d[sym]), dtype="datetime64[ns]")

    def p(self, sym, date, m, tol=TOL):
        v = self.d.get(sym, {}).get(date)
        if v is None: return np.nan
        mins, cl = v; i = np.searchsorted(mins, m - 1, side="right") - 1
        return float(cl[i]) if (i >= 0 and (m - 1) - mins[i] <= tol) else np.nan

    def day(self, sym, date, strictly_after=False):
        """first trading day on/after `date` (or strictly after), at most 6 calendar days away -- else None"""
        ds = self.days.get(sym)
        if ds is None or not len(ds): return None
        i = np.searchsorted(ds, np.datetime64(date), side="right" if strictly_after else "left")
        if i >= len(ds): return None
        d = pd.Timestamp(ds[i]); return d if (d - date).days <= 6 else None


def _ny(df: pd.DataFrame) -> pd.DataFrame:
    if "ts_event" in df.columns: df = df.set_index("ts_event")
    ny = pd.to_datetime(df.index, utc=True).tz_convert("America/New_York"); return pd.DataFrame(dict(date=ny.normalize().tz_localize(None), minute=(ny.hour * 60 + ny.minute).astype(np.int16), close=df["close"].to_numpy(float)))


def load_book(need: dict) -> Book:
    """need: {symbol: set of event dates}. Stocks: only the event days and the six calendar days after each are kept (memory)."""
    B = Book()
    for f in ("NQ", "ES"):
        p = CACHE / f"session_{f}.parquet"
        if not p.exists(): raise SystemExit("the futures cache is missing -- run `python -m src.intraday_v3e cache` first")
        B.add(f, pd.read_parquet(p))
    for sym, dates in need.items():
        folder = EQ / sym
        if sym in ("NQ", "ES") or not folder.exists() or not dates: continue
        keep = {d + pd.Timedelta(days=k) for d in dates for k in range(-1, 7)}; parts = []
        for p in sorted(folder.glob("*.parquet")):
            M = _ny(pd.read_parquet(p)); parts.append(M[M["date"].isin(keep)])
        M = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()
        if len(M): B.add(sym, M.sort_values(["date", "minute"]).drop_duplicates(["date", "minute"]))
    return B


# ------------------------------------------------------------------------------------------------ entries, exits, returns
def entry(B, sym, date, t0, mode, k):
    if mode == "ext": return (date, t0 + k) if date in B.d.get(sym, {}) else None                  # k minutes after the stamp, whatever the hour
    d = B.day(sym, date)                                                                           # "open": the first regular-session moment after the stamp
    if d is None: return None
    if d != date or t0 < 570: return (d, OPEN5)
    if t0 < 950: return (d, t0 + 5)
    d = B.day(sym, date, strictly_after=True); return (d, OPEN5) if d is not None else None


def exit_(B, sym, e, x, last):
    d, m = e
    if isinstance(x, int): return (d, m + x) if m + x <= last else None
    if x == "eod": return (d, last) if m <= last - 10 else None
    nxt = lambda: B.day(sym, d, strictly_after=True)
    if x == "open": return (d, OPEN5) if m < 570 else ((nxt(), OPEN5) if nxt() is not None else None)
    c = (d, CLOSE) if m <= CLOSE - 10 else ((nxt(), CLOSE) if nxt() is not None else None)
    if x == "close" or c is None: return c
    d2 = B.day(sym, c[0], strictly_after=True); return (d2, CLOSE) if d2 is not None else None     # "close+1"


def ret(B, sym, e, x, last):
    if e is None: return np.nan
    q = exit_(B, sym, e, x, last)
    if q is None: return np.nan
    pa = B.p(sym, *e); pb = B.p(sym, q[0], q[1], 15 if q[1] in (OPEN5, CLOSE) else TOL)
    if not (np.isfinite(pa) and np.isfinite(pb) and pa > 0): return np.nan
    r = np.log(pb / pa) * 1e4; return r if abs(r) < SPLIT else np.nan


def _stat(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]; n = len(v)
    if n < MIN_N: return dict(n=n, mean=np.nan, t=np.nan, hit=np.nan)
    s = v.std(ddof=1); return dict(n=n, mean=float(v.mean()), t=float(v.mean() / (s / np.sqrt(n))) if s > 0 else np.nan, hit=float((v > 0).mean()))


def _r(x, k=1): return round(float(x), k) if x is not None and np.isfinite(x) else None


def _lab(c): mode, k, x = c; a = f"{k} min after the stamp" if mode == "ext" else "next regular session"; b = {"eod": "to 16:59", "open": "to the next 09:35", "close": "to the next 16:00", "close+1": "to the 16:00 after that"}.get(x, f"hold {x} min"); return f"{a}, {b}"


# ------------------------------------------------------------------------------------------------ one family
def family(B, key, title, obs: pd.DataFrame, signals, cells, kind, rng, cluster=None, base=False):
    """obs: one row per observation with columns sym, date, t0 and the signal columns (score -1..+1; 0 = no position). Trade = sign(score) x return.
    Family p: the largest |t| over all signals x cells against the same largest |t| when the scores are shuffled across observations 2,000 times
    (or, with `cluster`, when each event's whole set of signs is flipped at random after removing each window's average return)."""
    last = LAST[kind]; E = {c: [entry(B, r.sym, r.date, int(r.t0), c[0], c[1]) for r in obs.itertuples()] for c in {(c[0], c[1], None) for c in cells}}
    R = {c: np.array([ret(B, r.sym, e, c[2], last) for r, e in zip(obs.itertuples(), E[(c[0], c[1], None)])], float) for c in cells}
    S = {s: np.where(np.sign(pd.to_numeric(obs[s], errors="coerce").fillna(0).to_numpy(float)) == 0, np.nan, np.sign(pd.to_numeric(obs[s], errors="coerce").fillna(0).to_numpy(float))) for s in signals}
    if cluster is not None:
        cid = pd.factorize(obs[cluster])[0]; nC = cid.max() + 1 if len(cid) else 0; R = {c: v - np.nanmean(v) if np.isfinite(v).any() else v for c, v in R.items()}
        def ev(v): ok = np.isfinite(v); s_ = np.bincount(cid[ok], weights=v[ok], minlength=nC); n_ = np.bincount(cid[ok], minlength=nC); return np.where(n_ > 0, s_ / np.maximum(n_, 1), np.nan)
        V = {(s, c): ev(S[s] * R[c]) for s in signals for c in cells}
    else: V = {(s, c): S[s] * R[c] for s in signals for c in cells}
    out = [dict(signal=s, cell=_lab(c), _c=c, **_stat(V[(s, c)])) for s in signals for c in cells]; ok = [o for o in out if np.isfinite(o["t"])]
    res = dict(key=key, title=title, n_obs=int(len(obs)), cells=[{k: v for k, v in o.items() if k != "_c"} for o in out], p_family=None, best=None, verdict="no cell has 30 observations", checks={})
    if not ok: return res
    best = max(ok, key=lambda o: abs(o["t"])); nmax = np.zeros(N_NULL); keys = [(o["signal"], o["_c"]) for o in ok]
    for i in range(N_NULL):
        if cluster is not None: f = rng.choice([-1.0, 1.0], nC); m = max(abs(_stat(V[k] * f)["t"]) for k in keys)
        else: perm = rng.permutation(len(obs)); m = max((abs(t) for t in (_stat(S[s][perm] * R[c])["t"] for s, c in keys) if np.isfinite(t)), default=0.0)
        nmax[i] = m if np.isfinite(m) else 0.0
    p = float((nmax >= abs(best["t"]) - 1e-12).mean()); s, c = best["signal"], best["_c"]; cost = COST[kind]; intraday = c[2] in ("eod",) or isinstance(c[2], int)
    passes = p < BAR and best["mean"] > cost
    res.update(p_family=p, best={k: v for k, v in best.items() if k != "_c"}, verdict=(("SUBJECTIVE grade A candidate" if intraday else "QUANT candidate (held past the session)") if passes else (("family p below the bar, but prices moved AGAINST the score -- not a pass, recorded" if best["mean"] < 0 else "family p below the bar but the mean does not cover the cost") if p < BAR else "does not pass")))
    # checks on the best cell (reported whatever the verdict)
    v = S[s] * R[c] if cluster is None else S[s] * R[c]; fin = np.isfinite(v); order = np.argsort(obs["stamp"].to_numpy()[fin]); vv = v[fin][order]; ch = {}
    ch["net of cost"] = round(float(vv.mean() - cost), 1); ch["four periods (mean bp; n)"] = [(round(float(q.mean()), 1), int(len(q))) for q in np.array_split(vv, 4)]
    ch["without the ten largest moves"] = round(float(np.delete(vv, np.argsort(-np.abs(vv))[:10]).mean()), 1) if len(vv) > 40 else None
    sc = np.abs(pd.to_numeric(obs[s], errors="coerce").to_numpy(float)); ch["score size: |score| 0.5+ vs below (mean bp; n)"] = [(round(float(np.nanmean(v[fin & m_])), 1) if (fin & m_).sum() else None, int((fin & m_).sum())) for m_ in (sc >= 0.5, sc < 0.5)]
    pl = np.array([S[s][i] * (lambda a, b: np.log(b / a) * 1e4 if np.isfinite(a) and np.isfinite(b) and a > 0 else np.nan)(B.p(r.sym, r.date, int(r.t0) - 35), B.p(r.sym, r.date, int(r.t0) - 5)) for i, r in enumerate(obs.itertuples())], float)
    st = _stat(pl); ch["before the stamp (the 30 minutes ending 5 minutes before it; should be near 0)"] = dict(n=st["n"], mean=_r(st["mean"]), t=_r(st["t"], 2))
    if base and c[0] == "ext":      # price-only comparison: follow the stock's own move from 5 minutes before the stamp to the entry
        mv = np.array([(lambda a, b: np.sign(b - a) if np.isfinite(a) and np.isfinite(b) else np.nan)(B.p(r.sym, r.date, int(r.t0) - 5), B.p(r.sym, r.date, int(r.t0) + c[1])) for r in obs.itertuples()], float); mv[mv == 0] = np.nan
        b_ = _stat(mv * R[c]); ag = _stat((S[s] * R[c])[mv == S[s]]); dg = _stat((S[s] * R[c])[mv == -S[s]])
        ch["price-only rule at the same cell (follow the move so far)"] = dict(n=b_["n"], mean=_r(b_["mean"]), t=_r(b_["t"], 2)); ch["score rule when the move so far AGREES with the score / DISAGREES"] = [dict(n=ag["n"], mean=_r(ag["mean"])), dict(n=dg["n"], mean=_r(dg["mean"]))]
    res["checks"] = ch; return res


# ------------------------------------------------------------------------------------------------ the observations
def _load():
    S = pd.read_csv(PROC / "ai_earnings_scores.csv", parse_dates=["accepted_ny"]); E = pd.read_csv(PROC / "ai_events_scores.csv", parse_dates=["accepted_ny"])
    for D in (S, E): D["stamp"] = D["accepted_ny"]; D["date"] = D["accepted_ny"].dt.normalize(); D["t0"] = D["accepted_ny"].dt.hour * 60 + D["accepted_ny"].dt.minute; D["sym"] = D["ticker"]
    for c in ("material", "fcf_outlook", "uncertainty", "own_stock", "market"): E[c] = pd.to_numeric(E[c], errors="coerce")
    return S, E


def _mentions(D: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for r in D.itertuples():
        try: A = json.loads(r.affected) if isinstance(r.affected, str) else []
        except Exception: A = []
        for a in (A or []):
            if not isinstance(a, dict): continue
            nm = str(a.get("company") or "").upper().strip(); tk = nm if nm in US + FOREIGN else NAMES.get(nm, next((v for k_, v in NAMES.items() if k_ in nm), None))
            try: dr = float(a.get("direction") or 0)
            except Exception: dr = 0.0
            if tk and tk != r.ticker and dr != 0: rows.append(dict(event=r.accession, reporter=r.ticker, sym=tk, date=r.date, t0=r.t0, stamp=r.stamp, direction=dr, reporter_own=r.own_stock, relation=str(a.get("relation"))))
    return pd.DataFrame(rows)


def build():
    S, E = _load(); eq0 = pd.Timestamp("2018-05-01"); F = {}
    u = S[S.ticker.isin(US) & S.t0.between(960, 1000)]; g = u.groupby("date"); d1 = g[SIG1].mean().reset_index(); d1["t0"] = g["t0"].max().to_numpy(); d1["stamp"] = d1["date"]; d1["sym"] = "NQ"; d1["n_releases"] = g.size().to_numpy()
    ext = [("ext", k, x) for k in (1, 5, 15) for x in (15, 30, "eod", "open", "close")]; ext_s = [("ext", k, x) for k in (1, 5, 15) for x in (15, 30, 60, "open", "close")]
    ev_cells = [("ext", 5, 30), ("ext", 5, 60), ("ext", 5, "open"), ("open", 0, 30), ("open", 0, 60), ("open", 0, "close"), ("open", 0, "close+1")]
    F["F1"] = dict(title="Results releases stamped 16:00-16:40 (US filers) -> the Nasdaq-100 future. One observation per day: the average score of that afternoon's releases, entry counted from the last stamp. From June 2010.", obs=d1, signals=SIG1, cells=ext, kind="future")
    s2 = S[S.ticker.isin(US) & (S.date >= eq0)].copy(); F["F2"] = dict(title="Results releases (US filers) -> the company's OWN stock, extended hours included. From May 2018.", obs=s2, signals=SIG1, cells=ext_s, kind="stock", base=True)
    m3 = _mentions(s2); F["F3"] = dict(title="Results releases -> the OTHER listed companies the reader named as affected. `direction` = the reader's sign for that company; `reporter_own` = simply copy the reporter's own sign (the 'everything moves together' rule).", obs=m3, signals=["direction", "reporter_own"], cells=ext_s, kind="stock", cluster="event")
    e4 = E[E.ticker.isin(US) & (E.date >= eq0) & (E.material >= 0.2)].copy(); e4["neg_uncertainty"] = -e4["uncertainty"]; sig4 = []
    for s in ("own_stock", "fcf_outlook", "neg_uncertainty"):
        for th in (0.2, 0.3, 0.5): e4[f"{s} | material {th}+"] = e4[s].where(e4.material >= th, 0.0); sig4.append(f"{s} | material {th}+")
    F["F4"] = dict(title="Other company events (US filers, material 0.2+ / 0.3+ / 0.5+) -> the company's OWN stock. `neg_uncertainty` = sell when the event raises uncertainty. From May 2018.", obs=e4, signals=sig4, cells=ev_cells, kind="stock")
    m5 = _mentions(e4[e4.material >= 0.3]); F["F5"] = dict(title="Other company events (material 0.3+) -> the OTHER listed companies named as affected.", obs=m5, signals=["direction", "reporter_own"], cells=ev_cells, kind="stock", cluster="event")
    e6 = E[E.ticker.isin(US) & (E.material >= 0.3)].copy(); e6["sym"] = "NQ"; sig6 = []
    for s in ("market", "own_stock"):
        for th in (0.3, 0.5): e6[f"{s} | material {th}+"] = e6[s].where(e6.material >= th, 0.0); sig6.append(f"{s} | material {th}+")
    F["F6"] = dict(title="Other company events (US filers, material 0.3+ / 0.5+) -> the Nasdaq-100 future. From June 2010.", obs=e6, signals=sig6, cells=[("ext", 5, 30), ("ext", 5, 60), ("open", 0, 30), ("open", 0, 60), ("open", 0, "close")], kind="future")
    f7 = pd.concat([S[S.ticker.isin(FOREIGN)][["ticker", "sym", "date", "t0", "stamp", "own_stock", "accession"]], E[E.ticker.isin(FOREIGN) & (E.material >= 0.3)][["ticker", "sym", "date", "t0", "stamp", "own_stock", "accession"]]], ignore_index=True); f7 = f7[f7.date >= eq0]
    F["F7"] = dict(title="Foreign filers (TSMC; SK Hynix once its prices are on disk): results, monthly revenue and material events -> own stock, entered at the next regular session because the SEC stamp can be hours after the release in Asia. From May 2018.", obs=f7, signals=["own_stock"], cells=[("open", 0, 30), ("open", 0, 60), ("open", 0, "close"), ("open", 0, "close+1")], kind="stock")
    need = {}
    for f in F.values():
        for sym, g_ in f["obs"].groupby("sym") if len(f["obs"]) else []: need.setdefault(sym, set()).update(g_["date"])
    return F, load_book(need)


def cmd_coverage():
    F, B = build(); print("stocks with minute prices on disk: " + ", ".join(sorted(s for s in B.d if s not in ("NQ", "ES"))) + "   | missing: " + (", ".join(s for s in US + FOREIGN if s not in B.d) or "none"))
    for k, f in F.items():
        o = f["obs"]; n = len(o); kind = f["kind"]; c0 = f["cells"][0]; have = sum(np.isfinite(B.p(r.sym, e[0], e[1])) for r, e in ((r, entry(B, r.sym, r.date, int(r.t0), c0[0], c0[1])) for r in o.itertuples()) if e is not None) if n else 0
        print(f"  {k}: {n} observations ({kind}); a price at the first entry point ({_lab(c0).split(',')[0]}) for {have}; {len(f['signals'])} signals x {len(f['cells'])} windows = {len(f['signals']) * len(f['cells'])} cells")
    print("No returns were computed.")


def cmd_run():
    F, B = build(); rng = np.random.default_rng(SEED); out = {}; L = ["# AI-chain news test: do Claude's scores of company news tell where prices go next?", "",
        f"Registered in `docs/prereg_ai_chain.md` before running. Trade = sign(score) x return after the text is public (SEC stamp, New York time). Returns in bp (1 bp = 0.01%), before cost. A cell is shown only with {MIN_N}+ observations. "
        f"Family p = how often shuffled scores produce a best cell as strong as the real best cell. A family passes at p < {BAR:.4f} (0.05 / 7 families) with a mean above the cost ({COST['future']:.0f} bp future, {COST['stock']:.0f} bp stock, assumed).", ""]
    for k, f in F.items():
        if not len(f["obs"]): out[k] = dict(key=k, title=f["title"], verdict="no observations"); L += [f"## {k}. {f['title']}", "", "No observations.", ""]; print(f"{k}: no observations"); continue
        r = family(B, k, f["title"], f["obs"].reset_index(drop=True), f["signals"], f["cells"], f["kind"], rng, cluster=f.get("cluster"), base=f.get("base", False)); out[k] = r; cells = list(dict.fromkeys(c["cell"] for c in r["cells"]))
        L += [f"## {k}. {f['title']}", "", f"Observations: {r['n_obs']}." + (" Unit = one event (its named companies averaged); each window's average return removed first." if f.get("cluster") else ""), "", "| signal | " + " | ".join(cells) + " |", "|---|" + "---|" * len(cells)]
        for s in f["signals"]:
            row = []
            for c in cells:
                o = next(x for x in r["cells"] if x["signal"] == s and x["cell"] == c); txt = "n " + str(o["n"]) if not np.isfinite(o["mean"]) else f"{o['mean']:+.1f} bp, {o['hit']:.0%}, n {o['n']}"
                row.append(f"**{txt}**" if r["best"] and o["signal"] == r["best"]["signal"] and o["cell"] == r["best"]["cell"] else txt)
            L.append(f"| {s} | " + " | ".join(row) + " |")
        if r["best"]:
            b = r["best"]; L += ["", f"**Best cell:** {b['signal']}; {b['cell']}: {b['mean']:+.1f} bp, t {b['t']:+.2f}, right on {b['hit']:.0%} of {b['n']}. **Family p = {r['p_family']:.4f}** -> **{r['verdict']}**.", "", "Checks on the best cell:"] + [f"- {kk}: {json.dumps(vv, default=lambda z: None if z != z else float(z))}" for kk, vv in r["checks"].items()]
            print(f"{k}: n {r['n_obs']}; best = {b['signal']}; {b['cell']}: {b['mean']:+.1f} bp, t {b['t']:+.2f}, hit {b['hit']:.0%}, n {b['n']}; family p {r['p_family']:.4f} -> {r['verdict']}")
            for kk, vv in r["checks"].items(): print(f"      {kk}: {json.dumps(vv, default=lambda z: None if z != z else float(z))}")
        else: L += ["", f"**{r['verdict']}.**"]; print(f"{k}: n {r['n_obs']}; {r['verdict']}")
        L.append("")
    DOCS.mkdir(exist_ok=True); (DOCS / "ai_chain_test.md").write_text("\n".join(L) + "\n"); (DOCS / "ai_chain_test.json").write_text(json.dumps(out, indent=1, default=lambda z: None if isinstance(z, float) and z != z else (float(z) if isinstance(z, (np.floating, np.integer)) else str(z))))
    print("-> docs/ai_chain_test.md, docs/ai_chain_test.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["coverage", "run"]); a = ap.parse_args(); {"coverage": cmd_coverage, "run": cmd_run}[a.cmd]()
