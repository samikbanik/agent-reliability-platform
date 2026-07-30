.DEFAULT_GOAL := help

COMPOSE := docker compose --env-file .env -f ops/compose/docker-compose.yml

.PHONY: help bootstrap install env lint format format-check typecheck test check pre-commit web api orchestrator up down logs e2e

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
	PYTHONPATH=apps/orchestrator uv run pytest

check: lint format-check typecheck test ## Run all local quality checks

pre-commit: ## Install the repository's Git pre-commit hooks
	uv run pre-commit install

web: ## Run the web application
	pnpm --filter @agent-reliability/web dev

api: ## Run the API service
	uv run --package agent-reliability-api uvicorn main:app --app-dir apps/api --reload --port 8000

orchestrator: ## Run the orchestrator service
	uv run --package agent-reliability-orchestrator uvicorn main:app --app-dir apps/orchestrator --reload --port 8001

up: env ## Build and start the Docker Compose stack
	$(COMPOSE) up --build -d

down: ## Stop the Docker Compose stack
	$(COMPOSE) down

logs: ## Follow Docker Compose logs
	$(COMPOSE) logs -f

e2e: ## Submit a job through the API and wait for completion
	@./scripts/e2e-smoke.sh
