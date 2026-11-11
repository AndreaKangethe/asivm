from app.core.database import Base, SessionLocal, engine
from app.modules.assets.models import Asset, AssetIdentifier
from app.modules.scans import models as _scan_models
from app.modules.risk_ml import models as _risk_models
from app.modules.vulnerabilities.models import AssetVulnerability, VulnerabilityCatalog


def main() -> None:
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        if db.query(Asset).count():
            return
        asset = Asset(name="lab-host-1")
        db.add(asset)
        db.flush()
        db.add(AssetIdentifier(asset_id=asset.id, identifier_type="hostname", value="lab-host-1"))
        vulnerability = VulnerabilityCatalog(
            cve_id="CVE-2026-0001",
            description="Demonstration vulnerability for the ASIVM prototype",
            cvss_score=8.1,
            epss_score=0.72,
            is_kev=True,
        )
        db.add(vulnerability)
        db.flush()
        db.add(AssetVulnerability(asset_id=asset.id, vulnerability_id=vulnerability.id, evidence={"source": "demo"}))
        db.commit()


if __name__ == "__main__":
    main()
