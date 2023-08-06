import numpy as np

from flyingfish.EDA.estimates_location import arithmetic_mean


def covariance(data_1: list[float], data_2: list[float]) -> float:
    """
    Compute covariance of two data sets according to following folumna:
    $$cov(X,Y) = \\frac{\\sum_{i=1}^{n}(x_i-\\bar{x})(y_i-\\bar{y})}{n-1}$$
    """
    assert len(data_1) == len(data_2)
    mean_1 = arithmetic_mean(data_1)
    mean_2 = arithmetic_mean(data_2)
    n = len(data_1)
    diff_1 = [i-mean_1 for i in data_1]
    diff_2 = [i-mean_2 for i in data_2]
    cov = sum(np.multiply(diff_1, diff_2))/(n-1)
    return cov


def lin_interpol_2D(
        x1: float, x2: float, xi: float, y1: float, y2: float) -> float:
    """Linear interpolation between two points in 2D Euclidean plane."""
    return y1 + (xi-x1)/(x2-x1)*(y2-y1)


def bin_2d_feature(
        x_intervals: list[float], 
        y_intervals: list[float],
        x_data: list[float], 
        y_data: list[float], 
        z_data: list[float], 
        aggregate_fn=np.mean
        ) -> np.array(float):
    """
    2D binning of a third feature.

    Args:
        x_intervals (list[float]): x binning edges (lower not included, upper included)
        y_intervals (list[float]): y binning edges (lower not included, upper included)
        x_data (list[float]): x values
        y_data (list[float]): y values
        z_data (list[float]): values to bin
        aggregate_fn (function): aggregation function (e.g. np.mean, np.sum)

    Returns:
        res_grid (np.array): binned
    """
    assert len(x_data) == len(y_data) == len(z_data)
    n = len(x_data)
    res_grid = np.zeros(shape=(len(y_intervals), len(x_intervals)))

    for xx in range(len(x_intervals)):
        for yy in range(len(y_intervals)):
            my_bin = []

            for i in range(n):
                if (x_intervals[xx][0] < x_data[i] <= x_intervals[xx][1]) and (y_intervals[yy][0] < y_data[i] <= y_intervals[yy][1]):
                    print(f"point ({x_data[i], y_data[i], z_data[i]}) goes to x interval {x_intervals[xx]} and y interval {y_intervals[yy]}")
                    my_bin.append(z_data[i])

            if my_bin != []:
                res_grid[yy,xx] = aggregate_fn(my_bin)
            else:
                res_grid[yy,xx] = 0

    return res_grid
