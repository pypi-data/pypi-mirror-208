"""Get a DataFrame column distribution overview."""
import pandas as pd

from coolpandas.plot import distplot


def plot_distribution(
    summary: pd.DataFrame,
    groupby_column: str,
    nbins: int = 100,
    title: str = "",
    subtitle: str = "",
    **kwargs,
) -> None:
    """Plot a feature distribution.

    Args:
        data_frame (pd.DataFrame): DataFrame to get distribution overview.
        groupby_column (str): Column to group by.
        nbins (int, optional): Number of bins. Defaults to 10.
        title (str, optional): Title of the plot. Defaults to "".
        subtitle (str, optional): Subtitle of the plot. Defaults to "".
        **kwargs: Keyword arguments to pass to distplot.
    """
    column: str = summary.columns[0]
    if not title:
        title = f"{column} distribution"
    if not subtitle:
        subtitle = f"Distribution for {summary.columns[0]} in DataFrame."
    if not kwargs.get("color"):
        kwargs["text_auto"] = True
    fig = distplot(
        summary,
        x_axis=groupby_column,
        y_axis=None,
        title=title,
        labels={
            "count": "Count",
        },
        subtitle=subtitle,
        histnorm="percent",
        nbins=nbins,
        **kwargs,
    )
    fig.update_yaxes(tickformat=".3")
    fig.update_layout(
        yaxis={"ticksuffix": "%"},
        yaxis_title="Percentage",
        barmode="overlay",
    )
    if kwargs.get("color"):
        fig.update_traces(opacity=0.75)
    fig.show()


def distribution_summaries(
    data_frame: pd.DataFrame,
    groupby_column: str,
    data_type: str,
    dependant_value: str = "",
) -> pd.DataFrame:
    if data_type == "categorical":
        summary: pd.DataFrame = (
            data_frame.groupby(groupby_column)
            .size()
            .to_frame()
            .reset_index()
            .rename(columns={0: "count"})
        )
        summary["percentage"] = round(
            summary["count"] / summary["count"].sum() * 100, 2
        )
    elif data_type == "numerical":
        summary = data_frame[groupby_column].describe().to_frame()
    if dependant_value:
        column_name: str = summary.columns[0]
        summary.rename(
            columns={column_name: f"{column_name}_{dependant_value}"}, inplace=True
        )
    return summary


def get_groupby_distribution(
    data_frame: pd.DataFrame,
    groupby_column: str,
    data_type: str,
    plot: bool = True,
    **kwargs,
) -> pd.DataFrame | list[pd.DataFrame]:
    """Get the distribution overview of a DataFrame ordinal column grouped by size.

    Args:
        data_frame (pd.DataFrame): DataFrame to get distribution overview.
        groupby_column (str): Column to group by.
        data_type (str): Data type to get distribution overview.
        plot (bool, optional): Plot the distribution. Defaults to True.
        Defaults to "".
        **kwargs: Keyword arguments to pass to plot_distribution.

    Returns:
        pd.DataFrame | list[pd.DataFrame]: Distribution overviews.
    """
    if plot and data_type == "categorical":
        kwargs["nbins"] = data_frame[groupby_column].nunique()
    elif plot and data_type == "numerical":
        kwargs["marginal"] = "box"
        if not kwargs.get("nbins"):
            kwargs["nbins"] = 31
    if plot and not kwargs.get("title"):
        kwargs["title"] = f"{groupby_column} distribution"
    if plot:
        plot_distribution(
            data_frame,
            groupby_column,
            **kwargs,
        )
    summaries: list[pd.DataFrame] = []
    dependant_column: str = kwargs.get("color")
    if not dependant_column:
        summaries.append(distribution_summaries(data_frame, groupby_column, data_type))
    else:
        summaries = [
            distribution_summaries(
                data_frame[data_frame[dependant_column] == i],
                groupby_column,
                data_type,
                str(i),
            )
            for i in data_frame[dependant_column].unique()
        ]
    return summaries[0] if not dependant_column else summaries
