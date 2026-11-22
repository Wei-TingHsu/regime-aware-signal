"""selloff_search.py -- sell-off study, stage D, step 2: the MACHINE SEARCH for patterns (registered in TRACK 3.98 before it runs).

Founder (21 Nov 2026): let the machine find the patterns instead of us writing hypotheses one by one -- e.g. 'semiconductor stocks rebound after a
sell-off, financials do not', 'after a sell-off set off by a peer's bad news the others are higher five sessions later'.

What it does, in order:
  1. Takes the input tables of src/selloff_inputs.py (conditions known at the close of the sell-off day) and cuts every column into simple items:
     low / middle / high (cut on 2005-2017 only), yes / no, or a category (a sector, a weekday). It also lets k-means sort the sell-offs of each
     table into 5 groups on its own (the unsupervised step) and adds 'belongs to group j' as an item.
  2. Tries EVERY combination of one, two or three items -- inside one table, or across a pair of tables -- against every outcome (price higher after
     1, 2, 3, 5, 7, 10 sessions; the same against the S&P 500 and against the stock's sector fund; the founder's two-session rebound and further slide).
  3. FOUND = in 2005-2017 the outcome's frequency inside the pattern differs strongly from its frequency over all sell-offs (z of 3.5 or more, on at
     least 60 day-equivalents). CONFIRMED = in 2018-2026 (not used for finding) the difference has the same sign and at least half the size, on at
     least 30 day-equivalents.
  4. Repeats the WHOLE search on scrambled data (every sell-off day is given the outcomes of another day of similar size, so each day still counts
     once and its outcomes still move together, but they no longer belong to that day's conditions), many times. If scrambled data gives as many CONFIRMED patterns as the real data, the list is luck.

    python -m src.selloff_search run --trial                      # a few minutes: checks everything works and estimates the time of the full run
    python -m src.selloff_search run --shuffles 100 --max-hours 7 # the night run -> docs/selloff_search.md, .json (written after every family: nothing is lost if it stops)
"""
from __future__ import annotations
import argparse, itertools, json, time
import numpy as np, pandas as pd
from src.selloff_study import ROOT, DOCS, _px, _kmeans

TB = ROOT / "tables"; HORIZONS = [1, 2, 3, 5, 7, 10]; SPLIT = pd.Timestamp("2018-01-01"); ZMIN, SUP_D, SUP_C, KEEP, SEED = 3.5, 60.0, 30.0, 0.5, 20261126
BASES = {"stocks, one day -5% or worse": ("stocks", "1 session, -5% or worse"), "stocks, 5 sessions -10% or worse": ("stocks", "5 sessions, -10% or worse"),
         "funds, one day -3% or worse": ("indices and sectors", "1 session, -3% or worse"), "funds, 5 sessions -7% or worse": ("indices and sectors", "5 sessions, -7% or worse")}
TABLES = {"T1": "the fall and the market", "T2": "who fell and who set it off", "T3": "the company's condition", "T4": "stress and other markets", "T5": "calendar", "T6": "Claude's reading", "T7": "short selling", "T8": "insiders' trades"}
IDS = ("event_id", "unit", "definition", "ticker", "day")


def _outcomes(B, P):
    """for the sell-offs of one base set: the outcome matrix (rows x outcomes, 0/1), its names, and the price move after each horizon"""
    from src.selloff_inputs import SECTOR_FUND
    spy = P["SPY"].close; stocks = B.unit.iloc[0] == "stocks"; sect = pd.read_csv(TB / "T2.csv").set_index("event_id").sector if (stocks and (TB / "T2.csv").exists()) else None; n = len(B); H = len(HORIZONS)
    up = np.full((n, H), np.nan); vs = np.full((n, H), np.nan); vf = np.full((n, H), np.nan); reb = np.full(n, np.nan); sld = np.full(n, np.nan); mv = np.full((n, H), np.nan)
    for q, r in enumerate(B.itertuples()):
        d = P[r.ticker]; c = d.close; i = int(r.i)
        if i + 10 >= len(c) or r.day not in spy.index: continue
        js = spy.index.get_loc(r.day); fund = P.get(SECTOR_FUND.get(sect.get(r.event_id, "other"), "SPY")) if sect is not None else None; fc = fund.close if fund is not None and r.day in fund.index else spy; jf = fc.index.get_loc(r.day)
        if js + 10 >= len(spy) or jf + 10 >= len(fc): continue
        for a, h in enumerate(HORIZONS):
            m = c.iloc[i + h] / c.iloc[i] - 1; mv[q, a] = m * 1e4; up[q, a] = m > 0; vs[q, a] = m > spy.iloc[js + h] / spy.iloc[js] - 1; vf[q, a] = m > fc.iloc[jf + h] / fc.iloc[jf] - 1
        g = [d.close.iloc[i + k] > d.open.iloc[i + k] for k in (1, 2)]; b = [d.close.iloc[i + k] < d.open.iloc[i + k] for k in (1, 2)]; reb[q] = all(g); sld[q] = all(b)
    names = [f"the price is higher after {h} session{'s' if h > 1 else ''}" for h in HORIZONS]; cols = [up]
    if stocks: names += [f"it beats the S&P 500 over {h} session{'s' if h > 1 else ''}" for h in HORIZONS] + [f"it beats its sector fund over {h} session{'s' if h > 1 else ''}" for h in HORIZONS]; cols += [vs, vf]
    names += ["REBOUND (each of the next 2 sessions closes above its open)", "FURTHER SLIDE (each of the next 2 sessions closes below its open)"]; Y = np.column_stack(cols + [reb, sld]); return Y, names, mv


def _items(B, disc, rng):
    """every column of every table -> simple yes/no items over the rows of the base set. Cuts are fixed on the discovery rows only."""
    items = []; ids = B.event_id.to_numpy(); nice = lambda c: str(c).replace("_", " ")
    for tn in TABLES:
        f = TB / f"{tn}.csv"
        if not f.exists(): continue
        T = pd.read_csv(f)
        if T.empty or "event_id" not in T.columns: continue
        T = T.drop_duplicates("event_id").set_index("event_id").reindex(ids); cols = [c for c in T.columns if c not in IDS]; num = []
        for c in cols:
            x = T[c]
            if x.notna().sum() < 200: continue
            if not pd.api.types.is_numeric_dtype(x):
                for cat, share in x[disc].value_counts(normalize=True).items():
                    if share >= 0.03: items.append((tn, c, f"{nice(c)} is {cat}", (x == cat).to_numpy()))
                continue
            v = x.to_numpy(float); u = np.unique(v[np.isfinite(v) & disc])
            if len(u) < 2: continue
            if len(u) == 2 and set(u) <= {0.0, 1.0}: items += [(tn, c, f"{nice(c)}: yes", v == 1), (tn, c, f"{nice(c)}: no", v == 0)]; continue
            num.append(c); q1, q2 = np.quantile(v[np.isfinite(v) & disc], [1 / 3, 2 / 3])
            if q1 == q2: items += [(tn, c, f"{nice(c)}: at or under {q1:.3g}", v <= q1), (tn, c, f"{nice(c)}: above {q1:.3g}", v > q1)]
            else: items += [(tn, c, f"{nice(c)}: low (under {q1:.3g})", v < q1), (tn, c, f"{nice(c)}: middle ({q1:.3g} to {q2:.3g})", (v >= q1) & (v <= q2)), (tn, c, f"{nice(c)}: high (over {q2:.3g})", v > q2)]
        if len(num) >= 3:      # the unsupervised step: k-means sorts the sell-offs of this table into 5 groups by its numeric columns alone
            X = T[num].to_numpy(float); ok = np.isfinite(X).all(axis=1)
            if (ok & disc).sum() >= 300:
                mu, sd = X[ok & disc].mean(0), X[ok & disc].std(0); sd[sd == 0] = 1; Z = np.clip((X - mu) / sd, -4, 4); C = _kmeans(Z[ok & disc], 5, rng, restarts=8, iters=40); lab = np.full(len(X), -1); lab[ok] = ((Z[ok][:, None, :] - C[None]) ** 2).sum(-1).argmin(1)
                for j in range(5):
                    top = np.argsort(-np.abs(C[j]))[:2]; items.append((tn, f"machine group in {tn}", f"machine group {j + 1} of 5 in '{TABLES[tn]}' (marked by {'high' if C[j][top[0]] > 0 else 'low'} {nice(num[top[0]])} and {'high' if C[j][top[1]] > 0 else 'low'} {nice(num[top[1]])})", lab == j))
    return items


def _search(items, fam, Yd, Yc, wd, wc, dmask, cmask, n_out, runs, keep_real):
    """one family (a table or a pair of tables): every pattern of 1-3 items. Returns found / confirmed counts per run, and the real confirmed patterns."""
    tabs = fam; idx = [k for k, it in enumerate(items) if it[0] in tabs]
    if not idx: return None
    Md = np.array([items[k][3][dmask] for k in idx], dtype=np.float32); Mc = np.array([items[k][3][cmask] for k in idx], dtype=np.float32); col = np.array([hash((items[k][0], items[k][1])) for k in idx]); tab = np.array([tabs.index(items[k][0]) for k in idx]); I = len(idx)
    bd = Yd.sum(0) / wd.sum(); bc = Yc.sum(0) / wc.sum(); vd = np.maximum(bd * (1 - bd), 1e-9); found = np.zeros(runs); conf = np.zeros(runs); tried = 0; real = []; pair = len(tabs) == 2
    def block(rows_d, id_d, rows_c, id_c, combos):
        nonlocal tried
        nd = rows_d @ wd[id_d]; ok = nd >= SUP_D
        if not ok.any(): return ok, nd
        rd = rows_d[ok]; sd = rd @ Yd[id_d]; ndk = nd[ok][:, None]; dd = sd / ndk - bd; z = dd / np.sqrt(vd / ndk); F = np.abs(z) >= ZMIN; tried += int(ok.sum()) * n_out
        if F.any():
            rc = rows_c[ok]; nc = (rc @ wc[id_c])[:, None]; dc = (rc @ Yc[id_c]) / np.maximum(nc, 1e-9) - bc; Cf = F & (nc >= SUP_C) & (np.sign(dc) == np.sign(dd)) & (np.abs(dc) >= KEEP * np.abs(dd))
            found[:] += F.reshape(len(rd), runs, n_out).sum(axis=(0, 2)); conf[:] += Cf.reshape(len(rd), runs, n_out).sum(axis=(0, 2))
            if keep_real:
                R = Cf.reshape(len(rd), runs, n_out)[:, 0, :]; pos = np.flatnonzero(ok)
                for a, o in zip(*np.nonzero(R)): real.append((tuple(idx[k] for k in combos[pos[a]]), int(o), float(ndk[a, 0]), float(sd[a, o] / ndk[a, 0]), float(bd[o]), float(z[a, o]), float(nc[a, 0]), float(dc[a, o] + bc[o]), float(bc[o])))
        return ok, nd
    alld = np.arange(Md.shape[1]); allc = np.arange(Mc.shape[1])
    if not pair: block(Md, alld, Mc, allc, [(k,) for k in range(I)])
    for i in range(I - 1):
        id_i = np.flatnonzero(Md[i]); ic_i = np.flatnonzero(Mc[i])
        if wd[id_i].sum() < SUP_D: continue
        js = np.array([j for j in range(i + 1, I) if col[j] != col[i]])
        if not len(js): continue
        rows_d = Md[js][:, id_i]; rows_c = Mc[js][:, ic_i]; use2 = (tab[js] != tab[i]) if pair else np.ones(len(js), bool); nd2 = rows_d @ wd[id_i]
        if use2.any(): block(rows_d[use2], id_i, rows_c[use2], ic_i, [(i, int(j)) for j in js[use2]])
        for a in np.flatnonzero(nd2 >= SUP_D):
            j = int(js[a]); id_ij = id_i[rows_d[a] > 0]; ic_ij = ic_i[rows_c[a] > 0]; ks = np.array([k for k in range(j + 1, I) if col[k] != col[i] and col[k] != col[j] and (not pair or not (tab[k] == tab[i] == tab[j]))])
            if len(ks): block(Md[ks][:, id_ij], id_ij, Mc[ks][:, ic_ij], ic_ij, [(i, j, int(k)) for k in ks])
    return dict(found=found, confirmed=conf, tried=tried, real=real, items=I)


def cmd_run(shuffles: int, max_hours: float, trial: bool):
    t0 = time.time(); E = pd.read_csv(ROOT / "events.csv", parse_dates=["day"]); E["event_id"] = E.index; P = _px(); rng = np.random.default_rng(SEED); out = {}; runs = 1 + shuffles
    have = [t for t in TABLES if (TB / f"{t}.csv").exists() and len(pd.read_csv(TB / f"{t}.csv", nrows=5))]; print(f"tables on disk: {', '.join(have)}; {shuffles} scrambled repeats; " + ("TRIAL" if trial else f"stops starting new work after {max_hours:.1f} hours"))
    head = ["# Sell-off study, stage D: the machine search for patterns", "", f"Registered in TRACK 3.98 before running. Patterns are FOUND on sell-offs of 2005-2017 and CONFIRMED on 2018-2026 (not used for finding). A pattern = one, two or three conditions together, from one table or a pair of tables. "
            f"FOUND: inside the pattern the outcome's frequency differs from its frequency over all sell-offs by z of {ZMIN} or more, on {SUP_D:.0f} or more day-equivalents (each day counts once however many securities fell). CONFIRMED: in 2018-2026 the difference has the same sign and at least half the size, on {SUP_C:.0f} or more day-equivalents. "
            f"**The test:** the whole search is repeated {shuffles} times on scrambled data (every sell-off day is given the outcomes of another day of similar size, a random number of places along the calendar). 'p' = the share of scrambled repeats that gave at least as many CONFIRMED patterns as the real data. A group of sell-offs counts at p < {0.05 / len(BASES):.4f} (0.05 / {len(BASES)} groups). "
            "Only then are its patterns candidates, and only those seen in 24 or more separate months of 2005-2017 and 12 or more of 2018-2026 with a difference of 10 points or more in 2018-2026.", ""]
    bases = list(BASES.items())[:1] if trial else list(BASES.items()); per_family_seconds = []
    for bname, (unit, dfn) in bases:
        B = E[(E.unit == unit) & (E.definition == dfn)].sort_values("day").reset_index(drop=True); Y, names, mv = _outcomes(B, P); ok = np.isfinite(Y).all(axis=1); B, Y, mv = B[ok].reset_index(drop=True), Y[ok], mv[ok]; n_out = len(names)
        disc = (B.day < SPLIT).to_numpy(); conf = ~disc; w = (1.0 / B.groupby("day").day.transform("size")).to_numpy().astype(np.float32); items = _items(B, disc, rng); fams = [(t,) for t in have if any(it[0] == t for it in items)]; fams += [p for p in itertools.combinations([f[0] for f in fams], 2)]
        if trial: fams = fams[:2] + fams[len([f for f in fams if len(f) == 1]):][:1]
        if disc.sum() < 300 or conf.sum() < 150: print(f"  {bname}: too few sell-offs ({int(disc.sum())} / {int(conf.sum())}) -- skipped"); continue
        def stack(Ysub, wsub, days):
            """real outcomes, then the scrambled copies. 22 Nov, third and final form (TRACK 3.100): every sell-off DAY takes the outcomes of ANOTHER day --
            the day a random number of places further along the calendar among days of similar size (1 sell-off; 2-3; 4-9; 10 or more) -- and each of its
            sell-offs draws one of that other day's outcomes. So in every scrambled copy: each day still counts once and every pattern has exactly the same
            support as in the real data; outcomes of one day still move together; busy days still get busy days' outcomes; only the link between a
            day's conditions and what followed is broken."""
            u, start, k = np.unique(days, return_index=True, return_counts=True); dayidx = np.repeat(np.arange(len(u)), k); b = np.digitize(k, [2, 4, 10]); cols = [Ysub]
            for _ in range(shuffles):
                donor = np.arange(len(u))
                for g in range(4):
                    ids = np.flatnonzero(b == g)
                    if len(ids) >= 2: donor[ids] = np.roll(ids, -int(rng.integers(1, len(ids))))
                dd = donor[dayidx]; cols.append(Ysub[start[dd] + np.floor(rng.random(len(days)) * k[dd]).astype(int)])
            return (np.concatenate(cols, axis=1) * wsub[:, None]).astype(np.float32)
        dnum = B.day.to_numpy(); Yd = stack(Y[disc], w[disc], dnum[disc]); Yc = stack(Y[conf], w[conf], dnum[conf]); wd, wc = w[disc], w[conf]; tot_f = np.zeros(runs); tot_c = np.zeros(runs); real = []; fam_rows = []; tried = 0; done = 0
        print(f"  {bname}: {int(disc.sum())} sell-offs to find on ({wd.sum():.0f} days), {int(conf.sum())} to confirm on ({wc.sum():.0f} days); {len(items)} items from {len(set(it[0] for it in items))} tables; {n_out} outcomes; {len(fams)} families")
        for fam in fams:
            if (time.time() - t0) / 3600 > max_hours and not trial: print(f"    time limit reached: {len(fams) - done} families of this group not searched"); break
            t1 = time.time(); R = _search(items, list(fam), Yd, Yc, wd, wc, disc, conf, n_out, runs, True)
            if R is None: continue
            done += 1; tot_f += R["found"]; tot_c += R["confirmed"]; tried += R["tried"]; real += R["real"]; nf, nc_ = R["found"][1:], R["confirmed"][1:]; per_family_seconds.append((time.time() - t1, R["items"], len(fam)))
            fam_rows.append(dict(family=" + ".join(fam), items=R["items"], tried=R["tried"], found=int(R["found"][0]), found_scrambled=float(np.median(nf)) if shuffles else None, confirmed=int(R["confirmed"][0]), confirmed_scrambled_median=float(np.median(nc_)) if shuffles else None, confirmed_scrambled_95=float(np.quantile(nc_, 0.95)) if shuffles else None, p=float((1 + (nc_ >= R["confirmed"][0]).sum()) / (1 + shuffles)) if shuffles else None))
            print(f"    {' + '.join(fam)}: {R['tried']:,} pattern-outcome pairs; found {int(R['found'][0])} (scrambled: {np.median(nf) if shuffles else 0:.0f}); CONFIRMED {int(R['confirmed'][0])} (scrambled: middle {np.median(nc_) if shuffles else 0:.0f}, top 5% {np.quantile(nc_, 0.95) if shuffles else 0:.0f}) [{(time.time() - t1) / 60:.1f} min]")
            # ---- the list so far, in plain words (written after every family)
            p_all = float((1 + (tot_c[1:] >= tot_c[0]).sum()) / (1 + shuffles)) if shuffles else None; passes = p_all is not None and p_all < 0.05 / len(BASES); month = (B.day.dt.year * 12 + B.day.dt.month).to_numpy(); shown = []; masks = []
            conf_d = {(frozenset(x[0]), x[1]): abs(x[7] - x[8]) for x in real}
            for (ids, o, nd, rd, bd, z, nc, rc, bc) in sorted(real, key=lambda x: -abs(x[7] - x[8]) * np.sqrt(x[6])):
                if len(shown) >= 40: break
                if len(ids) > 1 and any(conf_d.get((frozenset(sub), o), 0) >= 0.8 * abs(rc - bc) for r_ in range(1, len(ids)) for sub in itertools.combinations(ids, r_)): continue      # a simpler pattern says the same thing
                m = np.logical_and.reduce([items[k][3] for k in ids]); near = [o2 for o2, m2 in masks if (m & m2).sum() / max(1, (m | m2).sum()) > 0.6]
                if o in near or len(near) >= 2: continue      # the same sell-offs again: at most two outcomes are shown for one set
                masks.append((o, m)); md, mc = int(len(set(month[m & disc]))), int(len(set(month[m & conf]))); hz = range(len(HORIZONS))
                shown.append(dict(when=[items[k][2] for k in ids], tables=sorted({items[k][0] for k in ids}), outcome=names[o], found_rate=rd, found_all=bd, found_days=nd, found_months=md, confirm_rate=rc, confirm_all=bc, confirm_days=nc, confirm_months=mc, events_found=int((m & disc).sum()), events_confirm=int((m & conf).sum()),
                                  move_confirm={HORIZONS[a]: float(np.average(mv[m & conf, a], weights=w[m & conf])) for a in hz} if (m & conf).any() else {}, candidate=bool(passes and md >= 24 and mc >= 12 and abs(rc - bc) >= 0.10)))
            out[bname] = dict(sell_offs_find=int(disc.sum()), sell_offs_confirm=int(conf.sum()), families_searched=done, families_total=len(fams), tried=tried, found=int(tot_f[0]), found_scrambled_median=float(np.median(tot_f[1:])) if shuffles else None, confirmed=int(tot_c[0]), confirmed_scrambled_median=float(np.median(tot_c[1:])) if shuffles else None,
                              confirmed_scrambled_95=float(np.quantile(tot_c[1:], 0.95)) if shuffles else None, confirmed_scrambled_max=float(tot_c[1:].max()) if shuffles else None, p=p_all, passes=bool(passes), families=fam_rows, patterns=shown)
            _write(head, out, shuffles, trial)
        r = out.get(bname)
        if r: print(f"  => {bname}: {r['tried']:,} pattern-outcome pairs in {r['families_searched']} of {r['families_total']} families; CONFIRMED on real data {r['confirmed']}; on scrambled data middle {r['confirmed_scrambled_median']:.0f}, top 5% {r['confirmed_scrambled_95']:.0f}, most {r['confirmed_scrambled_max']:.0f}; p {r['p']:.3f} -> {'MORE THAN LUCK' if r['passes'] else 'no more than luck gives'}")
    if trial and per_family_seconds:
        sec = np.mean([s for s, _, _ in per_family_seconds]); nt = len(have); nf_all = (nt + nt * (nt - 1) // 2); est = sec * nf_all * len(BASES) * (1 + 100) / (1 + shuffles) * 0.6 / 3600
        print(f"TRIAL finished in {(time.time() - t0) / 60:.1f} minutes with {shuffles} scrambled repeats. Rough estimate for the night run (100 repeats, {nf_all} families x {len(BASES)} groups): {est:.1f} hours on this machine -- the run stops starting new work at the limit you give and keeps what is done.")
    print(f"-> docs/selloff_search{'_trial' if trial else ''}.md   ({(time.time() - t0) / 3600:.2f} hours)")


def _write(head, out, shuffles, trial):
    L = list(head)
    for bname, r in out.items():
        L += [f"## {bname}", "", f"{r['sell_offs_find']} sell-offs to find on, {r['sell_offs_confirm']} to confirm on. Searched {r['families_searched']} of {r['families_total']} families: {r['tried']:,} pattern-outcome pairs. FOUND in 2005-2017: {r['found']} (scrambled data, middle: {r['found_scrambled_median']}). "
              f"**CONFIRMED in 2018-2026: {r['confirmed']}; scrambled data gave {r['confirmed_scrambled_median']:.0f} in the middle, {r['confirmed_scrambled_95']:.0f} in its top 5%, at most {r['confirmed_scrambled_max']:.0f}. p = {r['p']:.3f} -> {'MORE THAN LUCK' if r['passes'] else 'no more than luck gives'}.**", "",
              "| family (tables) | items | pairs tried | found | found, scrambled | confirmed | confirmed, scrambled (middle; top 5%) | p |", "|---|---|---|---|---|---|---|---|"]
        L += [f"| {f['family']} | {f['items']} | {f['tried']:,} | {f['found']} | {f['found_scrambled']:.0f} | {f['confirmed']} | {f['confirmed_scrambled_median']:.0f}; {f['confirmed_scrambled_95']:.0f} | {f['p']:.3f} |" for f in r["families"]]
        L += ["", "### The confirmed patterns with the largest difference in 2018-2026 (overlapping ones removed)" + ("" if r["passes"] else " -- shown for the record; this group did NOT beat scrambled data, so read them as luck"), "",
              "| when ALL of these hold | then | 2005-2017: how often (all sell-offs) | days; months; sell-offs | 2018-2026: how often (all sell-offs) | days; months; sell-offs | average price move after, 2018-2026 | candidate |", "|---|---|---|---|---|---|---|---|"]
        for x in r["patterns"]:
            L.append(f"| {' AND '.join(x['when'])} | {x['outcome']} | {x['found_rate']:.0%} ({x['found_all']:.0%}) | {x['found_days']:.0f}; {x['found_months']}; {x['events_found']} | {x['confirm_rate']:.0%} ({x['confirm_all']:.0%}) | {x['confirm_days']:.0f}; {x['confirm_months']}; {x['events_confirm']} | " + ", ".join(f"+{h}: {v:+.0f} bp" for h, v in x["move_confirm"].items()) + f" | {'yes' if x['candidate'] else 'no'} |")
        L.append("")
    DOCS.mkdir(exist_ok=True); stem = "selloff_search_trial" if trial else "selloff_search"; (DOCS / f"{stem}.md").write_text("\n".join(L) + "\n"); (DOCS / f"{stem}.json").write_text(json.dumps(out, indent=1, default=lambda z: None if isinstance(z, float) and z != z else (float(z) if isinstance(z, (np.floating, np.integer)) else str(z))))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run"]); ap.add_argument("--shuffles", type=int, default=100); ap.add_argument("--max-hours", type=float, default=7.0); ap.add_argument("--trial", action="store_true"); a = ap.parse_args()
    cmd_run(3 if a.trial else a.shuffles, a.max_hours, a.trial)
