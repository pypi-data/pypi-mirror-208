"""Outliers transformations."""
import pandas as pd


def iqr_outliers(
    data_frame: pd.DataFrame,
    column: str,
    threshold: float = 1.5,
    create_outlier_column: bool = False,
    lower_bound: float | None = None,
    upper_bound: float | None = None,
) -> pd.DataFrame:
    """Transform outliers using the interquartile range method. If the lower_bound and upper_bound are not provided, they will be calculated using the threshold.

    Args:
        data_frame (pd.DataFrame): DataFrame to get outliers from.
        column (str): Column to get outliers from.
        threshold (float, optional): Threshold to use. Defaults to 1.5.
        create_outlier_column (bool, optional): Whether to create a column with
        outliers. Defaults to False.
        lower_bound (float, optional): Lower bound to use. Defaults to None.
        upper_bound (float, optional): Upper bound to use. Defaults to None.

    Returns:
        pd.DataFrame: DataFrame with outliers.
    """
    if lower_bound is None or upper_bound is None:
        quartile_1: float = data_frame[column].quantile(0.25)
        quartile_3: float = data_frame[column].quantile(0.75)
        iqr: float = quartile_3 - quartile_1
    if lower_bound is None:
        lower_bound: float = quartile_1 - (threshold * iqr)
    if upper_bound is None:
        upper_bound: float = quartile_3 + (threshold * iqr)
    if create_outlier_column:
        data_frame[f"{column}_outlier"] = data_frame[column].apply(
            lambda x: 1 if x < lower_bound or x > upper_bound else 0
        )
    data_frame[column] = data_frame[column].apply(
        lambda x: lower_bound
        if x < lower_bound
        else x
        if x < upper_bound
        else upper_bound
    )
    return data_frame
