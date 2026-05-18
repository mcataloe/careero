from types import SimpleNamespace

from app.services.artifact_performance import summarize_artifact_records


def _record(
    *,
    artifact_type: str = "tailored_resume",
    variant_name: str = "Platform Resume",
    role_category: str = "infrastructure",
    response: str | None = "pending",
    interview: str | None = "none_recorded",
):
    return SimpleNamespace(
        artifact_type=artifact_type,
        variant_name=variant_name,
        targeted_role_category=role_category,
        response_outcome=response,
        interview_outcome=interview,
    )


def test_artifact_performance_summarizes_variant_rates_without_causation() -> None:
    records = [
        _record(response="positive_response", interview="interview_received"),
        _record(response="positive_response", interview="interview_received"),
        _record(response="pending", interview="none_recorded"),
        _record(variant_name="Leadership Resume", role_category="leadership"),
    ]

    summary = summarize_artifact_records(records)

    platform = next(
        metric
        for metric in summary["by_variant"]
        if metric["label"] == "tailored_resume: Platform Resume"
    )
    assert platform["total"] == 3
    assert platform["responses"] == 2
    assert platform["response_rate"] == 0.6667
    assert summary["insights"][0]["basis"].endswith("correlation, not proof.")


def test_artifact_performance_reports_insufficient_data() -> None:
    summary = summarize_artifact_records([_record(response="pending")])

    assert summary["summary"][0]["total"] == 1
    assert summary["summary"][0]["response_rate"] == 0
    assert "at least three recorded uses" in summary["insufficient_data"][0]
    assert "No positive response outcomes" in summary["insufficient_data"][1]
