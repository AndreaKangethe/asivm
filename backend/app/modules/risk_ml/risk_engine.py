from app.modules.risk_ml.predictor import predict_risk


def combine_risk(model_score: float, *, cvss_score: float | None, epss_score: float | None, is_kev: bool) -> float:
    context = 0.0
    if cvss_score is not None:
        context += cvss_score / 10 * 0.2
    if epss_score is not None:
        context += epss_score * 0.2
    if is_kev:
        context += 0.2
    return min(1.0, max(0.0, model_score * 0.4 + context))


def assess(estimator: object, features: dict[str, float], *, cvss_score: float | None = None,
           epss_score: float | None = None, is_kev: bool = False) -> float:
    return combine_risk(
        predict_risk(estimator, features),
        cvss_score=cvss_score,
        epss_score=epss_score,
        is_kev=is_kev,
    )
