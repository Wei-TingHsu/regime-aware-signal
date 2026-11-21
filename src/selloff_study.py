"""selloff_study.py -- the sell-off study, stage B (registered in TRACK 3.92 before any outcome is looked at).

Question (founder, 20 Nov 2026): under WHICH CONDITIONS does a big sell-off bounce back, and under which does it keep falling -- found by grouping the
sell-offs by their conditions alone (unsupervised), not by asking whether sell-offs bounce on average (that was tested: no).

    python -m src.selloff_study prices       # free daily prices (Yahoo) for about 130 securities and the VIX -> data_provenance/selloff/prices/
    python -m src.selloff_study filings      # for the stocks: the dates and times of every 8-K (results or other), from the SEC. Free.
    python -m src.selloff_study build        # the sell-offs and their conditions AT THE CLOSE OF THE EVENT DAY. Nothing after that day is computed.
    python -m src.selloff_study run          # groups (k-means on earlier years), what happened next (later years), the nulls -> docs/selloff_study.md

Units: 'stocks' = the S&P 100 list (processed/universe100.csv) plus the founder's AI-chain list, from 2005; 'indices and sectors' = 5 index funds and
11 sector funds, from 1999. Train = events up to 2015; test = 2016 onward (groups are fixed on train and only applied to test)."""
from __future__ import annotations
import argparse, json, os, time
from pathlib import Path
import numpy as np, pandas as pd

ROOT = Path("data_provenance/selloff"); PX = ROOT / "prices"; DOCS = Path("docs")
INDEX = ["SPY", "QQQ", "SOXX", "SMH", "IWM"]; SECTORS = ["XLK", "XLC", "XLY", "XLP", "XLE", "XLF", "XLV", "XLI", "XLB", "XLRE", "XLU"]; CHAIN = ["AMD", "NVDA", "MU", "INTC", "AVGO", "SNDK", "ORCL", "TSM", "CRWD", "GOOG", "META", "AMZN", "MSFT"]
DEFS = {"stocks": [(1, 5), (1, 7), (1, 10), (5, 10), (10, 15)], "indices and sectors": [(1, 3), (1, 4), (5, 7)]}      # (sessions, fall of X% or worse)
HORIZONS = [1, 2, 3, 5, 10]; KS = [3, 4, 5]; SPLIT = pd.Timestamp("2016-01-01"); STOCKS_FROM = pd.Timestamp("2005-01-01"); N_NULL, SEED, COST_BP = 2000, 20261124, 30.0
FEATS = ["size in units of its own usual move", "last day's move %", "where it closed in the day's range", "gap at the open %", "volume against normal", "distance below the one-year high %", "run-up over the 60 sessions before %",
         "the S&P 500 over the same sessions %", "share of large stocks down 3%+ that day", "VIX level", "VIX change over the same sessions %", "S&P 500 against its 200-day average %"]
CAUSE = ["results filing in the window", "other company filing in the window"]


def _stocks():
    u = Path("processed/universe100.csv"); s = list(pd.read_csv(u).ticker) if u.exists() else []
    if not s: print("  processed/universe100.csv not found -- only the AI-chain stocks are used (run: python -m src.events100 universe)")
    return sorted(set(s) | set(CHAIN))


def cmd_prices():
    import yfinance as yf
    PX.mkdir(parents=True, exist_ok=True); ticks = _stocks() + INDEX + SECTORS + ["^VIX"]; n = 0; bad = []
    for t in ticks:
        f = PX / f"{t.replace('^', '_')}.parquet"
        if f.exists(): continue
        try:
            d = yf.download(t, start="1998-01-01", interval="1d", progress=False, auto_adjust=True)
            if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
            d = d[["Open", "High", "Low", "Close", "Volume"]].dropna(subset=["Close"]); d.columns = ["open", "high", "low", "close", "volume"]; d.index = pd.DatetimeIndex(d.index).tz_localize(None)
            if len(d) < 300: bad.append(t); continue
            d.to_parquet(f); n += 1
        except Exception: bad.append(t)
    print(f"{len(ticks)} securities; {n} downloaded now; without prices: {bad or 'none'}. No cost. -> {PX}")


def _px():
    return {f.stem.replace("_VIX", "^VIX"): pd.read_parquet(f) for f in sorted(PX.glob("*.parquet"))}


def cmd_filings():
    if not os.environ.get("SEC_CONTACT"): raise SystemExit("SEC_CONTACT is not set")
    import src.ai_earnings as A
    FS = A._sec(); cmap = json.loads(FS.get(FS.TICKERS)); look = {v["ticker"].upper(): str(v["cik_str"]).zfill(10) for v in cmap.values()}; rows = []; bad = []
    for t in _stocks():
        tick = next((a for a in A.ALIAS.get(t, [t]) if a in look), None)
        if tick is None: bad.append(t); continue
        try: F, _ = A._all_filings(FS, look[tick])
        except Exception: bad.append(t); continue
        F = F[F.form.str.upper().isin(["8-K", "8-K/A"])]; rows += [dict(ticker=t, accepted_raw=x.accepted_raw, results="2.02" in str(x.items)) for x in F.itertuples()]; time.sleep(0.15)
    M = pd.DataFrame(rows); M["accepted_ny"] = A._ny(M["accepted_raw"]); M = M.dropna(subset=["accepted_ny"]); ROOT.mkdir(parents=True, exist_ok=True); M[["ticker", "accepted_ny", "results"]].to_csv(ROOT / "filings8k.csv", index=False)
    print(f"{len(M)} 8-K filings of {M.ticker.nunique()} companies, {M.accepted_ny.min():%Y} to {M.accepted_ny.max():%Y} ({int(M.results.sum())} results filings); no list for: {bad or 'none'}. -> {ROOT / 'filings8k.csv'}")


def _events(c: pd.Series, n: int, x: float):
    r = (c / c.shift(n) - 1) * 100; hit = np.flatnonzero((r <= -x).to_numpy()); keep = []; last = -10 ** 9
    for i in hit:
        if i - last >= max(n, 1): keep.append(i); last = i
    return keep


def cmd_build():
    P = _px()
    if "SPY" not in P or "^VIX" not in P: raise SystemExit("prices missing: run `python -m src.selloff_study prices` first")
    spy = P["SPY"].close; vix = P["^VIX"].close; stocks = [t for t in _stocks() if t in P]; R1 = pd.DataFrame({t: P[t].close.pct_change() for t in stocks}); breadth = (R1 <= -0.03).sum(axis=1) / R1.notna().sum(axis=1).clip(lower=1)
    F8 = pd.read_csv(ROOT / "filings8k.csv", parse_dates=["accepted_ny"]) if (ROOT / "filings8k.csv").exists() else pd.DataFrame(columns=["ticker", "accepted_ny", "results"]); F8 = {t: g.sort_values("accepted_ny") for t, g in F8.groupby("ticker")}
    spy200 = spy / spy.rolling(200).mean() - 1; rows = []
    for unit, ticks in (("stocks", stocks), ("indices and sectors", [t for t in INDEX + SECTORS if t in P])):
        for t in ticks:
            d = P[t]; c = d.close; idx = c.index; ret = c.pct_change(); n_all = len(c)
            for n, x in DEFS[unit]:
                for i in _events(c, n, x):
                    day = idx[i]
                    if i < n + 262 or (unit == "stocks" and day < STOCKS_FROM) or day not in spy.index or day not in vix.index: continue
                    js = spy.index.get_loc(day); jv = vix.index.get_loc(day)
                    if js < 200 or jv < n: continue
                    vol = float(ret.iloc[i - n - 60:i - n].std()); rn = float(c.iloc[i] / c.iloc[i - n] - 1); hi, lo = float(d.high.iloc[i]), float(d.low.iloc[i]); v60 = float(d.volume.iloc[i - 60:i].mean())
                    f = [rn / (vol * np.sqrt(n)) if vol > 0 else np.nan, float(ret.iloc[i]) * 100, (float(c.iloc[i]) - lo) / (hi - lo) if hi > lo else 0.5, float(d.open.iloc[i] / c.iloc[i - 1] - 1) * 100, float(d.volume.iloc[i]) / v60 if v60 > 0 else np.nan,
                         float(c.iloc[i] / c.iloc[i - 252:i + 1].max() - 1) * 100, float(c.iloc[i - n] / c.iloc[i - n - 60] - 1) * 100, float(spy.iloc[js] / spy.iloc[js - n] - 1) * 100, float(breadth.get(day, np.nan)), float(vix.iloc[jv]), float(vix.iloc[jv] / vix.iloc[jv - n] - 1) * 100, float(spy200.iloc[js]) * 100]
                    row = dict(unit=unit, definition=f"{n} session{'s' if n > 1 else ''}, -{x}% or worse", n=n, x=x, ticker=t, day=day, i=i, sessions_after=n_all - 1 - i, fall_pct=rn * 100, **dict(zip(FEATS, f)))
                    if unit == "stocks":
                        g = F8.get(t); a = idx[i - n] + pd.Timedelta(hours=16); b = day + pd.Timedelta(hours=16); w = g[(g.accepted_ny > a) & (g.accepted_ny <= b)] if g is not None else None
                        row[CAUSE[0]] = float(w is not None and bool(w.results.any())); row[CAUSE[1]] = float(w is not None and len(w) > 0 and not bool(w.results.any()))
                    rows.append(row)
    E = pd.DataFrame(rows); ROOT.mkdir(parents=True, exist_ok=True); E.to_csv(ROOT / "events.csv", index=False)
    L = ["# Sell-off study, stage B: the events and their conditions (no outcome computed)", "", "| unit | definition | events | separate days | up to 2015 (train) | 2016 onward (test) | with a results filing | with another company filing |", "|---|---|---|---|---|---|---|---|"]
    for (u, dfn), g in E.groupby(["unit", "definition"], sort=False):
        L.append(f"| {u} | {dfn} | {len(g)} | {g.day.nunique()} | {int((g.day < SPLIT).sum())} | {int((g.day >= SPLIT).sum())} | {int(g.get(CAUSE[0], pd.Series(dtype=float)).fillna(0).sum()) if u == 'stocks' else ''} | {int(g.get(CAUSE[1], pd.Series(dtype=float)).fillna(0).sum()) if u == 'stocks' else ''} |")
        print(f"  {u}; {dfn}: {len(g)} events on {g.day.nunique()} separate days; train {int((g.day < SPLIT).sum())}, test {int((g.day >= SPLIT).sum())}" + (f"; results filing {int(g[CAUSE[0]].sum())}, other filing {int(g[CAUSE[1]].sum())}" if u == "stocks" else ""))
    DOCS.mkdir(exist_ok=True); (DOCS / "selloff_events.md").write_text("\n".join(L) + "\n"); print(f"{len(E)} events in all. Conditions are as of the close of the event day; nothing after it was computed. -> {ROOT / 'events.csv'}, docs/selloff_events.md")


def _kmeans(X, k, rng, restarts=20, iters=60):
    best = None
    for _ in range(restarts):
        C = X[rng.choice(len(X), k, replace=False)]
        for _ in range(iters):
            lab = ((X[:, None, :] - C[None]) ** 2).sum(-1).argmin(1); C2 = np.array([X[lab == j].mean(0) if (lab == j).any() else C[j] for j in range(k)])
            if np.allclose(C, C2): break
            C = C2
        sse = float(((X - C[lab]) ** 2).sum())
        if best is None or sse < best[0]: best = (sse, C)
    return best[1]


def _F(y, lab, w, k):
    """weighted between-group over within-group spread of y (the larger, the more the groups differ)"""
    m = np.average(y, weights=w); num = den = 0.0
    for j in range(k):
        s = lab == j
        if s.sum() < 2: continue
        mj = np.average(y[s], weights=w[s]); num += w[s].sum() * (mj - m) ** 2; den += (w[s] * (y[s] - mj) ** 2).sum()
    return num / den if den > 0 else 0.0


def cmd_run():
    E = pd.read_csv(ROOT / "events.csv", parse_dates=["day"]); P = _px(); spy = P["SPY"].close; rng = np.random.default_rng(SEED); out = {}
    Y = np.full((len(E), len(HORIZONS)), np.nan)      # what happened next, in bp: the security minus the S&P 500 (a stock) or the fund itself (an index or sector)
    for r in E.itertuples():
        c = P[r.ticker].close; i = int(r.i); js = spy.index.get_loc(r.day)
        for a, h in enumerate(HORIZONS):
            if i + h < len(c) and js + h < len(spy): Y[r.Index, a] = ((c.iloc[i + h] / c.iloc[i] - 1) - ((spy.iloc[js + h] / spy.iloc[js] - 1) if r.unit == "stocks" else 0.0)) * 1e4
    L = ["# Sell-off study: under which conditions does a big sell-off bounce, and under which does it go on?", "",
         f"Registered in TRACK 3.92 before any outcome. Each sell-off is described by its conditions at the close of the event day; the sell-offs up to 2015 are sorted into 3, 4 or 5 groups by those conditions alone (k-means); the groups are then applied unchanged to the sell-offs from 2016 on, "
         f"and what happened over the next {', '.join(map(str, HORIZONS))} sessions is compared between groups THERE. Outcome in bp (100 bp = 1%): a stock minus the S&P 500; an index or sector fund on its own. Each day counts once however many securities fell on it. "
         f"p = how often groups assigned at random differ as much as the real ones, taking the best of all group counts and horizons ({N_NULL} shuffles). A definition counts at p < 0.05 divided by the number of definitions tested. "
         f"**A group becomes a candidate only if** the definition passes AND the group's average in the test years is beyond {COST_BP:.0f} bp (stocks; 10 bp for funds) in the same direction as in the train years AND it has that sign in both halves of the test years.", ""]
    todo = [(u, dfn, g) for (u, dfn), g in E.groupby(["unit", "definition"], sort=False)]; res = []
    for u, dfn, g in todo:
        feats = FEATS + (CAUSE if u == "stocks" else []); ok = g[feats].notna().all(axis=1).to_numpy() & np.isfinite(Y[g.index]).all(axis=1); g = g[ok]; tr = (g.day < SPLIT).to_numpy(); te = ~tr
        if tr.sum() < 90 or te.sum() < 90: res.append((u, dfn, None, f"too few events (train {int(tr.sum())}, test {int(te.sum())}; 90 needed in each)")); continue
        X = g[feats].to_numpy(float); lo, hi = np.quantile(X[tr], 0.01, axis=0), np.quantile(X[tr], 0.99, axis=0); X = np.clip(X, lo, hi); mu, sd = X[tr].mean(0), X[tr].std(0); sd[sd == 0] = 1; Z = (X - mu) / sd
        y = Y[g.index]; w = (1.0 / g.groupby("day").day.transform("size")).to_numpy(); labs = {}; cents = {}
        for k in KS: C = _kmeans(Z[tr], k, rng); cents[k] = C; labs[k] = ((Z[:, None, :] - C[None]) ** 2).sum(-1).argmin(1)
        real = {(k, a): _F(y[te, a], labs[k][te], w[te], k) for k in KS for a in range(len(HORIZONS))}; (kb, ab) = max(real, key=real.get); nulls = np.zeros(N_NULL); yt = y[te]
        for b in range(N_NULL):
            pm = rng.permutation(len(yt)); nulls[b] = max(_F(yt[pm, a], labs[k][te], w[te], k) for k in KS for a in range(len(HORIZONS)))
        p = float((nulls >= real[(kb, ab)]).mean())
        beta = np.linalg.solve(Z[tr].T @ Z[tr] + 10.0 * np.eye(Z.shape[1]), Z[tr].T @ (y[tr, 3] - y[tr, 3].mean())); pred = Z[te] @ beta; corr = float(np.corrcoef(pred, yt[:, 3])[0, 1]); pc = float((np.array([np.corrcoef(pred, yt[rng.permutation(len(yt)), 3])[0, 1] for _ in range(1000)]) >= corr).mean())
        half = g.day[te].median(); groups = []
        for j in range(kb):
            s_te = te & (labs[kb] == j); s_tr = tr & (labs[kb] == j); zc = cents[kb][j]; top = np.argsort(-np.abs(zc))[:3]; desc = "; ".join(f"{'high' if zc[q] > 0 else 'low'} {feats[q]}" for q in top)
            st = lambda m, a: (float(np.average(y[m, a], weights=w[m])), float(np.median(y[m, a])), float((y[m, a] > 0).mean())) if m.sum() else (np.nan, np.nan, np.nan)
            h1 = s_te & (g.day <= half).to_numpy(); h2 = s_te & (g.day > half).to_numpy()
            groups.append(dict(group=j + 1, what=desc, n_train=int(s_tr.sum()), n_test=int(s_te.sum()), days_test=int(g.day[s_te].nunique()), train=st(s_tr, ab)[0], test={HORIZONS[a]: st(s_te, a) for a in range(len(HORIZONS))}, first_half=st(h1, ab)[0], second_half=st(h2, ab)[0]))
        res.append((u, dfn, dict(p=p, k=kb, horizon=HORIZONS[ab], n_train=int(tr.sum()), n_test=int(te.sum()), days_test=int(g.day[te].nunique()), all_test={HORIZONS[a]: float(np.average(yt[:, a], weights=w[te])) for a in range(len(HORIZONS))}, groups=groups, benchmark_corr=corr, benchmark_p=pc), ""))
    tested = [r for r in res if r[2] is not None]; bar = 0.05 / max(1, len(tested))
    for u, dfn, R, why in res:
        L += [f"## {u}: {dfn}", ""]
        if R is None: L += [f"Not tested: {why}.", ""]; print(f"  {u}; {dfn}: not tested -- {why}"); out[f"{u}; {dfn}"] = dict(not_tested=why); continue
        thr = COST_BP if u == "stocks" else 10.0; cands = []
        for G in R["groups"]:
            m = G["test"][R["horizon"]][0]; G["candidate"] = bool(R["p"] < bar and abs(m) > thr and np.sign(m) == np.sign(G["train"]) and np.sign(G["first_half"]) == np.sign(m) and np.sign(G["second_half"]) == np.sign(m) and G["n_test"] >= 30)
            if G["candidate"]: cands.append(G)
        verdict = ("PASSES; candidate group(s): " + ", ".join(f"group {G['group']} ({'bounces' if G['test'][R['horizon']][0] > 0 else 'keeps falling'})" for G in cands)) if cands else ("passes the bar, but no group meets all the conditions" if R["p"] < bar else "does not pass")
        L += [f"Train {R['n_train']} events, test {R['n_test']} events on {R['days_test']} separate days. All test events, next sessions: " + ", ".join(f"+{h}: {v:+.0f} bp" for h, v in R["all_test"].items()) + ".",
              f"**Largest difference between groups: {R['k']} groups, {R['horizon']} sessions after. p = {R['p']:.4f} (bar {bar:.4f}) -> {verdict}.** Plain benchmark (a straight-line model on the same conditions, 5 sessions): correlation with what happened {R['benchmark_corr']:+.3f} (p {R['benchmark_p']:.3f}).", "",
              "| group | what marks it | train events | test events (days) | train average | " + " | ".join(f"test +{h}: average; middle; share up" for h in HORIZONS) + " | test first half | test second half |", "|---|---|---|---|---|" + "---|" * (len(HORIZONS) + 2)]
        for G in R["groups"]: L.append(f"| {G['group']}{' **candidate**' if G['candidate'] else ''} | {G['what']} | {G['n_train']} | {G['n_test']} ({G['days_test']}) | {G['train']:+.0f} | " + " | ".join(f"{G['test'][h][0]:+.0f}; {G['test'][h][1]:+.0f}; {G['test'][h][2]:.0%}" for h in HORIZONS) + f" | {G['first_half']:+.0f} | {G['second_half']:+.0f} |")
        L.append(""); out[f"{u}; {dfn}"] = R
        print(f"  {u}; {dfn}: train {R['n_train']}, test {R['n_test']} ({R['days_test']} days); best = {R['k']} groups at +{R['horizon']} sessions, p {R['p']:.4f} -> {verdict}; benchmark corr {R['benchmark_corr']:+.3f} (p {R['benchmark_p']:.3f})")
        for G in R["groups"]: print(f"      group {G['group']} [{G['what']}]: train {G['train']:+.0f} bp (n {G['n_train']}); test +{R['horizon']}: {G['test'][R['horizon']][0]:+.0f} bp, middle {G['test'][R['horizon']][1]:+.0f}, up {G['test'][R['horizon']][2]:.0%} (n {G['n_test']}, {G['days_test']} days); halves {G['first_half']:+.0f} / {G['second_half']:+.0f}")
    DOCS.mkdir(exist_ok=True); (DOCS / "selloff_study.md").write_text("\n".join(L) + "\n"); (DOCS / "selloff_study.json").write_text(json.dumps(dict(bar=bar, results=out), indent=1, default=lambda z: None if isinstance(z, float) and z != z else (float(z) if isinstance(z, (np.floating, np.integer)) else str(z))))
    print(f"{len(tested)} definitions tested; bar p < {bar:.4f}. -> docs/selloff_study.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["prices", "filings", "build", "run"]); a = ap.parse_args(); {"prices": cmd_prices, "filings": cmd_filings, "build": cmd_build, "run": cmd_run}[a.cmd]()
