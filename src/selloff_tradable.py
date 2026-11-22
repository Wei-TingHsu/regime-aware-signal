"""selloff_tradable.py -- test SO-T: can the strong patterns of the machine search be ACTED ON? (registered in TRACK 3.103 before it runs)

The search (TRACK 3.101) measured everything from the CLOSE of the sell-off day. Nobody can trade at a close he has only just seen. This test takes every
CANDIDATE pattern of the one group that beat luck (stocks, one day -5% or worse) exactly as the machine found it -- the same sell-offs, rebuilt with the same
seed -- and measures the trade a user could really make: ENTER AT THE NEXT OPEN, in the direction the pattern says, against the S&P 500, exit at the close of
the pattern's own horizon, minus a cost of 30 basis points for the round trip. Other exits (1, 2, 3, 5 sessions) are shown beside it.

What this test can and cannot do: the patterns were chosen on these same years, so a good number here is flattered. A pattern that FAILS here is dead; a
pattern that PASSES is only allowed into the forward record, where the real verdict comes.

    python -m src.selloff_tradable run      # no download, no cost -> docs/selloff_tradable.md, .json
"""
from __future__ import annotations
import argparse, json, re
import numpy as np, pandas as pd
from src import selloff_search as S
from src.selloff_study import ROOT, DOCS, _px

COST, EXITS, NBOOT, GROUP = 30.0, [1, 2, 3, 5], 5000, "stocks, one day -5% or worse"


def _boot(day_vals: pd.Series, rng) -> float:
    """share of month-resampled averages at or below zero (whole calendar months are drawn, so days of one month stay together)"""
    m = day_vals.index.year * 12 + day_vals.index.month; g = day_vals.groupby(m); sums = g.sum().to_numpy(); cnt = g.size().to_numpy(); k = len(sums)
    if k < 6: return float("nan")
    pick = rng.integers(0, k, size=(NBOOT, k)); return float(((sums[pick].sum(1) / cnt[pick].sum(1)) <= 0).mean())


def cmd_run(everything: bool):
    J = json.loads((DOCS / "selloff_search.json").read_text())[GROUP]; pats = [p for p in J["patterns"] if everything or p.get("candidate")]
    if not pats: raise SystemExit("no candidate pattern in docs/selloff_search.json")
    E = pd.read_csv(ROOT / "events.csv", parse_dates=["day"]); E["event_id"] = E.index; P = _px(); unit, dfn = S.BASES[GROUP]; rng = np.random.default_rng(S.SEED)
    B = E[(E.unit == unit) & (E.definition == dfn)].sort_values("day").reset_index(drop=True); Y, names, mv = S._outcomes(B, P); ok = np.isfinite(Y).all(axis=1); B = B[ok].reset_index(drop=True)
    disc = (B.day < S.SPLIT).to_numpy(); items = S._items(B, disc, rng); by_label = {it[2]: it[3] for it in items}      # the same items the search used (same seed, same order of calls)
    spy = P["SPY"]; n = len(B); gap = np.full(n, np.nan); OC = {h: np.full(n, np.nan) for h in EXITS}; OCraw = {h: np.full(n, np.nan) for h in EXITS}; CC = {h: np.full(n, np.nan) for h in EXITS}
    for q, r in enumerate(B.itertuples()):
        d = P[r.ticker]; c, o = d.close, d.open; i = int(r.i); js = spy.index.get_loc(r.day); s, so = spy.close, spy.open
        gap[q] = ((o.iloc[i + 1] / c.iloc[i] - 1) - (so.iloc[js + 1] / s.iloc[js] - 1)) * 1e4
        for h in EXITS:
            OCraw[h][q] = (c.iloc[i + h] / o.iloc[i + 1] - 1) * 1e4; OC[h][q] = OCraw[h][q] - (s.iloc[js + h] / so.iloc[js + 1] - 1) * 1e4; CC[h][q] = ((c.iloc[i + h] / c.iloc[i] - 1) - (s.iloc[js + h] / s.iloc[js] - 1)) * 1e4
    brng = np.random.default_rng(20261122); rows = []; missing = []; K = len(pats); bar = 0.05 / K
    def per(x, m):      # one number per day (the average of that day's sell-offs), so each day counts once
        return pd.Series(x[m], index=pd.DatetimeIndex(B.day[m])).groupby(level=0).mean()
    for p in pats:
        if any(w not in by_label for w in p["when"]): missing.append(p["when"]); continue
        m = np.logical_and.reduce([by_label[w] for w in p["when"]]); sign = -1.0 if p["confirm_rate"] < p["confirm_all"] else 1.0; h0 = int(re.search(r"(\d+) session", p["outcome"]).group(1)) if re.search(r"(\d+) session", p["outcome"]) else 2
        h0 = min(EXITS, key=lambda x: abs(x - h0)); row = dict(when=p["when"], outcome=p["outcome"], side="SELL the stock, buy the S&P 500" if sign < 0 else "BUY the stock, sell the S&P 500", own_exit=h0, check_events=(int((m & disc).sum()), int((m & ~disc).sum())), search_events=(p["events_found"], p["events_confirm"]))
        for pn, pm in (("old", disc), ("new", ~disc)):
            mm = m & pm; d0 = per(sign * OC[h0], mm) - COST; row[pn] = dict(days=int(len(d0)), net=float(d0.mean()) if len(d0) else float("nan"), win=float((d0 > 0).mean()) if len(d0) else float("nan"), p=_boot(d0, brng) if len(d0) else float("nan"),
                                                                           gap=float(per(sign * gap, mm).mean()) if len(d0) else float("nan"), cc=float(per(sign * CC[h0], mm).mean()) if len(d0) else float("nan"), raw=float(per(sign * OCraw[h0], mm).mean()) if len(d0) else float("nan"),
                                                                           exits={h: float(per(sign * OC[h], mm).mean() - COST) for h in EXITS} if len(d0) else {})
        a, b = row["old"], row["new"]; row["passes"] = bool(a["net"] > 0 and b["net"] > 0 and b["p"] == b["p"] and b["p"] < bar); rows.append(row)
    f = lambda x: "n/a" if x != x else f"{x:+.0f}"
    L = ["# Sell-off study, test SO-T: can the strong patterns be acted on from the next open?", "", f"Registered in TRACK 3.103 before running. The {K} candidate patterns of the machine search (group: {GROUP}), rebuilt on exactly the same sell-offs. "
         f"Trade: enter at the NEXT OPEN after the sell-off day in the direction the pattern says, against the S&P 500 over the same span; exit at the close of the pattern's own horizon; minus {COST:.0f} basis points for the round trip. Each day counts once. "
         f"**PASSES** = the average after cost is above zero in 2005-2017 AND in 2018-2026, and in 2018-2026 the chance that this average is zero or less (calendar months redrawn {NBOOT} times) is under {bar:.4f} (0.05 / {K} patterns). "
         "These patterns were chosen on these same years, so the numbers are flattered: a pattern that fails here is dead; one that passes only enters the forward record.", "",
         "| when ALL of these hold | trade | exit (sessions after the sell-off) | 2005-2017: after cost, bp (days; share of days with a gain) | 2018-2026: after cost, bp (days; share with a gain; chance of zero or less) | 2018-2026, what the trade is made of: overnight move already gone / close-to-close the search saw / the trade before cost, all in bp | other exits 2018-2026, after cost: " + ", ".join(f"+{h}" for h in EXITS) + " | verdict |", "|---|---|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: -(r["new"]["net"] if r["new"]["net"] == r["new"]["net"] else -1e9)):
        a, b = r["old"], r["new"]; L.append(f"| {' AND '.join(r['when'])} | {r['side']} | +{r['own_exit']} | {f(a['net'])} ({a['days']}; {a['win']:.0%}) | {f(b['net'])} ({b['days']}; {b['win']:.0%}; {b['p']:.4f}) | {f(b['gap'])} / {f(b['cc'])} / {f(b['net'] + COST)} | " + ", ".join(f(b["exits"].get(h, float('nan'))) for h in EXITS) + f" | {'**PASSES**' if r['passes'] else 'fails'} |")
    npass = sum(r["passes"] for r in rows); gross = sum(r["new"]["net"] + COST > 0 for r in rows); net = sum(r["new"]["net"] > 0 for r in rows); bad = [r for r in rows if tuple(r["check_events"]) != tuple(r["search_events"])]
    L += ["", f"**{npass} of {len(rows)} patterns pass.** Before cost the trade gains in 2018-2026 for {gross} of {len(rows)}; after cost for {net}." + (f" {len(missing)} patterns could not be rebuilt (their conditions were not found among the items) and are not counted." if missing else "") +
          (f" WARNING: for {len(bad)} patterns the rebuilt set of sell-offs has a different size from the one the search printed -- the tables changed since the search ran; read those rows with care." if bad else " Every rebuilt pattern has exactly the number of sell-offs the search printed.")]
    DOCS.mkdir(exist_ok=True); (DOCS / "selloff_tradable.md").write_text("\n".join(L) + "\n"); (DOCS / "selloff_tradable.json").write_text(json.dumps(dict(cost_bp=COST, bar=bar, patterns=rows, missing=missing), indent=1, default=float))
    print(f"{K} candidate patterns; cost {COST:.0f} bp; bar p < {bar:.4f}. Rebuilt {len(rows)}" + (f", could not rebuild {len(missing)}" if missing else "") + (f"; SIZE MISMATCH in {len(bad)}" if bad else "; sizes match the search"))
    print("  after cost, 2005-2017 | after cost, 2018-2026 (days; chance of zero or less) | overnight gone / close-to-close / trade before cost | exit | trade | pattern")
    for r in sorted(rows, key=lambda r: -(r["new"]["net"] if r["new"]["net"] == r["new"]["net"] else -1e9)):
        a, b = r["old"], r["new"]; print(f"  {f(a['net']):>5} bp | {f(b['net']):>5} bp ({b['days']:>3}; {b['p']:.4f}) | {f(b['gap']):>4} / {f(b['cc']):>4} / {f(b['net'] + COST):>4} | +{r['own_exit']} | {'SELL' if r['side'].startswith('SELL') else 'BUY '} | {'PASSES' if r['passes'] else 'fails '} | {' AND '.join(r['when'])[:150]}")
    print(f"=> {npass} of {len(rows)} pass; before cost {gross} gain in 2018-2026, after cost {net}. -> docs/selloff_tradable.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run"]); ap.add_argument("--everything", action="store_true", help="also the confirmed patterns that are not candidates (for checking the code)"); a = ap.parse_args(); cmd_run(a.everything)
