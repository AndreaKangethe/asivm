from app.core.database import Base, SessionLocal, engine
from app.modules.assets.models import Asset, AssetIdentifier


def main() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(Asset).count():
            return
        asset = Asset(name="lab-host-1")
        db.add(asset)
        db.flush()
        db.add(AssetIdentifier(asset_id=asset.id, identifier_type="hostname", value="lab-host-1"))
        db.commit()


if __name__ == "__main__":
    main()
