from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.services.source_intelligence import _source_insights, summarize_source_performance


def _role(source_type: str, *, score_id=None):
    return SimpleNamespace(
        id=score_id or uuid4(),
        source=SimpleNamespace(source_type=source_type),
    )


def _application(role, state="applied", recruiter_notes=0):
    return SimpleNamespace(
        role=role,
        role_id=role.id,
        current_state=state,
        applied_at=None,
        interview_stages=[],
        note_entries=[
            SimpleNamespace(deleted_at=None, note_type="recruiter")
            for _ in range(recruiter_notes)
        ],
    )


def _evaluation(score=80, compensation_status="aligned"):
    return SimpleNamespace(
        overall_score=Decimal(str(score)),
        compensation_alignment={"status": compensation_status},
    )


def test_source_intelligence_summarizes_private_source_roi() -> None:
    linkedin_role = _role("linkedin_manual")
    recruiter_role = _role("recruiter")
    roles = [linkedin_role, recruiter_role]
    applications = [
        _application(linkedin_role, state="interviewing", recruiter_notes=1),
        _application(linkedin_role, state="rejected"),
        _application(recruiter_role, state="applied", recruiter_notes=2),
    ]

    summaries = summarize_source_performance(
        roles=roles,
        applications=applications,
        latest_compass={
            linkedin_role.id: _evaluation(82),
            recruiter_role.id: _evaluation(65, "below_target"),
        },
    )

    by_source = {summary["source_type"]: summary for summary in summaries}
    assert by_source["linkedin"]["applications"] == 2
    assert by_source["linkedin"]["responses"] == 1
    assert by_source["linkedin"]["response_rate"] == 0.5
    assert by_source["linkedin"]["average_compass_score"] == 82
    assert by_source["linkedin"]["compensation_aligned"] == 1
    assert by_source["recruiter"]["recruiter_contacts"] == 2
    assert "public recruiter" not in by_source["recruiter"]["basis"].lower()


def test_source_intelligence_normalizes_ats_sources_to_company_site() -> None:
    role = _role("greenhouse")

    summaries = summarize_source_performance(
        roles=[role],
        applications=[_application(role, state="offer")],
        latest_compass={},
    )

    assert summaries[0]["source_type"] == "company_site"
    assert summaries[0]["interview_rate"] == 1


def test_source_intelligence_insights_are_internal_and_source_grounded() -> None:
    summaries = [
        {
            "source_type": "linkedin",
            "label": "LinkedIn",
            "applications": 3,
            "response_rate": 0.667,
        },
        {
            "source_type": "recruiter",
            "label": "Recruiter",
            "applications": 2,
            "response_rate": 0.5,
        },
    ]

    insights = _source_insights(summaries)

    assert len(insights) == 1
    assert insights[0]["category"] == "source_intelligence"
    assert insights[0]["visibility"] == "internal"
    assert insights[0]["freshness"]["generated_at"]
    assert insights[0]["source_inputs"] == {
        "source_type": "linkedin",
        "applications": 3,
        "response_rate": 0.667,
    }
    assert "public recruiter" in insights[0]["basis"]
