"""
src/build_panel.py

Builds the processed data panels from raw/ cache files.

Produces two output files in processed/:
    - asset_returns.parquet    : daily log returns per asset, aligned on business days
    - macro_panel.parquet      : macro variables (rates, spreads, vol) aligned daily

Both are indexed by pd.DatetimeIndex (tz-naive business days) and can be joined
on their index for downstream analysis.

Run from project root:
    python -m src.build_panel
"""

import numpy as np
import pandas as pd
from pathlib import Path

from src.data_io import load_config, RAW_DIR, PROCESSED_DIR


# -----------------------------------------------------------------------------
# Config-driven business-day index
# -----------------------------------------------------------------------------
def business_day_index(cfg: dict) -> pd.DatetimeIndex:
    """Return a business-day (Mon-Fri) index spanning the configured range."""
    start = cfg["dates"]["panel_start"]
    end = cfg["dates"]["panel_end"] or pd.Timestamp.today().normalize()
    return pd.bdate_range(start=start, end=end, freq="B")


# -----------------------------------------------------------------------------
# Asset side — one column per ticker, containing daily log returns
# -----------------------------------------------------------------------------
def build_asset_returns(cfg: dict, bday_index: pd.DatetimeIndex) -> pd.DataFrame:
    """
    For every asset in every group, load its cached OHLCV, extract Close,
    compute daily log returns, align to the business-day index.

    Pre-inception days are NaN (no fabrication). Missing data (holidays,
    trading halts) also remains NaN — we do NOT forward-fill returns.
    """
    # Collect (group, ticker) pairs across all three groups
    ticker_list = []
    for group_name, group in cfg["assets"].items():
        for entry in group:
            ticker_list.append((group_name, entry["ticker"]))

    # Deduplicate while preserving group tag (some tickers may appear in multiple groups)
    seen = set()
    unique_tickers = []
    for grp, tkr in ticker_list:
        if tkr not in seen:
            unique_tickers.append(tkr)
            seen.add(tkr)

    frames = {}
    for ticker in unique_tickers:
        path = RAW_DIR / "yfinance" / f"{ticker}.parquet"
        df = pd.read_parquet(path)
        if "Close" not in df.columns:
            raise ValueError(f"{ticker} raw file has no 'Close' column")
        close = df["Close"].astype(float)
        # Log returns: ln(P_t / P_{t-1})
        log_ret = np.log(close / close.shift(1))
        frames[ticker] = log_ret

    returns = pd.DataFrame(frames)
    # Align to canonical business-day index
    returns = returns.reindex(bday_index)
    returns.index.name = "date"
    return returns


# -----------------------------------------------------------------------------
# Macro side — one column per FRED series, forward-filled to daily
# -----------------------------------------------------------------------------
def build_macro_panel(cfg: dict, bday_index: pd.DatetimeIndex) -> pd.DataFrame:
    """
    For every FRED series, load its cached values, align to the business-day index,
    forward-fill within-series to handle frequency mismatch (M2 is monthly, most
    others daily) and holiday gaps.

    IMPORTANT: forward-fill is applied AFTER reindexing, so we never fill dates
    that precede the series' first observation.
    """
    frames = {}
    for entry in cfg["fred_series"]:
        sid = entry["id"]
        path = RAW_DIR / "fred" / f"{sid}.parquet"
        df = pd.read_parquet(path)
        # cached_fetch normalizes Series to single-column DataFrame with _series_value
        if "_series_value" in df.columns:
            s = df["_series_value"]
        elif sid in df.columns:
            s = df[sid]
        else:
            s = df.iloc[:, 0]
        s = s.astype(float)
        s.index = pd.to_datetime(s.index)
        frames[sid] = s

    macro = pd.DataFrame(frames)
    # Align to business-day index, then forward-fill within each column.
    # ffill respects each column's own first valid observation — it does not
    # bleed values backwards across the beginning of the series.
    macro = macro.reindex(bday_index).ffill()
    macro.index.name = "date"
    return macro


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> None:
    cfg = load_config()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    bday = business_day_index(cfg)
    print(f"Business-day index: {bday.min().date()} → {bday.max().date()} ({len(bday)} days)")

    print("\nBuilding asset returns panel...")
    returns = build_asset_returns(cfg, bday)
    returns_path = PROCESSED_DIR / "asset_returns.parquet"
    returns.to_parquet(returns_path)
    print(f"  shape: {returns.shape}  →  {returns_path.relative_to(RAW_DIR.parent)}")

    print("\nBuilding macro panel...")
    macro = build_macro_panel(cfg, bday)
    macro_path = PROCESSED_DIR / "macro_panel.parquet"
    macro.to_parquet(macro_path)
    print(f"  shape: {macro.shape}  →  {macro_path.relative_to(RAW_DIR.parent)}")

    # Coverage report — a quick diagnostic printed to console
    print("\n=== Asset coverage (non-NaN return count per ticker) ===")
    coverage = returns.count().sort_values()
    print(coverage.to_string())

    print("\n=== Macro coverage (non-NaN observation count per series) ===")
    macro_cov = macro.count().sort_values()
    print(macro_cov.to_string())

    print("\nDone.")


if __name__ == "__main__":
    main()