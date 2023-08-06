"""Get a DataFrame columns summary."""
import pandas as pd
from IPython.display import display


def get_summary(data_frame: pd.DataFrame, display_summary: bool = True) -> pd.DataFrame:
    """Get a DataFrame summary.
    Args:
        data_frame (pd.DataFrame): DataFrame to get summary.
        display_summary (bool, optional): Whether to display summary. Defaults to True.

    Returns:
        pd.DataFrame: DataFrame summary.
    """
    summary: pd.DataFrame = data_frame.dtypes.to_frame().T
    summary.rename(index={0: "dtypes"}, inplace=True)
    summary = pd.concat([summary, data_frame.describe(include="all")])
    if display_summary:
        display(summary)
    return summary
