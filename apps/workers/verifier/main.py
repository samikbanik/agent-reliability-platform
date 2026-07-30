"""Verifier worker: check completeness, citations, and basic quality."""

from __future__ import annotations

import re
from typing import Any

from agent_reliability_common.db import session_scope
from agent_reliability_common.models import Job, JobStep
from agent_reliability_common.worker_runtime import run_worker
from agent_reliability_contracts import StepTaskMessage, WorkerRole
from sqlalchemy import select


def handle(
    message: StepTaskMessage, job: Job, _step: JobStep
) -> tuple[dict[str, Any], str | None, str]:
    report = _load_report(job.id)
    checks = {
        "has_title": bool(re.search(r"^#\s+\S+", report, flags=re.MULTILINE)),
        "has_summary_section": "## Summary" in report,
        "has_citations_section": "## Citations" in report,
        "has_inline_citations": bool(re.search(r"\[\d+\]", report)),
        "min_length": len(report.split()) >= 40,
        "mentions_goal_fragment": any(
            token.lower() in report.lower() for token in message.goal.split() if len(token) > 4
        )
        or len(message.goal.split()) <= 2,
    }
    approved = all(checks.values())
    reason = (
        "Report meets Phase 1 completeness checks."
        if approved
        else "Report failed one or more completeness checks: "
        + ", ".join(name for name, passed in checks.items() if not passed)
    )
    artifact = "\n".join(
        [
            "# Verification Result",
            "",
            f"**Approved:** {approved}",
            f"**Reason:** {reason}",
            "",
            "## Checks",
            *[f"- {name}: {'pass' if passed else 'fail'}" for name, passed in checks.items()],
        ]
    )
    output = {"approved": approved, "reason": reason, "checks": checks}
    return output, artifact, "verification"


def _load_report(job_id: Any) -> str:
    with session_scope() as session:
        synthesis = session.scalar(
            select(JobStep).where(
                JobStep.job_id == job_id,
                JobStep.role == WorkerRole.SYNTHESIS.value,
            )
        )
        if synthesis:
            report = synthesis.output_payload.get("report")
            if isinstance(report, str):
                return report
    return ""


def main() -> None:
    run_worker(WorkerRole.VERIFIER, handle)


if __name__ == "__main__":
    main()
