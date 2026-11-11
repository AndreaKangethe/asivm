from app.modules.risk_ml.features import build_feature_vector


def predict_risk(estimator: object, values: dict[str, float]) -> float:
    vector = [build_feature_vector(values)]
    if hasattr(estimator, "predict_proba"):
        return float(estimator.predict_proba(vector)[0][1])
    return float(estimator.predict(vector)[0])
