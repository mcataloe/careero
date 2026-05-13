from enum import StrEnum


class RoleStatus(StrEnum):
    FOUND = "found"
    INTERESTED = "interested"
    APPLIED = "applied"
    ARCHIVED = "archived"


class SourceType(StrEnum):
    MANUAL = "manual"
    LINKEDIN_MANUAL = "linkedin_manual"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    WORKABLE = "workable"
    OTHER = "other"


SOURCE_DISPLAY_NAMES: dict[SourceType, str] = {
    SourceType.MANUAL: "Manual",
    SourceType.LINKEDIN_MANUAL: "LinkedIn manual",
    SourceType.GREENHOUSE: "Greenhouse",
    SourceType.LEVER: "Lever",
    SourceType.ASHBY: "Ashby",
    SourceType.WORKABLE: "Workable",
    SourceType.OTHER: "Other",
}


class StrideEvaluationStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
