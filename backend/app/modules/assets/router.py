from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.assets.schemas import AssetCreate, AssetRead
from app.modules.assets.service import create_asset, list_assets

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("", response_model=AssetRead, status_code=201)
def post_asset(data: AssetCreate, db: Session = Depends(get_db)) -> AssetRead:
    return create_asset(db, data)


@router.get("", response_model=list[AssetRead])
def get_assets(db: Session = Depends(get_db)) -> list[AssetRead]:
    return list_assets(db)
