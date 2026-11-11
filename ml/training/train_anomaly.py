import argparse
import json

from app.modules.risk_ml.retraining import train_anomaly


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--artifacts", default="ml/artifacts")
    parser.add_argument("--version", required=True)
    args = parser.parse_args()
    data = json.loads(open(args.dataset).read())
    print(train_anomaly(data["features"], args.artifacts, args.version))


if __name__ == "__main__":
    main()
