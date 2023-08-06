"""Data shape of a DataFrame overview."""
import pandas as pd
from IPython.display import display


def get_shape(
    data_frame: pd.DataFrame, display_summary: bool = True
) -> dict[str, int | list[str]]:
    """Get a DataFrame shape overview.

    Args:
        data_frame (pd.DataFrame): DataFrame to get shape overview.

    Returns:
        dict[str, int | list[str]]: DataFrame shape summary.
    """
    summary: dict[str, int | list[str]] = {}
    summary["rows_number"], summary["columns_number"] = data_frame.shape
    summary["columns_name"] = data_frame.columns.tolist()
    summary["columns_type"] = data_frame.dtypes.tolist()
    if display_summary:
        display(data_frame.head())
        print(f"Number of rows: {summary.get('rows_number')}")
        print(f"Number of columns: {summary.get('columns_number')}")
        print(f"Columns name: {summary['columns_name']}")
        print(f"Columns type: {summary['columns_type']}")
    return summary
