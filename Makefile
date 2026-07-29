.DEFAULT_GOAL := help

.PHONY: help bootstrap install env lint format format-check typecheck test check pre-commit web api orchestrator

help: ## Show available development commands
	@awk 'BEGIN {FS = ":.*## "; printf "Usage: make <target>\n\n"} /^[a-zA-Z_-]+:.*## / {printf "  %-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

bootstrap: env install ## Create local configuration and install dependencies

install: ## Install JavaScript and Python workspace dependencies
	pnpm install
	uv sync --all-packages

env: ## Create .env from the safe development template
	@test -f .env || cp .env.example .env

lint: ## Lint all source files
	pnpm lint
	uv run ruff check .

format: ## Format all source files
	pnpm format
	uv run ruff format .

format-check: ## Check formatting without changing files
	pnpm format:check
	uv run ruff format --check .

typecheck: ## Type-check the web application
	pnpm typecheck

test: ## Run the Python test suite
	uv run pytest

check: lint format-check typecheck test ## Run all local quality checks

pre-commit: ## Install the repository's Git pre-commit hooks
	uv run pre-commit install

web: ## Run the web placeholder
	pnpm --filter @agent-reliability/web dev

api: ## Run the API placeholder
	uv run --package agent-reliability-api uvicorn main:app --app-dir apps/api --reload --port 8000

orchestrator: ## Run the orchestrator placeholder
	uv run --package agent-reliability-orchestrator uvicorn main:app --app-dir apps/orchestrator --reload --port 8001
