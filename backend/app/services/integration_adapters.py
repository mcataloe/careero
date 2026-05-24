from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


IntegrationOperation = Literal["import", "export"]


@dataclass(frozen=True)
class ReviewableIntegrationDraft:
    operation: IntegrationOperation
    adapter_name: str
    target_type: str
    target_id: str | None
    payload: dict[str, Any]
    provenance: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    requires_review: bool = True


class LocalIntegrationAdapter:
    """Base boundary for local-first integrations that never mutate externally."""

    adapter_name = "local"

    def build_draft(
        self,
        *,
        operation: IntegrationOperation,
        target_type: str,
        target_id: str | None,
        payload: dict[str, Any],
        provenance: dict[str, Any] | None = None,
        warnings: list[str] | None = None,
    ) -> ReviewableIntegrationDraft:
        return ReviewableIntegrationDraft(
            operation=operation,
            adapter_name=self.adapter_name,
            target_type=target_type,
            target_id=target_id,
            payload=payload,
            provenance=provenance or {},
            warnings=warnings or [],
        )
