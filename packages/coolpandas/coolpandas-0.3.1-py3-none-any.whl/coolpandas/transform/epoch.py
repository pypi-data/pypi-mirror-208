"""Date to epoch transformation."""
import pandas as pd
from pandas._libs.tslibs.timestamps import Timestamp


def timestamp_to_epoch(timestamp: Timestamp | pd.Series) -> int:
    """Convert a timestamp to a unix epoch timestamp.

    Args:
        timestamp (Timestamp | pd.Series): Timestamp or series of timestamps to convert.

    Returns:
        int: Unix epoch timestamp.
    """
    return (timestamp - pd.Timestamp("1970-01-01")) // pd.Timedelta("1s")
