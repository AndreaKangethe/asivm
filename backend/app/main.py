from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import Base, engine
from app.core.logging import configure_logging
from app.modules.assets import models as _asset_models
from app.modules.assets.router import router as assets_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    Base.metadata.create_all(bind=engine)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="ASIVM", version="0.1.0", lifespan=lifespan)
    app.include_router(assets_router)
    return app


app = create_app()
