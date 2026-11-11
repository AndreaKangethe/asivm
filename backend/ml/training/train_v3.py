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
    if "train_rows" not in dataset or "test_rows" not in dataset:
        raise ValueError("dataset must provide chronological train_rows and test_rows")
    train_rows = dataset["train_rows"]
    test_rows = dataset["test_rows"]
    result = train_multiclass_candidate(
        [row["features"] for row in train_rows],
        [row["label"] for row in train_rows],
        args.artifacts,
        args.version,
    )
    import joblib

    estimator = joblib.load(result["artifact_path"])
    result["test_metrics"] = evaluate_multiclass_candidate(
        estimator,
        [row["features"] for row in test_rows],
        [row["label"] for row in test_rows],
    )
    result["deployment_mode"] = "shadow"
    print(json.dumps(result))


if __name__ == "__main__":
    main()
