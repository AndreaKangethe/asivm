import argparse
import hashlib
import json
from datetime import datetime
from pathlib import Path

from app.modules.risk_ml.features import FEATURE_VERSION


def build_dataset(source: str, output: str, cutoff: datetime) -> dict:
    rows = json.loads(Path(source).read_text())
    selected = [row for row in rows if datetime.fromisoformat(row["observed_at"]) <= cutoff]
    payload = {
        "feature_version": FEATURE_VERSION,
        "cutoff": cutoff.isoformat(),
        "row_count": len(selected),
        "features": [row["features"] for row in selected],
        "labels": [row["label"] for row in selected if "label" in row],
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
