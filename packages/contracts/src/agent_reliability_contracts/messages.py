"""Queue payload contracts exchanged between API, orchestrator, and workers."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from agent_reliability_contracts.models import WorkerRole


class JobCreatedEvent(BaseModel):
    """Published by the API when a new research job is accepted."""

    type: str = Field(default="job_created", frozen=True)
    job_id: UUID


class StepTaskMessage(BaseModel):
    """Work item delivered to a role-specific worker queue."""

    type: str = Field(default="step_task", frozen=True)
    job_id: UUID
    step_id: UUID
    role: WorkerRole
    goal: str
    attempt: int = 1


class StepCompletedEvent(BaseModel):
    """Published by workers after a step succeeds or fails."""

    type: str = Field(default="step_completed", frozen=True)
    job_id: UUID
    step_id: UUID
    role: WorkerRole
    success: bool
    output: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None
