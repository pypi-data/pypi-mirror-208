import pytest
from pandas.testing import assert_frame_equal

from akerbp.mlpet import feature_engineering
from akerbp.mlpet.tests.client import CLIENT_READ, CLIENT_WRITE
from akerbp.mlpet.tests.data.data import FORMATION_DF as FORMATION_DF_WITH_SYSTEMS
from akerbp.mlpet.tests.data.data import (
    FORMATION_TOPS_MAPPER,
    TEST_DF,
    VERTICAL_DEPTHS_MAPPER,
    VERTICAL_DF,
)

ID_COLUMN = "well_name"
VSH_KWARGS = {
    "nan_numerical_value": -9999,
    "nan_textual_value": "MISSING",
    "VSH_curves": ["GR"],
}

FORMATION_DF = FORMATION_DF_WITH_SYSTEMS.drop(columns=["SYSTEM"])
DEPTH_COL = "DEPTH"


def test_add_formations_and_groups_using_mapper():
    df_with_tops = feature_engineering.add_formations_and_groups(
        FORMATION_DF[[DEPTH_COL, ID_COLUMN]],
        formation_tops_mapper=FORMATION_TOPS_MAPPER,
        id_column=ID_COLUMN,
    )
    # Sorting columns because column order is not so important
    assert_frame_equal(df_with_tops.sort_index(axis=1), FORMATION_DF.sort_index(axis=1))


def test_add_formations_and_groups_using_client():
    df_with_tops = feature_engineering.add_formations_and_groups(
        FORMATION_DF[[DEPTH_COL, ID_COLUMN]],
        id_column=ID_COLUMN,
        client=CLIENT_READ,
    )
    assert_frame_equal(df_with_tops.sort_index(axis=1), FORMATION_DF.sort_index(axis=1))


def test_add_formations_and_groups_using_client_with_systems():
    df_with_tops = feature_engineering.add_formations_and_groups(
        FORMATION_DF[[DEPTH_COL, ID_COLUMN]],
        id_column=ID_COLUMN,
        client=CLIENT_READ,
        add_systems=True,
    )
    assert_frame_equal(
        df_with_tops.sort_index(axis=1), FORMATION_DF_WITH_SYSTEMS.sort_index(axis=1)
    )


def test_add_vertical_depths_using_mapper():
    df_with_vertical_depths = feature_engineering.add_vertical_depths(
        VERTICAL_DF[[DEPTH_COL, ID_COLUMN]],
        trajectory_mapping=VERTICAL_DEPTHS_MAPPER,
        id_column=ID_COLUMN,
        md_column=DEPTH_COL,
    )

    assert_frame_equal(
        df_with_vertical_depths.sort_index(axis=1), VERTICAL_DF.sort_index(axis=1)
    )


def test_add_vertical_depths_using_client():
    df_with_vertical_depths = feature_engineering.add_vertical_depths(
        VERTICAL_DF[[DEPTH_COL, ID_COLUMN]],
        id_column=ID_COLUMN,
        md_column=DEPTH_COL,
        client=CLIENT_READ,
    )

    assert_frame_equal(
        df_with_vertical_depths.sort_index(axis=1),
        VERTICAL_DF.sort_index(axis=1),
    )


def test_add_wellbore_coordinates_wrong_trajectory_type_override_with_default():
    df_with_wellbore_coordinates = feature_engineering.add_wellbore_coordinates(
        VERTICAL_DF[[DEPTH_COL, ID_COLUMN]],
        id_column=ID_COLUMN,
        md_column=DEPTH_COL,
        trajectory_type="wrong_trajectory_type",
        client=CLIENT_READ,
    )
    coordinate_columns = ["X", "Y"]
    assertions = [
        col in df_with_wellbore_coordinates.columns for col in coordinate_columns
    ]
    assert len(assertions) == sum(assertions)


def test_add_trajectory_data_wrong_trajectory_type_raise_error():
    with pytest.raises(ValueError, match="Invalid trajectory_type provided!"):
        _ = feature_engineering.add_trajectory_data(
            VERTICAL_DF[[DEPTH_COL, ID_COLUMN]],
            id_column=ID_COLUMN,
            md_column=DEPTH_COL,
            trajectory_type="wrong_trajectory_type",
            client=CLIENT_READ,
        )


def test_add_well_metadata():
    metadata = {"30/11-6 S": {"FOO": 0}, "25/7-4 S": {"FOO": 1}}
    df = feature_engineering.add_well_metadata(
        TEST_DF,
        metadata_dict=metadata,
        metadata_columns=["FOO"],
        id_column=ID_COLUMN,
    )
    assert "FOO" in df.columns.tolist()


def test_add_petrophysical_features_add_VSH_call_CDF_model_return_only_vsh_aut():
    df = TEST_DF.rename(columns={"DENC": "DEN"})
    petrophysical_features = ["VSH"]
    result = feature_engineering.add_petrophysical_features(
        df=df,
        id_column=ID_COLUMN,
        petrophysical_features=petrophysical_features,
        keyword_arguments=VSH_KWARGS,
        client=CLIENT_WRITE,
    )
    output_curves = result.columns
    assert "VSH" in output_curves, "'VSH' not added to dataframe"
