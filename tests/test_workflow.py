from uuid import uuid4

from agent_reliability_contracts import JobState, WorkerRole
from workflow import _job_status_for_role


def test_job_status_maps_to_active_role() -> None:
    assert _job_status_for_role(WorkerRole.PLANNER) == JobState.PLANNING
    assert _job_status_for_role(WorkerRole.RESEARCH) == JobState.RUNNING
    assert _job_status_for_role(WorkerRole.SYNTHESIS) == JobState.RUNNING
    assert _job_status_for_role(WorkerRole.VERIFIER) == JobState.VERIFYING


def test_uuid_stable_for_smoke() -> None:
    assert uuid4().version == 4
