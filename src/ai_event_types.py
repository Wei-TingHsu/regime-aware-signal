"""ai_event_types.py -- ET-1: company announcements BY TYPE (registered in TRACK 3.89 before running).

Why (founder, 21 Nov: 'think of more tests ... maybe some of them pass and become top-block items'): the earlier test of other company events (family F4
of docs/ai_chain_test.md) POOLED every kind of announcement and did not pass. One kind may move the company's own stock while the pool does not.
Same scores (reader ai-event-v2), same minute prices already on disk, same clock (the SEC's acceptance stamp) and the same machinery as F4;
the only new thing is that each type is tested as its own family. No new data, no cost.

    python -m src.ai_event_types count      # how many events each type has (no prices)
    python -m src.ai_event_types run        # -> docs/ai_event_types.md, .json
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np, pandas as pd
import src.ai_chain_test as T

COST_BP = 30.0      # a round trip in a stock: the average measured on Interactive Brokers (docs/ai_chain_costs.md), not the 10 bp assumed in F4
MERGED = {"GROUP business news (contract or partnership; product or technology; guidance update; capital expenditure)": ["contract or partnership", "product or technology", "guidance update", "capital expenditure"],
          "GROUP trouble (legal or regulatory; cyber incident; accounting; restructuring; leadership change)": ["legal or regulatory", "cyber incident", "accounting", "restructuring", "leadership change"]}
CELLS = [("ext", 1, 15), ("ext", 1, 30), ("ext", 1, 60), ("ext", 5, 30), ("ext", 5, 60), ("ext", 5, "open"), ("open", 0, 30), ("open", 0, 60), ("open", 0, "close"), ("open", 0, "close+1")]
THS = (0.2, 0.3, 0.5)


def _events():
    _, E = T._load(); E = E[E.ticker.isin(T.US) & (E.date >= pd.Timestamp("2018-05-01")) & (E.material >= 0.2) & (E.event_type != "routine or administrative")].copy()
    E["event_type"] = E["event_type"].astype(str); E["neg_uncertainty"] = -E["uncertainty"]; return E


def _groups(E):
    G = [(k, g) for k, g in sorted(E.groupby("event_type"), key=lambda kv: -len(kv[1]))] + [(k, E[E.event_type.isin(v)]) for k, v in MERGED.items()]
    return G


def cmd_count():
    E = _events(); print(f"{len(E)} events of US filers from May 2018 with material 0.2 or more (routine filings left out). A type is tested with {T.MIN_N} or more. No prices were used.")
    for k, g in _groups(E): print(f"  {k}: " + ", ".join(f"material {th}+: {int((g.material >= th).sum())} ({int(((g.material >= th) & (g.own_stock != 0)).sum())} with a direction)" for th in THS) + ("" if len(g) >= T.MIN_N else "   -> under 30, not tested"))


def cmd_run():
    E = _events(); groups = [(k, g) for k, g in _groups(E) if len(g) >= T.MIN_N]; small = [(k, len(g)) for k, g in _groups(E) if len(g) < T.MIN_N]
    if not groups: print("no type has 30 events"); return
    B = T.load_book({sym: set(g["date"]) for sym, g in E.groupby("sym")}); rng = np.random.default_rng(20261121); bar = 0.05 / len(groups); out = dict(bar=bar, cost_bp=COST_BP, groups={}, not_tested=small)
    L = ["# ET-1: company announcements by type -- does Claude's score tell where the company's own stock goes next?", "",
         f"Registered in TRACK 3.89 before running. Events of the twelve US filers from May 2018, material 0.2 or more, routine filings left out. Trade = sign(score) x the stock's return after the SEC stamp, in bp, before cost. "
         f"Signals: `own_stock` (Claude's reading for the share) and `neg_uncertainty` (sell when the event raises uncertainty), each kept only for events of material 0.2+, 0.3+ or 0.5+. Windows: 1 or 5 minutes after the stamp held 15, 30 or 60 minutes or to the next 09:35; or entered at the next regular session and held 30 or 60 minutes, to 16:00, or to the 16:00 after. "
         f"Each type is one family: p = how often shuffled scores produce a best cell as strong as the real best cell (2,000 shuffles). {len(groups)} families are tested, so a family counts at p < {bar:.4f}. "
         f"**A type becomes a candidate only if** p is below that bar AND the best cell's average is above {COST_BP:.0f} bp (the measured cost of a round trip) AND at least three of its four time periods are positive. This is a second look at data already tested once in pooled form (F4), so a candidate is confirmed only by the forward record.", ""]
    for k, g in groups:
        o = g.reset_index(drop=True).copy(); sig = []
        for s in ("own_stock", "neg_uncertainty"):
            for th in THS: o[f"{s} | material {th}+"] = o[s].where(o.material >= th, 0.0); sig.append(f"{s} | material {th}+")
        r = T.family(B, k, k, o, sig, CELLS, "stock", rng); res = dict(n=int(len(o)), verdict="no cell has 30 observations")
        if r["best"]:
            b = r["best"]; per = [x[0] for x in r["checks"].get("four periods (mean bp; n)", [])]; pos = sum(1 for x in per if x is not None and x > 0)
            cand = r["p_family"] < bar and b["mean"] > COST_BP and pos >= 3
            verdict = "CANDIDATE (to be confirmed by the forward record)" if cand else ("p below the bar but prices moved AGAINST the score" if (r["p_family"] < bar and b["mean"] < 0) else ("p below the bar but the average does not cover the cost or is not steady over time" if r["p_family"] < bar else "does not pass"))
            res = dict(n=int(len(o)), p=r["p_family"], best_signal=b["signal"], best_cell=b["cell"], mean=b["mean"], t=b["t"], hit=b["hit"], n_cell=b["n"], after_cost=b["mean"] - COST_BP, periods=r["checks"].get("four periods (mean bp; n)"), without_ten_largest=r["checks"].get("without the ten largest moves"), before_stamp=r["checks"].get("before the stamp (the 30 minutes ending 5 minutes before it; should be near 0)"), verdict=verdict)
            L += [f"## {k} ({len(o)} events)", "", f"**Best cell:** {b['signal']}; {b['cell']}: {b['mean']:+.1f} bp before cost ({b['mean'] - COST_BP:+.1f} after {COST_BP:.0f} bp), t {b['t']:+.2f}, right on {b['hit']:.0%} of {b['n']}. **Family p = {r['p_family']:.4f}** (bar {bar:.4f}) -> **{verdict}**.",
                  f"Four periods in time order (average bp; events): {res['periods']}. Without the ten largest moves: {res['without_ten_largest']} bp. The 30 minutes before the stamp: {res['before_stamp']}.", "", "| signal | " + " | ".join(dict.fromkeys(c["cell"] for c in r["cells"])) + " |", "|---|" + "---|" * len(CELLS)]
            cells = list(dict.fromkeys(c["cell"] for c in r["cells"]))
            for s in sig: L.append(f"| {s} | " + " | ".join((lambda x: "n " + str(x["n"]) if not np.isfinite(x["mean"]) else f"{x['mean']:+.0f} bp, {x['hit']:.0%}, n {x['n']}")(next(x for x in r["cells"] if x["signal"] == s and x["cell"] == c)) for c in cells) + " |")
            L.append(""); print(f"  {k} ({len(o)}): best = {b['signal']}; {b['cell']}: {b['mean']:+.1f} bp ({b['mean'] - COST_BP:+.1f} after cost), t {b['t']:+.2f}, right {b['hit']:.0%} of {b['n']}; family p {r['p_family']:.4f}; four periods {per} -> {verdict}")
        else: L += [f"## {k} ({len(o)} events)", "", "No cell has 30 priced observations.", ""]; print(f"  {k} ({len(o)}): no cell has 30 priced observations")
        out["groups"][k] = res
    if small: L += ["## Not tested (under 30 events)", "", ", ".join(f"{k} ({n})" for k, n in small), ""]; print("  not tested (under 30): " + ", ".join(f"{k} {n}" for k, n in small))
    Path("docs").mkdir(exist_ok=True); Path("docs/ai_event_types.md").write_text("\n".join(L) + "\n"); Path("docs/ai_event_types.json").write_text(json.dumps(out, indent=1, default=lambda z: None if isinstance(z, float) and z != z else (float(z) if isinstance(z, (np.floating, np.integer)) else str(z))))
    print(f"{len(groups)} families tested; bar p < {bar:.4f}; cost {COST_BP:.0f} bp. -> docs/ai_event_types.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["count", "run"]); a = ap.parse_args(); {"count": cmd_count, "run": cmd_run}[a.cmd]()
