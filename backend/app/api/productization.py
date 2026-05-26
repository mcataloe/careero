from fastapi import APIRouter, Depends

from app.config import Settings, get_settings
from app.schemas.productization import ProductizationReadinessResponse
from app.services.productization_readiness import get_productization_readiness

router = APIRouter(prefix="/productization", tags=["productization"])


@router.get("/readiness", response_model=ProductizationReadinessResponse)
def productization_readiness(
    settings: Settings = Depends(get_settings),
) -> ProductizationReadinessResponse:
    return get_productization_readiness(settings)
