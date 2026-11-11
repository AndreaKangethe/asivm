def detect_anomaly(estimator: object, values: dict[str, float]) -> float:
    vector = [[float(value) for value in values.values()]]
    return float(estimator.decision_function(vector)[0])
