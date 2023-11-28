import functools
from collections.abc import Callable
from contextlib import contextmanager
from contextvars import ContextVar, Token
from inspect import Signature, ismethod, signature
from typing import Any, Concatenate, ParamSpec, TYPE_CHECKING, TypeVar, overload

from pyparsing import Generator

from ccm.base_parameters import BaseParameters


if TYPE_CHECKING:
    from ccm.parameters import Parameters as ModelParameters


# Context variable used to access the Parameters object
# see https://docs.python.org/3/library/contextvars.html
PARAMS_VAR: ContextVar["ModelParameters"] = ContextVar("config_var")

# This enables the functions to behave generically
ArbitraryParamsModel = TypeVar("ArbitraryParamsModel", bound=BaseParameters)


def _find_in_model(
    model: "ModelParameters",
    requested_model: type[ArbitraryParamsModel],
) -> tuple[str, ArbitraryParamsModel]:
    """
    Given the class of the requested parameter model, returns the
    attribute name instance of that class in the currently valid parameters object.
    """
    for name, value in model:
        if isinstance(value, requested_model):
            return name, value
    raise LookupError(f"No object of type {requested_model} found in Parameters. Please make sure it exists.")


def _update_params(new_value: "ModelParameters") -> Generator[None, None, None]:
    """
    Updates the Parameters object in the current context.
    This is a helper function for the context manager.
    """
    token: Token["ModelParameters"] = PARAMS_VAR.set(new_value)
    try:
        yield
    finally:
        PARAMS_VAR.reset(token)


@contextmanager
def using_parameters(new_params_value: "ModelParameters") -> Generator[None, None, None]:
    """
    Provides a Parameters object to the context for the duration of the context manager.
    If the context already has a Parameters object, it will be replaced by the provided one.

    This is implemented through context variables, per PEP 567 (https://peps.python.org/pep-0567/).
    The implementation is thread-safe and can be used in async environments.
    """
    yield from _update_params(new_params_value)


@contextmanager
def updated_parameters(
    updates: dict[str, Any],
    submodel: type[BaseParameters] | None = None,
) -> Generator[None, None, None]:
    """
    Updates attributes of the given parameters model in the current context. If no model is given,
    the default Parameters model is used. Updates are passed as a dictionary of attribute names and values,
    but cannot be nested (i.e. modify submodels).

    If you need to replace an entire parameters object at once, use `using_parameters` instead.

    Examples:
        >>> class MockParameters(BaseParameters):
        >>>     number: int
        >>>
        >>> params = MockParameters(number=2)
        >>> with using_parameters(params):
        >>>     assert get_parameters() == params # The same object is returned
        >>>     with updated_parameters({"number": 3}):
        >>>         assert get_parameters() == MockParameters(number=3)  # A new object is returned
    """
    old_params = get_parameters()
    if submodel:
        name, old_submodel = _find_in_model(old_params, submodel)
        # Validate the updates
        old_submodel.model_validate(updates)
        # Perform a granular update
        updated_submodel = old_submodel.model_copy(update=updates)
        updated_params = old_params.model_copy(update={name: updated_submodel})
        yield from _update_params(updated_params)
    else:
        # Validate the updates
        old_params.model_validate(updates)
        # Perform a granular update
        updated_params = old_params.model_copy(update=updates)
        yield from _update_params(updated_params)


def get_parameters(
    requested_submodel: type[ArbitraryParamsModel] | None = None,
) -> "ArbitraryParamsModel | ModelParameters":
    """
    Given the class of the requested parameter model, returns the
    instance of that class in the current context.

    If Parameters itself is requested, the Parameters object
    is returned as-is, else if a specific model is requested,
    a matching instance is obtained from the Parameters object.

    Examples:
        >>> class MockParameters(BaseParameters):
        >>>    number: int
        >>>
        >>> params = MockParameters(number=2)
        >>> with using_parameters(params):
        >>>   assert get_parameters() == params # The same object is returned
    """
    # Get the Parameters object from the context
    try:
        params: "ModelParameters" = PARAMS_VAR.get()
    except LookupError as e:
        raise LookupError(
            "No Parameters object found in context. "
            "Please use the `using_parameters` context manager to provide one."
        ) from e

    needed_param = None
    if requested_submodel:
        # Perform a lookup in the Parameters object
        _, needed_param = _find_in_model(params, requested_submodel)
        assert isinstance(needed_param, requested_submodel)
    else:
        needed_param = params

    return needed_param


# These help preserve strict type checking when using the decorator
# as prescribed by https://peps.python.org/pep-0484/ (type hints) and
# https://peps.python.org/pep-0612/ (param specs)
Parameters = ParamSpec("Parameters")
ReturnValue = TypeVar("ReturnValue")


# This is the type hint for normal functions
@overload
def inject_parameters(
    f: Callable[Concatenate[ArbitraryParamsModel, Parameters], ReturnValue]
) -> Callable[Parameters, ReturnValue]:
    ...


Self = TypeVar("Self")


# This is the type hint for methods
@overload
def inject_parameters(
    f: Callable[Concatenate[Self, ArbitraryParamsModel, Parameters], ReturnValue]
) -> Callable[Concatenate[Self, Parameters], ReturnValue]:
    ...


# The actual implementation
def inject_parameters(f: Callable) -> Callable:
    """
    A decorator that modifies a function or method to automatically fetch and inject a requested parameter model
    from the current context when called. The parameter model to be injected is indicated by the type annotation
    of the first argument of the decorated function or method.

    This decorator is designed to work with both regular functions and methods. For methods, it correctly handles
    the `self` parameter, ensuring that the method's access to its instance or class attributes is not affected.

    The parameter model must be a subclass of `BaseParameters`.

    Example:
        >>> class MockParameters(BaseParameters):
        >>>     number: int
        >>>
        >>> @inject_parameters
        >>> def example(params: MockParameters, x: int) -> int:
        >>>     return params.number + x
        >>>
        >>> params = MockParameters(number=2)
        >>> with using_parameters(params):
        >>>     assert example(3) == 5  # The `params` argument is automatically injected

    Args:
        f(Callable[Concatenate[ArbitraryParamsModel, Parameters], ReturnValue]): The function or method to be decorated.

    Returns:
        Callable[Parameters, ReturnValue]: The decorated function or method, which automatically fetches and injects
                                           the requested parameter model when called.

    Raises:
        TypeError: If the first argument of the function does not have a type annotation, or if the type annotation
                   is not a subclass of `BaseParameters`.
    """

    # Extract the expected type of the parameters from the signature
    arguments = list(signature(f).parameters.values())
    assert len(arguments) > 0, "The function should have at least one argument."
    # Check if the function is a method (ismethod doesn't work for unbound methods)
    is_method = ismethod(f) or arguments[0].name == "self"
    params_arg_name: str = arguments[1 if is_method else 0].name
    params_arg_type: type[BaseParameters] = arguments[1 if is_method else 0].annotation

    # Validate the type (it should be a Pydantic model)
    if params_arg_type is Signature.empty:
        raise TypeError("You should provide a type annotation for the first argument of the function.")
    try:
        submodel = None if params_arg_type.is_top_params_obj() else params_arg_type
    except AttributeError as e:
        raise TypeError("The first argument of the function should be a BaseParameters subclass.") from e

    # Create a new wrapper function that injects the identified class instance from the Parameters object
    # Because the actual injection happens in the inner function, it picks up the context
    # of the function call, not the decorator call.
    if is_method:

        def f_method(self, *args, **kwargs):
            needed_param = get_parameters(requested_submodel=submodel)
            return f(self, needed_param, *args, **kwargs)

        wrapper = f_method  # This signals rebinding

    else:

        def f_function(*args, **kwargs):
            needed_param = get_parameters(requested_submodel=submodel)
            return f(needed_param, *args, **kwargs)

        wrapper = f_function

    # Update signature
    new_arguments = arguments[0:1] + arguments[2:] if is_method else arguments[1:]
    wrapper.__signature__ = signature(f).replace(parameters=new_arguments)

    # Transfer docstrings and metadata
    wrapper_with_metadata = functools.update_wrapper(wrapper, f)

    # Update annotations
    if isinstance(wrapper.__annotations__, dict):
        wrapper.__annotations__.pop(params_arg_name, None)

    return wrapper_with_metadata


@overload
def inject_parameters_with_cache(
    f: Callable[Concatenate[ArbitraryParamsModel, Parameters], ReturnValue]
) -> Callable[Parameters, ReturnValue]:
    ...


@overload
def inject_parameters_with_cache(
    f: Callable[Concatenate[Self, ArbitraryParamsModel, Parameters], ReturnValue]
) -> Callable[Concatenate[Self, Parameters], ReturnValue]:
    ...


def inject_parameters_with_cache(f: Callable) -> Callable:
    """
    Caches the function alongside the injected parameters object.
    This ensures that the cache is invalidated whenever the injected parameters change.
    Equivalent to @cache + @fetch_parameters, but with proper type hints.

    Note: to keep things safe from memory leaks, probably don't use this function. It's technically okay to use when you
    know there is a tightly bounded set of permutations of Parameters available to be input into the target function,
    however that could always change in a future iteration without someone realizing they're creating a memory leak.

    Examples:
        >>> class MockParameters(BaseParameters):
        >>>    number: int
        >>>
        >>> @inject_parameters_with_cache
        >>> def some_function(params: MockParameters, x: int) -> int:
        >>>    return params.number + x
        >>>
        >>> params = MockParameters(number=2)
        >>> with using_parameters(params):
        >>>   assert some_function(3) == 5  # The `params` argument is automatically injected
        >>>   assert some_function(3) == 5  # The result is cached
        >>>
        >>> some_function(3) # But here the cache is invalidated
            LookupError: No Parameters object found in context...
    """
    # Cache and then wrap the function
    cached_f = functools.cache(f)
    injected_f = inject_parameters(cached_f)
    return functools.update_wrapper(injected_f, f)


def inject_parameters_with_lru_cache(maxsize: int = 128):
    """
    Caches the function alongside the injected parameters object.
    This ensures that the cache is invalidated whenever the injected parameters change.
    Equivalent to @lru_cache + @fetch_parameters, but with proper type hints.
    """

    @overload
    def lru_cached_injector(
        f: Callable[Concatenate[ArbitraryParamsModel, Parameters], ReturnValue]
    ) -> Callable[Parameters, ReturnValue]:
        ...

    @overload
    def lru_cached_injector(
        f: Callable[Concatenate[Self, ArbitraryParamsModel, Parameters], ReturnValue]
    ) -> Callable[Concatenate[Self, Parameters], ReturnValue]:
        ...

    def lru_cached_injector(f: Callable) -> Callable:
        cache_wrapper = functools.lru_cache(maxsize=maxsize)
        cached_f = cache_wrapper(f)
        injected_f = inject_parameters(cached_f)
        return functools.update_wrapper(injected_f, f)

    return lru_cached_injector
