from typing import Literal

import numpy as np
import pandas as pd
from numpy.typing import NDArray

import ccm.config as config
from ccm.world.risk_types import RiskType


def get_xrisks_df() -> pd.DataFrame:
    xrisk_projects_data = pd.read_csv(config.PROJECTS_DATA_DIR / "xrisk_df.csv")
    # TODO: Don't fudge this this way; instead, update xrisk_df.csv to the explicit values you want.
    xrisk_projects_data = xrisk_projects_data.replace(0, 10 ** (-6))
    return xrisk_projects_data


def get_risks_by_type(risk_type: RiskType | Literal["total"]) -> NDArray[np.float64]:
    try:
        return np.array(get_xrisks_df()[risk_type.value])  # type: ignore  # covered by try-except block
    except AttributeError:
        return np.array(get_xrisks_df()[risk_type])


def get_proportional_risks_by_type(risk_type: RiskType) -> NDArray[np.float64]:
    return get_risks_by_type(risk_type) / get_risks_by_type("total")


def get_baseline_risks() -> NDArray[np.float64]:
    return get_risks_by_type("total")
