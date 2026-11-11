"""horizon_audit.py -- the horizon audit (docs/prereg_horizon_audit.md, TRACK 3.51): every past test whose index row says "day 0 checked? no" is
re-measured under the founder's two rules of 11 Nov -- short windows first, and quant vs subjective (intraday).

For each test the events are rebuilt exactly as the original test built them, and the asset's return is measured, signed in the direction the test's
claim predicts, on:   day -1 (the day BEFORE the event -- a check, nothing should show) | day 0 (the event day itself) | day +1 | days +1..+2 |
days +1..+3 | days +1..+5.
Null: the asset's return series shifted in time by a random offset (1,000 draws); the event dates stay where they are. Three family p-values per
test, each "best cell of the whole test vs best cell on shifted data":  p_day0 (all day-0 cells), p_after (all cells on days +1 onward), p_before.
Label rule (registered): p_after < 0.05 -> QUANT candidate;  else p_day0 < 0.05 -> SUBJECTIVE grade B candidate when the event is INFORMATION
(a document, a call, a data release), or CONTEXT (same-day co-movement) when the event is itself a PRICE MOVE;  else NEITHER.

  python -m src.horizon_audit list
  python -m src.horizon_audit selloff | sudden | oil | fomc | calls [--csv ...] | htables | states | liquidity | resid
  python -m src.horizon_audit all            # every test, then the summary table docs/horizon_audit.md
  python -m src.horizon_audit summary
Nothing here writes the register and nothing calls the LLM or the network (liquidity reads the FRED files already cached on disk).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PROC, DOCS = Path("processed"), Path("docs")
SPANS = [("day -1", -1, -1, "before"), ("day 0", 0, 0, "day0"), ("day +1", 1, 1, "after"), ("days +1..+2", 1, 2, "after"), ("days +1..+3", 1, 3, "after"), ("days +1..+5", 1, 5, "after")]
N_NULL, MIN_N, ALPHA = 1000, 30, 0.05
ERAS = [("2004-08", "2004-01-01", "2008-12-31"), ("2009-14", "2009-01-01", "2014-12-31"), ("2015-19", "2015-01-01", "2019-12-31"), ("2020-21", "2020-01-01", "2021-12-31"), ("2022-26", "2022-01-01", "2026-12-31")]


def panel() -> pd.DataFrame:
    r = pd.read_parquet(PROC / "asset_returns.parquet"); r.index = pd.to_datetime(r.index)
    if getattr(r.index, "tz", None) is not None: r.index = r.index.tz_localize(None)
    return r.sort_index()


# ------------------------------------------------------------------------------------------------ the engine
# a variant = dict(label, parts=[(key, pos, sign)], skip0); `series` maps key -> (index, return array). skip0 = the event is defined by this asset's
# own move that day, so day 0 and day -1 are not measured for it.
def _cums(series, shift=0):
    return {k: np.concatenate([[0.0], np.cumsum(np.nan_to_num(np.roll(x, shift % len(x)) if shift else x))]) for k, (_, x) in series.items()}


def _signed(cums, parts, a, b):
    out = []
    for key, pos, sign in parts:
        cum = cums[key]; n = len(cum) - 1; ok = (pos + a >= 0) & (pos + b < n)
        out.append(sign[ok] * (cum[pos[ok] + b + 1] - cum[pos[ok] + a]))
    return np.concatenate(out) if out else np.array([])


def _t(v):
    n = len(v)
    if n < MIN_N: return np.nan, np.nan, n
    s = v.std(ddof=1); return float(v.mean()), (float(v.mean() / (s / np.sqrt(n))) if s > 0 else np.nan), n


def audit(name: str, title: str, kind: str, series: dict, variants: list, note: str = "") -> dict:
    """kind: 'information' (document / call / release) or 'price move'."""
    rng = np.random.default_rng(0); rows = []; C0 = _cums(series)
    for v in variants:
        for sp, a, b, grp in SPANS:
            if v.get("skip0") and a <= 0: continue
            sv = _signed(C0, v["parts"], a, b); m, t, n = _t(sv); hit = float((sv > 0).mean()) if n >= MIN_N else np.nan
            rows.append(dict(variant=v["label"], span=sp, group=grp, n=n, mean_bp=m * 1e4 if np.isfinite(m) else np.nan, t=t, hit=hit, _v=v, _a=a, _b=b))
    rows = [r for r in rows if np.isfinite(r["t"])]
    if not rows: print(f"{name}: no cell reaches {MIN_N} events"); return {}
    T = np.array([r["t"] for r in rows]); G = np.array([r["group"] for r in rows]); nmin = min(len(s[1]) for s in series.values())
    NT = np.full((N_NULL, len(rows)), np.nan)
    for k in range(N_NULL):
        sh = int(rng.integers(250, nmin - 250)) if nmin > 600 else int(rng.integers(1, nmin))
        Ck = _cums(series, sh)
        for j, r in enumerate(rows): NT[k, j] = _t(_signed(Ck, r["_v"]["parts"], r["_a"], r["_b"]))[1]
    fam = {}
    for g in ("before", "day0", "after"):
        m = G == g
        if not m.any(): fam[g] = dict(p=np.nan, best=None); continue
        nm = np.nanmax(np.abs(NT[:, m]), axis=1); obs = float(np.nanmax(np.abs(T[m]))); jb = int(np.where(m)[0][np.nanargmax(np.abs(T[m]))])
        fam[g] = dict(p=float((nm >= obs - 1e-12).mean()), q95=float(np.nanquantile(nm, 0.95)), best=dict(variant=rows[jb]["variant"], span=rows[jb]["span"], n=rows[jb]["n"], mean_bp=rows[jb]["mean_bp"], t=rows[jb]["t"], hit=rows[jb]["hit"]), _j=jb)
    for j, r in enumerate(rows): r["p"] = float((np.abs(NT[:, j]) >= abs(r["t"]) - 1e-12).mean())
    pa, p0 = fam["after"]["p"], fam["day0"]["p"]
    label = ("QUANT candidate" if (np.isfinite(pa) and pa < ALPHA) else ("SUBJECTIVE grade B candidate" if kind == "information" else "CONTEXT (same-day co-movement)") if (np.isfinite(p0) and p0 < ALPHA) else "NEITHER")
    # eras for the best day-0 and best after cell
    era_txt = {}
    for g in ("day0", "after"):
        if fam[g].get("best") is None: continue
        r = rows[fam[g]["_j"]]; bits = []
        for en, a_, z_ in ERAS:
            parts = []
            for key, pos, sign in r["_v"]["parts"]:
                d = series[key][0][pos]; mk = (d >= np.datetime64(a_)) & (d <= np.datetime64(z_)); parts.append((key, pos[mk], sign[mk]))
            v = _signed(C0, parts, r["_a"], r["_b"])
            if len(v) >= 10: bits.append(f"{en}: {v.mean() * 1e4:+.0f} bp (n {len(v)})")
        era_txt[g] = "; ".join(bits) or "too few per era"
    def bl(g):
        b = fam[g].get("best"); return "not measured" if b is None else f"`{b['variant']}` {b['span']}: mean {b['mean_bp']:+.0f} bp, t {b['t']:+.2f}, n {b['n']}, hit {b['hit']:.0%}; family p **{fam[g]['p']:.3f}** (null 95th percentile of |t| {fam[g]['q95']:.2f})"
    print(f"\n=== {name}: {title} [{kind}] ===\n  day 0 : {bl('day0')}\n  after : {bl('after')}\n  before: {bl('before')}\n  label -> {label}\n  best day-0 cell by era: {era_txt.get('day0', '-')}\n  best after cell by era: {era_txt.get('after', '-')}")
    L = [f"# Horizon audit — {title}", "", f"Event kind: **{kind}**. {note}", "", "Returns are signed in the direction the original claim predicts and shown in basis points (100 bp = 1%). p = share of 1,000 time-shifts of the asset's returns with |t| at least as large. Family p = the same for the best cell of the group.", "",
         f"- **Day 0** (the event day): {bl('day0')}. By era: {era_txt.get('day0', '-')}.", f"- **After** (days +1 … +5): {bl('after')}. By era: {era_txt.get('after', '-')}.", f"- **Before** (day −1, a check): {bl('before')}.", f"- **Label under the two-category rule: {label}**", "",
         "| variant | n | " + " | ".join(s[0] for s in SPANS) + " |", "|---|---|" + "---|" * len(SPANS)]
    for lab in dict.fromkeys(r["variant"] for r in rows):
        rr = {r["span"]: r for r in rows if r["variant"] == lab}; n_ = max(r["n"] for r in rr.values())
        L.append(f"| {lab} | {n_} | " + " | ".join((f"{rr[s[0]]['mean_bp']:+.0f} bp (t {rr[s[0]]['t']:+.1f}, p {rr[s[0]]['p']:.3f})" + ("**" if rr[s[0]]["p"] < 0.05 else "")) if s[0] in rr else "·" for s in SPANS) + " |")
    (DOCS / f"horizon_audit_{name}.md").write_text("\n".join(L) + "\n")
    res = dict(name=name, title=title, kind=kind, label=label, n_variants=len(variants), family={g: {k: v for k, v in fam[g].items() if not k.startswith("_")} for g in fam}, eras=era_txt,
               cells=[{k: v for k, v in r.items() if not k.startswith("_")} for r in rows])
    (DOCS / f"horizon_audit_{name}.json").write_text(json.dumps(res, indent=1, default=float)); return res


def _ser(s: pd.Series):
    s = s.dropna(); return (s.index.to_numpy(), s.to_numpy(float))


def _pos(index: np.ndarray, dates) -> np.ndarray:
    ix = pd.DatetimeIndex(index).get_indexer(pd.DatetimeIndex(dates)); return ix[ix >= 0]


def _ones(n): return np.ones(n)


# ------------------------------------------------------------------------------------------------ the tests
def t_selloff():
    from src.deeper import _crossings
    r = panel(); d = pd.DataFrame(dict(spy=r["SPY"], gld=r["GLD"])).dropna(); series = dict(GLD=(d.index.to_numpy(), d["gld"].to_numpy()), SPY=(d.index.to_numpy(), d["spy"].to_numpy())); V = []
    for look in (10, 20):
        dd = d["spy"].rolling(look).sum().to_numpy()
        for thr in (-0.04, -0.06, -0.08):
            pos = _crossings(dd, thr, 2 * look, look)
            V.append(dict(label=f"S&P {look}-session return crosses {thr:.0%} → gold", parts=[("GLD", pos, _ones(len(pos)))]))
            V.append(dict(label=f"S&P {look}-session return crosses {thr:.0%} → S&P itself", parts=[("SPY", pos, _ones(len(pos)))], skip0=True))
    return audit("selloff", "gold (and the S&P) around the day an S&P drawdown is completed (D1, T-L5b)", "price move", series, V, "Events as in D1: the first session the S&P's rolling return crosses the threshold, one event per 2 × look sessions. Positive = the asset rose.")


def t_sudden():
    r = panel(); d = pd.DataFrame(dict(spy=r["SPY"], gld=r["GLD"])).dropna(); series = dict(GLD=(d.index.to_numpy(), d["gld"].to_numpy()), SPY=(d.index.to_numpy(), d["spy"].to_numpy())); spy = d["spy"].to_numpy(); V = []
    for thr in (0.015, 0.02, 0.03, 0.04):
        pos = np.where(spy <= -thr)[0]
        V.append(dict(label=f"S&P falls ≥ {thr:.1%} in one session → gold", parts=[("GLD", pos, _ones(len(pos)))]))
        V.append(dict(label=f"S&P falls ≥ {thr:.1%} in one session → S&P itself", parts=[("SPY", pos, _ones(len(pos)))], skip0=True))
    return audit("sudden", "gold and the S&P around a sudden one-day S&P fall (D1b)", "price move", series, V, "Positive = the asset rose.")


def t_oil():
    df = pd.read_csv(PROC / "oil_shocks.csv"); df["date"] = pd.to_datetime(df["date"]); g = df[df.asset == "GLD"].drop_duplicates("date"); r = panel(); series = dict(GLD=_ser(r["GLD"])); V = []
    sets = [("all oil shocks", g)]
    if "oil5" in g.columns: sets += [("oil +5–8% in five sessions", g[(g.oil5 > 0) & (g.oil5 <= 0.08)]), ("oil +8–12%", g[(g.oil5 > 0.08) & (g.oil5 <= 0.12)]), ("oil > +12%", g[g.oil5 > 0.12])]
    for lab, s in sets:
        pos = _pos(series["GLD"][0], s["date"]); V.append(dict(label=f"{lab} → gold", parts=[("GLD", pos, _ones(len(pos)))]))
    return audit("oil", "gold around an oil shock (A3a, D5)", "price move", series, V, "Shock dates from processed/oil_shocks.csv (the session the five-session oil rise crosses the threshold). Positive = gold rose.")


def t_fomc():
    from src.chair_power import table
    t = table().dropna(subset=["s_norm"]); r = panel(); series = dict(GLD=_ser(r["GLD"])); V = []
    if "TLT" in r.columns: series["TLT"] = _ser(r["TLT"])
    big = t[t.s_norm.abs() >= t.s_norm.abs().median()]
    for lab, s in (("all statement days", t), ("larger-than-median rate surprise", big)):
        for a in series:
            pos = _pos(series[a][0], s["date"]); sg = -np.sign(s.set_index("date")["s_norm"].reindex(pd.DatetimeIndex(series[a][0][pos])).to_numpy())
            ok = sg != 0; V.append(dict(label=f"{lab} → {'gold' if a == 'GLD' else 'long Treasuries'}", parts=[(a, pos[ok], sg[ok])]))
    return audit("fomc", "gold and Treasuries around Fed statement days, signed by the rate surprise (row 14, T9b)", "information", series, V, "Sign: a rate surprise UP predicts the asset DOWN. Day 0 re-measures the known same-day reaction (T9b); the question here is the days after.")


def t_calls(csv: str):
    df = pd.read_csv(csv); df["date"] = pd.to_datetime(df["date"]); df = df[(df.h == 2) & (df.kind == "call")].dropna(subset=["call"]); r = panel(); series = {}; V = []; pooled = []; skipped = []
    for a, g in df.groupby("asset"):
        if a not in r.columns: skipped.append(a); continue
        series[a] = _ser(r[a]); ix = pd.DatetimeIndex(series[a][0]).get_indexer(pd.DatetimeIndex(g["date"])); ok = ix >= 0; pos = ix[ok]; sg = np.sign(g["call"].to_numpy(float)[ok]); k = sg != 0; part = (a, pos[k], sg[k]); pooled.append(part)
        if k.sum() >= MIN_N: V.append(dict(label=f"calls on {a}", parts=[part]))
    V.insert(0, dict(label="all calls, pooled", parts=pooled))
    if "tier" in df.columns:
        for tier, g in df.groupby("tier"):
            parts = []
            for a, gg in g.groupby("asset"):
                if a not in series: continue
                ix = pd.DatetimeIndex(series[a][0]).get_indexer(pd.DatetimeIndex(gg["date"])); ok = ix >= 0; sg = np.sign(gg["call"].to_numpy(float)[ok]); k = sg != 0; parts.append((a, ix[ok][k], sg[k]))
            if sum(len(p[1]) for p in parts) >= MIN_N: V.append(dict(label=f"tier {tier}", parts=parts))
    return audit("calls", "the report's document-driven calls: the report day itself and the days after (rows 24/27/33, A, D7)", "information", series, V,
                 f"{len(df):,} calls from {Path(csv).name}; sign = the call's direction; day 0 = the report date (the day the documents came out). Assets not in the price panel and skipped: {skipped or 'none'}.")


def t_htables():
    import src.history_tables as HT
    cap = []
    def grab(tid, title, rets, pos, grp=None, note=""): cap.append((tid, title, rets, list(pos), grp)); return {}
    orig = HT.run_table; HT.run_table = grab
    try: HT.h1(); HT.h3(); HT.h4(); HT.h5()
    finally: HT.run_table = orig
    series = {}; V = []
    for tid, title, rets, pos, grp in cap:
        for a in [c for c in ("SPY", "TLT", "GLD", "UUP", "USO") if c in rets.columns]:
            key = a
            if key not in series: series[key] = (rets.index.to_numpy(), rets[a].to_numpy(float))
            p = np.array(pos, int); sg = _ones(len(p))
            if grp is not None: sg = -np.array([grp[q] for q in pos], float); k = sg != 0; p, sg = p[k], sg[k]
            p_ok = np.isfinite(series[key][1][np.clip(p, 0, len(series[key][1]) - 1)]); V.append(dict(label=f"{tid} → {a}", parts=[(key, p[p_ok], sg[p_ok])]))
    return audit("htables", "the history tables' events — Fed decision days (H1), dollar jumps and drops (H3), 2-year yield shocks (H4), regime changes (H5) — on five markets", "price move", series, V,
                 "Events rebuilt by the history-table code itself. H1 is signed by the 2-year yield's move that day (yield up predicts the market down); the others are unsigned (positive = the market rose). H1 is an information event; it is grouped here with the price-move tables, so read its rows with the `fomc` audit.")


def t_states():
    r = panel(); series = {}; V = []; p = PROC / "fast_states.parquet"
    if p.exists():
        S = pd.read_parquet(p); S.index = pd.to_datetime(S.index)
        for a in [c for c in ("SPY", "GLD", "TLT") if c in r.columns]: series[a] = (S.index.to_numpy(), r[a].reindex(S.index).to_numpy(float))
        for col in S.columns:
            lab = S[col].to_numpy()
            for g in sorted(set(int(x) for x in lab[np.isfinite(lab)] if x >= 0)):
                pos = np.where(lab == g)[0]
                if len(pos) < MIN_N: continue
                for a in series: V.append(dict(label=f"fast state {col}:{g} → {a}", parts=[(a, pos, _ones(len(pos)))], skip0=True))
    try:
        from src.daytype import build
        d = build(); idx = d.index.to_numpy(); series["dt_GLD"] = (idx, d["gld"].to_numpy(float)); series["dt_SPY"] = (idx, d["spy"].to_numpy(float)); vc = d["type"].value_counts()
        for ty in list(vc[vc >= 60].index[:25]):
            pos = np.where((d["type"] == ty).to_numpy())[0]
            for key, a in (("dt_GLD", "gold"), ("dt_SPY", "S&P")): V.append(dict(label=f"day-type {ty} → {a}", parts=[(key, pos, _ones(len(pos)))], skip0=True))
        pos = np.where(d["founder"].to_numpy())[0]
        for key, a in (("dt_GLD", "gold"), ("dt_SPY", "S&P")): V.append(dict(label=f"founder's day-type (2y down, 10y up, gold up) → {a}", parts=[(key, pos, _ones(len(pos)))], skip0=True))
    except Exception as e: print(f"  day-types unavailable ({type(e).__name__}: {e})")
    return audit("states", "fast states and day-types → the next 1, 2, 3, 5 sessions (F1, Y3 at short spans)", "price move", series, V, "A state is defined by the day's own moves, so day 0 is not measured. Positive = the market rose.")


def t_liquidity():
    f = Path("data_provenance/liquidity/RRPONTSYD.csv")
    if not f.exists(): print("liquidity: data_provenance/liquidity/RRPONTSYD.csv not on disk -- run `python -m src.deeper2 daily` once to cache it"); return {}
    raw = pd.read_csv(f); dc = next(c for c in raw.columns if "date" in c.lower()); vc = [c for c in raw.columns if c != dc][-1]; rrp = pd.to_numeric(pd.Series(raw[vc].to_numpy(), index=pd.to_datetime(raw[dc])), errors="coerce")
    r = panel(); g = r["GLD"].dropna(); g = g[g.index >= "2013-09-23"]; add = -rrp.reindex(g.index).ffill().diff(); z = (add - add.rolling(60).mean()) / add.rolling(60).std(); series = dict(GLD=(g.index.to_numpy(), g.to_numpy(float))); V = []
    for bar in (0.5, 1.0, 1.5):
        m = (z.abs() > bar).to_numpy(); pos = np.where(m)[0]; V.append(dict(label=f"reverse-repo balance change beyond {bar} sd → gold", parts=[("GLD", pos, np.sign(z.to_numpy()[pos]))]))
    return audit("liquidity", "gold around a large daily change in the Fed's reverse-repo balance (D2c)", "information", series, V, "Sign: liquidity ADDED (money leaving the facility) predicts gold UP. The balance is published the same evening, so day 0 is the day of the change, known after the close.")


def t_resid():
    from src.residual_momentum import residual_series
    series = {}; V = []
    for a in ("GLD", "SLV", "USO", "SPY", "NVDA"):
        try: E, ret = residual_series(a)
        except Exception as e: print(f"  {a}: residual unavailable ({type(e).__name__})"); continue
        series[a] = (ret.index.to_numpy(), ret.to_numpy(float))
        for w in (1, 5, 20):
            s = E.rolling(w).sum(); z = (s / s.rolling(252).std()).to_numpy(); pos = np.where(np.abs(z) > 1.5)[0]
            if len(pos) >= MIN_N: V.append(dict(label=f"{a}: unexplained move over {w} session(s) beyond 1.5 sd", parts=[(a, pos, np.sign(z[pos]))], skip0=True))
    return audit("resid", "after a large unexplained move, does the asset continue (+) or reverse (−) over the next 1–5 sessions (T-H)", "price move", series, V, "Sign: the direction of the unexplained move, so a positive mean = continuation and a negative mean = reversal. Day 0 is the move itself and is not measured.")


TESTS = {"selloff": t_selloff, "sudden": t_sudden, "oil": t_oil, "fomc": t_fomc, "htables": t_htables, "states": t_states, "liquidity": t_liquidity, "resid": t_resid}


def cmd_summary():
    rows = []
    for f in sorted(DOCS.glob("horizon_audit_*.json")):
        j = json.loads(f.read_text())
        if j: rows.append(j)
    if not rows: print("no audit results on disk"); return
    def cell(b, p): return "not measured" if b is None else f"{b['span']}: {b['mean_bp']:+.0f} bp (t {b['t']:+.1f}), {b['variant']}; family p {p:.3f}"
    L = ["# Horizon audit — summary", "", "Every test re-measured on the event day and on days +1 … +5, signed in the direction of its claim. Label rule: family p on the days after < 0.05 → QUANT candidate; else family p on day 0 < 0.05 → SUBJECTIVE grade B candidate (information events) or CONTEXT (price-move events); else NEITHER.", "",
         "| test | event kind | day 0 — best cell | days after — best cell | day −1 check | label |", "|---|---|---|---|---|---|"]
    for j in rows:
        fm = j["family"]; L.append(f"| {j['title']} | {j['kind']} | {cell(fm['day0'].get('best'), fm['day0']['p'])} | {cell(fm['after'].get('best'), fm['after']['p'])} | {'family p %.3f' % fm['before']['p'] if fm['before'].get('best') else 'not measured'} | **{j['label']}** |")
        print(f"{j['name']:10} day0 p {fm['day0']['p']:.3f}   after p {fm['after']['p']:.3f}   before p {fm['before']['p']:.3f}   -> {j['label']}")
    (DOCS / "horizon_audit.md").write_text("\n".join(L) + "\n"); print("-> docs/horizon_audit.md")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["list", "all", "summary", "calls"] + list(TESTS)); ap.add_argument("--csv", default="processed/report_backfill_97d9bf07dd2c_n5793.csv"); a = ap.parse_args(); DOCS.mkdir(exist_ok=True)
    if a.cmd == "list": print("tests: " + ", ".join(list(TESTS) + ["calls"]))
    elif a.cmd == "summary": cmd_summary()
    else:
        for c in (list(TESTS) + ["calls"] if a.cmd == "all" else [a.cmd]):
            try: (t_calls(a.csv) if c == "calls" else TESTS[c]())
            except Exception as e: print(f"\n=== {c}: FAILED -- {type(e).__name__}: {e} (the other tests continue) ===")
        if a.cmd == "all": cmd_summary()
