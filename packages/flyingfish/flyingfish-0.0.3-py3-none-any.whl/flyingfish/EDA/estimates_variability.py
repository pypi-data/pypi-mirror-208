import statistics
from flyingfish.EDA.estimates_location import arithmetic_mean, median


def _abs_diff(data: list[float], value: float) -> list[float]:
    """
    Compute the absolute deviation from given value for a list
    of datapoints.
    """
    return [abs(i-value) for i in data]


def mu(data: list[float], k: int) -> float:
    """
    Compute the k-th statistical central moment related to the
    arithmetic mean according to the following formula.
    $$ \\mu^k = \\frac{1}{n} \\sum_{i=1}^{n} (x_i - \\overline{x})^{k}$$
    """
    assert len(data) != 0, "Empty data."
    mean = arithmetic_mean(data)
    diff_k = [(i-mean)**k for i in data]
    return sum(diff_k)/len(diff_k)


def MAD_mean(data: list[float]) -> float:
    """
    Compute the mean absolute deviation from the mean according to
    the following formula.
    $$MAD = \\frac{1}{n} \\sum_{i=1}^{n} |x_{i} - \\overline{x}|$$
    """
    assert len(data) != 0, "Empty data."
    mean = arithmetic_mean(data)
    deviations = _abs_diff(data, mean)
    return sum(deviations)/len(deviations)


def MAD_median(data: list[float]) -> float:
    """
    Compute the mean absolute deviation from the median according to
    the following formula.
    $$MAD = \\frac{1}{n}\\sum_{i=1}^{n} | x_{i} - median(X)|$$
    """
    assert len(data) != 0, "Empty data."
    med = median(data)
    deviations = _abs_diff(data, med)
    return sum(deviations)/len(deviations)


def MedAD_median(data: list[float]) -> float:
    """
    Compute the median absolute deviation from the median according
    to the following formula.
    $$MedAD = median(| x_{i} - median(X)|)$$
    """
    assert len(data) != 0, "Empty data."
    med = median(data)
    deviations = _abs_diff(data, med)
    return statistics.median(deviations)


def variance(data: list[float], biased: bool) -> float:
    """
    Compute the biased $s^2$ or unbiased variance $\\tilde{s^2}$ according
    to the following formula.

    biased: $$ s^2 = \\frac{1}{n}\\sum_{i=1}^{n} (x_i-\\overline{x})^{2} $$
    unbiased: $$ \\tilde{s^2} = \\frac{1}{n-1}\\sum_{i=1}^{n}
    (x_i-\\overline{x})^{2} $$
    """
    assert len(data) != 0, "Empty data."
    mu2 = mu(data, k=2)
    n = len(data)
    if biased:
        return mu2
    else:
        return mu2 * n/(n-1)


def stdev(data: list[float], biased: bool) -> float:
    """
    Compute the biased $s$ and unbiased standard deviation $\\tilde{s}$ from
    arithmetic mean according the the following formula.

    biased: $$ s = (\\frac{1}{n}\\sum_{i=1}^{n}
    (x_i-\\overline{x})^{2})^{1/2}$$
    unbiased: $$ \\tilde{s} = (\\frac{1}{n-1}\\sum_{i=1}^{n}
    (x_i-\\overline{x})^{2})^{1/2} $$
    """
    assert len(data) != 0, "Empty data."
    mu2 = mu(data, k=2)
    n = len(data)
    if biased:
        return mu2**(1/2)
    else:
        return (mu2*n/(n-1))**(1/2)


def range(data: list[float]) -> float:
    """Compute the range according the the following formula.
    $$r = max(X) - min(X)$$"""
    assert len(data) != 0, "Empty data."
    return max(data)-min(data)


def iqr(data: list[float]) -> float:
    """
    Compute the interquartile range according the the following formula.
    $$IQR = p_{75\\%}-p_{25\\%}$$
    """
    assert len(data) != 0, "Empty data."
    sort = sorted(data)
    index_25 = int(0.25*len(sort))
    index_75 = int(0.75*len(sort))
    # return np.subtract(*np.percentile(data, [75, 25]))
    return sort[index_75] - sort[index_25]


def coefficient_of_variation(data: list[float]) -> float:
    """
    Compute the variation coefficient based on the biased
    stdev and and the arithmetic mean according to the
    following formula.
    $$CV = \\frac{\\sigma}{\\overline{x}}$$
    """
    cv = float(stdev(data, biased=True)/arithmetic_mean(data))
    return cv
