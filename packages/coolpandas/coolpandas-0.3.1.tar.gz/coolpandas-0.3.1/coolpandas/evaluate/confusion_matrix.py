"""Confusion matrix functions."""
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

from coolpandas.plot import mapplot


def plot_confusion_matrix(cm: np.ndarray) -> None:
    """Plot a confusion matrix.

    Args:
        cm (np.ndarray): Confusion matrix to plot.
    """
    fig = mapplot(cm, title="Confusion matrix", width=400, height=400)
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=[1, 3, 5, 7, 9, 11],
            ticktext=["One", "Three", "Five", "Seven", "Nine", "Eleven"],
        )
    )
    ticks: list[int] = [i for i in range(len(cm))]
    fig.update_layout(
        xaxis_title="Predicted label",
        yaxis_title="True Label",
        xaxis=dict(tickmode="array", tickvals=ticks, ticktext=ticks),
        yaxis=dict(tickmode="array", tickvals=ticks, ticktext=ticks),
    )
    fig.show()


def get_confusion_matrix(
    y_true: pd.Series | np.ndarray | list,
    y_pred: pd.Series | np.ndarray | list,
    normalize: str | None = None,
    plot: bool = True,
) -> np.ndarray:
    """Create a confusion matrix.
    Args:
        y_true (pd.Series): True labels.
        y_pred (pd.Series): Predicted labels.
        normalize (str, optional): Normalize the confusion matrix.
        Defaults to None.
        plot (bool, optional): Plot the confusion matrix. Defaults to True.

    Returns:
        np.ndarray: Confusion matrix.
    """
    cm: np.ndarray = confusion_matrix(y_true, y_pred, normalize=normalize)
    if plot:
        plot_confusion_matrix(cm)
    return cm
