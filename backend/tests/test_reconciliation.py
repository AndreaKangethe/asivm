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


def test_new_ip_with_known_hostname_reuses_asset_and_closes_old_interval() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    observed_at = datetime(2026, 1, 2)
    with Session(engine) as db:
        asset = Asset(name="lab-host-2")
        db.add(asset)
        db.flush()
        db.add(
            AssetIdentifier(
                asset_id=asset.id,
                identifier_type="hostname",
                value="lab-host-2",
                valid_from=observed_at - timedelta(days=2),
            )
        )
        db.add(
            AssetIdentifier(
                asset_id=asset.id,
                identifier_type="ip",
                value="10.0.0.8",
                valid_from=observed_at - timedelta(days=2),
            )
        )
        db.commit()
        result = resolve_observation(
            db,
            ObservationData(
                identifiers={"hostname": "lab-host-2", "ip": "10.0.0.9"},
                observed_at=observed_at,
            ),
        )
        db.commit()
        identifiers = db.query(AssetIdentifier).filter_by(asset_id=asset.id).all()
        assert result.id == asset.id
        assert any(item.identifier_type == "ip" and item.value == "10.0.0.9" for item in identifiers)
        old_ip = next(item for item in identifiers if item.value == "10.0.0.8")
        assert old_ip.valid_to == observed_at
