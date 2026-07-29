# Cursor Handoff

Use this document as the implementation brief for Cursor.

## Mission

Build a production-style personal project called `Agent Reliability Platform`.

The platform allows a user to submit a long-running research task. The system should plan the work, execute it across async workers, verify quality, retry failures when appropriate, and deliver a final report with citations. The project must be built in a phased manner, local-first, and later promoted to AWS with Kubernetes and Terraform.

## What Matters Most

Prioritize these qualities:

- correctness
- clarity of architecture
- phased delivery
- reliability primitives
- observability
- maintainable code

Do not optimize for flashy abstractions before the first working flow exists.

## Source Of Truth

Read these files before implementation:

- [README.md](../README.md)
- [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- [docs/IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

If there is any conflict, follow this order:

1. `docs/IMPLEMENTATION_PLAN.md`
2. `docs/ARCHITECTURE.md`
3. `README.md`

## Delivery Rules

Implement one phase at a time.

For each phase:

1. state which phase is being implemented
2. list the concrete files and services to create or modify
3. implement only the scoped work for that phase
4. verify with tests or local checks where possible
5. summarize what is complete and what remains

Do not jump directly to AWS, Kafka, service mesh, or advanced security features before the local platform works.

## Required Repository Shape

Create and use this structure unless there is a strong reason to improve it:

```text
.
|-- README.md
|-- docs/
|-- apps/
|   |-- web/
|   |-- api/
|   |-- orchestrator/
|   `-- workers/
|       |-- planner/
|       |-- research/
|       |-- synthesis/
|       `-- verifier/
|-- packages/
|   `-- contracts/
|-- ops/
|   |-- compose/
|   `-- observability/
|-- deploy/
|   `-- k8s/
|       |-- base/
|       `-- overlays/
|           |-- local/
|           `-- aws/
`-- infra/
    `-- terraform/
        `-- aws/
```

## Recommended Technical Choices

Use these defaults unless there is a very good reason not to:

- Next.js + TypeScript for frontend
- FastAPI for API and orchestrator-related HTTP services
- Python for workers
- PostgreSQL for durable state
- Redis for cache and coordination
- RabbitMQ for queueing
- Docker Compose for local full-stack development
- kind for local Kubernetes
- Terraform for AWS infrastructure
- EKS for AWS Kubernetes
- OpenTelemetry, Prometheus, Grafana, Loki, Tempo for observability

## Product Requirements

The MVP user journey must support:

1. user submits a research job from the UI
2. API creates a job record
3. orchestrator schedules planner, research, synthesis, and verifier work
4. workers save artifacts and status updates
5. verifier accepts or rejects output
6. user sees final job result and job history

## Reliability Requirements

By the time the core platform is complete, it should include:

- retries
- timeout handling
- idempotency-aware worker execution
- persistent job and step state
- execution logs
- metrics and traces
- health endpoints
- clear failure states

## Non-Goals For Early Phases

Avoid these until the core stack is stable:

- Kafka
- LangChain-heavy architecture
- service mesh
- multi-region deployment
- enterprise auth
- complicated event sourcing

LangGraph may be considered later, but only after explicit orchestration is working.

## Suggested Implementation Sequence

Start with Phase 0 and Phase 1 from `docs/IMPLEMENTATION_PLAN.md`.

Expected first major milestone:

- the full stack runs via Docker Compose
- a user can submit a job
- the platform completes a simple research workflow end-to-end

Expected second major milestone:

- traces, logs, and metrics are available locally
- retries and verifier failure handling are implemented

Expected third major milestone:

- the platform runs on local Kubernetes

Expected fourth major milestone:

- Terraform provisions AWS resources
- the platform runs on EKS

## Coding Guidance

- keep service boundaries explicit
- define shared contracts for job states and task payloads
- prefer structured models over loose dictionaries
- keep orchestration logic readable
- document assumptions and tradeoffs
- add tests around workflow state transitions and retry logic

## Example Prompt To Start In Cursor

Use this prompt in Cursor when starting implementation:

```text
Read README.md, docs/ARCHITECTURE.md, and docs/IMPLEMENTATION_PLAN.md. Implement Phase 0 first and stop after completing it. Create the monorepo skeleton, shared environment configuration, local developer tooling, and basic service placeholders exactly as described. Explain the file structure you create, the assumptions you make, and how the repository is prepared for Phase 1.
```

## Example Prompt For The Next Step

```text
Read README.md, docs/ARCHITECTURE.md, and docs/IMPLEMENTATION_PLAN.md. Implement Phase 1 only. Build the local MVP with Docker Compose, Next.js frontend, FastAPI-based services, PostgreSQL, Redis, RabbitMQ, and the four workers: planner, research, synthesis, verifier. Ensure the end-to-end workflow works for one research job and explain how to run and test it locally.
```
