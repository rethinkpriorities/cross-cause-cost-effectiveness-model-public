import pandas as pd

from ccm.config import BASE_DIR


def get_test_xrisks_df() -> pd.DataFrame:
    xrisk_tests = pd.read_csv(BASE_DIR / "tests" / "xrisk_test.csv").set_index("year")
    return xrisk_tests
