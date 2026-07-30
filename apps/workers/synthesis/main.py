"""Synthesis worker: draft a Markdown report from research notes."""

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
    sources = _load_sources(job.id)
    citations = " ".join(f"[{source['id']}]" for source in sources) or "[1]"
    finding_lines = [
        (f"- {source['title']}: {source['excerpt']} ({source['url']}) [{source['id']}]")
        for source in sources
    ] or ["- No sources were available; verifier should reject this draft."]
    report = "\n".join(
        [
            "# Research Brief",
            "",
            "## Goal",
            message.goal,
            "",
            "## Summary",
            (
                "This Phase 1 brief is generated from deterministic local research notes. "
                f"It summarizes the requested topic and cites the collected sources {citations}."
            ),
            "",
            "## Findings",
            *finding_lines,
            "",
            "## Risks And Open Questions",
            "- Source material is synthetic for local development.",
            "- Deeper market data and live retrieval arrive in later phases.",
            "",
            "## Recommendation",
            (
                "Treat this as a scaffolded investment-style brief. "
                "Use the cited notes as the baseline for human review."
            ),
            "",
            "## Citations",
            *[f"[{source['id']}] {source['title']} - {source['url']}" for source in sources],
        ]
    )
    output = {
        "report": report,
        "citation_count": len(sources),
        "word_count": len(report.split()),
    }
    return output, report, "report"


def _load_sources(job_id: Any) -> list[dict[str, Any]]:
    with session_scope() as session:
        research = session.scalar(
            select(JobStep).where(
                JobStep.job_id == job_id,
                JobStep.role == WorkerRole.RESEARCH.value,
            )
        )
        if research and isinstance(research.output_payload.get("sources"), list):
            return [dict(item) for item in research.output_payload["sources"]]
    return []


def main() -> None:
    run_worker(WorkerRole.SYNTHESIS, handle)


if __name__ == "__main__":
    main()
