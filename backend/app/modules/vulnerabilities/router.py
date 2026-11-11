from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import require_api_key
from app.core.database import get_db
from app.modules.vulnerabilities.schemas import VulnerabilityRead, VulnerabilityUpsert
from app.modules.vulnerabilities.service import list_vulnerabilities, upsert_vulnerability

router = APIRouter(prefix="/vulnerabilities", tags=["vulnerabilities"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=VulnerabilityRead, status_code=201)
def post_vulnerability(data: VulnerabilityUpsert, db: Session = Depends(get_db)) -> VulnerabilityRead:
    return upsert_vulnerability(db, data)


@router.get("", response_model=list[VulnerabilityRead])
def get_vulnerabilities(db: Session = Depends(get_db)) -> list[VulnerabilityRead]:
    return list_vulnerabilities(db)
