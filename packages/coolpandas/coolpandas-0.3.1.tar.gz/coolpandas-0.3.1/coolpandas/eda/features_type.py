"""Get features type in a DataFrame."""
import numpy as np
import pandas as pd


def categorical_features(
    data_frame: pd.DataFrame, display_summary: bool = True
) -> list[str]:
    """Get categorical features in a DataFrame.
    Args:
        data_frame (pd.DataFrame): DataFrame to get categorical features.
        display_summary (bool, optional): Whether to display summary. Defaults to True.

    Returns:
        list[str]: Categorical features.
    """
    features: list[str] = data_frame.select_dtypes(object).columns.tolist()
    if display_summary:
        print(f"Number of categorical features: {len(features)}")
        print(f"Categorical features: {features}")
    return features


def numerical_features(
    data_frame: pd.DataFrame, display_summary: bool = True
) -> list[str]:
    """Get numerical features in a DataFrame.
    Args:
        data_frame (pd.DataFrame): DataFrame to get numerical features.
        display_summary (bool, optional): Whether to display summary. Defaults to True.

    Returns:
        list[str]: Numerical features.
    """
    features: list[str] = data_frame.select_dtypes(include=np.number).columns.tolist()
    if display_summary:
        print(f"Number of numerical features: {len(features)}")
        print(f"Numerical features: {features}")
    return features


def boolean_features(
    data_frame: pd.DataFrame, display_summary: bool = True
) -> list[str]:
    """Get boolean features in a DataFrame.
    Args:
        data_frame (pd.DataFrame): DataFrame to get boolean features.
        display_summary (bool, optional): Whether to display summary. Defaults to True.

    Returns:
        list[str]: Boolean features.
    """
    features: list[str] = [
        i for i in data_frame.columns if data_frame[i].nunique() == 2
    ]
    if display_summary:
        print(f"Number of boolean features: {len(features)}")
        print(f"Boolean features: {features}")
    return features


def zero_variance_features(
    data_frame: pd.DataFrame, display_summary: bool = True
) -> list[str]:
    """Get zero variance features in a DataFrame.
    Args:
        data_frame (pd.DataFrame): DataFrame to get zero variance features.
        display_summary (bool, optional): Whether to display summary. Defaults to True.

    Returns:
        list[str]: Zero variance features.
    """
    features: list[str] = [
        i for i in data_frame.columns if data_frame[i].nunique() == 1
    ]
    if display_summary:
        print(f"Number of zero variance features: {len(features)}")
        print(f"Zero variance features: {features}")
    return features
