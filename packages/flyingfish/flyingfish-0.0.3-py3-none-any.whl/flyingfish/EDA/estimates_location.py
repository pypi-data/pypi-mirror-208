import statistics
import numpy as np


def arithmetic_mean(data: list[float]) -> float:
    """
    Compute the arithmetic mean according to the following formula.
    $$\\overline{x} = \\frac{1}{n} \\sum_{i=1}^{n} x_{i}$$
    """
    if len(data) == 0:
        raise ValueError("empty data")
    return sum(data)/len(data)


def weighted_mean(data: list[float], weights: list[float]) -> float:
    """
    Compute the weighted mean according to the following formula.
    $$\\overline{x_{w}} = \\frac{\\sum_{i=1}^{n} w_i*x_i}
    {\\sum_{i=1}^{n} w_i} $$
    """
    if len(data) == 0:
        raise ValueError("empty data")
    return sum(np.multiply(data, weights))/sum(weights)


def trimean(data: list[float]) -> float:
    """
    Compute the trimean according to following formula.
    $$Trimean = \\frac{q_{0.25}+2q_{0.50}+q_{0.75}}{4} $$
    """
    if len(data) == 0:
        raise ValueError("empty data")
    q_025: float = np.quantile(data, 0.25)
    q_050: float = np.quantile(data, 0.50)
    q_075: float = np.quantile(data, 0.75)
    return (q_025 + 2*q_050 + q_075)/4


def trimmed_mean(data: list[float], p: int) -> float:
    """
    Compute the trimmed mean according to the following formula.
    $p$ is the number of smallest and largest elements which will be skipped.
    $$\\overline{x_{t}} = \\frac{\\sum_{i=p+1}^{n-p} x_i}{n-2p} $$
    """
    if len(data) == 0:
        raise ValueError("empty data")
    trimmed = sorted(data)[p:-p]
    return sum(trimmed)/len(trimmed)


def geometric_mean(data: list[float]) -> float:
    """
    Compute the geometric mean according to the following formula.
    $$\\overline{x_g} = (\\prod _{i=1}^{n}x_{i})^{1/n}$$
    """
    if len(data) == 0:
        raise ValueError("empty data")
    return statistics.geometric_mean(data)


def exponential_mean(data: list[float], m: float) -> float:
    """
    Compute the exponential mean according to the following formula.
    $$\\overline{x_e} = (\\frac{1}{n}\\sum_{i=1}^{n} x_{i}^{m})^{1/m}$$
    """
    if len(data) == 0:
        raise ValueError("empty data")
    base = (sum([x**m for x in data])/len(data))
    return base**(1/m)


def harmonic_mean(data: list[float]) -> float:
    """
    Compute the harmonic mean according to the following formula.
    $$\\overline{x_h} = \\frac{n}{\\sum_{i=1}^{n} \\frac{1}{x_i}}$$
    """
    if len(data) == 0:
        raise ValueError("empty data")
    return statistics.harmonic_mean(data)


def median(data: list[float]) -> float:
    """
    Compute the median. The median is the value in the middle of a
    sorted list. If the list is even, the mean of the two middle values
    is computed.
    """
    if len(data) == 0:
        raise ValueError("empty data")
    return statistics.median(data)


def weighted_median(data: list[float], weights: list[float]) -> float:
    """
    Compute the weighted median by representing a value $x_i$ $w_i$ times
    and compute the median afterwards.
    """
    if len(data) == 0:
        raise ValueError("empty data")
    weighted_list: list[float] = []
    for i in np.arange(len(data)):
        weighted = [data[i]]*weights[i]
        weighted_list.extend(weighted)
    return statistics.median(weighted_list)


def percentile(data: list[float], per: int) -> float:
    """
    Compute the percentile value according to the following formula.
    $$p = \\frac{per}{100}*ns$$
    """
    assert len(data) != 0, "Empty data."
    return float(np.percentile(a=sorted(data), q=per, method="linear"))
