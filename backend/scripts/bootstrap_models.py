from app.modules.risk_ml.retraining import train_anomaly, train_candidate


def main() -> None:
    features = [[0.1, 0.2, 10, 1], [0.8, 0.9, 100, 8], [0.2, 0.1, 20, 0], [0.9, 0.8, 200, 10]]
    train_candidate(features, [0, 1, 0, 1], "ml/artifacts", "risk-initial")
    train_anomaly(features, "ml/artifacts", "anomaly-initial")


if __name__ == "__main__":
    main()
