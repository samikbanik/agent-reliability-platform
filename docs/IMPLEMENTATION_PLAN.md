# Implementation Plan

This plan is written so the project can be implemented in phases without overbuilding early.

Each phase should end in a working checkpoint with a demoable outcome.

## Phase 0: Project Bootstrap

Goal:

- create the monorepo structure and development foundations

Tasks:

- create the repository layout from `docs/ARCHITECTURE.md`
- choose package and dependency tooling
- create a shared `.env.example`
- add a top-level Makefile or task runner
- add basic linting and formatting
- add pre-commit hooks if desired
- create a lightweight ADR or decisions section in docs

Deliverables:

- repo skeleton
- service placeholders
- development conventions documented

Acceptance criteria:

- repo installs cleanly
- each service folder has a clear purpose
- local developer setup is documented

## Phase 1: Local MVP With Docker Compose

Goal:

- ship the first end-to-end user flow locally

Scope:

- frontend job submission page
- API job create and read endpoints
- orchestrator service
- planner worker
- research worker
- synthesis worker
- verifier worker
- Postgres
- Redis
- RabbitMQ

Required user flow:

1. user submits a research task
2. API stores a job
3. orchestrator creates step records
4. workers execute sequentially or as a simple DAG
5. verifier approves or rejects
6. final report becomes available in UI

Suggested implementation constraints:

- keep auth minimal or use a dev-only stub
- use deterministic local inputs where possible
- use structured output schemas for LLM interactions
- keep report generation simple at first, Markdown is enough

Deliverables:

- Docker Compose setup
- working UI
- working API and orchestrator
- functioning workers
- first end-to-end demo

Acceptance criteria:

- one job can be created from the UI and completed successfully
- workflow state is persisted in Postgres
- failures are visible in job status
- workers are decoupled via the queue

## Phase 2: Reliability Features

Goal:

- make the workflow resilient and inspectable

Tasks:

- add retries with max-attempt control
- add timeout handling
- add dead-letter or failed-job handling
- add idempotency protections
- persist worker attempt history
- add verification failure repair path
- capture model usage and latency metadata

Deliverables:

- retry policy
- failure taxonomy
- operator-visible execution history

Acceptance criteria:

- failed steps can retry safely
- duplicate delivery does not corrupt workflow state
- verifier rejections lead to predictable repair or terminal failure

## Phase 3: Observability

Goal:

- instrument the platform for debugging and operations

Tasks:

- add OpenTelemetry to all services
- emit traces across API, orchestrator, and workers
- export metrics for job counts, latencies, retries, queue depth
- centralize logs
- stand up Prometheus, Grafana, Loki, and Tempo locally
- create dashboards for throughput, failure rate, and latency

Deliverables:

- observability stack running locally
- dashboards and trace visibility

Acceptance criteria:

- a single job can be traced across services
- dashboard shows at least job volume, success rate, retry count, and latency
- logs can be filtered by job id

## Phase 4: Local Kubernetes

Goal:

- run the full stack on local Kubernetes

Tasks:

- containerize all services cleanly
- create Kubernetes base manifests or Helm charts
- add ConfigMaps and Secrets
- add liveness and readiness probes
- add resource requests and limits
- deploy to kind or minikube
- document deployment flow

Deliverables:

- local K8s deployment
- environment overlays for local

Acceptance criteria:

- full stack runs on local Kubernetes
- services restart cleanly
- health probes behave correctly

## Phase 5: CI/CD and Quality Gates

Goal:

- enforce engineering discipline before cloud rollout

Tasks:

- add GitHub Actions for lint, test, and build
- build and tag container images
- add dependency or image scanning
- add migration checks
- define release conventions

Deliverables:

- CI workflows
- reproducible image builds

Acceptance criteria:

- pull requests run tests and builds
- images can be produced consistently

## Phase 6: Terraform AWS Infrastructure

Goal:

- provision AWS infrastructure as code

Provision with Terraform:

- VPC
- subnets
- security groups
- IAM roles and policies
- EKS cluster
- EKS node group
- RDS Postgres
- S3 bucket for artifacts

Optional later:

- Route53
- ACM certificate
- ECR repositories if desired

Deliverables:

- Terraform modules or organized root configs
- environment variable and secret expectations documented

Acceptance criteria:

- `terraform plan` is clean and understandable
- AWS infrastructure can be created from code without manual console steps

## Phase 7: AWS Deployment

Goal:

- deploy the platform to AWS on EKS

Tasks:

- adapt Kubernetes overlays for AWS
- connect services to RDS and S3
- configure ingress
- validate IAM and secrets handling
- deploy observability stack
- smoke test end-to-end workflow

Deliverables:

- live AWS environment
- deployment documentation

Acceptance criteria:

- a cloud-hosted user can submit a job and receive a result
- telemetry works in AWS
- infrastructure can be recreated

## Phase 8: Reliability Showcase

Goal:

- make the project interview-ready

Tasks:

- add autoscaling where sensible
- run load tests
- simulate worker or queue failures
- write a postmortem for a failure scenario
- add runbooks
- document known tradeoffs

Deliverables:

- incident-style documentation
- demo script
- architecture and operations narrative

Acceptance criteria:

- you can explain failure handling and recovery clearly
- you have at least one measurable reliability story

## Phase 9: Optional Advanced Extensions

Choose only after the core system is stable:

- Kafka migration or event streaming sidecar
- service mesh
- advanced evaluator pipelines
- multi-step report repair loops
- cost-aware model routing
- pgvector or retrieval augmentation
- notification service
- user auth hardening

## Guardrails

- do not introduce Kafka in the MVP unless there is a real need
- do not hide orchestration logic inside a framework too early
- do not start with AWS before the local stack is stable
- do not overbuild auth, RBAC, or service mesh ahead of the product loop
- do not add more workers until the first four-worker flow is reliable

## Definition Of Done For The Whole Project

The project is complete enough for portfolio use when:

- it works locally end-to-end
- it works on local Kubernetes
- it is provisioned on AWS with Terraform
- it is deployed on EKS
- it is observable
- it demonstrates retries, verification, and failure recovery
- it is documented well enough for another engineer to run and understand
