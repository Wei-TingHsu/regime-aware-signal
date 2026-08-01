"""
src/market_calendar.py

Utilities for aligning arbitrary timestamps (news events, off-hours prices,
24/7 asset feeds) to the US business day they should be attributed to.

Uses NYSE as the reference calendar since the project's asset universe
is US-listed equities and ETFs. All timestamps are internally normalized
to America/New_York timezone; naive timestamps are assumed to be in ET.

Core rule
---------
An event with timestamp T is attributed to the next NYSE trading day if:
    - T falls on a weekend, OR
    - T falls on a NYSE holiday, OR
    - T falls after the NYSE close (16:00 ET) on a trading day, OR
    - T falls between the close of one trading day and the next
      trading day's open.
Otherwise T is attributed to its own calendar date.

This matches CME's own bucketing rule for 24/7 gold futures: any trade
from Friday evening through Sunday evening carries the following business
day's trade date.
"""

import pandas as pd
import pandas_market_calendars as mcal
from functools import lru_cache


# =============================================================================
# NYSE calendar — the reference for all bucketing
# =============================================================================
NYSE = mcal.get_calendar("NYSE")

# Regular session hours (Eastern Time)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0

TZ_ET = "America/New_York"


# =============================================================================
# Cached schedule lookup
# =============================================================================
@lru_cache(maxsize=32)
def _schedule(start_year: int, end_year: int) -> pd.DataFrame:
    """
    Return the NYSE trading schedule for a range of years, cached.

    Includes both regular sessions and early-close days (e.g. day after
    Thanksgiving, Christmas Eve). Cached so repeated calls in a session
    don't rebuild the whole schedule.
    """
    return NYSE.schedule(
        start_date=f"{start_year}-01-01",
        end_date=f"{end_year}-12-31",
    )


def _relevant_schedule(ts: pd.Timestamp) -> pd.DataFrame:
    """Fetch the schedule spanning ~2 years around the given timestamp."""
    year = ts.year
    return _schedule(year - 1, year + 1)


# =============================================================================
# Timezone normalization
# =============================================================================
def _to_et(ts) -> pd.Timestamp:
    """
    Normalize any input to a tz-aware pd.Timestamp in America/New_York.

    - Naive strings/timestamps are assumed to be ET.
    - tz-aware inputs are converted to ET.
    """
    ts = pd.Timestamp(ts)
    if ts.tz is None:
        ts = ts.tz_localize(TZ_ET)
    else:
        ts = ts.tz_convert(TZ_ET)
    return ts


# =============================================================================
# Public API
# =============================================================================
def to_market_day(ts) -> pd.Timestamp:
    """
    Return the NYSE trading date this timestamp should be attributed to.

    Parameters
    ----------
    ts : str, datetime, or pd.Timestamp
        The event/observation timestamp. Naive inputs assumed ET.

    Returns
    -------
    pd.Timestamp
        A tz-naive date (time set to 00:00) representing the assigned
        trading day.

    Rules
    -----
    - Weekend or holiday event -> next trading day
    - Weekday event at or after 16:00 ET -> next trading day
    - Weekday event before 16:00 ET on a trading day -> same day
    """
    ts_et = _to_et(ts)
    schedule = _relevant_schedule(ts_et)

    # Get trading days as tz-naive dates for comparison
    trading_dates = pd.DatetimeIndex(schedule.index).tz_localize(None).normalize()
    event_date = ts_et.tz_localize(None).normalize()

  # Determine the close time to compare against: the NYSE close for that date,
    # OR the standard 16:00 if event_date is not itself a trading day
    if event_date in trading_dates:
        # Event is on a trading day. Get that day's actual close from schedule.
        # Match by tz-naive date, since schedule.index is tz-aware UTC.
        schedule_dates_naive = pd.DatetimeIndex(schedule.index).tz_localize(None).normalize()
        matching_rows = schedule[schedule_dates_naive == event_date]
        if len(matching_rows) > 0:
            close_time_et = matching_rows["market_close"].iloc[0].tz_convert(TZ_ET)
            if ts_et < close_time_et:
                return event_date  # same-day attribution
        # else fall through to "find next trading day"

    # Event is off-hours, weekend, holiday, or after close -> find next trading day
    future_days = trading_dates[trading_dates > event_date]
    if len(future_days) == 0:
        raise ValueError(
            f"No future trading day found in schedule for {ts_et}. "
            "Extend the calendar range."
        )
    return future_days[0]


def is_market_open(ts) -> bool:
    """
    Return True if the timestamp is inside the regular NYSE session
    (typically 9:30 AM - 4:00 PM ET on a trading day, adjusted for
    early-close days).

    Parameters
    ----------
    ts : str, datetime, or pd.Timestamp
        Naive inputs assumed ET.

    Returns
    -------
    bool
    """
    ts_et = _to_et(ts)
    schedule = _relevant_schedule(ts_et)

    event_date = ts_et.tz_localize(None).normalize()
    trading_dates = pd.DatetimeIndex(schedule.index).tz_localize(None).normalize()
    if event_date not in trading_dates:
        return False

# Find that day's open/close in the schedule
    schedule_dates_naive = pd.DatetimeIndex(schedule.index).tz_localize(None).normalize()
    matching_rows = schedule[schedule_dates_naive == event_date]
    if len(matching_rows) == 0:
        return False
    open_time = matching_rows["market_open"].iloc[0].tz_convert(TZ_ET)
    close_time = matching_rows["market_close"].iloc[0].tz_convert(TZ_ET)
    return open_time <= ts_et < close_time