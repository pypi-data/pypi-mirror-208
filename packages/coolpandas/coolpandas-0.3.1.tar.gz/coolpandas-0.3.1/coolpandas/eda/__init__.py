"""Exploratory Data Analysis (EDA) module for coolpandas."""
from .correlation import get_correlation
from .distribution import get_groupby_distribution
from .duplicates import duplicated_columns, duplicated_rows
from .features_type import (
    boolean_features,
    categorical_features,
    numerical_features,
    zero_variance_features,
)
from .geo_distance import GeoDistance
from .missing_values import get_missing_values
from .random_state import random_state
from .shape import get_shape
from .summary import get_summary
from .value_counts import get_groupby_value_counts, get_value_counts
