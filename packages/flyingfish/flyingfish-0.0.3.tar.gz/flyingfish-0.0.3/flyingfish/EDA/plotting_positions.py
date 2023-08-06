import numpy as np


def plotting_position(n: int, method: str) -> list[float] | None:
    """Compute plotting positions from a given number of elements $n$
    and a method listed below.

    Weibull (1939; all distributions):
    $$ \\frac{i}{n+1}$$
    Hazen (1914):
    $$\\frac{i-0.5}{n}$$
    Cunnane (1979; GEV, log-Gumbel, Pearson Type III, Log-Pearson Type III):
    $$\\frac{i-0.4}{n+0.2}$$
    Chegodayev (1965; GEV, log-Gumbel, Pearson Type III, Log-Pearson Type III):
    $$\\frac{i-0.3}{n+0.4}$$
    Beard (1945; all distributions):
    $$\\frac{i-0.3175}{n+0.365}$$
    """
    match method:
        case "Weibull":
            return [float(i/(n+1)) for i in np.arange(1, n+1, 1)]
        case "Hazen":
            return [float((i-0.5)/n) for i in np.arange(1, n+1, 1)]
        case "Cunnane":
            return [float((i-0.4)/(n+0.2)) for i in np.arange(1, n+1, 1)]
        case "Chegodayev":
            return [float((i-0.3)/(n+0.4)) for i in np.arange(1, n+1, 1)]
        case "Beard":
            return [float((i-0.3175)/(n+0.365)) for i in np.arange(1, n+1, 1)]
