import numpy as np
import pandas as pd

from flyingfish.EDA.estimates_location import arithmetic_mean, median, percentile
from flyingfish.EDA.estimates_variability import stdev, iqr, MedAD_median


def outlier(data: list[float], method: str, solving_strategy: str
            ) -> tuple[list[float], list[float]]:
    """Detect and handle outliers.

    The solving_strategy "drop_outlier" drops outliers beyond thresholds.
    The solving_strategy "cap_outlier" caps outliers with threshold values.
    The solving_strategy "none" (default) applies no correction.

    | method           | description                              |
    | ---------------- | ---------------------------------------- |
    | "zscore"         | Outliers have a z-score > 3.             |
    | "iqr"            | Outliers exceed 1.5 times IQR.           |
    | "hampler_filter" | Outliers lie beyond +/- MAD from median. |
    | "zscore_modified | zscore modified for small sample sizes   |
    """
    assert len(data) != 0, "Empty data."

    if method == "zscore":
        mean = arithmetic_mean(data)
        std = stdev(data, biased=False)
        threshold = 3
        upper_border = mean + threshold*std
        lower_border = mean - threshold*std
        outliers = [x for x in data if not lower_border <= x <= upper_border]
    elif method == "iqr":
        upper_border = percentile(data, 75) + 1.5*iqr(data)
        lower_border = percentile(data, 25) - 1.5*iqr(data)
        outliers = [x for x in data if not lower_border <= x <= upper_border]
    elif method == "hampler_filter":
        med = median(data)
        mad = MedAD_median(data)
        upper_border = med + 3*mad
        lower_border = med - 3*mad
        outliers = [x for x in data if not lower_border <= x <= upper_border]
    elif method == "zscore_modified":
        mean = arithmetic_mean(data)
        mad = MedAD_median(data)
        threshold = 3
        upper_border = mean + threshold*mad/0.6745
        lower_border = mean - threshold*mad/0.6745
        outliers = [x for x in data if not lower_border <= x <= upper_border]
    else:
        upper_border = np.inf
        lower_border = -np.inf
        raise ValueError("method not known")

    if solving_strategy == "drop_outlier":
        data_corr = [x for x in data if x not in outliers]
    elif solving_strategy == "cap_outlier":
        data_corr = [max(min(x, upper_border), lower_border) for x in data]
    elif solving_strategy == "none":
        data_corr = data
    else:
        raise ValueError("solving_strategy not known")

    return outliers, data_corr
