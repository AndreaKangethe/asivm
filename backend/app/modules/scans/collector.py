from datetime import datetime

from app.modules.assets.schemas import ObservationData


def collect() -> list[ObservationData]:
    return [
        ObservationData(
            identifier_type="hostname",
            identifier_value="lab-host-1",
            observed_at=datetime.utcnow(),
        )
    ]
