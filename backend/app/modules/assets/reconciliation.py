from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.modules.assets.models import Asset, AssetIdentifier
from app.modules.assets.schemas import ObservationData


def resolve_observation(db: Session, observation: ObservationData) -> Asset | None:
    identifier = db.scalar(
        select(AssetIdentifier)
        .where(
            and_(
                AssetIdentifier.identifier_type == observation.identifier_type,
                AssetIdentifier.value == observation.identifier_value,
                AssetIdentifier.valid_from <= observation.observed_at,
                or_(
                    AssetIdentifier.valid_to.is_(None),
                    AssetIdentifier.valid_to >= observation.observed_at,
                ),
            )
        )
        .order_by(AssetIdentifier.valid_from.desc())
    )
    return db.get(Asset, identifier.asset_id) if identifier else None
