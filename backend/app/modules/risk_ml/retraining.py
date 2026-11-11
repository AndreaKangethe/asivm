from pathlib import Path

import joblib
from sklearn.ensemble import GradientBoostingClassifier, IsolationForest
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
    roc_auc_score,
)

from app.modules.risk_ml.features import FEATURE_VERSION, FEATURE_VERSION_V3


def train_candidate(features: list[list[float]], labels: list[int], artifact_dir: str, version: str) -> dict:
    if len(features) != len(labels) or not features:
        raise ValueError("features and labels must be non-empty and aligned")
    model = GradientBoostingClassifier(random_state=42).fit(features, labels)
    path = Path(artifact_dir)
    path.mkdir(parents=True, exist_ok=True)
    artifact = path / f"{version}.joblib"
    joblib.dump(model, artifact)
    return {"version": version, "artifact_path": str(artifact), "feature_version": FEATURE_VERSION}


def train_multiclass_candidate(
    features: list[list[float]],
    labels: list[int],
    artifact_dir: str,
    version: str,
) -> dict:
    if len(features) != len(labels) or not features:
        raise ValueError("features and labels must be non-empty and aligned")
    if set(labels) != {0, 1, 2}:
        raise ValueError("real v3 training requires LOW, MEDIUM, and HIGH labels")
    model = GradientBoostingClassifier(random_state=42).fit(features, labels)
    path = Path(artifact_dir)
    path.mkdir(parents=True, exist_ok=True)
    artifact = path / f"{version}.joblib"
    joblib.dump(model, artifact)
    return {
        "version": version,
        "artifact_path": str(artifact),
        "feature_version": FEATURE_VERSION_V3,
        "classes": sorted(set(labels)),
    }


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
        probabilities = estimator.predict_proba(features)
        if probabilities.shape[1] == 2:
            return float(roc_auc_score(labels, probabilities[:, 1]))
        return float(roc_auc_score(labels, probabilities, multi_class="ovr", labels=estimator.classes_))
    raise ValueError("candidate does not expose probability predictions")


def evaluate_multiclass_candidate(estimator: object, features: list[list[float]], labels: list[int]) -> dict:
    if not hasattr(estimator, "predict_proba"):
        raise ValueError("candidate does not expose probability predictions")
    predictions = estimator.predict(features)
    probabilities = estimator.predict_proba(features)
    precision, recall, f1, support = precision_recall_fscore_support(
        labels, predictions, labels=[0, 1, 2], zero_division=0
    )
    metrics = {
        "accuracy": float(accuracy_score(labels, predictions)),
        "macro_f1": float(f1_score(labels, predictions, average="macro", zero_division=0)),
        "confusion_matrix": confusion_matrix(labels, predictions, labels=[0, 1, 2]).tolist(),
        "per_class": {
            str(label): {
                "precision": float(precision[index]),
                "recall": float(recall[index]),
                "f1": float(f1[index]),
                "support": int(support[index]),
            }
            for index, label in enumerate([0, 1, 2])
        },
    }
    try:
        metrics["roc_auc_ovr"] = float(roc_auc_score(labels, probabilities, multi_class="ovr", labels=[0, 1, 2]))
        metrics["pr_auc_macro"] = float(
            average_precision_score(
                [[1 if value == label else 0 for label in [0, 1, 2]] for value in labels],
                probabilities,
                average="macro",
            )
        )
    except ValueError:
        metrics["roc_auc_ovr"] = None
        metrics["pr_auc_macro"] = None
    return metrics


def promote_candidate(candidate_score: float, active_score: float | None, minimum_score: float = 0.6) -> bool:
    return candidate_score >= minimum_score and (active_score is None or candidate_score > active_score)
