from agent_reliability_contracts import JobState, WorkerRole


def test_architecture_vocabulary_is_stable() -> None:
    assert JobState.QUEUED == "queued"
    assert JobState.NEEDS_RETRY == "needs_retry"
    assert set(WorkerRole) == {"planner", "research", "synthesis", "verifier"}
