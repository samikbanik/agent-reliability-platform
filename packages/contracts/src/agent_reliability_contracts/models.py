"""Stable vocabulary shared by API, orchestration, and worker services."""

from enum import StrEnum


class JobState(StrEnum):
    """Lifecycle states described by the platform architecture."""

    QUEUED = "queued"
    PLANNING = "planning"
    RUNNING = "running"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_RETRY = "needs_retry"


class StepState(StrEnum):
    """Per-step execution states for the MVP workflow."""

    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class WorkerRole(StrEnum):
    """Worker boundaries included in the MVP."""

    PLANNER = "planner"
    RESEARCH = "research"
    SYNTHESIS = "synthesis"
    VERIFIER = "verifier"


# Sequential MVP DAG. Later phases can introduce richer dependency graphs.
WORKFLOW_ROLES: tuple[WorkerRole, ...] = (
    WorkerRole.PLANNER,
    WorkerRole.RESEARCH,
    WorkerRole.SYNTHESIS,
    WorkerRole.VERIFIER,
)


class QueueName(StrEnum):
    """RabbitMQ queue names used by the local MVP."""

    ORCHESTRATOR = "orchestrator.events"
    PLANNER = "tasks.planner"
    RESEARCH = "tasks.research"
    SYNTHESIS = "tasks.synthesis"
    VERIFIER = "tasks.verifier"


WORKER_QUEUES: dict[WorkerRole, QueueName] = {
    WorkerRole.PLANNER: QueueName.PLANNER,
    WorkerRole.RESEARCH: QueueName.RESEARCH,
    WorkerRole.SYNTHESIS: QueueName.SYNTHESIS,
    WorkerRole.VERIFIER: QueueName.VERIFIER,
}
