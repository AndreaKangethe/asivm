from app.modules.risk_ml.features import build_feature_vector
from app.modules.risk_ml.risk_engine import combine_risk
from app.modules.vulnerabilities.ingestion.kev import parse_kev_snapshot
from app.modules.vulnerabilities.ingestion.nvd import parse_nvd_snapshot


def test_feed_parsers_and_risk_context() -> None:
    nvd = parse_nvd_snapshot({"vulnerabilities": [{"cve": {"id": "CVE-2026-1", "descriptions": [{"lang": "en", "value": "test"}]}}]})
    kev = parse_kev_snapshot({"vulnerabilities": [{"cveID": "CVE-2026-1"}]})
    assert nvd[0].cve_id == "CVE-2026-1"
    assert kev[0].is_kev
    assert combine_risk(1.0, cvss_score=10, epss_score=1, is_kev=True) == 1.0
    assert len(build_feature_vector({})) == 4
