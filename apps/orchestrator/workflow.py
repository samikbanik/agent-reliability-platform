"""Explicit sequential workflow transitions for the MVP."""

from __future__ import annotations

import logging
import time
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from agent_reliability_common.cache import cache_job_status
from agent_reliability_common.models import Job, JobStep
from agent_reliability_common.queue import publish
from agent_reliability_contracts import (
    WORKER_QUEUES,
    WORKFLOW_ROLES,
    JobCreatedEvent,
    JobState,
    StepCompletedEvent,
    StepState,
    StepTaskMessage,
    WorkerRole,
)
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

logger = logging.getLogger(__name__)


def handle_event(session: Session, payload: dict[str, Any]) -> None:
    event_type = payload.get("type")
    if event_type == "job_created":
        _start_job(session, JobCreatedEvent.model_validate(payload))
    elif event_type == "step_completed":
        _on_step_completed(session, StepCompletedEvent.model_validate(payload))
    else:
        logger.warning("Ignoring unknown orchestrator event: %s", event_type)


def _start_job(session: Session, event: JobCreatedEvent) -> None:
    job = None
    for attempt in range(1, 6):
        job = session.scalar(
            select(Job).where(Job.id == event.job_id).options(selectinload(Job.steps))
        )
        if job is not None:
            break
        session.expire_all()
        time.sleep(0.2 * attempt)
    if job is None:
        logger.error("job_created for missing job %s", event.job_id)
        return
    if job.steps:
        logger.info("Job %s already has steps; skipping re-init", job.id)
        return

    for position, role in enumerate(WORKFLOW_ROLES):
        session.add(
            JobStep(
                job_id=job.id,
                role=role.value,
                status=StepState.PENDING.value,
                position=position,
                input_payload={"goal": job.goal},
            )
        )
    session.flush()
    session.refresh(job)
    _dispatch_next(session, job)


def _on_step_completed(session: Session, event: StepCompletedEvent) -> None:
    job = session.scalar(select(Job).where(Job.id == event.job_id).options(selectinload(Job.steps)))
    if job is None:
        logger.error("step_completed for missing job %s", event.job_id)
        return

    step = next((item for item in job.steps if item.id == event.step_id), None)
    if step is None:
        logger.error("step_completed for missing step %s", event.step_id)
        return

    # Worker already persisted step status; orchestrator only advances the job.
    if not event.success:
        job.status = JobState.FAILED.value
        job.error_message = event.error_message or f"{event.role.value} step failed"
        job.updated_at = datetime.now(UTC)
        _cache(job)
        return

    if event.role == WorkerRole.VERIFIER:
        approved = bool(event.output.get("approved", False))
        if approved:
            report = _extract_report(job)
            job.status = JobState.COMPLETED.value
            job.final_report = report
            job.error_message = None
        else:
            # Repair loops arrive in Phase 2; Phase 1 surfaces verifier rejection.
            job.status = JobState.FAILED.value
            job.error_message = event.output.get("reason") or "Verifier rejected the report"
        job.updated_at = datetime.now(UTC)
        _cache(job)
        return

    _dispatch_next(session, job)


def _dispatch_next(session: Session, job: Job) -> None:
    pending = sorted(job.steps, key=lambda step: step.position)
    next_step = next(
        (
            step
            for step in pending
            if step.status in {StepState.PENDING.value, StepState.QUEUED.value}
        ),
        None,
    )
    if next_step is None:
        logger.info("No pending steps for job %s", job.id)
        return

    role = WorkerRole(next_step.role)
    job.status = _job_status_for_role(role).value
    next_step.status = StepState.QUEUED.value
    next_step.updated_at = datetime.now(UTC)
    job.updated_at = datetime.now(UTC)
    # Commit before enqueue so workers always observe durable step rows.
    session.commit()

    message = StepTaskMessage(
        job_id=UUID(str(job.id)),
        step_id=UUID(str(next_step.id)),
        role=role,
        goal=job.goal,
    )
    publish(WORKER_QUEUES[role], message)
    logger.info("Dispatched %s for job %s", role.value, job.id)
    _cache(job)


def _job_status_for_role(role: WorkerRole) -> JobState:
    if role == WorkerRole.PLANNER:
        return JobState.PLANNING
    if role == WorkerRole.VERIFIER:
        return JobState.VERIFYING
    return JobState.RUNNING


def _extract_report(job: Job) -> str | None:
    synthesis = next((step for step in job.steps if step.role == WorkerRole.SYNTHESIS.value), None)
    if synthesis is None:
        return None
    report = synthesis.output_payload.get("report")
    if isinstance(report, str):
        return report
    return None


def _cache(job: Job) -> None:
    cache_job_status(
        UUID(str(job.id)),
        {
            "id": str(job.id),
            "status": job.status,
            "error_message": job.error_message,
            "final_report": job.final_report,
        },
    )
