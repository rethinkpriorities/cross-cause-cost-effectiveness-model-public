from typing import Annotated, TypeAlias, TypeVar, get_args

from frozendict import frozendict
from pydantic import BaseModel, ConfigDict, GetPydanticSchema, PlainSerializer
from pydantic_core import core_schema

KT, KV = TypeVar("KT"), TypeVar("KV")

FrozenDict: TypeAlias = Annotated[
    frozendict[KT, KV],
    GetPydanticSchema(
        # Makes frozendict pass as a dict in terms of validation
        lambda st, h: core_schema.no_info_after_validator_function(
            frozendict, h.generate_schema(dict.__class_getitem__(get_args(st)))
        )
    ),
    PlainSerializer(lambda x: dict(x), return_type=dict),
]


class BaseParameters(BaseModel, frozen=True):
    model_config: ConfigDict = ConfigDict(
        frozen=True,  # This repetition is to enable inheritance
        allow_inf_nan=False,
        validate_default=True,  # Validates all default values
        # TODO: Do we want to just ignore them? It's a graceful way of handling
        # malformed/malicious input, but it's also a silent failure.
        extra="forbid",  # See https://docs.pydantic.dev/latest/usage/model_config/#extra-attributes
        arbitrary_types_allowed=False,
    )

    @classmethod
    def is_top_params_obj(cls) -> bool:
        """Read-only property that informs whether the object is a top-level Parameters object"""

        return False
