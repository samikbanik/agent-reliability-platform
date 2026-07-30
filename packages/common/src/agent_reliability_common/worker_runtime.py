"""Shared queue consumer loop for role-specific workers."""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from agent_reliability_contracts import (
    WORKER_QUEUES,
    QueueName,
    StepCompletedEvent,
    StepState,
    StepTaskMessage,
    WorkerRole,
)

from agent_reliability_common import artifacts
from agent_reliability_common.db import init_db, session_scope
from agent_reliability_common.logging import configure_logging
from agent_reliability_common.models import Artifact, Job, JobStep
from agent_reliability_common.queue import consume, publish

logger = logging.getLogger(__name__)

StepHandler = Callable[[StepTaskMessage, Job, JobStep], tuple[dict[str, Any], str | None, str]]


def run_worker(role: WorkerRole, handler: StepHandler) -> None:
    """Consume tasks for a worker role until the process is stopped."""
    configure_logging(f"worker-{role.value}")
    init_db()
    queue = WORKER_QUEUES[role]
    logger.info("Starting %s worker on queue %s", role.value, queue.value)

    def _handle(payload: dict[str, Any]) -> None:
        message = StepTaskMessage.model_validate(payload)
        if message.role != role:
            raise ValueError(f"Unexpected role {message.role} for {role} worker")
        _process_task(message, handler)

    consume(queue, _handle)


def _process_task(message: StepTaskMessage, handler: StepHandler) -> None:
    with session_scope() as session:
        step = session.get(JobStep, message.step_id)
        job = session.get(Job, message.job_id)
        if step is None or job is None:
            raise ValueError(f"Unknown job/step for message {message}")

        step.status = StepState.RUNNING.value
        step.started_at = datetime.now(UTC)
        session.flush()

        try:
            output, artifact_text, artifact_kind = handler(message, job, step)
            storage_path = None
            if artifact_text is not None:
                storage_path = artifacts.write_text_artifact(
                    job_id=UUID(str(job.id)),
                    kind=artifact_kind,
                    content=artifact_text,
                )
                session.add(
                    Artifact(
                        job_id=job.id,
                        step_id=step.id,
                        kind=artifact_kind,
                        storage_path=storage_path,
                        content_type="text/markdown",
                        metadata_json={"role": message.role.value},
                    )
                )
                output = {**output, "artifact_path": storage_path}

            step.status = StepState.COMPLETED.value
            step.output_payload = output
            step.completed_at = datetime.now(UTC)
            step.error_message = None
            success = True
            error_message = None
        except Exception as exc:  # noqa: BLE001 - convert worker failures into workflow events
            logger.exception("Worker %s failed for step %s", message.role, message.step_id)
            step.status = StepState.FAILED.value
            step.error_message = str(exc)
            step.completed_at = datetime.now(UTC)
            step.output_payload = {}
            success = False
            error_message = str(exc)
            output = {}

        event = StepCompletedEvent(
            job_id=message.job_id,
            step_id=message.step_id,
            role=message.role,
            success=success,
            output=output,
            error_message=error_message,
        )

    publish(QueueName.ORCHESTRATOR, event)
