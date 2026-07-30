# Agent Reliability Platform

Agent Reliability Platform is a portfolio project for learning and demonstrating hands-on AI engineering with strong infrastructure and reliability fundamentals.

The product is a web application where a user submits a long-running research goal, the system decomposes it into tasks, executes them across agent workers, verifies quality, retries failures, and returns a final cited report. The technical objective is not only to build an AI app, but to build and operate a reliable distributed system around that app.

## Why This Project Exists

Most AI demos are single-prompt applications. This project is intended to showcase the skills required to build production-style AI systems:

- agent orchestration
- structured outputs and evaluation
- microservices
- queues and background workers
- PostgreSQL and Redis
- observability with logs, metrics, and traces
- Kubernetes deployment and operations
- Terraform-based infrastructure provisioning
- CI/CD, rollout safety, and incident readiness

## Product Summary

End user experience:

1. A user submits a research request such as "Analyze the UK EV charging market and produce a 2-page brief."
2. The system plans the work into steps.
3. Worker services gather sources, extract facts, synthesize findings, and draft a report.
4. A verifier checks quality, completeness, and citation coverage.
5. Failed or low-confidence steps are retried or repaired.
6. The user sees progress, final output, and operational details such as status and timing.

## Core Learning Goals

- Build an agentic loop that is stateful, observable, and resilient
- Learn service decomposition and async workflow orchestration
- Learn local-first development and cloud promotion to AWS
- Learn Kubernetes through real deployments, scaling, probes, and config management
- Learn Terraform by provisioning AWS infrastructure as code
- Practice reliability concepts such as retries, dead-letter handling, SLOs, tracing, dashboards, and runbooks

## Recommended Stack

- Frontend: Next.js, TypeScript
- API: FastAPI
- Orchestrator and workers: Python
- Database: PostgreSQL
- Cache and coordination: Redis
- Queue: RabbitMQ for MVP
- Storage: local filesystem or MinIO in dev, S3 in AWS
- Observability: OpenTelemetry, Prometheus, Grafana, Loki, Tempo
- Packaging: Docker
- Local orchestration: Docker Compose, then kind
- Cloud orchestration: EKS
- Infrastructure as code: Terraform
- CI/CD: GitHub Actions

Kafka is optional and should not be part of the MVP unless there is a specific need for stream replay, partition-based scaling, or a stronger event-streaming story.

## Architecture

Logical services:

- `web`: user interface
- `api`: authentication, job creation, status, artifact access
- `orchestrator`: workflow state machine and task dispatch
- `worker-planner`: converts user goals into executable plans
- `worker-research`: fetches and stores research artifacts
- `worker-synthesis`: drafts structured outputs and final reports
- `worker-verifier`: checks completeness, citations, and quality
- `postgres`: durable workflow state
- `redis`: short-lived coordination, caching, idempotency helpers
- `rabbitmq`: async task transport
- `observability`: logs, metrics, traces, dashboards

## Delivery Strategy

Build the project in layers:

1. Local product MVP with Docker Compose
2. Local Kubernetes deployment with kind
3. AWS infrastructure with Terraform
4. EKS deployment and production-style operations

Do not start with every advanced component. The strongest story is a stable, working system that evolves in disciplined phases.

## Repository Guide

- [Architecture](docs/ARCHITECTURE.md)
- [Implementation plan](docs/IMPLEMENTATION_PLAN.md)
- [Development guide](docs/DEVELOPMENT.md)
- [Cursor handoff](docs/CURSOR_HANDOFF.md)
- [Architecture decisions](docs/decisions/)

## Local Development

Phase 1 provides the first end-to-end local MVP. Install Node.js 20+, pnpm 10.4.1,
Python 3.12, uv, Make, and Docker, then run:

```bash
corepack enable
make bootstrap
make check
make up
```

Open [http://localhost:3000](http://localhost:3000), submit a research goal, and watch the
job move through planner → research → synthesis → verifier. Use `make e2e` for an API-level
smoke test and `make logs` to inspect service output.

See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) and [ops/compose/README.md](ops/compose/README.md)
for workspace conventions and Compose details.

## Success Criteria

This project is successful when:

- a user can submit a job and receive a verified result
- the workflow survives worker failures and retries cleanly
- the system is observable end-to-end
- the stack runs locally and on Kubernetes
- AWS infrastructure is provisioned with Terraform
- the repository demonstrates strong engineering discipline, not just a demo app
