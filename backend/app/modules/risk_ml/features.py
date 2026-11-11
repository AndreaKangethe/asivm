from collections.abc import Mapping


FEATURE_VERSION = "v1"
FEATURE_NAMES = ("kev_count", "epss_max", "asset_age_days", "observation_change_count")

FEATURE_VERSION_V3 = "v3"
FEATURE_NAMES_V3 = (
    "kev_count",
    "epss_max",
    "asset_age_days",
    "observation_change_count",
    "cvss_max",
    "vulnerability_count",
    "critical_vulnerability_count",
    "open_port_count",
    "new_port_count",
    "service_count",
    "new_service_count",
    "ip_change_count",
    "hostname_change_count",
    "vulnerability_change_count",
    "asset_criticality_score",
    "business_impact_score",
    "internet_exposed",
    "externally_reachable_port_count",
    "externally_reachable_service_count",
    "identity_confidence",
)


def build_feature_vector(values: Mapping[str, float]) -> list[float]:
    return [float(values.get(name, 0.0)) for name in FEATURE_NAMES]


def build_feature_vector_v3(values: Mapping[str, float]) -> list[float]:
    return [float(values.get(name, 0.0)) for name in FEATURE_NAMES_V3]
