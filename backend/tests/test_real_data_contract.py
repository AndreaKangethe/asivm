from datetime import datetime

import pytest

from app.modules.vulnerabilities.ingestion.epss import parse_epss_csv
from app.modules.vulnerabilities.ingestion.kev import parse_kev_snapshot
from app.modules.vulnerabilities.ingestion.nvd import parse_nvd_snapshot
from ml.training.dataset_v3 import validate_v3_rows
from app.modules.risk_ml.features import FEATURE_NAMES_V3


def test_public_feed_parsers_preserve_provenance_fields() -> None:
    nvd = parse_nvd_snapshot(
        {
            "vulnerabilities": [
                {
                    "cve": {
                        "id": "CVE-2026-1",
                        "published": "2026-01-01T00:00:00.000Z",
                        "lastModified": "2026-01-02T00:00:00.000Z",
                        "descriptions": [{"lang": "en", "value": "test"}],
                        "metrics": {"cvssMetricV40": [{"type": "Primary", "cvssData": {"baseScore": 9.1}}]},
                    }
                }
            ]
        }
    )
    kev = parse_kev_snapshot({"catalogVersion": "2026.01", "vulnerabilities": [{"cveID": "CVE-2026-1", "dateAdded": "2026-01-03", "dueDate": "2026-02-01", "requiredAction": "patch", "knownRansomwareCampaignUse": "Known"}]})
    epss = parse_epss_csv([{"cve": "CVE-2026-1", "epss": "0", "percentile": "0.01", "date": "2026-01-04", "model_version": "v2026"}])
    assert nvd[0].cvss_version == "4.0"
    assert kev[0].kev_required_action == "patch"
    assert epss[0].epss_score == 0.0
    assert epss[0].epss_percentile == 0.01


def test_v3_dataset_rejects_future_labels_and_duplicate_observations() -> None:
    row = {
        "asset_id": 1,
        "asset_group_id": "server",
        "observed_at": "2026-01-01T00:00:00",
        "label_assessed_at": "2026-01-02T00:00:00",
        "feature_version": "v3",
        "feature_names": list(FEATURE_NAMES_V3),
        "features": [0.0] * len(FEATURE_NAMES_V3),
        "label": 0,
    }
    validate_v3_rows([row])
    with pytest.raises(ValueError):
        validate_v3_rows([row, row.copy()])
    invalid = row.copy()
    invalid["label_assessed_at"] = "2025-12-31T00:00:00"
    with pytest.raises(ValueError):
        validate_v3_rows([invalid])
