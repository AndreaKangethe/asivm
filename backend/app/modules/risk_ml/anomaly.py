from app.modules.risk_ml.features import build_feature_vector, FEATURE_NAMES


def detect_anomaly(estimator: object, values: dict[str, float]) -> float:
    return float(estimator.decision_function([build_feature_vector(values)])[0])


def explain_anomaly(values: dict[str, float], score: float) -> dict[str, float]:
    return {name: float(values.get(name, 0.0)) for name in FEATURE_NAMES if values.get(name, 0.0)}
