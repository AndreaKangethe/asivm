from app.modules.risk_ml.features import FEATURE_NAMES, FEATURE_VERSION, build_feature_vector


def test_feature_contract_is_stable() -> None:
    assert FEATURE_VERSION == "v1"
    assert len(build_feature_vector({"kev_count": 1, "epss_max": 0.9})) == len(FEATURE_NAMES)
    assert build_feature_vector({"kev_count": 1}) == [1.0, 0.0, 0.0, 0.0]
