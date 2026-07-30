"""Research worker: produce deterministic local source notes."""

from __future__ import annotations

from typing import Any

from agent_reliability_common.db import session_scope
from agent_reliability_common.models import Job, JobStep
from agent_reliability_common.worker_runtime import run_worker
from agent_reliability_contracts import StepTaskMessage, WorkerRole
from sqlalchemy import select


def handle(
    message: StepTaskMessage, job: Job, _step: JobStep
) -> tuple[dict[str, Any], str | None, str]:
    topics = _load_topics(job.id, message.goal)
    sources = [
        {
            "id": index,
            "title": f"Source note {index}: {topic.split(':')[-1].strip()[:80]}",
            "url": f"https://example.local/research/{job.id}/{index}",
            "excerpt": (
                f"Deterministic research note for '{topic}'. "
                f"This stand-in content keeps the Phase 1 MVP offline-friendly."
            ),
        }
        for index, topic in enumerate(topics, start=1)
    ]
    artifact_lines = [
        "# Research Notes",
        "",
        f"**Goal:** {message.goal}",
        "",
    ]
    for source in sources:
        artifact_lines.extend(
            [
                f"## [{source['id']}] {source['title']}",
                f"- URL: {source['url']}",
                f"- Excerpt: {source['excerpt']}",
                "",
            ]
        )
    output = {"sources": sources, "topic_count": len(topics)}
    return output, "\n".join(artifact_lines), "research"


def _load_topics(job_id: Any, goal: str) -> list[str]:
    with session_scope() as session:
        planner = session.scalar(
            select(JobStep).where(
                JobStep.job_id == job_id,
                JobStep.role == WorkerRole.PLANNER.value,
            )
        )
        if planner and isinstance(planner.output_payload.get("topics"), list):
            return [str(item) for item in planner.output_payload["topics"]]
    return [
        f"Market overview for: {goal}",
        "Competitive landscape and notable players",
        "Risks, constraints, and open questions",
    ]


def main() -> None:
    run_worker(WorkerRole.RESEARCH, handle)


if __name__ == "__main__":
    main()
