"""Redis helpers used for lightweight job-status caching."""

from __future__ import annotations

import json
import logging
import time
from typing import Any
from uuid import UUID

import redis

from agent_reliability_common.settings import get_settings

logger = logging.getLogger(__name__)

_client: redis.Redis | None = None


def get_redis(retries: int = 30, delay_seconds: float = 2.0) -> redis.Redis:
    """Return a Redis client after waiting for readiness."""
    global _client
    if _client is not None:
        try:
            _client.ping()
            return _client
        except redis.RedisError:
            _client = None

    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            client = redis.Redis.from_url(get_settings().redis_url, decode_responses=True)
            client.ping()
            _client = client
            return client
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning("Redis not ready (attempt %s/%s): %s", attempt, retries, exc)
            time.sleep(delay_seconds)
    raise RuntimeError(f"Unable to connect to Redis: {last_error}")


def cache_job_status(job_id: UUID, payload: dict[str, Any], ttl_seconds: int = 300) -> None:
    """Cache a job status snapshot for fast UI polling."""
    try:
        get_redis(retries=3, delay_seconds=0.5).setex(
            f"job:{job_id}:status",
            ttl_seconds,
            json.dumps(payload, default=str),
        )
    except Exception:  # noqa: BLE001 - cache is best-effort in Phase 1
        logger.debug("Skipping Redis cache write for job %s", job_id, exc_info=True)


def get_cached_job_status(job_id: UUID) -> dict[str, Any] | None:
    """Return a cached job status snapshot when present."""
    try:
        raw = get_redis(retries=1, delay_seconds=0.1).get(f"job:{job_id}:status")
    except Exception:  # noqa: BLE001
        return None
    if not raw:
        return None
    return json.loads(raw)
