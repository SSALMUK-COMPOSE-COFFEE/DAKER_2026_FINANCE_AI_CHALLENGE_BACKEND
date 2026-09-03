from fastapi import APIRouter

from app.config import get_settings
from app.services.db import check_connection

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.app_name,
        "database": await check_connection(),
    }
