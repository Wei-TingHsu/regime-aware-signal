"""intraday_v3e.py -- the intraday tests (docs/prereg_intraday_v3e.md): can a same-day ("grade B") finding be CAUGHT after the release ("grade A")?

  python -m src.intraday_v3e cache      # once: the session minutes (08:00-16:15 New York) of NQ, ES, gold, 10-year note -> data_provenance/intraday/_cache/
  python -m src.intraday_v3e fed        # E1: Fed statement days -- when in the day does the move happen, and is anything left for someone who enters after the release
  python -m src.intraday_v3e releases   # E2: the 08:30 data releases -- does the first move continue or reverse, and does the document's composition score tell which
  python -m src.intraday_v3e all

Prices: P(m) = the last traded price before clock minute m (bars are 1 minute; a price older than 5 minutes counts as missing -- the market was halted or
shut). Release time of a Fed statement: whichever of 12:30, 14:00, 14:15 shows the largest 5-minute move in the 10-year note that day (the price dates
the news). Data releases: 08:30. All returns in basis points (100 bp = 1%). Costs: 2 bp round trip for a futures trade (shown beside the gross figure).
Data-treatment rules: TRACK 3.54 -- halts kept, a day judged only on the minutes used, one contract per day, nothing dropped silently.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path("data_provenance/intraday"); CACHE = ROOT / "_cache"; PROC, DOCS = Path("processed"), Path("docs")
FINAL = {"NQ": ("NQ", "NQ_alt"), "ES": ("ES", "ES_alt"), "GC": ("GCv", "GC_alt"), "ZN": ("ZNv", "ZN_alt")}
NAME = {"NQ": "Nasdaq-100", "ES": "S&P 500", "GC": "gold", "ZN": "10-year note"}
OPEN, CLOSE, TOL, COST_BP, N_NULL = 570, 960, 5, 2.0, 2000
ENTRY = [1, 5, 15, 30]                       # minutes after the release at which the trader enters (and the span used to read the first move)
EXIT = [15, 30, 60, "close"]                 # minutes held after entry, or to the 16:00 close  (short spans first -- the short-window rule, intraday)
FED_TIMES = [750, 840, 855]                  # 12:30, 14:00, 14:15


# ------------------------------------------------------------------------------------------------ data
def _slim(d: pd.DataFrame) -> pd.DataFrame:
    if "ts_event" in d.columns: d = d.set_index("ts_event")
    ny = pd.to_datetime(d.index, utc=True).tz_convert("America/New_York"); m = ny.hour * 60 + ny.minute; keep = (m >= 480) & (m <= 975)
    return pd.DataFrame(dict(date=ny.normalize().tz_localize(None)[keep], minute=np.asarray(m)[keep].astype(np.int16), close=d["close"].to_numpy(float)[keep]))


def cmd_cache():
    Q = pd.read_parquet(PROC / "intraday_quality_final.parquet"); CACHE.mkdir(parents=True, exist_ok=True)
    for sym, (main, alt) in FINAL.items():
        parts = [_slim(pd.read_parquet(p)) for p in sorted((ROOT / main).glob("*.parquet")) if p.stem.isdigit()]; M = pd.concat(parts, ignore_index=True)
        patch_days = set(pd.to_datetime(Q[(Q.symbol == sym) & (Q.source == "patch")]["date"])); ap = ROOT / alt / "all.parquet"
        if patch_days and ap.exists():
            A = _slim(pd.read_parquet(ap)); M = pd.concat([M[~M["date"].isin(patch_days)], A[A["date"].isin(patch_days)]], ignore_index=True)
        M = M.sort_values(["date", "minute"]).drop_duplicates(["date", "minute"]); M.to_parquet(CACHE / f"session_{sym}.parquet"); print(f"  {sym}: {M['date'].nunique():,} days, {len(M):,} session bars ({len(patch_days)} days from the patch file)")
    print(f"-> {CACHE}  (inside the ignored intraday folder; not uploaded)")


class Px:
    """P(sym, date, m): last traded price before clock minute m on that New York date (NaN if older than TOL minutes)."""
    def __init__(self):
        self.d = {}
        for sym in FINAL:
            p = CACHE / f"session_{sym}.parquet"
            if not p.exists(): raise SystemExit("run `python -m src.intraday_v3e cache` first")
            M = pd.read_parquet(p); self.d[sym] = {k: (g["minute"].to_numpy(), g["close"].to_numpy()) for k, g in M.groupby("date", sort=False)}
        self.days = sorted(set.intersection(*[set(v) for v in self.d.values()]))

    def p(self, sym, date, m, tol=TOL):
        v = self.d[sym].get(date)
        if v is None: return np.nan
        mins, cl = v; i = np.searchsorted(mins, m - 1, side="right") - 1
        return float(cl[i]) if (i >= 0 and (m - 1) - mins[i] <= tol) else np.nan

    def r(self, sym, date, a, b, tol=TOL):
        pa, pb = self.p(sym, date, a, tol), self.p(sym, date, b, 15 if b == CLOSE else tol)
        return (np.log(pb / pa) * 1e4) if (np.isfinite(pa) and np.isfinite(pb) and pa > 0) else np.nan


def _stat(v):
    v = np.asarray(v, float); v = v[np.isfinite(v)]; n = len(v)
    if n < 20: return dict(n=n, mean=np.nan, t=np.nan, hit=np.nan)
    s = v.std(ddof=1); return dict(n=n, mean=float(v.mean()), t=float(v.mean() / (s / np.sqrt(n))) if s > 0 else np.nan, hit=float((v > 0).mean()))


def _exit_min(t0, k, x): return CLOSE if x == "close" else min(t0 + k + x, CLOSE)


def _grid(px, days, t0s, sign_fn, asset, rng, placebo_days=None, placebo_t0=None, entries=None):
    """Enter `asset` k minutes after the release in the direction sign_fn(day, t0, k) (known at entry), hold x minutes or to the close.
    Returns the cells, the family p from shuffling the signs across days, and the same rule's result on placebo days (no release) at the same clock time."""
    cells = []; R = {}; S = {}
    for k in (entries or ENTRY):
        S[k] = np.array([sign_fn(d, t0, k) for d, t0 in zip(days, t0s)], float)
        for x in EXIT:
            R[(k, x)] = np.array([px.r(asset, d, t0 + k, _exit_min(t0, k, x)) for d, t0 in zip(days, t0s)], float)
            st = _stat(S[k] * R[(k, x)]); cells.append(dict(entry=k, exit=x, **st))
    ok = [c for c in cells if np.isfinite(c["t"])]
    if not ok: return cells, np.nan, None, {}
    best = max(ok, key=lambda c: abs(c["t"])); nmax = np.zeros(N_NULL)
    for i in range(N_NULL):
        perm = rng.permutation(len(days)); m = 0.0
        for c in ok:
            t = _stat(S[c["entry"]][perm] * R[(c["entry"], c["exit"])])["t"]
            if np.isfinite(t): m = max(m, abs(t))
        nmax[i] = m
    p_fam = float((nmax >= abs(best["t"]) - 1e-12).mean()); plc = {}
    if placebo_days is not None:
        k, x = best["entry"], best["exit"]; v = np.array([sign_fn(d, placebo_t0, k) * px.r(asset, d, placebo_t0 + k, _exit_min(placebo_t0, k, x)) for d in placebo_days], float); v = v[np.isfinite(v)]
        if len(v) > 200:
            n = best["n"]; draws = np.array([rng.choice(v, n, replace=False).mean() for _ in range(N_NULL)]); plc = dict(n=int(len(v)), mean=float(v.mean()), q95=float(np.quantile(draws, 0.95)), q05=float(np.quantile(draws, 0.05)), p=float((np.abs(draws - v.mean()) >= abs(best["mean"] - v.mean())).mean()))
    return cells, p_fam, best, plc


def _cells_md(cells):
    L = ["| enter after | " + " | ".join(f"hold {x} min" if x != "close" else "hold to the close" for x in EXIT) + " |", "|---|" + "---|" * len(EXIT)]
    for k in sorted(set(c["entry"] for c in cells)):
        row = []
        for x in EXIT:
            c = next(c for c in cells if c["entry"] == k and c["exit"] == x); row.append(f"{c['mean']:+.1f} bp (t {c['t']:+.1f}, hit {c['hit']:.0%}, n {c['n']})" if np.isfinite(c["t"]) else f"n {c['n']}")
        L.append(f"| {k} min | " + " | ".join(row) + " |")
    return L


# ------------------------------------------------------------------------------------------------ E1 Fed statement days
SCHEDULE = False      # --schedule: from March 2013 the statement time is fixed at 14:00 (the published schedule); earlier days are still dated by the note


def fed_days(px) -> pd.DataFrame:
    dates = set(pd.to_datetime(pd.read_csv(PROC / "fomc_decisions.csv")["date"]).dt.normalize())
    fs = Path("data_provenance/docs/fomc_statement")
    if fs.exists(): dates |= {pd.to_datetime(p.stem, format="%Y%m%d") for p in fs.glob("*.txt") if re.fullmatch(r"\d{8}", p.stem)}
    rows = []
    for d in sorted(x for x in dates if x in px.d["ZN"]):
        mv = {c: abs(px.r("ZN", d, c, c + 5)) for c in FED_TIMES}; mv = {c: v for c, v in mv.items() if np.isfinite(v)}
        if not mv: rows.append(dict(date=d, t0=np.nan, zn5=np.nan)); continue
        t0 = 840 if (SCHEDULE and d >= pd.Timestamp('2013-03-01') and 840 in mv) else max(mv, key=mv.get); rows.append(dict(date=d, t0=t0, zn5=mv[t0]))
    return pd.DataFrame(rows)


def cmd_fed():
    px = Px(); rng = np.random.default_rng(0); F = fed_days(px); left = F[F.t0.isna()]; F = F.dropna(subset=["t0"]).copy(); F["t0"] = F["t0"].astype(int); days = list(F["date"]); t0s = list(F["t0"]); idx = {d: i for i, d in enumerate(px.days)}
    by = F.groupby([F["date"].dt.year >= 2013, "t0"]).size(); share14 = float((F[F["date"].dt.year >= 2013].t0 == 840).mean())
    print(f"E1: {len(F)} Fed statement days with intraday data ({F['date'].min().date()} -> {F['date'].max().date()}); left out, no 10-year-note price at any candidate time: {[str(x.date()) for x in left['date']]}")
    print("  release time found by the note's 5-minute move -- before 2013: " + ", ".join(f"{t // 60}:{t % 60:02d} × {n}" for (late, t), n in by.items() if not late) + "; from 2013: " + ", ".join(f"{t // 60}:{t % 60:02d} × {n}" for (late, t), n in by.items() if late) + f" (14:00 on {share14:.0%} of days from 2013)")
    L = ["# E1 — Fed statement days, minute by minute", "", f"{len(F)} statement days {F['date'].min().date()} → {F['date'].max().date()}. Release time = whichever of 12:30, 14:00, 14:15 shows the largest 5-minute move in the 10-year note (14:00 on {share14:.0%} of days from 2013). Returns in basis points.", ""]
    # ---- (a) where in the day does the move sit?  sign = the direction of the note's whole-day move (note up = yields down -> gold predicted up)
    L += ["## (a) When does the day's move happen?", "", "Each asset's move, signed by the direction of the 10-year note's move over the whole day (note up = yields down; gold and equities counted as predicted up). This is the same-day link of the daily tests, cut into the parts of the day.", "",
          "| asset | whole day (prior close → close) | before the release (prior close → release) | first 5 minutes | minutes 5–30 | 30 minutes after → close | share of the day's move that comes AFTER the first 5 minutes |", "|---|---|---|---|---|---|---|"]; decomp = {}
    print("\n  (a) where the day's move sits (signed by the note's whole-day direction), mean bp:")
    for a in ("GC", "ES", "NQ", "ZN"):
        parts = {k: [] for k in ("day", "pre", "f5", "m5_30", "rest")}
        for d, t0 in zip(days, t0s):
            i = idx.get(d)
            if i is None or i == 0: continue
            prev = px.days[i - 1]; pc = px.p("ZN", prev, CLOSE, 15); zc = px.p("ZN", d, CLOSE, 15)
            if not (np.isfinite(pc) and np.isfinite(zc)): continue
            sg = np.sign(np.log(zc / pc)); pa = px.p(a, prev, CLOSE, 15); p0 = px.p(a, d, t0); p5 = px.p(a, d, t0 + 5); p30 = px.p(a, d, t0 + 30); pcl = px.p(a, d, CLOSE, 15)
            if not all(np.isfinite(v) for v in (pa, p0, p5, p30, pcl)) or sg == 0: continue
            lg = lambda u, w: np.log(w / u) * 1e4 * sg
            for k, v in (("day", lg(pa, pcl)), ("pre", lg(pa, p0)), ("f5", lg(p0, p5)), ("m5_30", lg(p5, p30)), ("rest", lg(p30, pcl))): parts[k].append(v)
        m = {k: float(np.mean(v)) for k, v in parts.items()}; after = (m["m5_30"] + m["rest"]) / m["day"] if m["day"] else np.nan; decomp[a] = dict(n=len(parts["day"]), **m, share_after_5min=after)
        L.append(f"| {NAME[a]} | {m['day']:+.1f} (n {len(parts['day'])}) | {m['pre']:+.1f} | {m['f5']:+.1f} | {m['m5_30']:+.1f} | {m['rest']:+.1f} | {after:.0%} |")
        print(f"    {NAME[a]:13} day {m['day']:+6.1f} | before release {m['pre']:+6.1f} | first 5 min {m['f5']:+6.1f} | min 5-30 {m['m5_30']:+6.1f} | 30 min -> close {m['rest']:+6.1f} | after first 5 min = {after:.0%} of the day   (n {len(parts['day'])})")
    # ---- (b) catchable: watch the note for k minutes, then enter in that direction
    placebo = [d for d in px.days if d not in set(days)]; out = dict(decomposition=decomp, catch={})
    L += ["", "## (b) Is anything left for someone who enters after the release?", "", f"Rule: watch the 10-year note for k minutes after the release; enter the asset at that minute in the direction the note moved (note up → buy gold / buy equities / buy the note); hold x minutes or to the close. Mean per trade in basis points before a {COST_BP:.0f} bp round-trip cost. Family p: the best cell against the best cell when the notes' directions are shuffled across days ({N_NULL:,} draws). Placebo: the same rule at 14:00 on days with no statement.", ""]
    print(f"\n  (b) enter k minutes after the release in the direction the note moved (gross bp; cost {COST_BP:.0f} bp):")
    def sign_note(d, t0, k):
        v = px.r("ZN", d, t0, t0 + k); return np.sign(v) if np.isfinite(v) else np.nan
    for a in ("GC", "ES", "NQ", "ZN"):
        cells, pf, best, plc = _grid(px, days, t0s, sign_note, a, rng, placebo, 840); out["catch"][a] = dict(cells=cells, p_family=pf, best=best, placebo=plc)
        if best is None: print(f"    {NAME[a]}: too few days"); continue
        net = best["mean"] - COST_BP * np.sign(best["mean"]); ptxt = (f"placebo days: mean {plc['mean']:+.1f} bp, 5%–95% range for {best['n']} days {plc['q05']:+.1f} … {plc['q95']:+.1f}, p vs placebo {plc['p']:.3f}" if plc else "placebo not available")
        verdict = "GRADE A candidate" if (pf < 0.05 and plc and plc["p"] < 0.05 and abs(best["mean"]) > COST_BP) else "not shown"
        print(f"    {NAME[a]:13} best: enter {best['entry']} min, hold {best['exit']}: {best['mean']:+.1f} bp (net {net:+.1f}), t {best['t']:+.2f}, hit {best['hit']:.0%}, n {best['n']}; family p {pf:.3f}; {ptxt} -> {verdict}")
        L += [f"### {NAME[a]}", ""] + _cells_md(cells) + ["", f"Best cell: enter {best['entry']} min after, hold {best['exit']}{' min' if best['exit'] != 'close' else ''}: **{best['mean']:+.1f} bp** before cost ({net:+.1f} after), t {best['t']:+.2f}, hit {best['hit']:.0%}, n {best['n']}; **family p {pf:.3f}**; {ptxt}. **{verdict}.**", ""]
    # ---- (c) statement days after a >= 4% semiconductor fall, signed by the document's own score (v3d at the minute level)
    try:
        from src.news_events3 import _reads, _events
        rd = _reads(); rd = rd[rd["kind"] == "fomc"].set_index("date")["implication"]; ev, ix, _ = _events(); sox = ev[(ev["index"] == "SOX") & (ev["sign"] < 0)]; after = set()
        for p_ in sox["pos"]: after.update(ix[p_ + 1: p_ + 11])
        sub = [(d, t0) for d, t0 in zip(days, t0s) if d in rd.index]; sub_fall = [(d, t0) for d, t0 in sub if d in after]
        L += ["## (c) Statement days signed by the document's own score (what the statement means for stocks, −1 … +1)", "", "Rule: enter the Nasdaq future k minutes after the release in the direction of the document's score; hold x minutes or to the close. The score is known only once the document is read, so k = 1 assumes a reader that scores it within a minute.", ""]
        for lab, ss in (("all statement days with a score", sub), ("statement days within 10 sessions after a ≥ 4% semiconductor fall", sub_fall)):
            if len(ss) < 20: L += [f"**{lab}:** {len(ss)} days — too few to test (minimum 20).", ""]; print(f"\n  (c) {lab}: {len(ss)} days -- too few to test"); out.setdefault("score", {})[lab] = dict(n=len(ss)); continue
            dd, tt = [x[0] for x in ss], [x[1] for x in ss]; cells, pf, best, _ = _grid(px, dd, tt, lambda d, t0, k: np.sign(rd.get(d, np.nan)), "NQ", rng)
            print(f"\n  (c) {lab} ({len(ss)} days), Nasdaq: best enter {best['entry']} min, hold {best['exit']}: {best['mean']:+.1f} bp, t {best['t']:+.2f}, n {best['n']}; family p {pf:.3f}")
            L += [f"### {lab} ({len(ss)} days), Nasdaq-100", ""] + _cells_md(cells) + ["", f"Best cell {best['mean']:+.1f} bp, t {best['t']:+.2f}; family p {pf:.3f}.", ""]; out.setdefault("score", {})[lab] = dict(n=len(ss), cells=cells, p_family=pf, best=best)
    except Exception as e: print(f"\n  (c) document scores unavailable ({type(e).__name__}: {e})")
    L += ["## Days left out", "", f"No 10-year-note price at any candidate release time: {', '.join(str(x.date()) for x in left['date']) or 'none'}. Inside each cell, a day is left out only when the entry or exit minute has no price within {TOL} minutes (a halt or a closed market); the cell's n shows how many days it used."]
    tag = "_sched" if SCHEDULE else ""; out["n_days"] = len(F); out["schedule"] = SCHEDULE
    (DOCS / f"intraday_v3e_fed{tag}.md").write_text("\n".join(L) + "\n"); (DOCS / f"intraday_v3e_fed{tag}.json").write_text(json.dumps(out, indent=1, default=float)); F.to_csv(PROC / f"fed_release_times{tag}.csv", index=False); print(f"\n-> docs/intraday_v3e_fed{tag}.md")


# ------------------------------------------------------------------------------------------------ E2 the 08:30 data releases
def cmd_releases():
    px = Px(); rng = np.random.default_rng(1); T0 = 510
    from src.news_events3 import _reads, BLS_KINDS
    rd = _reads(); rd = rd[rd["kind"].isin(BLS_KINDS)]; day = rd.groupby("date").agg(score=("implication", "mean"), kinds=("kind", lambda s: "+".join(sorted(set(s))))); days = [d for d in day.index if d in px.d["ES"] and d >= pd.Timestamp("2010-06-07")]
    ok = [d for d in days if np.isfinite(px.p("ES", d, T0)) and np.isfinite(px.p("ES", d, T0 + 5))]; left = [d for d in days if d not in ok]; days = ok; t0s = [T0] * len(days); placebo = [d for d in px.days if d not in set(days)]
    print(f"E2: {len(days)} data-release days at 08:30 with a document score and intraday prices; left out (no S&P future price at 08:30 or 08:35 -- overnight halts): {[str(x.date()) for x in left]}")
    L = ["# E2 — the 08:30 data releases, minute by minute", "", f"{len(days)} release days (jobs, consumer prices, producer prices, job openings, import/export prices) that fall within ten sessions after a ≥ 4% move and have a composition score. Returns in basis points; cost {COST_BP:.0f} bp round trip. Placebo: the same rule at 08:30 on days without such a release (some of those days carry other 08:30 releases, so the placebo is a strict one).", ""]; out = {}
    first5 = np.array([px.r("ES", d, T0, T0 + 5) for d in days]); sc = np.array([day.loc[d, "score"] for d in days]); agree = np.sign(first5) == np.sign(sc); nz = (np.sign(sc) != 0) & np.isfinite(first5)
    print(f"  S&P future's first 5 minutes: mean absolute move {np.nanmean(np.abs(first5)):.1f} bp; the first move has the same sign as the document's score on {agree[nz].mean():.0%} of days (n {int(nz.sum())})")
    L += [f"First 5 minutes of the S&P future: mean absolute move {np.nanmean(np.abs(first5)):.1f} bp. The first move has the same sign as the document's composition score on **{agree[nz].mean():.0%}** of days (n {int(nz.sum())}; 50% = the score says nothing about the first move).", ""]; out["first_move_vs_score"] = dict(n=int(nz.sum()), same_sign=float(agree[nz].mean()))
    rules = [("continuation", "enter in the direction of the S&P future's own first k minutes (+ = the first move continues, − = it reverses)", lambda d, t0, k: (np.sign(px.r("ES", d, t0, t0 + k)) if np.isfinite(px.r("ES", d, t0, t0 + k)) else np.nan), days),
             ("score", "enter in the direction of the document's composition score", lambda d, t0, k: np.sign(day.loc[d, "score"]) if d in day.index else np.nan, days),
             ("score_disagrees", "only days where the first 5 minutes went AGAINST the score: enter in the direction of the score (does the price come round to the document?)", lambda d, t0, k: np.sign(day.loc[d, "score"]), [d for d, a_, z in zip(days, agree, nz) if z and not a_])]
    for name, desc, fn, dd in rules:
        L += [f"## Rule: {desc}", ""]; out[name] = {}
        for a in ("ES", "NQ"):
            cells, pf, best, plc = _grid(px, dd, [T0] * len(dd), fn, a, rng, placebo if name == "continuation" else None, T0, entries=(None if name != "score_disagrees" else [5, 15, 30]))
            out[name][a] = dict(n_days=len(dd), cells=cells, p_family=pf, best=best, placebo=plc)
            if best is None: print(f"  {name} / {NAME[a]}: {len(dd)} days -- too few"); L += [f"**{NAME[a]}:** {len(dd)} days — too few to test.", ""]; continue
            ptxt = f"; placebo days {plc['mean']:+.1f} bp, p vs placebo {plc['p']:.3f}" if plc else ""
            print(f"  {name:16} {NAME[a]:11} ({len(dd)} days) best: enter {best['entry']} min, hold {best['exit']}: {best['mean']:+.1f} bp, t {best['t']:+.2f}, hit {best['hit']:.0%}, n {best['n']}; family p {pf:.3f}{ptxt}")
            L += [f"### {NAME[a]} ({len(dd)} days)", ""] + _cells_md(cells) + ["", f"Best cell: enter {best['entry']} min, hold {best['exit']}: {best['mean']:+.1f} bp, t {best['t']:+.2f}, hit {best['hit']:.0%}; **family p {pf:.3f}**{ptxt}.", ""]
    L += ["## Days left out", "", f"No S&P future price at 08:30 or 08:35 (overnight price-limit halts): {', '.join(str(x.date()) for x in left) or 'none'}."]
    (DOCS / "intraday_v3e_releases.md").write_text("\n".join(L) + "\n"); (DOCS / "intraday_v3e_releases.json").write_text(json.dumps(out, indent=1, default=float)); print("-> docs/intraday_v3e_releases.md")


def cmd_score(max_usd: float):
    """Scores EVERY Fed statement in the corpus with the same reader, prompt and cache as the N1 v3 documents (n1-doc-v3), not only those that fell inside
    an event window -- so part (c) of E1 can run on all statement days instead of 45."""
    from src.news_events2 import _client, _ask
    from src.news_events3 import SYS_DOC, PV3, READS3, CHARS, IN_RATE, OUT_RATE
    fs = Path("data_provenance/docs/fomc_statement"); files = sorted(p for p in fs.glob("*.txt") if re.fullmatch(r"\d{8}", p.stem)); todo = [p for p in files if not (READS3 / f"fomc_{p.stem}__{PV3}.json").exists()]
    print(f"statements: {len(files)} in the corpus, {len(todo)} not yet scored under {PV3}; cap US${max_usd:.2f}")
    if not todo: return
    client = _client(); tin = tout = 0
    for k, p in enumerate(todo):
        d, a, b = _ask(client, SYS_DOC, f"DOCUMENT (fomc, {p.stem[:4]}-{p.stem[4:6]}-{p.stem[6:]}):\n{p.read_text()[:CHARS]}", f"fomc_{p.stem}", READS3, PV3); tin += a; tout += b; usd = tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE
        if usd >= max_usd: print(f"  cap reached after {k + 1} reads (~US${usd:.2f})"); break
    print(f"done: ~US${tin / 1e6 * IN_RATE + tout / 1e6 * OUT_RATE:.2f}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["cache", "fed", "releases", "score", "all"]); ap.add_argument("--schedule", action="store_true", help="fed: statement time fixed at 14:00 from March 2013"); ap.add_argument("--max-usd", type=float, default=3.0); a = ap.parse_args(); DOCS.mkdir(exist_ok=True)
    SCHEDULE = a.schedule
    for c in (["cache", "fed", "releases"] if a.cmd == "all" else [a.cmd]): {"cache": cmd_cache, "fed": cmd_fed, "releases": cmd_releases, "score": lambda: cmd_score(a.max_usd)}[c]()
