"""value_counts function for pandas DataFrame."""
import pandas as pd

from coolpandas.plot import barplot


def plot_value_counts(summary: pd.DataFrame) -> None:
    """Plot a DataFrame column value counts overview.

    Args:
        data_frame (pd.DataFrame): DataFrame to get value counts overview.
        column (str): Column to get value counts.
    """
    column: str = summary.columns[0]
    fig = barplot(
        summary,
        x_axis=column,
        y_axis="percentage",
        title=f"{column} value counts",
        hover_data={
            "count": True,
        },
        labels={
            "count": "Count",
            "percentage": "Percentage",
        },
        subtitle=f"Value counts for {summary.columns[0]} in DataFrame.",
        text="count",
    )
    fig.update_layout(
        yaxis={"ticksuffix": "%", "range": [0, 100]},
        xaxis=dict(tickmode="array", tickvals=summary[column].values),
        showlegend=False,
    )
    fig.show()


def get_value_counts(
    data_frame: pd.DataFrame, column: str, plot: bool = True
) -> pd.DataFrame:
    """Get a DataFrame column value counts overview.

    Args:
        data_frame (pd.DataFrame): DataFrame to get value counts overview.
        column (str): Column to get value counts.

    Returns:
        pd.DataFrame: DataFrame value counts summary.
    """
    summary: pd.DataFrame = pd.DataFrame(data_frame[column].value_counts(dropna=False))
    summary.columns = ["count"]
    summary["percentage"] = round(
        data_frame[column].value_counts(dropna=False, normalize=True) * 100, 2
    )
    summary = summary.reset_index().rename(columns={"index": column})
    if plot:
        plot_value_counts(summary)
    return summary


def get_groupby_value_counts(
    data_frame: pd.DataFrame,
    groupby_column: str,
    plot: bool = True,
) -> pd.DataFrame:
    """Get the value counts overview of a DataFrame column grouped by size.

    Args:
        data_frame (pd.DataFrame): DataFrame to get value counts overview.
        groupby_column (str): Column to group by.

    Returns:
        pd.DataFrame: DataFrame value counts summary.
    """
    summary: pd.DataFrame = (
        data_frame.groupby(groupby_column)
        .size()
        .to_frame()
        .reset_index()
        .rename(columns={0: "count"})
    )
    summary["percentage"] = round(summary["count"] / summary["count"].sum() * 100, 2)
    if plot:
        plot_value_counts(summary)
    return summary
