from pathlib import Path

import joblib
from sklearn.ensemble import GradientBoostingClassifier, IsolationForest

from app.modules.risk_ml.features import FEATURE_VERSION


def train_candidate(features: list[list[float]], labels: list[int], artifact_dir: str, version: str) -> dict:
    if len(features) != len(labels) or not features:
        raise ValueError("features and labels must be non-empty and aligned")
    model = GradientBoostingClassifier(random_state=42).fit(features, labels)
    path = Path(artifact_dir)
    path.mkdir(parents=True, exist_ok=True)
    artifact = path / f"{version}.joblib"
    joblib.dump(model, artifact)
    return {"version": version, "artifact_path": str(artifact), "feature_version": FEATURE_VERSION}


def train_anomaly(features: list[list[float]], artifact_dir: str, version: str) -> str:
    if not features:
        raise ValueError("features must be non-empty")
    model = IsolationForest(random_state=42, contamination="auto").fit(features)
    path = Path(artifact_dir)
    path.mkdir(parents=True, exist_ok=True)
    artifact = path / f"{version}.joblib"
    joblib.dump(model, artifact)
    return str(artifact)
