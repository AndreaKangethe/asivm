from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.modules.assets.models import Asset, AssetIdentifier
from app.modules.assets.schemas import ObservationData

IDENTIFIER_PRIORITY = ("mac", "hostname", "fqdn", "ip")

def _active_identifier(db: Session, identifier_type: str, value: str, observed_at: datetime) -> AssetIdentifier | None:
    return db.scalar(
        select(AssetIdentifier)
        .where(
            and_(
                AssetIdentifier.identifier_type == identifier_type,
                AssetIdentifier.value == value,
                AssetIdentifier.valid_from <= observed_at,
                or_(AssetIdentifier.valid_to.is_(None), AssetIdentifier.valid_to >= observed_at),
            )
        )
        .order_by(AssetIdentifier.valid_from.desc())
    )


def _asset_name(observation: ObservationData) -> str:
    return observation.asset_name or observation.identifiers.get("hostname") or observation.identifiers.get("fqdn") or observation.identifiers.get("ip") or next(iter(observation.identifiers.values()))


def _upsert_identifier(db: Session, asset: Asset, identifier_type: str, value: str, observed_at: datetime) -> None:
    current = db.scalar(
        select(AssetIdentifier)
        .where(
            AssetIdentifier.asset_id == asset.id,
            AssetIdentifier.identifier_type == identifier_type,
            AssetIdentifier.valid_to.is_(None),
        )
        .order_by(AssetIdentifier.valid_from.desc())
    )
    if current and current.value == value:
        return
    if current:
        current.valid_to = observed_at
    db.add(
        AssetIdentifier(
            asset_id=asset.id,
            identifier_type=identifier_type,
            value=value,
            valid_from=observed_at,
        )
    )


def resolve_observation(db: Session, observation: ObservationData) -> Asset:
    for identifier_type in IDENTIFIER_PRIORITY:
        value = observation.identifiers.get(identifier_type)
        if value:
            identifier = _active_identifier(db, identifier_type, value, observation.observed_at)
            if identifier:
                asset = db.get(Asset, identifier.asset_id)
                break
    else:
        asset = Asset(name=_asset_name(observation))
        db.add(asset)
        db.flush()

    for identifier_type, value in observation.identifiers.items():
        _upsert_identifier(db, asset, identifier_type, value, observation.observed_at)
    db.flush()
    return asset
