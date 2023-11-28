from typing import Annotated, Literal

from pydantic import Field

from ccm.base_parameters import BaseParameters


class GhdInterventionParams(BaseParameters, frozen=True):
    type: Literal["GHD Intervention Parameters"] = "GHD Intervention Parameters"
    version: Literal["1"] = "1"
    adjust_for_xrisk: Annotated[
        bool,
        Field(
            title="Adjust for existential risk",
            description=(
                "Adjust for the existential risks when estimating GHD effectiveness estimates. "
                "This downward adjustement is applied when estimating the time over which the "
                "intervention has an effect."
            ),
        ),
    ] = False
