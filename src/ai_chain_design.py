"""ai_chain_design.py -- design questions on the AI-chain news test (founder, 17 Nov), registered in TRACK 3.67 before running; priors #156-#157.

The first test traded ONE unit in the direction of the SIGN of a score, every signal on its own. The founder's questions, as he would meet them in real
trading: (1) do two signals on the same stock in the same hour ever point opposite ways, and how often? (2) does the SIZE of the score (and for other
events the 'material' mark) carry information -- would trading only the strong scores, or sizing by the score, have earned more?

    D0  overlaps: how often signals on one stock within 60 minutes disagree (own results, own events, and other companies' releases naming it)
    D1  score size: the SAME fixed cells as before, split by the size of the score; and one test per cell -- do larger scores earn more?
        (rank correlation between |score| and the trade's return, against |score| shuffled across trades; four cells, so a cell counts at p < 0.0125)

    python -m src.ai_chain_design run        # -> docs/ai_chain_design.md, .json   (no cost; prices and scores are on disk)
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np, pandas as pd
from src.ai_chain_test import build, entry, ret, LAST, _lab, _mentions, _load, US

CELLS = [("F2", "own_stock", ("ext", 1, 60)), ("F2", "market", ("ext", 5, 30)), ("F1", "results_vs_prior_guidance", ("ext", 5, "open")), ("F4", "own_stock | material 0.2+", ("open", 0, 60))]      # the cells already on record; nothing is searched
BINS = [(0.0, 0.3), (0.3, 0.6), (0.6, 0.9), (0.9, 1.01)]; N_NULL, SEED, BAR = 5000, 20261117, 0.05 / 4


def _f(t): return f"{t[1]:+.1f} bp (n {t[0]})" if t[0] else "no trades"


def _rank(x): return pd.Series(x).rank().to_numpy()


def d0():
    S, E = _load(); eq0 = pd.Timestamp("2018-05-01"); out = {}; L = []
    own = pd.concat([S[S.ticker.isin(US) & (S.date >= eq0)][["ticker", "stamp", "own_stock"]].assign(kind="results"), E[E.ticker.isin(US) & (E.date >= eq0) & (E.material >= 0.3)][["ticker", "stamp", "own_stock"]].assign(kind="event")], ignore_index=True)
    own["own_stock"] = pd.to_numeric(own["own_stock"], errors="coerce"); own = own[own.own_stock.fillna(0) != 0].sort_values(["ticker", "stamp"]); pairs = opp = 0
    for _, g in own.groupby("ticker"):
        t = g.stamp.to_numpy(); s = np.sign(g.own_stock.to_numpy())
        for i in range(len(g) - 1):
            j = i + 1
            while j < len(g) and (t[j] - t[i]) <= np.timedelta64(60, "m"): pairs += 1; opp += s[i] != s[j]; j += 1
    out["own signals"] = dict(signals=int(len(own)), pairs_within_60_min=int(pairs), opposite=int(opp)); L.append(f"- **A company's own signals** (results and material events, from May 2018): {len(own)} signals; pairs on the same stock within 60 minutes: {pairs}; of these pointing opposite ways: {opp}.")
    M = pd.concat([_mentions(S[S.ticker.isin(US) & (S.date >= eq0)]), _mentions(E[E.ticker.isin(US) & (E.date >= eq0) & (E.material >= 0.3)])], ignore_index=True)
    if len(M):
        M["day"] = pd.to_datetime(M["stamp"]).dt.normalize(); M["after"] = pd.to_datetime(M["stamp"]).dt.hour >= 16; g = M[M.after].groupby(["sym", "day"])["direction"]; n = g.size(); mixed = g.apply(lambda x: (np.sign(x) > 0).any() and (np.sign(x) < 0).any())
        multi = int((n > 1).sum()); out["spill-over"] = dict(stock_afternoons=int(len(n)), with_two_or_more_mentions=multi, mixed_signs=int(mixed[n > 1].sum()))
        L.append(f"- **Other companies' releases naming a stock** (after 16:00): {len(n)} stock-afternoons with at least one mention; {multi} with two or more; of these with BOTH a positive and a negative direction for the same stock: {int(mixed[n > 1].sum())} ({(mixed[n > 1].mean() if multi else 0):.0%}).")
        R = S[S.ticker.isin(US) & (S.date >= eq0)].copy(); R["day"] = R["date"]; J = M[M.after].merge(R[["ticker", "day", "own_stock"]].rename(columns={"ticker": "sym"}), on=["sym", "day"]); J = J[pd.to_numeric(J.own_stock, errors="coerce").fillna(0) != 0]
        dis = int((np.sign(J.direction) != np.sign(pd.to_numeric(J.own_stock))).sum()); out["own results vs others' view"] = dict(cases=int(len(J)), disagree=dis)
        L.append(f"- **A stock that reports AND is named by another reporter the same afternoon:** {len(J)} cases; the other company's release points the opposite way to the stock's own results score in {dis}" + (f" ({dis / len(J):.0%})." if len(J) else "."))
    return out, L


def d1(F, B, rng):
    out = {}; L = []
    for fam, sig, cell in CELLS:
        f = F[fam]; o = f["obs"].reset_index(drop=True); last = LAST[f["kind"]]; sc = pd.to_numeric(o[sig], errors="coerce").fillna(0).to_numpy(float)
        r = np.array([ret(B, x.sym, entry(B, x.sym, x.date, int(x.t0), cell[0], cell[1]), cell[2], last) for x in o.itertuples()], float); ok = np.isfinite(r) & (sc != 0); v = np.sign(sc[ok]) * r[ok]; a = np.abs(sc[ok]); name = f"{fam}: {sig}; {_lab(cell)}"
        if ok.sum() < 30: L += [f"### {name}", "", f"Only {int(ok.sum())} trades with a price; not analysed.", ""]; out[name] = dict(n=int(ok.sum())); continue
        rows = []
        for lo, hi in BINS:
            m = (a > lo) & (a <= hi) if lo > 0 else (a > 0) & (a <= hi); rows.append(dict(bin=f"{lo:.1f} to {min(hi, 1.0):.1f}", n=int(m.sum()), mean=float(v[m].mean()) if m.sum() else None, hit=float((v[m] > 0).mean()) if m.sum() else None))
        w = float((a * v).sum() / a.sum())
        if np.unique(a).size < 2: rho, p = float("nan"), float("nan")      # every score the same size: nothing to compare
        else: rho = float(np.corrcoef(_rank(a), _rank(v))[0, 1]); null = np.array([np.corrcoef(_rank(rng.permutation(a)), _rank(v))[0, 1] for _ in range(N_NULL)]); p = float((null >= rho - 1e-12).mean())
        strong = {th: (int((a >= th).sum()), float(v[a >= th].mean()) if (a >= th).sum() else None) for th in (0.5, 0.8)}
        out[name] = dict(n=int(ok.sum()), all_mean=float(v.mean()), bins=rows, sized_by_score=w, only_strong=strong, rank_corr=rho, p=p, verdict="larger scores earn more" if p < BAR and rho > 0 else "no evidence that larger scores earn more")
        print(f"{name}\n   every signal, one unit: {v.mean():+.1f} bp (n {int(ok.sum())}) | by |score|: " + "; ".join(f"{b['bin']}: " + (f"{b['mean']:+.1f} bp, {b['hit']:.0%}, n {b['n']}" if b["n"] else "n 0") for b in rows) + f"\n   only |score| 0.5+: {_f(strong[0.5])} | only 0.8+: {_f(strong[0.8])}" + f" | sized by the score: {w:+.1f} bp per unit | rank correlation {rho:+.3f}, p {p:.4f} -> {out[name]['verdict']}")
        L += [f"### {name}", "", f"Every signal with one unit: **{v.mean():+.1f} bp** (n {int(ok.sum())}), before cost.", "", "| size of the score | trades | average | right on |", "|---|---|---|---|"] + [f"| {b['bin']} | {b['n']} | " + (f"{b['mean']:+.1f} bp | {b['hit']:.0%} |" if b["n"] else " | |") for b in rows]
        L += ["", f"- Trade only scores of 0.5 or more: {_f(strong[0.5])}. Only 0.8 or more: {_f(strong[0.8])}.", f"- Position sized by the score (a score of 1.0 trades twice the size of 0.5): {w:+.1f} bp per unit of position.", f"- Do larger scores earn more? Rank correlation between the size of the score and the trade's return: {rho:+.3f}; shuffled sizes reach this in {p:.1%} of 5,000 tries -> **{out[name]['verdict']}** (bar {BAR:.4f}).", ""]
    return out, L


def run():
    F, B = build(); rng = np.random.default_rng(SEED); o0, L0 = d0(); print("D0 overlaps:"); [print("  " + x) for x in L0]; o1, L1 = d1(F, B, rng)
    L = ["# AI-chain news: design questions (overlapping signals; the size of the score)", "", "Registered in TRACK 3.67 before running. The first test traded one unit in the direction of the SIGN of each score, every signal on its own, returns before cost. This file asks what that design left out.", "", "## D0. How often do signals on the same stock disagree?", ""] + L0 + ["", "## D1. Does the size of the score matter?", ""] + L1
    Path("docs").mkdir(exist_ok=True); Path("docs/ai_chain_design.md").write_text("\n".join(L) + "\n"); Path("docs/ai_chain_design.json").write_text(json.dumps(dict(D0=o0, D1=o1), indent=1, default=str)); print("-> docs/ai_chain_design.md, .json")


if __name__ == "__main__": run()
