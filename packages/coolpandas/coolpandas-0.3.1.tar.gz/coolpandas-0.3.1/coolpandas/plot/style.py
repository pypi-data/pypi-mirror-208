"""Style functions for CoolPandas plots."""
import plotly.express as px
import plotly.graph_objects as go

custom_template = {
    "layout": go.Layout(
        font={
            "family": "Nunito",
            "size": 12,
            "color": "#707070",
        },
        title={
            "font": {
                "family": "Lato",
                "size": 18,
                "color": "#1f1f1f",
            },
            "xref": "paper",
            "yref": "paper",
            "xanchor": "left",
            "x": 0,
        },
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        colorway=px.colors.qualitative.G10,
    )
}


def format_title(title: str, subtitle: str = None, subtitle_font_size: int = 14) -> str:
    """Format title and subtitle for plotly figures.

    Args:
        title (str): Title of the plot.
        subtitle (str, optional): Subtitle of the plot. Defaults to None.
        subtitle_font_size (int, optional): Font size of the subtitle. Defaults to 14.

    Returns:
        str: Formatted title.
    """
    title = f"<b>{title}</b>"
    if not subtitle:
        return title
    subtitle = f'<span style="font-size: {subtitle_font_size}px;">{subtitle}</span>'
    return f"{title}<br>{subtitle}"
