import re
import time
import traceback
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, Union

from novalabs.utils.constant import SECONDS_PER_UNIT


def convert_candle_to_timedelta(candle: str) -> timedelta:
    multi = int(float(re.findall(r"\d+", candle)[0]))
    if "m" in candle:
        candle_duration = timedelta(minutes=multi)
    elif "h" in candle:
        candle_duration = timedelta(hours=multi)
    elif "d" in candle:
        candle_duration = timedelta(days=multi)
    else:
        raise ValueError(
            "Please enter a valid candle value. Must contain the letter m, h or d."
        )

    return candle_duration


def convert_max_holding_to_candle_nb(candle: str, max_holding: timedelta) -> int:
    """
    Return:
        the number maximum of candle we can hold a position
    """

    candle_duration = convert_candle_to_timedelta(candle=candle)

    return int(max_holding.total_seconds() / candle_duration.total_seconds())


def get_timedelta_unit(interval: str) -> timedelta:
    """
    Returns a timedelta object based on the interval string.

    Args:
        interval (str): A string containing the interval value and unit (e.g. "10m", "2h", "3d").

    Returns:
        timedelta: A timedelta object representing the duration of the interval.

    Raises:
        ValueError: If the interval string is not in the correct format.

    """
    # Use regex to extract the numeric multiplier from the interval string.
    match = re.search(r"^(\d+)", interval)
    if not match:
        raise ValueError("Invalid interval format: {}".format(interval))
    multiplier = int(match.group())

    # Determine the timedelta unit based on the interval string.
    unit = interval[-1]
    if unit == "m":
        return timedelta(minutes=multiplier)
    elif unit == "h":
        return timedelta(hours=multiplier)
    elif unit == "d":
        return timedelta(days=multiplier)
    else:
        raise ValueError("Invalid interval unit: {}".format(unit))


def milliseconds_to_interval(interval_ms: int) -> str:
    if interval_ms < 3600000:
        return str(int(60 / (3600000 / interval_ms))) + "T"
    elif interval_ms < 86400000:
        return str(int(24 / (86400000 / interval_ms))) + "H"
    else:
        return str(int(interval_ms / 86400000)) + "D"


def interval_to_minutes_str(interval: str) -> str:
    """Convert a Binance interval string to milliseconds
    Args:
        interval: interval string, e.g.: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    Returns:
         int value of interval in milliseconds
         None if interval prefix is not a decimal integer
         None if interval suffix is not one of m, h, d, w
    """
    if "m" in interval:
        interval += "in"

    if "h" in interval:
        interval += "our"

    if "d" in interval:
        interval += "ay"

    if "w" in interval:
        interval += "eek"

    return interval


def interval_to_minutes(interval: str) -> Optional[int]:
    """Convert a Binance interval string to milliseconds
    Args:
        interval: interval string, e.g.: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    Returns:
         int value of interval in milliseconds
         None if interval prefix is not a decimal integer
         None if interval suffix is not one of m, h, d, w
    """
    minutes_per_unit: Dict[str, int] = {
        "m": 1,
        "h": 60,
        "d": 24 * 60,
        "w": 7 * 24 * 60,
    }
    try:
        return int(interval[:-1]) * minutes_per_unit[interval[-1]]
    except (ValueError, KeyError):
        return None


def interval_to_milliseconds(interval: str) -> int:
    """
    Converts a Binance interval string to the corresponding number of milliseconds.
    The interval string should have the format '<number><unit>', where <number> is a positive integer and <unit> is one
    of the following characters: 'm' (minutes), 'h' (hours), 'd' (days), or 'w' (weeks).
    Returns:
        - The number of milliseconds corresponding to the input interval.
        - None if the input string is not in the correct format or the <number> part is zero.
    """
    try:
        number = int(interval[:-1])
        unit = interval[-1]
    except ValueError:
        return 0

    if unit not in SECONDS_PER_UNIT:
        return 0

    return number * SECONDS_PER_UNIT[unit] * 1000


def limit_to_start_date(interval: str, nb_candles: int) -> Optional[int]:
    """
    Computes the start time timestamp in milliseconds for production data.
    The number of candles is determined with the "now" timestamp.
    Args:
        interval: interval string, e.g.: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
        nb_candles: number of candles needed.
    Returns:
        The start time timestamp in milliseconds, or None if the interval prefix is not a decimal integer
        or the interval suffix is not one of m, h, d, w.
    """
    interval_in_ms = interval_to_milliseconds(interval)
    if interval_in_ms is None:
        return None
    now_timestamp_ms = int(time.time() * 1000)
    start_timestamp_ms = now_timestamp_ms - (nb_candles + 1) * interval_in_ms
    return start_timestamp_ms


def is_opening_candle(interval: str, current_date: datetime) -> bool:
    """Determine whether the current candle is an opening candle given the interval and current date
    Args:
        interval: interval string, e.g.: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
        current_date: the current date and time
    Returns:
        True if the current candle is an opening candle, False otherwise
    """
    multi = int(float(re.findall(r"\d+", interval)[0]))
    unit = interval[-1]

    if multi == 1:
        if unit == "m":
            return current_date.second == 0
        elif unit == "h":
            return current_date.minute + current_date.second == 0
        elif unit == "d":
            return current_date.hour + current_date.minute + current_date.second == 0
    else:
        if unit == "m":
            return current_date.minute % multi + current_date.second == 0
        elif unit == "h":
            return (
                current_date.hour % multi + current_date.minute + current_date.second
                == 0
            )

    return False


def compute_time_difference(
    start_time: Optional[int], end_time: Optional[int], unit: str
) -> Optional[float]:
    """
    Compute the time difference between two timestamps in the specified unit.

    Args:
        start_time: Start time in timestamp milliseconds.
        end_time: End time in timestamp milliseconds.
        unit: The time unit to express the difference in. Can be 'second', 'minute', 'hour', or 'day'.

    Returns:
        The time difference between start_time and end_time in the specified unit, or None if either timestamp is None.
    """
    if start_time is None or end_time is None:
        return None
    try:
        difference_in_seconds = end_time // 1000 - start_time // 1000
        return difference_in_seconds / SECONDS_PER_UNIT[unit]
    except (ValueError, KeyError, ZeroDivisionError):
        return None


def interval_to_oanda_granularity(interval: str) -> str:
    """
    Convert an interval string to an Oanda granularity string.

    Args:
        interval: Interval string, e.g.: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w.

    Returns:
        The equivalent Oanda granularity string.
    """
    _number = interval[:-1]
    _letter = interval[-1].upper()

    return f"{_letter}{_number}" if _letter in ["M", "H"] else f"{_letter}"


def retry_requests(
    func: Callable[..., Any],
    retries: int = 10,
) -> Callable[..., Any]:
    """
    Decorator function to retry requests for a specified number of times
    Args:
        func: the function to be decorated
        retries: number of retries

    Returns:
        The decorated function
    """

    def retry_wrapper(*args: Any, **kwargs: Any) -> Optional[Any]:
        for _ in range(retries):
            try:
                response = func(*args, **kwargs)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                traceback.print_exc()
                print(f"Error: {e}")
                time.sleep(5)
        raise ConnectionError(f"Failed to retrieve data after {retries} attempts")

    return retry_wrapper


def format_precision(
    value: float, precision: int, tick: float, up: bool = True
) -> Union[int, float]:
    """
    Rounds a float value to a specified precision and tick size.

    Args:
        value: The value to be rounded.
        precision: The number of decimal places to round to.
        tick: The tick size, i.e. the smallest price increment.
        up: A flag indicating whether to round up (True) or down (False) if the value is not already at a tick.

    Returns:
        The rounded value, with the same type as the input (int or float).
    """
    if precision == 0:
        return int(value)

    residue = round(value, precision) % tick

    if up:
        return round(value + tick - residue, precision)
    else:
        return round(value - residue, precision)
