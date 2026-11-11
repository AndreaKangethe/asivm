from dataclasses import dataclass
from pathlib import Path

import joblib
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.risk_ml.features import FEATURE_NAMES, FEATURE_NAMES_V3
from app.modules.risk_ml.models import MLModelVersion


FEATURE_NAMES_BY_VERSION = {
    "v1": FEATURE_NAMES,
    "v2": (),
    "v3": FEATURE_NAMES_V3,
}
SUPPORTED_FEATURE_VERSIONS = frozenset(FEATURE_NAMES_BY_VERSION)


@dataclass(frozen=True)
class LoadedModel:
    version: str
    estimator: object


class ModelRegistry:
    def __init__(self, artifact_path: str):
        self.artifact_path = Path(artifact_path)
        self._models: dict[str, LoadedModel] = {}

    def load(self, version: str) -> LoadedModel:
        if version not in self._models:
            path = self.artifact_path / f"{version}.joblib"
            if not path.is_file():
                raise FileNotFoundError(f"Model artifact not found: {path}")
            self._models[version] = LoadedModel(version, joblib.load(path))
        return self._models[version]

    def load_active(self, db: Session, name: str, feature_version: str | None = None) -> LoadedModel:
        query = select(MLModelVersion).where(
            MLModelVersion.name == name,
            MLModelVersion.is_active.is_(True),
        )
        if feature_version is not None:
            query = query.where(MLModelVersion.feature_version == feature_version)
        record = db.scalar(query.order_by(MLModelVersion.id.desc()))
        if record is None:
            requested = f" with feature version {feature_version}" if feature_version else ""
            raise RuntimeError(f"No active {name} model{requested} is registered")
        if record.feature_version not in SUPPORTED_FEATURE_VERSIONS:
            raise RuntimeError(f"Model {record.version} uses unsupported feature version {record.feature_version}")
        expected_names = FEATURE_NAMES_BY_VERSION[record.feature_version]
        if expected_names and record.feature_names and tuple(record.feature_names) != expected_names:
            raise RuntimeError(f"Model {record.version} does not match the {record.feature_version} feature contract")
        return self.load(record.version)
