import itertools
from enum import Enum
from typing import TypeAlias


class RiskTypeGLT(str, Enum):
    def __init__(self, display_name: str) -> None:
        self.display_name = display_name

    def __str__(self) -> str:
        return self.display_name

    NUKES = "nukes"
    BIO = "bio"
    NATURAL = "natural"
    UNKNOWN = "unknown"
    NANO = "nano"


class RiskTypeAI(str, Enum):
    def __init__(self, display_name: str) -> None:
        self.display_name = display_name

    def __str__(self) -> str:
        return self.display_name

    TOTAL = "ai"
    MISALIGNMENT = "ai misalignment"
    MISUSE = "ai misuse"


RiskType: TypeAlias = RiskTypeAI | RiskTypeGLT


RISK_TYPES = {
    # Dict of Risk Category: list(risk_type)
    "glt": list(RiskTypeGLT),
    "ai": [r for r in RiskTypeAI if r.name != "TOTAL"],
}


def get_glt_risk_types() -> list[RiskTypeGLT]:
    """
    Returns list of GLT Risk Types only
    """
    return RISK_TYPES["glt"]


def get_risk_types() -> list[RiskType]:
    """
    Returns list of all Risk Types.
    """
    return list(itertools.chain(*list(RISK_TYPES.values())))


def get_risk_type_by_name(name: str) -> RiskType:
    if name not in get_risk_types():
        raise ValueError(f"No supported risk type with name: {name}")
    try:
        return RiskTypeAI(name)
    except ValueError:
        return RiskTypeGLT(name)
