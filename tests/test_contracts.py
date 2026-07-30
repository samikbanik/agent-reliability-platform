from agent_reliability_contracts import (
    WORKFLOW_ROLES,
    JobCreatedEvent,
    JobState,
    StepTaskMessage,
    WorkerRole,
)


def test_architecture_vocabulary_is_stable() -> None:
    assert JobState.QUEUED == "queued"
    assert JobState.NEEDS_RETRY == "needs_retry"
    assert set(WorkerRole) == {"planner", "research", "synthesis", "verifier"}
    assert [role.value for role in WORKFLOW_ROLES] == [
        "planner",
        "research",
        "synthesis",
        "verifier",
    ]


def test_queue_messages_round_trip() -> None:
    created = JobCreatedEvent.model_validate(
        {"type": "job_created", "job_id": "11111111-1111-1111-1111-111111111111"}
    )
    task = StepTaskMessage(
        job_id=created.job_id,
        step_id="22222222-2222-2222-2222-222222222222",
        role=WorkerRole.PLANNER,
        goal="Investigate a market",
    )
    assert task.model_dump()["role"] == "planner"
