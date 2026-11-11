from app.modules.risk_ml.features import (
    FEATURE_NAMES,
    FEATURE_NAMES_V3,
    FEATURE_VERSION,
    FEATURE_VERSION_V3,
    build_feature_vector,
    build_feature_vector_v3,
)


def test_feature_contract_is_stable() -> None:
    assert FEATURE_VERSION == "v1"
    assert len(build_feature_vector({"kev_count": 1, "epss_max": 0.9})) == len(FEATURE_NAMES)
    assert build_feature_vector({"kev_count": 1}) == [1.0, 0.0, 0.0, 0.0]


def test_v3_contract_is_distinct_and_ordered() -> None:
    assert FEATURE_VERSION_V3 == "v3"
    assert len(FEATURE_NAMES_V3) == 20
    assert FEATURE_NAMES_V3[:4] == FEATURE_NAMES
    assert build_feature_vector_v3({"asset_criticality_score": 75})[14] == 75.0
    assert len(build_feature_vector_v3({})) == len(FEATURE_NAMES_V3)
