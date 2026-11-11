from datetime import datetime

from app.modules.assets.schemas import ObservationData

_scan_number = 0

def collect() -> list[ObservationData]:
    global _scan_number
    _scan_number += 1
    services = ["ssh", "http"] if _scan_number == 1 else ["ssh", "http", "admin-api"]
    return [
        ObservationData(
            identifiers={"hostname": "lab-host-1", "ip": "10.0.0.5"},
            observed_at=datetime.utcnow(),
            metadata={"ports": [22, 80, 8443] if _scan_number > 1 else [22, 80], "services": services},
        )
    ]
