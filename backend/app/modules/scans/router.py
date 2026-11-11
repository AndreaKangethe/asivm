from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.auth import require_api_key
from app.core.database import get_db
from app.modules.scans.schemas import ScanRead
from app.modules.scans.service import run_scan

router = APIRouter(prefix="/scans", tags=["scans"], dependencies=[Depends(require_api_key)])


@router.post("", response_model=ScanRead, status_code=201)
@router.post("/run", response_model=ScanRead, status_code=201, include_in_schema=True)
def post_scan(db: Session = Depends(get_db)) -> ScanRead:
    return run_scan(db)
