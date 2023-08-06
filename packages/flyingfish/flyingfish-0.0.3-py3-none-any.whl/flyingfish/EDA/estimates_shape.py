from collections import Counter

from flyingfish.EDA.estimates_variability import mu, stdev


def coefficient_of_skewness(data: list[float], biased: bool) -> float:
    """
    Compute the biased ($\\mu^3$) and unbiased skewness ($\\tilde{\\mu^3}$)
    according the the following formula.

    biased: $$\\mu^3 = \\frac{1}{n}\\sum_{i=1}^{n}
    (\\frac{x_i-\\overline{x}}{s})^3$$
    unbiased: $$\\tilde{\\mu^3} = \\frac{1}{n-1}\\sum_{i=1}^{n}
    (\\frac{x_i-\\overline{x}}{s})^3$$
    """
    assert len(data) != 0, "Empty data."
    s = stdev(data, biased=True)
    mu3 = mu(data, k=3)
    skew = mu3/s**3
    n = len(data)
    if biased:
        return skew
    else:
        return skew*(n**2)/((n-1)*(n-2))


def coefficient_of_kurtosis(data: list[float], biased: bool) -> float:
    """Compute the biased ($\\mu^4$) and unbiased kortosis ($\\tilde{\\mu^4}$)
    according the the following formula. The excess can easily be computed by
    subtracting 3 from the returned kortosis.

    biased: $$\\mu^4 = \\frac{1}{n}\\sum_{i=1}^{n}
    (\\frac{x_i-\\overline{x}}{s})^4$$
    unbiased: $$\\tilde{\\mu^4} = \\frac{1}{n-1}\\sum_{i=1}^{n}
    (\\frac{x_i-\\overline{x}}{s})^4$$
    """
    assert len(data) != 0, "Empty data."
    s = stdev(data, biased=True)
    mu4 = mu(data, k=4)
    kurt = mu4/s**4
    n = len(data)
    if biased:
        return kurt
    else:
        return kurt*(n**3)/((n-1)*(n-2)*(n-3))


def mode(data: list[float]) -> list[float]:
    """
    Compute the mode. A mode is the most frequent value within the sample.
    """
    assert len(data) != 0, "Empty data."
    c = Counter(data)
    return [k for k, v in c.items() if v == c.most_common(1)[0][1]]
