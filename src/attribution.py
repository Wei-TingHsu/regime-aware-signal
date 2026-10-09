"""
T16 Part B -- the attribution engine, historical two-bin form. Registered: docs/prereg_prints_and_attribution.md B2-B4.

  python -m src.attribution --build-ohlc           # fetch & cache daily Open/Close for the five model ETFs (Yahoo; once)
  python -m src.attribution --states               # refined coverage states A / B misread / D not-the-driver / C on big-move days
  python -m src.attribution --influence            # influence weights per source class x regime (hit share vs null, slope)

Event-class timestamps (fixed, prereg B2):
  fomc_statement 14:00 ET -> intraday bin        fomc_minutes 14:00 -> intraday
  earnings_8k    uses the filing's acceptance time when the report carries it; else: pre-market -> overnight (most releases)
  political_*    overnight (Federal Register publication is next day; the act is overnight relative to the session)
  data_print     08:30 -> overnight (T16 Part A; not yet a source)
Nothing here touches the report, the estimator or the forward ledger.
"""
from __future__ import annotations
import argparse, json
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd

LAMBDA, BIG, N_PERM, MIN_EVENTS = 0.94, 2.0, 10_000, 30
ASSETS = ["SPY", "TLT", "GLD", "UUP", "USO"]
AX = {"SPY": "equity", "TLT": "duration", "GLD": "gold", "UUP": "dollar", "USO": "oil"}
OHLC = Path("processed/ohlc_core.parquet")
BIN_OF = {"fomc_statement": "intraday", "fomc_minutes": "intraday", "earnings_8k": "overnight",
          "political_order": "overnight", "political_other": "overnight", "political": "overnight", "data_print": "overnight"}


def ewma_sigma(r): return np.sqrt(r.fillna(0).pow(2).ewm(alpha=1 - LAMBDA, adjust=False).mean().shift(1))


def dir_of(doc, a):
    d = doc.get("direction") or {}; v = d.get(a)
    if v is None: v = d.get(AX[a])
    return float(v or 0.0)


def build_ohlc():
    import yfinance as yf
    frames = {}
    for a in ASSETS:
        d = yf.Ticker(a).history(start="2005-12-01", interval="1d", auto_adjust=False)
        if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
        d.index = pd.to_datetime(d.index).tz_localize(None) if getattr(d.index, "tz", None) is not None else pd.to_datetime(d.index)
        frames[a] = d[["Open", "Close"]]
    out = pd.concat(frames, axis=1); out.to_parquet(OHLC)
    print(f"ohlc cached: {OHLC} {out.index.min().date()} -> {out.index.max().date()}")


def bins(ohlc: pd.DataFrame, a: str) -> pd.DataFrame:
    o, c = ohlc[(a, "Open")], ohlc[(a, "Close")]
    return pd.DataFrame({"overnight": np.log(o / c.shift(1)), "intraday": np.log(c / o), "day": np.log(c / c.shift(1))})


def report_dir():
    bf = sorted([d for d in Path("outputs/reports_backfill").glob("*/") if "altinstr" not in d.name], key=lambda p: p.stat().st_mtime)
    return bf[-1] if bf else Path("outputs/reports")


PRINT_AXES = {   # fixed sign map, registered 9 Oct (T16 A2): direction per unit of positive surprise; the influence table tests it per regime
    "empsit": {"SPY": +1, "TLT": -1, "UUP": +1, "GLD": -1}, "unrate": {"SPY": -1, "TLT": +1, "UUP": -1, "GLD": +1},
    "claims": {"SPY": -1, "TLT": +1, "UUP": -1}, "cpi": {"TLT": -1, "UUP": +1, "GLD": -1}, "cpi_core": {"TLT": -1, "UUP": +1, "GLD": -1},
    "ppi": {"TLT": -1, "UUP": +1}, "pce": {"TLT": -1, "UUP": +1, "GLD": -1}, "gdp": {"SPY": +1, "TLT": -1, "UUP": +1}, "retail": {"SPY": +1, "TLT": -1},
}
_PRINTS = None


def prints_on(day: pd.Timestamp) -> list:
    """Layer-1 prints as data_print events (overnight bin). Reading = sign(surprise) scaled to +-0.5 by the print's own surprise z over history."""
    global _PRINTS
    if _PRINTS is None:
        p = Path("processed/prints.csv")
        if not p.exists(): _PRINTS = pd.DataFrame(); return []
        df = pd.read_csv(p, parse_dates=["date"]).dropna(subset=["surprise"])
        df["z"] = df.groupby("name")["surprise"].transform(lambda x: (x - x.mean()) / (x.std(ddof=0) or 1.0))
        _PRINTS = df
    if _PRINTS.empty: return []
    out = []
    for _, r in _PRINTS[_PRINTS.date == day].iterrows():
        axes = PRINT_AXES.get(r["name"], {})
        if not axes: continue
        mag = float(min(1.0, abs(r["z"]) / 2))                         # a 2-sigma surprise is magnitude 1
        out.append(dict(source="data_print", bin="overnight", direction={a: axes.get(a, 0) * np.sign(r["z"]) * 0.5 for a in ASSETS}, mag=mag, spec=0.9, name=r["name"]))
    return out


def events_on(day: pd.Timestamp, rep_dir: Path, with_prints: bool = True):
    f = rep_dir / f"{day:%Y%m%d}.json"
    if not f.exists():
        return (None, []) if not with_prints else ({"documents": []}, prints_on(day))
    R = json.loads(f.read_text())
    ev = prints_on(day) if with_prints else []
    for d in R.get("documents", []):
        src = d.get("source", ""); b = BIN_OF.get(src, "overnight")
        ev.append(dict(source=src, bin=b, direction={a: dir_of(d, a) for a in ASSETS}, mag=float(d.get("magnitude") or 0), spec=float(d.get("specificity") or 0)))
    return R, ev


def states(out_md=Path("docs/attribution_states.md"), with_prints=True):
    if not OHLC.exists(): raise SystemExit("run --build-ohlc first")
    ohlc = pd.read_parquet(OHLC); rets = pd.read_parquet("processed/asset_returns.parquet"); rets.index = pd.to_datetime(rets.index)
    rep = report_dir()
    L = ["# T16 B2 — refined coverage states on big-move days", "",
         f"*Run {datetime.now():%Y-%m-%d %H:%M}. Registered in `docs/prereg_prints_and_attribution.md`. Reports from `{rep.name}`; bins from daily open/close; "
         f"big move = |z| > {BIG}. Days with any document OR any data print ({'prints included' if with_prints else 'prints excluded'}). B = a document in the same bin as the move reading against it (a misread); "
         f"D = the only document on that axis is in the other bin (not the driver); the 8 Oct 'wrong' column was B + D.*", "",
         "| market | big-move document days | A blind | **B misread** | **D not the driver** | C seen | of which move was mostly overnight |", "|---|---|---|---|---|---|---|"]
    for a in ASSETS:
        z = rets[a] / ewma_sigma(rets[a]); bb = bins(ohlc, a)
        cnt = {"A": 0, "B": 0, "C": 0, "D": 0}; n = 0; ovn = 0
        for d, zz in z.items():
            if not np.isfinite(zz) or abs(zz) <= BIG or d not in bb.index: continue
            R, ev = events_on(d, rep, with_prints)
            if R is None or (not ev and not R.get("documents")): continue
            n += 1
            big_bin = "overnight" if abs(bb.loc[d, "overnight"]) >= abs(bb.loc[d, "intraday"]) else "intraday"
            if big_bin == "overnight": ovn += 1
            on_axis = [e for e in ev if abs(e["direction"][a]) > 0.05]
            if not on_axis: cnt["A"] += 1; continue
            same = [e for e in on_axis if e["bin"] == big_bin]
            if same:
                net = sum(e["direction"][a] * max(e["mag"] * e["spec"], 1e-6) for e in same)
                cnt["C" if np.sign(net) == np.sign(bb.loc[d, big_bin]) else "B"] += 1
            else:
                cnt["D"] += 1
        f = lambda k: f"{cnt[k] / max(n, 1):.0%}"
        L.append(f"| {a} | {n} | {f('A')} | **{f('B')}** | **{f('D')}** | {f('C')} | {ovn / max(n, 1):.0%} |")
    L += ["", "*The last column is the share of big-move days whose larger half was the overnight gap — the bin where the 08:30 prints land. "
          "Until T16 Part A makes prints a source, most of those days are state A.*"]
    out_md.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"\n  -> {out_md}")


def influence(out_md=Path("docs/attribution_influence.md")):
    if not OHLC.exists(): raise SystemExit("run --build-ohlc first")
    import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import asset_extension as AE
    cfg = AE.load_config(); sc, _ = AE.load_data(); lab = pd.Series(np.asarray(AE.regime_labels_expanding(sc, cfg)), index=pd.DatetimeIndex(sc.index))
    ohlc = pd.read_parquet(OHLC); rep = report_dir(); rng = np.random.default_rng(0)
    rows = []
    days = sorted(set(pd.Timestamp(f.stem) for f in rep.glob("*.json")) | set(pd.read_csv("processed/prints.csv", parse_dates=["date"]).date) if Path("processed/prints.csv").exists() else set(pd.Timestamp(f.stem) for f in rep.glob("*.json")))
    for day in days:
        if day not in ohlc.index or day not in lab.index or lab.loc[day] < 0: continue
        R, ev = events_on(day, rep)
        for a in ASSETS:
            bb = bins(ohlc, a).loc[day]
            for e in ev:
                dv = e["direction"][a]
                if abs(dv) <= 0.05: continue
                rows.append(dict(date=day, asset=a, source=(e["source"] + ":" + e["name"]) if e.get("name") else e["source"], regime=int(lab.loc[day]), reading=dv, move=float(bb[e["bin"]])))
    df = pd.DataFrame(rows)
    L = ["# T16 B4 — influence weights per source class × regime", "",
         f"*Run {datetime.now():%Y-%m-%d %H:%M}. Registered in `docs/prereg_prints_and_attribution.md` B4. An event = one document with a non-zero reading on one asset; "
         f"its move = the bin it landed in (overnight for prints/8-Ks/orders, intraday for FOMC). Hit share vs a within-class permutation null ({N_PERM:,} draws); "
         f"weight > 0 only at p < 0.05 with ≥ {MIN_EVENTS} events. **Displayed only; not used in the 3-day line.***", "",
         "| asset | source | regime | events | hit share | null mean | p | slope (bp per unit reading) | weight |", "|---|---|---|---|---|---|---|---|---|"]
    for (a, src, r), g in df.groupby(["asset", "source", "regime"]):
        n = len(g)
        hit = float((np.sign(g.reading) == np.sign(g["move"])).mean())
        reading = g.reading.to_numpy(); move = g["move"].to_numpy()
        null = np.array([(np.sign(rng.permutation(reading)) == np.sign(move)).mean() for _ in range(N_PERM if n >= MIN_EVENTS else 200)])
        p = float((null >= hit).mean())
        slope = float(np.polyfit(reading, move, 1)[0] * 1e4) if n >= 5 else float("nan")
        w = "**earned**" if (n >= MIN_EVENTS and p < 0.05) else ("too few" if n < MIN_EVENTS else "none")
        L.append(f"| {a} | {src} | {r} | {n} | {hit:.0%} | {null.mean():.0%} | {p:.3f} | {slope:+.1f} | {w} |")
    out_md.write_text("\n".join(L) + "\n"); print("\n".join(L[:40])); print(f"  ... {len(L) - 8} rows -> {out_md}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--build-ohlc", action="store_true"); ap.add_argument("--states", action="store_true"); ap.add_argument("--influence", action="store_true")
    ap.add_argument("--no-prints", action="store_true", help="states without the data_print events (the before picture)")
    a = ap.parse_args()
    if a.build_ohlc: build_ohlc()
    if a.states: states(Path("docs/attribution_states_noprints.md") if a.no_prints else Path("docs/attribution_states.md"), with_prints=not a.no_prints)
    if a.influence: influence()


if __name__ == "__main__":
    main()
