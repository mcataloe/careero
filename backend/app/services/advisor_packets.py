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
    ApplicationReminder,
    GeneratedArtifact,
    Role,
    User,
)
from app.schemas.advisor_packets import AdvisorPacketIncludeOptions
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

    def get_application_packet(
        self,
        application_id: uuid.UUID,
        include_options: AdvisorPacketIncludeOptions | None = None,
    ) -> dict[str, Any]:
        user = self.get_default_user()
        application = self._get_application(application_id=application_id, user_id=user.id)
        if application is None:
            raise AdvisorPacketNotFoundError("Application workflow not found")

        return _packet_response(
            application=application,
            artifacts=self._artifacts(application),
            include_options=include_options or AdvisorPacketIncludeOptions(),
        )

    def export_application_packet_markdown(
        self,
        application_id: uuid.UUID,
        include_options: AdvisorPacketIncludeOptions | None = None,
    ) -> AdvisorPacketExportResult:
        packet = self.get_application_packet(application_id, include_options)
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
    include_options: AdvisorPacketIncludeOptions,
) -> dict[str, Any]:
    role = application.role
    active_notes = _active_notes(application)
    active_interviews = _active_interviews(application)
    active_links = _active_links(application)
    active_reminders = list(application.reminders)
    selected_artifact_ids = set(include_options.artifact_ids)
    selected_link_ids = set(include_options.external_link_ids)
    selected_interview_ids = set(include_options.interview_stage_ids)
    selected_reminder_ids = set(include_options.reminder_ids)
    selected_links = [link for link in active_links if link.id in selected_link_ids]
    selected_interviews = [
        interview for interview in active_interviews if interview.id in selected_interview_ids
    ]
    selected_reminders = [
        reminder for reminder in active_reminders if reminder.id in selected_reminder_ids
    ]
    advisor_context = _trim_context(include_options.advisor_context)
    artifact_summaries = [
        _artifact_summary(
            artifact,
            include_content=artifact.id in selected_artifact_ids,
        )
        for artifact in artifacts
    ]
    warnings = _warnings(
        artifacts=artifact_summaries,
        selected_link_count=len(selected_links),
        selected_interview_count=len(selected_interviews),
        selected_reminder_count=len(selected_reminders),
        advisor_context=advisor_context,
    )
    return {
        "packet_version": PACKET_VERSION,
        "mode": "local_preview",
        "generated_at": datetime.now(timezone.utc),
        "local_only": True,
        "external_sharing_enabled": False,
        "advisory_notice": ADVISORY_NOTICE,
        "include_options": {
            "artifact_ids": list(include_options.artifact_ids),
            "external_link_ids": list(include_options.external_link_ids),
            "interview_stage_ids": list(include_options.interview_stage_ids),
            "reminder_ids": list(include_options.reminder_ids),
            "advisor_context": advisor_context,
        },
        "sections": _sections(
            artifact_count=len(artifacts),
            artifact_content_count=sum(
                1 for artifact in artifact_summaries if artifact["content_included"]
            ),
            link_count=len(selected_links),
            interview_count=len(selected_interviews),
            reminder_count=len(selected_reminders),
            advisor_context=advisor_context,
        ),
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
        "artifacts": artifact_summaries,
        "selected_external_links": [_link_summary(link) for link in selected_links],
        "selected_interviews": [
            _interview_summary(interview) for interview in selected_interviews
        ],
        "selected_reminders": [
            _reminder_summary(reminder) for reminder in selected_reminders
        ],
        "advisor_context": advisor_context,
        "redactions": _redactions(
            notes_count=len(active_notes),
            links_count=len(active_links),
            interviews_count=len(active_interviews),
            reminders_count=len(active_reminders),
            selected_artifact_content_count=sum(
                1 for artifact in artifact_summaries if artifact["content_included"]
            ),
            selected_links_count=len(selected_links),
            selected_interviews_count=len(selected_interviews),
            selected_reminders_count=len(selected_reminders),
            advisor_context_included=advisor_context is not None,
        ),
        "warnings": warnings,
    }


def _artifact_summary(
    artifact: GeneratedArtifact,
    *,
    include_content: bool,
) -> dict[str, Any]:
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
            "code": (
                "artifact_content_included"
                if include_content
                else "artifact_content_excluded"
            ),
            "message": (
                "Artifact content was explicitly selected for this local-only "
                "preview. Keep lifecycle and truthfulness warnings attached."
                if include_content
                else (
                    "Artifact content is not included in the default advisor packet. "
                    "Only lifecycle summary metadata is shown."
                )
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
        "content_included": include_content,
        "content": artifact.content if include_content else None,
        "updated_at": artifact.updated_at,
        "warnings": warnings,
    }


def _link_summary(link: ApplicationExternalLink) -> dict[str, Any]:
    return {
        "id": link.id,
        "label": link.label,
        "url": link.url,
        "link_type": link.link_type,
        "warning": (
            "This link was explicitly selected for local preview. Verify it does "
            "not expose private portals, tracking URLs, or account-specific access."
        ),
    }


def _interview_summary(interview: ApplicationInterviewStage) -> dict[str, Any]:
    return {
        "id": interview.id,
        "title": interview.title,
        "stage_type": interview.stage_type,
        "status": interview.status,
        "scheduled_at": interview.scheduled_at,
        "completed_at": interview.completed_at,
        "notes_included": True,
        "notes": interview.notes,
        "preparation_notes": interview.preparation_notes,
        "outcome_notes": interview.outcome_notes,
        "warning": (
            "Interview notes were explicitly selected for local preview. "
            "Interviewer names and meeting links remain redacted."
        ),
    }


def _reminder_summary(reminder: ApplicationReminder) -> dict[str, Any]:
    return {
        "id": reminder.id,
        "title": reminder.title,
        "due_at": reminder.due_at,
        "completed_at": reminder.completed_at,
        "notes_included": reminder.notes is not None,
        "notes": reminder.notes,
        "warning": (
            "Reminder details were explicitly selected for local preview. Confirm "
            "the text does not reveal private deadlines or pressure points."
        ),
    }


def _sections(
    *,
    artifact_count: int,
    artifact_content_count: int,
    link_count: int,
    interview_count: int,
    reminder_count: int,
    advisor_context: str | None,
) -> list[dict[str, Any]]:
    return [
        {
            "key": "opportunity_summary",
            "title": "Opportunity summary",
            "status": "included",
            "item_count": 1,
            "warnings": [],
        },
        {
            "key": "application_summary",
            "title": "Application summary",
            "status": "included",
            "item_count": 1,
            "warnings": [],
        },
        {
            "key": "artifact_summaries",
            "title": "Artifact summaries",
            "status": "summary_only" if artifact_count else "excluded",
            "item_count": artifact_count,
            "warnings": [
                {
                    "code": "artifact_lifecycle_warning",
                    "message": (
                        "Generated artifacts must keep lifecycle, source-grounding, "
                        "and truthfulness warnings visible."
                    ),
                }
            ],
        },
        {
            "key": "selected_artifact_content",
            "title": "Selected artifact content",
            "status": "included" if artifact_content_count else "excluded",
            "item_count": artifact_content_count,
            "warnings": [
                {
                    "code": "explicit_selection_required",
                    "message": "Artifact content is excluded unless explicitly selected.",
                }
            ],
        },
        {
            "key": "selected_external_links",
            "title": "Selected external links",
            "status": "included" if link_count else "excluded",
            "item_count": link_count,
            "warnings": [
                {
                    "code": "link_exposure_warning",
                    "message": (
                        "Links can expose private portals, tracking URLs, or account "
                        "context; include only reviewed links."
                    ),
                }
            ],
        },
        {
            "key": "selected_interview_notes",
            "title": "Selected interview notes",
            "status": "included" if interview_count else "excluded",
            "item_count": interview_count,
            "warnings": [
                {
                    "code": "interview_note_redaction_warning",
                    "message": (
                        "Interview notes are excluded by default and interviewer names "
                        "and meeting links remain redacted."
                    ),
                }
            ],
        },
        {
            "key": "selected_reminders",
            "title": "Selected reminders",
            "status": "included" if reminder_count else "excluded",
            "item_count": reminder_count,
            "warnings": [
                {
                    "code": "reminder_privacy_warning",
                    "message": "Reminders are excluded unless explicitly selected.",
                }
            ],
        },
        {
            "key": "advisor_context",
            "title": "Advisor context",
            "status": "included" if advisor_context else "excluded",
            "item_count": 1 if advisor_context else 0,
            "warnings": [
                {
                    "code": "user_authored_context",
                    "message": (
                        "Advisor context is user-authored for this local preview and "
                        "is not persisted as a collaborator record."
                    ),
                }
            ],
        },
    ]


def _warnings(
    *,
    artifacts: list[dict[str, Any]],
    selected_link_count: int,
    selected_interview_count: int,
    selected_reminder_count: int,
    advisor_context: str | None,
) -> list[dict[str, str]]:
    warnings = [
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
                "Private notes, compensation strategy, COMPASS rationale, ATS "
                "risk notes, recruiter intelligence, raw sources, and automation "
                "logs are excluded by default."
            ),
        },
        {
            "code": "truthguard_source_grounding",
            "message": (
                "Generated artifacts remain draft/local records and must retain "
                "TruthGuard and source-grounding warnings."
            ),
        },
    ]
    if any(artifact["content_included"] for artifact in artifacts):
        warnings.append(
            {
                "code": "artifact_content_explicitly_selected",
                "message": (
                    "Artifact content appears only because it was explicitly selected "
                    "for this local preview."
                ),
            }
        )
    if selected_link_count:
        warnings.append(
            {
                "code": "external_links_explicitly_selected",
                "message": "External links appear only because they were explicitly selected.",
            }
        )
    if selected_interview_count:
        warnings.append(
            {
                "code": "interview_notes_explicitly_selected",
                "message": "Interview notes appear only because they were explicitly selected.",
            }
        )
    if selected_reminder_count:
        warnings.append(
            {
                "code": "reminders_explicitly_selected",
                "message": "Reminders appear only because they were explicitly selected.",
            }
        )
    if advisor_context:
        warnings.append(
            {
                "code": "advisor_context_user_authored",
                "message": (
                    "Advisor context is user-authored local preview text and is not "
                    "stored as a collaborator note."
                ),
            }
        )
    return warnings


def _redactions(
    *,
    notes_count: int,
    links_count: int,
    interviews_count: int,
    reminders_count: int,
    selected_artifact_content_count: int,
    selected_links_count: int,
    selected_interviews_count: int,
    selected_reminders_count: int,
    advisor_context_included: bool,
) -> list[dict[str, Any]]:
    return [
        {
            "data_class": "Raw job description",
            "field": "opportunity.raw_description",
            "default_visibility": "Private",
            "status": "excluded",
            "included": False,
            "reason": "Raw source material is for grounding and is not advisor-visible by default.",
            "warning": "Raw opportunity source text can leak proprietary posting details.",
        },
        {
            "data_class": "COMPASS score and explanation",
            "field": "compass_evaluation",
            "default_visibility": "Private by default",
            "status": "excluded",
            "included": False,
            "reason": "Internal fit analysis remains advisory, source-grounded, and private by default.",
            "warning": "COMPASS is advisory, not deterministic truth.",
        },
        {
            "data_class": "ATS risk notes",
            "field": "compass_evaluation.ats",
            "default_visibility": "Private by default",
            "status": "excluded",
            "included": False,
            "reason": "ATS risk notes are internal strategy and are not employer- or advisor-visible by default.",
            "warning": "ATS notes must not become employer-facing material.",
        },
        {
            "data_class": "Compensation targets and strategy",
            "field": "opportunity.compensation",
            "default_visibility": "Private by default",
            "status": "excluded",
            "included": False,
            "reason": "Negotiation-sensitive compensation data is excluded from default packets.",
            "warning": "Compensation information can weaken negotiation posture if exposed.",
        },
        {
            "data_class": "Private user notes",
            "field": "application_notes.body",
            "default_visibility": "Private by default",
            "status": "excluded",
            "included": False,
            "reason": f"{notes_count} note(s) exist and require explicit future selection before inclusion.",
            "warning": "Private notes are not advisor comments and remain separate.",
        },
        {
            "data_class": "Recruiter/source/contact metadata",
            "field": "role.source_id",
            "default_visibility": "Private by default",
            "status": "excluded",
            "included": False,
            "reason": "Recruiter and contact intelligence is excluded by default.",
            "warning": "Source and contact metadata can reveal private search channels.",
        },
        {
            "data_class": "Interview notes",
            "field": "application_interview_stages.notes",
            "default_visibility": "Private by default",
            "status": "included" if selected_interviews_count else "excluded",
            "included": selected_interviews_count > 0,
            "reason": (
                f"{selected_interviews_count} of {interviews_count} interview "
                "stage(s) explicitly selected; names and meeting links remain redacted."
            ),
            "warning": "Interview notes can contain sensitive impressions and preparation strategy.",
        },
        {
            "data_class": "External links",
            "field": "application_external_links.url",
            "default_visibility": "Packet-eligible if selected",
            "status": "included" if selected_links_count else "excluded",
            "included": selected_links_count > 0,
            "reason": (
                f"{selected_links_count} of {links_count} link(s) explicitly "
                "selected for this local preview."
            ),
            "warning": "Links can expose private portals, tracking URLs, or account context.",
        },
        {
            "data_class": "Generated artifact content",
            "field": "generated_artifacts.content",
            "default_visibility": "Packet-eligible if selected",
            "status": "included" if selected_artifact_content_count else "excluded",
            "included": selected_artifact_content_count > 0,
            "reason": (
                f"{selected_artifact_content_count} artifact(s) explicitly selected "
                "for content inclusion; lifecycle summaries remain visible."
            ),
            "warning": "Generated artifacts need lifecycle, TruthGuard, and source-grounding warnings.",
        },
        {
            "data_class": "Reminders",
            "field": "application_reminders",
            "default_visibility": "Private by default",
            "status": "included" if selected_reminders_count else "excluded",
            "included": selected_reminders_count > 0,
            "reason": (
                f"{selected_reminders_count} of {reminders_count} reminder(s) "
                "explicitly selected for this local preview."
            ),
            "warning": "Reminder text can expose private deadlines or pressure points.",
        },
        {
            "data_class": "User-authored advisor context",
            "field": "advisor_context",
            "default_visibility": "Packet-eligible if user-authored",
            "status": "included" if advisor_context_included else "excluded",
            "included": advisor_context_included,
            "reason": (
                "User-authored context is included only for this local preview."
                if advisor_context_included
                else "No advisor context was provided for this local preview."
            ),
            "warning": "This context is not persisted as a collaborator record.",
        },
        {
            "data_class": "Career strategy synthesis",
            "field": "strategy",
            "default_visibility": "Private by default",
            "status": "excluded",
            "included": False,
            "reason": "Strategy synthesis is internal, advisory, source-derived, and private by default.",
            "warning": "Strategy synthesis can reveal private decision rationale.",
        },
        {
            "data_class": "Activity and automation approval logs",
            "field": "activity_log.automation",
            "default_visibility": "Private by default",
            "status": "excluded",
            "included": False,
            "reason": "Audit and automation records are not shareable packet content by default.",
            "warning": "Automation logs remain internal audit records.",
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
                    f"  - Content included: {'yes' if artifact.get('content_included') else 'no'}",
                ]
            )
            if artifact.get("content_included") and artifact.get("content"):
                lines.extend(
                    [
                        "",
                        f"### {artifact['title']} content",
                        "",
                        str(artifact["content"]),
                        "",
                    ]
                )
    else:
        lines.append("- No generated resume or cover-letter artifacts found.")
    if packet.get("selected_external_links"):
        lines.extend(["", "## Selected External Links", ""])
        for link in packet["selected_external_links"]:
            lines.append(f"- {link['label']}: {link['url']}")
    if packet.get("selected_interviews"):
        lines.extend(["", "## Selected Interview Notes", ""])
        for interview in packet["selected_interviews"]:
            lines.append(f"- {interview['title']} ({interview['status']})")
            for key in ("notes", "preparation_notes", "outcome_notes"):
                if interview.get(key):
                    lines.append(f"  - {key.replace('_', ' ').title()}: {interview[key]}")
    if packet.get("selected_reminders"):
        lines.extend(["", "## Selected Reminders", ""])
        for reminder in packet["selected_reminders"]:
            lines.append(f"- {reminder['title']} due {_display(reminder.get('due_at'))}")
            if reminder.get("notes"):
                lines.append(f"  - Notes: {reminder['notes']}")
    if packet.get("advisor_context"):
        lines.extend(["", "## Advisor Context", "", str(packet["advisor_context"])])
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


def _trim_context(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    if not normalized:
        return None
    return normalized[:4000]


def _active_notes(application: Application) -> list[ApplicationNote]:
    return [note for note in application.note_entries if note.deleted_at is None]


def _active_interviews(application: Application) -> list[ApplicationInterviewStage]:
    return [stage for stage in application.interview_stages if stage.deleted_at is None]


def _active_links(application: Application) -> list[ApplicationExternalLink]:
    return [link for link in application.external_links if link.deleted_at is None]
