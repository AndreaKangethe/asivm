from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import require_api_key
from app.core.database import get_db
from app.modules.risk_ml.inference import infer_all
from app.modules.risk_ml.models import AnomalyEvent, MLModelVersion, RiskAssessment
from app.modules.risk_ml.schemas import AnomalyRead, RiskAssessmentRead

router = APIRouter(prefix="/risk", tags=["risk"], dependencies=[Depends(require_api_key)])


class TriageUpdate(BaseModel):
    reviewed_by: str
    review_note: str | None = None
    status: str = "triaged"


@router.get("/assessments", response_model=list[RiskAssessmentRead])
def get_assessments(db: Session = Depends(get_db)) -> list[RiskAssessment]:
    return list(db.scalars(select(RiskAssessment).order_by(RiskAssessment.assessed_at.desc())))


@router.get("/anomalies", response_model=list[AnomalyRead])
def get_anomalies(db: Session = Depends(get_db)) -> list[AnomalyEvent]:
    return list(db.scalars(select(AnomalyEvent).order_by(AnomalyEvent.detected_at.desc())))


@router.patch("/anomalies/{event_id}/triage", response_model=AnomalyRead)
def triage_anomaly(event_id: int, data: TriageUpdate, db: Session = Depends(get_db)) -> AnomalyEvent:
    if data.status not in {"triaged", "closed"}:
        raise HTTPException(status_code=422, detail="status must be triaged or closed")
    event = db.get(AnomalyEvent, event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Anomaly not found")
    event.status = data.status
    event.reviewed_by = data.reviewed_by
    event.reviewed_at = datetime.utcnow()
    event.review_note = data.review_note
    db.commit()
    db.refresh(event)
    return event


@router.post("/infer")
def infer(db: Session = Depends(get_db)) -> dict[str, int]:
    return {"assessments_created": infer_all(db)}


@router.get("/models")
def get_models(db: Session = Depends(get_db)) -> list[dict[str, object]]:
    return [
        {
            "name": item.name,
            "version": item.version,
            "feature_version": item.feature_version,
            "is_active": item.is_active,
            "metrics": item.metrics,
        }
        for item in db.scalars(select(MLModelVersion).order_by(MLModelVersion.name, MLModelVersion.version))
    ]
