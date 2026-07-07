"""
src/data_io.py

Reproducibility utilities: a cache-first data fetcher.

Every API call in this project routes through cached_fetch(). If a cache file
exists for the requested key, it is loaded from disk. Otherwise, the provided
fetch function is called, its result is saved to disk, and then returned.

The raw/ folder is treated as write-once. Do not edit cache files by hand.
If the underlying data needs to be re-pulled, delete the cache file and
re-run the download script.
"""

from pathlib import Path
import time
import pandas as pd
import yaml


# -----------------------------------------------------------------------------
# Project paths — derived from this file's location, so they work regardless
# of where the script is run from.
# -----------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "raw"
PROCESSED_DIR = PROJECT_ROOT / "processed"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
CONFIG_PATH = PROJECT_ROOT / "config" / "config.yaml"


def load_config() -> dict:
    """Read config/config.yaml and return as a dict."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)


def cached_fetch(
    source: str,
    key: str,
    fetch_fn,
    force_refresh: bool = False,
) -> pd.DataFrame | pd.Series:
    """
    Cache-first fetcher.

    Parameters
    ----------
    source : str
        Subfolder under raw/ where this kind of data lives, e.g. 'yfinance', 'fred'.
    key : str
        A filename-safe identifier for this specific request, e.g. 'SPY' or 'DGS10'.
    fetch_fn : callable
        A zero-argument function that, when called, performs the actual API call
        and returns a pandas DataFrame or Series.
    force_refresh : bool, default False
        If True, ignore any existing cache and re-fetch.

    Returns
    -------
    pd.DataFrame or pd.Series
        The cached or freshly fetched data.

    Notes
    -----
    - Cache files are written as Parquet (fast, typed, compact).
    - Series are converted to single-column DataFrames before saving, then
      converted back on load if originally a Series. This keeps Parquet happy.
    """
    cache_dir = RAW_DIR / source
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{key}.parquet"

    if cache_path.exists() and not force_refresh:
        # Cache hit — load and return without touching the API.
        df = pd.read_parquet(cache_path)
        # If we stored a Series-as-DataFrame, restore it.
        if df.shape[1] == 1 and df.columns[0] == "_series_value":
            return df["_series_value"].rename(key)
        return df

  # Cache miss (or forced refresh) — call the fetch function with retries.
    print(f"[fetch] {source}/{key} — calling API...")
    max_attempts = 4
    base_delay = 2.0  # seconds; doubled each retry
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            data = fetch_fn()
            break
        except Exception as e:
            last_error = e
            if attempt == max_attempts:
                print(f"[error] {source}/{key} failed after {max_attempts} attempts: {e}")
                raise
            delay = base_delay * (2 ** (attempt - 1))
            print(f"[retry] {source}/{key} attempt {attempt}/{max_attempts} failed ({type(e).__name__}); retrying in {delay:.1f}s...")
            time.sleep(delay)

    # Normalize to DataFrame for Parquet storage.
    if isinstance(data, pd.Series):
        to_save = data.to_frame(name="_series_value")
    elif isinstance(data, pd.DataFrame):
        to_save = data
    else:
        raise TypeError(
            f"fetch_fn for {source}/{key} returned {type(data).__name__}, "
            "expected pandas DataFrame or Series."
        )

    to_save.to_parquet(cache_path)
    print(f"[cache] saved {cache_path.relative_to(PROJECT_ROOT)}")
    return data


def cache_exists(source: str, key: str) -> bool:
    """Check whether a cache file exists for the given source/key."""
    return (RAW_DIR / source / f"{key}.parquet").exists()