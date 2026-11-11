import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

from app.modules.risk_ml.features import FEATURE_NAMES, FEATURE_VERSION


def _validate_row(row: dict, index: int) -> None:
    if not isinstance(row, dict):
        raise ValueError(f"row {index} must be an object")
    if "observed_at" not in row:
        raise ValueError(f"row {index} is missing observed_at")
    if "features" not in row:
        raise ValueError(f"row {index} is missing features")
    try:
        datetime.fromisoformat(row["observed_at"])
    except (TypeError, ValueError) as exc:
        raise ValueError(f"row {index} has an invalid observed_at timestamp") from exc
    features = row["features"]
    if not isinstance(features, list) or len(features) != len(FEATURE_NAMES):
        raise ValueError(
            f"row {index} must contain exactly {len(FEATURE_NAMES)} features for {FEATURE_VERSION}"
        )
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in features):
        raise ValueError(f"row {index} features must be numeric")
    if row.get("feature_version", FEATURE_VERSION) != FEATURE_VERSION:
        raise ValueError(f"row {index} has an unsupported feature version")
    if "feature_names" in row and tuple(row["feature_names"]) != FEATURE_NAMES:
        raise ValueError(f"row {index} feature names do not match the {FEATURE_VERSION} contract")


def build_dataset(source: str, output: str, cutoff: datetime) -> dict:
    rows = json.loads(Path(source).read_text())
    if not isinstance(rows, list):
        raise ValueError("source dataset must be a JSON array")
    for index, row in enumerate(rows):
        _validate_row(row, index)

    selected = [row for row in rows if datetime.fromisoformat(row["observed_at"]) <= cutoff]
    labeled = ["label" in row for row in selected]
    if any(labeled) and not all(labeled):
        raise ValueError("selected rows must either all contain labels or all omit them")
    if all(labeled) and any(not isinstance(row["label"], (int, float)) or isinstance(row["label"], bool) for row in selected):
        raise ValueError("labels must be numeric")

    payload = {
        "feature_version": FEATURE_VERSION,
        "feature_names": list(FEATURE_NAMES),
        "cutoff": cutoff.isoformat(),
        "row_count": len(selected),
        "features": [row["features"] for row in selected],
        "labels": [row["label"] for row in selected] if all(labeled) else [],
    }
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    return {"dataset_version": target.stem, "cutoff": cutoff.isoformat(), "row_count": len(selected), "sha256": digest}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--cutoff", required=True)
    args = parser.parse_args()
    print(json.dumps(build_dataset(args.source, args.output, datetime.fromisoformat(args.cutoff))))


if __name__ == "__main__":
    main()
