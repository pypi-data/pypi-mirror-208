from fractions import Fraction
from itertools import chain, repeat, zip_longest
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

from fast_poibin.pmf import FloatSequence, calc_pmf_dp, convolve


def calc_pmf_fractions(probabilities: list[Fraction]) -> list[float]:
    """Calculate PMF of Poisson binomial distribution by dynamic programming.

    Complexity:
        Time: O(N^2)
        Space: O(N)
    """
    dp = [Fraction()] * (len(probabilities) + 1)
    dp[0] = Fraction(1)
    for i, prob in enumerate(probabilities):
        for j in range(i + 1, 0, -1):
            dp[j] = dp[j] * (1 - prob) + dp[j - 1] * prob
        dp[0] *= 1 - prob
    return [float(x) for x in dp]


def calc_pmf_fft(probabilities: FloatSequence) -> npt.NDArray[np.float64]:
    """Calculate PMF of Poisson binomial distribution by divide and conquer method.

    Complexity:
        Time: O(N(logN)^2)
        Space: O(N)
    """
    size = len(probabilities)
    polynomials = [np.array((1 - p, p), dtype=np.float64) for p in probabilities]

    def _convolve(
        poly1: npt.NDArray[np.float64], poly2: Optional[npt.NDArray[np.float64]]
    ) -> npt.NDArray[np.float64]:
        if poly2 is None:
            return poly1
        return convolve(poly1, poly2)

    while len(polynomials) > 1:
        it = iter(polynomials)
        polynomials = [_convolve(p1, p2) for p1, p2 in zip_longest(it, it)]

    res = polynomials[0]
    res.resize(size + 1, refcheck=False)
    return np.maximum(res, 0.0)


probs_frac = list(chain.from_iterable(repeat(Fraction(1, denom), 1) for denom in range(2, 100)))
probs_float = [float(x) for x in probs_frac]
pmf_exact = calc_pmf_fractions(probs_frac)
pmf_dp = calc_pmf_dp(np.array(probs_float, dtype=np.float64))
pmf_fft = calc_pmf_fft(probs_float)
plt.style.use("seaborn-v0_8-whitegrid")
plt.plot(pmf_exact, label="exact value")
plt.plot(pmf_dp, label="DP")
plt.plot(pmf_fft, label="FFT")
print(max([abs(x - y) / x for x, y in zip(pmf_exact, pmf_dp)]))
plt.yscale("log")
plt.legend()
plt.xlabel("number of success")
plt.ylabel("probability mass")
plt.title("PMF for 1/2, 1/3, ..., 1/99")
plt.savefig("accuracy.png")
