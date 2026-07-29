# ADR 0001: Tooling and Repository Layout

- Status: accepted
- Date: 2026-07-29

## Context

The platform combines a TypeScript frontend with several Python services. Phase 0 needs
reproducible local setup without introducing Phase 1 infrastructure prematurely.

## Decision

- Keep the service-oriented layout specified in `docs/ARCHITECTURE.md`.
- Use pnpm workspaces for JavaScript and uv workspaces for Python.
- Standardize on Node.js 20+ and Python 3.12.
- Use Prettier for repository text and TypeScript, and Ruff for Python.
- Keep one root Makefile as the stable developer interface.
- Store only safe local defaults in `.env.example`; real `.env` files remain untracked.
- Keep deploy and operations directories as documented placeholders until their phases.

## Consequences

Both ecosystems retain native dependency metadata while sharing top-level install and
quality commands. Developers must install pnpm and uv. Service-specific containers and
infrastructure are deliberately deferred to preserve phased delivery.
