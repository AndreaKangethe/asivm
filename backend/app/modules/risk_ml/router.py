from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_api_key
from app.core.database import get_db
from app.modules.risk_ml.models import AnomalyEvent, RiskAssessment
from app.modules.risk_ml.schemas import AnomalyRead, RiskAssessmentRead

router = APIRouter(prefix="/risk", tags=["risk"], dependencies=[Depends(require_api_key)])


@router.get("/assessments", response_model=list[RiskAssessmentRead])
def get_assessments(db: Session = Depends(get_db)) -> list[RiskAssessment]:
    return list(db.scalars(select(RiskAssessment).order_by(RiskAssessment.assessed_at.desc())))


@router.get("/anomalies", response_model=list[AnomalyRead])
def get_anomalies(db: Session = Depends(get_db)) -> list[AnomalyEvent]:
    return list(db.scalars(select(AnomalyEvent).order_by(AnomalyEvent.detected_at.desc())))


@router.patch("/anomalies/{event_id}/triage", response_model=AnomalyRead)
def triage_anomaly(event_id: int, db: Session = Depends(get_db)) -> AnomalyEvent:
    event = db.get(AnomalyEvent, event_id)
    if event is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Anomaly not found")
    event.status = "triaged"
    db.commit()
    db.refresh(event)
    return event
