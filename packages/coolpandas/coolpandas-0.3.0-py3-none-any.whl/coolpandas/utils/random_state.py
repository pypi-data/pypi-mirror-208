"""Set Python seeds for results reproducibility."""
import os
import random

import numpy as np


def random_state(seed: int = 0) -> None:
    """Set Python seeds for results reproducibility.

    Args:
        seed (int): Seed to use.
    """
    random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)
