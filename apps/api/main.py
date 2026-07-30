"""HTTP API for job creation, status, and artifact access."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import Any
from uuid import UUID

from agent_reliability_common.cache import cache_job_status, get_cached_job_status
from agent_reliability_common.db import get_session_factory, init_db
from agent_reliability_common.logging import configure_logging
from agent_reliability_common.models import Artifact, Job
from agent_reliability_common.queue import publish
from agent_reliability_contracts import JobCreatedEvent, JobState, QueueName
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from schemas import (
    CreateJobRequest,
    JobResponse,
    JobSummaryResponse,
)
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging("api")
    init_db()
    logger.info("API ready")
    yield


app = FastAPI(title="Agent Reliability API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db() -> Any:
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@app.get("/healthz", tags=["health"])
def health() -> dict[str, str]:
    return {"service": "api", "status": "ok"}


@app.post("/jobs", response_model=JobResponse, tags=["jobs"])
def create_job(payload: CreateJobRequest, db: Session = Depends(get_db)) -> Job:
    job = Job(goal=payload.goal.strip(), status=JobState.QUEUED.value)
    db.add(job)
    # Commit before enqueue so the orchestrator can load the durable job row.
    db.commit()
    db.refresh(job)
    publish(QueueName.ORCHESTRATOR, JobCreatedEvent(job_id=job.id))
    logger.info("Created job %s", job.id)
    return job


@app.get("/jobs", response_model=list[JobSummaryResponse], tags=["jobs"])
def list_jobs(db: Session = Depends(get_db)) -> list[Job]:
    return list(db.scalars(select(Job).order_by(Job.created_at.desc()).limit(50)))


@app.get("/jobs/{job_id}", response_model=JobResponse, tags=["jobs"])
def get_job(job_id: UUID, db: Session = Depends(get_db)) -> Job:
    cached = get_cached_job_status(job_id)
    job = db.scalar(
        select(Job)
        .where(Job.id == job_id)
        .options(selectinload(Job.steps), selectinload(Job.artifacts))
    )
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    response = JobResponse.model_validate(job)
    if cached and cached.get("status") == response.status:
        # Prefer durable Postgres state; cache is only a readiness hint in Phase 1.
        pass
    cache_job_status(job_id, response.model_dump(mode="json"))
    return job


@app.get("/jobs/{job_id}/artifacts/{artifact_id}", tags=["artifacts"])
def get_artifact_content(
    job_id: UUID, artifact_id: UUID, db: Session = Depends(get_db)
) -> dict[str, Any]:
    from agent_reliability_common import artifacts as artifact_store

    artifact = db.scalar(
        select(Artifact).where(Artifact.id == artifact_id, Artifact.job_id == job_id)
    )
    if artifact is None:
        raise HTTPException(status_code=404, detail="Artifact not found")
    try:
        content = artifact_store.read_text_artifact(artifact.storage_path)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Artifact file missing") from exc
    return {
        "id": artifact.id,
        "kind": artifact.kind,
        "content_type": artifact.content_type,
        "content": content,
    }
