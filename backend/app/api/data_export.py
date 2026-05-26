from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.database import get_db
from app.schemas.data_export import LocalDataExportResponse
from app.services.data_export import DataExportSeedMissingError, LocalDataExportService

router = APIRouter(prefix="/data-export", tags=["data-export"])


def get_local_data_export_service(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> LocalDataExportService:
    return LocalDataExportService(db, settings=settings)


@router.get("/local", response_model=LocalDataExportResponse)
def export_local_data(
    service: LocalDataExportService = Depends(get_local_data_export_service),
) -> LocalDataExportResponse:
    try:
        return service.build_export()
    except DataExportSeedMissingError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
