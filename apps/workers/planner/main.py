"""Planner worker: turn a research goal into a deterministic plan."""

from __future__ import annotations

from typing import Any

from agent_reliability_common.models import Job, JobStep
from agent_reliability_common.worker_runtime import run_worker
from agent_reliability_contracts import StepTaskMessage, WorkerRole


def handle(
    message: StepTaskMessage, _job: Job, _step: JobStep
) -> tuple[dict[str, Any], str | None, str]:
    topics = _topics_from_goal(message.goal)
    plan = {
        "goal": message.goal,
        "topics": topics,
        "deliverable": "2-page investment-style brief with citations",
        "steps": [
            "Collect source notes for each topic",
            "Synthesize a structured Markdown report",
            "Verify citations and completeness",
        ],
    }
    artifact = "\n".join(
        [
            "# Research Plan",
            "",
            f"**Goal:** {message.goal}",
            "",
            "## Topics",
            *[f"- {topic}" for topic in topics],
            "",
            "## Deliverable",
            plan["deliverable"],
        ]
    )
    return plan, artifact, "plan"


def _topics_from_goal(goal: str) -> list[str]:
    cleaned = " ".join(goal.strip().split())
    return [
        f"Market overview for: {cleaned}",
        "Competitive landscape and notable players",
        "Risks, constraints, and open questions",
        "Investment implications and summary thesis",
    ]


def main() -> None:
    run_worker(WorkerRole.PLANNER, handle)


if __name__ == "__main__":
    main()
