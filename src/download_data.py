"""
src/download_data.py

Downloads every asset price and FRED macro series defined in config.yaml.
All downloads route through cached_fetch, so re-running this script is cheap
(cache hits) until you delete cache files or pass --force.

Run from project root:
    python -m src.download_data
    python -m src.download_data --force   # re-pull everything, ignoring cache
"""

import argparse
import os
from dotenv import load_dotenv
import pandas as pd
import yfinance as yf
from fredapi import Fred
from tqdm import tqdm

from src.data_io import load_config, cached_fetch


# Load .env so FRED_API_KEY is available
load_dotenv()


# -----------------------------------------------------------------------------
# yfinance
# -----------------------------------------------------------------------------
def download_yfinance_ticker(ticker: str, start: str, end: str | None) -> pd.DataFrame:
    """
    Fetch one ticker's full OHLCV history from Yahoo via yfinance.

    Returns a DataFrame indexed by date, with columns Open/High/Low/Close/Volume.
    Auto-adjusted prices (splits and dividends already incorporated).
    """
    df = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=True,
        progress=False,
        threads=False,
    )
    if df.empty:
        raise ValueError(f"yfinance returned empty data for {ticker}")
    # yfinance may return multi-level columns when only one ticker is fetched
    # (a recent API change). Flatten if so.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df.index = pd.to_datetime(df.index).tz_localize(None)
    return df


def download_all_yfinance(cfg: dict, force: bool) -> None:
    """Pull every unique ticker referenced anywhere in cfg['assets']."""
    start = cfg["dates"]["panel_start"]
    end = cfg["dates"]["panel_end"]  # may be None — yfinance treats that as today

    # Collect unique tickers across all asset groups
    tickers = set()
    for group_name, group_list in cfg["assets"].items():
        for entry in group_list:
            tickers.add(entry["ticker"])

    print(f"\n=== yfinance: {len(tickers)} unique tickers ===")
    for ticker in tqdm(sorted(tickers), desc="yfinance"):
        cached_fetch(
            source="yfinance",
            key=ticker,
            fetch_fn=lambda t=ticker: download_yfinance_ticker(t, start, end),
            force_refresh=force,
        )


# -----------------------------------------------------------------------------
# FRED
# -----------------------------------------------------------------------------
def download_fred_series(fred: Fred, series_id: str, start: str) -> pd.Series:
    """Fetch one FRED series from `start` to today."""
    s = fred.get_series(series_id, observation_start=start)
    if s.empty:
        raise ValueError(f"FRED returned empty data for {series_id}")
    s.index = pd.to_datetime(s.index)
    s.name = series_id
    return s


def download_all_fred(cfg: dict, force: bool) -> None:
    """Pull every FRED series in cfg['fred_series']."""
    api_key = os.getenv("FRED_API_KEY")
    if not api_key:
        raise RuntimeError(
            "FRED_API_KEY not found. Check that .env exists and contains the key."
        )
    fred = Fred(api_key=api_key)
    start = cfg["dates"]["panel_start"]

    print(f"\n=== FRED: {len(cfg['fred_series'])} series ===")
    for entry in tqdm(cfg["fred_series"], desc="FRED"):
        series_id = entry["id"]
        cached_fetch(
            source="fred",
            key=series_id,
            fetch_fn=lambda sid=series_id: download_fred_series(fred, sid, start),
            force_refresh=force,
        )


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(description="Download all configured data.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore cache and re-fetch everything.",
    )
    args = parser.parse_args()

    cfg = load_config()
    download_all_yfinance(cfg, force=args.force)
    download_all_fred(cfg, force=args.force)

    print("\nDone.")


if __name__ == "__main__":
    main()