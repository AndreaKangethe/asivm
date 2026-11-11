from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.assets.models import Asset
from app.modules.assets.schemas import AssetCreate


def create_asset(db: Session, data: AssetCreate) -> Asset:
    asset = Asset(name=data.name)
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


def list_assets(db: Session) -> list[Asset]:
    return list(db.scalars(select(Asset).order_by(Asset.id)))
