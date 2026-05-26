import logging

from fastapi import FastAPI, Response, status

from app.api.activity_log import router as activity_log_router
from app.api.advisor_packets import router as advisor_packets_router
from app.api.automation import router as automation_router
from app.api.artifact_exports import router as artifact_exports_router
from app.api.artifact_performance import router as artifact_performance_router
from app.api.applications import router as applications_router
from app.api.compensation_intelligence import router as compensation_intelligence_router
from app.api.cover_letter_artifacts import router as cover_letter_artifacts_router
from app.api.historical_learning import router as historical_learning_router
from app.api.opportunities import router as opportunities_router
from app.api.recommendations import router as recommendations_router
from app.api.resume_sources import router as resume_sources_router
from app.api.resume_artifacts import router as resume_artifacts_router
from app.api.roles import router as roles_router
from app.api.search_analytics import router as search_analytics_router
from app.api.search_health import router as search_health_router
from app.api.source_intelligence import router as source_intelligence_router
from app.api.strategy import router as strategy_router
from app.api.compass_insights import router as compass_insights_router
from app.api.compass_evaluations import router as compass_evaluations_router
from app.api.workspaces import router as workspaces_router
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
    app.include_router(advisor_packets_router, prefix="/api")
    app.include_router(automation_router, prefix="/api")
    app.include_router(artifact_exports_router, prefix="/api")
    app.include_router(artifact_performance_router, prefix="/api")
    app.include_router(applications_router, prefix="/api")
    app.include_router(compensation_intelligence_router, prefix="/api")
    app.include_router(cover_letter_artifacts_router, prefix="/api")
    app.include_router(historical_learning_router, prefix="/api")
    app.include_router(opportunities_router, prefix="/api")
    app.include_router(recommendations_router, prefix="/api")
    app.include_router(resume_sources_router, prefix="/api")
    app.include_router(resume_artifacts_router, prefix="/api")
    app.include_router(roles_router, prefix="/api")
    app.include_router(search_analytics_router, prefix="/api")
    app.include_router(search_health_router, prefix="/api")
    app.include_router(source_intelligence_router, prefix="/api")
    app.include_router(strategy_router, prefix="/api")
    app.include_router(compass_insights_router, prefix="/api")
    app.include_router(compass_evaluations_router, prefix="/api")
    app.include_router(workspaces_router, prefix="/api")

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
