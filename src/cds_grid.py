"""cds_grid.py -- test CDS-3 (TRACK 3.133): EVERY situation of the CDS that the data allows, not only the average one.

CDS-1 and CDS-2 asked whether CDS changes, big and small together, come before share moves. Founder, 26 Nov 2026: 'why dont we check all the situations'.
Here every cell of a grid is one situation:

  whose CDS      Oracle | Oracle against the whole credit market | the six AI borrowers together | all listed technology companies together
  what happened  a jump of 5% or more | a jump of 10% or more | any widening | a new 20-day high | a fall of 5% or more (the other side)
  what is watched   the semiconductor fund SOXX | Oracle's own share
  how long after    1, 5, 10, 20 sessions (from that day's close)

For each cell: the average move after such days minus the average move after all other days, and how unusual that is.

How 'more than luck' is decided -- and why not cell by cell. The data has about 580 days. The honest copies (the event days slid along the calendar, which keeps
their clustering) number only about 540, so no single cell can be shown at a limit as strict as 160 cells would need. The registered verdict is therefore ONE
question for the whole grid: is the strongest cell stronger than the strongest cell of the slid copies? (the 'whole-search' check used before in this project).
Cells with fewer than 8 event days are 'too few' and take no part.

    python -m src.cds_grid run       # free, no download; needs data_provenance/cds_public/raw and data_provenance/leading (python -m src.leading fetch)
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np, pandas as pd

DOCS = Path("docs"); LEAD = Path("data_provenance/leading"); HS = [1, 5, 10, 20]; TARGETS = {"the semiconductor fund (SOXX)": "SOXX", "Oracle's own share (ORCL)": "ORCL"}; MIN_EVENTS, MINSHIFT = 8, 20
TRIG = {"a jump of 5% or more": lambda c, lv: c >= np.log(1.05), "a jump of 10% or more": lambda c, lv: c >= np.log(1.10), "any widening": lambda c, lv: c > 0,
        "a new 20-day high": lambda c, lv: lv > lv.shift(1).rolling(20, min_periods=10).max(), "a fall of 5% or more": lambda c, lv: c <= -np.log(1.05)}


def _px(sym):
    for pre in ("y_", "f_"):
        f = LEAD / f"{pre}{sym}.parquet"
        if f.exists(): s = pd.read_parquet(f).iloc[:, 0]; s.index = pd.DatetimeIndex(s.index).tz_localize(None) if getattr(s.index, "tz", None) is not None else pd.DatetimeIndex(s.index); return s.dropna()
    return None


def series():
    """the four CDS series: for each, the day's change (log) and a level (log). Same building rules as CDS-1 (TRACK 3.128)."""
    from src import cds_public as C
    X = C.trades(); days = pd.DatetimeIndex(sorted(pd.to_datetime([f.stem for f in C.RAW.glob("*.parquet")]))); bd = pd.bdate_range(days.min(), days.max())
    D = X.groupby(["key", "day"]).bp.median().unstack(0).reindex(bd); L = np.log(D); cnt = D.notna().sum(); dl = L.ffill(limit=5).diff().where(L.notna())
    others = [c for c in D.columns if c not in C.NAMES and cnt[c] >= 60]; market = dl[others].median(axis=1).where(dl[others].notna().sum(axis=1) >= 8)
    tech = [c for c in D.columns if c in C.NAMES]; ai = [c for c in C.AI_DEBT if c in dl.columns]; lev = lambda ch: ch.fillna(0).cumsum().where(ch.notna())
    S = {"Oracle": (dl["Oracle"], L["Oracle"]), "Oracle against the whole credit market": (dl["Oracle"] - market, lev(dl["Oracle"] - market)),
         "the six AI borrowers together": (dl[ai].mean(axis=1), lev(dl[ai].mean(axis=1))), "all listed technology companies together": (dl[tech].mean(axis=1), lev(dl[tech].mean(axis=1)))}
    return S, bd, D


def cmd_run():
    S, bd, D = series(); P = {}
    for name, sym in TARGETS.items():
        p = _px(sym)
        if p is None: print(f"no prices of {sym} in {LEAD}: run `python -m src.leading fetch` first"); return
        P[name] = p
    cal = P["the semiconductor fund (SOXX)"].index; cal = cal[(cal >= bd[0]) & (cal <= bd[-1] + pd.Timedelta(days=45))]; n0 = int((cal <= bd[-1]).sum())      # sessions inside the CDS period; later prices only complete the look-aheads
    R = {(t, H): (P[t].reindex(cal).shift(-H) / P[t].reindex(cal) - 1).to_numpy()[:n0] for t in TARGETS for H in HS}; day = cal[:n0]
    cells = []; flags = {}
    for sname, (chg, lv) in S.items():
        chg = chg.reindex(day); lv = lv.reindex(day)
        for tname, f in TRIG.items():
            e = f(chg, lv).fillna(False).to_numpy(bool) & chg.notna().to_numpy(); flags[(sname, tname)] = e
    def zstat(e, r):
        ok = np.isfinite(r); a = r[e & ok]; b = r[~e & ok]
        if len(a) < MIN_EVENTS or len(b) < 30: return np.nan, len(a), np.nan
        sd = np.nanstd(r[ok]); return (a.mean() - b.mean()) / (sd / np.sqrt(len(a))), len(a), a.mean() - b.mean()
    shifts = list(range(MINSHIFT, n0 - MINSHIFT)); best = np.zeros(len(shifts)); obs = {}
    for (sname, tname), e in flags.items():
        for (t, H), r in R.items():
            z, n, diff = zstat(e, r); obs[(sname, tname, t, H)] = (z, n, diff, int(e.sum()))
    Z = {k: v[0] for k, v in obs.items() if v[0] == v[0]}; exceed = {k: 0 for k in Z}
    for i, k in enumerate(shifts):
        m = 0.0
        for (sname, tname), e in flags.items():
            es = np.roll(e, k)
            for (t, H), r in R.items():
                key = (sname, tname, t, H)
                if key not in Z: continue
                z, _, _ = zstat(es, r)
                if z == z:
                    m = max(m, abs(z)); exceed[key] += abs(z) >= abs(Z[key])
        best[i] = m
    top = max(Z, key=lambda k: abs(Z[k])) if Z else None; whole = float((np.sum(best >= abs(Z[top])) + 1) / (len(shifts) + 1)) if top else np.nan
    for k, (z, n, diff, ne) in obs.items(): cells.append(dict(cds=k[0], happened=k[1], watched=k[2], H=k[3], event_days=ne, used=n, diff_pct=diff * 100 if diff == diff else np.nan, z=z, chance=(exceed[k] + 1) / (len(shifts) + 1) if k in Z else np.nan))
    T = pd.DataFrame(cells); J = T[T.z.notna()].copy(); few = T[T.z.isna()]; under5 = int((J.chance < 0.05).sum())
    verdict = "MORE THAN LUCK" if whole == whole and whole < 0.05 else "NOT more than luck"
    L = ["# Test CDS-3: every situation of the CDS the data allows", "", f"Registered in TRACK 3.133 before running. {n0} sessions, {day[0]:%Y-%m-%d} to {day[-1]:%Y-%m-%d}; all in one market condition of the main page ('Rapid money growth, a high policy rate', TRACK 3.129). "
         f"{len(T)} cells = 4 CDS series x 5 things that can happen x 2 shares watched x 4 look-aheads; {len(J)} have at least {MIN_EVENTS} event days, {len(few)} are 'too few'. "
         "'Difference' = the share's average move after such a day minus its average move after all other days. 'Chance' of one cell = the share of the slid copies in which that cell is at least as strong -- a description: with this many cells about 1 in 20 will be under 0.05 by luck alone.", "",
         f"**Verdict for the whole grid: {verdict}.** The strongest cell (" + (f"{top[0]}, {top[1]}, {top[2]}, {top[3]} sessions" if top else "none") + f") is matched or beaten by the strongest cell of {whole:.0%} of the {len(shifts)} slid copies (limit 5%). "
         f"Cells with their own chance under 0.05: {under5} of {len(J)}; expected by luck alone: about {len(J) * 0.05:.0f}.", "",
         "| whose CDS | what happened that day | share watched | sessions after | event days | difference, % | chance of this cell |", "|---|---|---|---|---|---|---|"]
    for r in J.sort_values("chance").itertuples(): L.append(f"| {r.cds} | {r.happened} | {r.watched} | {r.H} | {r.used} | {r.diff_pct:+.2f} | {r.chance:.4f} |")
    L += ["", "## Too few event days to judge (under 8)", "", ", ".join(sorted({f"{r.cds}: {r.happened} ({r.event_days})" for r in few.itertuples()})) or "none"]
    # the situation of 24 Nov 2026, shown case by case
    e = flags[("Oracle", "a jump of 10% or more")]; ev = day[e]; L += ["", "## The situation of 24 Nov 2026 case by case: every past day on which Oracle's spread jumped 10% or more", "", "| day | Oracle's spread, basis points (the day before with a trade -> that day) | SOXX after 1 / 5 / 10 / 20 sessions | ORCL after 1 / 5 / 10 / 20 sessions |", "|---|---|---|---|"]
    o = D["Oracle"].reindex(day); prev = o.ffill().shift(1); f2 = lambda x: "n/a" if x != x else f"{x * 100:+.1f}%"
    print(f"{n0} sessions, {day[0]:%Y-%m-%d} to {day[-1]:%Y-%m-%d}; {len(T)} cells, {len(J)} with {MIN_EVENTS}+ event days, {len(few)} too few; {len(shifts)} slid copies")
    print(f"VERDICT FOR THE WHOLE GRID: {verdict} -- the strongest cell is matched or beaten in {whole:.0%} of the copies (limit 5%). Cells under 0.05 on their own: {under5} of {len(J)}; by luck alone about {len(J) * 0.05:.0f}.")
    print("  the 12 strongest cells: difference % (chance of the cell) | event days | sessions after | whose CDS | what happened | share watched")
    for r in J.sort_values("chance").head(12).itertuples(): print(f"    {r.diff_pct:+.2f} ({r.chance:.4f}) | {r.used} | {r.H} | {r.cds} | {r.happened} | {r.watched}")
    print(f"  every past day with an Oracle jump of 10% or more ({len(ev)}): day | spread before -> that day | SOXX after 1/5/10/20 sessions | ORCL after 1/5/10/20")
    idx = {d: i for i, d in enumerate(day)}
    for d in ev:
        i = idx[d]; a = " / ".join(f2(R[("the semiconductor fund (SOXX)", H)][i]) for H in HS); b = " / ".join(f2(R[("Oracle's own share (ORCL)", H)][i]) for H in HS)
        L.append(f"| {d:%Y-%m-%d} | {prev[d]:.0f} -> {o[d]:.0f} | {a} | {b} |"); print(f"    {d:%Y-%m-%d} | {prev[d]:.0f} -> {o[d]:.0f} | {a} | {b}")
    L += ["", "What this cannot say: the trades with a hidden size (72% of all) are not usable, so some jumps are dated a day late or missed; one market condition only; the share is bought at the close of the jump day, a few minutes after the last CDS trades counted.",
          "The data: public trade reports under the SEC's Regulation SBSR (DTCC), kept for our own testing, not uploaded (TRACK 3.127)."]
    DOCS.mkdir(exist_ok=True); (DOCS / "cds_grid.md").write_text("\n".join(L) + "\n"); T.to_csv(DOCS / "cds_grid.csv", index=False); print("-> docs/cds_grid.md, docs/cds_grid.csv")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run"]); ap.parse_args(); cmd_run()
