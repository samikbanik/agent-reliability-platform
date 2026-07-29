# Development

## Prerequisites

- Node.js 20 or newer
- pnpm 10.4.1 (Corepack can install the version declared in `package.json`)
- Python 3.12
- uv
- GNU Make

Docker is not required until Phase 1.

## First-Time Setup

```bash
corepack enable
make bootstrap
make check
```

`make bootstrap` copies `.env.example` to the ignored `.env` file when needed, installs
the pnpm workspace, and creates a shared uv environment for all Python workspace members.
No real credentials belong in `.env.example`.

## Common Commands

```bash
make help          # list commands
make web           # Next.js placeholder on port 3000
make api           # API health endpoint on port 8000
make orchestrator  # orchestrator health endpoint on port 8001
make format        # apply Prettier and Ruff
make check         # lint, formatting, types, and tests
make pre-commit    # optional local Git hook installation
```

The API and orchestrator expose `GET /healthz`. Worker entry points intentionally only
identify themselves; queue consumers arrive in Phase 1.

## Conventions

- TypeScript is strict and formatted with Prettier.
- Python targets 3.12 and is linted and formatted with Ruff.
- Shared service vocabulary belongs in `packages/contracts`.
- Runtime configuration comes from environment variables; committed defaults are safe
  local-development examples only.
- Service folders own their runtime dependencies and must retain explicit boundaries.
- Generated files, local artifacts, virtual environments, and secrets are not committed.

## Workspace Boundaries

- pnpm manages JavaScript packages listed in `pnpm-workspace.yaml`.
- uv manages Python projects listed in the root `pyproject.toml`.
- The root Makefile is the supported developer interface over both toolchains.
