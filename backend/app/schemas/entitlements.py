from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


BillingStatus = Literal["not_configured"]
PaymentProvider = Literal["none"]


class EntitlementItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    enabled: bool
    category: str
    description: str


class FeatureLimit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    value: int | str | None
    description: str


class CurrentEntitlementsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    plan_id: str
    plan_display_name: str
    billing_status: BillingStatus
    payment_provider: PaymentProvider
    entitlements: list[EntitlementItem]
    feature_limits: list[FeatureLimit]
    unavailable_future_features: list[str]
    monetization_guardrails: list[str]
    local_first_note: str
    metadata: dict[str, Any]
