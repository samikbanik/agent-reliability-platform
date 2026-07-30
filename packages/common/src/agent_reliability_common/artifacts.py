"""Local filesystem artifact storage for the MVP."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID

from agent_reliability_common.settings import get_settings


def storage_root() -> Path:
    """Return the configured local artifact root, creating it if needed."""
    root = Path(get_settings().artifact_storage_path)
    root.mkdir(parents=True, exist_ok=True)
    return root


def write_text_artifact(
    *,
    job_id: UUID,
    kind: str,
    content: str,
    extension: str = "md",
) -> str:
    """Persist a text artifact and return its relative storage path."""
    job_dir = storage_root() / str(job_id)
    job_dir.mkdir(parents=True, exist_ok=True)
    relative = f"{job_id}/{kind}.{extension}"
    path = storage_root() / relative
    path.write_text(content, encoding="utf-8")
    return relative


def read_text_artifact(storage_path: str) -> str:
    """Read a previously written text artifact."""
    return (storage_root() / storage_path).read_text(encoding="utf-8")
