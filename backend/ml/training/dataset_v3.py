import hashlib
import json
from datetime import datetime
from pathlib import Path

from app.modules.risk_ml.features import FEATURE_NAMES_V3, FEATURE_VERSION_V3


VALID_LABELS = {0, 1, 2}


def _timestamp(value: str, field: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"invalid {field} timestamp") from exc


def validate_v3_rows(rows: list[dict]) -> None:
    seen: set[tuple[object, str]] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"row {index} must be an object")
        for field in ("asset_id", "observed_at", "features", "label", "label_assessed_at"):
            if field not in row:
                raise ValueError(f"row {index} is missing {field}")
        key = (row["asset_id"], row["observed_at"])
        if key in seen:
            raise ValueError(f"duplicate asset observation at row {index}")
        seen.add(key)
        observed_at = _timestamp(row["observed_at"], "observed_at")
        label_at = _timestamp(row["label_assessed_at"], "label_assessed_at")
        if label_at < observed_at:
            raise ValueError(f"row {index} label precedes observation")
        if row.get("feature_version", FEATURE_VERSION_V3) != FEATURE_VERSION_V3:
            raise ValueError(f"row {index} must use {FEATURE_VERSION_V3}")
        if row.get("feature_names", list(FEATURE_NAMES_V3)) != list(FEATURE_NAMES_V3):
            raise ValueError(f"row {index} feature names do not match {FEATURE_VERSION_V3}")
        features = row["features"]
        if isinstance(features, dict):
            if tuple(features) != FEATURE_NAMES_V3:
                raise ValueError(f"row {index} feature mapping order does not match {FEATURE_VERSION_V3}")
            values = [features[name] for name in FEATURE_NAMES_V3]
        else:
            values = features
        if not isinstance(values, list) or len(values) != len(FEATURE_NAMES_V3):
            raise ValueError(f"row {index} must contain {len(FEATURE_NAMES_V3)} features")
        if any(not isinstance(value, (int, float)) or isinstance(value, bool) for value in values):
            raise ValueError(f"row {index} features must be numeric")
        if row["label"] not in VALID_LABELS:
            raise ValueError(f"row {index} label must be LOW=0, MEDIUM=1, or HIGH=2")
        if not row.get("asset_group_id"):
            raise ValueError(f"row {index} is missing asset_group_id")


def build_v3_dataset(source: str, output: str, cutoff: datetime) -> dict:
    rows = json.loads(Path(source).read_text())
    if not isinstance(rows, list):
        raise ValueError("source dataset must be a JSON array")
    eligible = [row for row in rows if _timestamp(row.get("observed_at"), "observed_at") <= cutoff]
    validate_v3_rows(eligible)
    if {row["label"] for row in eligible} != VALID_LABELS:
        raise ValueError("dataset must contain all three risk classes")
    payload = {
        "dataset_version": Path(output).stem,
        "feature_version": FEATURE_VERSION_V3,
        "feature_names": list(FEATURE_NAMES_V3),
        "cutoff": cutoff.isoformat(),
        "row_count": len(eligible),
        "asset_count": len({row["asset_id"] for row in eligible}),
        "rows": eligible,
    }
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2) + "\n")
    return {
        "dataset_version": target.stem,
        "feature_version": FEATURE_VERSION_V3,
        "row_count": len(eligible),
        "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
    }
