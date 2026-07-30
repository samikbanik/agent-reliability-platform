"""Workflow orchestrator: create steps, dispatch tasks, advance state."""

from __future__ import annotations

import logging
import threading
from contextlib import asynccontextmanager
from typing import Any

from agent_reliability_common.db import init_db, session_scope
from agent_reliability_common.logging import configure_logging
from agent_reliability_common.queue import consume
from agent_reliability_contracts import QueueName
from fastapi import FastAPI
from workflow import handle_event

logger = logging.getLogger(__name__)


def _consumer_loop() -> None:
    def _handle(payload: dict[str, Any]) -> None:
        with session_scope() as session:
            handle_event(session, payload)

    consume(QueueName.ORCHESTRATOR, _handle)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    configure_logging("orchestrator")
    init_db()
    thread = threading.Thread(target=_consumer_loop, name="orchestrator-consumer", daemon=True)
    thread.start()
    logger.info("Orchestrator ready")
    yield


app = FastAPI(title="Agent Reliability Orchestrator", lifespan=lifespan)


@app.get("/healthz", tags=["health"])
def health() -> dict[str, str]:
    return {"service": "orchestrator", "status": "ok"}
