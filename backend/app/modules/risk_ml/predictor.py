from app.modules.risk_ml.features import build_feature_vector


def predict_risk(estimator: object, values: dict[str, float]) -> float:
    vector = [build_feature_vector(values)]
    if hasattr(estimator, "predict_proba"):
        return float(estimator.predict_proba(vector)[0][1])
    return float(estimator.predict(vector)[0])


def explain_risk(estimator: object, values: dict[str, float]) -> dict[str, float]:
    try:
        import shap
    except ImportError as exc:
        raise RuntimeError("SHAP is required for explanations") from exc
    explanation = shap.TreeExplainer(estimator)([build_feature_vector(values)])
    values = explanation.values[0]
    if getattr(values, "ndim", 1) > 1:
        values = values[:, -1]
    from app.modules.risk_ml.features import FEATURE_NAMES
    return dict(zip(FEATURE_NAMES, (float(value) for value in values), strict=True))
