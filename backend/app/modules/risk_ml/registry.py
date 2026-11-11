from dataclasses import dataclass
from pathlib import Path

import joblib
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.risk_ml.models import MLModelVersion


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

    def load_active(self, db: Session, name: str) -> LoadedModel:
        record = db.scalar(
            select(MLModelVersion)
            .where(MLModelVersion.name == name, MLModelVersion.is_active.is_(True))
            .order_by(MLModelVersion.id.desc())
        )
        if record is None:
            raise RuntimeError(f"No active {name} model is registered")
        if record.feature_version != "v1":
            raise RuntimeError(f"Model {record.version} uses unsupported feature version {record.feature_version}")
        return self.load(record.version)
