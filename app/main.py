from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import analysis, documents, evidence, health, intake, personas, reference, uploads


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version="0.2.0")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Disposition"],
    )

    api = APIRouter(prefix="/api")
    api.include_router(health.router)
    api.include_router(reference.router)
    api.include_router(intake.router)
    api.include_router(evidence.router)
    api.include_router(uploads.router)
    api.include_router(analysis.router)
    api.include_router(documents.router)
    api.include_router(personas.router)
    application.include_router(api)

    return application


app = create_app()
