"""mw_direction.py -- test MW-2 (TRACK 3.146): can a Treasury auction result be TRADED, and how much does a late source cost?

MW-1 (TRACK 3.143, result in 3.146) showed that the four futures move more than usual after an auction closes. It gave no direction. A rule needs a direction.
Two ways to get a direction from what is on disk, both free:

  SIGNAL A, 'the first move': which way the 10-year note future went in the first 5 minutes after the auction closed. Up = the auction was taken well.
            The trade goes the same way. (If the trade loses, the opposite trade -- against the first move -- wins by the same amount before cost.)
  SIGNAL B, 'demand': the auction's bid-to-cover (how many dollars were bid for every dollar sold) against the average of the six auctions of the same
            term before it. Higher = strong demand = buy; lower = sell.

THE LAG IS PART OF THE GRID. The trade is entered 1, 3, 5, 10, 15, 30 or 60 minutes after the auction closed (signal A cannot start before minute 5).
A fast source lets us enter at minute 1 to 5; a source that shows the result 30 minutes late can only enter at minute 30 or later. Reading the result
across the entry minutes IS the answer to 'how much does the lag cost'.

Grid: 2 signals x entry minute x holding time (15, 30, 60 minutes, or until 15:59 New York) x 4 futures x 7 situations
      (all auctions | short terms 2 to 7 years | long terms 10 to 30 years | each of the main page's four market conditions).
Measure of a cell: the average result in basis points (1 bp = 0.01%), signed by the signal, BEFORE cost.
Chance:  signal A -- the same trade on the 20 sessions before with no auction at that minute (a first move continues or not on ordinary days too);
                     5,000 draws of one ordinary day per auction.   signal B -- 5,000 shuffles of which auction had strong demand.
Verdict: ONE per signal, on the whole grid: how often the strongest cell of a draw is at least as strong as the strongest real cell. Under 0.05 = more than luck.
         Single cells are shown with their own chance but get no verdict.

    python -m src.mw_direction run        # free, no download; needs the futures history and the auction list of src/mw_auctions.py; several minutes
"""
from __future__ import annotations
import argparse, re
import numpy as np, pandas as pd
from src import mw_auctions as MA

ENTRY = [1, 3, 5, 10, 15, 30, 60]; HOLD = [15, 30, 60, "close"]; FIRST = 5; PRIOR = 6; NDRAW = 5000; CLOSE_M = 15 * 60 + 59 - MA.M0; NOTE = "10-year Treasury note futures"
STEP_BP = {"S&P 500 futures": 0.4, "Nasdaq-100 futures": 0.2, "gold futures": 0.3, "10-year Treasury note futures": 1.4}      # one price step as a share of the price, roughly (an assumption, stated in the report)


def _years(term: str) -> int:
    y = re.search(r"(\d+)-Year", term); mth = re.search(r"(\d+)-Month", term); return (int(y.group(1)) if y else 0) + (1 if mth else 0)      # '9-Year 10-Month' is a 10-year note sold again


def _ret(G, i, a, b):
    if a < 0 or b >= G.shape[1] or b <= a: return np.nan
    return G[i, b] / G[i, a] - 1


def cmd_run(ndraw=NDRAW):
    f = MA.MW / "auctions.csv"
    if not f.exists(): print("run `python -m src.mw_auctions auctions` first"); return
    A = pd.read_csv(f, parse_dates=["day"]).sort_values("day"); A["m"] = A.close_h * 60 + A.close_m - MA.M0; A["years"] = A.term.map(_years)
    A["surprise"] = A.bid_to_cover - A.groupby("years").bid_to_cover.transform(lambda s: s.shift(1).rolling(PRIOR, min_periods=PRIOR).mean())
    ev = A.groupby(["day", "m"], as_index=False).agg(surprise=("surprise", "mean"), years=("years", "max")); clock = set(zip(ev.day, ev.m)); rng = np.random.default_rng(20261128)
    grids = {}
    for name, root in MA.ROOTS.items():
        days, G = MA._grid(root)
        if days is not None: grids[name] = (days, G, {d: i for i, d in enumerate(days)})
    if NOTE not in grids: print("no prices of the 10-year note future on disk: run `python -m src.mw_auctions fetch` first"); return
    nd, nG, npos = grids[NOTE]
    try:
        from src.leading import _conditions
        lab, names = _conditions(pd.DatetimeIndex(ev.day) - pd.Timedelta(days=1))      # the condition known the day before
    except Exception as e: print(f"  (market conditions not loaded: {type(e).__name__}: {str(e)[:80]})"); lab, names = None, {}
    n = len(ev); SUB = {"all auctions": np.ones(n, bool), "short terms (2 to 7 years)": (ev.years <= 7).to_numpy(), "long terms (10 to 30 years)": (ev.years >= 10).to_numpy()}
    if lab is not None:
        lv = np.asarray(lab)
        for k in sorted({int(x) for x in lv[pd.notna(lv)]}): SUB[f"market condition: {names.get(k, f'condition {k + 1}')}"] = np.array([pd.notna(x) and int(x) == k for x in lv])
    # the sign of signal A on the auction day and on each of the 20 ordinary sessions before it (from the note future's first 5 minutes)
    sA = np.full(n, np.nan); sAp = np.full((n, MA.BEFORE), np.nan); prevs = []
    for e, (d, m) in enumerate(zip(ev.day, ev.m)):
        i = npos.get(d); pv = []
        if i is not None:
            sA[e] = np.sign(_ret(nG, i, m, m + FIRST)); pv = [j for j in range(i - 1, -1, -1) if (nd[j], m) not in clock][:MA.BEFORE]
            for k, j in enumerate(pv): sAp[e, k] = np.sign(_ret(nG, j, m, m + FIRST))
        prevs.append([nd[j] for j in pv])
    sA[sA == 0] = np.nan; sAp[sAp == 0] = np.nan; sB = np.sign(ev.surprise.to_numpy(float)); sB[sB == 0] = np.nan
    pick = rng.integers(0, MA.BEFORE, size=(ndraw, n)); perm = np.array([rng.permutation(n) for _ in range(ndraw)]); rows = []; ZA = []; ZB = []; ar = np.arange(n)
    print(f"{n} auction closings; signal A known for {int(np.isfinite(sA).sum())}, signal B for {int(np.isfinite(sB).sum())}; {len(SUB)} situations; {ndraw:,} draws. This takes several minutes.")
    for name, (days, G, pos) in grids.items():
        for E in ENTRY:
            for H in HOLD:
                r = np.full(n, np.nan); rp = np.full((n, MA.BEFORE), np.nan)
                for e, (d, m) in enumerate(zip(ev.day, ev.m)):
                    i = pos.get(d); b = CLOSE_M if H == "close" else m + E + H
                    if i is None: continue
                    r[e] = _ret(G, i, m + E, b)
                    for k, pdx in enumerate(prevs[e]):
                        j = pos.get(pdx)
                        if j is not None: rp[e, k] = _ret(G, j, m + E, b)
                for sig in ("A", "B"):
                    if sig == "A" and E < FIRST: continue
                    x = (sA if sig == "A" else sB) * r
                    if sig == "A": D = (sAp * rp)[ar, pick]      # ndraw x n: the same trade on one ordinary day per auction
                    else: D = sB[perm] * r      # ndraw x n: the demand signs handed to other auctions
                    for sname, mask in SUB.items():
                        xs = x[mask]; k = int(np.isfinite(xs).sum())
                        if k < 30: continue
                        mean = float(np.nanmean(xs)); dm = np.nanmean(D[:, mask], axis=1); mu = float(np.nanmean(dm)); sd = float(np.nanstd(dm))
                        if not sd > 0: continue
                        z = (mean - mu) / sd; zd = (dm - mu) / sd; p = float((np.sum(np.abs(zd) >= abs(z)) + 1) / (ndraw + 1))
                        rows.append(dict(signal=sig, future=name, entry=E, hold=H, situation=sname, n=k, bp=mean * 1e4, ordinary_bp=mu * 1e4, right=float(np.nanmean(xs[np.isfinite(xs)] > 0)), z=z, chance=p)); (ZA if sig == "A" else ZB).append(zd)
        print(f"  {name}: done")
    R = pd.DataFrame(rows)
    if R.empty: print("no cell had 30 auctions with prices"); return
    verdict = {}
    for sig, Z in (("A", ZA), ("B", ZB)):
        g = R[R.signal == sig]
        if g.empty: continue
        mx = np.nanmax(np.abs(np.vstack(Z)), axis=0); top = float(g.z.abs().max()); verdict[sig] = (float((np.sum(mx >= top) + 1) / (ndraw + 1)), len(g), top)
    R.to_csv(MA.DOCS / "mw_direction.csv", index=False); f1 = lambda v: f"{v:+.1f}"; hl = lambda h: "until 15:59" if h == "close" else f"{h} minutes"
    SN = {"A": "Signal A, the first move (go the way the 10-year note future went in the first 5 minutes)", "B": "Signal B, demand (buy when bid-to-cover is above the average of the last six auctions of that term, sell when below)"}
    L = ["# Test MW-2: can a Treasury auction result be traded, and what does a late source cost?", "", f"Fixed in TRACK 3.146 before running. {n} auction closings of notes and bonds since {MA.START}. All results are averages per trade in basis points (1 bp = 0.01%), BEFORE cost. "
         "A minus sign means the opposite trade would have won. 'Entry' = minutes after the auction closed at which the trade starts: a late source can only use the later entries. "
         f"'Ordinary' = what the same trade gives on days without an auction (signal A) or with the demand signs shuffled (signal B). 'Chance' is for that one cell alone; the verdict is for the whole grid of a signal ({ndraw:,} draws).",
         "Cost, as an assumption: one price step is roughly " + ", ".join(f"{v} bp for {k}" for k, v in STEP_BP.items()) + ". A trade pays about one step in and one out, so an average smaller than two steps is not tradable.", ""]
    for sig in ("A", "B"):
        if sig not in verdict: continue
        p, k, top = verdict[sig]; g = R[R.signal == sig]
        L += [f"## {SN[sig]}", "", f"**Whole grid ({k} cells): the strongest cell would be matched by luck in {p:.1%} of draws -> {'MORE THAN LUCK' if p < 0.05 else 'not more than luck'}.**", ""]
        for name in grids:
            a = g[(g.future == name) & (g.situation == "all auctions")]
            if a.empty: continue
            L += [f"### {name}, all auctions: average bp by entry minute (down) and holding time (across)", "", "| entry, minutes after the close | " + " | ".join(hl(h) for h in HOLD) + " |", "|---|" + "---|" * len(HOLD)]
            for E in ENTRY:
                c = [a[(a.entry == E) & (a.hold == H)] for H in HOLD]
                if all(x.empty for x in c): continue
                L.append(f"| {E} | " + " | ".join("" if x.empty else f"{f1(x.bp.iloc[0])} (chance {x.chance.iloc[0]:.3f})" for x in c) + " |")
            L.append("")
        b = g.reindex(g.z.abs().sort_values(ascending=False).index).head(15)
        L += ["### The 15 strongest cells of this signal (any future, any situation)", "", "| future | situation | entry | hold | auctions | average bp | ordinary bp | right, % | chance (this cell alone) |", "|---|---|---|---|---|---|---|---|---|"]
        L += [f"| {x.future} | {x.situation} | {x.entry} | {hl(x.hold)} | {x.n} | {f1(x.bp)} | {f1(x.ordinary_bp)} | {x.right:.0%} | {x.chance:.4f} |" for x in b.itertuples()] + [""]
    L += ["What this cannot say: the true surprise of an auction is its yield against the yield traded just before it closed, which is not in the public list; signal A uses the market's own first move instead, and signal B uses bid-to-cover. "
          "Prices are 1-minute closes of the most-traded contract; a real order pays the step assumed above and can slip in the first minute. Every cell is in `docs/mw_direction.csv`.",
          "Sources: US Treasury, Fiscal Data (auction list, public); Databento GLBX.MDP3 1-minute futures prices (licensed, not uploaded)."]
    (MA.DOCS / "mw_direction.md").write_text("\n".join(L) + "\n")
    for sig in ("A", "B"):
        if sig not in verdict: continue
        p, k, top = verdict[sig]; g = R[R.signal == sig]; print(f"{SN[sig]}"); print(f"  WHOLE GRID, {k} cells: chance {p:.4f} -> {'MORE THAN LUCK' if p < 0.05 else 'not more than luck'}")
        for name in grids:
            a = g[(g.future == name) & (g.situation == "all auctions")]
            for H in HOLD:
                c = a[a.hold == H].sort_values("entry")
                if len(c): print(f"    {name}, hold {hl(H)}: " + " | ".join(f"entry {x.entry}: {f1(x.bp)} bp ({x.chance:.3f})" for x in c.itertuples()))
        for x in g.reindex(g.z.abs().sort_values(ascending=False).index).head(6).itertuples(): print(f"    strongest: {f1(x.bp)} bp (ordinary {f1(x.ordinary_bp)}), right {x.right:.0%}, chance {x.chance:.4f}, {x.n} auctions | {x.future} | {x.situation} | entry {x.entry} | hold {hl(x.hold)}")
    print("-> docs/mw_direction.md, docs/mw_direction.csv")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run"]); ap.parse_args(); cmd_run()
