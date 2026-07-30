# ADR 0002: Phase 1 Local MVP Shape

- Status: accepted
- Date: 2026-07-31

## Context

Phase 1 must deliver one end-to-end research job through Docker Compose without
introducing cloud infrastructure, Kafka, or reliability machinery reserved for Phase 2.

## Decision

- Keep orchestration explicit in the orchestrator service as a sequential four-step workflow.
- Use RabbitMQ queues for `orchestrator.events` and one queue per worker role.
- Persist jobs, steps, and artifact metadata in PostgreSQL; store artifact bodies on a shared volume.
- Use Redis as a best-effort job-status cache, not as the source of truth.
- Keep workers deterministic and offline-friendly so the demo does not require an LLM key.
- Share runtime helpers through `packages/common` and vocabulary through `packages/contracts`.

## Consequences

The MVP is easy to reason about and demo locally. Retries, repair loops, timeouts, and
idempotency are intentionally deferred to Phase 2.
