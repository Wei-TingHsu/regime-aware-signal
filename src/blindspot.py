"""
T13 case A -- the blind-spot flag and the commodity-shock chain. Registered: docs/prereg_blindspot.md.

  python -m src.blindspot --backfill      # A1 state shares + A2 chain-alert test on 2006-2026 -> docs/blindspot_backfill.md
  python -m src.blindspot --today         # nightly: writes outputs/blindspot/YYYYMMDD.json for the last completed session
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

LAMBDA, BIG, WIN, DGS2_BP = 0.94, 2.0, 5, 10.0
HL = 20
ASSETS = ["SPY", "TLT", "GLD", "UUP", "USO"]
AX = {"SPY": "equity", "TLT": "duration", "GLD": "gold", "UUP": "dollar", "USO": "oil"}
OUT = Path("outputs/blindspot"); PROC = Path("processed"); REPORTS = Path("outputs/reports")


def ewma_sigma(r: pd.Series) -> pd.Series:
    v = r.fillna(0).pow(2).ewm(alpha=1 - LAMBDA, adjust=False).mean().shift(1)
    return np.sqrt(v)


def _refuse():
    raise RuntimeError("no fetch")


def load_macro(idx):
    """DGS2 and DTWEXBGS from the FRED cache (fredapi fallback with FRED_API_KEY)."""
    out = {}
    for key in ("DGS2", "DTWEXBGS"):
        s = None
        try:
            from src.data_io import cached_fetch
            d = cached_fetch(source="fred", key=key, fetch_fn=_refuse, force_refresh=False)
            s = d.iloc[:, 0] if isinstance(d, pd.DataFrame) else d
        except Exception:
            try:
                from dotenv import load_dotenv; load_dotenv()
                from fredapi import Fred
                s = Fred(api_key=os.environ["FRED_API_KEY"]).get_series(key)
            except Exception:
                s = None
        if s is None:
            raise SystemExit(f"{key} unavailable")
        s = pd.to_numeric(s, errors="coerce"); s.index = pd.to_datetime(s.index)
        out[key] = s.reindex(idx).ffill()
    return out["DGS2"], out["DTWEXBGS"]


def chain_alerts(z_oil: pd.Series, dgs2: pd.Series, dxy: pd.Series) -> pd.Series:
    """True on session t if within the last WIN sessions oil had a big up move, DGS2 rose >= DGS2_BP, DXY rose."""
    big_up = (z_oil > BIG)
    oil_recent = big_up.rolling(WIN, min_periods=1).max().astype(bool)
    d2 = (dgs2 - dgs2.shift(WIN)) * 100 >= DGS2_BP
    dx = dxy > dxy.shift(WIN)
    return oil_recent & d2 & dx


def coverage_for_day(day: pd.Timestamp) -> dict:
    """From the written report: per asset, covering document present? sign of net_view?"""
    f = REPORTS / f"{day:%Y%m%d}.json"
    if not f.exists():
        return {a: dict(covered=False, net=None) for a in ASSETS}
    R = json.loads(f.read_text()); out = {}
    for a in ASSETS:
        docs = [d for d in R.get("documents", []) if abs((d.get("direction") or {}).get(AX[a]) or 0) > 0.05]
        out[a] = dict(covered=bool(docs), net=R["assets"][a].get("net_view"))
    return out


def state(z: float, cov: dict) -> str | None:
    if not np.isfinite(z) or abs(z) <= BIG:
        return None
    if not cov["covered"]:
        return "A"
    if cov["net"] is not None and np.sign(cov["net"]) == -np.sign(z):
        return "B"
    return "C"


def backfill(out_md=Path("docs/blindspot_backfill.md"), n_perm=10_000):
    rng = np.random.default_rng(0)
    rets = pd.read_parquet(PROC / "asset_returns.parquet"); rets.index = pd.to_datetime(rets.index)
    z = {a: rets[a] / ewma_sigma(rets[a]) for a in ASSETS}
    dgs2, dxy = load_macro(rets.index)
    L = [f"# T13 case A — blind-spot backfill", "", f"*Run {datetime.now():%Y-%m-%d %H:%M}. Registered in `docs/prereg_blindspot.md`. "
         f"{rets.index[0].date()} → {rets.index[-1].date()}; big move = |z| > {BIG}; chain window {WIN} sessions, DGS2 ≥ {DGS2_BP:.0f} bp.*", ""]
    # A1: state shares on the days the engine has reports for (backfill folder preferred, else live reports)
    bf = sorted(Path("outputs/reports_backfill").glob("*/"), key=lambda p: p.stat().st_mtime)
    rep_dir = (bf[-1] if bf else REPORTS)
    L += [f"## A1 — state shares on big-move days (reports from `{rep_dir}`)", "", "| market | big-move days | A blind | B wrong | C seen |", "|---|---|---|---|---|"]
    for a in ASSETS:
        cnt = {"A": 0, "B": 0, "C": 0}; n = 0
        for d, zz in z[a].items():
            if not np.isfinite(zz) or abs(zz) <= BIG:
                continue
            f = rep_dir / f"{d:%Y%m%d}.json"
            if not f.exists():
                continue
            R = json.loads(f.read_text())
            docs = [x for x in R.get("documents", []) if abs((x.get("direction") or {}).get(AX[a]) or 0) > 0.05]
            cov = dict(covered=bool(docs), net=R["assets"][a].get("net_view"))
            s = state(zz, cov); cnt[s] += 1; n += 1
        L.append(f"| {a} | {n} | {cnt['A']/max(n,1):.0%} | {cnt['B']/max(n,1):.0%} | {cnt['C']/max(n,1):.0%} |" if n else f"| {a} | 0 | — | — | — |")
    L.append("\n*Only document days have reports, so these shares describe big moves on days the engine wrote a report; big moves on "
             "days with no documents at all are state A by definition and are counted in A2's denominator, not here.*")
    # A2: chain alerts -> gold forward returns
    alerts = chain_alerts(z["USO"], dgs2, dxy)
    starts = alerts & ~alerts.shift(1, fill_value=False)        # first day of each alert run
    dates = list(starts[starts].index)
    gld = rets["GLD"]
    def fwd(d, h):
        i = gld.index.get_loc(d); return float(gld.iloc[i + 1:i + 1 + h].sum()) if i + h < len(gld) else np.nan
    f20 = np.array([fwd(d, 20) for d in dates]); f60 = np.array([fwd(d, 60) for d in dates])
    f20, f60 = f20[np.isfinite(f20)], f60[np.isfinite(f60)]
    m60 = float(f60.mean()) if len(f60) else np.nan
    valid = np.arange(len(gld) - 61)
    null = np.array([gld.iloc[j + 1:j + 61].sum() for j in rng.choice(valid, size=(n_perm, max(len(f60), 1))).reshape(-1)]).reshape(n_perm, -1).mean(axis=1) if len(f60) else np.array([np.nan])
    p = float((null <= m60).mean()) if len(f60) else np.nan
    verdict = ("PASS" if (len(f60) >= 10 and m60 < 0 and p < 0.05) else ("INCONCLUSIVE" if (np.isfinite(m60) and m60 < 0) else "FAIL"))
    L += ["", "## A2 — chain alerts and gold's forward return", "",
          f"Chain alert runs: **{len(dates)}** ({', '.join(d.strftime('%Y-%m-%d') for d in dates[:20])}{' …' if len(dates) > 20 else ''})", "",
          f"| horizon | n | mean gold return after alert | one-sided p vs random dates |", "|---|---|---|---|",
          f"| 20 sessions | {len(f20)} | {f20.mean() if len(f20) else float('nan'):+.3%} | — |",
          f"| 60 sessions | {len(f60)} | {m60:+.3%} | {p:.4f} |", "",
          f"## Verdict A2: **{verdict}** (registered prior: INCONCLUSIVE — {'held' if verdict == 'INCONCLUSIVE' else 'wrong'})", "",
          "A PASS is the only verdict under which the gold card's chain alert may carry a direction. Named precedents: "
          "2022-03 (Ukraine) and 2026-03 (Iran) — reported whether or not they fall inside the alert set."]
    out_md.write_text("\n".join(L) + "\n"); print("\n".join(L)); print(f"\n  -> {out_md}")


def today():
    rets = pd.read_parquet(PROC / "asset_returns.parquet"); rets.index = pd.to_datetime(rets.index)
    day = rets.index[-1]
    f = OUT / f"{day:%Y%m%d}.json"
    if f.exists():
        print(f"blindspot: {f.name} exists, not rewritten"); return
    OUT.mkdir(parents=True, exist_ok=True)
    z = {a: float((rets[a] / ewma_sigma(rets[a])).iloc[-1]) for a in ASSETS}
    cov = coverage_for_day(day)
    # B-rate (EW, half-life HL) from the ledger of past files
    hist = sorted(OUT.glob("*.json"))
    b_rate = {}
    for a in ASSETS:
        xs = []
        for h in hist[-120:]:
            rec = json.loads(h.read_text()).get("states", {}).get(a)
            if rec in ("A", "B", "C"):
                xs.append(1.0 if rec == "B" else 0.0)
        if xs:
            w = 0.5 ** (np.arange(len(xs))[::-1] / HL); b_rate[a] = float(np.dot(w, xs) / w.sum())
        else:
            b_rate[a] = 0.0
    dgs2, dxy = load_macro(rets.index)
    alert = bool(chain_alerts(rets["USO"] / ewma_sigma(rets["USO"]), dgs2, dxy).iloc[-1])
    rec = dict(date=day.strftime("%Y-%m-%d"), z=z, states={a: state(z[a], cov[a]) for a in ASSETS},
               b_rate=b_rate, haircut={a: 1 - 0.5 * b_rate[a] for a in ASSETS},
               chain_alert=alert,
               chain_inputs=dict(oil_z=z["USO"], dgs2_5d_bp=float((dgs2.iloc[-1] - dgs2.iloc[-1 - WIN]) * 100), dxy_5d=float(dxy.iloc[-1] / dxy.iloc[-1 - WIN] - 1)))
    f.write_text(json.dumps(rec, indent=2))
    flagged = {a: s for a, s in rec["states"].items() if s}
    print(f"blindspot {rec['date']}: {flagged or 'no big moves'}; chain alert {alert}")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--backfill", action="store_true"); ap.add_argument("--today", action="store_true")
    a = ap.parse_args()
    if a.backfill: backfill()
    if a.today: today()


if __name__ == "__main__":
    main()
