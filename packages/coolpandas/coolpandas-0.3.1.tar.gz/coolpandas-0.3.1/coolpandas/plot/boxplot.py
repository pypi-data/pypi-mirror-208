"""Box plot module."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .style import custom_template, format_title


def boxplot(
    data_frame: pd.DataFrame,
    x_axis: str,
    y_axis: str,
    title: str,
    subtitle: str | None = None,
    **kwargs,
) -> go.Figure:
    """Create a box plot.

    Args:
        data_frame (pd.DataFrame): DataFrame to plot.
        x_axis (str): Column to use as x axis.
        y_axis (str): Column to use as y axis.
        title (str): Title of the plot.
        subtitle (str, optional): Subtitle of the plot. Defaults to None.
        **kwargs: Keyword arguments to pass to plotly.express.box.

    Returns:
        go.Figure: Box plot figure.
    """
    if "color" not in kwargs:
        kwargs["color"] = x_axis
    fig = px.box(
        data_frame,
        x=x_axis,
        y=y_axis,
        notched=True,
        title=format_title(title, subtitle=subtitle),
        template=custom_template,
        width=800,
        height=400,
        **kwargs,
    )
    if kwargs.get("color") == x_axis:
        fig.layout.update(showlegend=False)
    return fig
