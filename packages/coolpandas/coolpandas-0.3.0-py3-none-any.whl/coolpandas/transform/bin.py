"""Bin a list of values into a list of bins."""
import numpy as np
import pandas as pd


def to_bin(
    series: pd.Series | np.ndarray | list[float | int], step: float = 0.1
) -> pd.Series | np.ndarray | list[float | int]:
    """Bin a series, a numpy array or a list of floats or ints by step.

    Args:
        series (pd.Series | np.ndarray | list[float | int]): Series, numpy array or
        list of floats or ints to bin.
        step (float, optional): Step to bin. Defaults to 0.1.

    Returns:
        pd.Series | np.ndarray | list[float | int]: Binned series, numpy array or list
        of floats or ints.
    """
    binner: callable = lambda x: np.floor(x / step) * step
    return binner(series)
