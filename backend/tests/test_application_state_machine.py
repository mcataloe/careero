import pytest

from app.constants import ApplicationWorkflowState
from app.services.application_state_machine import (
    can_transition,
    get_available_transitions,
)


@pytest.mark.parametrize(
    ("from_state", "to_state"),
    [
        ("discovered", "interested"),
        ("discovered", "withdrawn"),
        ("discovered", "archived"),
        ("interested", "applied"),
        ("interested", "withdrawn"),
        ("interested", "archived"),
        ("applied", "interviewing"),
        ("applied", "rejected"),
        ("applied", "withdrawn"),
        ("applied", "archived"),
        ("interviewing", "offer"),
        ("interviewing", "rejected"),
        ("interviewing", "withdrawn"),
        ("interviewing", "archived"),
        ("offer", "withdrawn"),
        ("offer", "archived"),
        ("rejected", "archived"),
        ("withdrawn", "archived"),
    ],
)
def test_allows_canonical_transitions(from_state: str, to_state: str) -> None:
    assert can_transition(from_state, to_state)


def test_rejects_non_canonical_transitions() -> None:
    assert not can_transition("discovered", "offer")
    assert not can_transition("rejected", "interviewing")
    assert not can_transition("withdrawn", "applied")


def test_same_state_transition_is_idempotent() -> None:
    assert can_transition("applied", "applied")


def test_reactivation_requires_explicit_flag() -> None:
    assert not can_transition("archived", "interested")
    assert can_transition("archived", "interested", reactivate=True)
    assert can_transition("archived", "discovered", reactivate=True)
    assert not can_transition("archived", "applied", reactivate=True)


def test_available_transitions_include_reactivation_only_when_requested() -> None:
    assert get_available_transitions("discovered") == [
        ApplicationWorkflowState.INTERESTED,
        ApplicationWorkflowState.WITHDRAWN,
        ApplicationWorkflowState.ARCHIVED,
    ]
    assert get_available_transitions("archived") == []
    assert get_available_transitions("archived", include_reactivation=True) == [
        ApplicationWorkflowState.DISCOVERED,
        ApplicationWorkflowState.INTERESTED,
    ]
