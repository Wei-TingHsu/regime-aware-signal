"""
src/build_panel.py

Builds the processed data panels from raw/ cache files.

Produces two output files in processed/:
    - asset_returns.parquet    : daily log returns per asset, aligned on business days
    - macro_panel.parquet      : macro variables (rates, spreads, vol) aligned daily

Both are indexed by pd.DatetimeIndex (tz-naive NYSE TRADING SESSIONS) and can be
joined on their index for downstream analysis.

CALENDAR NOTE (changed 2026-08-18): the index is the NYSE session calendar, NOT
pd.bdate_range. bdate_range is Mon-Fri INCLUDING market holidays, which put 194
rows into the 2006+ panel that carry no asset returns at all -- yet still entered
the PCA and the GMM, because those are macro-only. The macro side was
forward-filled onto them, so the great majority were exact duplicates of the
preceding row: manufactured data, which inflates apparent regime persistence.
The trade is not free -- a minority of those rows (Good Fridays, when the Fed is
open and the NYSE is not; plus unscheduled closures such as Hurricane Sandy 2012)
carry genuinely new macro values, at most 46 per series. Dropping them is still
correct: a macro state with no trading session is not a state any engine can act
on, and it contributes zero return information.

Run from project root:
    python -m src.build_panel
"""

import numpy as np
import pandas as pd
from pathlib import Path

from src.data_io import load_config, RAW_DIR, PROCESSED_DIR
from src.market_calendar import trading_days


# -----------------------------------------------------------------------------
# Config-driven NYSE session index
# -----------------------------------------------------------------------------
def trading_day_index(cfg: dict) -> pd.DatetimeIndex:
    """Return the NYSE trading sessions spanning the configured range.

    Weekends AND market holidays are excluded. See the CALENDAR NOTE in the
    module docstring for why this is not pd.bdate_range.
    """
    start = cfg["dates"]["panel_start"]
    end = cfg["dates"]["panel_end"] or pd.Timestamp.today().normalize()
    return trading_days(start, end)


# -----------------------------------------------------------------------------
# Asset side — one column per ticker, containing daily log returns
# -----------------------------------------------------------------------------
def build_asset_returns(cfg: dict, session_index: pd.DatetimeIndex) -> pd.DataFrame:
    """
    For every asset in every group, load its cached OHLCV, extract Close,
    compute daily log returns, align to the NYSE session index.

    Pre-inception days are NaN (no fabrication). Missing data (trading halts,
    vendor gaps) also remains NaN — we do NOT forward-fill returns. Market
    holidays are no longer in the index at all, so a NaN row now means genuinely
    missing data rather than a closed market: the two are distinguishable.
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
    # Align to canonical NYSE session index
    returns = returns.reindex(session_index)
    returns.index.name = "date"
    return returns


# -----------------------------------------------------------------------------
# Macro side — one column per FRED series, forward-filled to daily
# -----------------------------------------------------------------------------
def build_macro_panel(cfg: dict, session_index: pd.DatetimeIndex) -> pd.DataFrame:
    """
    For every FRED series, load its cached values, align to the NYSE session index,
    forward-fill within-series to handle frequency mismatch (M2 is monthly, most
    others daily) and gaps where a series does not publish on a trading day
    (e.g. Columbus Day and Veterans Day: bond market shut, NYSE open).

    This ffill is legitimate frequency alignment -- there IS a session to attribute
    the state to. It is NOT the same as the pre-2026-08-18 behaviour of filling
    macro values onto market holidays, where no session existed at all.

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
    # Align to session index, then forward-fill within each column.
    # ffill respects each column's own first valid observation — it does not
    # bleed values backwards across the beginning of the series.
    macro = macro.reindex(session_index).ffill()
    macro.index.name = "date"
    return macro


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> None:
    cfg = load_config()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    sessions = trading_day_index(cfg)
    print(f"NYSE session index: {sessions.min().date()} → {sessions.max().date()} "
          f"({len(sessions)} sessions)")

    print("\nBuilding asset returns panel...")
    returns = build_asset_returns(cfg, sessions)
    returns_path = PROCESSED_DIR / "asset_returns.parquet"
    returns.to_parquet(returns_path)
    print(f"  shape: {returns.shape}  →  {returns_path.relative_to(RAW_DIR.parent)}")

    print("\nBuilding macro panel...")
    macro = build_macro_panel(cfg, sessions)
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