import json
import random
from pathlib import Path

import numpy as np

SEED = 42


def seed_everything() -> None:
    random.seed(SEED)
    np.random.seed(SEED)


def write_metadata(path: str, metadata: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(metadata, indent=2) + "\n")
