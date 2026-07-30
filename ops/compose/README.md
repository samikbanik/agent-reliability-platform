# Local Compose Operations

Phase 1 local stack for the Agent Reliability Platform.

## Services

- `web` on [http://localhost:3000](http://localhost:3000)
- `api` on [http://localhost:8000](http://localhost:8000)
- `orchestrator` on [http://localhost:8001](http://localhost:8001)
- `postgres`, `redis`, `rabbitmq`
- `worker-planner`, `worker-research`, `worker-synthesis`, `worker-verifier`

RabbitMQ management UI is available at [http://localhost:15672](http://localhost:15672)
(`agent_reliability` / `agent_reliability`).

## Run

From the repository root:

```bash
make env
make up
```

Then open the web UI and submit a research goal. The UI polls job status until the
verifier completes.

```bash
make down      # stop containers
make logs      # follow compose logs
make e2e       # create a job through the API and wait for completion
```

## Notes

- Workers use deterministic local content so the demo does not require an LLM API key.
- Artifacts are stored in the `artifact-data` Docker volume.
- Workflow state is persisted in Postgres (`jobs`, `job_steps`, `artifacts`).
