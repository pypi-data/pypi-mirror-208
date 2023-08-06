import os

import pandas as pd
import pytest
import yaml
from cognite.client.exceptions import CogniteAuthError

from akerbp.mlpet import utilities as utils
from akerbp.mlpet.tests.client import CLIENT_WRITE as CLIENT_READ
from akerbp.mlpet.tests.data.data import (
    FORMATION_TOPS_MAPPER,
    TEST_DF,
    VERTICAL_DEPTHS_MAPPER,
)

ID_COLUMNS = "well_name"
VSH_KWARGS = {
    "nan_numerical_value": -9999,
    "nan_textual_value": "MISSING",
    "VSH_curves": ["GR"],
}


WELL_NAMES = ["25/10-10"]


def test_get_formation_tops():
    formation_tops_mapper = utils.get_formation_tops(WELL_NAMES, CLIENT_READ)
    assert formation_tops_mapper == FORMATION_TOPS_MAPPER


def test_get_vertical_depths():
    retrieved_vertical_depths = utils.get_vertical_depths(WELL_NAMES, CLIENT_READ)
    # empty_queries should be an empty list for the provided WELL_NAMES
    assert retrieved_vertical_depths == VERTICAL_DEPTHS_MAPPER


def test_get_trajectory_mapper_from_cdf_returns_all_fields():
    fields = ["MD", "TVDBML", "TVDSS", "TVDKB", "X", "Y"]
    trajectory_mapper = utils.get_trajectory_mapper_from_cdf(WELL_NAMES, CLIENT_READ)
    fields_in_mapper = trajectory_mapper[WELL_NAMES[0]].keys()
    assertions = [field in fields_in_mapper for field in fields]
    assertions_ = [field in fields for field in fields_in_mapper]
    assert sum(assertions) == len(assertions) and sum(assertions_) == len(assertions_)


def test_get_vertical_depths_returns_no_coordinates():
    vertical_depths_mapper = utils.get_vertical_depths(WELL_NAMES, CLIENT_READ)
    fields = vertical_depths_mapper[WELL_NAMES[0]].keys()
    coordinate_fields = ["X", "Y"]
    assertions = [coordinate not in fields for coordinate in coordinate_fields]
    assert sum(assertions) == len(assertions)


def test_get_vertical_depths_returns_vertical_depths():
    vertical_depths_mapper = utils.get_vertical_depths(WELL_NAMES, CLIENT_READ)
    fields = vertical_depths_mapper[WELL_NAMES[0]].keys()
    depth_fields = ["TVDBML", "TVDSS", "TVDKB"]
    assertions = [depth in fields for depth in depth_fields]
    assert sum(assertions) == len(assertions)


def test_get_wellbore_coordinates_returns_coordinates():
    coordinates_mapper = utils.get_wellbore_coordinates(WELL_NAMES, CLIENT_READ)
    fields = coordinates_mapper[WELL_NAMES[0]].keys()
    coordinate_fields = ["X", "Y"]
    assertions = [coordinate in fields for coordinate in coordinate_fields]
    assert sum(assertions) == len(assertions)


def test_get_wellbore_coordinates_returns_no_vertical_depths():
    coordinates_mapper = utils.get_wellbore_coordinates(WELL_NAMES, CLIENT_READ)
    fields = coordinates_mapper[WELL_NAMES[0]].keys()
    vertical_depths = ["TVDBML", "TVDSS", "TVDKB"]
    assertions = [depth not in fields for depth in vertical_depths]
    assert sum(assertions) == len(assertions)


def test_remove_wo_label():
    df = utils.drop_rows_wo_label(TEST_DF[["AC", "BS"]], label_column="BS")
    assert df.shape[0] == 8


def test_standardize_names():
    mapper = yaml.load(
        open("src/akerbp/mlpet/tests/data/test_mappings.yaml", "r"),
        Loader=yaml.SafeLoader,
    )
    utils.standardize_names(TEST_DF.columns.tolist(), mapper=mapper)


def test_standardize_group_formation_name():
    assert utils.standardize_group_formation_name("ØRN") == "ORN"


def test_map_formation_group_system():
    tests = pd.Series(["UNDIFFERENTIATED", "FOO BAR", "NO FORMAL NAME 1", "HeGrE"])
    tests = tests.apply(utils.standardize_group_formation_name)
    assert utils.map_formation_group_system(tests, MissingValue=-9999) == (
        ("UNKNOWN FM", -9999, "UNKNOWN FM", -9999),
        ("UNKNOWN GP", -9999, "UNKNOWN GP", "HEGRE GP"),
        (-9999, -9999, -9999, "TRIASSIC SY"),
    )


def test_get_well_metadata():
    metadata = utils.get_well_metadata(client=CLIENT_READ, well_names=WELL_NAMES)
    assert metadata[WELL_NAMES[0]]["CDF_wellName"] == WELL_NAMES[0]


def test_get_cognite_client_is_logged_in():
    client_id = os.environ["COGNITE_CLIENT_ID_READ"]
    client_secret = os.environ["COGNITE_CLIENT_SECRET_READ"]

    client = utils.get_cognite_client(
        client_id=client_id,
        client_secret=client_secret,
    )
    assert client.iam.token.inspect() is not None


def test_get_cognite_client_wrong_credentials_raise_exception():
    wrong_id = "wrong_id_go_home"
    wrong_secret = "wrong_secret_go_home"
    client = utils.get_cognite_client(client_id=wrong_id, client_secret=wrong_secret)
    with pytest.raises(CogniteAuthError):
        client.login.status()
