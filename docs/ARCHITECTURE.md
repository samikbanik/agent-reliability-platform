# Architecture

## Product Definition

This project is a research automation product backed by a reliability-focused agent platform.

The user-facing product is simple:

- submit a research goal
- watch job progress
- receive a final report with citations

The engineering value is in how the platform handles long-running work:

- planning
- async execution
- persistence
- retries
- verification
- observability
- deployment and operations

## Primary Use Case

Example request:

`Analyze the UK EV charging market, compare 15 startups, and produce a 2-page investment brief.`

Expected system behavior:

1. accept the request and create a job
2. generate a task plan
3. execute tasks asynchronously
4. store artifacts and intermediate outputs
5. verify the final result
6. retry or repair failures
7. deliver final output with status history

## High-Level Components

### Frontend

Responsibilities:

- submit jobs
- view status
- show artifacts and reports
- display basic confidence, timing, and failure information

Suggested stack:

- Next.js
- TypeScript

### API Service

Responsibilities:

- auth stub or simple auth
- job creation
- job listing and job detail
- artifact retrieval
- health endpoints

Suggested stack:

- FastAPI
- SQLAlchemy or SQLModel

### Orchestrator Service

Responsibilities:

- create and track workflow state
- dispatch tasks to the queue
- manage retries, timeouts, and failure transitions
- coordinate verifier outcomes and repair loops

Notes:

- keep orchestration logic explicit rather than hiding it inside a framework
- LangGraph can be explored later, but should not be required for the first working system

### Worker Services

Recommended worker roles for MVP:

- `planner`
- `research`
- `synthesis`
- `verifier`

Optional later workers:

- `citation-normalizer`
- `report-formatter`
- `notification`
- `cost-analyzer`

### Data Layer

- `PostgreSQL`: jobs, steps, artifacts metadata, run history
- `Redis`: caches, idempotency helpers, lightweight coordination
- `S3` or local artifact storage: raw source files, generated reports

### Queue Layer

MVP recommendation:

- RabbitMQ

Reason:

- simple mental model
- widely used
- enough for async task routing and retries

Optional later:

- Kafka if the project evolves toward richer event streaming and replay

### Observability Layer

- OpenTelemetry instrumentation in every service
- Prometheus for metrics
- Grafana dashboards
- Loki for logs
- Tempo for traces

## Deployment Environments

### Local Dev

Purpose:

- fastest implementation and debugging loop

Components:

- Docker Compose
- local Postgres
- local Redis
- local RabbitMQ
- local observability stack

### Local Kubernetes

Purpose:

- learn Kubernetes before paying for cloud

Components:

- kind or minikube
- same app containers
- local manifests or Helm-based deployment

### AWS

Purpose:

- production-style showcase

Recommended split:

- managed: EKS, RDS Postgres, S3, IAM, VPC
- self-managed in cluster: Redis, RabbitMQ, Prometheus, Grafana, Loki, Tempo

## Suggested Repository Layout

```text
.
|-- README.md
|-- docs/
|   |-- ARCHITECTURE.md
|   |-- IMPLEMENTATION_PLAN.md
|   `-- CURSOR_HANDOFF.md
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

## Core Domain Model

Suggested initial entities:

- `Job`
- `JobStep`
- `Artifact`
- `WorkerRun`
- `VerificationResult`

Example job states:

- `queued`
- `planning`
- `running`
- `verifying`
- `completed`
- `failed`
- `needs_retry`

## Non-Goals For MVP

- multi-tenant enterprise auth
- payments
- Kafka-first architecture
- service mesh
- multi-region deployment
- advanced security policy engines

These are valid future extensions, but they should not block the first reliable end-to-end system.
