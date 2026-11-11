FEATURE_VERSION = "v1"
FEATURE_NAMES = ("kev_count", "epss_max", "asset_age_days", "observation_change_count")

def build_feature_vector(values: dict[str, float]) -> list[float]:
    return [float(values.get(name, 0.0)) for name in FEATURE_NAMES]
