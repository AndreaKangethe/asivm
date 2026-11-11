import argparse
import json

from joblib import load

from app.modules.risk_ml.retraining import evaluate_candidate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--dataset", required=True)
    args = parser.parse_args()
    model = load(args.artifact)
    data = json.loads(open(args.dataset).read())
    print(json.dumps({"roc_auc": evaluate_candidate(model, data["features"], data["labels"])}))


if __name__ == "__main__":
    main()
