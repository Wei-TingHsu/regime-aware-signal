"""cds_intraday.py -- test CDS-2 (TRACK 3.130): INSIDE the day, do shares move after a CDS trade at a wider or tighter spread -- or before it?

CDS-1 (3.129) asked the question from one day to the next and found nothing, on 266 days. The public files give every trade's time to the second, and the
1-minute share prices of the pool stocks are on disk, so the same question can be asked in minutes.

    python -m src.cds_intraday run        # free, no download; needs data_provenance/cds_public/raw (cds_public fetch) and data_provenance/intraday/eq (pool_intraday fetch)

An EVENT = a trade of a company's 5-year CDS whose spread is given in the file and differs from that company's previous such trade (at least one minute earlier,
at most 3 sessions back) by at least a threshold. Wider = credit worse. For every event: the share's move over the next 5, 15, 30 and 60 minutes (and, as the
other way round, over the same minutes BEFORE the trade). The measure is the average of (direction of the spread change) x (share move): negative = shares
fall after a widening and rise after a tightening, i.e. the CDS trade comes first.

What this cannot say: the trade's time is when it was DONE. The rule lets it be reported up to a day later, and the files do not say when each trade became
public. So a pass would mean 'the CDS market moved first', not yet 'we could have seen it in time'. Measuring the publication delay needs live collection.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np, pandas as pd

EQ = Path("data_provenance/intraday/eq"); DOCS = Path("docs"); NY = "America/New_York"
OWN = {"Oracle": "ORCL", "Amazon": "AMZN", "Meta": "META", "Microsoft": "MSFT", "Alphabet": "GOOG", "Nvidia": "NVDA", "AMD": "AMD", "Intel": "INTC", "IBM": "IBM", "Cisco": "CSCO", "Apple": "AAPL"}
AI = ["Oracle", "Amazon", "Meta", "Microsoft", "Alphabet"]; CHIPS = ["NVDA", "AMD", "AVGO", "MU", "INTC", "QCOM", "TXN", "TSM"]
HS = [5, 15, 30, 60]; THR = [0.01, 0.05]; NCOPY = 5000; MAXSHIFT = 20; MINUTES = 390


def _grid(sym: str, days: pd.DatetimeIndex) -> np.ndarray:
    """the share's price at each of the 390 minutes of each session (rows = sessions, columns = minutes after 09:30 New York); a missing minute takes the last price, at most 5 minutes old"""
    fr = [pd.read_parquet(f, columns=["close"]) for f in sorted((EQ / sym).glob("*.parquet")) if f.stem[:4].isdigit() and int(f.stem[:4]) >= days[0].year]
    if not fr: return np.full((len(days), MINUTES), np.nan)
    s = pd.concat(fr).close; s = s[~s.index.duplicated()]; ix = pd.to_datetime(s.index, utc=True).tz_convert(NY); m = (ix.hour * 60 + ix.minute) - 570; ok = (m >= 0) & (m < MINUTES)
    d = pd.DatetimeIndex(ix[ok].date); pos = days.get_indexer(d); G = np.full((len(days), MINUTES), np.nan); k = pos >= 0; G[pos[k], m[ok][k]] = s.to_numpy(float)[ok][k]
    return pd.DataFrame(G).T.ffill(limit=5).T.to_numpy()


def _events() -> pd.DataFrame:
    from src import cds_public as C
    X = C.trades(); X = X[(X.how == "given") & X.company.isin(OWN)].sort_values(["company", "t"]).copy(); out = []
    for comp, g in X.groupby("company"):
        t = g.t.dt.tz_convert("UTC").dt.tz_localize(None).to_numpy(); bp = g.bp.to_numpy(float); j = np.searchsorted(t, t - np.timedelta64(60, "s"), side="right") - 1      # the last trade at least a minute earlier
        ok = j >= 0; prev = np.where(ok, bp[np.maximum(j, 0)], np.nan); gap = np.where(ok, (t - t[np.maximum(j, 0)]) / np.timedelta64(1, "D"), np.nan)
        e = g.assign(prev=prev, gap=gap); e["chg"] = np.log(e.bp / e.prev); out.append(e[(e.gap <= 5) & e.chg.notna() & (e.chg != 0)])
    E = pd.concat(out, ignore_index=True); ny = E.t.dt.tz_convert(NY); E["day"] = pd.to_datetime(ny.dt.date); E["m"] = (ny.dt.hour * 60 + ny.dt.minute) - 570 + 1      # the first full minute after the trade
    return E[(E.m >= 1) & (E.m < MINUTES)]


def _stat(sign, d, m, G, H, back=False):
    """average of sign x share move; forward: from minute m to m+H; back: from m-1-H to m-1. G may be a list of grids (a basket: the average of the moves)."""
    Gs = G if isinstance(G, list) else [G]; a, b = (m - 1 - H, m - 1) if back else (m, m + H); ok = (a >= 0) & (b < MINUTES) & (d >= 0) & (d < Gs[0].shape[0]); r = np.full(len(d), np.nan)
    if ok.any():
        rr = np.nanmean(np.stack([g[d[ok], b[ok]] / g[d[ok], a[ok]] - 1 for g in Gs]), axis=0) if len(Gs) > 1 else Gs[0][d[ok], b[ok]] / Gs[0][d[ok], a[ok]] - 1; r[ok] = rr
    v = sign * r; k = np.isfinite(v); return (float(v[k].mean()) if k.sum() else np.nan), int(k.sum())


def cmd_run(ncopy=NCOPY):
    E = _events()
    if not len(E): print("no events: run `python -m src.cds_public fetch` first"); return
    ref = sorted((EQ / "ORCL").glob("*.parquet"))
    if not ref: print("no 1-minute prices on disk: run `python -m src.pool_intraday fetch` first"); return
    s = pd.concat([pd.read_parquet(f, columns=["close"]) for f in ref if f.stem[:4].isdigit() and int(f.stem[:4]) >= E.day.min().year]); days = pd.DatetimeIndex(sorted(set(pd.to_datetime(s.index, utc=True).tz_convert(NY).date)))
    G = {sym: _grid(sym, days) for sym in sorted(set(OWN.values()) | set(CHIPS))}; chips = [G[x] for x in CHIPS]; E["d"] = days.get_indexer(E.day); E = E[E.d >= 0].copy(); rng = np.random.default_rng(20261126)
    sets = {"the five AI spenders (Oracle, Amazon, Meta, Microsoft, Alphabet)": E[E.company.isin(AI)], "Oracle alone": E[E.company == "Oracle"]}
    tests = len(sets) * 2 * len(THR) * len(HS); bar = 0.05 / tests; rows = []
    print(f"{len(E):,} events (a CDS trade with a given spread that differs from the company's previous one) on {E.day.nunique()} days, {E.day.min():%Y-%m-%d} to {E.day.max():%Y-%m-%d}; by company: " + ", ".join(f"{c} {n}" for c, n in E.company.value_counts().items()))
    print(f"{tests} tests; limit: chance under {bar:.5f}; {ncopy:,} copies with each event day moved to another day within {MAXSHIFT} sessions (same minute of the day)")
    for sname, S in sets.items():
        for thr in THR:
            T = S[S.chg.abs() >= thr]; sign = np.sign(T.chg.to_numpy()); d = T.d.to_numpy(); m = T.m.to_numpy(); ud, inv = np.unique(d, return_inverse=True)
            def own_stat(dd, H, back=False):
                v = []
                for sym in set(OWN[c] for c in T.company):
                    k = (T.company.map(OWN) == sym).to_numpy(); a, n_ = _stat(sign[k], dd[k], m[k], G[sym], H, back); v.append((a, n_))
                tot = sum(n_ for a, n_ in v if a == a); return (sum(a * n_ for a, n_ in v if a == a) / tot if tot else np.nan), tot
            for target in ("its own share", "the chip shares (NVDA, AMD, AVGO, MU, INTC, QCOM, TXN, TSM)"):
                f = (lambda dd, H, back=False: own_stat(dd, H, back)) if target == "its own share" else (lambda dd, H, back=False: _stat(sign, dd, m, chips, H, back))
                for H in HS:
                    st, n = f(d, H); rv, nr = f(d, H, True); hits = 0; done = 0
                    if n >= 30:
                        for _ in range(ncopy):
                            sh = rng.integers(1, MAXSHIFT + 1, len(ud)) * rng.choice([-1, 1], len(ud)); z, nz = f(ud[inv] + sh[inv], H)
                            if nz >= 20 and z == z: done += 1; hits += abs(z) >= abs(st)
                    p = (hits + 1) / (done + 1) if done else np.nan
                    rows.append(dict(events=sname, threshold=thr, target=target, H=H, n=n, wider=int((sign > 0).sum()), avg_bp=st * 1e4 if st == st else np.nan, p=p, before_bp=rv * 1e4 if rv == rv else np.nan, n_before=nr, passes=bool(p == p and p < bar)))
    R = pd.DataFrame(rows); f1 = lambda x: "n/a" if x != x else f"{x:+.1f}"; f4 = lambda x: "too few" if x != x else f"{x:.4f}"
    L = ["# Test CDS-2: inside the day, do shares move after a CDS trade -- or before it?", "", f"Registered in TRACK 3.130 before running. {len(E):,} events on {E.day.nunique()} days ({E.day.min():%Y-%m-%d} to {E.day.max():%Y-%m-%d}). An event = a 5-year CDS trade whose spread is given in the public file and differs from the company's previous such trade. "
         "'After' = the share's move over the next H minutes, times the direction of the spread change, averaged, in basis points: NEGATIVE = shares fall after a widening and rise after a tightening (the CDS trade came first). 'Before' = the same over the H minutes before the trade: negative = shares had already moved that way (shares came first). "
         f"'Chance' = the share of {ncopy:,} copies, with each event day moved to another day within {MAXSHIFT} sessions at the same minute, that show an 'after' at least as large. **PASSES** = chance under {bar:.5f} (0.05 / {tests} tests); under 30 events: too few.", "",
         "| events | spread change of at least | share measured | minutes H | events (of them wider) | after, basis points (chance) | before, basis points | verdict |", "|---|---|---|---|---|---|---|---|"]
    for r in R.itertuples(): L.append(f"| {r.events} | {r.threshold:.0%} | {r.target} | {r.H} | {r.n} ({r.wider}) | {f1(r.avg_bp)} ({f4(r.p)}) | {f1(r.before_bp)} | {'**PASSES**' if r.passes else ('too few' if r.n < 30 else 'no')} |")
    L += ["", f"**{int(R.passes.sum())} of {len(R)} tests pass.**", "", "What a pass would NOT mean: the trade's time is when it was done; the rule allows it to be reported up to a day later and the files do not say when it became public. Whether it could have been seen in time needs live collection of the files.",
          "The data: public trade reports under the SEC's Regulation SBSR (DTCC), kept for our own testing, not uploaded (TRACK 3.127); 1-minute share prices from Databento (XNAS.ITCH), not uploaded."]
    DOCS.mkdir(exist_ok=True); (DOCS / "cds_intraday.md").write_text("\n".join(L) + "\n"); R.to_csv(DOCS / "cds_intraday.csv", index=False)
    print("  after, bp (chance) | before, bp | events (wider) | H min | threshold | verdict | events of ... -> share")
    for r in R.sort_values("p").itertuples(): print(f"  {f1(r.avg_bp)} ({f4(r.p)}) | {f1(r.before_bp)} | {r.n} ({r.wider}) | {r.H} | {r.threshold:.0%} | {'PASSES' if r.passes else ('too few' if r.n < 30 else 'no')} | {r.events} -> {r.target[:24]}")
    print(f"=> {int(R.passes.sum())} of {len(R)} tests pass. -> docs/cds_intraday.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run"]); ap.add_argument("--copies", type=int, default=NCOPY); a = ap.parse_args(); cmd_run(a.copies)
