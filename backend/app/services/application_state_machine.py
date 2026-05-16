from __future__ import annotations

from app.constants import ApplicationWorkflowState


_TRANSITIONS: dict[ApplicationWorkflowState, tuple[ApplicationWorkflowState, ...]] = {
    ApplicationWorkflowState.DISCOVERED: (
        ApplicationWorkflowState.INTERESTED,
        ApplicationWorkflowState.WITHDRAWN,
        ApplicationWorkflowState.ARCHIVED,
    ),
    ApplicationWorkflowState.INTERESTED: (
        ApplicationWorkflowState.APPLIED,
        ApplicationWorkflowState.WITHDRAWN,
        ApplicationWorkflowState.ARCHIVED,
    ),
    ApplicationWorkflowState.APPLIED: (
        ApplicationWorkflowState.INTERVIEWING,
        ApplicationWorkflowState.REJECTED,
        ApplicationWorkflowState.WITHDRAWN,
        ApplicationWorkflowState.ARCHIVED,
    ),
    ApplicationWorkflowState.INTERVIEWING: (
        ApplicationWorkflowState.OFFER,
        ApplicationWorkflowState.REJECTED,
        ApplicationWorkflowState.WITHDRAWN,
        ApplicationWorkflowState.ARCHIVED,
    ),
    ApplicationWorkflowState.OFFER: (
        ApplicationWorkflowState.WITHDRAWN,
        ApplicationWorkflowState.ARCHIVED,
    ),
    ApplicationWorkflowState.REJECTED: (ApplicationWorkflowState.ARCHIVED,),
    ApplicationWorkflowState.WITHDRAWN: (ApplicationWorkflowState.ARCHIVED,),
    ApplicationWorkflowState.ARCHIVED: (),
}

_REACTIVATION_TRANSITIONS: tuple[ApplicationWorkflowState, ...] = (
    ApplicationWorkflowState.DISCOVERED,
    ApplicationWorkflowState.INTERESTED,
)


def get_available_transitions(
    current_state: str | ApplicationWorkflowState,
    *,
    include_reactivation: bool = False,
) -> list[ApplicationWorkflowState]:
    state = ApplicationWorkflowState(current_state)
    if state == ApplicationWorkflowState.ARCHIVED and include_reactivation:
        return list(_REACTIVATION_TRANSITIONS)
    return list(_TRANSITIONS[state])


def can_transition(
    from_state: str | ApplicationWorkflowState,
    to_state: str | ApplicationWorkflowState,
    *,
    reactivate: bool = False,
) -> bool:
    source = ApplicationWorkflowState(from_state)
    target = ApplicationWorkflowState(to_state)
    if source == target:
        return True
    if source == ApplicationWorkflowState.ARCHIVED:
        return reactivate and target in _REACTIVATION_TRANSITIONS
    return target in _TRANSITIONS[source]
