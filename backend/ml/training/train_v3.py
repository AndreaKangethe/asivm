import argparse
import json
from pathlib import Path

from app.modules.risk_ml.retraining import evaluate_multiclass_candidate, train_multiclass_candidate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--artifacts", default="ml/artifacts")
    parser.add_argument("--version", required=True)
    args = parser.parse_args()

    dataset = json.loads(Path(args.dataset).read_text())
    rows = dataset["rows"]
    features = [row["features"] for row in rows]
    labels = [row["label"] for row in rows]
    result = train_multiclass_candidate(features, labels, args.artifacts, args.version)
    estimator = __import__("joblib").load(result["artifact_path"])
    result["metrics_on_training_data"] = evaluate_multiclass_candidate(estimator, features, labels)
    result["deployment_mode"] = "shadow"
    print(json.dumps(result))


if __name__ == "__main__":
    main()
