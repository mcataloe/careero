from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models import (
    Application,
    ApplicationExternalLink,
    ApplicationInterviewStage,
    ApplicationNote,
    GeneratedArtifact,
    Role,
    User,
)
from app.seed import DEFAULT_LOCAL_USER_ID


PACKET_VERSION = "advisor_packet.local_preview.v1"
ADVISORY_NOTICE = (
    "Local-only owner preview. Nothing is externally shared, no advisor account "
    "exists, and private strategy is redacted by default."
)


class AdvisorPacketError(Exception):
    pass


class AdvisorPacketNotFoundError(AdvisorPacketError):
    pass


class AdvisorPacketSeedMissingError(AdvisorPacketError):
    pass


@dataclass(frozen=True)
class AdvisorPacketExportResult:
    content: bytes
    media_type: str
    file_name: str
    content_hash: str


class AdvisorPacketService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_default_user(self) -> User:
        user = self.db.get(User, DEFAULT_LOCAL_USER_ID)
        if user is None or user.deleted_at is not None:
            raise AdvisorPacketSeedMissingError(
                "Default local user is missing; run python -m app.seed"
            )
        return user

    def get_application_packet(self, application_id: uuid.UUID) -> dict[str, Any]:
        user = self.get_default_user()
        application = self._get_application(application_id=application_id, user_id=user.id)
        if application is None:
            raise AdvisorPacketNotFoundError("Application workflow not found")

        return _packet_response(application=application, artifacts=self._artifacts(application))

    def export_application_packet_markdown(
        self,
        application_id: uuid.UUID,
    ) -> AdvisorPacketExportResult:
        packet = self.get_application_packet(application_id)
        content = _render_markdown(packet).encode("utf-8")
        content_hash = f"sha256:{hashlib.sha256(content).hexdigest()}"
        title = packet["opportunity"]["title"]
        return AdvisorPacketExportResult(
            content=content,
            media_type="text/markdown; charset=utf-8",
            file_name=f"{_slug(title)}-advisor-packet.md",
            content_hash=content_hash,
        )

    def _get_application(
        self,
        *,
        application_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Application | None:
        return self.db.scalar(
            select(Application)
            .where(
                Application.id == application_id,
                Application.user_id == user_id,
                Application.deleted_at.is_(None),
            )
            .options(
                joinedload(Application.role).joinedload(Role.company),
                selectinload(Application.note_entries),
                selectinload(Application.reminders),
                selectinload(Application.interview_stages),
                selectinload(Application.external_links),
            )
        )

    def _artifacts(self, application: Application) -> list[GeneratedArtifact]:
        return list(
            self.db.scalars(
                select(GeneratedArtifact)
                .where(
                    GeneratedArtifact.user_id == application.user_id,
                    GeneratedArtifact.workspace_id == application.workspace_id,
                    GeneratedArtifact.role_id == application.role_id,
                    GeneratedArtifact.deleted_at.is_(None),
                    GeneratedArtifact.artifact_type.in_(
                        ["tailored_resume", "cover_letter"]
                    ),
                )
                .order_by(GeneratedArtifact.updated_at.desc(), GeneratedArtifact.id.desc())
            )
        )


def _packet_response(
    *,
    application: Application,
    artifacts: list[GeneratedArtifact],
) -> dict[str, Any]:
    role = application.role
    active_notes = _active_notes(application)
    active_interviews = _active_interviews(application)
    active_links = _active_links(application)
    return {
        "packet_version": PACKET_VERSION,
        "mode": "local_preview",
        "generated_at": datetime.now(timezone.utc),
        "local_only": True,
        "external_sharing_enabled": False,
        "advisory_notice": ADVISORY_NOTICE,
        "opportunity": {
            "id": role.id,
            "workspace_id": role.workspace_id,
            "title": role.title,
            "company_name": role.company.name,
            "status": role.status,
            "location": role.location,
            "remote_type": role.remote_type,
        },
        "application": {
            "id": application.id,
            "current_state": application.current_state,
            "applied_at": application.applied_at,
            "next_action_at": application.next_action_at,
            "counts": {
                "notes": len(active_notes),
                "reminders": len(application.reminders),
                "interviews": len(active_interviews),
                "external_links": len(active_links),
            },
        },
        "artifacts": [_artifact_summary(artifact) for artifact in artifacts],
        "redactions": _redactions(
            notes_count=len(active_notes),
            links_count=len(active_links),
            interviews_count=len(active_interviews),
        ),
        "warnings": [
            {
                "code": "local_only_preview",
                "message": (
                    "This packet is a local preview/export only. It does not create "
                    "hosted access, invitations, accounts, public links, comments, "
                    "or external sharing."
                ),
            },
            {
                "code": "redacted_by_default",
                "message": (
                    "Private notes, compensation strategy, STRIDE rationale, ATS "
                    "risk notes, recruiter intelligence, raw sources, and artifact "
                    "content are excluded by default."
                ),
            },
        ],
    }


def _artifact_summary(artifact: GeneratedArtifact) -> dict[str, Any]:
    contract = (
        artifact.artifact_metadata.get("contract")
        if artifact.artifact_metadata
        else None
    )
    revision = contract.get("revision", {}) if isinstance(contract, dict) else {}
    lifecycle_status = (
        contract.get("lifecycleStatus") if isinstance(contract, dict) else None
    )
    warnings = [
        {
            "code": "artifact_content_excluded",
            "message": (
                "Artifact content is not included in the default advisor packet. "
                "Only lifecycle summary metadata is shown."
            ),
        }
    ]
    if lifecycle_status != "approved":
        warnings.append(
            {
                "code": "artifact_not_approved",
                "message": (
                    "Generated artifact lifecycle is not approved; keep draft and "
                    "truthfulness warnings visible before any future sharing flow."
                ),
            }
        )
    return {
        "id": artifact.id,
        "artifact_type": artifact.artifact_type,
        "title": artifact.title,
        "lifecycle_status": lifecycle_status,
        "revision_number": revision.get("revisionNumber"),
        "content_included": False,
        "updated_at": artifact.updated_at,
        "warnings": warnings,
    }


def _redactions(
    *,
    notes_count: int,
    links_count: int,
    interviews_count: int,
) -> list[dict[str, str]]:
    return [
        {
            "data_class": "Raw job description",
            "default_visibility": "Private",
            "status": "excluded",
            "reason": "Raw source material is for grounding and is not advisor-visible by default.",
        },
        {
            "data_class": "STRIDE score and explanation",
            "default_visibility": "Private by default",
            "status": "excluded",
            "reason": "Internal fit analysis remains advisory, source-grounded, and private by default.",
        },
        {
            "data_class": "ATS risk notes",
            "default_visibility": "Private by default",
            "status": "excluded",
            "reason": "ATS risk notes are internal strategy and are not employer- or advisor-visible by default.",
        },
        {
            "data_class": "Compensation targets and strategy",
            "default_visibility": "Private by default",
            "status": "excluded",
            "reason": "Negotiation-sensitive compensation data is excluded from default packets.",
        },
        {
            "data_class": "Private user notes",
            "default_visibility": "Private by default",
            "status": "excluded",
            "reason": f"{notes_count} note(s) exist and require explicit future selection before inclusion.",
        },
        {
            "data_class": "Recruiter/source/contact metadata",
            "default_visibility": "Private by default",
            "status": "excluded",
            "reason": "Recruiter and contact intelligence is excluded by default.",
        },
        {
            "data_class": "Interview notes",
            "default_visibility": "Private by default",
            "status": "summary_only" if interviews_count else "excluded",
            "reason": f"{interviews_count} interview stage(s) are counted, but notes and names are redacted.",
        },
        {
            "data_class": "External links",
            "default_visibility": "Packet-eligible if selected",
            "status": "excluded",
            "reason": f"{links_count} link(s) exist and require explicit future selection before inclusion.",
        },
        {
            "data_class": "Generated artifact content",
            "default_visibility": "Packet-eligible if selected",
            "status": "excluded",
            "reason": "Only artifact lifecycle summaries are included in this default packet preview.",
        },
        {
            "data_class": "Career strategy synthesis",
            "default_visibility": "Private by default",
            "status": "excluded",
            "reason": "Strategy synthesis is internal, advisory, source-derived, and private by default.",
        },
        {
            "data_class": "Activity and automation approval logs",
            "default_visibility": "Private by default",
            "status": "excluded",
            "reason": "Audit and automation records are not shareable packet content by default.",
        },
    ]


def _render_markdown(packet: dict[str, Any]) -> str:
    opportunity = packet["opportunity"]
    application = packet["application"]
    lines = [
        f"# Advisor Packet Preview: {opportunity['title']}",
        "",
        packet["advisory_notice"],
        "",
        "## Opportunity Summary",
        "",
        f"- Company: {opportunity['company_name']}",
        f"- Status: {opportunity['status']}",
        f"- Location: {_display(opportunity.get('location'))}",
        f"- Remote type: {_display(opportunity.get('remote_type'))}",
        "",
        "## Application Summary",
        "",
        f"- Current state: {application['current_state']}",
        f"- Applied at: {_display(application.get('applied_at'))}",
        f"- Next action at: {_display(application.get('next_action_at'))}",
        f"- Notes count: {application['counts'].get('notes', 0)}",
        f"- Reminders count: {application['counts'].get('reminders', 0)}",
        f"- Interviews count: {application['counts'].get('interviews', 0)}",
        "",
        "## Artifact Summaries",
        "",
    ]
    artifacts = packet.get("artifacts") or []
    if artifacts:
        for artifact in artifacts:
            lines.extend(
                [
                    f"- {artifact['title']} ({artifact['artifact_type']})",
                    f"  - Lifecycle status: {_display(artifact.get('lifecycle_status'))}",
                    f"  - Revision: {_display(artifact.get('revision_number'))}",
                    "  - Content included: no",
                ]
            )
    else:
        lines.append("- No generated resume or cover-letter artifacts found.")
    lines.extend(["", "## Redactions", ""])
    for redaction in packet.get("redactions") or []:
        lines.append(
            f"- {redaction['data_class']}: {redaction['status']} - {redaction['reason']}"
        )
    lines.extend(["", "## Warnings", ""])
    for warning in packet.get("warnings") or []:
        lines.append(f"- {warning['message']}")
    lines.append("")
    return "\n".join(lines)


def _display(value: Any) -> str:
    if value is None:
        return "Not included"
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    return str(value)


def _slug(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return slug or "careero"


def _active_notes(application: Application) -> list[ApplicationNote]:
    return [note for note in application.note_entries if note.deleted_at is None]


def _active_interviews(application: Application) -> list[ApplicationInterviewStage]:
    return [stage for stage in application.interview_stages if stage.deleted_at is None]


def _active_links(application: Application) -> list[ApplicationExternalLink]:
    return [link for link in application.external_links if link.deleted_at is None]
