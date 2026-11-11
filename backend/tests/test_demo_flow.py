from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.database import Base
from app.modules.assets.models import Asset, AssetIdentifier
from app.modules.risk_ml.models import AnomalyEvent, RiskAssessment
from app.modules.scans.service import run_scan
from app.modules.vulnerabilities.models import AssetVulnerability, VulnerabilityCatalog


def test_scan_creates_demo_risk_and_anomaly() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        asset = Asset(name="lab-host-1")
        db.add(asset)
        db.flush()
        db.add(AssetIdentifier(asset_id=asset.id, identifier_type="hostname", value="lab-host-1"))
        vuln = VulnerabilityCatalog(cve_id="CVE-2026-0001", cvss_score=8, epss_score=0.7, is_kev=True)
        db.add(vuln)
        db.flush()
        db.add(AssetVulnerability(asset_id=asset.id, vulnerability_id=vuln.id, evidence={}))
        db.commit()
        run_scan(db)
        run_scan(db)
        assert db.query(RiskAssessment).count() == 2
        assert db.query(AnomalyEvent).count() == 1
