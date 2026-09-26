import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional


def plot_time_series(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str = "Time Series Plot",
    color_col: Optional[str] = None,
) -> go.Figure:
    """Generates a standard time series line chart using Plotly."""
    fig = px.line(df, x=x_col, y=y_col, color=color_col, title=title)
    fig.update_layout(template="plotly_white", hovermode="x unified")
    return fig


def plot_distribution(
    df: pd.DataFrame, col: str, title: str = "Distribution Plot"
) -> go.Figure:
    """Generates a histogram with marginal box plot for a numerical column."""
    fig = px.histogram(df, x=col, marginal="box", title=title)
    fig.update_layout(template="plotly_white")
    return fig


def plot_correlation_heatmap(
    df: pd.DataFrame, title: str = "Correlation Matrix"
) -> go.Figure:
    """Generates a heatmap for the correlation matrix of numerical columns."""
    corr = df.corr()
    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        title=title,
        color_continuous_scale="RdBu_r",
    )
    return fig
