from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.modules.assets.models import Asset, AssetIdentifier
from app.modules.assets.reconciliation import resolve_observation
from app.modules.assets.schemas import ObservationData


def test_ip_change_resolves_to_same_asset() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    observed_at = datetime(2026, 1, 2)
    with Session(engine) as db:
        asset = Asset(name="lab-host-1")
        db.add(asset)
        db.flush()
        db.add_all(
            [
                AssetIdentifier(
                    asset_id=asset.id,
                    identifier_type="ip",
                    value="10.0.0.1",
                    valid_from=observed_at - timedelta(days=2),
                    valid_to=observed_at - timedelta(days=1),
                ),
                AssetIdentifier(
                    asset_id=asset.id,
                    identifier_type="ip",
                    value="10.0.0.2",
                    valid_from=observed_at - timedelta(days=1),
                ),
            ]
        )
        db.commit()
        result = resolve_observation(
            db,
            ObservationData(
                identifier_type="ip",
                identifier_value="10.0.0.2",
                observed_at=observed_at,
            ),
        )
        assert result is not None
        assert result.id == asset.id
