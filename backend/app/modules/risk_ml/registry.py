from dataclasses import dataclass
from pathlib import Path

import joblib
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.risk_ml.features import FEATURE_NAMES, FEATURE_NAMES_V2, FEATURE_NAMES_V3
from app.modules.risk_ml.models import MLModelVersion, ModelLifecycleEvent


FEATURE_NAMES_BY_VERSION = {
    "v1": FEATURE_NAMES,
    "v2": FEATURE_NAMES_V2,
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
        self._validate_contract(record)
        return self.load(record.version)

    @staticmethod
    def _validate_contract(record: MLModelVersion) -> None:
        if record.feature_version not in SUPPORTED_FEATURE_VERSIONS:
            raise RuntimeError(f"Model {record.version} uses unsupported feature version {record.feature_version}")
        expected_names = FEATURE_NAMES_BY_VERSION[record.feature_version]
        if record.feature_names and tuple(record.feature_names) != expected_names:
            raise RuntimeError(f"Model {record.version} does not match the {record.feature_version} feature contract")

    def register_shadow(
        self,
        db: Session,
        *,
        name: str,
        version: str,
        artifact_path: str,
        feature_version: str,
        metrics: dict,
        training_metadata: dict,
        contract_hash: str | None = None,
        actor: str = "training-job",
    ) -> MLModelVersion:
        if feature_version not in SUPPORTED_FEATURE_VERSIONS:
            raise ValueError(f"unsupported feature version: {feature_version}")
        if db.scalar(select(MLModelVersion).where(MLModelVersion.version == version)) is not None:
            raise ValueError(f"model version already registered: {version}")
        record = MLModelVersion(
            name=name,
            version=version,
            artifact_path=artifact_path,
            feature_version=feature_version,
            feature_names=list(FEATURE_NAMES_BY_VERSION[feature_version]),
            contract_hash=contract_hash,
            training_metadata=training_metadata,
            metrics=metrics,
            deployment_mode="shadow",
            is_active=False,
        )
        db.add(record)
        db.flush()
        db.add(ModelLifecycleEvent(model_version_id=record.id, event_type="registered_shadow", actor=actor, details=metrics))
        db.commit()
        db.refresh(record)
        return record

    def promote(self, db: Session, version: str, actor: str = "operator") -> MLModelVersion:
        candidate = db.scalar(select(MLModelVersion).where(MLModelVersion.version == version))
        if candidate is None:
            raise ValueError(f"unknown model version: {version}")
        self._validate_contract(candidate)
        if candidate.deployment_mode != "shadow":
            raise ValueError("only shadow candidates can be explicitly promoted")
        retired = []
        for active in db.scalars(
            select(MLModelVersion).where(
                MLModelVersion.name == candidate.name,
                MLModelVersion.feature_version == candidate.feature_version,
                MLModelVersion.is_active.is_(True),
            )
        ):
            active.is_active = False
            active.deployment_mode = "retired"
            retired.append(active.version)
        candidate.is_active = True
        candidate.deployment_mode = "active"
        db.add(
            ModelLifecycleEvent(
                model_version_id=candidate.id,
                event_type="promoted",
                actor=actor,
                details={"retired_versions": retired},
            )
        )
        db.commit()
        db.refresh(candidate)
        return candidate
