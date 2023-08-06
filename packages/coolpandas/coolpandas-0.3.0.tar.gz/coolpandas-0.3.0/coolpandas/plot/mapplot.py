"""Correlation map function."""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .style import custom_template, format_title


def mapplot(
    matrix: pd.DataFrame,
    title: str,
    subtitle: str = None,
    width: int = 1000,
    height: int = 1000,
    **kwargs,
) -> go.Figure:
    """Create a correlation map.

    Args:
        matrix (pd.DataFrame): Correlation matrix to plot.
        title (str): Title of the plot.
        subtitle (str, optional): Subtitle of the plot. Defaults to None.
        width (int, optional): Width of the plot. Defaults to 1000.
        height (int, optional): Height of the plot. Defaults to 1000.
        **kwargs: Keyword arguments to pass to plotly.express.imshow.

    Returns:
        go.Figure: Correlation map figure.
    """
    fig = px.imshow(
        matrix,
        text_auto=True,
        zmin=-1,
        zmax=1,
        title=format_title(title, subtitle=subtitle),
        template=custom_template,
        width=width,
        height=height,
        **kwargs,
    )
    return fig
