from abc import abstractmethod
from typing import Annotated, Callable, Literal, Optional, TypeAlias, Union

import numpy as np
import squigglepy as sq
from pydantic import BaseModel, Field, field_validator


def _clean_float(v) -> float | None:
    # Returns None if infinite, nan or None
    if v is None or np.isinf(v) or np.isnan(v):
        return None

    return float(v)


def _has_x_y(dist: sq.OperableDistribution) -> bool:
    return dist.x is not None and dist.y is not None


def clip_validator(v):
    if v[0] is not None and v[1] is not None and v[0] >= v[1]:
        raise ValueError("Left clip must be less than right clip")
    return v


class DistributionSpec(BaseModel, frozen=True):
    type: str = Field(
        description=(
            "The way the distribution is specified. This is used as a discriminator"
            " for how the distribution is being defined."
        )
    )
    distribution: Literal["normal", "lognormal", "uniform", "beta", "gamma", "constant"] = Field(
        description="The type of the resulting distribution itself. Also the corresponding name in Squiggle."
    )
    __hash__: Callable[..., int] = object.__hash__

    @abstractmethod
    def get_distribution(self) -> sq.OperableDistribution:
        """Obtains the Squigglepy distribution specified by this spec."""
        ...

    @classmethod
    def from_distribution(cls, dist: sq.OperableDistribution) -> "SomeDistribution":
        """Constructs a DistributionSpec from a Squigglepy distribution."""
        if isinstance(dist, sq.UniformDistribution):
            return UniformDistributionSpec.from_distribution(dist)
        elif isinstance(dist, sq.ConstantDistribution):
            return ConstantDistributionSpec.from_distribution(dist)
        elif isinstance(dist, sq.NormalDistribution) or isinstance(dist, sq.LognormalDistribution) and _has_x_y(dist):
            return ConfidenceDistributionSpec.from_distribution(dist)
        elif isinstance(dist, sq.GammaDistribution):
            return GammaDistributionSpec.from_distribution(dist)
        elif isinstance(dist, sq.BetaDistribution):
            return BetaDistributionSpec.from_distribution(dist)
        elif isinstance(dist, sq.DiscreteDistribution):
            return CategoricalDistributionSpec.from_distribution(dist)
        raise TypeError(f"Unsupported distribution: {type(dist)}")

    def to_sq(self):
        # Shortcut for get_distribution
        return self.get_distribution()

    @classmethod
    def from_sq(cls, dist: sq.OperableDistribution):
        # Shortcut for from_distribution
        return cls.from_distribution(dist)


class ConstantDistributionSpec(DistributionSpec, frozen=True):
    """
    A way to specify a constant distribution by giving a constant value.
    """

    type: Literal["constant"]
    distribution: Literal["constant"]
    value: float

    def get_distribution(self):
        return sq.ConstantDistribution(self.value)

    @classmethod
    def from_distribution(cls, dist: sq.ConstantDistribution):
        return cls(type="constant", distribution="constant", value=float(dist.x))


class RangeDistributionSpec(DistributionSpec, frozen=True):
    """
    Abstract base class for distribution specs that specify a range.
    """

    range: tuple[float, float]

    @field_validator("range")
    @classmethod
    def range_validator(cls, v):
        if v[0] >= v[1]:
            raise ValueError("Range low must be less than range high")
        return v


class UniformDistributionSpec(RangeDistributionSpec, frozen=True):
    """
    A way to specify a uniform distribution by giving a range.
    """

    type: Literal["uniform"]
    distribution: Literal["uniform"]

    def get_distribution(self):
        x, y = self.range
        if self.distribution == "uniform":
            return sq.uniform(x, y)
        raise ValueError(f"Unknown distribution type: {self.distribution}")

    @classmethod
    def from_distribution(cls, dist: sq.UniformDistribution | sq.BetaDistribution | sq.GammaDistribution):
        if not _has_x_y(dist):
            raise ValueError("Distribution must have x and y values")

        if not isinstance(dist, sq.UniformDistribution):
            raise TypeError(f"Unknown distribution type: {type(dist)}")

        return cls(
            type="uniform",
            distribution="uniform",
            # Typing ignored because Squigglepy has the wrong types for clip
            # (will be fixed in the next squigglepy release)
            range=(float(dist.x), float(dist.y)),  # type: ignore
        )


class ConfidenceDistributionSpec(RangeDistributionSpec, frozen=True):
    """
    A way to specify a distribution by giving a confidence interval.
    """

    type: Literal["confidence"]
    distribution: Optional[Literal["normal", "lognormal"]] = Field(
        description="If not given, lognormal will be preferred for positive ranges and normal for negative ranges."
    )
    clip: tuple[float | None, float | None] = (None, None)
    credibility: Literal[90, 80, 50] = 90

    @field_validator("clip")
    @classmethod
    def clip_validator(cls, v):
        return clip_validator(v)

    def get_distribution(self):
        x, y = self.range
        if self.distribution == "normal":
            return sq.norm(x, y, credibility=self.credibility, lclip=self.clip[0], rclip=self.clip[1])
        elif self.distribution == "lognormal":
            return sq.lognorm(x, y, credibility=self.credibility, lclip=self.clip[0], rclip=self.clip[1])
        elif self.distribution is None:
            # This dynamically uses either a normal or lognormal distribution
            # depending on the range of the distribution
            return sq.to(x, y, credibility=self.credibility, lclip=self.clip[0], rclip=self.clip[1])
        raise ValueError(f"Unknown distribution type: {self.distribution}")

    @classmethod
    def from_distribution(cls, dist: sq.NormalDistribution | sq.LognormalDistribution):
        if not _has_x_y(dist):
            raise ValueError("Distribution must have x and y values")

        if dist.credibility not in (90, 80, 50):
            raise ValueError(f"Non-standard credibility: {dist.credibility} (not supported by Squiggle)")

        distribution: Optional[Literal["normal", "lognormal"]]
        if isinstance(dist, sq.NormalDistribution):
            distribution = "normal"
        elif isinstance(dist, sq.LognormalDistribution):
            distribution = "lognormal"
        else:
            raise TypeError(f"Unknown distribution type: {type(dist)}")

        return cls(
            type="confidence",
            distribution=distribution,
            range=(float(dist.x), float(dist.y)),  # type: ignore
            credibility=dist.credibility or 90,
            clip=(_clean_float(dist.lclip), _clean_float(dist.rclip)),
        )

    @classmethod
    def norm(
        cls,
        lo: float,
        hi: float,
        credibility: Literal[90, 80, 50] = 90,
        lclip: float | None = None,
        rclip: float | None = None,
    ):
        """Construct a normal distribution instance of ConfidenceDistributionSpec."""
        return cls(
            type="confidence",
            distribution="normal",
            range=(lo, hi),
            credibility=credibility,
            clip=(_clean_float(lclip), _clean_float(rclip)),
        )

    @classmethod
    def lognorm(
        cls,
        lo: float,
        hi: float,
        credibility: Literal[90, 80, 50] = 90,
        lclip: float | None = None,
        rclip: float | None = None,
    ):
        """Construct a lognormal distribution instance of ConfidenceDistributionSpec."""
        return cls(
            type="confidence",
            distribution="lognormal",
            range=(lo, hi),
            credibility=credibility,
            clip=(_clean_float(lclip), _clean_float(rclip)),
        )


class GammaDistributionSpec(DistributionSpec, frozen=True):
    """
    A way to specify a gamma distribution by giving a shape and scale.
    """

    type: Literal["gamma"]
    distribution: Literal["gamma"]
    clip: tuple[float | None, float | None] = (None, None)
    shape: float = Field(gt=0)
    scale: float = Field(gt=0)

    @field_validator("clip")
    @classmethod
    def clip_validator(cls, v):
        return clip_validator(v)

    def get_distribution(self):
        return sq.gamma(self.shape, self.scale, lclip=self.clip[0], rclip=self.clip[1])  # type: ignore

    @classmethod
    def from_distribution(cls, dist: sq.GammaDistribution):
        return cls(
            type="gamma",
            distribution="gamma",
            shape=float(dist.shape),
            scale=float(dist.scale),
            clip=(_clean_float(dist.lclip), _clean_float(dist.rclip)),
        )


class BetaDistributionSpec(DistributionSpec, frozen=True):
    """
    A way to specify a beta distribution by giving alpha and beta.
    """

    type: Literal["beta"]
    distribution: Literal["beta"]
    alpha: float = Field(gt=0)
    beta: float = Field(gt=0)

    def get_distribution(self):
        return sq.beta(self.alpha, self.beta)

    @classmethod
    def from_distribution(cls, dist: sq.BetaDistribution):
        return cls(type="beta", distribution="beta", alpha=float(dist.a), beta=float(dist.b))

    @classmethod
    def create(cls, alpha: float, beta: float):
        """Create a BetaDistributionSpec from alpha and beta parameters. Note: The convention would be to call this
        method `beta`, but that would conflict with the instance variable named `beta`.
        """
        return cls(type="beta", distribution="beta", alpha=alpha, beta=beta)


class CategoricalDistributionSpec(DistributionSpec, frozen=True):
    type: Literal["categorical"]
    distribution: Literal["categorical"]
    items: list[tuple[float, float]] = Field(description="List of (probability, category) tuples")

    @field_validator("items")
    @classmethod
    def categories_validator(cls, v):
        if sum(x[0] for x in v) != 1:
            raise ValueError("Probabilities must sum to 1")
        return v

    def get_distribution(self):
        return sq.discrete([[x, y] for x, y in self.items])

    @classmethod
    def from_distribution(cls, dist: sq.DiscreteDistribution):
        if isinstance(dist.items, list):
            if isinstance(dist.items[0], list):
                # Convert to tuple
                items = list(dist.items)
            else:
                # Implies equal probability for each category
                prob = 1 / len(dist.items)
                items = [(prob, x) for x in dist.items]

        elif isinstance(dist.items, dict):
            items = [(y, x) for x, y in dist.items.items()]
        else:
            raise TypeError(f"Unknown way to specify categories: {type(dist.items)}")

        return cls(type="categorical", distribution="categorical", items=items)


SomeDistribution: TypeAlias = Annotated[
    Union[
        # Type alias meant to be used in place of DistributionSpec
        # for models that accept any of the distribution types
        # This is useful because it disambiguates the
        # type of the distribution to TypeScript clients
        UniformDistributionSpec,
        ConstantDistributionSpec,
        ConfidenceDistributionSpec,
        GammaDistributionSpec,
        BetaDistributionSpec,
        CategoricalDistributionSpec,
    ],
    Field(discriminator="type", validate_default=True),
]


class OutcomeShapeModel(BaseModel, frozen=True):
    """Probability of a project being net good, and intensity modifier of how bad it can turn out to be otherwise"""

    prob_good: Annotated[float, Field(description="Probability of a project turning out to be net good.")]
    intensity_bad: Annotated[float, Field(description="Intensity modifier for how bad the project can turn out to be.")]
