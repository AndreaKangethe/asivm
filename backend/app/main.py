from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.core.database import SessionLocal
from app.core.logging import configure_logging
from app.modules.assets import models as _asset_models
from app.modules.assets.router import router as assets_router
from app.modules.scans import models as _scan_models
from app.modules.scans.router import router as scans_router
from app.modules.vulnerabilities import models as _vulnerability_models
from app.modules.vulnerabilities.router import router as vulnerabilities_router
from app.modules.risk_ml import models as _risk_models
from app.modules.risk_ml.router import router as risk_router
from app.modules.risk_ml.scheduler import create_scheduler
from app.modules.scans.service import run_scan


def scheduled_scan() -> None:
    with SessionLocal() as db:
        run_scan(db)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    Base.metadata.create_all(bind=engine)
    scheduler = create_scheduler(scheduled_scan)
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


def create_app() -> FastAPI:
    app = FastAPI(title="ASIVM", version="0.1.0", lifespan=lifespan)
    app.include_router(assets_router)
    app.include_router(scans_router)
    app.include_router(vulnerabilities_router)
    app.include_router(risk_router)
    return app


app = create_app()
