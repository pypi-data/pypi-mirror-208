"""DataFrames cleaning module."""
import pandas as pd


def duplicated_rows(
    data_frame: pd.DataFrame, display_summary: bool = True, drop: bool = False
) -> pd.DataFrame:
    """Get duplicated rows in a DataFrame and drop them if specified.
    Args:
        data_frame (pd.DataFrame): DataFrame to get duplicated rows.
        display_summary (bool, optional): Whether to display summary. Defaults to True.
        drop (bool, optional): Whether to drop duplicated rows. Defaults to True.
    Returns:
        pd.DataFrame: Duplicated rows.
    """
    duplicated_data_frame: pd.DataFrame = data_frame[data_frame.duplicated(keep=False)]
    if display_summary:
        print(f"Number of duplicated rows: {duplicated_data_frame.shape[0]}")
    if drop:
        data_frame.drop_duplicates(inplace=True)
    if display_summary and drop:
        print("DataFrame shape after dropping duplicated rows:")
        print(data_frame.shape)
    return duplicated_data_frame


def duplicated_columns(
    data_frame: pd.DataFrame, display_summary: bool = True, drop: bool = False
) -> pd.DataFrame:
    """Get duplicated columns in a DataFrame and drop them if specified.
    Args:
        data_frame (pd.DataFrame): DataFrame to get duplicated columns.
        display_summary (bool, optional): Whether to display summary. Defaults to True.
        drop (bool, optional): Whether to drop duplicated columns. Defaults to True.
    Returns:
        pd.DataFrame: Duplicated columns.
    """
    # uniques, indexes = np.unique(data_frame, return_index=True, axis=1)
    # return pd.DataFrame(uniq, index=data_frame.index, columns=data_frame.columns[~indexes])
    duplicates: pd.Series = data_frame.apply(lambda x: x.duplicated(), axis=1).all()
    duplicated_data_frame: pd.DataFrame = data_frame[duplicates[duplicates].index]
    if display_summary:
        print(f"Number of duplicated columns: {duplicated_data_frame.shape[1]}")
    if drop:
        data_frame.drop(columns=duplicated_data_frame.columns, inplace=True)
    if display_summary and drop:
        print("DataFrame shape after dropping duplicated columns:")
        print(data_frame.shape)
    return duplicated_data_frame
