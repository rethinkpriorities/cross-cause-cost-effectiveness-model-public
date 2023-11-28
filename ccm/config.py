from pathlib import Path

SIMULATIONS = 50_000
CURRENT_YEAR = 2023


# Get the root directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Inputs
PROJECTS_DATA_DIR = BASE_DIR / "data" / "projects"

# Outputs
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_CSVS_DIR = OUTPUT_DIR / "csvs"
OUTPUT_PLOTS_DIR = OUTPUT_DIR / "plots"

RISK_WEIGHTER = "WLU - aggressive"  # EU, MIN, MAX, WLU - aggressive, WLU - symmetric


def get_risk_weighter() -> str:
    return RISK_WEIGHTER


def get_simulations() -> int:
    return SIMULATIONS


def get_current_year() -> int:
    return CURRENT_YEAR
