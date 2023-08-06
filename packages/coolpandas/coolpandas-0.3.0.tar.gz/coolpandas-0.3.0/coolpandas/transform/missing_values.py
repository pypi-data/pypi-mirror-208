"""Missing values transformation."""
import pandas as pd


def fill_missing_values(
    data_frame: pd.DataFrame, columns: list[str], value: any
) -> pd.DataFrame:
    """Fill missing values in columns of a DataFrame.

    Args:
        data_frame (pd.DataFrame): DataFrame to fill missing values in.
        columns (list[str]): List of columns to fill missing values in.
        value (any): Value to fill missing values with.

    Returns:
        pd.DataFrame: DataFrame with missing values filled.
    """
    data_frame[columns] = data_frame[columns].fillna(value)
    return data_frame
