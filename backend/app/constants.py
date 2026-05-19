from enum import StrEnum


class RoleStatus(StrEnum):
    FOUND = "found"
    INTERESTED = "interested"
    APPLIED = "applied"
    ARCHIVED = "archived"


class ApplicationWorkflowState(StrEnum):
    DISCOVERED = "discovered"
    INTERESTED = "interested"
    APPLIED = "applied"
    INTERVIEWING = "interviewing"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    ARCHIVED = "archived"


class WorkspaceStatus(StrEnum):
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    COMPLETED = "completed"


class WorkspaceType(StrEnum):
    FULL_TIME_LEADERSHIP = "full_time_leadership"
    FULL_TIME_INDIVIDUAL_CONTRIBUTOR = "full_time_individual_contributor"
    CONTRACT_CONSULTING = "contract_consulting"
    EXPLORATION = "exploration"
    RELOCATION = "relocation"
    OTHER = "other"


class SourceType(StrEnum):
    MANUAL = "manual"
    LINKEDIN_MANUAL = "linkedin_manual"
    LINKEDIN = "linkedin"
    RECRUITER = "recruiter"
    REFERRAL = "referral"
    COMPANY_SITE = "company_site"
    JOB_BOARD = "job_board"
    NETWORKING = "networking"
    DIRECT_OUTREACH = "direct_outreach"
    INTERNAL_REFERRAL = "internal_referral"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    WORKABLE = "workable"
    OTHER = "other"


SOURCE_DISPLAY_NAMES: dict[SourceType, str] = {
    SourceType.MANUAL: "Manual",
    SourceType.LINKEDIN_MANUAL: "LinkedIn manual",
    SourceType.LINKEDIN: "LinkedIn",
    SourceType.RECRUITER: "Recruiter",
    SourceType.REFERRAL: "Referral",
    SourceType.COMPANY_SITE: "Company site",
    SourceType.JOB_BOARD: "Job board",
    SourceType.NETWORKING: "Networking",
    SourceType.DIRECT_OUTREACH: "Direct outreach",
    SourceType.INTERNAL_REFERRAL: "Internal referral",
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


class StrideRecommendation(StrEnum):
    APPLY = "apply"
    MONITOR = "monitor"
    SKIP = "skip"
    NEEDS_REVIEW = "needs_review"


class StrideConfidenceLevel(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class StrideDimension(StrEnum):
    STRATEGIC_FIT = "strategic_fit"
    TECHNICAL_ALIGNMENT = "technical_alignment"
    SENIORITY_ALIGNMENT = "seniority_alignment"
    COMPENSATION_ALIGNMENT = "compensation_alignment"
    REMOTE_LOCATION_ALIGNMENT = "remote_location_alignment"
    COMPANY_SIGNAL = "company_signal"
    ROLE_CLARITY = "role_clarity"
    APPLICATION_EFFORT = "application_effort"
    ATS_RESUME_ALIGNMENT = "ats_resume_alignment"
    RISK_FLAGS = "risk_flags"


class ResumeSourceType(StrEnum):
    MASTER_RESUME = "master_resume"
    PROFILE = "profile"
    LINKEDIN_EXPORT = "linkedin_export"
    OTHER = "other"
