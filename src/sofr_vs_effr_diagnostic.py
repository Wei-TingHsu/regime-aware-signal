"""
SOFR-vs-EFFR diagnostic  (decide how to extend the macro regime's history)

The macro PCA panel inner-joins its FRED series, so SOFR (starts 2018-04)
truncates the WHOLE panel to ~2018+, which is why the macro cross-check only
spanned 2018-2026. EFFR (effective fed funds rate) is already in the panel
and runs back to the 1950s. If EFFR carries essentially the same short-rate/
liquidity signal as SOFR, we can DROP SOFR and refit on the full 1995+ panel
-- no imputation, no weaker data, 3 decades of history back.

This script answers three questions so the drop-vs-splice call is evidence-based:
  1. How correlated are SOFR and EFFR on their overlap (levels AND daily changes)?
  2. How truncating is SOFR really -- what span does the panel gain by dropping it?
  3. Does SOFR add a distinct signal, or is it ~redundant with EFFR?
     (regress SOFR on EFFR; a high R^2 + tiny residual => redundant.)

Reads only what you already have: processed/macro_panel.parquet (preferred) or
the config's fred_series roles to locate the two columns.

Run:
    python -m src.sofr_vs_effr_diagnostic
Optional:
    --panel processed/macro_panel.parquet
"""
import argparse

import numpy as np
import pandas as pd

from src.data_io import load_config


def find_col(df, wanted_roles, cfg):
    """Locate a column by trying role->id mapping from config, then raw ids/names."""
    # Build role->id map from config fred_series
    role_to_id = {}
    for e in cfg.get("fred_series", []):
        role_to_id[e.get("role")] = e.get("id")
    candidates = []
    for r in wanted_roles:
        candidates.append(r)                      # column might be named by role
        if r in role_to_id:
            candidates.append(role_to_id[r])      # or by FRED id
    for c in candidates:
        if c in df.columns:
            return c
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--panel", default="processed/macro_panel.parquet")
    args = ap.parse_args()

    cfg = load_config()
    df = pd.read_parquet(args.panel)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    print("=" * 72)
    print("SOFR vs EFFR -- panel-extension diagnostic")
    print("=" * 72)
    print(f"macro_panel: {df.shape[1]} cols, {len(df)} rows, "
          f"{df.index.min().date()} -> {df.index.max().date()}")

    sofr_col = find_col(df, ["sofr"], cfg)
    effr_col = find_col(df, ["effective_ff_rate", "effr"], cfg)
    if sofr_col is None or effr_col is None:
        raise SystemExit(f"could not locate columns. sofr={sofr_col}, effr={effr_col}. "
                         f"panel columns: {list(df.columns)}")
    print(f"using columns:  SOFR='{sofr_col}'   EFFR='{effr_col}'")

    s, e = df[sofr_col], df[effr_col]

    # --- 1. spans & the truncation cost ------------------------------------
    s_start = s.dropna().index.min()
    full_no_sofr = df.drop(columns=[sofr_col]).dropna()
    full_with_sofr = df.dropna()
    print("\n[1] TRUNCATION COST")
    print(f"  SOFR first observation: {s_start.date()}")
    print(f"  panel span WITH SOFR (inner-join): "
          f"{full_with_sofr.index.min().date()} -> {full_with_sofr.index.max().date()} "
          f"({len(full_with_sofr)} rows)")
    print(f"  panel span WITHOUT SOFR:            "
          f"{full_no_sofr.index.min().date()} -> {full_no_sofr.index.max().date()} "
          f"({len(full_no_sofr)} rows)")
    print(f"  -> dropping SOFR recovers "
          f"{len(full_no_sofr) - len(full_with_sofr):+d} rows of history.")

    # --- 2. how alike are they, on the overlap -----------------------------
    both = pd.concat([s, e], axis=1, keys=["SOFR", "EFFR"]).dropna()
    lvl_corr = both["SOFR"].corr(both["EFFR"])
    chg = both.diff().dropna()
    chg_corr = chg["SOFR"].corr(chg["EFFR"])
    spread = (both["SOFR"] - both["EFFR"])
    print("\n[2] SIMILARITY ON OVERLAP "
          f"({both.index.min().date()} -> {both.index.max().date()}, {len(both)} days)")
    print(f"  level correlation        = {lvl_corr:+.4f}")
    print(f"  daily-change correlation = {chg_corr:+.4f}")
    print(f"  SOFR-EFFR spread: mean {spread.mean()*100:+.1f} bps, "
          f"std {spread.std()*100:.1f} bps, "
          f"max |{spread.abs().max()*100:.0f}| bps")

    # --- 3. redundancy: regress SOFR on EFFR -------------------------------
    x = both["EFFR"].to_numpy()
    y = both["SOFR"].to_numpy()
    A = np.vstack([x, np.ones_like(x)]).T
    beta, *_ = np.linalg.lstsq(A, y, rcond=None)
    resid = y - A @ beta
    ss_res = float(np.sum(resid ** 2))
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot else float("nan")
    print("\n[3] REDUNDANCY  (SOFR ~ a*EFFR + b)")
    print(f"  slope a = {beta[0]:.3f},  intercept b = {beta[1]*100:+.1f} bps")
    print(f"  R^2 = {r2:.4f},  residual std = {resid.std()*100:.1f} bps")

    print("\n" + "=" * 72)
    print("HOW TO DECIDE")
    print("  If level & change corr are both high (>~0.95) and R^2 is high with a")
    print("  small residual, SOFR is ~redundant with EFFR you already carry ->")
    print("  DROP SOFR, refit PCA + regimes on the full 1995+ panel (no imputation).")
    print("  If SOFR carries a distinct funding-stress signal (corr lower, residual")
    print("  spikes in 2019 repo / 2020), prefer SPLICING EFFR<-2018 + SOFR>=2018")
    print("  into one continuous rate rather than dropping it.")
    print("=" * 72)


if __name__ == "__main__":
    main()
