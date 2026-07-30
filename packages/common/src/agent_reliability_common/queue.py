"""Thin RabbitMQ helpers built on pika."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Callable
from typing import Any

import pika
from agent_reliability_contracts import WORKER_QUEUES, QueueName
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pydantic import BaseModel

from agent_reliability_common.settings import get_settings

logger = logging.getLogger(__name__)

ALL_QUEUES: tuple[str, ...] = (
    QueueName.ORCHESTRATOR.value,
    *(queue.value for queue in WORKER_QUEUES.values()),
)


def _connection_params() -> pika.URLParameters:
    return pika.URLParameters(get_settings().rabbitmq_url)


def connect(retries: int = 30, delay_seconds: float = 2.0) -> BlockingConnection:
    """Open a RabbitMQ connection, retrying while dependencies start."""
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            connection = pika.BlockingConnection(_connection_params())
            declare_queues(connection.channel())
            return connection
        except Exception as exc:  # noqa: BLE001 - startup readiness is best-effort
            last_error = exc
            logger.warning("RabbitMQ not ready (attempt %s/%s): %s", attempt, retries, exc)
            time.sleep(delay_seconds)
    raise RuntimeError(f"Unable to connect to RabbitMQ: {last_error}")


def declare_queues(channel: BlockingChannel) -> None:
    """Declare durable queues used by the MVP."""
    for queue_name in ALL_QUEUES:
        channel.queue_declare(queue=queue_name, durable=True)


def publish(queue: str | QueueName, message: BaseModel | dict[str, Any]) -> None:
    """Publish a JSON message to a durable queue."""
    queue_name = queue.value if isinstance(queue, QueueName) else queue
    body = (
        message.model_dump_json().encode("utf-8")
        if isinstance(message, BaseModel)
        else (json.dumps(message).encode("utf-8"))
    )
    connection = connect(retries=5, delay_seconds=1.0)
    try:
        channel = connection.channel()
        declare_queues(channel)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=body,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=2,
            ),
        )
    finally:
        connection.close()


def consume(
    queue: str | QueueName,
    handler: Callable[[dict[str, Any]], None],
    *,
    prefetch: int = 1,
) -> None:
    """Block forever consuming JSON messages from a queue."""
    queue_name = queue.value if isinstance(queue, QueueName) else queue
    connection = connect()
    channel = connection.channel()
    declare_queues(channel)
    channel.basic_qos(prefetch_count=prefetch)

    def _callback(ch: BlockingChannel, method, _properties, body: bytes) -> None:  # noqa: ANN001
        payload = json.loads(body.decode("utf-8"))
        try:
            handler(payload)
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception:
            logger.exception("Failed handling message on %s: %s", queue_name, payload)
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    channel.basic_consume(queue=queue_name, on_message_callback=_callback)
    logger.info("Consuming queue %s", queue_name)
    channel.start_consuming()
