"""
Surprise conditioning, stage A -- does the level-1 surprise explain the reaction? (T9b)

Registered: docs/prereg_surprise.md (2026-09-29). Nothing here changes the estimator.

Inputs (all on disk)
  data_provenance/doc_reads/fomc_statement__*.json   stance, direction (the reader's read)
  processed/asset_returns.parquet                     3-session forward outcomes, 5-session run-up
  DGS2 daily                                          from the project's FRED cache, else fredapi
                                                      (FRED_API_KEY in .env), else FAIL LOUDLY

Output
  docs/surprise_stageA.md   per-asset table, verdict, the 3x3 (stance x bucket) means

Usage
  python -m src.surprise_stageA                                      # level 1: DGS2 proxy
  python -m src.surprise_stageA --surprise-file data_provenance/mps/monetary-policy-surprises-data.xlsx --inspect
  python -m src.surprise_stageA --surprise-file data_provenance/mps/monetary-policy-surprises-data.xlsx  # level 3
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

READS = Path("data_provenance/doc_reads")
PANEL = Path("processed/asset_returns.parquet")
OUT = Path("docs/surprise_stageA.md")
ASSETS = ["TLT", "GLD", "SPY", "UUP", "USO"]
EXPECTED = {"TLT": -1, "GLD": -1, "SPY": -1, "UUP": +1, "USO": -1}     # sign of b2 under a hawkish surprise
CRITERION_ASSETS = ("TLT", "GLD")
H, RUNUP, THRESH_BP, N_PERM = 3, 5, 2.0, 10_000


def _refuse():
    raise RuntimeError("no fetch inside the surprise test")


def load_dgs2() -> pd.Series:
    """2-year yield, percent, daily. Project cache first; fredapi second; never silent."""
    try:
        from src.data_io import cached_fetch
        df = cached_fetch(source="fred", key="DGS2", fetch_fn=_refuse, force_refresh=False)
        s = df.iloc[:, 0] if isinstance(df, pd.DataFrame) else df
        s = pd.to_numeric(s, errors="coerce").dropna(); s.index = pd.to_datetime(s.index)
        if len(s) > 1000:
            return s
    except Exception:
        pass
    try:
        from dotenv import load_dotenv; load_dotenv()
        from fredapi import Fred
        s = Fred(api_key=os.environ["FRED_API_KEY"]).get_series("DGS2").dropna()
        s.index = pd.to_datetime(s.index); return s
    except Exception as e:
        raise SystemExit(f"DGS2 unavailable from cache and from FRED ({type(e).__name__}: {e}). "
                         "Set FRED_API_KEY in .env or run src.download_data first.")


def load_published(path: str, sheet=None, column=None, inspect=False) -> pd.Series:
    """FRBSF Monetary Policy Surprises (Bauer-Swanson, updated): date -> surprise in bp.
    Column names are taken from the file; --inspect prints sheets and columns and exits."""
    xl = pd.ExcelFile(path)
    if inspect:
        for sh in xl.sheet_names:
            df = xl.parse(sh, nrows=5)
            print(f"sheet {sh!r}: columns {list(df.columns)}")
        raise SystemExit(0)
    sh = sheet or xl.sheet_names[0]
    df = xl.parse(sh)
    dcol = next((c for c in df.columns if "date" in str(c).lower()), df.columns[0])
    if column is None:
        cands = [c for c in df.columns if "mps" in str(c).lower() and "orth" not in str(c).lower()]
        column = cands[0] if cands else next(c for c in df.columns if c != dcol)
    out = pd.Series(pd.to_numeric(df[column], errors="coerce").values, index=pd.to_datetime(df[dcol], errors="coerce")).dropna()
    out = out[~out.index.isna()].sort_index()
    if len(out) < 50:
        raise SystemExit(f"published series: only {len(out)} usable rows from sheet {sh!r} column {column!r} -- "
                         "wrong sheet or column; run --inspect and pass --sheet/--column. Refusing to fall back to the proxy.")
    print(f"published surprises: sheet {sh!r}, column {column!r}, {len(out)} announcements, {out.index.min().date()} -> {out.index.max().date()}")
    return out


def load_statements() -> pd.DataFrame:
    rows = []
    for f in sorted(glob.glob(str(READS / "fomc_statement__*.json"))):
        d = json.loads(Path(f).read_text())
        stance = None
        ex = d.get("extra") or {}
        for k in ("stance", "policy_stance"):
            v = ex.get(k, d.get(k))
            if v is not None:
                stance = v; break
        if isinstance(stance, str):
            s = stance.lower(); stance = 1 if "hawk" in s else (-1 if "dov" in s else 0)
        elif isinstance(stance, (int, float)):
            stance = int(np.sign(stance))
        else:
            dur = (d.get("direction") or {}).get("duration")
            stance = -int(np.sign(dur)) if dur is not None else 0
        rows.append(dict(date=pd.Timestamp(d["date"]), stance=stance))
    df = pd.DataFrame(rows).drop_duplicates("date").set_index("date").sort_index()
    if df.empty:
        raise SystemExit("no fomc_statement reads found under data_provenance/doc_reads")
    return df


def build(stmts: pd.DataFrame, rets: pd.DataFrame, dgs2: pd.Series, published: pd.Series | None = None) -> pd.DataFrame:
    idx = pd.DatetimeIndex(rets.index)
    d2 = dgs2.reindex(idx).ffill()
    out = []
    for t, r in stmts.iterrows():
        if t not in idx:
            j = idx.searchsorted(t); t = idx[j] if j < len(idx) else None
            if t is None:
                continue
        i = idx.get_loc(t)
        if i < RUNUP or i + H >= len(idx):
            continue
        proxy_bp = float((d2.iloc[i] - d2.iloc[i - 1]) * 100)
        pub = None
        if published is not None:
            near = published.loc[t - pd.Timedelta(days=1): t + pd.Timedelta(days=1)]
            pub = float(near.iloc[0]) if len(near) else None
        s_bp = pub if pub is not None else proxy_bp
        bucket = 1 if s_bp > THRESH_BP else (-1 if s_bp < -THRESH_BP else 0)
        row = dict(date=t, stance=int(r["stance"]), s_bp=s_bp, bucket=bucket, is_proxy=(pub is None))
        for a in ASSETS:
            if a not in rets.columns:
                continue
            row[f"y_{a}"] = float(rets[a].iloc[i + 1:i + 1 + H].sum())
            row[f"u_{a}"] = float(rets[a].iloc[i - RUNUP:i].sum())
        out.append(row)
    df = pd.DataFrame(out).set_index("date")
    for a in ASSETS:
        if f"u_{a}" in df:
            u = df[f"u_{a}"]; df[f"u_{a}"] = (u - u.mean()) / (u.std(ddof=0) or 1.0)
    return df


def ols_b2(y, stance, bucket, u):
    X = np.column_stack([np.ones(len(y)), stance, bucket, u])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(beta[2]), beta


def test_asset(df: pd.DataFrame, a: str, rng: np.random.Generator, continuous: bool = False) -> dict:
    d = df.dropna(subset=[f"y_{a}", f"u_{a}"])
    y, st, u = d[f"y_{a}"].to_numpy(), d["stance"].to_numpy(float), d[f"u_{a}"].to_numpy()
    bk = d["s_bp"].to_numpy(float) if continuous else d["bucket"].to_numpy(float)
    b2, beta = ols_b2(y, st, bk, u)
    null = np.empty(N_PERM)
    for k in range(N_PERM):
        null[k], _ = ols_b2(y, st, rng.permutation(bk), u)
    p = float((np.abs(null) >= abs(b2)).mean())
    sign_ok = np.sign(b2) == EXPECTED[a]
    return dict(asset=a, n=int(len(d)), b_stance=float(beta[1]), b_surprise=b2, b_runup=float(beta[3]),
                p_surprise=p, expected_sign=EXPECTED[a], sign_ok=bool(sign_ok), sig=bool(p < 0.05))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--surprise-file", help="FRBSF monetary-policy-surprises xlsx (level 3); omit for level 1")
    ap.add_argument("--sheet"); ap.add_argument("--column")
    ap.add_argument("--inspect", action="store_true", help="print the file's sheets and columns, then exit")
    a = ap.parse_args()
    rng = np.random.default_rng(0)
    published = load_published(a.surprise_file, a.sheet, a.column, a.inspect) if a.surprise_file else None
    level = 3 if published is not None else 1
    continuous = published is not None                      # registered: level 3 uses the bp value continuously
    global OUT
    OUT = Path(f"docs/surprise_stageA_level{level}.md") if level == 3 else OUT
    rets = pd.read_parquet(PANEL); rets.index = pd.to_datetime(rets.index)
    stmts = load_statements(); dgs2 = load_dgs2()
    df = build(stmts, rets, dgs2, published)
    n_proxy = int(df["is_proxy"].sum()) if "is_proxy" in df else 0
    print(f"statements usable: {len(df)}  |  buckets: hawkish {int((df.bucket==1).sum())}, neutral {int((df.bucket==0).sum())}, "
          f"dovish {int((df.bucket==-1).sum())}  |  stance: hawkish {int((df.stance==1).sum())}, neutral {int((df.stance==0).sum())}, "
          f"dovish {int((df.stance==-1).sum())}")
    res = [test_asset(df, a, rng, continuous) for a in ASSETS if f"y_{a}" in df]
    R = {r["asset"]: r for r in res}
    hits = [a for a in CRITERION_ASSETS if a in R and R[a]["sig"] and R[a]["sign_ok"]]
    verdict = "PASS" if len(hits) == 2 else ("INCONCLUSIVE" if len(hits) == 1 else "FAIL")
    src = ("published FRBSF Bauer–Swanson 30-minute surprise (bp), used continuously; "
           f"{n_proxy} statement(s) after the series end use the ΔDGS2 proxy" if level == 3
           else f"same-day ΔDGS2 proxy, buckets at ±{THRESH_BP:.0f} bp")
    L = [f"# Surprise conditioning — stage A, level {level}", "",
         f"*Run {datetime.now():%Y-%m-%d %H:%M}. Registered in `docs/prereg_surprise.md` (§2{'b' if level == 3 else ''}). "
         f"{len(df)} FOMC statements; surprise = {src}; outcome = {H}-session forward log return; "
         f"{N_PERM:,} permutations of the surprise.*", "",
         "| asset | n | b(stance) | b(surprise" + (" per bp" if level == 3 else " per bucket") + ") | b(run-up) | p(surprise) | expected sign | sign ok | significant |",
         "|---|---|---|---|---|---|---|---|---|"]
    for r in res:
        L.append(f"| {r['asset']} | {r['n']} | {r['b_stance']:+.4f} | **{r['b_surprise']:+.4f}** | {r['b_runup']:+.4f} | "
                 f"{r['p_surprise']:.4f} | {'−' if r['expected_sign'] < 0 else '+'} | {'yes' if r['sign_ok'] else 'no'} | "
                 f"{'yes' if r['sig'] else 'no'} |")
    L += ["", f"## Verdict: **{verdict}** (criterion assets: {', '.join(CRITERION_ASSETS)}; met on: {', '.join(hits) or 'none'})", ""]
    # 3x3 descriptive table for GLD and TLT
    for a in ("GLD", "TLT"):
        if f"y_{a}" not in df:
            continue
        tab = df.pivot_table(values=f"y_{a}", index="stance", columns="bucket", aggfunc=["mean", "count"])
        L += [f"### {a}: mean {H}-session return by reader stance (rows) × surprise bucket (columns) — descriptive only", "",
              "| stance \\ surprise | dovish (−1) | neutral (0) | hawkish (+1) |", "|---|---|---|---|"]
        for stv, lab in ((-1, "dovish"), (0, "neutral"), (1, "hawkish")):
            cells = []
            for bk in (-1, 0, 1):
                try:
                    m = tab[("mean", bk)].get(stv, np.nan); n = tab[("count", bk)].get(stv, 0)
                    cells.append(f"{m:+.2%} (n={int(n)})" if n else "—")
                except Exception:
                    cells.append("—")
            L.append(f"| {lab} | " + " | ".join(cells) + " |")
        L.append("")
    L += ["*Reading.* TLT is close to tautological here — the 2-year change on the day is the bond market's own reaction — so "
          "GLD is the informative row. If only TLT passes, the proxy is measuring the bond market, not the surprise, and the "
          "published Swanson / Bauer–Swanson series is the next registration (level 3)."]
    OUT.write_text("\n".join(L) + "\n")
    print("\n".join(L[4:])); print(f"\n  -> {OUT}")


if __name__ == "__main__":
    main()
