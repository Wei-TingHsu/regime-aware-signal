"""selloff_model.py -- the sell-off study, stage C (registered in TRACK 3.94 before running): a PROBABILITY for each sell-off, checked against what happened.

Founder's definitions (21 Nov 2026), nothing compared with the sell-off day itself:
  REBOUND       = each of the next 2 sessions closes ABOVE its own open (two up-days in a row)
  FURTHER SLIDE = each of the next 2 sessions closes BELOW its own open (two down-days in a row)
  MIXED         = anything else
Horizons for the size of the move (price at the close of session +h against the sell-off day's close): 1, 2, 3, 5, 7, 10.

How the probability is made and checked: for each year, a plain logistic model is trained ONLY on sell-offs of earlier years (the same conditions as
stage B, known at the close of the sell-off day) and gives each sell-off of that year a probability of REBOUND and of FURTHER SLIDE. Those out-of-sample
probabilities are then compared with what happened: (a) are they better than always quoting the historical frequency? (b) when the model says 40%, did
about 40% happen? Uncertainty counts separate calendar MONTHS, not events -- the fault of stage B.

    python -m src.selloff_model run      # needs: python -m src.selloff_study prices / filings / build   -> docs/selloff_model.md, .json
"""
from __future__ import annotations
import argparse, json
import numpy as np, pandas as pd
from src.selloff_study import ROOT, DOCS, FEATS, CAUSE, _px

HORIZONS = [1, 2, 3, 5, 7, 10]; N_BOOT, SEED, RIDGE, MIN_TRAIN, MIN_EPI = 2000, 20261125, 10.0, 300, 40; BINS = [0, .15, .25, .35, .45, 1.01]; LIFT = 0.10


def _fit(Z, y, w):
    """logistic regression with a ridge penalty (the intercept is not penalised); returns coefficients, intercept first"""
    X = np.column_stack([np.ones(len(Z)), Z]); b = np.zeros(X.shape[1]); pen = np.eye(X.shape[1]) * RIDGE; pen[0, 0] = 0; w = w / w.mean()
    for _ in range(40):
        p = 1 / (1 + np.exp(-np.clip(X @ b, -30, 30))); g = X.T @ (w * (p - y)) + pen @ b; H = (X * (w * p * (1 - p))[:, None]).T @ X + pen
        step = np.linalg.solve(H + 1e-8 * np.eye(len(b)), g); b = b - step
        if np.abs(step).max() < 1e-7: break
    return b


def _episodes(days: pd.Series) -> np.ndarray:
    """the unit of separate evidence: the calendar MONTH. (Chaining nearby days into 'episodes' does not work for stocks: with a hundred stocks some
    sell-off happens almost every week, and the chain becomes one endless episode.)"""
    return (days.dt.year * 12 + days.dt.month).to_numpy()


def cmd_run():
    E = pd.read_csv(ROOT / "events.csv", parse_dates=["day"]); P = _px(); rng = np.random.default_rng(SEED); n = len(E)
    cls = np.full(n, "", dtype=object); MV = np.full((n, len(HORIZONS)), np.nan)
    for r in E.itertuples():
        d = P[r.ticker]; i = int(r.i)
        if i + 2 < len(d):
            up = [d.close.iloc[i + k] > d.open.iloc[i + k] for k in (1, 2)]; dn = [d.close.iloc[i + k] < d.open.iloc[i + k] for k in (1, 2)]; cls[r.Index] = "REBOUND" if all(up) else ("SLIDE" if all(dn) else "MIXED")
        for a, h in enumerate(HORIZONS):
            if i + h < len(d): MV[r.Index, a] = (d.close.iloc[i + h] / d.close.iloc[i] - 1) * 1e4
    E["cls"] = cls; out = {}; fam = [(u, dfn, g) for (u, dfn), g in E.groupby(["unit", "definition"], sort=False)]; n_tests = len(fam) * 2; bar = 0.05 / n_tests
    L = ["# Sell-off study, stage C: how likely is a rebound or a further slide after THIS sell-off?", "",
         "Registered in TRACK 3.94 before running. **Founder's definitions:** REBOUND = each of the next 2 sessions closes above its own open; FURTHER SLIDE = each of the next 2 sessions closes below its own open; anything else is MIXED. "
         "For every year the model is trained only on sell-offs of earlier years and gives each sell-off of that year two probabilities. 'Always quote history' = the frequency seen in those earlier years, the same number for every sell-off. "
         f"**Skill** = how much smaller the model's error is than that of always quoting history (0% = no better; error = the squared gap between the probability given and what happened). Its range and p come from resampling whole months {N_BOOT} times "
         f"(all sell-offs of one calendar month are one piece of evidence, because neighbouring days move together); p = how often the model was no better than history. {n_tests} tests, so skill counts at p < {bar:.4f}. "
         f"**The probability is usable only if** skill passes AND, among the sell-offs where the model said at least {LIFT:.0%} points above history, the event really happened at least 5 points more often than history, in 20 or more separate months. "
         "Price moves are the price itself (not against the market), in bp: 100 bp = 1%.", ""]
    for u, dfn, g in fam:
        feats = FEATS + (CAUSE if u == "stocks" else []); g = g[g[feats].notna().all(axis=1) & (g.cls != "")].sort_values("day"); key = f"{u}; {dfn}"; L += [f"## {key}", ""]
        X = g[feats].to_numpy(float); w = (1.0 / g.groupby("day").day.transform("size")).to_numpy(); epi = _episodes(g.day); yr = g.day.dt.year.to_numpy(); mv = MV[g.index]; res = dict(events=int(len(g)), episodes=int(len(set(epi))))
        pr = {k: np.full(len(g), np.nan) for k in ("REBOUND", "SLIDE")}; bs = {k: np.full(len(g), np.nan) for k in pr}; coef = {}
        for Y in sorted(set(yr)):
            tr = (g.day < pd.Timestamp(f"{Y}-01-01") - pd.Timedelta(days=5)).to_numpy(); te = yr == Y
            if tr.sum() < MIN_TRAIN or len(set(epi[tr])) < MIN_EPI: continue
            lo, hi = np.quantile(X[tr], 0.01, axis=0), np.quantile(X[tr], 0.99, axis=0); Xc = np.clip(X, lo, hi); mu, sd = Xc[tr].mean(0), Xc[tr].std(0); sd[sd == 0] = 1; Z = (Xc - mu) / sd
            for k in pr:
                y = (g.cls == k).to_numpy().astype(float); b = _fit(Z[tr], y[tr], w[tr]); pr[k][te] = 1 / (1 + np.exp(-np.clip(np.column_stack([np.ones(te.sum()), Z[te]]) @ b, -30, 30))); bs[k][te] = np.average(y[tr], weights=w[tr]); coef[k] = b
        oos = np.isfinite(pr["REBOUND"])
        if oos.sum() < 200 or len(set(epi[oos])) < MIN_EPI: L += [f"Not tested: too few sell-offs to train on earlier years and test on later ones ({int(len(g))} events, {res['episodes']} months).", ""]; print(f"  {key}: not tested (too few events)"); out[key] = dict(res, not_tested=True); continue
        res.update(first_year_predicted=int(yr[oos].min()), predicted_events=int(oos.sum()), predicted_days=int(g.day[oos].nunique()), predicted_episodes=int(len(set(epi[oos]))))
        share = {k: float(np.average((g.cls[oos] == k).to_numpy(), weights=w[oos])) for k in ("REBOUND", "SLIDE", "MIXED")}; res["what_happened"] = share
        res["move_by_outcome"] = {k: {h: float(np.nanmean(mv[oos & (g.cls == k).to_numpy(), a])) for a, h in enumerate(HORIZONS)} for k in ("REBOUND", "SLIDE", "MIXED")}
        L += [f"{res['events']} sell-offs in {res['episodes']} separate months; predicted out of sample from {res['first_year_predicted']}: {res['predicted_events']} sell-offs on {res['predicted_days']} days, {res['predicted_episodes']} months. "
              f"What happened: REBOUND {share['REBOUND']:.0%}, FURTHER SLIDE {share['SLIDE']:.0%}, MIXED {share['MIXED']:.0%}.", "",
              "What each outcome meant for the price (average change from the sell-off day's close):", "", "| outcome | " + " | ".join(f"+{h}" for h in HORIZONS) + " |", "|---|" + "---|" * len(HORIZONS)]
        L += [f"| {k} | " + " | ".join(f"{res['move_by_outcome'][k][h]:+.0f} bp" for h in HORIZONS) + " |" for k in ("REBOUND", "SLIDE", "MIXED")] + [""]
        for k in ("REBOUND", "SLIDE"):
            y = (g.cls == k).to_numpy().astype(float)[oos]; p = pr[k][oos]; b0 = bs[k][oos]; ww = w[oos]; ee = epi[oos]; ids = np.unique(ee); em = pd.DataFrame(dict(e=ee, m=ww * (p - y) ** 2, b=ww * (b0 - y) ** 2)).groupby("e").sum()
            skill = 1 - em.m.sum() / em.b.sum(); M, B = em.m.to_numpy(), em.b.to_numpy(); pick = rng.integers(0, len(ids), size=(N_BOOT, len(ids))); sk = 1 - M[pick].sum(1) / B[pick].sum(1); pv = float((sk <= 0).mean())
            rows = []
            for a, b_ in zip(BINS[:-1], BINS[1:]):
                s = (p >= a) & (p < b_)
                if s.sum(): rows.append(dict(bin=f"{a:.0%} to {min(b_, 1):.0%}", events=int(s.sum()), episodes=int(len(set(ee[s]))), said=float(np.average(p[s], weights=ww[s])), happened=float(np.average(y[s], weights=ww[s]))))
            top = p >= b0 + LIFT; T = dict(events=int(top.sum()), episodes=int(len(set(ee[top]))) if top.any() else 0)
            if top.any(): T.update(said=float(np.average(p[top], weights=ww[top])), happened=float(np.average(y[top], weights=ww[top])), history=float(np.average(b0[top], weights=ww[top])), move={h: float(np.nanmean(mv[oos][top, a])) for a, h in enumerate(HORIZONS)})
            usable = bool(pv < bar and skill > 0 and top.any() and T["episodes"] >= 20 and T["happened"] >= T["history"] + 0.05)
            cz = coef[k][1:]; order = np.argsort(-np.abs(cz))[:4]; drivers = "; ".join(f"{'more likely' if cz[q] > 0 else 'less likely'} with high {feats[q]}" for q in order)
            res[k] = dict(skill=float(skill), low=float(np.quantile(sk, 0.05)), high=float(np.quantile(sk, 0.95)), p=pv, calibration=rows, top=T, usable=usable, drivers=drivers)
            verdict = "USABLE" if usable else ("better than history, but not by enough to show a customer" if (pv < bar and skill > 0) else "no better than always quoting history")
            L += [f"### Probability of {'a REBOUND' if k == 'REBOUND' else 'a FURTHER SLIDE'}", "", f"**Skill {skill:+.1%}** (range {res[k]['low']:+.1%} to {res[k]['high']:+.1%}; p {pv:.4f}; bar {bar:.4f}) -> **{verdict}**. In the latest model: {drivers}.", "",
                  "| the model said | sell-offs | separate months | average said | actually happened |", "|---|---|---|---|---|"] + [f"| {x['bin']} | {x['events']} | {x['episodes']} | {x['said']:.0%} | {x['happened']:.0%} |" for x in rows]
            if top.any(): L += ["", f"Where the model said at least {LIFT:.0%} points above history: {T['events']} sell-offs in {T['episodes']} separate months; it said {T['said']:.0%}, history said {T['history']:.0%}, it happened {T['happened']:.0%}. Price after: " + ", ".join(f"+{h}: {v:+.0f} bp" for h, v in T["move"].items()) + "."]
            else: L += ["", f"The model never said {LIFT:.0%} points above history."]
            L.append(""); print(f"  {key} | {k}: happened {share[k]:.0%}; skill {skill:+.1%} ({res[k]['low']:+.1%} to {res[k]['high']:+.1%}), p {pv:.4f} -> {verdict}" + (f"; when it said {T['said']:.0%} (history {T['history']:.0%}) it happened {T['happened']:.0%} in {T['episodes']} months" if top.any() else "; never 10 points above history") + f" | {drivers}")
        out[key] = res
    DOCS.mkdir(exist_ok=True); (DOCS / "selloff_model.md").write_text("\n".join(L) + "\n"); (DOCS / "selloff_model.json").write_text(json.dumps(dict(bar=bar, results=out), indent=1, default=lambda z: None if isinstance(z, float) and z != z else (float(z) if isinstance(z, (np.floating, np.integer)) else str(z))))
    E[["unit", "definition", "ticker", "day", "cls"]].to_csv(ROOT / "outcomes.csv", index=False); print(f"{n_tests} tests; bar p < {bar:.4f}. -> docs/selloff_model.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["run"]); ap.parse_args(); cmd_run()
