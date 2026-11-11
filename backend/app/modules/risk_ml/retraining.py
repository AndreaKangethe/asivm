from pathlib import Path

import joblib
from sklearn.metrics import roc_auc_score
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


def evaluate_candidate(estimator: object, features: list[list[float]], labels: list[int]) -> float:
    if hasattr(estimator, "predict_proba"):
        return float(roc_auc_score(labels, estimator.predict_proba(features)[:, 1]))
    raise ValueError("candidate does not expose probability predictions")


def promote_candidate(candidate_score: float, active_score: float | None, minimum_score: float = 0.6) -> bool:
    return candidate_score >= minimum_score and (active_score is None or candidate_score > active_score)
