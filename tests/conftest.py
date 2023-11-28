from collections.abc import Generator
from typing import Any

import pytest

from ccm.contexts import get_parameters, using_parameters
from ccm.parameters import Parameters


@pytest.fixture(autouse=True, scope="module")
def model_parameters() -> Generator[Parameters, Any, None]:
    """
    Provides a default set of parameters for all tests in this module.

    Doesn't need to be used explicitly in tests, but can be if access to the parameters is needed.
    """
    with using_parameters(Parameters()):
        yield get_parameters()
