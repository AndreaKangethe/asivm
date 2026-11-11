import secrets
from typing import Annotated

from fastapi import Header, HTTPException, status

from app.core.config import get_settings


def require_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    if not x_api_key or not secrets.compare_digest(x_api_key, get_settings().api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
