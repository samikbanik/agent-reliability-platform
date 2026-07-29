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


class WorkerRole(StrEnum):
    """Worker boundaries included in the MVP."""

    PLANNER = "planner"
    RESEARCH = "research"
    SYNTHESIS = "synthesis"
    VERIFIER = "verifier"
