"""Workflow orchestrator service placeholder."""

from fastapi import FastAPI

app = FastAPI(title="Agent Reliability Orchestrator")


@app.get("/healthz", tags=["health"])
def health() -> dict[str, str]:
    """Confirm that the placeholder process is serving requests."""
    return {"service": "orchestrator", "status": "ok"}
