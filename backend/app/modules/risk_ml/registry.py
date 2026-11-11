from dataclasses import dataclass
from pathlib import Path

import joblib


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
