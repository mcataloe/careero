from typing import Any

from pydantic import BaseModel, ConfigDict


class DataExportMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: str
    generated_at: str
    readiness_note: str
    current_user: dict[str, Any]
    derived_data_notes: list[str]


class LocalDataExportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    metadata: DataExportMetadata
    workspaces: list[dict[str, Any]]
    companies: list[dict[str, Any]]
    job_sources: list[dict[str, Any]]
    opportunities: list[dict[str, Any]]
    resume_sources: list[dict[str, Any]]
    resume_source_versions: list[dict[str, Any]]
    compass_evaluations: list[dict[str, Any]]
    generated_artifacts: list[dict[str, Any]]
    artifact_performance_records: list[dict[str, Any]]
    applications: list[dict[str, Any]]
    application_state_history: list[dict[str, Any]]
    notes: list[dict[str, Any]]
    reminders: list[dict[str, Any]]
    external_links: list[dict[str, Any]]
    interview_stages: list[dict[str, Any]]
    activity_logs: list[dict[str, Any]]
    account_lifecycle_requests: list[dict[str, Any]]
    ai_usage_events: list[dict[str, Any]]
    automation_suggestions: list[dict[str, Any]]
    automation_approval_logs: list[dict[str, Any]]
