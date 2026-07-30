# Development

## Prerequisites

- Node.js 20 or newer
- pnpm 10.4.1 (Corepack can install the version declared in `package.json`)
- Python 3.12
- uv
- GNU Make
- Docker and Docker Compose for the Phase 1 full stack

## First-Time Setup

```bash
corepack enable
make bootstrap
make check
```

`make bootstrap` copies `.env.example` to the ignored `.env` file when needed, installs
the pnpm workspace, and creates a shared uv environment for all Python workspace members.
No real credentials belong in `.env.example`.

## Full Local Stack

```bash
make up      # build and start Compose services
make e2e     # create a job and wait for completion
make logs    # follow service logs
make down    # stop the stack
```

Useful endpoints:

- Web UI: `http://localhost:3000`
- API: `http://localhost:8000/healthz`
- Orchestrator: `http://localhost:8001/healthz`
- RabbitMQ management: `http://localhost:15672`

Phase 1 workers are deterministic and do not require an LLM API key.

## Common Commands

```bash
make help          # list commands
make web           # Next.js app on port 3000
make api           # API on port 8000
make orchestrator  # orchestrator on port 8001
make format        # apply Prettier and Ruff
make check         # lint, formatting, types, and tests
make pre-commit    # optional local Git hook installation
```

## Conventions

- TypeScript is strict and formatted with Prettier.
- Python targets 3.12 and is linted and formatted with Ruff.
- Shared service vocabulary belongs in `packages/contracts`.
- Shared DB, queue, cache, and artifact helpers belong in `packages/common`.
- Runtime configuration comes from environment variables; committed defaults are safe
  local-development examples only.
- Service folders own their runtime dependencies and must retain explicit boundaries.
- Generated files, local artifacts, virtual environments, and secrets are not committed.

## Workspace Boundaries

- pnpm manages JavaScript packages listed in `pnpm-workspace.yaml`.
- uv manages Python projects listed in the root `pyproject.toml`.
- The root Makefile is the supported developer interface over both toolchains.
- Docker Compose definitions live in `ops/compose/`.
