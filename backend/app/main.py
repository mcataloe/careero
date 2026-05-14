import logging

from fastapi import FastAPI, Response, status

from app.api.activity_log import router as activity_log_router
from app.api.resume_sources import router as resume_sources_router
from app.api.resume_artifacts import router as resume_artifacts_router
from app.api.roles import router as roles_router
from app.api.stride_evaluations import router as stride_evaluations_router
from app.config import Settings, get_settings
from app.database import check_database
from app.logging import configure_logging

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        description="Local-first API foundation for Careero.",
        version="0.1.0",
    )
    app.include_router(activity_log_router, prefix="/api")
    app.include_router(resume_sources_router, prefix="/api")
    app.include_router(resume_artifacts_router, prefix="/api")
    app.include_router(roles_router, prefix="/api")
    app.include_router(stride_evaluations_router, prefix="/api")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "app_name": settings.app_name,
            "environment": settings.environment,
        }

    @app.get("/health/database")
    def database_health(response: Response) -> dict[str, str]:
        try:
            check_database(settings)
        except Exception as exc:
            logger.warning(
                "Database health check failed: %s",
                type(exc).__name__,
            )
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {
                "status": "unhealthy",
                "database": "unavailable",
            }

        return {
            "status": "ok",
            "database": "available",
        }

    return app


app = create_app()
