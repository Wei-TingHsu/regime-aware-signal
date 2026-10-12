"""
WTI_CONT -- the oil column beside USO (TRACK §3.13; prereg_instrument_robustness amendments 8 and 11 Oct).

  build    FRED DCOILWTICO spot + Yahoo CL=F -> processed/wti_cont.parquet (USO, WTI_SPOT, WTI_FUT log returns on the
           panel's session index); prints correlations and the cumulative USO-vs-spot drag
  chain    W2-seq chain alerts (src.blindspot.chain_alerts) on each oil column; firing dates side by side
  referee  swap ONLY the USO column of the panel for WTI_SPOT, run the report backfill at h=2 under tag <baseline>_wtispot,
           restore (hash-verified); then the same for WTI_FUT -> _wtifut. Never within an hour of the 15:00 job.
  compare  the USO primary cell from the three scoreboards + chain + drag -> docs/wti_cont.md
"""
import argparse, hashlib, os, shutil, subprocess, sys
from datetime import datetime
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
PANEL = Path("processed/asset_returns.parquet")
OUT = Path("processed/wti_cont.parquet")
BACKUP = Path("processed/asset_returns.ORIGINAL_backup_wti.parquet")
LOCK = Path("processed/.wti_test.lock")
RAW = Path("raw/fred/DCOILWTICO.csv")
MD = Path("docs/wti_cont.md")


def _sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def _fred_spot():
    if RAW.exists():
        s = pd.read_csv(RAW, index_col=0, parse_dates=True).iloc[:, 0]
        if s.index.max() >= pd.Timestamp.today().normalize() - pd.Timedelta(days=7):
            return s
    from fredapi import Fred
    s = Fred(api_key=os.environ["FRED_API_KEY"]).get_series("DCOILWTICO")
    RAW.parent.mkdir(parents=True, exist_ok=True); s.to_frame("DCOILWTICO").to_csv(RAW)
    return s


def _yahoo_close(tk, start):
    import yfinance as yf
    d = yf.Ticker(tk).history(start=start, interval="1d", auto_adjust=False)
    if isinstance(d.columns, pd.MultiIndex): d.columns = d.columns.get_level_values(0)
    c = d["Close"]; c.index = pd.to_datetime(c.index).tz_localize(None); return c


def cmd_build(a):
    panel = pd.read_parquet(PANEL); panel.index = pd.to_datetime(panel.index)
    idx = panel.index
    spot = _fred_spot().dropna(); spot = spot[spot > 0]
    fut = _yahoo_close("CL=F", str(idx.min().date())); fut = fut[fut > 0]
    def rets_on(px):
        px = px.reindex(idx.union(px.index)).ffill(limit=3).reindex(idx)
        return np.log(px).diff()
    out = pd.DataFrame({"USO": panel["USO"], "WTI_SPOT": rets_on(spot), "WTI_FUT": rets_on(fut)}, index=idx)
    out.to_parquet(OUT)
    ok = out.dropna()
    print(f"  written {OUT}: {len(out)} sessions, {len(ok)} with all three")
    print("  daily correlation:", ok.corr().round(3).to_dict())
    cum = np.exp(ok.cumsum()).iloc[-1]
    yrs = (ok.index[-1] - ok.index[0]).days / 365.25
    print(f"  {ok.index[0].date()} -> {ok.index[-1].date()} ({yrs:.1f}y) cumulative: USO x{cum['USO']:.2f}, spot x{cum['WTI_SPOT']:.2f}, "
          f"CL=F x{cum['WTI_FUT']:.2f}; USO vs spot drag {(np.log(cum['USO']/cum['WTI_SPOT'])/yrs)*100:+.1f}%/yr")
    for y in (2008, 2014, 2020, 2022, 2026):
        yy = ok.loc[str(y)]
        if len(yy): print(f"    {y}: USO {np.exp(yy['USO'].sum())-1:+.0%}  spot {np.exp(yy['WTI_SPOT'].sum())-1:+.0%}  CL=F {np.exp(yy['WTI_FUT'].sum())-1:+.0%}")


def cmd_chain(a):
    from src.blindspot import chain_alerts, load_macro
    w = pd.read_parquet(OUT); w.index = pd.to_datetime(w.index)
    dgs2, dxy = load_macro(w.index)
    rows = []
    for col in ("USO", "WTI_SPOT", "WTI_FUT"):
        al = chain_alerts(w[col].fillna(0), dgs2, dxy)
        fires = [str(d.date()) for d in al[al].index]
        rows.append((col, len(fires), ", ".join(fires) or "none"))
        print(f"  {col}: {len(fires)} firing(s): {', '.join(fires) or 'none'}")
    pd.DataFrame(rows, columns=["column", "n_fires", "dates"]).to_csv("processed/wti_chain_alerts.csv", index=False)


def cmd_a2(a):
    """Registered A2 (prereg_blindspot §A2) applied to each oil column's firings: gold's forward 20/60-session return,
    permutation null over random 60-session windows, 10,000 draws. n<10 -> INCONCLUSIVE at best, as registered."""
    from src.blindspot import chain_alerts, load_macro
    w = pd.read_parquet(OUT); w.index = pd.to_datetime(w.index)
    panel = pd.read_parquet(PANEL); panel.index = pd.to_datetime(panel.index); gld = panel["GLD"].reindex(w.index).fillna(0)
    dgs2, dxy = load_macro(w.index); rng = np.random.default_rng(0)
    pos = {d: i for i, d in enumerate(w.index)}; valid = np.arange(0, len(w) - 61)
    L = ["| column | firing | gold +20 sessions | gold +60 sessions |", "|---|---|---|---|"]
    for col in ("USO", "WTI_SPOT", "WTI_FUT"):
        al = chain_alerts(w[col].fillna(0), dgs2, dxy); dates = list(al[al].index)
        f60 = []
        for d in dates:
            j = pos[d]; r20 = gld.iloc[j+1:j+21].sum(); r60 = gld.iloc[j+1:j+61].sum()
            if j + 61 <= len(w): f60.append(r60)
            L.append(f"| {col} | {d.date()} | {np.expm1(r20):+.1%} | {np.expm1(r60):+.1%} |")
        if f60:
            m60 = float(np.mean(f60))
            null = np.array([gld.iloc[j+1:j+61].sum() for j in rng.choice(valid, size=(10_000, len(f60))).reshape(-1)]).reshape(10_000, -1).mean(axis=1)
            pval = float((null <= m60).mean())
            verdict = "PASS" if (len(f60) >= 10 and m60 < 0 and pval < 0.05) else ("INCONCLUSIVE" if m60 < 0 else "FAIL")
            L.append(f"| {col} | **mean, n={len(f60)}** | | **{np.expm1(m60):+.1%}, p {pval:.3f} -> {verdict}** |")
    Path("processed/wti_chain_a2.md").write_text("\n".join(L) + "\n"); print("\n".join(L))


def _swap_run(col, tag, n_perm):
    if LOCK.exists(): raise SystemExit(f"{LOCK} exists -- a previous run did not restore the panel; check {BACKUP} by hand")
    w = pd.read_parquet(OUT); panel = pd.read_parquet(PANEL)
    alt = panel.copy(); alt["USO"] = w[col].reindex(panel.index).values
    LOCK.write_text(str(datetime.now())); shutil.copy2(PANEL, BACKUP); h = _sha(PANEL)
    try:
        alt.to_parquet(PANEL)
        print(f"  panel USO -> {col} (original {h} backed up); backfill -> {tag}")
        r = subprocess.run([sys.executable, "-m", "src.report_backfill", "--hash", tag, "--n-perm", str(n_perm)])
        if r.returncode != 0: print("  backfill returned non-zero")
    finally:
        shutil.copy2(BACKUP, PANEL); ok = _sha(PANEL) == h
        print(f"  panel restored: {'verified' if ok else 'HASH MISMATCH -- inspect ' + str(BACKUP)}")
        if ok: LOCK.unlink(missing_ok=True)


def cmd_referee(a):
    for col, suf in (("WTI_SPOT", "wtispot"), ("WTI_FUT", "wtifut")):
        tag = f"{a.baseline}_{suf}"
        if Path(f"docs/report_scoreboard_backfill_{tag}.md").exists(): print(f"  {tag}: exists, skipped"); continue
        _swap_run(col, tag, a.n_perm)


def _uso_rows(tag):
    f = Path(f"docs/report_scoreboard_backfill_{tag}.md")
    if not f.exists(): return ["(not run)"]
    return [l for l in f.read_text().splitlines() if l.startswith("| USO") or l.startswith("| h2_primary")]


def cmd_compare(a):
    w = pd.read_parquet(OUT).dropna(); yrs = (w.index[-1] - w.index[0]).days / 365.25
    cum = np.exp(w.cumsum()).iloc[-1]
    ch = pd.read_csv("processed/wti_chain_alerts.csv") if Path("processed/wti_chain_alerts.csv").exists() else None
    L = ["# WTI_CONT beside USO — oil column re-runs (TRACK §3.13)", "",
         f"*{datetime.now():%Y-%m-%d}. Columns: USO (model instrument), WTI_SPOT = FRED DCOILWTICO, WTI_FUT = Yahoo CL=F as spliced. "
         f"Sessions with all three: {len(w)} ({w.index[0].date()} → {w.index[-1].date()}).*", "",
         "## 1. The instrument itself", "",
         f"Daily correlation USO–spot {w['USO'].corr(w['WTI_SPOT']):.3f}, USO–CL=F {w['USO'].corr(w['WTI_FUT']):.3f}, spot–CL=F "
         f"{w['WTI_SPOT'].corr(w['WTI_FUT']):.3f}. Cumulative over {yrs:.1f} years: USO ×{cum['USO']:.2f}, spot ×{cum['WTI_SPOT']:.2f}, "
         f"CL=F ×{cum['WTI_FUT']:.2f}; USO's drag against spot {(np.log(cum['USO']/cum['WTI_SPOT'])/yrs)*100:+.1f}% a year. "
         "What this measures: the level drift of the ETF against the commodity. What it does not: the day-to-day direction, which "
         "is what the engine's calls are scored on — see §3.", "",
         "## 2. Chain alerts (W2-seq) by oil column", ""]
    if ch is not None:
        L += ["| column | firings | dates |", "|---|---|---|"] + [f"| {r.column} | {r.n_fires} | {r.dates} |" for r in ch.itertuples()]
    a2p = Path("processed/wti_chain_a2.md")
    L += ["", "The rule was calibrated on USO (8 Oct). Same dates on all three = the rule is about oil, not about the ETF.", ""]
    if a2p.exists(): L += ["**A2 on each column's firings (gold forward):**", ""] + a2p.read_text().splitlines()
    L += ["",
          "## 3. Referee — the USO cell with each column (h = 2, 10,000 permutations, USO column swapped only)", ""]
    for tag, name in ((a.baseline, "USO (baseline)"), (f"{a.baseline}_wtispot", "WTI_SPOT"), (f"{a.baseline}_wtifut", "WTI_FUT")):
        L += [f"**{name}** — `{tag}`", ""] + _uso_rows(tag) + [""]
    L += ["Read against the 29 Sep criteria C1–C4 (prereg_instrument_robustness): verdict class unchanged, hit-rate within the "
          "stated band, same sign. Status: measured, this file; T1's USO cell on the new column is the next registered step; the "
          "oil amendment is complete when that is in.", ""]
    MD.write_text("\n".join(L)); print("\n".join(L)); print(f"-> {MD}")


def _rows_h2(tag):
    import json
    df = pd.read_csv(f"processed/report_backfill_{tag}.csv", parse_dates=["date"])
    df = df[(df["h"] == 2) & (df["kind"] == "call") & (df["status"] == "matured")].copy()
    df["hit"] = (np.sign(df["call"]) == np.sign(df["ret_primary"])) & (df["ret_primary"] != 0)
    j = json.loads(Path(f"processed/report_scoreboard_backfill_{tag}.json").read_text())
    return df.set_index(["date", "asset"]), j["verdict"], j["cells"]["h2_primary"]["nonoverlap"]


def cmd_criteria(a):
    """C1 verdict identical; C2 row-level hit/miss agreement >= 90%; C3 non-overlap hit-rate within 2.0 pts; C4 asymmetry within 0.15."""
    rb, vb, cb = _rows_h2(a.baseline)
    L = ["## 4. C1–C4 at h = 2 (criteria as registered 29 Sep)", ""]
    for suf, name in (("wtispot", "WTI_SPOT"), ("wtifut", "WTI_FUT")):
        tag = f"{a.baseline}_{suf}"
        if not Path(f"processed/report_backfill_{tag}.csv").exists(): L.append(f"{name}: not run"); continue
        ra, va, ca = _rows_h2(tag)
        common = rb.index.intersection(ra.index)
        agree = rb.loc[common, "hit"].to_numpy() == ra.loc[common, "hit"].to_numpy()
        c1 = vb == va; c2 = float(agree.mean())
        c3 = abs(cb["hit"] - ca["hit"]) * 100 <= 2.0; c4 = abs(cb["asym"] - ca["asym"]) <= 0.15
        verdict = "CONSISTENT" if (c1 and c2 >= 0.90 and c3 and c4) else "DIFFERENT"
        L += [f"**{name}** (`{tag}`) — **{verdict}**", "",
              "| criterion | USO baseline | " + name + " | threshold | met |", "|---|---|---|---|---|",
              f"| C1 primary verdict | {vb} | {va} | identical | {'yes' if c1 else 'NO'} |",
              f"| C2 row-level hit/miss agreement | — | {c2:.1%} on {len(common):,} shared rows | ≥ 90% | {'yes' if c2 >= 0.9 else 'NO'} |",
              f"| C3 non-overlap hit-rate | {cb['hit']:.1%} | {ca['hit']:.1%} | within 2.0 pts | {'yes' if c3 else 'NO'} |",
              f"| C4 asymmetry | {cb['asym']:.3f} | {ca['asym']:.3f} | within 0.15 | {'yes' if c4 else 'NO'} |", "",
              "| asset | shared rows | agreement | flips |", "|---|---|---|---|"]
        flips = pd.Series(~agree, index=common)
        for asset in ("SPY", "TLT", "GLD", "UUP", "USO"):
            m = [i for i in common if i[1] == asset]
            if m: L.append(f"| {asset} | {len(m)} | {1 - flips.loc[m].mean():.1%} | {int(flips.loc[m].sum())} |")
        L.append("")
    L.append("Only the USO column was swapped, so every flip is an oil row: the other four assets must show 100% agreement, "
             "and the USO line is the whole result. What C1–C4 measure: whether the panel-level verdict depends on the oil "
             "instrument. What they do not: whether the oil cell itself is tradeable (n ≈ 55).")
    txt = "\n".join(L); print(txt)
    md = MD.read_text()
    if "## 4. C1–C4" not in md: MD.write_text(md.rstrip("\n") + "\n\n" + txt + "\n"); print(f"-> appended to {MD}")


def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build"); sub.add_parser("chain"); sub.add_parser("a2")
    r = sub.add_parser("referee"); r.add_argument("--baseline", required=True); r.add_argument("--n-perm", type=int, default=10_000)
    c = sub.add_parser("compare"); c.add_argument("--baseline", required=True)
    k = sub.add_parser("criteria"); k.add_argument("--baseline", required=True)
    a = ap.parse_args()
    {"build": cmd_build, "chain": cmd_chain, "a2": cmd_a2, "referee": cmd_referee, "compare": cmd_compare, "criteria": cmd_criteria}[a.cmd](a)


if __name__ == "__main__":
    main()
