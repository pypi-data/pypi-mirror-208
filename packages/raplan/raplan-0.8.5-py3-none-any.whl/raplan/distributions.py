"""RaPlan distributions module."""

import math
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Optional, Union

from serde import InternalTagging, field, serde

__all__ = [
    "compound_probability",
    "Exponential",
    "LogNormal",
    "Pareto",
    "Triangular",
    "Uniform",
    "Weibull",
]


def compound_probability(probabilities: Iterable[float]) -> float:
    """Compound CDF value of multiple contributions."""
    return max(0.0, 1.0 - math.prod(1 - p for p in probabilities))


class Distribution(ABC):
    """Abstract base class for distributions."""

    def cdf(self, x: Union[int, float] = 1.0) -> float:
        """Cumulative probability density function of this distribution."""
        if x < 0:
            return 0.0
        return self._cdf(x)

    @abstractmethod
    def _cdf(self, x: Union[int, float] = 1.0) -> float:
        """Cumulative probability density function of this distribution."""

    @abstractmethod
    def sample(self) -> float:
        """Take a sample of this distribution."""


@serde(tagging=InternalTagging("type"))
@dataclass
class Exponential(Distribution):
    """Exponential distribution.

    Arguments:
        lambd: Occasion rate or 1 divided by the desired mean. In scheduling, it should
            be greater than zero.
    """

    lambd: Union[int, float] = 1.0

    def __post_init__(self):
        self.lambd = float(self.lambd)

    def _cdf(self, x: Union[int, float] = 1.0) -> float:
        return 1.0 - math.exp(-self.lambd * x)

    def sample(self) -> float:
        return random.expovariate(self.lambd)


@serde(tagging=InternalTagging("type"))
@dataclass
class LogNormal(Distribution):
    """Log-normal distribution.

    Arguments:
        mu: Mean of the underlying normal distribution. Any value.
        sigma: Standard deviation of the underlying normal distribution. Must be >0.
    """

    mu: Union[int, float] = 1.0
    sigma: Union[int, float] = 1.0

    def __post_init__(self):
        if self.sigma < 0.0:
            raise ValueError("sigma must be greater than 0.")

    def _cdf(self, x: Union[int, float] = 1.0) -> float:
        return 0.5 * (1.0 + math.erf(math.log(x - self.mu) / (self.sigma * math.sqrt(2))))

    def sample(self) -> float:
        return random.lognormvariate(self.mu, self.sigma)


@serde(tagging=InternalTagging("type"))
@dataclass
class Pareto(Distribution):
    """Pareto distribution.

    Arguments:
        min_x: Minimum x value.
    """

    min_x: Union[int, float] = 1.0
    alpha: Union[int, float] = 1.0

    def __post_init__(self):
        try:
            assert self.min_x > 0, "min_x should be > 0."
            assert self.alpha > 0, "alpha should be > 0."
        except AssertionError as e:
            raise ValueError(e)

    def _cdf(self, x: Union[int, float] = 1.0) -> float:
        if x < self.min_x:
            return 0.0
        else:
            return 1 - (self.min_x / x) ** (self.alpha)

    def sample(self) -> float:
        return self.min_x * random.paretovariate(self.alpha)


@serde(tagging=InternalTagging("type"))
@dataclass
class Triangular(Distribution):
    """Triangular distribution.

    Samples are in the range [low, high] and with the specified mode between those
    bounds. The mode defaults to the midpoint between the two bounds.

    Arguments:
        low: Lower bound of the sample range.
        high: Upper bound of the sample range.
        mode: The mode between those two bounds.
    """

    low: Union[int, float] = 0.0
    high: Union[int, float] = 1.0
    mode: Optional[Union[int, float]] = field(default=None, skip_if_default=True)

    def __post_init__(self):
        if self.mode is None:
            self.mode = 0.5 * (self.high + self.low)

    def _cdf(self, x: Union[int, float] = 1.0) -> float:
        assert self.mode is not None
        a, b, c = self.low, self.high, self.mode
        if x < a:
            return 0.0
        elif x <= c:
            return (x - a) * (x - a) / ((b - a) * (c - a))
        elif x <= b:
            return 1.0 - (b - x) * (b - x) / ((b - a) * (b - c))
        else:
            return 1.0

    def sample(self) -> float:
        return random.triangular(self.low, self.high, self.mode)


@serde(tagging=InternalTagging("type"))
@dataclass
class Uniform(Distribution):
    """A uniform distribution."""

    a: Union[int, float] = 0.0
    b: Union[int, float] = 1.0

    def _cdf(self, x: Union[int, float] = 1.0) -> float:
        a, b = self.a, self.b
        if x <= a:
            return 0.0
        elif x < b:
            return (x - a) / (b - a)
        else:
            return 1.0

    def sample(self):
        return random.uniform(self.a, self.b)


@serde(tagging=InternalTagging("type"))
@dataclass
class Weibull(Distribution):
    """Weibull distribution (2-parameter).

    Arguments:
        alpha: Shape parameter.
        mtbf: Mean time between failure.
    """

    alpha: Union[int, float] = 2.0
    mtbf: Union[int, float] = 10.0

    @property
    def beta(self) -> float:
        """Weibull scale parameter."""
        return self.mtbf / math.gamma(1.0 + 1.0 / self.alpha)

    def _cdf(self, x: Union[int, float] = 1.0) -> float:
        return 1.0 - math.exp(-((x / self.beta) ** self.alpha))

    def sample(self) -> float:
        return random.weibullvariate(self.alpha, self.beta)


Distributions = Union[Exponential, LogNormal, Pareto, Triangular, Uniform, Weibull]
