from functools import lru_cache
from inspect import get_annotations, signature
from random import randrange

import pytest
from pydantic import ValidationError

from ccm.base_parameters import BaseParameters, FrozenDict
from ccm.contexts import (
    get_parameters,
    inject_parameters,
    inject_parameters_with_cache,
    inject_parameters_with_lru_cache,
    updated_parameters,
    using_parameters,
)
from ccm.parameters import Parameters as ModelParameters


# This overrides the fixture in conftest.py
# so that we can test the `using_parameters` context manager
# without any defaults set already
@pytest.fixture(autouse=True, scope="module")
def model_parameters():
    return None


class MockSpecificParameters(BaseParameters, frozen=True):
    other_number: int = 2


class MockParameters(ModelParameters, frozen=True):
    number: int = 1
    mw: MockSpecificParameters = MockSpecificParameters()


def test_get_parameters():
    params = MockParameters()
    with using_parameters(params):
        assert get_parameters() == params
        assert get_parameters(MockSpecificParameters) == params.mw


@inject_parameters
def example(params: MockParameters, x: int) -> int:
    """
    This is an example function that uses the `inject_parameters` decorator.
    """
    return params.number + x


def test_basic_injection():
    params = MockParameters()
    with using_parameters(params):
        assert example(3) == 4


def test_injection_with_override():
    params = MockParameters()
    another_params = MockParameters(number=3)
    with using_parameters(params):
        assert example(3) == 4
        with using_parameters(another_params):
            assert example(3) == 6
        assert example(3) == 4


def test_injection_without_context():
    with pytest.raises(LookupError):
        example(3)


def test_injection_with_wrong_context():
    with pytest.raises(AttributeError), using_parameters(MockSpecificParameters()):  # type: ignore
        example(3)


def test_injection_preserves_metadata():
    # Check the function name
    assert example.__name__ == "example"
    # Check docstring
    assert example.__doc__ is not None
    assert "decorator" in example.__doc__
    # Check return annotation
    assert get_annotations(example)["return"] == int


def test_injection_strips_first_arg():
    # The signature shouldn't include the `params` argument
    sig = signature(example)
    assert len(sig.parameters) == 1
    # Check the annotations
    assert get_annotations(example) == {"x": int, "return": int}


@inject_parameters
def example_mw(params: MockSpecificParameters, x: int) -> int:
    return params.other_number + x


def test_injection_specific_params():
    params = MockParameters()
    with using_parameters(params):
        assert example_mw(3) == 5


def test_specific_injection_with_override():
    params = MockParameters()
    another_params = MockParameters(mw=MockSpecificParameters(other_number=6))
    with using_parameters(params):
        assert example_mw(3) == 5
        with using_parameters(another_params):
            assert example_mw(3) == 9
        assert example_mw(3) == 5


def test_specific_injection_with_no_context():
    with pytest.raises(LookupError):
        example_mw(3)


def test_update():
    params = MockParameters()
    with using_parameters(params):
        assert example(3) == 4
        updates = {"number": 3}
        with updated_parameters(updates):
            assert example(3) == 6
        assert example(3) == 4
    with pytest.raises(LookupError):
        example(3)


def test_specific_update():
    params = MockParameters()
    with using_parameters(params):
        assert example_mw(3) == 5
        updates = {"other_number": 3}
        with updated_parameters(updates, submodel=MockSpecificParameters):
            assert example_mw(3) == 6
        assert example_mw(3) == 5


def test_invalid_update():
    params = MockParameters()
    with using_parameters(params):
        assert example(3) == 4
        invalid_updates = {"random_attribute": 3}
        with pytest.raises(ValidationError), updated_parameters(invalid_updates, submodel=MockSpecificParameters):
            example(3)
        assert example(3) == 4


@lru_cache
@inject_parameters
def cache_wraps_params(params: MockParameters, x: int) -> int:
    return params.number + x


def test_injection_with_cache():
    params = MockParameters()
    with using_parameters(params):
        assert cache_wraps_params(3) == 4

    assert cache_wraps_params(3) == 4  # should be cached

    other_params = MockParameters(number=3)
    with using_parameters(other_params):
        assert cache_wraps_params(3) == 4  # should still be cached


@inject_parameters
@lru_cache
def params_wraps_cache(params: MockParameters, x: int) -> int:
    return params.number + x


# In tests with raw @lru_cache,
# type checking fails because @lru_cache isn't properly typed.
def test_cache_with_injection():
    params = MockParameters()
    with using_parameters(params):
        assert params_wraps_cache(3) == 4  # type: ignore

    with pytest.raises(LookupError):
        params_wraps_cache(3)  # type: ignore


def test_cache_with_injection_and_override():
    params = MockParameters()
    another_params = MockParameters(number=7)
    with using_parameters(params):
        assert params_wraps_cache(3) == 4  # type: ignore
        with using_parameters(another_params):
            assert params_wraps_cache(3) == 10  # type: ignore
        assert params_wraps_cache(3) == 4  # type: ignore


@inject_parameters_with_cache
def cache_helper(params: MockParameters, x: int) -> int:
    """This is an example docstring"""
    return params.number + x


def test_inject_with_cache_helper():
    params = MockParameters(number=8)
    with using_parameters(params):
        assert cache_helper(3) == 11

    with pytest.raises(LookupError):
        cache_helper(3)


def test_cache_helper_preserves_metadata():
    # Check the function name
    assert cache_helper.__name__ == "cache_helper"
    # Check docstring
    assert cache_helper.__doc__ is not None
    assert "example docstring" in cache_helper.__doc__
    # Check return annotation
    assert get_annotations(cache_helper)["return"] == int


def test_cache_helper_strips_first_arg():
    # The signature shouldn't include the `params` argument
    sig = signature(cache_helper)
    assert len(sig.parameters) == 1
    # Check the annotations
    assert get_annotations(cache_helper) == {"x": int, "return": int}


class Example:
    x = 1

    @inject_parameters
    def method(self, params: MockParameters, x: int) -> int:
        """
        This is an example function that uses the `inject_parameters` decorator.
        """
        return params.number + self.x


def test_method_injection():
    params = MockParameters(number=3)
    with using_parameters(params):
        assert Example().method(3) == 4


def test_method_preserves_metadata():
    # Check the function name
    assert Example.method.__name__ == "method"
    # Check docstring
    assert Example.method.__doc__ is not None
    assert "decorator" in Example.method.__doc__
    # Check return annotation
    assert get_annotations(Example.method)["return"] == int


# Test the FrozenDict primitive
class FrozenDictModel(BaseParameters, frozen=True):
    x: FrozenDict[str, int]


def test_frozendict():
    model = FrozenDictModel(x=FrozenDict({"a": 1, "b": 2}))
    assert model.x == {"a": 1, "b": 2}
    # Test that it's hashable
    hash(model)
    hash(model.x)
    # Test that it can be serialized
    model.model_dump()
    model.model_dump_json()
    # Test that it can be deserialized
    test = {"x": {"a": 1, "b": 2}}
    deserialized_model = FrozenDictModel.model_validate(test)
    assert deserialized_model.x == {"a": 1, "b": 2}
    # Test that it can be deserialized from json
    test_json = model.model_dump_json()
    deserialized_model = FrozenDictModel.model_validate_json(test_json)
    assert deserialized_model.x == {"a": 1, "b": 2}
    # Test that the schema can be generated
    FrozenDictModel.model_json_schema()


def test_inject_parameters_with_lru_cache():
    value1: int
    value2: int
    value3: int
    with using_parameters(MockParameters(number=1)):
        value1 = _get_injected_lru_cached_value()
        value2 = _get_injected_lru_cached_value()
        value3 = _get_injected_lru_cached_value()
    assert value1 == value2 == value3

    value4: int
    with using_parameters(MockParameters(number=2)):
        value4 = _get_injected_lru_cached_value()
    assert value1 != value4

    # Pushing the first value out of the cache...
    with using_parameters(MockParameters(number=3)):
        _get_injected_lru_cached_value()

    # This should still be in the cache at this point
    value6: int
    with using_parameters(MockParameters(number=2)):
        value6 = _get_injected_lru_cached_value()
    assert value4 == value6

    # Expecting a different output this time, in spite of using MockParameters(1) again, because we went over the
    #   cache maxsize
    value7: int
    with using_parameters(MockParameters(number=1)):
        value7 = _get_injected_lru_cached_value()
    assert value1 != value7


def test_inject_parameters_with_lru_cache_and_additional_args():
    with using_parameters(MockParameters(number=1)):
        value1 = _get_injected_lru_cached_value_with_additional_args(func_param=1)
        assert value1[1] == 1
        value2 = _get_injected_lru_cached_value_with_additional_args(func_param=2)
        value3 = _get_injected_lru_cached_value_with_additional_args(func_param=1)
        # Pushing the first call out of the cache
        _get_injected_lru_cached_value_with_additional_args(func_param=3)
        _get_injected_lru_cached_value_with_additional_args(func_param=4)
        value4 = _get_injected_lru_cached_value_with_additional_args(func_param=1)
        # Expecting BOTH parts of value2 to be different from value1, because the additional arg causes a new cache key
        #   to be used.
        assert value1[0] != value2[0]
        assert value1[1] != value2[1]
        # This should retrieve the cached value from before when the args were the same
        assert value3 == value1
        # ...But the first entry has been pushed out of the cache by this point...
        assert value4 != value1


@inject_parameters_with_lru_cache(maxsize=2)
def _get_injected_lru_cached_value(params: ModelParameters) -> int:
    return randrange(100_000_000)


@inject_parameters_with_lru_cache(maxsize=2)
def _get_injected_lru_cached_value_with_additional_args(params: ModelParameters, func_param: int) -> tuple[int, int]:
    return (randrange(100_000_000), func_param)
