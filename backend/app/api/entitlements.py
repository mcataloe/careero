from fastapi import APIRouter

from app.schemas.entitlements import CurrentEntitlementsResponse
from app.services.entitlements import get_current_entitlements

router = APIRouter(prefix="/entitlements", tags=["entitlements"])


@router.get("/current", response_model=CurrentEntitlementsResponse)
def current_entitlements() -> CurrentEntitlementsResponse:
    return get_current_entitlements()
