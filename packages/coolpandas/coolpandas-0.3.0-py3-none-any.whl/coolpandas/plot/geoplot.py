"""Geo plot module."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .style import custom_template, format_title


def geoplot(
    data_frame: pd.DataFrame,
    lat: str,
    lon: str,
    title: str,
    subtitle: str = None,
    **kwargs,
) -> go.Figure:
    """Create a map plot based on latitude and longitude of DataFrame passed columns.

    Args:
        data_frame (pd.DataFrame): DataFrame to plot.
        lat (str): Column to use as latitude.
        lon (str): Column to use as longitude.
        title (str): Title of the plot.
        subtitle (str, optional): Subtitle of the plot. Defaults to None.
        **kwargs: Keyword arguments to pass to plotly.express.scatter_geo.

    Returns:
        go.Figure: Bar plot figure.
    """
    fig = px.scatter_geo(
        data_frame,
        lat=lat,
        lon=lon,
        title=format_title(title, subtitle=subtitle),
        template=custom_template,
        projection="natural earth",
        width=800,
        height=400,
        **kwargs,
    )
    return fig
