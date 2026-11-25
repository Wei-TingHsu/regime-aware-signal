"""selloff_rules.py -- the sell-off patterns that PASSED with the founder's real cost (TRACK 3.106), frozen as rules that can be checked on any new day.

Why freezing is needed. The search described its patterns with cuts ('gap at the open under -2.94%') and with groups the machine made itself ('machine
group 3 of 5'). A machine group is defined by numbers the search computed on the 2005-2017 data (which columns, their averages and spreads, the five group
centres). If the data on disk is ever refreshed, a new run would make slightly different groups and the rule would silently change. `freeze` writes those
numbers down once, checks that the written-down rule picks EXACTLY the sell-offs the search picked, and from then on only the frozen file is used.

    python -m src.selloff_rules freeze     # free, no download -> docs/selloff_rules.json, docs/selloff_rules.md
(The daily check of new sell-offs against the frozen rules, the forward record and the card on the page come in the next step and read only this file.)
"""
from __future__ import annotations
import argparse, json
import numpy as np, pandas as pd
from src import selloff_search as S
from src.selloff_study import ROOT, DOCS, _px

GROUP = "stocks, one day -5% or worse"; OUT = DOCS / "selloff_rules.json"; CODES = ["SS-2a", "SS-2b", "SS-2c", "SS-2d", "SS-2e"]


def _items_with_centres(B, disc, rng):
    """the search's own `_items`, line for line, that also hands back what defines each machine group and each cut. Checked against S._items below."""
    items = []; cuts = {}; ids = B.event_id.to_numpy(); nice = lambda c: str(c).replace("_", " ")
    for tn in S.TABLES:
        f = S.TB / f"{tn}.csv"
        if not f.exists(): continue
        T = pd.read_csv(f)
        if T.empty or "event_id" not in T.columns: continue
        T = T.drop_duplicates("event_id").set_index("event_id").reindex(ids); cols = [c for c in T.columns if c not in S.IDS]; num = []
        for c in cols:
            x = T[c]
            if x.notna().sum() < 200: continue
            if not pd.api.types.is_numeric_dtype(x):
                for cat, share in x[disc].value_counts(normalize=True).items():
                    if share >= 0.03: items.append((tn, c, f"{nice(c)} is {cat}", (x == cat).to_numpy())); cuts[items[-1][2]] = dict(kind="is", table=tn, column=c, value=str(cat))
                continue
            v = x.to_numpy(float); u = np.unique(v[np.isfinite(v) & disc])
            if len(u) < 2: continue
            if len(u) == 2 and set(u) <= {0.0, 1.0}:
                items += [(tn, c, f"{nice(c)}: yes", v == 1), (tn, c, f"{nice(c)}: no", v == 0)]; cuts[f"{nice(c)}: yes"] = dict(kind="eq", table=tn, column=c, value=1.0); cuts[f"{nice(c)}: no"] = dict(kind="eq", table=tn, column=c, value=0.0); continue
            num.append(c); q1, q2 = (float(z) for z in np.quantile(v[np.isfinite(v) & disc], [1 / 3, 2 / 3]))
            if q1 == q2:
                items += [(tn, c, f"{nice(c)}: at or under {q1:.3g}", v <= q1), (tn, c, f"{nice(c)}: above {q1:.3g}", v > q1)]; cuts[items[-2][2]] = dict(kind="le", table=tn, column=c, value=q1); cuts[items[-1][2]] = dict(kind="gt", table=tn, column=c, value=q1)
            else:
                items += [(tn, c, f"{nice(c)}: low (under {q1:.3g})", v < q1), (tn, c, f"{nice(c)}: middle ({q1:.3g} to {q2:.3g})", (v >= q1) & (v <= q2)), (tn, c, f"{nice(c)}: high (over {q2:.3g})", v > q2)]
                cuts[items[-3][2]] = dict(kind="lt", table=tn, column=c, value=q1); cuts[items[-2][2]] = dict(kind="between", table=tn, column=c, value=q1, value2=q2); cuts[items[-1][2]] = dict(kind="gt", table=tn, column=c, value=q2)
        if len(num) >= 3:
            X = T[num].to_numpy(float); ok = np.isfinite(X).all(axis=1)
            if (ok & disc).sum() >= 300:
                mu, sd = X[ok & disc].mean(0), X[ok & disc].std(0); sd[sd == 0] = 1; Z = np.clip((X - mu) / sd, -4, 4); C = S._kmeans(Z[ok & disc], 5, rng, restarts=8, iters=40); lab = np.full(len(X), -1); lab[ok] = ((Z[ok][:, None, :] - C[None]) ** 2).sum(-1).argmin(1)
                for j in range(5):
                    top = np.argsort(-np.abs(C[j]))[:2]; label = f"machine group {j + 1} of 5 in '{S.TABLES[tn]}' (marked by {'high' if C[j][top[0]] > 0 else 'low'} {nice(num[top[0]])} and {'high' if C[j][top[1]] > 0 else 'low'} {nice(num[top[1]])})"
                    items.append((tn, f"machine group in {tn}", label, lab == j)); cuts[label] = dict(kind="group", table=tn, group=j, columns=list(num), mean=[float(z) for z in mu], spread=[float(z) for z in sd], centres=[[float(z) for z in row] for row in C])
    return items, cuts


def apply_condition(c: dict, T: pd.DataFrame) -> np.ndarray:
    """one frozen condition on the rows of its table (T: one row per sell-off, the table's columns). Used for the check here and for every new day later."""
    if c["kind"] == "group":
        X = T.reindex(columns=c["columns"]).to_numpy(float); ok = np.isfinite(X).all(axis=1); Z = np.clip((X - np.array(c["mean"])) / np.array(c["spread"]), -4, 4); lab = np.full(len(X), -1)
        if ok.any(): lab[ok] = ((Z[ok][:, None, :] - np.array(c["centres"])[None]) ** 2).sum(-1).argmin(1)
        return lab == c["group"]
    if c["column"] not in T.columns: return np.zeros(len(T), bool)
    if c["kind"] == "is": return (T[c["column"]].astype(str) == c["value"]).to_numpy()
    v = pd.to_numeric(T[c["column"]], errors="coerce").to_numpy(float)
    return {"eq": lambda: v == c["value"], "lt": lambda: v < c["value"], "le": lambda: v <= c["value"], "gt": lambda: v > c["value"], "between": lambda: (v >= c["value"]) & (v <= c["value2"])}[c["kind"]]()


def cmd_freeze(everything=False):
    J = json.loads((DOCS / "selloff_real.json").read_text()); pats = [r for r in J["patterns"] if everything or r["hedged"]["passes"] or r["alone"]["passes"]]
    if not pats: raise SystemExit("no passing pattern in docs/selloff_real.json")
    E = pd.read_csv(ROOT / "events.csv", parse_dates=["day"]); E["event_id"] = E.index; P = _px(); unit, dfn = S.BASES[GROUP]
    B = E[(E.unit == unit) & (E.definition == dfn)].sort_values("day").reset_index(drop=True); Y, _, _ = S._outcomes(B, P); ok = np.isfinite(Y).all(axis=1); B = B[ok].reset_index(drop=True); disc = (B.day < S.SPLIT).to_numpy()
    ref = {it[2]: it[3] for it in S._items(B, disc, np.random.default_rng(S.SEED))}; items, cuts = _items_with_centres(B, disc, np.random.default_rng(S.SEED)); mine = {it[2]: it[3] for it in items}
    same = set(ref) == set(mine) and all(np.array_equal(ref[k], mine[k]) for k in ref); print(f"  the copy of the search's item builder gives the same {len(ref)} items as the search itself: {'YES' if same else 'NO -- STOP, tell Claude'}")
    if not same: raise SystemExit(1)
    tabs = {tn: pd.read_csv(S.TB / f"{tn}.csv").drop_duplicates("event_id").set_index("event_id").reindex(B.event_id.to_numpy()) for tn in S.TABLES if (S.TB / f"{tn}.csv").exists()}
    rules = []; L = ["# The sell-off rules that passed, frozen (SS-2)", "", "Each rule is one pattern of the machine search that PASSED test SO-T2 (the founder's real cost; `docs/selloff_real.md`). 'Frozen' = every cut and every machine group is written down as numbers in `docs/selloff_rules.json`, so the rule cannot drift when data is refreshed. "
                     "The check column says whether the frozen rule picks exactly the sell-offs the search picked.", "", "| code | when ALL of these hold on a day a stock of the list closes 5% or more down | trade | exit | sell-offs picked 2005-2017 / 2018-2026 | frozen rule = the search's pattern | passed |", "|---|---|---|---|---|---|---|"]; allok = True
    for code, r in zip(CODES, pats):
        if any(w not in cuts for w in r["when"]): print(f"  {code}: a condition was not found -- STOP, tell Claude: {r['when']}"); allok = False; continue
        conds = [dict(cuts[w], label=w) for w in r["when"]]; m_ref = np.logical_and.reduce([ref[w] for w in r["when"]]); m_new = np.logical_and.reduce([apply_condition(c, tabs[c["table"]]) for c in conds]); good = bool(np.array_equal(m_ref, m_new)); allok &= good
        rules.append(dict(code=code, when=r["when"], side=r["side"], exit=int(r["exit"]), conditions=conds, passed_against_spx=bool(r["hedged"]["passes"]), passed_alone=bool(r["alone"]["passes"]), history=dict(against_spx_bp=r["hedged"]["new"]["bp"], alone_bp=r["alone"]["new"]["bp"], days=r["hedged"]["new"]["days"], per_year=r["hedged"]["new"]["per_year"], against_spx_bp_old=r["hedged"]["old"]["bp"], alone_bp_old=r["alone"]["old"]["bp"]),
                          picked=dict(old=int((m_new & disc).sum()), new=int((m_new & ~disc).sum()))))
        how = ("against the S&P 500 and alone" if r["hedged"]["passes"] and r["alone"]["passes"] else "against the S&P 500 only" if r["hedged"]["passes"] else "alone only")
        L.append(f"| {code} | {' AND '.join(r['when'])} | {r['side']} the stock at the next open | close {r['exit']} sessions after the sell-off | {int((m_new & disc).sum())} / {int((m_new & ~disc).sum())} | {'YES, exactly' if good else 'NO'} | {how} |"); print(f"  {code}: {int((m_new & disc).sum())} / {int((m_new & ~disc).sum())} sell-offs; frozen rule = the search's pattern: {'YES, exactly' if good else 'NO -- STOP, tell Claude'}; passed {how}; exit +{r['exit']}; {' AND '.join(r['when'])[:150]}")
    if not allok: raise SystemExit("nothing written: a rule did not reproduce")
    L += ["", "What a machine group is, in numbers: the columns of its table are each turned into 'how many usual spreads away from the 2005-2017 average' (cut at 4), and a sell-off belongs to the group whose centre is nearest. The columns, averages, spreads and the five centres are in the json file.", ""]
    for r in rules:
        for c in r["conditions"]:
            if c["kind"] == "group": L.append(f"- {r['code']}, '{c['label'][:60]}...': {len(c['columns'])} columns ({', '.join(c['columns'])}); centre of the group, in spreads from the average: " + ", ".join(f"{n} {v:+.2f}" for n, v in sorted(zip(c["columns"], c["centres"][c["group"]]), key=lambda x: -abs(x[1]))[:5]) + " ...")
    made = f"{pd.Timestamp.now():%Y-%m-%d %H:%M}"; DOCS.mkdir(exist_ok=True); OUT.write_text(json.dumps(dict(made=made, group=GROUP, seed=S.SEED, split=f"{S.SPLIT:%Y-%m-%d}", rules=rules), indent=1)); (DOCS / "selloff_rules.md").write_text("\n".join(L) + "\n")
    print(f"{len(rules)} rules frozen -> docs/selloff_rules.json, docs/selloff_rules.md")


def cmd_risk(limits=(0.30, 0.50)):
    """Founder, 25 Nov: the cost comparison never counted the risk of a margin call when a stock is sold short. On the history of the three frozen rules: how far did the stock RISE
    against a short position inside each trade (from the entry at the next open to the highest price before the exit), what was the largest loss, and how often would the account's
    cushion have fallen under a broker's limit? One trade = the whole US$70,000 sold short on an account of US$70,000 (the worst case; a day with several signals splits the money)."""
    from src import real_cost as RC
    R = json.loads(OUT.read_text())["rules"]; E = pd.read_csv(ROOT / "events.csv", parse_dates=["day"]); E["event_id"] = E.index; P = _px(); unit, dfn = S.BASES[GROUP]
    B = E[(E.unit == unit) & (E.definition == dfn)].sort_values("day").reset_index(drop=True); tabs = {tn: pd.read_csv(S.TB / f"{tn}.csv").drop_duplicates("event_id").set_index("event_id").reindex(B.event_id.to_numpy()) for tn in S.TABLES if (S.TB / f"{tn}.csv").exists()}; A = RC.ACCOUNT
    L = ["# Selling short under the three sell-off rules: how far the stock went against the position", "", f"Every past trade of SS-2a, SS-2b, SS-2c (2005-2026): the stock is sold short at the open after the sell-off and bought back at the rule's exit. 'Worst rise' = the highest price before the exit against the entry price. "
         f"The account: US${A:,.0f}, all of it sold short in one stock (the worst case). The cushion = (account + money received - cost of buying the shares back) / cost of buying them back; a broker closes the position when the cushion falls under its limit. "
         "The founder's broker's limit for short sales is not known; 30% and 50% are shown. **A 2x inverse fund bought with half the money can lose at most US$35,000 and has no margin call; a 1x fund at most US$70,000.**", "",
         "| rule | trades | worst rise inside a trade: middle | 9 in 10 under | 99 in 100 under | the largest | trades with a rise over 10% | over 20% | largest loss of one trade | cushion under 50% (rise over 33%) | cushion under 30% (rise over 54%) |", "|---|---|---|---|---|---|---|---|---|---|---|"]; rows = []
    for r in R:
        m = np.logical_and.reduce([apply_condition(c, tabs[c["table"]]) for c in r["conditions"]]); h = int(r["exit"]); adv = []; fin = []; when = []
        for q in np.flatnonzero(m):
            b = B.iloc[q]; d = P[b.ticker]; i = int(b.i)
            if i + h >= len(d): continue
            ent = float(d.open.iloc[i + 1]); hi = float(d.high.iloc[i + 1:i + h + 1].max()); adv.append(hi / ent - 1); fin.append(float(d.close.iloc[i + h]) / ent - 1); when.append((b.ticker, b.day))
        adv = np.array(adv); fin = np.array(fin); k = int(np.argmax(adv)); worst_loss = float(fin.max()); kl = int(np.argmax(fin)); br = {x: float((1 + 1) / (1 + x) - 1) for x in limits}      # cushion = (2A - A(1+rise)) / (A(1+rise)) < limit  <=>  rise > 2/(1+limit) - 1
        L.append(f"| {r['code']} | {len(adv)} | {np.median(adv):+.1%} | {np.quantile(adv, 0.9):+.1%} | {np.quantile(adv, 0.99):+.1%} | {adv[k]:+.1%} ({when[k][0]}, {when[k][1]:%Y-%m-%d}) | {int((adv > 0.10).sum())} ({(adv > 0.10).mean():.1%}) | {int((adv > 0.20).sum())} | {worst_loss:+.1%} = US${worst_loss * A:,.0f} ({when[kl][0]}, {when[kl][1]:%Y-%m-%d}) | {int((adv > br[0.50]).sum())} | {int((adv > br[0.30]).sum())} |")
        rows.append((r["code"], len(adv), float(np.median(adv)), float(np.quantile(adv, 0.9)), float(np.quantile(adv, 0.99)), float(adv[k]), when[k], int((adv > 0.10).sum()), worst_loss, when[kl], int((adv > br[0.50]).sum()), int((adv > br[0.30]).sum())))
    L += ["", "What this does not show: a rise larger than any in these years; a jump overnight between two sessions that cannot be traded out of (the 'largest' column includes such jumps only as far as the day's high); the broker raising its limit on a volatile stock; two positions open at once."]
    (DOCS / "selloff_short_risk.md").write_text("\n".join(L) + "\n")
    print("  rule | trades | worst rise inside a trade: middle; 9 in 10 under; 99 in 100 under; largest | rises over 10% | largest loss of one trade | cushion under 50% | under 30%")
    for c, n, md, q9, q99, mx, w, n10, wl, wlw, b50, b30 in rows: print(f"  {c} | {n} | {md:+.1%}; {q9:+.1%}; {q99:+.1%}; {mx:+.1%} ({w[0]} {w[1]:%Y-%m-%d}) | {n10} | {wl:+.1%} = US${wl * A:,.0f} ({wlw[0]} {wlw[1]:%Y-%m-%d}) | {b50} | {b30}")
    print("-> docs/selloff_short_risk.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["freeze", "risk"]); ap.add_argument("--everything", action="store_true"); a = ap.parse_args(); cmd_freeze(a.everything) if a.cmd == "freeze" else cmd_risk()
